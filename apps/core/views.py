from django.contrib.auth.decorators import login_not_required
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from apps.catalog.models import Category


@login_not_required
def landing(request):
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "core/landing.html")


def home(request):
    categories = Category.objects.all()
    return render(request, "core/home.html", {"categories": categories})


@login_not_required
@never_cache
def healthz(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return HttpResponse("ok", content_type="text/plain")
