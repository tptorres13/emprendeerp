import pytest
from django.db import IntegrityError

from apps.catalog.tests.factories import CategoryFactory

pytestmark = pytest.mark.django_db


def test_category_names_are_unique_per_business_ignoring_case(in_business):
    CategoryFactory(name="Remeras")
    with pytest.raises(IntegrityError):
        CategoryFactory(name="REMERAS")


def test_str(in_business):
    assert str(CategoryFactory(name="Remeras")) == "Remeras"
