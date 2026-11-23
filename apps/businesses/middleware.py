from django.shortcuts import redirect

from apps.core.tenancy import use_business

from .services import memberships_for

SESSION_KEY = "current_business_id"


def _resolve_membership(request):
    memberships = list(memberships_for(request.user))
    if not memberships:
        return None
    wanted = request.session.get(SESSION_KEY)
    for membership in memberships:
        if membership.business_id == wanted:
            return membership
    membership = memberships[0]
    request.session[SESSION_KEY] = membership.business_id
    return membership


def business_not_required(view_func):
    """Mark a view as usable by a logged-in user that has no business yet."""
    view_func.business_not_required = True
    return view_func


class CurrentBusinessMiddleware:
    """Activates the user's business for the whole request.

    - `request.business` / `request.membership` are set for logged-in users.
    - Business-owned queries are scoped to that business (see `TenantManager`).
    - Logged-in users without a business are sent to onboarding.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.business = None
        request.membership = None
        user = request.user if request.user.is_authenticated else None
        if user is not None:
            membership = _resolve_membership(request)
            if membership is not None:
                request.membership = membership
                request.business = membership.business
        with use_business(request.business, user):
            return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.business is not None or not request.user.is_authenticated:
            return None
        if getattr(view_func, "business_not_required", False):
            return None
        if getattr(view_func, "login_required", True) is False:
            return None  # public view
        module = getattr(view_func, "__module__", "") or ""
        if module.startswith(("allauth.", "django.contrib.admin")):
            return None
        return redirect("onboarding")
