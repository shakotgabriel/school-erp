from django.urls import path

from .views import (
	RegisterView,
	LoginView,
	MeView,
	ChangePasswordView,
	PasswordResetRequestView,
	PasswordResetConfirmView,
	SuperuserRegisterView,
)

app_name = "users"

urlpatterns = [
	path("register/", RegisterView.as_view(), name="register"),
	path("login/", LoginView.as_view(), name="login"),
	path("me/", MeView.as_view(), name="me"),
	path("change-password/", ChangePasswordView.as_view(), name="change-password"),
	path("password-reset/request/", PasswordResetRequestView.as_view(), name="password-reset-request"),
	path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
	path("superuser/register/", SuperuserRegisterView.as_view(), name="superuser-register"),
]

