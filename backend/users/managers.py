from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):


    def _create_user(self, email=None, admission_number=None, password=None, role=None, **extra_fields):
        
        if role != 'student' and not email:
            raise ValueError("The Email must be set")
        if role == 'student' and not admission_number:
            raise ValueError("Admission number must be provided for students.")

        email = self.normalize_email(email) if email else None
        user = self.model(
            email=email,
            admission_number=admission_number,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        user.date_joined = timezone.now()
        
        try:
            user.full_clean()
        except Exception:
            
            raise

        user.save(using=self._db)
        return user

    def create_user(self, email=None, admission_number=None, password=None, role='student', **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email=email, admission_number=admission_number, password=password, role=role, **extra_fields)

    def create_superuser(self, email, password=None, role='admin', **extra_fields):
        
        if role != 'admin':
            raise ValueError("Superuser must have role='admin'")

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        if not email:
            raise ValueError('Superusers must have an email address')

        return self._create_user(email=email, password=password, role=role, **extra_fields)
