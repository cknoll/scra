from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.views import View
from . import models
from . import core


from ipydex import IPS


def static_md_view(request, md_fname=None):

    try:
        md_src = core.get_md_content(md_fname)
    except FileNotFoundError:
        return HttpResponseServerError(f"File not found: {md_fname}")

    context = {"title": "Title", "md_src": md_src}

    return render(request, "mainapp/md_view.html", context)


class QueryView(View):
    def get(self, request, landingpage=False):

        context = {"landingpage": landingpage}
        if landingpage:
            md_fname = "index.md"
            try:
                md_src = core.get_md_content(md_fname)
            except FileNotFoundError:
                return HttpResponseServerError(f"File not found: {md_fname}")

            context.update(md_src=md_src)
            core.update_with_search_hints(context)

        return render(request, "mainapp/query.html", context)

    def post(self, request, **kwargs):
        ge_str = request.POST.get("GeographicEntity")
        if not ge_str:
            return redirect(reverse("query-page"))

        tag_strings = [value for key, value in request.POST.items() if key.startswith("tag") and value]
        directives = core.get_directives(ge_str, *tag_strings)

        ge = models.GeographicEntity.objects.filter(name=ge_str).first()
        context = {"result_ge": ge, "directive_list": directives}
        core.update_with_search_hints(context)

        return render(request, "mainapp/query.html", context)


def debug_view(request, xyz=0):

    z = 1

    if xyz == 1:
        # start interactive shell for debugging (helpful if called from the unittests)
        IPS()

    elif xyz == 2:
        return HttpResponseServerError("Errormessage")

    return HttpResponse("Some plain message")
