import pytest

from apps.accounts.tests.factories import DEFAULT_PASSWORD, UserFactory
from apps.businesses.models import Role
from apps.businesses.tests.factories import BusinessFactory, MembershipFactory
from apps.core.tenancy import use_business


@pytest.fixture
def password():
    return DEFAULT_PASSWORD


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def business(db):
    return BusinessFactory()


@pytest.fixture
def owner(business):
    return MembershipFactory(business=business, role=Role.OWNER).user


@pytest.fixture
def owner_client(client, owner):
    client.force_login(owner)
    return client


@pytest.fixture
def in_business(business, owner):
    """Activate `business` for code that touches business-owned data directly."""
    with use_business(business, owner):
        yield business
