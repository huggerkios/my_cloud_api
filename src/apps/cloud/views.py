import logging

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.timezone import now
from django.core.exceptions import ValidationError

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions, status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.decorators import action
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.serializers import CharField
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    inline_serializer,
    OpenApiParameter,
    OpenApiTypes,
)

from .models import File
from .serializers import FileSerializer, FileUpdateSerializer

logger = logging.getLogger(__name__)

User = get_user_model()


@extend_schema(tags=["files"])
@extend_schema_view(
    list=extend_schema(
        summary="Список файлов",
        parameters=[
            OpenApiParameter(
                "uuid",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description=(
                    "Указатель хранилища для работы администратора с файлами "
                    "пользователя (uuid пользователя, к хранилищу которого необходим доступ)."
                ),
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Просмотр файла",
    ),
    create=extend_schema(
        summary="Загрузка файла",
        request=FileSerializer,
        responses={
            status.HTTP_201_CREATED: FileSerializer,
        },
    ),
    partial_update=extend_schema(
        summary="Редактирование имени, комментария файла",
        request=FileUpdateSerializer,
        responses={
            status.HTTP_200_OK: FileSerializer,
        },
    ),
    destroy=extend_schema(
        summary="Удаление файла",
    ),
)
class FileViewSet(viewsets.ModelViewSet):
    """User files storage actions."""

    http_method_names = ("get", "post", "patch", "delete")
    queryset = File.objects.all()
    lookup_field = "uuid"
    serializer_class = FileSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    )
    ordering = ("user", "uploaded_at", "last_download", "type", "size", "name")
    search_fields = ("name", "comment")
    parser_classes = (MultiPartParser, JSONParser)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            storage_id = self.request.query_params.get("uuid", "")
            self.request.session["storage_id"] = storage_id
            try:
                return File.objects.filter(user__uuid=storage_id)
            except ValidationError:
                return File.objects.all()
        if self.action == "share":
            return File.objects.all()
        return user.files.all()

    def get_serializer_class(self):
        match self.action:
            case "update" | "partial_update":
                return FileUpdateSerializer
            case _:
                return super().get_serializer_class()

    def perform_create(self, serializer):
        logger.info(f"Загрузка файла пользователем {self.request.user.username}. ")

        storage_id = self.request.session.get(
            "storage_id", ""
        ) or self.request.query_params.get("uuid", "")
        if storage_id and self.request.user.is_staff:
            storage_user = User.objects.get(uuid=storage_id)
            serializer.validated_data["user"] = storage_user
            logger.info(f"Хранилище пользователя {storage_user.username}. ")

        super().perform_create(serializer)

        logger.info("Файл сохранен.")

    def perform_update(self, serializer, *args, **kwargs):
        logger.info(
            f"Редактирование файла. {self.request.user.username}"
            f"Новые данные: {serializer.validated_data}"
        )

        super().perform_update(serializer, *args, **kwargs)

        logger.info("Файл обновлен.")

    def perform_destroy(self, instance):
        logger.info(
            f"Удаление файла пользователем {self.request.user.username}. "
            f"Владелец файла {instance.user.username}. "
            f"Имя файла {instance.name}. "
        )

        super().perform_destroy(instance)

        logger.info("Файл удален.")

    @extend_schema(summary="Скачивание файла")
    @action(
        methods=("get",),
        detail=True,
    )
    def download(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()

        response = HttpResponse(instance.file, content_type=instance.type)
        response["Content-Disposition"] = "attachment;filename=" + instance.name
        response["Access-Control-Expose-Headers"] = "Content-Disposition"

        logger.info(
            f"Скачивание файла пользователем {self.request.user.username}. "
            f"Владелец файла {instance.user.username}. "
            f"Имя файла {instance.name}. "
            f"Тип файла {instance.type}. "
            f"Размер файла {instance.size} байт. "
        )

        instance.last_download = now()
        instance.save()

        return response

    @extend_schema(summary="Скачивание файла через специальную ссылку")
    @action(
        methods=("get",),
        detail=False,
        url_path="share/<slug:uuid>",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def share(self, request, pk=None, *args, **kwargs):
        return self.download(request, pk, *args, **kwargs)

    @extend_schema(
        summary="Получение специальной ссылки",
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="get_download_link_detail_message",
                fields={
                    "link": CharField(),
                },
            ),
        },
    )
    @action(
        methods=("get",),
        detail=True,
        url_path="download-link",
    )
    def get_download_link(self, request, *args, **kwargs):
        instance = self.get_object()

        logger.info(
            f"Получение ссылки для скачивания файла пользователем {self.request.user.username}. "
            f"Имя файла {instance.name}. "
        )

        return Response(
            {
                "link": request.build_absolute_uri(
                    reverse("share", args=[str(instance.uuid)])
                )
            },
            status=status.HTTP_200_OK,
        )
