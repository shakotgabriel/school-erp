
from .models import Guardian, AdmissionApplication

import django.contrib.admin as admin

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
	list_display = ("first_name", "last_name", "phone", "email", "relationship")
	search_fields = ("first_name", "last_name", "phone", "email")

@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
	list_display = ("first_name", "last_name", "dob", "gender", "preferred_class", "preferred_academic_year", "status", "applied_on")
	list_filter = ("status", "preferred_class", "preferred_academic_year")
	search_fields = ("first_name", "last_name", "guardian__phone")
