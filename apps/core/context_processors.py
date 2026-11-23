from django.conf import settings

from .navigation import nav_items_for


def app_context(request):
    return {
        "PRODUCT_NAME": settings.PRODUCT_NAME,
        "current_business": getattr(request, "business", None),
        "nav_items": nav_items_for(request),
    }
