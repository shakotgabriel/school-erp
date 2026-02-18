from django.contrib import admin
from .models import TimeSlot, Timetable, TimetableEntry


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['name', 'day_of_week', 'start_time', 'end_time', 'is_break', 'order', 'is_active']
    list_filter = ['day_of_week', 'is_break', 'is_active']
    search_fields = ['name']
    ordering = ['day_of_week', 'order', 'start_time']


class TimetableEntryInline(admin.TabularInline):
    model = TimetableEntry
    extra = 1
    fields = ['time_slot', 'subject', 'teacher_assignment']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['name', 'school_class', 'section', 'academic_year', 'term', 'is_active', 'created_by']
    list_filter = ['is_active', 'academic_year', 'term', 'school_class']
    search_fields = ['name', 'school_class__name', 'section__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TimetableEntryInline]


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ['timetable', 'time_slot', 'subject', 'get_teacher']
    list_filter = ['timetable__school_class', 'time_slot__day_of_week', 'subject']
    search_fields = ['timetable__name', 'subject__name', 'teacher_assignment__teacher__first_name', 'teacher_assignment__teacher__last_name']
    ordering = ['timetable', 'time_slot__day_of_week', 'time_slot__order']
    
    @admin.display(description='Teacher')
    def get_teacher(self, obj):
        if obj.teacher_assignment:
            return obj.teacher_assignment.teacher
        return '-'

