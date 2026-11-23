import pytest

from apps.accounts.models import User
from apps.businesses.tests.factories import BusinessFactory
from apps.catalog.tests.factories import CategoryFactory
from apps.core.tenancy import use_business

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client(client):
    client.force_login(User.objects.create_superuser("staff@example.com", "x" * 12))
    return client


def test_staff_sees_business_data_of_every_business_read_only(admin_client):
    for name in ("Uno", "Dos"):
        business = BusinessFactory()
        with use_business(business):
            CategoryFactory(name=f"Categoría {name}")
    response = admin_client.get("/admin/catalog/category/")
    assert response.status_code == 200
    page = response.content.decode()
    assert "Categoría Uno" in page and "Categoría Dos" in page
    assert admin_client.get("/admin/catalog/category/add/").status_code == 403


def test_business_admin_works(admin_client):
    BusinessFactory(name="Lunares")
    assert "Lunares" in admin_client.get("/admin/businesses/business/").content.decode()
