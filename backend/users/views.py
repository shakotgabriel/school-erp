from datetime import timedelta
from typing import Any, Dict, cast

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from .models import PasswordResetToken
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    SuperuserRegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from rest_framework.permissions import IsAdminUser

class SuperuserRegisterView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = SuperuserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "Superuser created successfully.", "user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)
from .permissions import IsAdmin

User = get_user_model()


def _jwt_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class RegisterView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {"message": "User created successfully.", "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = cast(Dict[str, Any], serializer.validated_data)

        user = data.get("user")
        if user is None:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

        tokens = _jwt_for_user(user)
        return Response({"tokens": tokens, "user": UserSerializer(user).data}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(Dict[str, Any], serializer.validated_data)

        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if not old_password or not new_password:
            return Response({"detail": "Invalid payload."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(old_password):
            return Response(
                {"old_password": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(Dict[str, Any], serializer.validated_data)

        email = data.get("email")
        if not email:
            return Response({"email": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()

        
        if not user:
            return Response(
                {"message": "If that email exists, reset instructions were sent."},
                status=status.HTTP_200_OK,
            )

        ttl_minutes = int(getattr(settings, "PASSWORD_RESET_TTL_MINUTES", 30))
        expires_at = timezone.now() + timedelta(minutes=ttl_minutes)

        reset_obj = PasswordResetToken.objects.create(user=user, expires_at=expires_at, used=False)

        payload = {"message": "Reset token generated."}
        if getattr(settings, "DEBUG", False):
            payload["debug_token"] = str(reset_obj.token)

        return Response(payload, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(Dict[str, Any], serializer.validated_data)

        token = data.get("token")
        new_password = data.get("new_password")

        if not token or not new_password:
            return Response({"detail": "Invalid payload."}, status=status.HTTP_400_BAD_REQUEST)

        reset_obj = PasswordResetToken.objects.filter(token=token).select_related("user").first()
        if not reset_obj:
            return Response({"token": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        if reset_obj.used:
            return Response({"token": "Token already used."}, status=status.HTTP_400_BAD_REQUEST)

        if reset_obj.expires_at and reset_obj.expires_at < timezone.now():
            return Response({"token": "Token expired."}, status=status.HTTP_400_BAD_REQUEST)

        user = reset_obj.user
        user.set_password(new_password)
        user.save(update_fields=["password"])

        reset_obj.used = True
        reset_obj.save(update_fields=["used"])

        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
