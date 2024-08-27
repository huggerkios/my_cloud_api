from django.contrib.auth import get_user_model

from rest_framework import serializers

from djoser.serializers import UserCreateSerializer

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    admin = serializers.BooleanField(source="is_staff")

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "full_name",
            "admin",
        )
        read_only_fields = fields


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=4, max_length=20)

    class Meta:
        model = User
        fields = (
            "username",
            "password",
        )
        read_only_fields = ()


class UserRegistrationSerializer(UserCreateSerializer):
    username = serializers.CharField(
        min_length=4,
        max_length=20,
    )
    username = serializers.CharField(
        min_length=4,
        max_length=300,
        required=False,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "full_name",
            "email",
            "password",
        )
