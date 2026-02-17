from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class AcademicYear(models.Model):
	name = models.CharField(max_length=20, unique=True)
	start_date = models.DateField()
	end_date = models.DateField()
	is_active = models.BooleanField(default=False)

	class Meta:
		ordering = ["-start_date"]

	def clean(self):
		if self.start_date and self.end_date and self.start_date >= self.end_date:
			raise ValidationError({"end_date": "End date must be later than start date."})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)
		if self.is_active:
			AcademicYear.objects.exclude(pk=self.pk).update(is_active=False)

	def __str__(self):
		return self.name


class Term(models.Model):
	academic_year = models.ForeignKey(
		AcademicYear,
		on_delete=models.CASCADE,
		related_name="terms",
	)
	name = models.CharField(max_length=30)
	start_date = models.DateField()
	end_date = models.DateField()
	is_active = models.BooleanField(default=False)

	class Meta:
		ordering = ["start_date"]
		constraints = [
			models.UniqueConstraint(
				fields=["academic_year", "name"],
				name="unique_term_name_per_academic_year",
			)
		]

	def clean(self):
		if self.start_date and self.end_date and self.start_date >= self.end_date:
			raise ValidationError({"end_date": "End date must be later than start date."})
		if self.academic_year_id:
			if self.start_date < self.academic_year.start_date or self.end_date > self.academic_year.end_date:
				raise ValidationError({
					"start_date": "Term dates must be within the selected academic year.",
					"end_date": "Term dates must be within the selected academic year.",
				})

	def __str__(self):
		return f"{self.academic_year.name} - {self.name}"


class SchoolClass(models.Model):
	name = models.CharField(max_length=60, unique=True)
	code = models.CharField(max_length=20, unique=True)
	level = models.PositiveIntegerField(blank=True, null=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ["level", "name"]
		verbose_name_plural = "School classes"

	def __str__(self):
		return self.name


class Stream(models.Model):
	school_class = models.ForeignKey(
		SchoolClass,
		on_delete=models.CASCADE,
		related_name="streams",
	)
	name = models.CharField(max_length=30)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ["school_class__name", "name"]
		constraints = [
			models.UniqueConstraint(
				fields=["school_class", "name"],
				name="unique_stream_per_class",
			)
		]

	def __str__(self):
		return f"{self.school_class.name} - {self.name}"


class Section(models.Model):
	school_class = models.ForeignKey(
		SchoolClass,
		on_delete=models.CASCADE,
		related_name="sections",
	)
	stream = models.ForeignKey(
		Stream,
		on_delete=models.SET_NULL,
		related_name="sections",
		blank=True,
		null=True,
	)
	name = models.CharField(max_length=30)
	class_teacher = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		related_name="class_sections",
		blank=True,
		null=True,
		limit_choices_to={"role": "teacher"},
	)
	capacity = models.PositiveIntegerField(default=40)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ["school_class__name", "name"]
		constraints = [
			models.UniqueConstraint(
				fields=["school_class", "stream", "name"],
				name="unique_section_per_stream_and_class",
			)
		]

	def clean(self):
		if self.stream_id and self.stream.school_class_id != self.school_class_id:
			raise ValidationError({"stream": "Selected stream does not belong to this class."})

	def __str__(self):
		if self.stream:
			return f"{self.school_class.name} / {self.stream.name} / {self.name}"
		return f"{self.school_class.name} / {self.name}"


class Subject(models.Model):
	name = models.CharField(max_length=100, unique=True)
	code = models.CharField(max_length=20, unique=True)
	school_classes = models.ManyToManyField(
		SchoolClass,
		related_name="subjects",
		blank=True,
	)
	is_optional = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return f"{self.name} ({self.code})"
