from django.db import models
from django.conf import settings
from adminstration.models import Subject, AcademicYear, SchoolClass, Section

class TeacherAssignment(models.Model):
	teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={"role": "teacher"}, related_name="assignments")
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="teacher_assignments")
	school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="teacher_assignments")
	section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name="teacher_assignments")
	academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="teacher_assignments")
	assigned_on = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("teacher", "subject", "school_class", "section", "academic_year")

	def __str__(self):
		return f"{self.teacher} - {self.subject} - {self.school_class} - {self.section or ''} ({self.academic_year})"


class StudentProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile", blank=True, null=True)
	admission_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
	first_name = models.CharField(max_length=50)
	middle_name = models.CharField(max_length=50, blank=True, null=True)
	last_name = models.CharField(max_length=50)
	dob = models.DateField()
	gender = models.CharField(max_length=10)
	religion = models.CharField(max_length=30, blank=True, null=True)
	guardian = models.ForeignKey('admission.Guardian', on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
	admission_application = models.OneToOneField('admission.AdmissionApplication', on_delete=models.SET_NULL, null=True, blank=True, related_name="student_profile")
	created_at = models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		if not self.admission_number:
			import random
			from datetime import datetime
			date_str = datetime.now().strftime('%Y%m%d')
			rand = random.randint(1000, 9999)
			self.admission_number = f"S{date_str}{rand}"
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.first_name} {self.last_name}"

class MedicalRecord(models.Model):
	student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="medical_records")
	record_date = models.DateField(auto_now_add=True)
	description = models.TextField()
	doctor = models.CharField(max_length=100, blank=True, null=True)
	notes = models.TextField(blank=True, null=True)

	def __str__(self):
		return f"MedicalRecord({self.student}, {self.record_date})"

class DisciplineRecord(models.Model):
	student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="discipline_records")
	record_date = models.DateField(auto_now_add=True)
	incident = models.TextField()
	action_taken = models.TextField(blank=True, null=True)
	reported_by = models.CharField(max_length=100, blank=True, null=True)
	notes = models.TextField(blank=True, null=True)

	def __str__(self):
		return f"DisciplineRecord({self.student}, {self.record_date})"

class Enrollment(models.Model):
	student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="enrollments")
	academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="enrollments")
	school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name="enrollments")
	section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name="enrollments")
	enrolled_on = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		unique_together = ("student", "academic_year")

	def __str__(self):
		return f"{self.student} - {self.school_class} ({self.academic_year})"
