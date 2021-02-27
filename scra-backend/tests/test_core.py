import os
import sys
import unittest
import yamlpyowl as ypo
import scra_core as scra

# noinspection PyUnresolvedReferences
from ipydex import IPS, activate_ips_on_exception

BASEPATH_PACKAGE = os.path.dirname(os.path.dirname(os.path.abspath(sys.modules.get(__name__).__file__)))
PATH_KNOWLEDGEBASE = os.path.join(os.path.dirname(BASEPATH_PACKAGE), "knowledge-base")


# noinspection PyPep8Naming
class TestCore(unittest.TestCase):
    def setUp(self):
        # prevent that the tests do influence each other -> create a new world each time
        self.world = ypo.owl2.World()
        path = os.path.join(PATH_KNOWLEDGEBASE, "general", "world.yml")
        self.onto = ypo.OntologyManager(path, self.world)

    def test_regional_structure(self):
        n = self.onto.n

        self.assertTrue(n.leipzig in n.saxony.hasPart)
        self.assertTrue("dresden" in self.onto.name_mapping)
        self.assertFalse(n.leipzig in n.bavaria.hasPart)

        self.onto.sync_reasoner(infer_property_values=True, infer_data_property_values=True)

        self.assertTrue(n.bamberg in n.germany.hasPart)
        self.assertEqual(n.LV_Sn_CoViD.appliesTo, [n.saxony])

        self.assertTrue(n.dir_rule2 in n.dresden.hasDirective)
        self.assertTrue(n.dir_rule3 in n.dresden.hasDirective)
        self.assertFalse(n.dir_rule2 in n.munich.hasDirective)

    def test_query_rules_for_region(self):
        n = self.onto.n
        self.onto.sync_reasoner(infer_property_values=True, infer_data_property_values=True)

        SM = scra.SemanticManager(self.onto)
        res = SM.get_directives_for_region("munich")
        self.assertEquals(res, {n.dir_rule1})

        res = SM.get_directives_for_region("dresden")
        self.assertEquals(res, {n.dir_rule1, n.dir_rule2, n.dir_rule3, n.dir_rule5})

        res = SM.get_directives_for_region("leipzig")
        self.assertEquals(res, {n.dir_rule1, n.dir_rule2, n.dir_rule5})

