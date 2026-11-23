from django.forms.renderers import TemplatesSetting


class AppFormRenderer(TemplatesSetting):
    """Render every form (ours and allauth's) with the app's own templates."""

    form_template_name = "forms/form.html"
    field_template_name = "forms/field.html"
