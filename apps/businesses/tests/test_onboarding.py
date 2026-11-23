import pytest

from apps.businesses.middleware import SESSION_KEY
from apps.businesses.models import Business, Membership, Role
from apps.businesses.services import create_business
from apps.catalog.models import Category
from apps.core.tenancy import use_business

pytestmark = pytest.mark.django_db


@pytest.fixture
def new_user_client(client, user):
    client.force_login(user)
    return client


def test_user_without_business_is_sent_to_onboarding(new_user_client):
    assert new_user_client.get("/inicio/").url == "/empezar/"
    assert new_user_client.get("/negocio/").url == "/empezar/"


def test_full_onboarding_creates_business_with_categories(new_user_client, user):
    c = new_user_client
    assert c.get("/empezar/").status_code == 200

    r = c.post("/empezar/?paso=1", {"name": "  Lunares   Deco ", "industry": "home"})
    assert r.url == "/empezar/?paso=2"
    r = c.post("/empezar/?paso=2", {"tax_condition": "monotributo", "currency": "ARS"})
    assert r.url == "/empezar/?paso=3"
    page = c.get("/empezar/?paso=3").content.decode()
    assert "Velas y aromas" in page  # preset for the "home" industry

    r = c.post(
        "/empezar/?paso=3",
        {"categories": ["Velas y aromas", "Textiles"], "extra_categories": "Macetas\ntextiles\n"},
    )
    assert r.url == "/inicio/"

    business = Business.objects.get()
    assert business.name == "Lunares Deco"
    assert business.tax_condition == "monotributo"
    membership = Membership.objects.get(business=business)
    assert membership.user == user and membership.role == Role.OWNER
    assert c.session[SESSION_KEY] == business.pk
    with use_business(business):
        assert sorted(Category.objects.values_list("name", flat=True)) == [
            "Macetas",
            "Textiles",
            "Velas y aromas",
        ]
    assert c.get("/inicio/").status_code == 200


def test_onboarding_cannot_skip_steps(new_user_client):
    response = new_user_client.get("/empezar/?paso=3")
    assert "Paso 1 de 3" in response.content.decode()


def test_onboarding_ignores_garbage_step(new_user_client):
    response = new_user_client.get("/empezar/?paso=abc")
    assert "Paso 1 de 3" in response.content.decode()


def test_onboarding_validates_input(new_user_client):
    response = new_user_client.post("/empezar/?paso=1", {"name": "   ", "industry": "nope"})
    assert response.status_code == 200
    assert not Business.objects.exists()


def test_other_industry_has_no_presets(new_user_client):
    c = new_user_client
    c.post("/empezar/?paso=1", {"name": "Varios", "industry": "other"})
    c.post("/empezar/?paso=2", {"tax_condition": "not_registered", "currency": "USD"})
    page = c.get("/empezar/?paso=3").content.decode()
    assert "¿Con qué categorías querés empezar?" in page
    c.post("/empezar/?paso=3", {"extra_categories": ""})
    business = Business.objects.get()
    assert business.currency == "USD"
    with use_business(business):
        assert not Category.objects.exists()


def test_user_with_business_skips_onboarding(owner_client):
    assert owner_client.get("/empezar/").url == "/inicio/"


def test_create_business_dedupes_and_trims_categories(user):
    business = create_business(
        owner=user,
        name="Mi negocio",
        industry="clothing",
        tax_condition="responsable_inscripto",
        currency="ARS",
        category_names=["Remeras", " remeras ", "", "Buzos   y camperas"],
    )
    with use_business(business):
        assert sorted(Category.objects.values_list("name", flat=True)) == [
            "Buzos y camperas",
            "Remeras",
        ]


def test_account_pages_work_without_a_business(new_user_client):
    assert new_user_client.get("/cuenta/logout/").status_code == 200


def test_public_pages_work_without_a_business(new_user_client):
    # The landing page is public; it then forwards logged-in users to the app.
    assert new_user_client.get("/healthz/").status_code == 200
    assert new_user_client.get("/").url == "/inicio/"
