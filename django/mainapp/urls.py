from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.static_md_view, name="landingpage", kwargs={"md_fname": "index.md"}),
    path("query", views.QueryView.as_view(), name="query-page"),
    path(r"debug", views.debug_view, name="imprint-page"),
    path(r"debug", views.debug_view, name="privacy-page"),
    path(r"debug", views.debug_view, name="contact-page"),
    path(r"debug", views.debug_view, name="debugpage0"),
    path(r"debug/<int:xyz>", views.debug_view, name="debugpage_with_argument"),
]
