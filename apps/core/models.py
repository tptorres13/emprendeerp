from django.conf import settings
from django.db import models

from .tenancy import TenantScopeError, get_current_user, require_current_business


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantQuerySet(models.QuerySet):
    pass


class TenantManager(models.Manager.from_queryset(TenantQuerySet)):
    """Default manager for business-owned models: always filtered by the active business."""

    def get_queryset(self):
        business = require_current_business()
        return super().get_queryset().filter(business=business)


class TenantModel(TimeStampedModel):
    """Base class for every model that belongs to a business.

    - `objects` only ever returns rows of the active business (and raises if
      there is none).
    - `unscoped` sees every business. Use it only for system-level work
      (admin, maintenance commands, background jobs that loop over businesses).
    - `business`, `created_by` and `updated_by` are filled automatically.
    """

    business = models.ForeignKey(
        "businesses.Business", on_delete=models.CASCADE, related_name="+", editable=False
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        editable=False,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        editable=False,
    )

    objects = TenantManager()
    unscoped = models.Manager()  # noqa: DJ012 (second manager, not a field)

    class Meta:
        abstract = True
        # Related-object access (e.g. `line.product`) and deletion cascades use
        # the plain manager; the parent row was already scoped.
        base_manager_name = "unscoped"

    def save(self, *args, **kwargs):
        business = require_current_business()
        if self.business_id is None:
            self.business = business
        elif self.business_id != business.pk:
            raise TenantScopeError(
                f"Refusing to save {self.__class__.__name__} of business "
                f"{self.business_id} while business {business.pk} is active."
            )
        user = get_current_user()
        if user is not None and getattr(user, "is_authenticated", False):
            if self._state.adding and self.created_by_id is None:
                self.created_by = user
            self.updated_by = user
        super().save(*args, **kwargs)
