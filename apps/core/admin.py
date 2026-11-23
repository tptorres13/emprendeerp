from django.contrib import admin


class TenantReadOnlyAdmin(admin.ModelAdmin):
    """Support-staff view over business-owned data: every business, read only.

    Editing business data from the admin would bypass the app's rules, so it
    is disabled on purpose.
    """

    def get_queryset(self, request):
        return self.model.unscoped.select_related("business")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
