from django.db import models
from django.conf import settings


class Dashboard(models.Model):
    """Represents different dashboard types for different user roles"""
    DASHBOARD_TYPE_CHOICES = (
        ('overview', 'Overview Dashboard'),
        ('student', 'Student Dashboard'),
        ('finance', 'Finance Dashboard'),
        ('staff', 'Staff Dashboard'),
        ('academic', 'Academic Dashboard'),
    )

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=DASHBOARD_TYPE_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_dashboards'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"  # type: ignore[attr-defined]


class DashboardWidget(models.Model):
    """Represents individual widgets/metrics on a dashboard"""
    WIDGET_TYPE_CHOICES = (
        ('metric', 'Single Metric'),
        ('chart', 'Chart'),
        ('table', 'Data Table'),
        ('progress', 'Progress Bar'),
    )

    CHART_TYPE_CHOICES = (
        ('bar', 'Bar Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        ('doughnut', 'Doughnut Chart'),
    )

    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets'
    )
    title = models.CharField(max_length=200)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPE_CHOICES, default='metric')
    chart_type = models.CharField(max_length=20, choices=CHART_TYPE_CHOICES, blank=True, null=True)
    data_source = models.CharField(max_length=100)  # e.g., 'users.total', 'finance.revenue'
    configuration = models.JSONField(blank=True, null=True)  # For custom config like colors, filters
    position = models.PositiveIntegerField(default=0)  # For ordering
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', 'title']
        unique_together = ['dashboard', 'data_source']

    def __str__(self):
        return f"{self.dashboard.name} - {self.title}"

