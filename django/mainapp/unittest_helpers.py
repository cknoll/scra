from django.core.management import call_command
from bs4 import BeautifulSoup

from ipydex import IPS
import json


def get_first_form(response):
    """
    Auxiliary function that returns a bs-object of the first form which is specifies by action-url.

    :param response:
    :return:
    """
    bs = BeautifulSoup(response.content, "html.parser")
    forms = bs.find_all("form")

    return forms[0]


def get_form_fields_to_submit(form):
    """
    Return two lists: fields and hidden_fields.

    :param form:
    :return:
    """

    inputs = form.find_all("input")
    # noinspection SpellCheckingInspection
    textareas = form.find_all("textarea")

    post_fields = inputs + textareas

    types_to_omit = ["submit", "cancel"]

    fields = []
    hidden_fields = []
    for field in post_fields:
        # noinspection SpellCheckingInspection
        ftype = field.attrs.get("type")
        if ftype in types_to_omit:
            continue

        if ftype == "hidden":
            hidden_fields.append(field)
        else:
            fields.append(field)

    return fields, hidden_fields


def generate_post_data_for_form(form, default_value="xyz", spec_values=None):
    """
    Return a dict containing all dummy-data for the form

    :param form:
    :param default_value:   str; use this value for all not specified fields
    :param spec_values:     dict; use these values to override default value

    :return:                dict of post_data
    """

    if spec_values is None:
        spec_values = {}

    fields, hidden_fields = get_form_fields_to_submit(form)

    all_field_names = []

    post_data = {}
    for f in hidden_fields:
        name = f.attrs.get("name")
        all_field_names.append(name)
        post_data[f.attrs["name"]] = f.attrs["value"]

    for f in fields:
        name = f.attrs.get("name")

        if name is None:
            # ignore fields without a name (relevant for dropdown checkbox)
            continue
        all_field_names.append(name)

        if name.startswith("captcha"):
            # special case for captcha fields (assume CAPTCHA_TEST_MODE=True)
            post_data[name] = "passed"
        else:
            post_data[name] = default_value

    # ensure that the keys of spec_values indeed refer to form field names:

    spec_keys = set(spec_values.keys())
    assert spec_keys.difference(all_field_names) == set()

    post_data.update(spec_values)

    return post_data


def parse_json_object(response, id_value: str):
    bs = BeautifulSoup(response.content, "html.parser")
    tag = bs.find("script", attrs={"id": id_value})

    assert tag
    assert len(tag.contents) == 1

    res = json.loads(tag.contents[0])

    return res


def call_command_silent(*args, **kwargs):
    kwargs.update(silent=True)
    call_command(*args, **kwargs)
