from django.db.models import Sum
from django.contrib.auth import get_user_model

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from djoser.serializers import UserCreateSerializer

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """Serializer to list users."""

    is_admin = serializers.BooleanField(source="is_staff")
    files_count = serializers.SerializerMethodField()
    files_size = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "uuid",
            "username",
            "email",
            "full_name",
            "is_admin",
            "files_count",
            "files_size",
        )
        read_only_fields = fields

    @extend_schema_field(serializers.IntegerField)
    def get_files_count(self, user) -> int:
        return user.files.count()

    @extend_schema_field(serializers.IntegerField)
    def get_files_size(self, user) -> int:
        try:
            return user.files.aggregate(total_size=Sum("size")).get("total_size")
        except Exception:
            return 0


class UserLoginSerializer(serializers.ModelSerializer):
    """Serializer to login users."""

    username = serializers.CharField(min_length=4, max_length=20)

    class Meta:
        model = User
        fields = (
            "username",
            "password",
        )
        read_only_fields = ()


class UserRegistrationSerializer(UserCreateSerializer):
    """Serializer to create users."""

    username = serializers.CharField(
        min_length=4,
        max_length=20,
    )
    full_name = serializers.CharField(
        min_length=4,
        max_length=300,
        required=False,
    )

    default_error_messages = {
        "cannot_create_user": "Пользователь с текущими данными уже существует."
    }

    class Meta:
        model = User
        fields = (
            "username",
            "full_name",
            "email",
            "password",
        )
