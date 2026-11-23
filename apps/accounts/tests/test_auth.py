import re

import pytest
from django.core import mail

from apps.accounts.models import User

pytestmark = pytest.mark.django_db


def test_signup_creates_user_and_goes_to_onboarding(client, password):
    response = client.post(
        "/cuenta/signup/",
        {"full_name": "Ana Pérez", "email": "Ana@Example.com", "password1": password},
    )
    assert response.status_code == 302
    assert response.url == "/inicio/"
    user = User.objects.get()
    assert user.email == "ana@example.com"
    assert user.full_name == "Ana Pérez"
    assert user.check_password(password)
    assert password not in user.password
    # No business yet: any private page sends the user to onboarding.
    assert client.get("/inicio/").url == "/empezar/"


def test_signup_rejects_weak_passwords(client):
    response = client.post(
        "/cuenta/signup/",
        {"full_name": "Ana", "email": "ana@example.com", "password1": "12345678"},
    )
    assert response.status_code == 200
    assert "La contraseña no puede tener solo números." in response.content.decode()
    assert not User.objects.exists()


def test_login_with_email(client, user, password):
    response = client.post("/cuenta/login/", {"login": user.email, "password": password})
    assert response.status_code == 302
    assert "_auth_user_id" in client.session


def test_login_error_is_in_rioplatense(client, user):
    response = client.post("/cuenta/login/", {"login": user.email, "password": "incorrecta"})
    assert response.status_code == 200
    assert "El email o la contraseña no son correctos" in response.content.decode()


def test_login_is_rate_limited_after_repeated_failures(client, user, password):
    for _ in range(5):
        client.post("/cuenta/login/", {"login": user.email, "password": "incorrecta"})
    # Even the right password is refused while the account is locked out.
    response = client.post("/cuenta/login/", {"login": user.email, "password": password})
    assert "_auth_user_id" not in client.session
    assert "demasiados intentos" in response.content.decode().lower()


def test_password_reset_flow(client, user):
    response = client.post("/cuenta/password/reset/", {"email": user.email})
    assert response.status_code == 302
    assert len(mail.outbox) == 1
    message = mail.outbox[0]
    assert message.to == [user.email]
    assert "contraseña" in message.subject.lower()
    assert "Recibimos un pedido para cambiar la contraseña" in message.body

    reset_url = re.search(r"https?://[^/]+(/cuenta/password/reset/key/\S+)", message.body).group(1)
    response = client.get(reset_url, follow=True)
    form_url = response.redirect_chain[-1][0]
    response = client.post(
        form_url, {"password1": "otraClaveNueva456", "password2": "otraClaveNueva456"}
    )
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.check_password("otraClaveNueva456")


def test_password_reset_does_not_reveal_unknown_emails(client):
    response = client.post("/cuenta/password/reset/", {"email": "nadie@example.com"})
    assert response.status_code == 302
    assert response.url == "/cuenta/password/reset/done/"


def test_create_superuser():
    admin = User.objects.create_superuser("admin@example.com", "x" * 12)
    assert admin.is_staff and admin.is_superuser


def test_user_display_helpers():
    assert str(User(email="a@example.com")) == "a@example.com"
    assert User(email="a@example.com", full_name="Ana Pérez").first_name == "Ana"
    with pytest.raises(ValueError):
        User.objects.create_user("")
