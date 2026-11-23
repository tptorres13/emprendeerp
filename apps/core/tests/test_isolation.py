"""Every business-owned model must keep each business's data apart.

When you add a new `TenantModel`, register a factory for it in
`TENANT_FACTORIES`; the test below fails until you do.
"""

import pytest
from django.apps import apps

from apps.businesses.tests.factories import BusinessFactory, MembershipFactory
from apps.catalog.tests.factories import CategoryFactory
from apps.core.models import TenantModel
from apps.core.tenancy import use_business

TENANT_FACTORIES = {
    "catalog.Category": CategoryFactory,
}


def tenant_models():
    return [m for m in apps.get_models() if issubclass(m, TenantModel)]


def test_every_tenant_model_has_an_isolation_factory():
    missing = [m._meta.label for m in tenant_models() if m._meta.label not in TENANT_FACTORIES]
    assert not missing, f"Register an isolation factory for: {missing}"


@pytest.mark.django_db
@pytest.mark.parametrize("label", sorted(TENANT_FACTORIES))
def test_business_only_sees_its_own_rows(label):
    model = apps.get_model(label)
    factory = TENANT_FACTORIES[label]
    business_a, business_b = BusinessFactory(), BusinessFactory()
    with use_business(business_a):
        row_a = factory()
    with use_business(business_b):
        row_b = factory()

    with use_business(business_a):
        assert list(model.objects.values_list("pk", flat=True)) == [row_a.pk]
        with pytest.raises(model.DoesNotExist):
            model.objects.get(pk=row_b.pk)
    with use_business(business_b):
        assert list(model.objects.values_list("pk", flat=True)) == [row_b.pk]


@pytest.mark.django_db
def test_pages_only_show_data_of_the_logged_in_business(client):
    owner_a = MembershipFactory(business__name="Negocio A").user
    membership_b = MembershipFactory(business__name="Negocio B")
    with use_business(membership_b.business):
        CategoryFactory(name="Secreto de B")

    client.force_login(owner_a)
    response = client.get("/inicio/")
    assert response.status_code == 200
    assert "Negocio A" in response.content.decode()
    assert "Secreto de B" not in response.content.decode()
