CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3030",
    "http://localhost:5173",
    "http://localhost",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3030",
    "http://127.0.0.1:5173",
    "http://127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
