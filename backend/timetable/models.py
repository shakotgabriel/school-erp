from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from adminstration.models import AcademicYear, Term, SchoolClass, Section, Subject
from students.models import TeacherAssignment


class TimeSlot(models.Model):
    """Defines time slots for the timetable"""
    DAY_CHOICES = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )

    name = models.CharField(max_length=50)  # e.g., "Period 1", "Morning Break", "Lunch"
    day_of_week = models.CharField(max_length=20, choices=DAY_CHOICES, db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False, db_index=True)
    order = models.PositiveIntegerField(default=0)  # To maintain sequence
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['day_of_week', 'order', 'start_time']
        constraints = [
            models.UniqueConstraint(
                fields=['day_of_week', 'start_time'],
                name='unique_timeslot_per_day'
            )
        ]

    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError({'end_time': 'End time must be later than start time.'})
        
        if self.pk:
            overlapping = TimeSlot.objects.filter(
                day_of_week=self.day_of_week,
                is_active=True
            ).exclude(pk=self.pk).filter(
                models.Q(start_time__lt=self.end_time, end_time__gt=self.start_time)
            )
        else:
            overlapping = TimeSlot.objects.filter(
                day_of_week=self.day_of_week,
                is_active=True,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            )
        
        if overlapping.exists():
            raise ValidationError('This time slot overlaps with an existing time slot on the same day.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.name} ({self.start_time} - {self.end_time})"


class Timetable(models.Model):
    """Represents a timetable for a specific class/section in an academic year and term"""
    name = models.CharField(max_length=200)
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name='timetables',
        db_index=True
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='timetables',
        blank=True,
        null=True,
        db_index=True
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='timetables',
        db_index=True
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='timetables',
        db_index=True
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_timetables',
        limit_choices_to={'role__in': ['admin', 'teacher']},
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-academic_year__start_date', 'school_class__name']
        unique_together = ('school_class', 'section', 'academic_year', 'term')
        indexes = [
            models.Index(fields=['is_active', 'academic_year', 'term']),
        ]

    def __str__(self):
        section_name = f" - {self.section.name}" if self.section else ""
        return f"{self.name} for {self.school_class.name}{section_name} ({self.academic_year.name} - {self.term.name})"


class TimetableEntry(models.Model):
    """An entry in a timetable, linking a subject, teacher, and time slot"""
    timetable = models.ForeignKey(
        Timetable,
        on_delete=models.CASCADE,
        related_name='entries',
        db_index=True
    )
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='timetable_entries',
        db_index=True
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='timetable_entries',
        db_index=True
    )
    teacher_assignment = models.ForeignKey(
        TeacherAssignment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timetable_entries',
        db_index=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['time_slot__day_of_week', 'time_slot__order']
        unique_together = ('timetable', 'time_slot')
        indexes = [
            models.Index(fields=['timetable', 'time_slot']),
            models.Index(fields=['subject', 'teacher_assignment']),
        ]

    def __str__(self):
        return f"{self.timetable.name} - {self.time_slot} - {self.subject.name}"

    def clean(self):
        # Ensure the teacher is assigned to the subject for the given class
        if self.teacher_assignment:
            timetable = self.timetable
            assignment = self.teacher_assignment
            
            if (
                assignment.subject != self.subject or
                assignment.school_class != timetable.school_class or
                assignment.section != timetable.section or
                assignment.academic_year != timetable.academic_year
            ):
                raise ValidationError(
                    "Teacher assignment does not match the timetable's subject, class, section, or academic year."
                )

        # Check for teacher clashes
        if self.teacher_assignment:
            clashes = TimetableEntry.objects.filter(
                is_active=True,
                time_slot=self.time_slot,
                teacher_assignment=self.teacher_assignment
            ).exclude(pk=self.pk)
            
            if clashes.exists():
                raise ValidationError(
                    f"Teacher {self.teacher_assignment.teacher} is already assigned to another class at this time."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

