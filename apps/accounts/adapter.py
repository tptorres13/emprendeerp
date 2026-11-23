from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):
    def render_mail(self, template_prefix, email, context, headers=None):
        context = {**context, "product_name": settings.PRODUCT_NAME}
        return super().render_mail(template_prefix, email, context, headers=headers)
