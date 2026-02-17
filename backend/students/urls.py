
from rest_framework import routers
from .views import StudentProfileViewSet, EnrollmentViewSet, MedicalRecordViewSet, DisciplineRecordViewSet
from .views import TeacherAssignmentViewSet

router = routers.DefaultRouter()
router.register(r'students', StudentProfileViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'medical-records', MedicalRecordViewSet)
router.register(r'discipline-records', DisciplineRecordViewSet)
router.register(r'teacher-assignments', TeacherAssignmentViewSet)

urlpatterns = router.urls
