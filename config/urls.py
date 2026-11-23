from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from apps.core import views as core_views

admin.site.site_header = f"{settings.PRODUCT_NAME} · administración"

urlpatterns = [
    path("", core_views.landing, name="landing"),
    path("inicio/", core_views.home, name="home"),
    path("healthz/", core_views.healthz, name="healthz"),
    path("cuenta/", include("allauth.urls")),
    path("", include("apps.businesses.urls")),
    path(settings.ADMIN_URL, admin.site.urls),
]
