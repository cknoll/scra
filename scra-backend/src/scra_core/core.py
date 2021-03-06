import os
from typing import List, Tuple, Dict, Union
from collections import defaultdict

import yaml
import yamlpyowl as ypo

from ipydex import IPS

from . import util

LANGUAGE_CODES = ["de_de"]


class SemanticManager(object):
    def __init__(self, om: ypo.OntologyManager):
        self.om = om

    def get_directives_for_region(self, region: str) -> set:
        """

        :param region:
        :return:
        """

        qq = f"""
        PREFIX P: <{self.om.iri}>
        SELECT ?x WHERE {{
        P:{region} P:hasDirective ?x.}}
        """

        return self.om.make_query(qq)


class RuleManager(object):
    """
    Loads rules form specific yaml files and convert the into ontological python objects.
    """

    def __init__(self, basepath: str, om: ypo.OntologyManager = None):

        self.basepath = basepath
        self.basepath_rules = os.path.join(basepath, "rules")
        if om:
            self.om = om
        else:
            onto_path = os.path.join(basepath, "general", "world.yml")
            self.om = ypo.OntologyManager(onto_path, world=ypo.owl2.World())

        self.files = []
        self.raw_yaml_contents = []
        self.directives: List[ypo.Thing] = []

        # dict of items like [("de_de", <inner_dict1>), ...]
        # where inner_dict1 consists of items like [(<label_str>, <tag_object>), ...]
        self.label_tag_map: Dict[str, dict] = defaultdict(dict)

        # dict of inverse dicts. inner_dicts consists of items like [(<tag_object.iri>, <label_str>), ...]
        self.tag_iri_label_map: Dict[str, dict] = defaultdict(dict)

        self._get_tags()

        self._get_all_files()
        self._load_rule_data()
        self._process_all_rule_data()

    def _get_all_files(self):

        for subdir, dirs, files in os.walk(self.basepath):
            for file in files:
                if file == "rules.yml":
                    self.files.append(os.path.join(subdir, file))

    def _load_rule_data(self):

        for fpath in self.files:

            with open(fpath, "r") as myfile:
                yaml_docs = tuple(yaml.safe_load_all(myfile))

                # the tuple should contain of a header-dict and a rule-list
                assert len(yaml_docs) == 2
                self.raw_yaml_contents.append(yaml_docs)

    def _process_all_rule_data(self):

        for raw_object in self.raw_yaml_contents:
            assert ypo.check_type(raw_object, Tuple[dict, list])
            self._process_rule_document(raw_object)

    def _get_tags(self):
        # note that tags are classes, not individuals.
        tag_entities = list(self.om.n.Tag.descendants())

        for te in tag_entities:
            for lc in LANGUAGE_CODES:
                label = self._get_label_with_lc(te, lc)
                self.label_tag_map[lc][label] = te

                # also save the inverse mapping
                self.tag_iri_label_map[lc][te.iri] = label

    @staticmethod
    def _get_label_with_lc(entity: ypo.Thing, lc: str) -> Union[str, None]:
        for label_entry in entity.label:
            lc_marker = f"@{lc}"
            if label_entry.endswith(lc_marker):
                return label_entry.replace(lc_marker, "").strip()
            else:
                return None

    def _process_rule_document(self, raw_tuple: Tuple[dict, list]):

        header_dict, rule_list = raw_tuple
        assert header_dict["extends"] == self.om.iri
        sd_name = header_dict["iri-suffix"]
        labels = header_dict["labels"]
        source_uri = header_dict["source"]
        language_code = header_dict["language"]
        applies_to = [self._resolve_name(n) for n in ypo.ensure_list(header_dict["appliesTo"])]

        full_iri = f"{self.om.iri}{sd_name}"

        # ensure that this iri is unique
        assert len(self.om.onto.search(iri=full_iri)) == 0

        source_doc = self.om.n.DirectiveSourceDocument(
            sd_name, label=labels, hasSourceURI=source_uri, appliesTo=applies_to
        )

        for i, outer_rule_dict in enumerate(rule_list):

            assert len(outer_rule_dict) == 1
            inner_rule_dict = outer_rule_dict["Directive"]

            python_directive = Directive(self, inner_rule_dict, source_doc, i + 1, language_code)

            doc_ref = python_directive.get_doc_ref()

            # now create the ontological object
            owl_directive = self.om.n.Directive(name=python_directive.name, X_hasDocumentReference_RC=[doc_ref])

            python_directive.add_restrictions_for_tags(owl_directive)

    def _resolve_name(self, name):

        return self.om.name_mapping[name]


class Directive(object):
    def __init__(
        self, rule_manager: RuleManager, inner_rule_dict: dict, source_doc: ypo.Thing, counter: int, language_code: str
    ):
        self.RM = rule_manager
        self.inner_rule_dict = inner_rule_dict
        self.source_doc = source_doc
        self.counter = counter
        self.language_code = language_code

        self.section = inner_rule_dict["section"]
        self.name = f"{self.source_doc.name}_{counter:03d}"

        self.tags: List[ypo.Thing] = []
        self._get_tags()

    def get_doc_ref(self):
        doc_ref = self.RM.om.n.X_DocumentReference_RC(
            name=f"{self.name}_dref", hasSourceDocument=self.source_doc, hasSection=self.section
        )

        return doc_ref

    def _get_tags(self) -> None:
        """
        Parse the natural language tags from the rule.yml files and match them to the owl-objects
        """

        tag_strings = self.inner_rule_dict.get("tags", [])

        if not tag_strings:
            msg = f"The rule {self.name} needs at least one tag."
            raise ValueError(msg)

        for ts in tag_strings:
            tag_object = self.RM.label_tag_map[self.language_code].get(ts)

            if tag_object is None:
                print(util.yellow("Unmatched tag string:"), f'"{ts}"')

            self.tags.append(tag_object)

        # ensure uniqueness
        self.tags = list(set(self.tags))

    def add_restrictions_for_tags(self, o_directive: ypo.Thing):

        for tag_object in self.tags:
            # note that tags are classes
            evaluated_restriction = self.RM.om.n.hasTag.some(tag_object)

            # applying the restricion
            o_directive.is_a.append(evaluated_restriction)
