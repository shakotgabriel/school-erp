from django.conf import settings
from django.db import models
from adminstration.models import AcademicYear, SchoolClass, Section

class StudentProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile", blank=True, null=True)
	first_name = models.CharField(max_length=50)
	middle_name = models.CharField(max_length=50, blank=True, null=True)
	last_name = models.CharField(max_length=50)
	dob = models.DateField()
	gender = models.CharField(max_length=10)
	religion = models.CharField(max_length=30, blank=True, null=True)
	guardian = models.ForeignKey('admission.Guardian', on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
	admission_application = models.OneToOneField('admission.AdmissionApplication', on_delete=models.SET_NULL, null=True, blank=True, related_name="student_profile")
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.first_name} {self.last_name}"

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
