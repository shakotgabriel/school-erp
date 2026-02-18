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
    day_of_week = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)  # To maintain sequence
    is_active = models.BooleanField(default=True)

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
        
        # Check for overlapping time slots on the same day
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
        related_name='timetables'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='timetables',
        blank=True,
        null=True
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='timetables'
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='timetables'
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_timetables',
        limit_choices_to={'role__in': ['admin', 'teacher']}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-academic_year__start_date', 'school_class__name']
        constraints = [
            models.UniqueConstraint(
                fields=['school_class', 'section', 'academic_year', 'term'],
                name='unique_timetable_per_section_term'
            )
        ]

    def clean(self):
        if self.section and self.section.school_class != self.school_class:
            raise ValidationError({'section': 'Selected section does not belong to this class.'})
        
        if self.term and self.academic_year:
            if self.term.academic_year != self.academic_year:
                raise ValidationError({'term': 'Selected term does not belong to the selected academic year.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        section_str = f" - {self.section.name}" if self.section else ""
        return f"{self.school_class.name}{section_str} ({self.academic_year.name} - {self.term.name})"


class TimetableEntry(models.Model):
    """Individual entry in a timetable (a specific subject at a specific time)"""
    timetable = models.ForeignKey(
        Timetable,
        on_delete=models.CASCADE,
        related_name='entries'
    )
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='timetable_entries',
        blank=True,
        null=True
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teaching_entries',
        limit_choices_to={'role': 'teacher'}
    )
    room = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['time_slot__day_of_week', 'time_slot__order']
        verbose_name_plural = 'Timetable entries'
        constraints = [
            models.UniqueConstraint(
                fields=['timetable', 'time_slot'],
                name='unique_entry_per_timeslot'
            )
        ]

    def clean(self):
        # If time slot is a break, subject and teacher should be null
        if self.time_slot and self.time_slot.is_break:
            if self.subject or self.teacher:
                raise ValidationError('Break periods cannot have subjects or teachers assigned.')
        else:
            # Regular periods should have a subject
            if not self.subject:
                raise ValidationError({'subject': 'Non-break periods must have a subject assigned.'})

        # Check if teacher is already assigned to another class at the same time
        if self.teacher and self.time_slot:
            conflicting_entries = TimetableEntry.objects.filter(
                teacher=self.teacher,
                time_slot=self.time_slot
            ).exclude(pk=self.pk)
            
            if conflicting_entries.exists():
                conflicting = conflicting_entries.first()
                raise ValidationError({
                    'teacher': f'Teacher is already assigned to {conflicting.timetable} at this time slot.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.time_slot.is_break:
            return f"{self.timetable} - {self.time_slot.name}"
        return f"{self.timetable} - {self.time_slot.name}: {self.subject.name if self.subject else 'N/A'}"

