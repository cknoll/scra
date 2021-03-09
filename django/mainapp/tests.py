from django.test import TestCase
from django.urls import reverse
from . import unittest_helpers as uh
from . import models, core

# noinspection PyUnresolvedReferences
from ipydex import IPS

# The tests can be run with
# `python manage.py test`
# `python manage.py test --rednose` # with colors


class TestMainApp1(TestCase):
    def setup(self):
        pass

    def test_home_page1(self):

        # get url by its unique name, see urls.py

        url = reverse("landingpage")
        res = self.client.get(url)

        # `utc` means "unit test comment"
        # this is a simple mechanism to ensure the desired content actually was delivered
        self.assertEquals(res.status_code, 200)
        self.assertContains(res, "utc_landing_page")

    def test_populate(self):

        uh.call_command_silent("populate_db_from_ontology", flush=True, no_reasoner=True)

        r = models.Directive.objects.filter(name__startswith="COVID19_rules_of_saxony").first()
        self.assertEqual(len(r.tags.all()), 3)
        self.assertTrue("Maskenpflicht" in r.text)

    def test_query_without_tags(self):
        uh.call_command_silent("populate_db_from_ontology", flush=True)

        url = reverse("query-page")
        res = self.client.get(url)
        self.assertEquals(res.status_code, 200)
        self.assertContains(res, "utc_query_page")

        form = uh.get_first_form(res)

        form_values = {"GeographicEntity": "saxony", "tag1": "", "tag2": ""}
        post_data = uh.generate_post_data_for_form(form, spec_values=form_values)

        res2 = self.client.post(url, post_data)
        self.assertContains(res2, "utc_number_of_directives:7")

    def test_query_with_tags(self):
        uh.call_command_silent("populate_db_from_ontology", flush=True)

        url = reverse("query-page")
        res = self.client.get(url)
        self.assertEquals(res.status_code, 200)
        self.assertContains(res, "utc_query_page")

        form = uh.get_first_form(res)

        form_values = {"GeographicEntity": "saxony", "tag1": "Reisen", "tag2": ""}
        post_data = uh.generate_post_data_for_form(form, spec_values=form_values)

        res2 = self.client.post(url, post_data)
        dll = uh.parse_json_object(res2, "directive_list_length")
        self.assertEqual(dll, 3)

    def test_get_directives(self):

        uh.call_command_silent("populate_db_from_ontology", flush=True, no_reasoner=False)

        # test behaviour with tags
        res = core.get_directives("saxony", "Reisen")

        self.assertEquals(len(res), 3)

        res = core.get_directives("saxony", "Bewegungsfreiheit")
        self.assertEquals(len(res), 2)

        res = core.get_directives("saxony", "Gastronomie")
        self.assertEquals(len(res), 1)

    def test_debug1(self):
        res = self.client.get(reverse("debugpage0"))
        self.assertEquals(res.status_code, 200)

        url = reverse("debugpage_with_argument", kwargs={"xyz": 1})

        print("\n-> Debug-URL with argument:", url)
        # this will start the interactive shell inside the view
        # res = self.client.get(url)

        # this will deliberately provoke an server error (http status code 500)
        res = self.client.get(reverse("debugpage_with_argument", kwargs={"xyz": 2}))
        self.assertEquals(res.status_code, 500)
