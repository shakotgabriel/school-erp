from django.contrib import admin
from .models import Dashboard, DashboardWidget


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'is_active', 'created_by', 'created_at')
    list_filter = ('type', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'dashboard', 'widget_type', 'data_source', 'position', 'is_active')
    list_filter = ('widget_type', 'chart_type', 'is_active', 'dashboard')
    search_fields = ('title', 'data_source')
    ordering = ('dashboard', 'position')

