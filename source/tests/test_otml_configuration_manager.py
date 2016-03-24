#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals
import unittest
import os
import codecs
from otml_configuration_manager import OtmlConfigurationManager,OtmlConfigurationError

class TestOtmlConfigurationManager(unittest.TestCase):

    def setUp(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))

        json_str = codecs.open(os.path.join(dirname, "fixtures/configuration/otml_configuration.json"),'r').read()
        self.otml_configuration_manager = OtmlConfigurationManager(json_str)

    def test_configurations(self):
        self.assertEqual(self.otml_configuration_manager["MIN_NUMBER_OF_CONSTRAINTS_IN_CONSTRAINT_SET"], 1)

    def test_mappings(self):
        self.assertEqual(self.otml_configuration_manager["MAX_FEATURES_IN_BUNDLE"], float("inf"))
        self.assertEqual(self.otml_configuration_manager["THRESHOLD"], 10**-2)

    def test_derived_configurations(self):
        self.assertEqual(self.otml_configuration_manager["LEXICON_SELECTION_WEIGHT"], 2)
        self.assertEqual(self.otml_configuration_manager["PHONOTACTIC_WEIGHT_FOR_INSERT"], 1)


    def test_update(self):
        self.otml_configuration_manager["MIN_NUMBER_OF_CONSTRAINTS_IN_CONSTRAINT_SET"] = 2
        self.assertEqual(self.otml_configuration_manager["MIN_NUMBER_OF_CONSTRAINTS_IN_CONSTRAINT_SET"], 2)
        self.otml_configuration_manager["LEXICON_MUTATION_WEIGHTS"] = {"insert_segment": 1,
                                                                       "delete_segment": 0,
                                                                       "change_segment": 0}
        self.assertEqual(self.otml_configuration_manager["LEXICON_SELECTION_WEIGHT"], 1)
        # test reset_to_original_configurations()
        self.otml_configuration_manager.reset_to_original_configurations()
        self.assertEqual(self.otml_configuration_manager["MIN_NUMBER_OF_CONSTRAINTS_IN_CONSTRAINT_SET"], 1)

    def test_validation(self):
        with self.assertRaises(OtmlConfigurationError):
            self.otml_configuration_manager["CONSTRAINT_INSERTION_WEIGHTS"] = {"Dep": 0,
                                                                               "Max": 0,
                                                                               "Ident": 0,
                                                                               "Phonotactic": 0}

    def tearDown(self):
        self.otml_configuration_manager.reset_to_original_configurations()
