from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from adminstration.models import AcademicYear, Term, Subject


class Department(models.Model):
    """Represents school departments"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        limit_choices_to={'role__in': ['teacher', 'admin']}
    )
    is_active = models.BooleanField(default=True)
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
        limit_choices_to={'role__in': ['teacher', 'accountant', 'hr', 'admin']}
    )
    employee_id = models.CharField(max_length=20, unique=True)
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
        related_name='staff_members'
    )
    position = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    date_of_joining = models.DateField()
    date_of_leaving = models.DateField(blank=True, null=True)
    
    highest_qualification = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    bio = models.TextField(blank=True, null=True)
    photo = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_of_joining']

    def save(self, *args, **kwargs):
        if not self.employee_id:
            from datetime import datetime
            import random
            date_str = datetime.now().strftime('%Y%m%d')
            rand = random.randint(1000, 9999)
            self.employee_id = f"EMP{date_str}{rand}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.employee_id})"


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
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_applications',
        limit_choices_to={'role__in': ['teacher', 'accountant', 'hr']}
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.PositiveIntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
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
        ordering = ['-created_at']

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError({'end_date': 'End date must be later than or equal to start date.'})
            
            self.total_days = (self.end_date - self.start_date).days + 1

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.staff.first_name} {self.staff.last_name} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"


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
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        limit_choices_to={'role__in': ['teacher', 'accountant', 'hr']}
    )
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
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
        return f"{self.staff.first_name} {self.staff.last_name} - {self.date} ({self.get_status_display()})"


class Payroll(models.Model):
    """Manages monthly staff payroll"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )

    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payroll_records',
        limit_choices_to={'role__in': ['teacher', 'accountant', 'hr']}
    )
    month = models.PositiveIntegerField()  # 1-12
    year = models.PositiveIntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
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
        ordering = ['-year', '-month']
        constraints = [
            models.UniqueConstraint(
                fields=['staff', 'month', 'year'],
                name='unique_payroll_per_staff_per_month'
            )
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
        return f"{self.staff.first_name} {self.staff.last_name} - {month_name} {self.year}"

