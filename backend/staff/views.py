from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q, Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime, timedelta
from users.permissions import IsAdminOrHR, IsAdmin
from .models import Department, StaffProfile, Leave, Attendance, Payroll
from .serializers import (
    DepartmentSerializer,
    StaffProfileSerializer,
    LeaveSerializer,
    AttendanceSerializer,
    PayrollSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing departments.
    Only admins and HR can manage departments.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrHR]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'head']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active departments"""
        active_depts = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_depts, many=True)
        return Response(serializer.data)


class StaffProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing staff profiles.
    Only admins and HR can manage staff.
    """
    queryset = StaffProfile.objects.select_related('user', 'department')
    serializer_class = StaffProfileSerializer
    permission_classes = [IsAdminOrHR]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'employment_type', 'is_active', 'user__role']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'user__email', 'position']
    ordering_fields = ['date_of_joining', 'employee_id', 'created_at']
    ordering = ['-date_of_joining']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active staff members"""
        active_staff = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_staff, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get staff grouped by department"""
        department_id = request.query_params.get('department_id')
        if not department_id:
            return Response(
                {'error': 'department_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        staff = self.queryset.filter(department_id=department_id, is_active=True)
        serializer = self.get_serializer(staff, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get staff statistics"""
        total_staff = self.queryset.filter(is_active=True).count()
        by_role = self.queryset.filter(is_active=True).values('user__role').annotate(count=Count('id'))
        by_employment = self.queryset.filter(is_active=True).values('employment_type').annotate(count=Count('id'))
        by_department = self.queryset.filter(is_active=True).values('department__name').annotate(count=Count('id'))
        
        avg_experience = self.queryset.filter(is_active=True).aggregate(avg=Avg('years_of_experience'))['avg'] or 0
        
        return Response({
            'total_staff': total_staff,
            'by_role': list(by_role),
            'by_employment_type': list(by_employment),
            'by_department': list(by_department),
            'average_experience': round(avg_experience, 2)
        })


class LeaveViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave applications.
    Only admins and HR can manage all leaves.
    Staff can view their own leaves.
    """
    queryset = Leave.objects.select_related('staff', 'approved_by')
    serializer_class = LeaveSerializer
    permission_classes = [IsAdminOrHR]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['staff', 'leave_type', 'status', 'start_date', 'end_date']
    search_fields = ['staff__first_name', 'staff__last_name', 'reason']
    ordering_fields = ['created_at', 'start_date']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending leave applications"""
        pending_leaves = self.queryset.filter(status='pending')
        serializer = self.get_serializer(pending_leaves, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a leave application"""
        leave = self.get_object()
        
        if leave.status != 'pending':
            return Response(
                {'error': 'Only pending leaves can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        leave.status = 'approved'
        leave.approved_by = request.user
        leave.approval_date = timezone.now()
        leave.save()
        
        serializer = self.get_serializer(leave)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a leave application"""
        leave = self.get_object()
        rejection_reason = request.data.get('rejection_reason')
        
        if leave.status != 'pending':
            return Response(
                {'error': 'Only pending leaves can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not rejection_reason:
            return Response(
                {'error': 'rejection_reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        leave.status = 'rejected'
        leave.approved_by = request.user
        leave.approval_date = timezone.now()
        leave.rejection_reason = rejection_reason
        leave.save()
        
        serializer = self.get_serializer(leave)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get leave statistics"""
        total_leaves = self.queryset.count()
        by_status = self.queryset.values('status').annotate(count=Count('id'))
        by_type = self.queryset.values('leave_type').annotate(count=Count('id'))
        
        now = timezone.now()
        current_month_leaves = self.queryset.filter(
            start_date__month=now.month,
            start_date__year=now.year
        ).count()
        
        return Response({
            'total_leaves': total_leaves,
            'by_status': list(by_status),
            'by_type': list(by_type),
            'current_month': current_month_leaves
        })


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing staff attendance.
    Only admins and HR can manage attendance.
    """
    queryset = Attendance.objects.select_related('staff', 'recorded_by')
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminOrHR]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['staff', 'date', 'status']
    search_fields = ['staff__first_name', 'staff__last_name']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's attendance"""
        today = timezone.now().date()
        today_attendance = self.queryset.filter(date=today)
        serializer = self.get_serializer(today_attendance, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_staff(self, request):
        """Get attendance for a specific staff member"""
        staff_id = request.query_params.get('staff_id')
        if not staff_id:
            return Response(
                {'error': 'staff_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attendance = self.queryset.filter(staff_id=staff_id)
        serializer = self.get_serializer(attendance, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_mark(self, request):
        """Mark attendance for multiple staff at once"""
        attendance_data = request.data.get('attendance', [])
        
        if not attendance_data:
            return Response(
                {'error': 'attendance array is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_records = []
        errors = []
        
        for data in attendance_data:
            data['recorded_by'] = request.user.id
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                created_records.append(serializer.data)
            else:
                errors.append({
                    'data': data,
                    'errors': serializer.errors
                })
        
        return Response({
            'created': created_records,
            'errors': errors,
            'summary': {
                'total': len(attendance_data),
                'created': len(created_records),
                'failed': len(errors)
            }
        }, status=status.HTTP_201_CREATED if created_records else status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get attendance statistics"""
        today = timezone.now().date()
        today_attendance = self.queryset.filter(date=today)
        today_stats = today_attendance.values('status').annotate(count=Count('id'))
        
        this_month_attendance = self.queryset.filter(
            date__month=today.month,
            date__year=today.year
        )
        month_stats = this_month_attendance.values('status').annotate(count=Count('id'))
        
        return Response({
            'today': {
                'total': today_attendance.count(),
                'by_status': list(today_stats)
            },
            'this_month': {
                'total': this_month_attendance.count(),
                'by_status': list(month_stats)
            }
        })


class PayrollViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payroll.
    Only admins and HR can manage payroll.
    """
    queryset = Payroll.objects.select_related('staff', 'processed_by')
    serializer_class = PayrollSerializer
    permission_classes = [IsAdminOrHR]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['staff', 'month', 'year', 'status']
    search_fields = ['staff__first_name', 'staff__last_name']
    ordering_fields = ['year', 'month', 'created_at']
    ordering = ['-year', '-month']

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending/draft payrolls"""
        pending = self.queryset.filter(status='draft')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process a payroll (change status to processed)"""
        payroll = self.get_object()
        
        if payroll.status != 'draft':
            return Response(
                {'error': 'Only draft payrolls can be processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payroll.status = 'processed'
        payroll.processed_by = request.user
        payroll.save()
        
        serializer = self.get_serializer(payroll)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark payroll as paid"""
        payroll = self.get_object()
        payment_date = request.data.get('payment_date')
        
        if payroll.status not in ['draft', 'processed']:
            return Response(
                {'error': 'Invalid payroll status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not payment_date:
            payment_date = timezone.now().date()
        
        payroll.status = 'paid'
        payroll.payment_date = payment_date
        payroll.save()
        
        serializer = self.get_serializer(payroll)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get payroll statistics"""
        total_payrolls = self.queryset.count()
        by_status = self.queryset.values('status').annotate(count=Count('id'))
        
        now = timezone.now()
        current_month_payroll = self.queryset.filter(
            month=now.month,
            year=now.year
        )
        
        total_this_month = current_month_payroll.aggregate(total=Sum('net_salary'))['total'] or 0
        
        return Response({
            'total_payrolls': total_payrolls,
            'by_status': list(by_status),
            'current_month': {
                'count': current_month_payroll.count(),
                'total_amount': total_this_month
            }
        })

