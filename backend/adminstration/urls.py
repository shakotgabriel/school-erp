from rest_framework import routers
from .views import (
    AcademicYearViewSet, TermViewSet, SchoolClassViewSet,
    StreamViewSet, SectionViewSet, SubjectViewSet
)

router = routers.DefaultRouter()
router.register(r'academic-years', AcademicYearViewSet)
router.register(r'terms', TermViewSet)
router.register(r'classes', SchoolClassViewSet)
router.register(r'streams', StreamViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'subjects', SubjectViewSet)

urlpatterns = router.urls
