
from .models import StudentProfile, Enrollment

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
	list_display = ("first_name", "last_name", "dob", "gender", "guardian")
	search_fields = ("first_name", "last_name")

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
	list_display = ("student", "academic_year", "school_class", "section", "is_active", "enrolled_on")
	list_filter = ("academic_year", "school_class", "section", "is_active")
