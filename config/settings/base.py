"""Base settings shared by every environment.

All secrets and environment-specific values come from environment variables
(see `.env.example`). Nothing secret lives in the code.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

PRODUCT_NAME = env("PRODUCT_NAME", default="Emprende")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.forms",
    # Third party
    "allauth",
    "allauth.account",
    "django_htmx",
    "django_tailwind_cli",
    # Local
    "apps.core",
    "apps.accounts",
    "apps.businesses",
    "apps.catalog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "apps.businesses.middleware.CurrentBusinessMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.app_context",
            ],
        },
    },
]

# All forms (ours and allauth's) render with our own Tailwind templates.
FORM_RENDERER = "apps.core.forms.AppFormRenderer"

DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://postgres:postgres@localhost:5432/erp"),
}
DATABASES["default"]["ATOMIC_REQUESTS"] = False
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DATABASE_CONN_MAX_AGE", default=60)

# Database-backed cache: shared between workers (needed for login rate limits)
# without having to run Redis.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Auth -------------------------------------------------------------------

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "home"

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*"]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_SIGNUP_FORM_CLASS = "apps.accounts.forms.SignupExtraForm"
ACCOUNT_ADAPTER = "apps.accounts.adapter.AccountAdapter"
ACCOUNT_EMAIL_SUBJECT_PREFIX = f"[{PRODUCT_NAME}] "
ACCOUNT_PREVENT_ENUMERATION = True
# Brute-force protection (per IP and per account). Uses the shared cache.
ACCOUNT_RATE_LIMITS = {
    "login": "30/m/ip",
    "login_failed": "10/m/ip,5/300s/key",
    "signup": "20/m/ip",
    "reset_password": "20/m/ip,5/m/key",
    "reset_password_from_key": "20/m/ip",
    "change_password": "5/m/user",
}

# --- Email ------------------------------------------------------------------

EMAIL_CONFIG = env.email("EMAIL_URL", default="consolemail://")
vars().update(EMAIL_CONFIG)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=f"{PRODUCT_NAME} <no-reply@localhost>")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# --- i18n -------------------------------------------------------------------

LANGUAGE_CODE = "es-ar"
LANGUAGES = [("es-ar", "Español (Argentina)")]
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / "locale"]

# --- Static -----------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

TAILWIND_CLI_SRC_CSS = "assets/tailwind.css"
TAILWIND_CLI_DIST_CSS = "css/app.css"

# --- Security (hardened further in prod.py) ---------------------------------

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days ("remember me")
CSRF_COOKIE_HTTPONLY = False  # HTMX reads the token from the page, not the cookie
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", default="INFO")},
}

# Admin lives at a non-obvious path in production (set ADMIN_URL).
ADMIN_URL = env("ADMIN_URL", default="admin/")

# Pinned so local, CI and Docker builds produce the same CSS.
TAILWIND_CLI_VERSION = "4.1.3"
