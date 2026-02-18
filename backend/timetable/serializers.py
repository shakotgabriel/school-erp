from rest_framework import serializers
from .models import TimeSlot, Timetable, TimetableEntry
from adminstration.models import AcademicYear, Term, SchoolClass, Section, Subject


class TimeSlotSerializer(serializers.ModelSerializer):
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = TimeSlot
        fields = [
            'id', 'name', 'day_of_week', 'day_of_week_display', 'start_time',
            'end_time', 'is_break', 'order', 'is_active'
        ]

    def validate(self, data):
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError({'end_time': 'End time must be later than start time.'})
        return data


class TimetableEntrySerializer(serializers.ModelSerializer):
    time_slot_name = serializers.CharField(source='time_slot.name', read_only=True)
    time_slot_detail = TimeSlotSerializer(source='time_slot', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    day_of_week = serializers.CharField(source='time_slot.day_of_week', read_only=True)
    day_of_week_display = serializers.CharField(source='time_slot.get_day_of_week_display', read_only=True)

    class Meta:
        model = TimetableEntry
        fields = [
            'id', 'timetable', 'time_slot', 'time_slot_name', 'time_slot_detail',
            'day_of_week', 'day_of_week_display', 'subject', 'subject_name',
            'subject_code', 'teacher', 'teacher_name', 'room', 'notes'
        ]

    def get_teacher_name(self, obj):
        if obj.teacher:
            return f"{obj.teacher.first_name} {obj.teacher.last_name}"
        return None

    def validate(self, data):
        time_slot = data.get('time_slot')
        subject = data.get('subject')
        teacher = data.get('teacher')

        if time_slot and time_slot.is_break:
            if subject or teacher:
                raise serializers.ValidationError('Break periods cannot have subjects or teachers assigned.')
        else:
            if not subject:
                raise serializers.ValidationError({'subject': 'Non-break periods must have a subject assigned.'})

        return data


class TimetableSerializer(serializers.ModelSerializer):
    school_class_name = serializers.CharField(source='school_class.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    entries = TimetableEntrySerializer(many=True, read_only=True)
    entries_count = serializers.SerializerMethodField()

    class Meta:
        model = Timetable
        fields = [
            'id', 'name', 'school_class', 'school_class_name', 'section',
            'section_name', 'academic_year', 'academic_year_name', 'term',
            'term_name', 'is_active', 'created_by', 'created_by_name',
            'entries', 'entries_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None

    def get_entries_count(self, obj):
        return obj.entries.count()

    def validate(self, data):
        section = data.get('section')
        school_class = data.get('school_class')
        term = data.get('term')
        academic_year = data.get('academic_year')

        if section and school_class:
            if section.school_class != school_class:
                raise serializers.ValidationError({'section': 'Selected section does not belong to this class.'})

        if term and academic_year:
            if term.academic_year != academic_year:
                raise serializers.ValidationError({'term': 'Selected term does not belong to the selected academic year.'})

        return data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TimetableDetailSerializer(TimetableSerializer):
    """More detailed serializer that groups entries by day"""
    entries_by_day = serializers.SerializerMethodField()

    class Meta(TimetableSerializer.Meta):
        fields = TimetableSerializer.Meta.fields + ['entries_by_day']

    def get_entries_by_day(self, obj):
        entries = obj.entries.select_related('time_slot', 'subject', 'teacher').all()
        
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        entries_by_day = {}
        
        for day in days:
            day_entries = entries.filter(time_slot__day_of_week=day)
            if day_entries.exists():
                entries_by_day[day] = TimetableEntrySerializer(day_entries, many=True).data
        
        return entries_by_day
