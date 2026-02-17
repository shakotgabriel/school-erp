from django import forms

from .models import User

class CustomUserCreationForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ("email", "first_name", "last_name", "role", "admission_number", "password")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["email"].required = False

	def clean_email(self):
		email = self.cleaned_data.get("email")
		role = self.cleaned_data.get("role")
		if role != "student" and not email:
			raise forms.ValidationError("Email is required for non-student users.")
		return email

	def clean_admission_number(self):
		admission_number = self.cleaned_data.get("admission_number")
		role = self.cleaned_data.get("role")
		if role == "student" and not admission_number:
			raise forms.ValidationError("Admission number is required for students.")
		return admission_number


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
	list_display = ("email", "first_name", "last_name", "role", "is_active", "is_verified", "date_joined")
	search_fields = ("email", "first_name", "last_name", "admission_number")
	ordering = ("email",)
	fieldsets = (
		(None, {"fields": ("email", "password")}),
		("Personal info", {"fields": ("first_name", "last_name", "phone_number", "admission_number", "role")}),
		("Permissions", {"fields": ("is_active", "is_verified", "is_staff", "is_superuser", "groups", "user_permissions")}),
		("Important dates", {"fields": ("date_joined",)}),
	)
	add_fieldsets = (
		(None, {
			"classes": ("wide",),
			"fields": ("email", "first_name", "last_name", "role", "admission_number", "password"),
		}),
	)
	add_form = CustomUserCreationForm
	form = CustomUserCreationForm
