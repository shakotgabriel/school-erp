from rest_framework import routers
from .views import GuardianViewSet, AdmissionApplicationViewSet

router = routers.DefaultRouter()
router.register(r'guardians', GuardianViewSet)
router.register(r'applications', AdmissionApplicationViewSet)

urlpatterns = router.urls
