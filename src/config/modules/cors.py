CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3030",
    "http://localhost:5173",
    "http://localhost",
    # Дополнительные разрешенные источники, если есть
]

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
