from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from mainapp import models
from typing import Type

from ipydex import IPS

import scra_core as scra


entity_object_mapping = {}


def convert_entities(model_class: Type[models.BaseModel], onto_entities, **kwargs):
    """

    :param model_class:           target model
    :param onto_entities:   sequence of owlready instances
    :return:                None
    """

    for e in onto_entities:
        # noinspection PyCallingNonCallable
        new_instance = model_class(name=e.name)

        entity_object_mapping[e.iri] = new_instance

        for attr_name, attr_getter in kwargs.items():

            if isinstance(attr_getter, str):
                property_name = attr_getter
                # evaluate the property from the ontology
                value = getattr(e, property_name)
            elif callable(attr_getter):
                value = attr_getter(e)
            else:
                value = None

            # and store it to the db-object
            setattr(new_instance, attr_name, value)

        new_instance.save()


class Command(BaseCommand):
    """
    Run the reasoner and load relevant objects into database

    """

    help = "Run the reasoner and load relevant objects into database."

    def add_arguments(self, parser):
        # Positional arguments
        # parser.add_argument('poll_ids', nargs='+', type=int)

        # Named (optional) arguments
        parser.add_argument(
            "--flush",
            action="store_true",
            help="delete the db before doing anything else",
        )

        parser.add_argument(
            "--no-reasoner",
            action="store_true",
            help="omit running the reasoner (increase performance during testing)",
        )

        parser.add_argument(
            "--interactive",
            action="store_true",
            help="start ipython shell after finishing command (useful during testing)",
        )

    def handle(self, *args, **options):

        RM = scra.RuleManager(settings.PATH_KNOWLEDGEBASE)

        if options.get("flush"):
            call_command("flush", verbosity=0, interactive=False)

        if not options.get("no_reasoner"):
            RM.om.sync_reasoner(infer_property_values=True, infer_data_property_values=True)

        # add geographic entities, source documents, directives

        ge_entities = RM.om.n.GeographicEntity.instances()
        convert_entities(models.GeographicEntity, ge_entities)

        sd_entities = RM.om.n.DirectiveSourceDocument.instances()
        convert_entities(models.SourceDocument, sd_entities, source_uri="hasSourceURI")

        def get_source_doc(entity):

            # these attributes are specified in world.owl.yml
            ref = entity.X_hasDocumentReference_RC.first()
            if ref:
                sd_entity = ref.hasSourceDocument
                return entity_object_mapping[sd_entity.iri]
            else:
                return None

        def get_section(entity):

            # these attributes are specified in world.owl.yml
            ref = entity.X_hasDocumentReference_RC.first()
            if ref:
                return ref.hasSection
            else:
                return None

        dr_entities = RM.om.n.Directive.instances()
        convert_entities(models.Directive, dr_entities, source_document=get_source_doc, section=get_section)

        for ge in ge_entities:
            regional_dr_entities = ge.hasDirective

            ge_object = entity_object_mapping[ge.iri]

            for rdre in regional_dr_entities:
                rdre_object = entity_object_mapping[rdre.iri]

                # add entry to  ManyToManyField
                ge_object.applying_directives.add(rdre_object)

        if options.get("interactive"):
            # this is usefule during development
            dd = RM.om.n.dresden
            IPS(print_tb=False)

        self.stdout.write(self.style.SUCCESS("Done"))
