from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q
from django_filters.rest_framework import DjangoFilterBackend
from users.permissions import IsAdminOrAccountant, IsAdmin
from .models import FeeStructure, FeePayment, Invoice, Expense, Budget
from .serializers import (
    FeeStructureSerializer,
    FeePaymentSerializer,
    InvoiceSerializer,
    ExpenseSerializer,
    BudgetSerializer
)


class FeeStructureViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing fee structures.
    Only admins and accountants can manage fee structures.
    """
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAdminOrAccountant]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school_class', 'academic_year', 'frequency', 'is_mandatory', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'amount', 'created_at']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active fee structures"""
        active_structures = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_structures, many=True)
        return Response(serializer.data)


class FeePaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing fee payments.
    Only admins and accountants can manage payments.
    """
    queryset = FeePayment.objects.select_related('student', 'fee_structure', 'term', 'recorded_by')
    serializer_class = FeePaymentSerializer
    permission_classes = [IsAdminOrAccountant]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'fee_structure', 'term', 'payment_method', 'status']
    search_fields = ['student__first_name', 'student__last_name', 'transaction_reference']
    ordering_fields = ['payment_date', 'amount_paid', 'created_at']
    ordering = ['-payment_date']

    @action(detail=False, methods=['get'])
    def student_payments(self, request):
        """Get all payments for a specific student"""
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response(
                {'error': 'student_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payments = self.queryset.filter(student_id=student_id)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def payment_summary(self, request):
        """Get payment summary statistics"""
        payments = self.queryset.filter(status='completed')
        total_received = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
        
        summary = {
            'total_payments': payments.count(),
            'total_amount_received': total_received,
            'pending_payments': self.queryset.filter(status='pending').count(),
        }
        return Response(summary)


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing invoices.
    Only admins and accountants can manage invoices.
    """
    queryset = Invoice.objects.select_related('student', 'academic_year', 'term', 'created_by')
    serializer_class = InvoiceSerializer
    permission_classes = [IsAdminOrAccountant]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'academic_year', 'term', 'status']
    search_fields = ['invoice_number', 'student__first_name', 'student__last_name']
    ordering_fields = ['issue_date', 'due_date', 'total_amount', 'created_at']
    ordering = ['-issue_date']

    @action(detail=False, methods=['get'])
    def outstanding(self, request):
        """Get all outstanding invoices"""
        outstanding = self.queryset.filter(
            Q(status='sent') | Q(status='overdue')
        ).filter(balance__gt=0)
        serializer = self.get_serializer(outstanding, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark an invoice as paid"""
        invoice = self.get_object()
        invoice.status = 'paid'
        invoice.amount_paid = invoice.total_amount
        invoice.balance = 0
        invoice.save()
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def invoice_summary(self, request):
        """Get invoice summary statistics"""
        invoices = self.queryset.all()
        summary = {
            'total_invoices': invoices.count(),
            'total_amount': invoices.aggregate(total=Sum('total_amount'))['total'] or 0,
            'total_paid': invoices.aggregate(total=Sum('amount_paid'))['total'] or 0,
            'total_outstanding': invoices.aggregate(total=Sum('balance'))['total'] or 0,
            'paid_invoices': invoices.filter(status='paid').count(),
            'overdue_invoices': invoices.filter(status='overdue').count(),
        }
        return Response(summary)


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing expenses.
    Only admins and accountants can manage expenses.
    """
    queryset = Expense.objects.select_related('academic_year', 'term', 'approved_by', 'recorded_by')
    serializer_class = ExpenseSerializer
    permission_classes = [IsAdminOrAccountant]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'academic_year', 'term']
    search_fields = ['title', 'description', 'vendor']
    ordering_fields = ['expense_date', 'amount', 'created_at']
    ordering = ['-expense_date']

    @action(detail=False, methods=['get'])
    def expense_summary(self, request):
        """Get expense summary by category"""
        expenses = self.queryset.all()
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
        
        by_category = {}
        for category in Expense.CATEGORY_CHOICES:
            category_total = expenses.filter(category=category[0]).aggregate(total=Sum('amount'))['total'] or 0
            by_category[category[0]] = {
                'name': category[1],
                'total': category_total
            }
        
        summary = {
            'total_expenses': total_expenses,
            'expense_count': expenses.count(),
            'by_category': by_category
        }
        return Response(summary)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an expense (admin only)"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Only admins can approve expenses'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        expense = self.get_object()
        expense.approved_by = request.user
        expense.save()
        serializer = self.get_serializer(expense)
        return Response(serializer.data)


class BudgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing budgets.
    Only admins can create/update/delete budgets.
    Accountants can view budgets.
    """
    queryset = Budget.objects.select_related('academic_year', 'term', 'created_by')
    serializer_class = BudgetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['academic_year', 'term', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'total_budget', 'created_at']
    ordering = ['-start_date']

    def get_permissions(self):
        """
        Admins have full access, accountants can only view
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAdminOrAccountant]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active budgets"""
        active_budgets = self.queryset.filter(status='active')
        serializer = self.get_serializer(active_budgets, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a budget (admin only)"""
        budget = self.get_object()
        budget.status = 'active'
        budget.save()
        serializer = self.get_serializer(budget)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def budget_summary(self, request):
        """Get budget utilization summary"""
        budgets = self.queryset.filter(status='active')
        summary = {
            'total_budget': budgets.aggregate(total=Sum('total_budget'))['total'] or 0,
            'total_spent': budgets.aggregate(total=Sum('spent_amount'))['total'] or 0,
            'total_remaining': budgets.aggregate(total=Sum('remaining_amount'))['total'] or 0,
            'active_budgets': budgets.count(),
        }
        return Response(summary)

