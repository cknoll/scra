from . import models
from ipydex import IPS

from django.shortcuts import get_object_or_404


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
