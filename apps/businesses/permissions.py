from functools import wraps

from django.core.exceptions import PermissionDenied

from .models import Role


def role_required(*roles: str):
    """Allow the view only to members of the current business with one of `roles`."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            membership = getattr(request, "membership", None)
            if membership is None or membership.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


owner_required = role_required(Role.OWNER)
