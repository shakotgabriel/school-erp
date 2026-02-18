
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AcademicYear",
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
                ("name", models.CharField(max_length=20, unique=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("is_active", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["-start_date"],
            },
        ),
        migrations.CreateModel(
            name="SchoolClass",
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
                ("name", models.CharField(max_length=60, unique=True)),
                ("code", models.CharField(max_length=20, unique=True)),
                ("level", models.PositiveIntegerField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name_plural": "School classes",
                "ordering": ["level", "name"],
            },
        ),
        migrations.CreateModel(
            name="Stream",
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
                ("name", models.CharField(max_length=30)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "school_class",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="streams",
                        to="adminstration.schoolclass",
                    ),
                ),
            ],
            options={
                "ordering": ["school_class__name", "name"],
            },
        ),
        migrations.CreateModel(
            name="Section",
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
                ("name", models.CharField(max_length=30)),
                ("capacity", models.PositiveIntegerField(default=40)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "class_teacher",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"role": "teacher"},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="class_sections",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "school_class",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sections",
                        to="adminstration.schoolclass",
                    ),
                ),
                (
                    "stream",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sections",
                        to="adminstration.stream",
                    ),
                ),
            ],
            options={
                "ordering": ["school_class__name", "name"],
            },
        ),
        migrations.CreateModel(
            name="Subject",
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
                ("name", models.CharField(max_length=100, unique=True)),
                ("code", models.CharField(max_length=20, unique=True)),
                ("is_optional", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "school_classes",
                    models.ManyToManyField(
                        blank=True,
                        related_name="subjects",
                        to="adminstration.schoolclass",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Term",
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
                ("name", models.CharField(max_length=30)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("is_active", models.BooleanField(default=False)),
                (
                    "academic_year",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="terms",
                        to="adminstration.academicyear",
                    ),
                ),
            ],
            options={
                "ordering": ["start_date"],
            },
        ),
        migrations.AddConstraint(
            model_name="stream",
            constraint=models.UniqueConstraint(
                fields=("school_class", "name"), name="unique_stream_per_class"
            ),
        ),
        migrations.AddConstraint(
            model_name="section",
            constraint=models.UniqueConstraint(
                fields=("school_class", "stream", "name"),
                name="unique_section_per_stream_and_class",
            ),
        ),
        migrations.AddConstraint(
            model_name="term",
            constraint=models.UniqueConstraint(
                fields=("academic_year", "name"),
                name="unique_term_name_per_academic_year",
            ),
        ),
    ]
