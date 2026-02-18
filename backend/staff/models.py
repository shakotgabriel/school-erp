from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from adminstration.models import AcademicYear, Term, Subject


class Department(models.Model):
    """Represents school departments"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        limit_choices_to={'role__in': ['teacher', 'admin']},
        db_index=True
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class StaffProfile(models.Model):
    """Extended profile for staff members (teachers, accountants, HR, etc.)"""
    EMPLOYMENT_TYPE_CHOICES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
    )

    MARITAL_STATUS_CHOICES = (
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profile',
        limit_choices_to={'role__in': ['teacher', 'accountant', 'hr', 'admin']},
        db_index=True
    )
    employee_id = models.CharField(max_length=20, unique=True, db_index=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True, null=True)
    
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    emergency_contact_relationship = models.CharField(max_length=50)
    
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_members',
        db_index=True
    )
    position = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time', db_index=True)
    date_of_joining = models.DateField(db_index=True)
    date_of_leaving = models.DateField(blank=True, null=True, db_index=True)
    
    highest_qualification = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    bio = models.TextField(blank=True, null=True)
    photo = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_of_joining']
        indexes = [
            models.Index(fields=['department', 'is_active']),
            models.Index(fields=['user', 'is_active']),
        ]

    def save(self, *args, **kwargs):
        if not self.employee_id:
            from datetime import datetime
            import random
            date_str = datetime.now().strftime('%Y%m%d')
            rand = random.randint(1000, 9999)
            self.employee_id = f"EMP{date_str}{rand}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Leave(models.Model):
    """Manages staff leave applications"""
    LEAVE_TYPE_CHOICES = (
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('annual', 'Annual Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('unpaid', 'Unpaid Leave'),
        ('study', 'Study Leave'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name='leaves',
        db_index=True
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES, db_index=True)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves',
        limit_choices_to={'role__in': ['admin', 'hr']}
    )
    approval_date = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['staff', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError({'end_date': 'End date must be later than or equal to start date.'})
            
            self.total_days = (self.end_date - self.start_date).days + 1

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.staff.user.first_name} {self.staff.user.last_name} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"


class Attendance(models.Model):
    """Tracks daily staff attendance"""
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
        ('on_leave', 'On Leave'),
    )

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name='attendances',
        db_index=True
    )
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)
    check_in_time = models.TimeField(blank=True, null=True)
    check_out_time = models.TimeField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_attendances',
        limit_choices_to={'role__in': ['admin', 'hr']}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['staff', 'date'],
                name='unique_attendance_per_staff_per_day'
            )
        ]

    def __str__(self):
        return f"{self.staff.user.first_name} {self.staff.user.last_name} - {self.date} ({self.get_status_display()})"


class Payroll(models.Model):
    """Manages monthly staff payroll"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name='payrolls',
        db_index=True
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='payrolls',
        db_index=True
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='payrolls',
        db_index=True
    )
    month = models.PositiveIntegerField()  # 1-12
    year = models.PositiveIntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(blank=True, null=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    remarks = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payrolls',
        limit_choices_to={'role__in': ['admin', 'hr']}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month', 'staff']
        unique_together = ('staff', 'month', 'year')
        indexes = [
            models.Index(fields=['academic_year', 'term']),
            models.Index(fields=['status', 'payment_date']),
        ]

    def clean(self):
        if self.month and (self.month < 1 or self.month > 12):
            raise ValidationError({'month': 'Month must be between 1 and 12.'})

    def save(self, *args, **kwargs):
        self.net_salary = self.basic_salary + self.allowances - self.deductions
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        from datetime import date
        month_name = date(self.year, self.month, 1).strftime('%B')
        return f"{self.staff.user.first_name} {self.staff.user.last_name} - {month_name} {self.year}"

