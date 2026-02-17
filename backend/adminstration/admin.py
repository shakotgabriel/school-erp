
from .models import AcademicYear, Term, SchoolClass, Stream, Section, Subject


import django.contrib.admin as admin

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
	list_display = ("name", "start_date", "end_date", "is_active")
	list_filter = ("is_active",)
	search_fields = ("name",)

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
	list_display = ("name", "academic_year", "start_date", "end_date", "is_active")
	list_filter = ("academic_year", "is_active")
	search_fields = ("name",)

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
	list_display = ("name", "code", "level", "is_active")
	list_filter = ("is_active",)
	search_fields = ("name", "code")

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
	list_display = ("name", "school_class", "is_active")
	list_filter = ("school_class", "is_active")
	search_fields = ("name",)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
	list_display = ("name", "school_class", "stream", "class_teacher", "capacity", "is_active")
	list_filter = ("school_class", "stream", "is_active")
	search_fields = ("name",)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
	list_display = ("name", "code", "is_optional", "is_active")
	list_filter = ("is_optional", "is_active")
	search_fields = ("name", "code")
