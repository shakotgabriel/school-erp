from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from adminstration.models import AcademicYear, SchoolClass

class Guardian(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	phone = models.CharField(max_length=20)
	email = models.EmailField(blank=True, null=True)
	relationship = models.CharField(max_length=30, blank=True, null=True)
	address = models.CharField(max_length=255, blank=True, null=True)

	def __str__(self):
		return f"{self.first_name} {self.last_name} ({self.phone})"

class AdmissionApplication(models.Model):
	STATUS_CHOICES = [
		("draft", "Draft"),
		("submitted", "Submitted"),
		("accepted", "Accepted"),
		("rejected", "Rejected"),
		("waitlisted", "Waitlisted"),
	]
	first_name = models.CharField(max_length=50)
	middle_name = models.CharField(max_length=50, blank=True, null=True)
	last_name = models.CharField(max_length=50)
	dob = models.DateField()
	gender = models.CharField(max_length=10)
	religion = models.CharField(max_length=30, blank=True, null=True)
	preferred_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name="applications")
	preferred_academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="applications")
	guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, related_name="applications")
	previous_school = models.CharField(max_length=100, blank=True, null=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
	applied_on = models.DateTimeField(auto_now_add=True)
	submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="admission_applications")
	notes = models.TextField(blank=True, null=True)

	class Meta:
		ordering = ["-applied_on"]
		indexes = [
			models.Index(fields=["status", "preferred_class", "preferred_academic_year"]),
		]

	def clean(self):
		pass

	def __str__(self):
		return f"{self.first_name} {self.last_name} ({self.preferred_class})"
