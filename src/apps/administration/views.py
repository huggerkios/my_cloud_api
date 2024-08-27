from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate, logout
from django.http import HttpRequest, HttpResponse

from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    UserListSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
)

User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    @action(
        methods=("post",),
        detail=False,
        serializer_class=UserRegistrationSerializer,
        permission_classes=(permissions.AllowAny,),
    )
    def registration(self, request, *args, **kwargs):
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
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        # logged passed data

        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            # loggen user login succeed
            return Response(
                {
                    "detail": "Вход выполнен.",
                },
                status=status.HTTP_200_OK,
            )
        # loggen user login failed
        return Response(
            {
                "detail": "Пользователь не найден.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    @action(
        methods=("post",),
        detail=False,
        serializer_class=None,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def logout(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        logout(request)

        return Response(
            {
                "detail": "Выход выполнен.",
            },
            status=status.HTTP_200_OK,
        )


class UserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    http_method_names = ("get", "post", "delete")
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = (permissions.IsAdminUser,)

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

        return Response(
            {
                "admin": user.is_staff,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        methods=("delete",),
        detail=True,
        url_path="delete",
        serializer_class=None,
        permission_classes=(permissions.IsAdminUser,),
    )
    def destroy_user(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()

        return Response(
            {
                "detail": "Пользователь удалён.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )
