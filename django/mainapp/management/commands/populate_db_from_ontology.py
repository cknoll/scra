from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from mainapp import models
from mainapp import core
from typing import Type, List

from ipydex import IPS

import scra_core as scra


entity_object_mapping = {}


def convert_entities(model_class: Type[models.BaseModel], onto_entities, **kwargs) -> List[models.BaseModel]:
    """

    :param model_class:           target model
    :param onto_entities:   sequence of owlready instances
    :return:                None
    """

    result = []
    for e in onto_entities:
        # noinspection PyCallingNonCallable
        new_instance = model_class(name=e.name)

        entity_object_mapping[e.iri] = new_instance

        ManyToMany_handler_tuples = []

        for attr_name, attr_getter in kwargs.items():

            if isinstance(attr_getter, str):
                property_name = attr_getter
                # evaluate the property from the ontology
                value = getattr(e, property_name)
                setattr(new_instance, attr_name, value)
            elif callable(attr_getter) and attr_getter.__name__.startswith("get"):
                value = attr_getter(e)
                setattr(new_instance, attr_name, value)
            elif callable(attr_getter) and attr_getter.__name__.startswith("add"):
                # ManyToManyFields must be handled after the instance has been saved (id necessary)
                ManyToMany_handler_tuples.append((e, new_instance, attr_name, attr_getter))

            else:
                value = None
                setattr(new_instance, attr_name, value)

            # and store it to the db-object

        new_instance.save()

        # Handle ManyToManyFields (must take place after the instance has been saved (id necessary))
        for owl_entity, new_instance, attr_name, attr_getter in ManyToMany_handler_tuples:
            # evaluate the `add_...` function and iterate over that list
            for res in attr_getter(owl_entity):
                getattr(new_instance, attr_name).add(res)

        result.append(new_instance)

    return result


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

        # note that tags are modelled as classes not as instances
        tag_entities = RM.om.n.Tag.descendants()
        django_tag_entities = convert_entities(models.Tag, tag_entities)

        # auxiliary functions to convert direcitves (must start with "get" or "add")

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

        def add_tags(dr_entity):
            """
            returns a list of django_tag_objects for the supplied Directive-instance

            :param dr_entity:
            :return:
            """

            owl_tags = [
                elt.value
                for elt in dr_entity.is_a
                if isinstance(elt, scra.ypo.owl2.class_construct.Restriction) and elt.property == RM.om.n.hasTag
            ]

            python_tags = [entity_object_mapping[tag.iri] for tag in owl_tags]
            return python_tags

        dr_entities = RM.om.n.Directive.instances()

        # add_tags(list(dr_entities)[-2])

        django_directive_entities = convert_entities(
            models.Directive, dr_entities, source_document=get_source_doc, section=get_section, tags=add_tags
        )

        # associate the directives to the GeographicEntities (assuming successful reasoning has been performed)
        for ge in ge_entities:
            regional_dr_entities = ge.hasDirective

            ge_object = entity_object_mapping[ge.iri]

            for rdre in regional_dr_entities:
                # retrieve the according django object
                rdre_object = entity_object_mapping[rdre.iri]

                # add entry to  ManyToManyField
                ge_object.applying_directives.add(rdre_object)

        if options.get("interactive"):
            # this is usefule during development
            dd = RM.om.n.dresden
            IPS(print_tb=False)

        self.stdout.write(self.style.SUCCESS("Done"))
