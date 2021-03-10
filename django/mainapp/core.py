import os
from django.conf import settings
from . import models

# noinspection PyUnresolvedReferences
from ipydex import IPS


from django.shortcuts import get_object_or_404

MD_CONTENT_PATH = os.path.join(settings.DJANGO_BASEDIR, "mainapp", "md_content")


def get_md_content(md_fname: str) -> str:

    assert md_fname.endswith("md")
    path = os.path.join(MD_CONTENT_PATH, md_fname)

    with open(path, "r") as txtfile:
        md_src = txtfile.read()

    return md_src


def update_with_search_hints(context):

    all_ge = models.GeographicEntity.objects.all()
    all_tags = models.Tag.objects.all()
    context.update(all_ge=all_ge, all_tags=all_tags)


def get_directives_for_ge(ge_name: str) -> list:
    """

    :param ge_name:
    :return:
    """

    ge = models.GeographicEntity.objects.filter(name=ge_name).first()
    if ge:
        directive_list = list(ge.applying_directives.all())
    else:
        directive_list = []

    return directive_list


def get_directives(ge_name: str, *taglist) -> list:
    """

    :param ge_name:
    :return:
    """

    ge = get_object_or_404(models.GeographicEntity, name=ge_name)
    if not ge:
        msg = f'Unkonwn GeographicEntity: "{ge_name}"'
        raise ValueError(msg)

    directive_list = ge.applying_directives.all()
    matching_tags = models.Tag.objects.all().filter(label__in=[*taglist])

    if taglist:
        result = directive_list.filter(tags__in=matching_tags)
    else:
        result = directive_list

    return list(result)
