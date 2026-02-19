from django.db import models
from django.conf import settings
from students.models import StudentProfile, Enrollment
from adminstration.models import AcademicYear, Term, SchoolClass, Section


class Attendance(models.Model):
    """Records student attendance"""
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='attendances',
        db_index=True
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='attendances',
        db_index=True
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='attendances',
        db_index=True
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='attendances',
        db_index=True
    )
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name='attendances',
        db_index=True
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances',
        db_index=True
    )
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)
    remarks = models.TextField(blank=True, null=True)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='marked_attendances',
        limit_choices_to={'role__in': ['teacher', 'admin']},
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'student__first_name']
        unique_together = ['student', 'date']
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['school_class', 'date']),
            models.Index(fields=['academic_year', 'term', 'date']),
        ]

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"

