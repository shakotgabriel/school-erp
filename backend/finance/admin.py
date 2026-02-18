from django.contrib import admin
from .models import FeeStructure, FeePayment, Invoice, Expense, Budget


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'school_class', 'academic_year', 'amount', 'frequency', 'is_mandatory', 'is_active']
    list_filter = ['is_active', 'is_mandatory', 'frequency', 'academic_year', 'school_class']
    search_fields = ['name', 'description']
    ordering = ['-created_at']


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'fee_structure', 'amount_paid', 'payment_date', 'payment_method', 'status', 'recorded_by']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['student__first_name', 'student__last_name', 'transaction_reference']
    ordering = ['-payment_date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'student', 'total_amount', 'amount_paid', 'balance', 'status', 'due_date']
    list_filter = ['status', 'issue_date', 'academic_year', 'term']
    search_fields = ['invoice_number', 'student__first_name', 'student__last_name']
    ordering = ['-issue_date']
    readonly_fields = ['invoice_number', 'balance', 'issue_date', 'created_at', 'updated_at']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'amount', 'expense_date', 'vendor', 'approved_by', 'recorded_by']
    list_filter = ['category', 'expense_date', 'academic_year', 'term']
    search_fields = ['title', 'description', 'vendor']
    ordering = ['-expense_date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_year', 'total_budget', 'spent_amount', 'remaining_amount', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'academic_year', 'term']
    search_fields = ['name', 'description']
    ordering = ['-start_date']
    readonly_fields = ['remaining_amount', 'created_at', 'updated_at']

