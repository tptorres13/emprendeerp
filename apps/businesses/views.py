from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import (
    TAX_HELP,
    BusinessBasicsForm,
    BusinessCategoriesForm,
    BusinessSettingsForm,
    BusinessTaxForm,
)
from .industry_presets import presets_for
from .middleware import SESSION_KEY, business_not_required
from .permissions import owner_required
from .services import create_business

ONBOARDING_SESSION_KEY = "onboarding"
STEPS = {1: BusinessBasicsForm, 2: BusinessTaxForm, 3: BusinessCategoriesForm}
TOTAL_STEPS = len(STEPS)


def _build_form(step: int, data, state: dict):
    form_class = STEPS[step]
    kwargs = {"data": data}
    if step == 3:
        kwargs["presets"] = presets_for(state.get("industry", ""))
    else:
        kwargs["initial"] = state
    return form_class(**kwargs)


@business_not_required
@require_http_methods(["GET", "POST"])
def onboarding(request):
    if request.business is not None:
        return redirect("home")

    state = request.session.get(ONBOARDING_SESSION_KEY, {})
    try:
        step = int(request.GET.get("paso", 1))
    except ValueError:
        step = 1
    # Never skip ahead of the data we already have.
    max_step = 1 + sum(1 for s in (1, 2) if state.get(f"step{s}_done"))
    step = min(max(step, 1), max_step, TOTAL_STEPS)

    if request.method == "POST":
        form = _build_form(step, request.POST, state)
        if form.is_valid():
            if step < TOTAL_STEPS:
                state.update(form.cleaned_data)
                state[f"step{step}_done"] = True
                request.session[ONBOARDING_SESSION_KEY] = state
                return redirect(f"{request.path}?paso={step + 1}")
            business = create_business(
                owner=request.user,
                name=state["name"],
                industry=state["industry"],
                tax_condition=state["tax_condition"],
                currency=state["currency"],
                category_names=form.category_names(),
            )
            request.session.pop(ONBOARDING_SESSION_KEY, None)
            request.session[SESSION_KEY] = business.pk
            messages.success(request, f"¡Listo! {business.name} ya está creado.")
            return redirect("home")
    else:
        form = _build_form(step, None, state)

    return render(
        request,
        "businesses/onboarding.html",
        {
            "form": form,
            "step": step,
            "total_steps": TOTAL_STEPS,
            "steps_range": range(1, TOTAL_STEPS + 1),
            "tax_help": TAX_HELP,
        },
    )


@owner_required
@require_http_methods(["GET", "POST"])
def business_settings(request):
    form = BusinessSettingsForm(request.POST or None, instance=request.business)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Guardamos los cambios.")
        return redirect("business_settings")
    return render(request, "businesses/settings.html", {"form": form})
