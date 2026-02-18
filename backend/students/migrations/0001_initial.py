
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("adminstration", "0001_initial"),
        ("admission", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=50)),
                ("middle_name", models.CharField(blank=True, max_length=50, null=True)),
                ("last_name", models.CharField(max_length=50)),
                ("dob", models.DateField()),
                ("gender", models.CharField(max_length=10)),
                ("religion", models.CharField(blank=True, max_length=30, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "admission_application",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="student_profile",
                        to="admission.admissionapplication",
                    ),
                ),
                (
                    "guardian",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="students",
                        to="admission.guardian",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("enrolled_on", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "academic_year",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="enrollments",
                        to="adminstration.academicyear",
                    ),
                ),
                (
                    "school_class",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="enrollments",
                        to="adminstration.schoolclass",
                    ),
                ),
                (
                    "section",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="enrollments",
                        to="adminstration.section",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to="students.studentprofile",
                    ),
                ),
            ],
            options={
                "unique_together": {("student", "academic_year")},
            },
        ),
    ]
