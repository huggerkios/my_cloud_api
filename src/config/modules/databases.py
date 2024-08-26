import os

from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": os.getenv("DB_NAME", default="postgres"),
        "USER": os.getenv("DB_USER", default=""),
        "PASSWORD": os.getenv("DB_PASSWORD", default="postgres"),
        "HOST": os.getenv("DB_HOST", default=""),
        "PORT": os.getenv("DB_PORT", default="5432"),
    }
}
