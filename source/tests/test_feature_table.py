#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals
import codecs


from tests.otml_configuration_for_testing import configurations
from grammar.feature_table import FeatureTable, FeatureParseError, Segment, FeatureType
from grammar.feature_bundle import FeatureBundle
from tests.stochastic_testcase import StochasticTestCase
from tests.persistence_tools import get_feature_table_fixture, get_feature_table_by_fixture


class TestFeatureTable(StochasticTestCase):

    def setUp(self):
        self.correct_set_filename = get_feature_table_fixture("feature_table.json")
        self.illegal_feature_value_filename = get_feature_table_fixture("illegal_feature_table_illegal_"
                                                                    "feature_value.json")
        self.mismatch_in_number_of_features_filename = get_feature_table_fixture("illegal_feature_table_"
                                                                             "mismatch_in_number_of_features.json")
        self.feature_table = FeatureTable.load(self.correct_set_filename)

    def test_get_item_with_feature_label(self):
        self.assertEqual(self.feature_table['a', "syll"], '+')
        self.assertEqual(self.feature_table['b', "syll"], '-')
        self.assertEqual(self.feature_table['c', "syll"], '+')
        self.assertEqual(self.feature_table['d', "syll"], '-')
        self.assertEqual(self.feature_table['a', "son"], '-')
        self.assertEqual(self.feature_table['b', "son"], '-')
        self.assertEqual(self.feature_table['c', "son"], '+')
        self.assertEqual(self.feature_table['d', "son"], '+')

    def test_get_item_invalid(self):
        with self.assertRaises(Exception):
            res = self.feature_table['a', 2]

        with self.assertRaises(Exception):
            res = self.feature_table['y', 5]

        with self.assertRaises(Exception):
            res = self.feature_table[5]


    def test_illegal_set_illegal_feature_value(self):
        with self.assertRaises(FeatureParseError):
            ft = FeatureTable.load(self.illegal_feature_value_filename)

    def test_illegal_set_illegal_mismatch_in_number_of_features(self):
        with self.assertRaises(FeatureParseError):
            ft = FeatureTable.load(self.mismatch_in_number_of_features_filename)

    def test_from_csv(self):
        feature_table = self.correct_set_filename = get_feature_table_by_fixture("a_b_and_son_feature_table.csv")
        self.assertEqual(feature_table['a', "cons"], '-')


    #segment tests:
    def test_segment(self):
        segment = Segment('a', self.feature_table)
        self.assertEqual(str(segment), "Segment a[+, -]")
        self.assertEqual(segment['son'], u'-')

    def test_segment_encoding_Length(self):
        segment = Segment('a', self.feature_table)
        self.assertEqual(segment.get_encoding_length(), 2)

    def test_segment_has_feature_bundle(self):
        segment = Segment('a', self.feature_table)
        self.assertTrue(segment.has_feature_bundle(FeatureBundle({'syll': '+'}, self.feature_table)))
        self.assertTrue(segment.has_feature_bundle(FeatureBundle({'son': '-'}, self.feature_table)))
        self.assertTrue(segment.has_feature_bundle(FeatureBundle({'syll': '+', 'son': '-'}, self.feature_table)))
        self.assertFalse(segment.has_feature_bundle(FeatureBundle({'son': '+'}, self.feature_table)))
        self.assertFalse(segment.has_feature_bundle(FeatureBundle({'syll': '+', 'son': '+'}, self.feature_table)))

    #featureType tests:
    def test_feature_type(self):
        feature = FeatureType('syll', ['+', '-'])
        self.assertEqual(str(feature), "FeatureType syll with possible values: [+, -]")
        self.assertEqual('+' in feature, True)
        self.assertEqual('?' in feature, False)

