from django.urls import path
from .views import (
    overview_dashboard,
    student_dashboard,
    finance_dashboard,
    staff_dashboard,
    academic_dashboard
)

urlpatterns = [
    path('overview/', overview_dashboard, name='overview-dashboard'),
    path('students/', student_dashboard, name='student-dashboard'),
    path('finance/', finance_dashboard, name='finance-dashboard'),
    path('staff/', staff_dashboard, name='staff-dashboard'),
    path('academic/', academic_dashboard, name='academic-dashboard'),
]
