import pytest

from apps.businesses.tests.factories import BusinessFactory
from apps.catalog.models import Category
from apps.catalog.tests.factories import CategoryFactory
from apps.core.tenancy import TenantScopeError, get_current_business, use_business

pytestmark = pytest.mark.django_db


def test_query_without_active_business_fails_closed():
    with pytest.raises(TenantScopeError):
        list(Category.objects.all())


def test_save_without_active_business_fails_closed():
    with pytest.raises(TenantScopeError):
        Category(name="Sin negocio").save()


def test_save_fills_business_and_audit_fields(business, owner):
    with use_business(business, owner):
        category = CategoryFactory()
    assert category.business == business
    assert category.created_by == owner
    assert category.updated_by == owner


def test_updated_by_tracks_last_editor(business, owner, user):
    with use_business(business, owner):
        category = CategoryFactory()
    with use_business(business, user):
        category.name = "Otro nombre"
        category.save()
    category.refresh_from_db()
    assert category.created_by == owner
    assert category.updated_by == user


def test_cannot_save_a_row_of_another_business(business, owner):
    other = BusinessFactory()
    with use_business(other):
        foreign = CategoryFactory()
    with use_business(business, owner), pytest.raises(TenantScopeError):
        foreign.name = "Hackeado"
        foreign.save()


def test_unscoped_manager_sees_every_business():
    a, b = BusinessFactory(), BusinessFactory()
    with use_business(a):
        CategoryFactory()
    with use_business(b):
        CategoryFactory()
    assert Category.unscoped.count() == 2


def test_use_business_restores_previous_scope(business):
    other = BusinessFactory()
    with use_business(business):
        with use_business(other):
            assert get_current_business() == other
        assert get_current_business() == business
    assert get_current_business() is None
