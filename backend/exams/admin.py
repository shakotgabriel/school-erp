from django.contrib import admin
from .models import Exam, ExamResult

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'school_class', 'section', 'term', 'date', 'total_marks']
    list_filter = ['academic_year', 'term', 'school_class', 'subject']
    search_fields = ['name', 'subject__name', 'school_class__name']
    date_hierarchy = 'date'

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'marks_obtained', 'grade']
    list_filter = ['exam__academic_year', 'exam__term', 'exam__school_class', 'grade']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number', 'exam__name']
    readonly_fields = ['grade']
