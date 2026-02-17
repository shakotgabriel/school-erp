

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import StudentProfile, Enrollment, MedicalRecord, DisciplineRecord
from .serializers import StudentProfileSerializer, EnrollmentSerializer, MedicalRecordSerializer, DisciplineRecordSerializer
from .serializers import TeacherAssignmentSerializer
from users.permissions import IsAdmin

class StudentProfileViewSet(viewsets.ModelViewSet):
	queryset = StudentProfile.objects.all()
	serializer_class = StudentProfileSerializer
	permission_classes = [IsAdmin]

	@action(detail=False, methods=["post"], url_path="bulk-create")
	def bulk_create(self, request):
		serializer = self.get_serializer(data=request.data, many=True)
		serializer.is_valid(raise_exception=True)
		students = serializer.save()
		return Response(self.get_serializer(students, many=True).data, status=status.HTTP_201_CREATED)

class EnrollmentViewSet(viewsets.ModelViewSet):
	queryset = Enrollment.objects.all()
	serializer_class = EnrollmentSerializer
	permission_classes = [IsAdmin]

class MedicalRecordViewSet(viewsets.ModelViewSet):
	queryset = MedicalRecord.objects.all()
	serializer_class = MedicalRecordSerializer
	permission_classes = [IsAdmin]

class TeacherAssignmentViewSet(viewsets.ModelViewSet):
	queryset = TeacherAssignment.objects.all()
	serializer_class = TeacherAssignmentSerializer
	permission_classes = [IsAdmin]
class DisciplineRecordViewSet(viewsets.ModelViewSet):
	queryset = DisciplineRecord.objects.all()
	serializer_class = DisciplineRecordSerializer
	permission_classes = [IsAdmin]
