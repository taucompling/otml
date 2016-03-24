from __future__ import absolute_import, division, print_function, unicode_literals

import os

from tests.otml_configuration_for_testing import configurations
from grammar.feature_bundle import FeatureBundle
from grammar.feature_table import FeatureTable
from tests.stochastic_testcase import StochasticTestCase
from tests.persistence_tools import get_feature_table_fixture

class TestFeature(StochasticTestCase):

    def setUp(self):
        self.correct_set_filename = get_feature_table_fixture("feature_table.json")
        self.feature_table = FeatureTable.load(self.correct_set_filename)

    #featureBundle tests:
    def test_feature_bundle(self):
        feature_bundle = FeatureBundle({'syll': '+', 'son': '+'}, self.feature_table)  # TODO  test same feature twice, illegal feature
        self.assertEqual(feature_bundle.feature_dict['syll'], '+')
        self.assertEqual(feature_bundle.feature_dict['son'], '+')

    def test_feature_bundle_augment(self):
        feature_bundle = FeatureBundle({'son': '+'}, self.feature_table)
        result1 = str(FeatureBundle({'son': '+', 'syll': '+'}, self.feature_table))
        result2 = str(FeatureBundle({'son': '+', 'syll': '-'}, self.feature_table))
        possible_results = [result1, result2]
        self.stochastic_object_method_testing(feature_bundle, "augment_feature_bundle", possible_results,
                                              num_of_tests=40, possible_result_threshold=5)

    def test_feature_bundle_generate_random(self):
        if configurations["INITIAL_NUMBER_OF_FEATURES"] is 1:
            feature_bundle_str1 = str(FeatureBundle({'son': '+'}, self.feature_table))
            feature_bundle_str2 = str(FeatureBundle({'son': '-'}, self.feature_table))
            feature_bundle_str3 = str(FeatureBundle({'syll': '+'}, self.feature_table))
            feature_bundle_str4 = str(FeatureBundle({'syll': '-'}, self.feature_table))
            possible_results = [feature_bundle_str1, feature_bundle_str2, feature_bundle_str3, feature_bundle_str4]
            self.stochastic_class_generate_random_testing(FeatureBundle, possible_results, num_of_tests=100,
                                                    possible_result_threshold=10, all_possible_result_flag=True)