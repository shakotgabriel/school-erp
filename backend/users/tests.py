from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from .models import User, PasswordResetToken, UserProfile


class UserModelTests(TestCase):
	def test_create_user_requires_email_for_non_student(self):
		with self.assertRaisesMessage(ValueError, 'The Email must be set'):
			User.objects.create_user(email=None, first_name='T', last_name='L', role='teacher', password='pw')

	def test_create_student_can_be_created_without_email(self):
		u = User.objects.create_user(email=None, first_name='Stu', last_name='Dent', role='student', password='pw', admission_number='S001')
		self.assertEqual(u.role, 'student')
		self.assertIsNone(u.email)
		self.assertEqual(u.admission_number, 'S001')

	def test_create_superuser_enforces_admin_role_and_email(self):
		with self.assertRaisesMessage(ValueError, "Superuser must have role='admin'"):
			User.objects.create_superuser(email='a@x.com', first_name='A', last_name='B', role='teacher', password='pw')

		with self.assertRaisesMessage(ValueError, 'Superusers must have an email address'):
			User.objects.create_superuser(email=None, first_name='A', last_name='B', role='admin', password='pw')

		admin = User.objects.create_superuser(email='admin@example.com', first_name='Admin', last_name='User', role='admin', password='pw')
		self.assertTrue(admin.is_superuser)
		self.assertEqual(admin.role, 'admin')

	def test_get_full_name_and_str_student(self):
		s = User.objects.create_user(email=None, first_name='First', last_name='Last', role='student', password='pw', admission_number='AD123')
		self.assertEqual(s.get_full_name(), 'First Last')
		self.assertEqual(str(s), 'AD123')

	def test_user_clean_requires_admission_for_students(self):
		u = User(first_name='X', last_name='Y', role='student')
		with self.assertRaises(Exception):
			u.full_clean()

	def test_manager_helpers(self):
		User.objects.create_user(email='t1@example.com', first_name='T1', last_name='L', role='teacher', password='pw')
		User.objects.create_user(email=None, first_name='S', last_name='L', role='student', password='pw', admission_number='S2')
		self.assertEqual(User.objects.teachers().count(), 1)
		self.assertEqual(User.objects.students().count(), 1)


class TokenAndVerificationTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(email='u@example.com', first_name='U', last_name='X', role='teacher', password='pw')

	def test_password_reset_token_is_expired(self):
		past = timezone.now() - timedelta(hours=1)
		future = timezone.now() + timedelta(hours=1)
		t1 = PasswordResetToken.objects.create(user=self.user, expires_at=past)
		t2 = PasswordResetToken.objects.create(user=self.user, expires_at=future)
		self.assertTrue(t1.is_expired)
		self.assertFalse(t2.is_expired)




class SerializerTests(TestCase):
	def test_register_serializer_student_without_email(self):
		from .serializers import RegisterSerializer

		data = {
			'email': None,
			'first_name': 'Stu',
			'last_name': 'D',
			'role': 'student',
			'admission_number': 'AD100',
			'password': 'StrongP@ssw0rd1',
		}
		ser = RegisterSerializer(data=data)
		self.assertTrue(ser.is_valid(), ser.errors)
		user = ser.save()
		self.assertEqual(user.role, 'student')
		self.assertEqual(user.admission_number, 'AD100')

	def test_register_serializer_requires_email_for_staff(self):
		from .serializers import RegisterSerializer

		data = {
			'email': None,
			'first_name': 'T',
			'last_name': 'L',
			'role': 'teacher',
			'password': 'StrongP@ssw0rd1',
		}
		ser = RegisterSerializer(data=data)
		self.assertFalse(ser.is_valid())
		self.assertIn('email', ser.errors)

	def test_login_serializer_email_and_admission(self):
		from .serializers import LoginSerializer

		teacher = User.objects.create_user(email='t@example.com', first_name='T', last_name='L', role='teacher', password='TeacherP@ss1')
		student = User.objects.create_user(email=None, first_name='S', last_name='L', role='student', password='StudentP@ss1', admission_number='AD200')

		ser = LoginSerializer(data={'identifier': 't@example.com', 'password': 'TeacherP@ss1'}, context={'request': None})
		self.assertTrue(ser.is_valid(), ser.errors)
		self.assertEqual(ser.validated_data['user'].pk, teacher.pk)

		ser2 = LoginSerializer(data={'identifier': 'AD200', 'password': 'StudentP@ss1'}, context={'request': None})
		self.assertTrue(ser2.is_valid(), ser2.errors)
		self.assertEqual(ser2.validated_data['user'].pk, student.pk)

	def test_change_password_serializer_checks_old_password(self):
		from types import SimpleNamespace
		from .serializers import ChangePasswordSerializer

		user = User.objects.create_user(email='x@y.com', first_name='X', last_name='Y', role='teacher', password='OrigP@ss1')
		req = SimpleNamespace(user=user)

		ser = ChangePasswordSerializer(data={
			'old_password': 'wrong',
			'new_password': 'NewStrongP@ss1',
			'new_password_confirm': 'NewStrongP@ss1',
		}, context={'request': req})
		self.assertFalse(ser.is_valid())

		ser2 = ChangePasswordSerializer(data={
			'old_password': 'OrigP@ss1',
			'new_password': 'NewStrongP@ss1',
			'new_password_confirm': 'NewStrongP@ss1',
		}, context={'request': req})
		self.assertTrue(ser2.is_valid(), ser2.errors)
