
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("adminstration", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TimeSlot",
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
                ("name", models.CharField(max_length=50)),
                (
                    "day_of_week",
                    models.CharField(
                        choices=[
                            ("monday", "Monday"),
                            ("tuesday", "Tuesday"),
                            ("wednesday", "Wednesday"),
                            ("thursday", "Thursday"),
                            ("friday", "Friday"),
                            ("saturday", "Saturday"),
                            ("sunday", "Sunday"),
                        ],
                        max_length=20,
                    ),
                ),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("is_break", models.BooleanField(default=False)),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["day_of_week", "order", "start_time"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("day_of_week", "start_time"),
                        name="unique_timeslot_per_day",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="Timetable",
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
                ("name", models.CharField(max_length=200)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "academic_year",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="timetables",
                        to="adminstration.academicyear",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        limit_choices_to={"role__in": ["admin", "teacher"]},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_timetables",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "school_class",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="timetables",
                        to="adminstration.schoolclass",
                    ),
                ),
                (
                    "section",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="timetables",
                        to="adminstration.section",
                    ),
                ),
                (
                    "term",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="timetables",
                        to="adminstration.term",
                    ),
                ),
            ],
            options={
                "ordering": ["-academic_year__start_date", "school_class__name"],
            },
        ),
        migrations.CreateModel(
            name="TimetableEntry",
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
                ("room", models.CharField(blank=True, max_length=50, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "subject",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="timetable_entries",
                        to="adminstration.subject",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"role": "teacher"},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="teaching_entries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "time_slot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="timetable_entries",
                        to="timetable.timeslot",
                    ),
                ),
                (
                    "timetable",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="entries",
                        to="timetable.timetable",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Timetable entries",
                "ordering": ["time_slot__day_of_week", "time_slot__order"],
            },
        ),
        migrations.AddConstraint(
            model_name="timetable",
            constraint=models.UniqueConstraint(
                fields=("school_class", "section", "academic_year", "term"),
                name="unique_timetable_per_section_term",
            ),
        ),
        migrations.AddConstraint(
            model_name="timetableentry",
            constraint=models.UniqueConstraint(
                fields=("timetable", "time_slot"), name="unique_entry_per_timeslot"
            ),
        ),
    ]
