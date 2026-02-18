from django.db import models

from django.db import models
from students.models import StudentProfile
from adminstration.models import Subject, AcademicYear, Term, SchoolClass, Section
class Exam(models.Model):
	name = models.CharField(max_length=100)
	academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='exams')
	term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='exams')
	school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='exams')
	section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='exams')
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
	date = models.DateField()
	total_marks = models.PositiveIntegerField(default=100)
	def __str__(self):
		return f"{self.name} - {self.subject} - {self.school_class} ({self.term})"

class ExamResult(models.Model):
	exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
	student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='exam_results')
	marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
	grade = models.CharField(max_length=2)
	remarks = models.TextField(blank=True, null=True)
	class Meta:
		unique_together = ('exam', 'student')

	def __str__(self):
		return f"{self.student} - {self.exam}: {self.marks_obtained} ({self.grade})"
from django.db import models

