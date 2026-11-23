import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_healthcheck_is_public(client):
    response = client.get("/healthz/")
    assert response.status_code == 200
    assert response.content == b"ok"


def test_landing_is_public(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Crear cuenta gratis" in response.content.decode()


def test_landing_redirects_logged_in_users(owner_client):
    response = owner_client.get("/")
    assert response.status_code == 302
    assert response.url == "/inicio/"


def test_private_pages_require_login(client):
    response = client.get("/inicio/")
    assert response.status_code == 302
    assert response.url.startswith("/cuenta/login/")


def test_home_lists_business_categories(owner_client, in_business):
    from apps.catalog.tests.factories import CategoryFactory

    CategoryFactory(name="Velas")
    response = owner_client.get("/inicio/")
    assert "Velas" in response.content.decode()


def test_forms_are_csrf_protected():
    client = Client(enforce_csrf_checks=True)
    response = client.post("/cuenta/login/", {"login": "a@example.com", "password": "x"})
    assert response.status_code == 403
