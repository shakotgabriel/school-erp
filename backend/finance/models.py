from django.db import models
from decimal import Decimal
from django.db.models import Sum
from django.conf import settings
from django.core.exceptions import ValidationError
from adminstration.models import AcademicYear, Term, SchoolClass
from students.models import StudentProfile


class FeeStructure(models.Model):
    """Defines fee structure for different classes and academic years"""
    FREQUENCY_CHOICES = (
        ('once', 'Once'),
        ('termly', 'Termly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name='fee_structures',
        db_index=True
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='fee_structures',
        db_index=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='termly', db_index=True)
    is_mandatory = models.BooleanField(default=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-academic_year__start_date', 'school_class__name', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'school_class', 'academic_year'],
                name='unique_fee_structure_per_class_year'
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.school_class.name} ({self.academic_year.name})"


class FeePayment(models.Model):
    """Records student fee payments"""
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('cheque', 'Cheque'),
        ('card', 'Card'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='fee_payments',
        db_index=True
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.PROTECT,
        related_name='payments',
        db_index=True
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='fee_payments',
        blank=True,
        null=True,
        db_index=True
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(db_index=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, db_index=True)
    transaction_reference = models.CharField(max_length=100, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='completed', db_index=True)
    remarks = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_payments',
        limit_choices_to={'role__in': ['admin', 'accountant']},
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']
        indexes = [
            models.Index(fields=['student', 'fee_structure']),
            models.Index(fields=['status', 'payment_date']),
        ]

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.fee_structure.name} - {self.amount_paid}"


class Invoice(models.Model):
    """Represents student invoices"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )

    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='invoices',
        db_index=True
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='invoices',
        db_index=True
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='invoices',
        db_index=True
    )
    issue_date = models.DateField(db_index=True)
    due_date = models.DateField(db_index=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices',
        limit_choices_to={'role__in': ['admin', 'accountant']},
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['student', 'academic_year', 'term']),
            models.Index(fields=['status', 'due_date']),
        ]

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.student.first_name} {self.student.last_name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from datetime import date
            today = date.today()
            count = Invoice.objects.filter(issue_date__year=today.year).count() + 1
            self.invoice_number = f"INV-{today.year}-{count:04d}"
        
        self.balance = self.total_amount - self.paid_amount
        if self.balance <= 0 and self.status not in ['paid', 'cancelled']:
            self.status = 'paid'
        
        super().save(*args, **kwargs)

    def update_amounts(self):
        """Recalculates total amount from invoice items"""
        self.total_amount = self.items.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')  # type: ignore[attr-defined]
        self.save()

    def update_paid_amount(self):
        """Recalculates paid amount from related payments"""
        self.paid_amount = self.payments.filter(status='completed').aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')  # type: ignore[attr-defined]
        self.save()


class InvoiceItem(models.Model):
    """Represents individual items within an invoice"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.PROTECT, related_name='invoice_items')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['description']
        unique_together = ('invoice', 'fee_structure')

    def __str__(self):
        return f"{self.description} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = self.fee_structure.name
        super().save(*args, **kwargs)
        self.invoice.update_amounts()

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        super().delete(*args, **kwargs)
        invoice.update_amounts()


class Expense(models.Model):
    """Records school expenses"""
    CATEGORY_CHOICES = (
        ('salaries', 'Salaries'),
        ('utilities', 'Utilities'),
        ('maintenance', 'Maintenance'),
        ('supplies', 'Supplies'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    )

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    expense_date = models.DateField(db_index=True)
    receipt = models.FileField(upload_to='expense_receipts/', blank=True, null=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_expenses',
        limit_choices_to={'role__in': ['admin', 'accountant']},
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.category} - {self.amount} on {self.expense_date}"


class Budget(models.Model):
    """Manages budgets for academic years"""
    academic_year = models.OneToOneField(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='budget',
        db_index=True
    )
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_budgets',
        limit_choices_to={'role__in': ['admin', 'accountant']},
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-academic_year__start_date']

    def __str__(self):
        return f"Budget for {self.academic_year.name} - {self.total_budget}"

    def clean(self):
        if self.total_budget <= 0:
            raise ValidationError("Total budget must be a positive number.")

    @property
    def total_expenses(self):
        """Calculate total expenses for the budget's academic year"""
        start_date = self.academic_year.start_date
        end_date = self.academic_year.end_date
        return Expense.objects.filter(
            expense_date__range=(start_date, end_date)
        ).aggregate(total=Sum('amount'))['total'] or 0

    @property
    def remaining_budget(self):
        """Calculate the remaining budget"""
        return self.total_budget - self.total_expenses
