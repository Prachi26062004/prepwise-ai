import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-insecure-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.auth", "django.contrib.contenttypes", "django.contrib.staticfiles",
    "rest_framework", "corsheaders", "drf_spectacular",
    "accounts", "resumes", "job_matcher", "interviews", "ai_engine", "roadmaps", "analytics", "stories","tracker","defense"
]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware", "django.middleware.security.SecurityMiddleware",
              "django.middleware.common.CommonMiddleware"]
ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATIC_URL = "static/"
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "config.errors.handler",
}
SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(hours=8), "REFRESH_TOKEN_LIFETIME": timedelta(days=7)}
SPECTACULAR_SETTINGS = {"TITLE": "PrepWise API", "VERSION": "0.1.0"}

AI_PROVIDER = os.environ.get("AI_PROVIDER", "none")  # none | openai | gemini
AI_MODEL = os.environ.get("AI_MODEL") or ("gemini-3.8-flash" if AI_PROVIDER == "gemini" else "gpt-4o-mini")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
AI_PRICE_IN = os.environ.get("AI_PRICE_IN", "0.15")    # USD per 1M input tokens
AI_PRICE_OUT = os.environ.get("AI_PRICE_OUT", "0.60")  # USD per 1M output tokens
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")