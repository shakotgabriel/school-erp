from django.contrib import admin
from .models import Department, StaffProfile, Leave, Attendance, Payroll


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'head', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'department', 'position', 'employment_type', 'date_of_joining', 'is_active']
    list_filter = ['is_active', 'employment_type', 'department', 'user__role']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'user__email', 'position']
    readonly_fields = ['employee_id', 'created_at', 'updated_at']
    ordering = ['-date_of_joining']


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['staff', 'leave_type', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'leave_type', 'start_date']
    search_fields = ['staff__user__first_name', 'staff__user__last_name', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'date', 'status', 'check_in_time', 'check_out_time', 'recorded_by']
    list_filter = ['status', 'date']
    search_fields = ['staff__first_name', 'staff__last_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date']


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['staff', 'month', 'year', 'basic_salary', 'net_salary', 'status', 'payment_date']
    list_filter = ['status', 'year', 'month']
    search_fields = ['staff__first_name', 'staff__last_name']
    readonly_fields = ['net_salary', 'created_at', 'updated_at']
    ordering = ['-year', '-month']

