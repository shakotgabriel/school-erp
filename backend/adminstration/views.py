
from rest_framework import viewsets
from .models import AcademicYear, Term, SchoolClass, Stream, Section, Subject
from .serializers import (
	AcademicYearSerializer, TermSerializer, SchoolClassSerializer,
	StreamSerializer, SectionSerializer, SubjectSerializer
)
from users.permissions import IsAdmin

class AcademicYearViewSet(viewsets.ModelViewSet):
	queryset = AcademicYear.objects.all()
	serializer_class = AcademicYearSerializer
	permission_classes = [IsAdmin]

class TermViewSet(viewsets.ModelViewSet):
	queryset = Term.objects.all()
	serializer_class = TermSerializer
	permission_classes = [IsAdmin]

class SchoolClassViewSet(viewsets.ModelViewSet):
	queryset = SchoolClass.objects.all()
	serializer_class = SchoolClassSerializer
	permission_classes = [IsAdmin]

class StreamViewSet(viewsets.ModelViewSet):
	queryset = Stream.objects.all()
	serializer_class = StreamSerializer
	permission_classes = [IsAdmin]

class SectionViewSet(viewsets.ModelViewSet):
	queryset = Section.objects.all()
	serializer_class = SectionSerializer
	permission_classes = [IsAdmin]

class SubjectViewSet(viewsets.ModelViewSet):
	queryset = Subject.objects.all()
	serializer_class = SubjectSerializer
	permission_classes = [IsAdmin]
