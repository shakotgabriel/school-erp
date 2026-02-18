from rest_framework import serializers
from .models import Department, StaffProfile, Leave, Attendance, Payroll
from django.utils import timezone


class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.SerializerMethodField()
    staff_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'description', 'head', 'head_name',
            'staff_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_head_name(self, obj):
        if obj.head:
            return f"{obj.head.first_name} {obj.head.last_name}"
        return None

    def get_staff_count(self, obj):
        return obj.staff_members.filter(is_active=True).count()


class StaffProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = StaffProfile
        fields = [
            'id', 'user', 'user_name', 'user_email', 'user_role', 'employee_id',
            'date_of_birth', 'age', 'gender', 'nationality', 'marital_status',
            'address', 'city', 'state', 'postal_code', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship',
            'department', 'department_name', 'position', 'employment_type',
            'date_of_joining', 'date_of_leaving', 'highest_qualification',
            'specialization', 'years_of_experience', 'basic_salary', 'bio',
            'photo', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['employee_id', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_age(self, obj):
        from datetime import date
        today = date.today()
        return today.year - obj.date_of_birth.year - (
            (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
        )

    def validate_basic_salary(self, value):
        if value <= 0:
            raise serializers.ValidationError("Basic salary must be greater than zero.")
        return value


class LeaveSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Leave
        fields = [
            'id', 'staff', 'staff_name', 'leave_type', 'leave_type_display',
            'start_date', 'end_date', 'total_days', 'reason', 'status',
            'status_display', 'approved_by', 'approved_by_name', 'approval_date',
            'rejection_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_days', 'approved_by', 'approval_date', 'created_at', 'updated_at']

    def get_staff_name(self, obj):
        return f"{obj.staff.first_name} {obj.staff.last_name}"

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}"
        return None

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError({'end_date': 'End date must be later than or equal to start date.'})
            
            data['total_days'] = (end_date - start_date).days + 1

        return data


class AttendanceSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    recorded_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id', 'staff', 'staff_name', 'date', 'status', 'status_display',
            'check_in_time', 'check_out_time', 'remarks', 'recorded_by',
            'recorded_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_staff_name(self, obj):
        return f"{obj.staff.first_name} {obj.staff.last_name}"

    def get_recorded_by_name(self, obj):
        if obj.recorded_by:
            return f"{obj.recorded_by.first_name} {obj.recorded_by.last_name}"
        return None

    def validate(self, data):
        check_in = data.get('check_in_time')
        check_out = data.get('check_out_time')

        if check_in and check_out:
            if check_in >= check_out:
                raise serializers.ValidationError({'check_out_time': 'Check-out time must be later than check-in time.'})

        return data

    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)


class PayrollSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    processed_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    month_name = serializers.SerializerMethodField()

    class Meta:
        model = Payroll
        fields = [
            'id', 'staff', 'staff_name', 'month', 'month_name', 'year',
            'basic_salary', 'allowances', 'deductions', 'net_salary',
            'payment_date', 'status', 'status_display', 'remarks',
            'processed_by', 'processed_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['net_salary', 'created_at', 'updated_at']

    def get_staff_name(self, obj):
        return f"{obj.staff.first_name} {obj.staff.last_name}"

    def get_processed_by_name(self, obj):
        if obj.processed_by:
            return f"{obj.processed_by.first_name} {obj.processed_by.last_name}"
        return None

    def get_month_name(self, obj):
        from datetime import date
        return date(obj.year, obj.month, 1).strftime('%B')

    def validate_month(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError("Month must be between 1 and 12.")
        return value

    def validate(self, data):
        basic_salary = data.get('basic_salary', 0)
        allowances = data.get('allowances', 0)
        deductions = data.get('deductions', 0)

        if basic_salary <= 0:
            raise serializers.ValidationError({'basic_salary': 'Basic salary must be greater than zero.'})
        
        if deductions > basic_salary + allowances:
            raise serializers.ValidationError({'deductions': 'Deductions cannot exceed basic salary plus allowances.'})

        return data

    def create(self, validated_data):
        validated_data['processed_by'] = self.context['request'].user
        return super().create(validated_data)
