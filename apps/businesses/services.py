from django.db import transaction

from apps.catalog.models import Category
from apps.core.tenancy import use_business

from .models import Business, Membership, Role


@transaction.atomic
def create_business(
    *,
    owner,
    name: str,
    industry: str,
    tax_condition: str,
    currency: str,
    category_names: list[str] | None = None,
) -> Business:
    """Create a business, make `owner` its owner and load its starter categories."""
    business = Business.objects.create(
        name=name.strip(), industry=industry, tax_condition=tax_condition, currency=currency
    )
    Membership.objects.create(user=owner, business=business, role=Role.OWNER)

    seen: set[str] = set()
    with use_business(business, owner):
        for raw in category_names or []:
            category_name = " ".join(raw.split())
            key = category_name.casefold()
            if not category_name or key in seen:
                continue
            seen.add(key)
            Category.objects.create(name=category_name[:80])
    return business


def memberships_for(user):
    return (
        Membership.objects.filter(user=user, is_active=True)
        .select_related("business")
        .order_by("created_at")
    )
