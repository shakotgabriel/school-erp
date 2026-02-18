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
    list_display = ['invoice_number', 'student', 'total_amount', 'paid_amount', 'balance', 'status', 'due_date']
    list_filter = ['status', 'issue_date', 'academic_year', 'term']
    search_fields = ['invoice_number', 'student__user__first_name', 'student__user__last_name']
    ordering = ['-issue_date']
    readonly_fields = ['invoice_number', 'balance', 'created_at', 'updated_at']



@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'expense_date', 'recorded_by']
    list_filter = ['category', 'expense_date']
    search_fields = ['description']
    ordering = ['-expense_date']
    readonly_fields = ['created_at', 'updated_at']



@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'total_budget', 'total_expenses', 'remaining_budget']
    search_fields = ['academic_year__name', 'description']
    ordering = ['-academic_year__start_date']
    readonly_fields = ['total_expenses', 'remaining_budget', 'created_at', 'updated_at']


