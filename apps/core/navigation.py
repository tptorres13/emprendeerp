"""Main navigation. Each module adds its entry here when it ships."""

from dataclasses import dataclass

from django.urls import reverse

from apps.businesses.models import Role


@dataclass(frozen=True)
class NavItem:
    label: str
    url_name: str
    icon: str
    roles: tuple[str, ...] = (Role.OWNER, Role.SELLER, Role.VIEWER)


NAV = [
    NavItem("Inicio", "home", "home"),
    NavItem("Mi negocio", "business_settings", "briefcase", roles=(Role.OWNER,)),
    NavItem("Mi cuenta", "account_change_password", "user"),
]


def nav_items_for(request) -> list[dict]:
    membership = getattr(request, "membership", None)
    if membership is None:
        return []
    items = []
    for item in NAV:
        if membership.role not in item.roles:
            continue
        url = reverse(item.url_name)
        items.append(
            {
                "label": item.label,
                "url": url,
                "icon": item.icon,
                "active": request.path == url or (url != "/" and request.path.startswith(url)),
            }
        )
    return items
