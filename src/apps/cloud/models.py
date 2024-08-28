import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_delete
from django.dispatch import receiver

User = get_user_model()


def user_files_path(instance, filename):
    """Returns path to user file storage"""
    return f"upload_files/{instance.user.uuid}/{filename}"


class File(models.Model):
    """User uploaded files model."""

    uuid = models.UUIDField(
        default=uuid.uuid4,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="files",
    )
    file = models.FileField(
        upload_to=user_files_path,
    )
    name = models.CharField(
        max_length=256,
    )
    comment = models.CharField(
        max_length=256,
        blank=True,
        null=True,
    )
    type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    size = models.BigIntegerField()
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )
    last_download = models.DateTimeField(
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"

    def __str__(self) -> str:
        return self.name


@receiver(pre_delete, sender=File)
def extra_file_delete(sender, instance, **kwargs):
    """Removes files from storage after File instance destroyed."""
    if instance.file.name:
        instance.file.delete(False)
