import os

from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.views import View
from django.conf import settings
from . import models
from . import core


from ipydex import IPS


def static_md_view(request, md_fname=None):

    assert md_fname.endswith("md")
    path = os.path.join(settings.BASE_DIR, "mainapp", "md_content", md_fname)
    try:

        with open(path, "r") as txtfile:
            md_src = txtfile.read()
    except FileNotFoundError:
        return HttpResponseServerError(f"File not found: {md_fname}")

    all_ge = models.GeographicEntity.objects.all()
    context = {"title": "Title", "md_src": md_src, "all_ge": all_ge}

    return render(request, "mainapp/md_view.html", context)


class QueryView(View):
    def get(self, request):
        context = {}

        return render(request, "mainapp/query.html", context)

    def post(self, request):
        ge_str = request.POST.get("GeographicEntity")
        if not ge_str:
            return redirect(reverse("query-page"))

        tag_strings = [value for key, value in request.POST.items() if key.startswith("tag") and value]
        directives = core.get_directives(ge_str, *tag_strings)

        ge = models.GeographicEntity.objects.filter(name=ge_str).first()
        context = {"result_ge": ge, "directive_list": directives}

        return render(request, "mainapp/query.html", context)


def debug_view(request, xyz=0):

    z = 1

    if xyz == 1:
        # start interactive shell for debugging (helpful if called from the unittests)
        IPS()

    elif xyz == 2:
        return HttpResponseServerError("Errormessage")

    return HttpResponse("Some plain message")
