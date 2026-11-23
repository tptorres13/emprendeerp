from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Industry(models.TextChoices):
    CLOTHING = "clothing", "Ropa y accesorios"
    FOOD = "food", "Alimentos y bebidas"
    BEAUTY = "beauty", "Cosmética y cuidado personal"
    HOME = "home", "Deco y hogar"
    ELECTRONICS = "electronics", "Tecnología y electrónica"
    CRAFTS = "crafts", "Artesanías y regalos"
    OTHER = "other", "Otro rubro"


class TaxCondition(models.TextChoices):
    MONOTRIBUTO = "monotributo", "Monotributo"
    RESPONSABLE_INSCRIPTO = "responsable_inscripto", "Responsable inscripto"
    NOT_REGISTERED = "not_registered", "Todavía no estoy inscripto"


class Currency(models.TextChoices):
    ARS = "ARS", "Pesos argentinos (ARS)"
    USD = "USD", "Dólares (USD)"


class Business(TimeStampedModel):
    """The tenant. Every business-owned row points here."""

    name = models.CharField("nombre del negocio", max_length=120)
    industry = models.CharField("rubro", max_length=20, choices=Industry.choices)
    tax_condition = models.CharField(
        "condición frente al IVA", max_length=30, choices=TaxCondition.choices
    )
    currency = models.CharField(
        "moneda principal", max_length=3, choices=Currency.choices, default=Currency.ARS
    )

    class Meta:
        verbose_name = "negocio"
        verbose_name_plural = "negocios"

    def __str__(self):
        return self.name


class Role(models.TextChoices):
    OWNER = "owner", "Dueño/a"
    SELLER = "seller", "Vendedor/a"
    VIEWER = "viewer", "Solo lectura"


class Membership(TimeStampedModel):
    """Links a user to a business with a role.

    Today every business has a single owner; the model already supports
    several users with different roles.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.OWNER)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "membresía"
        verbose_name_plural = "membresías"
        constraints = [
            models.UniqueConstraint(fields=["user", "business"], name="unique_membership"),
        ]

    def __str__(self):
        return f"{self.user} @ {self.business} ({self.get_role_display()})"
