from django import forms

from .models import Business, Currency, Industry, TaxCondition

TAX_HELP = {
    TaxCondition.MONOTRIBUTO: "Pagás una cuota fija por mes. Tus precios no discriminan IVA.",
    TaxCondition.RESPONSABLE_INSCRIPTO: "Cobrás y pagás IVA. Tus ventas discriminan el IVA.",
    TaxCondition.NOT_REGISTERED: "Podés empezar igual y cambiarlo cuando te inscribas.",
}


class BusinessBasicsForm(forms.Form):
    name = forms.CharField(
        label="¿Cómo se llama tu negocio?",
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Ej: Lunares Deco", "autofocus": True}),
    )
    industry = forms.ChoiceField(
        label="¿Qué vendés?", choices=Industry.choices, widget=forms.RadioSelect
    )

    def clean_name(self):
        name = " ".join(self.cleaned_data["name"].split())
        if not name:
            raise forms.ValidationError("Escribí el nombre de tu negocio.")
        return name


class BusinessTaxForm(forms.Form):
    tax_condition = forms.ChoiceField(
        label="¿Cuál es tu situación frente a ARCA (ex AFIP)?",
        choices=TaxCondition.choices,
        widget=forms.RadioSelect,
    )
    currency = forms.ChoiceField(
        label="¿En qué moneda manejás tus precios?",
        choices=Currency.choices,
        initial=Currency.ARS,
        widget=forms.RadioSelect,
        help_text="Después vas a poder cargar precios en dólares con la cotización que elijas.",
    )


class BusinessCategoriesForm(forms.Form):
    categories = forms.MultipleChoiceField(
        label="Elegí las categorías que querés usar",
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    extra_categories = forms.CharField(
        label="¿Querés sumar otras?",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Una por línea"}),
        help_text="Podés agregar, cambiar o borrar categorías cuando quieras.",
    )

    def __init__(self, *args, presets: list[str], **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categories"].choices = [(name, name) for name in presets]
        if not self.is_bound:
            self.fields["categories"].initial = presets
        if not presets:
            del self.fields["categories"]
            self.fields["extra_categories"].label = "¿Con qué categorías querés empezar?"

    def category_names(self) -> list[str]:
        names = list(self.cleaned_data.get("categories", []))
        names += self.cleaned_data.get("extra_categories", "").splitlines()
        return names


class BusinessSettingsForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ["name", "industry", "tax_condition", "currency"]
        widgets = {"tax_condition": forms.RadioSelect, "currency": forms.RadioSelect}
