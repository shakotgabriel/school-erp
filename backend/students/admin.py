
from .models import StudentProfile, Enrollment
from .models import MedicalRecord, DisciplineRecord
from .models import TeacherAssignment

import django.contrib.admin as admin

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
	list_display = ("admission_number", "first_name", "last_name", "dob", "gender", "guardian")
	search_fields = ("admission_number", "first_name", "last_name")

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
	list_display = ("student", "academic_year", "school_class", "section", "is_active", "enrolled_on")
	list_filter = ("academic_year", "school_class", "section", "is_active")

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
	list_display = ("student", "record_date", "doctor")
	search_fields = ("student__first_name", "student__last_name", "doctor")

@admin.register(DisciplineRecord)
class DisciplineRecordAdmin(admin.ModelAdmin):
	list_display = ("student", "record_date", "incident", "reported_by")
	search_fields = ("student__first_name", "student__last_name", "incident", "reported_by")

@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
	list_display = ("teacher", "subject", "school_class", "section", "academic_year", "assigned_on")
	list_filter = ("academic_year", "school_class", "subject", "teacher")
	search_fields = ("teacher__email", "subject__name", "school_class__name")
