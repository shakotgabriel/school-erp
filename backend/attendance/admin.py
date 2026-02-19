from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'school_class', 'section', 'date', 'status', 'marked_by')
    list_filter = ('status', 'date', 'school_class', 'section', 'academic_year', 'term')
    search_fields = ('student__first_name', 'student__last_name', 'student__admission_number')
    ordering = ('-date', 'student__first_name')
    date_hierarchy = 'date'

