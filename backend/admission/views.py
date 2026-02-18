

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Guardian, AdmissionApplication
from .serializers import GuardianSerializer, AdmissionApplicationSerializer
from users.permissions import IsAdmin, IsAdminOrHR
from students.models import StudentProfile, Enrollment
from students.serializers import StudentProfileSerializer, EnrollmentSerializer

class GuardianViewSet(viewsets.ModelViewSet):
	queryset = Guardian.objects.all()
	serializer_class = GuardianSerializer
	permission_classes = [IsAdmin]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	filterset_fields = ['phone', 'email']
	search_fields = ['first_name', 'last_name', 'phone', 'email']
	ordering_fields = ['first_name', 'last_name']

class AdmissionApplicationViewSet(viewsets.ModelViewSet):
	queryset = AdmissionApplication.objects.select_related('preferred_class', 'preferred_academic_year', 'guardian', 'submitted_by').all()
	serializer_class = AdmissionApplicationSerializer
	def get_permissions(self):
		if self.action == 'accept_application':
			return [IsAdminOrHR()]
		return [IsAdmin()]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	filterset_fields = ['status', 'preferred_class', 'preferred_academic_year', 'guardian']
	search_fields = ['first_name', 'last_name', 'guardian__first_name', 'guardian__last_name']
	ordering_fields = ['applied_on', 'first_name', 'last_name']

	@action(detail=True, methods=["post"], url_path="accept")
	def accept_application(self, request, pk=None):
		app = self.get_object()
		if app.status == "accepted":
			return Response({"detail": "Already accepted."}, status=status.HTTP_400_BAD_REQUEST)
		student = StudentProfile.objects.create(
			first_name=app.first_name,
			middle_name=app.middle_name,
			last_name=app.last_name,
			dob=app.dob,
			gender=app.gender,
			religion=app.religion,
			guardian=app.guardian,
			admission_application=app,
		)
		enrollment = Enrollment.objects.create(
			student=student,
			academic_year=app.preferred_academic_year,
			school_class=app.preferred_class,
		)
		app.status = "accepted"
		app.save(update_fields=["status"])
		return Response({
			"student": StudentProfileSerializer(student).data,
			"enrollment": EnrollmentSerializer(enrollment).data,
		}, status=status.HTTP_201_CREATED)
