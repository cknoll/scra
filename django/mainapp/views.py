import os
import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

from ipydex import IPS


def home_page_view(request):

    context = {}

    return render(request, 'mainapp/landing.html', context)


def debug_view(request, xyz=0):

    z = 1

    if xyz == 1:
        # start interactive shell for debugging (helpful if called from the unittests)
        IPS()

    elif xyz == 2:
        return HttpResponseServerError("Errormessage")

    return HttpResponse('Some plain message')