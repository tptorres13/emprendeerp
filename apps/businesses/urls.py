from django.urls import path

from . import views

urlpatterns = [
    path("empezar/", views.onboarding, name="onboarding"),
    path("negocio/", views.business_settings, name="business_settings"),
]
