from django.db import models
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
        related_name='fee_structures'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='termly')
    is_mandatory = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
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
        related_name='fee_payments'
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='fee_payments',
        blank=True,
        null=True
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='completed')
    remarks = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_payments',
        limit_choices_to={'role__in': ['admin', 'accountant']}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.amount_paid} ({self.payment_date})"

    def clean(self):
        if self.amount_paid and self.amount_paid <= 0:
            raise ValidationError({'amount_paid': 'Amount must be greater than zero.'})


class Invoice(models.Model):
    """Generates invoices for students"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )

    invoice_number = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='invoices',
        blank=True,
        null=True
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices',
        limit_choices_to={'role__in': ['admin', 'accountant']}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-created_at']

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.student.first_name} {self.student.last_name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from datetime import datetime
            import random
            date_str = datetime.now().strftime('%Y%m%d')
            rand = random.randint(1000, 9999)
            self.invoice_number = f"INV{date_str}{rand}"
        
        self.balance = self.total_amount - self.amount_paid
        super().save(*args, **kwargs)


class Expense(models.Model):
    """Tracks school expenses"""
    CATEGORY_CHOICES = (
        ('salaries', 'Salaries'),
        ('utilities', 'Utilities'),
        ('maintenance', 'Maintenance'),
        ('supplies', 'Supplies'),
        ('equipment', 'Equipment'),
        ('transportation', 'Transportation'),
        ('food', 'Food'),
        ('other', 'Other'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField()
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='expenses',
        blank=True,
        null=True
    )
    vendor = models.CharField(max_length=200, blank=True, null=True)
    receipt_number = models.CharField(max_length=100, blank=True, null=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_expenses',
        limit_choices_to={'role': 'admin'}
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_expenses',
        limit_choices_to={'role__in': ['admin', 'accountant']}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.amount} ({self.expense_date})"

    def clean(self):
        if self.amount and self.amount <= 0:
            raise ValidationError({'amount': 'Amount must be greater than zero.'})


class Budget(models.Model):
    """Manages school budgets"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='budgets',
        blank=True,
        null=True
    )
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_budgets',
        limit_choices_to={'role': 'admin'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.academic_year.name}"

    def save(self, *args, **kwargs):
        self.remaining_amount = self.total_budget - self.spent_amount
        super().save(*args, **kwargs)

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError({'end_date': 'End date must be later than start date.'})
        if self.total_budget and self.total_budget <= 0:
            raise ValidationError({'total_budget': 'Budget must be greater than zero.'})
