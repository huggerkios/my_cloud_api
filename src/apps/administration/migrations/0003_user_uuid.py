# Generated by Django 5.1 on 2024-08-27 16:45

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("administration", "0002_user_full_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
