"""Request-scoped "current business" and "current user".

Every business-owned query goes through `TenantManager`, which reads the active
business from here. If there is no active business the query fails loudly
instead of returning data from every business (fail closed).
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from apps.businesses.models import Business

_current_business: ContextVar[Business | None] = ContextVar("current_business", default=None)
_current_user: ContextVar[Any | None] = ContextVar("current_user", default=None)


class TenantScopeError(RuntimeError):
    """Raised when business-owned data is accessed without an active business."""


def get_current_business() -> Business | None:
    return _current_business.get()


def require_current_business() -> Business:
    business = _current_business.get()
    if business is None:
        raise TenantScopeError(
            "No active business. Wrap the code in `use_business(...)` or use the "
            "`unscoped` manager explicitly for system-level work."
        )
    return business


def get_current_user():
    return _current_user.get()


@contextmanager
def use_business(business: Business | None, user=None):
    """Activate `business` (and optionally `user`) for the enclosed block."""
    business_token = _current_business.set(business)
    user_token = _current_user.set(user)
    try:
        yield business
    finally:
        _current_business.reset(business_token)
        _current_user.reset(user_token)
