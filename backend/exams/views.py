
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Exam, ExamResult
from .serializers import ExamSerializer, ExamResultSerializer

class ExamViewSet(viewsets.ModelViewSet):
	queryset = Exam.objects.select_related('academic_year', 'term', 'school_class', 'section', 'subject').all()
	serializer_class = ExamSerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	filterset_fields = ['academic_year', 'term', 'school_class', 'section', 'subject']
	search_fields = ['name']
	ordering_fields = ['date', 'total_marks']

class ExamResultViewSet(viewsets.ModelViewSet):
	queryset = ExamResult.objects.select_related('exam', 'student').all()
	serializer_class = ExamResultSerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	filterset_fields = ['exam', 'student', 'grade']
	search_fields = ['student__first_name', 'student__last_name']
	ordering_fields = ['marks_obtained']
