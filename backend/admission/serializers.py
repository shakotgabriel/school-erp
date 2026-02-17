from rest_framework import serializers
from .models import Guardian, AdmissionApplication
from adminstration.models import SchoolClass, AcademicYear

class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = "__all__"

class AdmissionApplicationSerializer(serializers.ModelSerializer):
    guardian = GuardianSerializer()
    preferred_class = serializers.SlugRelatedField(slug_field="name", queryset=SchoolClass.objects.all())
    preferred_academic_year = serializers.SlugRelatedField(slug_field="name", queryset=AcademicYear.objects.all())

    class Meta:
        model = AdmissionApplication
        fields = "__all__"

    def create(self, validated_data):
        guardian_data = validated_data.pop("guardian")
        guardian, _ = Guardian.objects.get_or_create(**guardian_data)
        return AdmissionApplication.objects.create(guardian=guardian, **validated_data)

    def update(self, instance, validated_data):
        guardian_data = validated_data.pop("guardian", None)
        if guardian_data:
            for attr, value in guardian_data.items():
                setattr(instance.guardian, attr, value)
            instance.guardian.save()
        return super().update(instance, validated_data)
