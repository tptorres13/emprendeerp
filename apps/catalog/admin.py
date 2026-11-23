from django.contrib import admin

from apps.core.admin import TenantReadOnlyAdmin

from .models import Category


@admin.register(Category)
class CategoryAdmin(TenantReadOnlyAdmin):
    list_display = ["name", "business", "created_at"]
    search_fields = ["name", "business__name"]
