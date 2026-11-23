import pytest

from apps.businesses.middleware import SESSION_KEY
from apps.businesses.models import Business, Role
from apps.businesses.tests.factories import BusinessFactory, MembershipFactory

pytestmark = pytest.mark.django_db


def test_owner_can_edit_business_settings(owner_client, business):
    assert owner_client.get("/negocio/").status_code == 200
    response = owner_client.post(
        "/negocio/",
        {
            "name": "Nuevo nombre",
            "industry": "food",
            "tax_condition": "responsable_inscripto",
            "currency": "ARS",
        },
    )
    assert response.status_code == 302
    business.refresh_from_db()
    assert business.name == "Nuevo nombre"
    assert business.tax_condition == "responsable_inscripto"


@pytest.mark.parametrize("role", [Role.SELLER, Role.VIEWER])
def test_non_owners_cannot_edit_business_settings(client, role):
    membership = MembershipFactory(role=role)
    client.force_login(membership.user)
    assert client.get("/negocio/").status_code == 403
    response = client.post("/negocio/", {"name": "x"})
    assert response.status_code == 403
    assert Business.objects.get().name != "x"


def test_settings_link_is_only_shown_to_owners(client):
    membership = MembershipFactory(role=Role.SELLER)
    client.force_login(membership.user)
    page = client.get("/inicio/").content.decode()
    assert "Mi negocio" not in page


def test_current_business_comes_from_session(client):
    membership = MembershipFactory()
    second = MembershipFactory(user=membership.user, business=BusinessFactory(name="Segundo"))
    client.force_login(membership.user)
    session = client.session
    session[SESSION_KEY] = second.business_id
    session.save()
    assert "Segundo" in client.get("/inicio/").content.decode()


def test_session_cannot_point_to_a_foreign_business(client):
    membership = MembershipFactory(business__name="Propio")
    foreign = BusinessFactory(name="Ajeno")
    client.force_login(membership.user)
    session = client.session
    session[SESSION_KEY] = foreign.pk
    session.save()
    page = client.get("/inicio/").content.decode()
    assert "Propio" in page and "Ajeno" not in page


def test_inactive_membership_gives_no_access(client):
    membership = MembershipFactory(is_active=False)
    client.force_login(membership.user)
    assert client.get("/inicio/").url == "/empezar/"


def test_str_representations():
    membership = MembershipFactory(business__name="Lunares", role=Role.OWNER)
    assert str(membership.business) == "Lunares"
    assert "Lunares" in str(membership) and "Dueño/a" in str(membership)
