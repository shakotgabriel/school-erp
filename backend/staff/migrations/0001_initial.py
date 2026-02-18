
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
            name="Department",
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
                ("description", models.TextField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "head",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"role__in": ["teacher", "admin"]},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="headed_departments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Leave",
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
                (
                    "leave_type",
                    models.CharField(
                        choices=[
                            ("sick", "Sick Leave"),
                            ("casual", "Casual Leave"),
                            ("annual", "Annual Leave"),
                            ("maternity", "Maternity Leave"),
                            ("paternity", "Paternity Leave"),
                            ("unpaid", "Unpaid Leave"),
                            ("study", "Study Leave"),
                            ("other", "Other"),
                        ],
                        max_length=20,
                    ),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("total_days", models.PositiveIntegerField()),
                ("reason", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("approval_date", models.DateTimeField(blank=True, null=True)),
                ("rejection_reason", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"role__in": ["admin", "hr"]},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approved_leaves",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        limit_choices_to={"role__in": ["teacher", "accountant", "hr"]},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="leave_applications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="StaffProfile",
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
                ("employee_id", models.CharField(max_length=20, unique=True)),
                ("date_of_birth", models.DateField()),
                ("gender", models.CharField(max_length=10)),
                ("nationality", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "marital_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("single", "Single"),
                            ("married", "Married"),
                            ("divorced", "Divorced"),
                            ("widowed", "Widowed"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                ("address", models.TextField()),
                ("city", models.CharField(max_length=100)),
                ("state", models.CharField(blank=True, max_length=100, null=True)),
                ("postal_code", models.CharField(blank=True, max_length=20, null=True)),
                ("emergency_contact_name", models.CharField(max_length=100)),
                ("emergency_contact_phone", models.CharField(max_length=20)),
                ("emergency_contact_relationship", models.CharField(max_length=50)),
                ("position", models.CharField(max_length=100)),
                (
                    "employment_type",
                    models.CharField(
                        choices=[
                            ("full_time", "Full Time"),
                            ("part_time", "Part Time"),
                            ("contract", "Contract"),
                            ("temporary", "Temporary"),
                        ],
                        default="full_time",
                        max_length=20,
                    ),
                ),
                ("date_of_joining", models.DateField()),
                ("date_of_leaving", models.DateField(blank=True, null=True)),
                (
                    "highest_qualification",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "specialization",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("years_of_experience", models.PositiveIntegerField(default=0)),
                ("basic_salary", models.DecimalField(decimal_places=2, max_digits=10)),
                ("bio", models.TextField(blank=True, null=True)),
                ("photo", models.URLField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "department",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="staff_members",
                        to="staff.department",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        limit_choices_to={
                            "role__in": ["teacher", "accountant", "hr", "admin"]
                        },
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="staff_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-date_of_joining"],
            },
        ),
        migrations.CreateModel(
            name="Attendance",
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
                ("date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("present", "Present"),
                            ("absent", "Absent"),
                            ("late", "Late"),
                            ("half_day", "Half Day"),
                            ("on_leave", "On Leave"),
                        ],
                        max_length=20,
                    ),
                ),
                ("check_in_time", models.TimeField(blank=True, null=True)),
                ("check_out_time", models.TimeField(blank=True, null=True)),
                ("remarks", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "recorded_by",
                    models.ForeignKey(
                        limit_choices_to={"role__in": ["admin", "hr"]},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="recorded_attendances",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        limit_choices_to={"role__in": ["teacher", "accountant", "hr"]},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attendance_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-date"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("staff", "date"),
                        name="unique_attendance_per_staff_per_day",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="Payroll",
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
                ("month", models.PositiveIntegerField()),
                ("year", models.PositiveIntegerField()),
                ("basic_salary", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "allowances",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "deductions",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                ("net_salary", models.DecimalField(decimal_places=2, max_digits=10)),
                ("payment_date", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("processed", "Processed"),
                            ("paid", "Paid"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("remarks", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "processed_by",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"role__in": ["admin", "hr"]},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="processed_payrolls",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        limit_choices_to={"role__in": ["teacher", "accountant", "hr"]},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payroll_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-year", "-month"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("staff", "month", "year"),
                        name="unique_payroll_per_staff_per_month",
                    )
                ],
            },
        ),
    ]
