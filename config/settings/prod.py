from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import SECRET_KEY, env

DEBUG = False

if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set in production.")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SECURE_REDIRECT_EXEMPT = [r"^healthz/$"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("DJANGO_HSTS_SECONDS", default=60 * 60 * 24 * 30)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
# HSTS preload is hard to undo; enable it only once the final domain is settled.
SILENCED_SYSTEM_CHECKS = ["security.W021"]
