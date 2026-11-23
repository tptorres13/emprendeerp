import factory

from apps.accounts.tests.factories import UserFactory
from apps.businesses.models import Business, Currency, Industry, Membership, Role, TaxCondition


class BusinessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Business

    name = factory.Sequence(lambda n: f"Negocio {n}")
    industry = Industry.HOME
    tax_condition = TaxCondition.MONOTRIBUTO
    currency = Currency.ARS


class MembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Membership

    user = factory.SubFactory(UserFactory)
    business = factory.SubFactory(BusinessFactory)
    role = Role.OWNER
