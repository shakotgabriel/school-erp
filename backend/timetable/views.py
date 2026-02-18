from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from users.permissions import IsAdminOrTeacher, IsAdmin
from .models import TimeSlot, Timetable, TimetableEntry
from .serializers import (
    TimeSlotSerializer,
    TimetableSerializer,
    TimetableDetailSerializer,
    TimetableEntrySerializer
)


class TimeSlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing time slots.
    Admins and teachers can manage time slots.
    """
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAdminOrTeacher]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['day_of_week', 'is_break', 'is_active']
    search_fields = ['name']
    ordering_fields = ['day_of_week', 'order', 'start_time']
    ordering = ['day_of_week', 'order']

    @action(detail=False, methods=['get'])
    def by_day(self, request):
        """Get time slots grouped by day of week"""
        day = request.query_params.get('day')
        if not day:
            return Response(
                {'error': 'day parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        time_slots = self.queryset.filter(day_of_week=day, is_active=True)
        serializer = self.get_serializer(time_slots, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active time slots"""
        active_slots = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_slots, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def weekly_schedule(self, request):
        """Get time slots organized by day for the entire week"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        weekly_data = {}
        
        for day in days:
            day_slots = self.queryset.filter(day_of_week=day, is_active=True)
            weekly_data[day] = self.get_serializer(day_slots, many=True).data
        
        return Response(weekly_data)


class TimetableViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing timetables.
    Admins and teachers can manage timetables.
    """
    queryset = Timetable.objects.select_related(
        'school_class', 'section', 'academic_year', 'term', 'created_by'
    ).prefetch_related('entries')
    permission_classes = [IsAdminOrTeacher]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school_class', 'section', 'academic_year', 'term', 'is_active']
    search_fields = ['name', 'school_class__name', 'section__name']
    ordering_fields = ['created_at', 'school_class__name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TimetableDetailSerializer
        return TimetableSerializer

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active timetables"""
        active_timetables = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_timetables, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_class(self, request):
        """Get timetables for a specific class and optional section"""
        class_id = request.query_params.get('class_id')
        section_id = request.query_params.get('section_id')
        
        if not class_id:
            return Response(
                {'error': 'class_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(school_class_id=class_id)
        
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_teacher(self, request):
        """Get timetables where the teacher is assigned"""
        teacher_id = request.query_params.get('teacher_id')
        
        if not teacher_id:
            # If no teacher_id provided, use current user if they're a teacher
            if request.user.role == 'teacher':
                teacher_id = request.user.id
            else:
                return Response(
                    {'error': 'teacher_id parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        timetables = self.queryset.filter(
            entries__teacher_id=teacher_id
        ).distinct()
        
        serializer = self.get_serializer(timetables, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a timetable for a different term or class"""
        original = self.get_object()
        
        # Get new academic year and term from request
        new_term_id = request.data.get('term_id')
        new_academic_year_id = request.data.get('academic_year_id')
        
        if not new_term_id or not new_academic_year_id:
            return Response(
                {'error': 'Both term_id and academic_year_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create duplicate timetable
        new_timetable = Timetable.objects.create(
            name=f"{original.name} (Copy)",
            school_class=original.school_class,
            section=original.section,
            academic_year_id=new_academic_year_id,
            term_id=new_term_id,
            created_by=request.user
        )
        
        # Copy all entries
        for entry in original.entries.all():
            TimetableEntry.objects.create(
                timetable=new_timetable,
                time_slot=entry.time_slot,
                subject=entry.subject,
                teacher=entry.teacher,
                room=entry.room,
                notes=entry.notes
            )
        
        serializer = self.get_serializer(new_timetable)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TimetableEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing timetable entries.
    Admins and teachers can manage entries.
    """
    queryset = TimetableEntry.objects.select_related(
        'timetable', 'time_slot', 'subject', 'teacher'
    )
    serializer_class = TimetableEntrySerializer
    permission_classes = [IsAdminOrTeacher]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['timetable', 'time_slot', 'subject', 'teacher']
    search_fields = ['subject__name', 'teacher__first_name', 'teacher__last_name', 'room']
    ordering_fields = ['time_slot__day_of_week', 'time_slot__order']
    ordering = ['time_slot__day_of_week', 'time_slot__order']

    @action(detail=False, methods=['get'])
    def by_timetable(self, request):
        """Get all entries for a specific timetable"""
        timetable_id = request.query_params.get('timetable_id')
        if not timetable_id:
            return Response(
                {'error': 'timetable_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        entries = self.queryset.filter(timetable_id=timetable_id)
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def teacher_schedule(self, request):
        """Get a teacher's complete teaching schedule"""
        teacher_id = request.query_params.get('teacher_id')
        
        if not teacher_id:
            # If no teacher_id provided, use current user if they're a teacher
            if request.user.role == 'teacher':
                teacher_id = request.user.id
            else:
                return Response(
                    {'error': 'teacher_id parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        entries = self.queryset.filter(teacher_id=teacher_id)
        
        # Group by day
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        schedule = {}
        
        for day in days:
            day_entries = entries.filter(time_slot__day_of_week=day)
            if day_entries.exists():
                schedule[day] = self.get_serializer(day_entries, many=True).data
        
        return Response(schedule)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple timetable entries at once"""
        entries_data = request.data.get('entries', [])
        
        if not entries_data:
            return Response(
                {'error': 'entries array is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_entries = []
        errors = []
        
        for entry_data in entries_data:
            serializer = self.get_serializer(data=entry_data)
            if serializer.is_valid():
                serializer.save()
                created_entries.append(serializer.data)
            else:
                errors.append({
                    'data': entry_data,
                    'errors': serializer.errors
                })
        
        return Response({
            'created': created_entries,
            'errors': errors,
            'summary': {
                'total': len(entries_data),
                'created': len(created_entries),
                'failed': len(errors)
            }
        }, status=status.HTTP_201_CREATED if created_entries else status.HTTP_400_BAD_REQUEST)

