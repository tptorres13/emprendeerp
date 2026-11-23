import factory

from apps.catalog.models import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    """Must be used inside `use_business(...)` (the business comes from the scope)."""

    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Categoría {n}")
