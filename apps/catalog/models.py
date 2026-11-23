from django.db import models
from django.db.models.functions import Lower

from apps.core.models import TenantModel


class Category(TenantModel):
    name = models.CharField("nombre", max_length=80)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                "business", Lower("name"), name="unique_category_name_per_business"
            ),
        ]

    def __str__(self):
        return self.name
