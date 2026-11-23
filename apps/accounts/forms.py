from django import forms


class SignupExtraForm(forms.Form):
    """Extra fields for allauth's signup form."""

    full_name = forms.CharField(
        label="Tu nombre",
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "name", "placeholder": "Ej: Ana Pérez"}),
    )

    field_order = ["full_name", "email", "password1"]

    def signup(self, request, user):
        user.full_name = self.cleaned_data["full_name"].strip()
        user.save(update_fields=["full_name"])
