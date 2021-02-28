import os
from typing import List, Tuple

import yaml
import yamlpyowl as ypo


from ipydex import IPS


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
            self.om = ypo.OntologyManager(onto_path)

        self.files = []
        self.raw_yaml_contents = []
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

    def _process_rule_document(self, raw_tuple: Tuple[dict, list]):

        header_dict, rule_list = raw_tuple
        assert header_dict["extends"] == self.om.iri
        sd_name = header_dict["iri-suffix"]
        labels = header_dict["labels"]
        source_uri = header_dict["source"]
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

            rule_name = f"_{sd_name}{i+1:03d}"

            doc_ref = self.om.n.X_DocumentReference_RC(name=f"{rule_name}_dref", hasSourceDocument=source_doc,
                                                       hasSection=inner_rule_dict["section"])
            rule = self.om.n.Directive(name=rule_name, X_hasDocumentReference_RC=[doc_ref])


    def _resolve_name(self, name):

        return self.om.name_mapping[name]


