from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TimeSlotViewSet, TimetableViewSet, TimetableEntryViewSet

router = DefaultRouter()
router.register(r'time-slots', TimeSlotViewSet, basename='time-slot')
router.register(r'timetables', TimetableViewSet, basename='timetable')
router.register(r'entries', TimetableEntryViewSet, basename='timetable-entry')

urlpatterns = [
    path('', include(router.urls)),
]
