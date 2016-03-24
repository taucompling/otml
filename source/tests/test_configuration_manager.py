#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals
import unittest
import os
import codecs
from configuration_manager import ConfigurationManager,ConfigurationManagerError

class TestConfigurationManager(unittest.TestCase):

    def setUp(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        json_str = codecs.open(os.path.join(dirname, "fixtures/configuration/configuration_example.json"), 'r').read()
        self.configuration_manager = ConfigurationManager(json_str)
        self.update_json_str = codecs.open(os.path.join(dirname, "fixtures/configuration/configuration_update.json"), 'r').read()
        self.illegal_update_json_str = codecs.open(os.path.join(dirname, "fixtures/configuration/illegal_configuration_update.json"), 'r').read()

    def test_singeltoness(self):
        self.assertEqual(id(self.configuration_manager), id(ConfigurationManager()))


    def test_configurations(self):
        self.assertEqual(self.configuration_manager["PROPERTY1"], "spam")


    def test_update_configuration(self):
        self.configuration_manager.update_configurations(self.update_json_str)
        self.assertEqual(self.configuration_manager["PROPERTY1"], "egg")

    def test_update_configuration_illegal(self):
        with self.assertRaises(ConfigurationManagerError):
            self.configuration_manager.update_configurations(self.illegal_update_json_str)

