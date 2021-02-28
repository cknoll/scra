from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from mainapp import models

from ipydex import IPS

import scra_core as scra


def convert_entities(model_class: models.BaseModel, onto_entities):
    """

    :param model_class:           target model
    :param onto_entities:   sequence of owlready instances
    :return:                None
    """

    for e in onto_entities:
        # noinspection PyCallingNonCallable
        new_instance = model_class(name=e.name)
        new_instance.save()


class Command(BaseCommand):
    """
    Run the reasoner and load relevant objects into database

    """
    help = 'Run the reasoner and load relevant objects into database.'

    def add_arguments(self, parser):
        # Positional arguments
        # parser.add_argument('poll_ids', nargs='+', type=int)

        # Named (optional) arguments
        parser.add_argument(
            '--flush',
            action='store_true',
            help='delete the db before doing anything else',
        )

    def handle(self, *args, **options):

        RM = scra.RuleManager(settings.PATH_KNOWLEDGEBASE)
        RM.om.sync_reasoner(infer_property_values=True, infer_data_property_values=True)

        if options.get("flush"):
            call_command("flush", verbosity=0, interactive=False)

        # add geographic entities

        ge_entities = RM.om.n.GeographicEntity.instances()

        convert_entities(models.GeographicEntity, ge_entities)

        self.stdout.write("working")
        IPS(print_tb=False)
        self.stdout.write(self.style.SUCCESS('Done'))
