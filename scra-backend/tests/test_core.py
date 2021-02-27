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

    def test_regional_structure(self):
        path = os.path.join(PATH_KNOWLEDGEBASE, "general", "world.yml")
        onto = ypo.OntologyManager(path, self.world)
        n = onto.n

        self.assertTrue(n.leipzig in n.saxony.hasPart)
        self.assertTrue("dresden" in onto.name_mapping)
        self.assertFalse(n.leipzig in n.bavaria.hasPart)

        onto.sync_reasoner(infer_property_values=True, infer_data_property_values=True)

        self.assertTrue(n.bamberg in n.germany.hasPart)
