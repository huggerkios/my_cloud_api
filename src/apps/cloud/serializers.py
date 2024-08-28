import logging

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import File
from .fields import HybridFileField

logger = logging.getLogger(__name__)


class FileSerializer(serializers.ModelSerializer):
    """Serializer to retrieve, create files."""

    size_mb = serializers.SerializerMethodField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    file = HybridFileField(required=True, trust_provided_content_type=True)

    class Meta:
        model = File
        fields = (
            "uuid",
            "user",
            "file",
            "name",
            "comment",
            "type",
            "size",
            "size_mb",
            "uploaded_at",
            "last_download",
        )
        read_only_fields = (
            "uuid",
            "type",
            "size",
            "size_mb",
            "uploaded_at",
            "last_download",
        )

    @extend_schema_field(serializers.IntegerField)
    def get_size_mb(self, obj: File) -> int:
        """File size in MB."""
        return round(obj.size / 1024 / 1024, 2)

    def create(self, validated_data):
        file = validated_data.get("file")

        validated_data["size"] = file.size
        validated_data["type"] = file.content_type
        validated_data["name"] = validated_data.get("name", file.name)

        logger.info(
            f"Имя файла: {validated_data['name']}. "
            f"Тип файла: {validated_data['type']}. "
            f"Размер файла: {validated_data['size']} байт. "
        )

        return super().create(validated_data)


class FileUpdateSerializer(FileSerializer):
    """Serializer to update files."""

    class Meta(FileSerializer.Meta):
        read_only_fields = FileSerializer.Meta.read_only_fields + ("file",)
