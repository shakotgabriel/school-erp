from rest_framework import serializers
from .models import FeeStructure, FeePayment, Invoice, Expense, Budget
from students.models import StudentProfile
from adminstration.models import AcademicYear, Term, SchoolClass


class FeeStructureSerializer(serializers.ModelSerializer):
    school_class_name = serializers.CharField(source='school_class.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)

    class Meta:
        model = FeeStructure
        fields = [
            'id', 'name', 'description', 'school_class', 'school_class_name',
            'academic_year', 'academic_year_name', 'amount', 'frequency',
            'is_mandatory', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class FeePaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    fee_structure_name = serializers.CharField(source='fee_structure.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    recorded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = FeePayment
        fields = [
            'id', 'student', 'student_name', 'fee_structure', 'fee_structure_name',
            'term', 'term_name', 'amount_paid', 'payment_date', 'payment_method',
            'transaction_reference', 'status', 'remarks', 'recorded_by',
            'recorded_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'recorded_by']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"

    def get_recorded_by_name(self, obj):
        if obj.recorded_by:
            return f"{obj.recorded_by.first_name} {obj.recorded_by.last_name}"
        return None

    def validate_amount_paid(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)


class InvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'student', 'student_name', 'academic_year',
            'academic_year_name', 'term', 'term_name', 'total_amount', 'amount_paid',
            'balance', 'issue_date', 'due_date', 'status', 'notes', 'created_by',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['invoice_number', 'balance', 'issue_date', 'created_at', 'updated_at', 'created_by']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None

    def validate(self, data):
        if data.get('total_amount', 0) <= 0:
            raise serializers.ValidationError({'total_amount': 'Total amount must be greater than zero.'})
        if data.get('amount_paid', 0) > data.get('total_amount', 0):
            raise serializers.ValidationError({'amount_paid': 'Amount paid cannot exceed total amount.'})
        return data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ExpenseSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    approved_by_name = serializers.SerializerMethodField()
    recorded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'description', 'category', 'amount', 'expense_date',
            'academic_year', 'academic_year_name', 'term', 'term_name', 'vendor',
            'receipt_number', 'approved_by', 'approved_by_name', 'recorded_by',
            'recorded_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'recorded_by']

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}"
        return None

    def get_recorded_by_name(self, obj):
        if obj.recorded_by:
            return f"{obj.recorded_by.first_name} {obj.recorded_by.last_name}"
        return None

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)


class BudgetSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            'id', 'name', 'description', 'academic_year', 'academic_year_name',
            'term', 'term_name', 'total_budget', 'spent_amount', 'remaining_amount',
            'status', 'start_date', 'end_date', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['remaining_amount', 'created_at', 'updated_at', 'created_by']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None

    def validate(self, data):
        if data.get('total_budget', 0) <= 0:
            raise serializers.ValidationError({'total_budget': 'Budget must be greater than zero.'})
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError({'end_date': 'End date must be later than start date.'})
        if data.get('spent_amount', 0) > data.get('total_budget', 0):
            raise serializers.ValidationError({'spent_amount': 'Spent amount cannot exceed total budget.'})
        return data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
