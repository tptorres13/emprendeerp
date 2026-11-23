from django.contrib import admin

from .models import Business, Membership


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    autocomplete_fields = ["user"]


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ["name", "industry", "tax_condition", "currency", "created_at"]
    list_filter = ["industry", "tax_condition"]
    search_fields = ["name"]
    inlines = [MembershipInline]
