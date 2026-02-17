from rest_framework import serializers
from .models import StudentProfile, Enrollment
from adminstration.models import AcademicYear, SchoolClass, Section
from admission.models import Guardian, AdmissionApplication
from .models import TeacherAssignment

class StudentProfileSerializer(serializers.ModelSerializer):
    guardian = serializers.PrimaryKeyRelatedField(queryset=Guardian.objects.all(), required=False, allow_null=True)
    admission_application = serializers.PrimaryKeyRelatedField(queryset=AdmissionApplication.objects.all(), required=False, allow_null=True)
    class Meta:
        model = StudentProfile
        fields = "__all__"

class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all())
    academic_year = serializers.PrimaryKeyRelatedField(queryset=AcademicYear.objects.all())
    school_class = serializers.PrimaryKeyRelatedField(queryset=SchoolClass.objects.all())
    section = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all(), required=False, allow_null=True)
    class Meta:
        model = Enrollment
        fields = "__all__"

class TeacherAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherAssignment
        fields = "__all__"
class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = "__all__"

class DisciplineRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisciplineRecord
        fields = "__all__"
