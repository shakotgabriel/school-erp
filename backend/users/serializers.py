from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

User = get_user_model()



class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone_number",
            "admission_number",
            "role",
            "is_verified",
            "is_active",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "is_verified",
            "is_active",
            "date_joined",
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()




class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    def validate_password(self, value):
        validate_password(value)
        return value

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "admission_number",
            "role",
            "password",
        ]

    def validate(self, data):
        role = data.get("role")
        email = data.get("email")
        admission_number = data.get("admission_number")

        if role == "student" and not admission_number:
            raise serializers.ValidationError(
                {"admission_number": "Admission number is required for students."}
            )
        if role != "student" and not email:
            raise serializers.ValidationError(
                {"email": "Email is required for staff users."}
            )
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class SuperuserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
        ]

    def validate(self, data):
        if not data.get("email"):
            raise serializers.ValidationError({"email": "Email is required for superuser."})
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_superuser(password=password, role="admin", **validated_data)



class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get("identifier")
        password = data.get("password")

        if not identifier or not password:
            raise serializers.ValidationError(
                _("Identifier and password are required.")
            )

  
        user = None

 
        if "@" in identifier:
            user = authenticate(
                request=self.context.get("request"),
                username=identifier,
                password=password,
            )
        else:
          
            try:
                user_obj = User.objects.get(admission_number=identifier)
                if user_obj.check_password(password):
                    user = user_obj
            except User.DoesNotExist:
                pass

        if not user:
            raise serializers.ValidationError(
                _("Invalid login credentials.")
            )

        if not user.is_active:
            raise serializers.ValidationError(
                _("User account is disabled.")
            )

        data["user"] = user
        return data



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Passwords do not match."}
            )

        validate_password(data["new_password"])

       
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and not user.check_password(data["old_password"]):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})

        return data



class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No user found with this email."
            )
        return value



class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
