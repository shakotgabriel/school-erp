

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import StudentProfile, Enrollment, MedicalRecord, DisciplineRecord, TeacherAssignment
from .serializers import StudentProfileSerializer, EnrollmentSerializer, MedicalRecordSerializer, DisciplineRecordSerializer, TeacherAssignmentSerializer
from users.permissions import IsAdmin, IsTeacher, IsStudent, IsOwnerOrReadOnly, IsAdminOrRole

class StudentProfileViewSet(viewsets.ModelViewSet):
	queryset = StudentProfile.objects.all()
	serializer_class = StudentProfileSerializer
	def get_permissions(self):
		if self.action in ['list', 'retrieve']:
			return [IsAdminOrRole('student')]
		return [IsAdmin()]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = ['admission_number', 'guardian', 'admission_application']
	search_fields = ['first_name', 'last_name', 'admission_number']

	@action(detail=False, methods=["post"], url_path="bulk-create")
	def bulk_create(self, request):
		serializer = self.get_serializer(data=request.data, many=True)
		serializer.is_valid(raise_exception=True)
		students = serializer.save()
		return Response(self.get_serializer(students, many=True).data, status=status.HTTP_201_CREATED)

class EnrollmentViewSet(viewsets.ModelViewSet):
	queryset = Enrollment.objects.all()
	serializer_class = EnrollmentSerializer
	def get_permissions(self):
		if self.action in ['list', 'retrieve']:
			return [IsAdminOrRole('student')]
		return [IsAdmin()]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = ['student', 'academic_year', 'school_class', 'section']
	search_fields = []

class MedicalRecordViewSet(viewsets.ModelViewSet):
	queryset = MedicalRecord.objects.all()
	serializer_class = MedicalRecordSerializer
	def get_permissions(self):
		if self.action in ['list', 'retrieve']:
			return [IsAdminOrRole('student')]
		return [IsAdmin()]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = ['student']
	search_fields = ['description', 'doctor', 'notes']

class TeacherAssignmentViewSet(viewsets.ModelViewSet):
	queryset = TeacherAssignment.objects.all()
	serializer_class = TeacherAssignmentSerializer
	def get_permissions(self):
		if self.action in ['list', 'retrieve']:
			return [IsAdminOrRole('teacher')]
		return [IsAdmin()]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = ['teacher', 'subject', 'school_class', 'section', 'academic_year']
	search_fields = []
class DisciplineRecordViewSet(viewsets.ModelViewSet):
	queryset = DisciplineRecord.objects.all()
	serializer_class = DisciplineRecordSerializer
	def get_permissions(self):
		if self.action in ['list', 'retrieve']:
			return [IsAdminOrRole('student')]
		return [IsAdmin()]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = ['student']
	search_fields = ['incident', 'action_taken', 'reported_by']
