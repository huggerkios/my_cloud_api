from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import LoginRegexValidator


class User(AbstractUser):
    full_name = models.CharField(
        ("Полное имя"),
        max_length=300,
        blank=True,
    )

    username_validator = LoginRegexValidator()

    REQUIRED_FIELDS = ("password",)
    LOGIN_FIELD = "username"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
