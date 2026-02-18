from rest_framework import serializers
from .models import AcademicYear, Term, SchoolClass, Stream, Section, Subject

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"

class TermSerializer(serializers.ModelSerializer):
    academic_year = serializers.SlugRelatedField(slug_field="name", queryset=AcademicYear.objects.all())
    class Meta:
        model = Term
        fields = "__all__"

class SchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = "__all__"

class StreamSerializer(serializers.ModelSerializer):
    school_class = serializers.SlugRelatedField(slug_field="name", queryset=SchoolClass.objects.all())
    class Meta:
        model = Stream
        fields = "__all__"

class SectionSerializer(serializers.ModelSerializer):
    school_class = serializers.SlugRelatedField(slug_field="name", queryset=SchoolClass.objects.all())
    stream = serializers.SlugRelatedField(slug_field="name", queryset=Stream.objects.all(), allow_null=True, required=False)
    from users.models import User
    class_teacher = serializers.SlugRelatedField(slug_field="email", queryset=User.objects.filter(role='teacher'), allow_null=True, required=False)
    class Meta:
        model = Section
        fields = "__all__"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from users.models import User
        self.fields['class_teacher'].queryset = User.objects.filter(role='teacher')

class SubjectSerializer(serializers.ModelSerializer):
    school_classes = serializers.SlugRelatedField(slug_field="name", queryset=SchoolClass.objects.all(), many=True)
    class Meta:
        model = Subject
        fields = "__all__"
