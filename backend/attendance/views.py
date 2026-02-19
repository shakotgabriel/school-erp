from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import Attendance
from .serializers import AttendanceSerializer
from users.permissions import IsAdmin, IsTeacher, IsAdminOrTeacher


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related(
        'student', 'enrollment', 'academic_year', 'term',
        'school_class', 'section', 'marked_by'
    ).all()
    serializer_class = AttendanceSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAdminOrTeacher()]
        return [IsAdmin()]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'student', 'enrollment', 'academic_year', 'term',
        'school_class', 'section', 'date', 'status'
    ]
    search_fields = [
        'student__first_name', 'student__last_name',
        'student__admission_number'
    ]
    ordering_fields = ['date', 'student__first_name', 'status', 'created_at']
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def class_attendance(self, request):
        """Get attendance for a specific class on a specific date"""
        class_id = request.query_params.get('class_id')
        date = request.query_params.get('date')
        if not class_id or not date:
            return Response(
                {'error': 'class_id and date parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        attendances = self.queryset.filter(
            school_class_id=class_id,
            date=date
        )
        serializer = self.get_serializer(attendances, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def student_attendance(self, request):
        """Get attendance history for a specific student"""
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response(
                {'error': 'student_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        attendances = self.queryset.filter(student_id=student_id)
        serializer = self.get_serializer(attendances, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def attendance_summary(self, request):
        """Get attendance summary statistics"""
        academic_year_id = request.query_params.get('academic_year')
        term_id = request.query_params.get('term')
        class_id = request.query_params.get('class')

        filters = Q()
        if academic_year_id:
            filters &= Q(academic_year_id=academic_year_id)
        if term_id:
            filters &= Q(term_id=term_id)
        if class_id:
            filters &= Q(school_class_id=class_id)

        attendances = self.queryset.filter(filters)

        summary = attendances.values('status').annotate(count=Count('id'))

        total_students = attendances.values('student').distinct().count()
        total_days = attendances.values('date').distinct().count()

        return Response({
            'total_students': total_students,
            'total_days': total_days,
            'by_status': list(summary)
        })

    @action(detail=False, methods=['post'])
    def bulk_mark(self, request):
        """Bulk mark attendance for a class"""
        attendances_data = request.data.get('attendances', [])
        if not attendances_data:
            return Response(
                {'error': 'attendances data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_attendances = []
        for attendance_data in attendances_data:
            serializer = self.get_serializer(data=attendance_data)
            if serializer.is_valid():
                attendance = serializer.save()
                created_attendances.append(attendance)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            self.get_serializer(created_attendances, many=True).data,
            status=status.HTTP_201_CREATED
        )

