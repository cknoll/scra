from . import models


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
