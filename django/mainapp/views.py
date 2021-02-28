import os
import json
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.views import View
from mainapp import models
from ipydex import IPS


def home_page_view(request):

    all_ge = models.GeographicEntity.objects.all()

    context = {"all_ge": all_ge}

    return render(request, "mainapp/landing.html", context)


class QueryView(View):
    def get(self, request):
        context = {}

        return render(request, "mainapp/query.html", context)

    def post(self, request):
        ge_str = request.POST.get("GeographicEntity")
        if not ge_str:
            return redirect(reverse("query-page"))
        else:
            ge = models.GeographicEntity.objects.filter(name=ge_str).first()

            directive_list = []

        context = {"result": ge, "directive_list": directive_list}

        return render(request, "mainapp/query.html", context)


def debug_view(request, xyz=0):

    z = 1

    if xyz == 1:
        # start interactive shell for debugging (helpful if called from the unittests)
        IPS()

    elif xyz == 2:
        return HttpResponseServerError("Errormessage")

    return HttpResponse("Some plain message")
