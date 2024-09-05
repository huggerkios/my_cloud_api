import logging

from django.contrib.auth import get_user_model, login, authenticate, logout
from django.http import HttpRequest, HttpResponse

from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import CharField, BooleanField
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer

from .serializers import (
    UserListSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
)

logger = logging.getLogger(__name__)

User = get_user_model()


@extend_schema(tags=["auth"])
@extend_schema_view(
    registration=extend_schema(
        summary="Регистрация",
        responses={
            status.HTTP_201_CREATED: UserRegistrationSerializer,
        },
    ),
    login=extend_schema(
        summary="Вход в аккаунт",
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="login_detail_message",
                fields={
                    "detail": CharField(),
                },
            ),
        },
    ),
    logout=extend_schema(
        summary="Выход из аккаунта",
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="logout_detail_message",
                fields={
                    "detail": CharField(),
                },
            ),
        },
    ),
)
class AuthViewSet(viewsets.GenericViewSet):
    """Authentication actions."""

    @action(
        methods=("post",),
        detail=False,
        serializer_class=UserRegistrationSerializer,
        permission_classes=(permissions.AllowAny,),
    )
    def registration(self, request, *args, **kwargs):
        logger.info(f"Запрос регистрации: {request.data}")

        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        methods=("post",),
        detail=False,
        serializer_class=UserLoginSerializer,
        permission_classes=(permissions.AllowAny,),
    )
    def login(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        logger.info(f"Запрос авторизации: {request.data}")

        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        logger.info("Данные валидны.")

        username = serializer.validated_data.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.info(
                f"Авторизация не выполнена. Пользователь с логином {username} не найден."
            )
            return Response(
                {
                    "detail": "Проверьте корректность логина.",
                    "code": "invalid_username",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        password = serializer.validated_data.get("password")
        user = authenticate(username=username, password=password)

        if user is None:
            logger.info("Авторизация не выполнена. Пароль не совпадает.")
            return Response(
                {
                    "detail": "Проверьте корректность пароля.",
                    "code": "invalid_password",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        login(request, user)

        logger.info(f"Авторизация выполнена. Пользователь: {user}.")
        return Response(
            {
                "detail": "Вход выполнен.",
            },
            status=status.HTTP_200_OK,
        )

    @action(
        methods=("post",),
        detail=False,
        serializer_class=None,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def logout(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        logger.info(f"Запрос выхода из аккаунта: {request.user}")

        logout(request)
        logger.info("Выход выполнен.")

        return Response(
            {
                "detail": "Выход выполнен.",
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["users"])
@extend_schema_view(
    list=extend_schema(
        summary="Список пользователей",
    ),
    destroy=extend_schema(
        summary="Удаление пользователя",
    ),
    admin_status_set=extend_schema(
        summary="Изменение статуса пользователя",
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="admin_status_set_detail_message",
                fields={
                    "is_admin": BooleanField(),
                },
            ),
        },
    ),
)
class UserViewSet(
    mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    """Admin panel actions."""

    http_method_names = ("get", "post", "delete")
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = (permissions.IsAdminUser,)

    def perform_destroy(self, user):
        logger.info(
            f"Удаление пользователя {user.username} администратором "
            f"{self.request.user.username}"
        )
        return super().perform_destroy(user)

    @action(
        methods=("post",),
        detail=True,
        url_path="admin-set",
        serializer_class=None,
        permission_classes=(permissions.IsAdminUser,),
    )
    def admin_status_set(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_staff = not user.is_staff
        user.save()

        logger.info(
            f"Изменение статуса администратора пользователя {user.username} администратором "
            f"{self.request.user.username}: {user.is_staff}"
        )

        return Response(
            {
                "is_admin": user.is_staff,
            },
            status=status.HTTP_201_CREATED,
        )
