from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.hashers import check_password, make_password
import uuid
from .managers import UserManager
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('accountant', 'Accountant'),
        ('hr', 'Hr'),
    )

    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    admission_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    # Mark that a first-login notification for staff was already sent
    first_login_notified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    EMAIL_FIELD = 'email'

    class Meta:
        indexes = [
            models.Index(fields=['role']),
        ]

    def clean(self):
        """Model-level validation:
        - non-students must have an email
        - students must have an admission_number
        """
        super().clean()
        if self.role == 'student' and not self.admission_number:
            from django.core.exceptions import ValidationError

            raise ValidationError({'admission_number': 'Student users must have an admission_number.'})
        if self.role != 'student' and not self.email:
            from django.core.exceptions import ValidationError

            raise ValidationError({'email': 'Non-student users must have an email address.'})

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        if self.role == 'student':
            return self.admission_number or f"student-{self.pk}"
        return self.email or self.phone_number or f"user-{self.pk}"
class UserProfile(models.Model):
    BACKGROUND_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    background_check_status = models.CharField(max_length=20, choices=BACKGROUND_STATUS, default='pending')
    @property
    def properties_count(self):
        if hasattr(self.user, 'properties'):
            return self.user.properties.count()
        return 0
    def __str__(self):
        # defensive: user.email may be None for student-less accounts
        owner = self.user.email or self.user.get_full_name() or f"user-{self.user.pk}"
        return f"{owner} Profile"
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    class Meta:
        indexes = [
            models.Index(fields=['expires_at']),
            models.Index(fields=['used']),
        ]

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at
    def __str__(self):
        return f"Token for {self.user.email}"

