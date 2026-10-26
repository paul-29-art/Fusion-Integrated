from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True
CELERY_TASK_ALWAYS_EAGER = True

# Dev-only fixtures that legitimately touch every module; never in production.
INSTALLED_APPS = [*INSTALLED_APPS, "devtools"]

# Local development fallback to SQLite if PostgreSQL is not active
if env("USE_SQLITE", "true").lower() in ("true", "1", "yes"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
