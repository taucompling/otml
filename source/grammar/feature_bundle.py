#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from six import iterkeys
from random import choice

from unicode_mixin import UnicodeMixin
from grammar.grammar import GrammarParseError
from otml_configuration_manager import OtmlConfigurationManager, OtmlConfigurationError


logger = logging.getLogger(__name__)
configurations = OtmlConfigurationManager.get_instance()
if configurations is None:
    raise OtmlConfigurationError("OtmlConfigurationManager was not initialized")

class FeatureBundle(UnicodeMixin, object):
    __slots__ = ["feature_dict", "feature_table"]
    def __init__(self, feature_dict, feature_table):
        for feature in feature_dict.keys():
            if not feature_table.is_valid_feature(feature):
                raise GrammarParseError("Illegal feature: {0}".format(feature))

        self.feature_dict = feature_dict
        self.feature_table = feature_table

    def get_encoding_length(self):
        return 2 * len(self.feature_dict)

    def get_keys(self):
        return list(iterkeys(self.feature_dict))

    def get_feature_dict(self):
        return self.feature_dict

    def augment_feature_bundle(self):
        if len(self.feature_dict) < configurations["MAX_FEATURES_IN_BUNDLE"]:
            all_feature_labels = self.feature_table.get_features()
            feature_labels_in_feature_bundle = iterkeys(self.feature_dict)
            available_feature_labels = list(set(all_feature_labels) - set(feature_labels_in_feature_bundle))
            if available_feature_labels:
                feature_label = choice(available_feature_labels)
                self.feature_dict[feature_label] = self.feature_table.get_random_value(feature_label)
                return True
        return False

    @classmethod
    def generate_random(cls, feature_table):
        if configurations["INITIAL_NUMBER_OF_FEATURES"]> feature_table.get_number_of_features():
            raise OtmlConfigurationError("INITIAL_NUMBER_OF_FEATURES is bigger from number of available features")

        feature_dict = dict()
        available_feature_labels = feature_table.get_features()
        for i in range(configurations["INITIAL_NUMBER_OF_FEATURES"]):
            feature_label = choice(available_feature_labels)
            feature_dict[feature_label] = feature_table.get_random_value(feature_label)
            available_feature_labels.remove(feature_label)
        return FeatureBundle(feature_dict, feature_table)

    def __eq__(self, other):
        return self.feature_dict == other.feature_dict

    def __unicode__(self):
        return str(self.feature_dict)

    def __getitem__(self, item):
        return self.feature_dict[item]
