

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Guardian, AdmissionApplication
from .serializers import GuardianSerializer, AdmissionApplicationSerializer
from users.permissions import IsAdmin, IsAdminOrHR
from students.models import StudentProfile, Enrollment
from students.serializers import StudentProfileSerializer, EnrollmentSerializer

class GuardianViewSet(viewsets.ModelViewSet):
	queryset = Guardian.objects.all()
	serializer_class = GuardianSerializer
	permission_classes = [IsAdmin]

class AdmissionApplicationViewSet(viewsets.ModelViewSet):
	queryset = AdmissionApplication.objects.all()
	serializer_class = AdmissionApplicationSerializer
	def get_permissions(self):
		if self.action == 'accept_application':
			return [IsAdminOrHR()]
		return [IsAdmin()]

	@action(detail=True, methods=["post"], url_path="accept")
	def accept_application(self, request, pk=None):
		app = self.get_object()
		if app.status == "accepted":
			return Response({"detail": "Already accepted."}, status=status.HTTP_400_BAD_REQUEST)
		# Create StudentProfile
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
		# Create Enrollment
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
