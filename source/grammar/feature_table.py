#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

import codecs
import json
from random import choice
import logging
from copy import deepcopy
import os

from six import string_types, integer_types, StringIO, iterkeys

from unicode_mixin import UnicodeMixin
from otml_configuration_manager import OtmlConfigurationManager, OtmlConfigurationError


logger = logging.getLogger(__name__)
configurations = OtmlConfigurationManager.get_instance()
if configurations is None:
    raise OtmlConfigurationError("OtmlConfigurationManager was not initialized")

class FeatureParseError(Exception):
    pass


class FeatureTable(UnicodeMixin, object):
    def __init__(self, feature_table_dict_from_json):
        self.feature_table_dict = dict()
        self.feature_types_dict = dict()
        self.segments_list = list()
        feature_type_list = [dict(**feature) for feature in feature_table_dict_from_json['feature']]
        feature_types_label_in_order = [feature['label'] for feature in feature_table_dict_from_json['feature']]

        for feature_type_label in feature_types_label_in_order:
            if feature_types_label_in_order.count(feature_type_label) > 1:
                raise FeatureParseError('feature "{}" appears more then one time'.format(feature_type_label))

        self.feature_order_dict = dict()
        for i, feature in enumerate(feature_types_label_in_order):
            self.feature_order_dict[i] = feature

        for feature_type in feature_type_list:
            self.feature_types_dict[feature_type['label']] = feature_type['values']

        for symbol in feature_table_dict_from_json['feature_table'].keys():
            feature_values = feature_table_dict_from_json['feature_table'][symbol]
            if len(feature_values) != len(self.feature_types_dict):
                raise FeatureParseError("Mismatch in number of features for segment {0}".format(symbol))
            symbol_feature_dict = dict()
            for i, feature_value in enumerate(feature_values):
                feature_label = feature_types_label_in_order[i]
                if not feature_value in self.feature_types_dict[feature_label]:
                    raise FeatureParseError("Illegal feature was found for segment {0}".format(symbol))
                symbol_feature_dict[feature_label] = feature_value
            self.feature_table_dict[symbol] = symbol_feature_dict

        for symbol in self.get_alphabet():
            self.segments_list.append(Segment(symbol, self))


    @classmethod
    def loads(cls, feature_table_str):
        feature_table_dict = json.loads(feature_table_str)
        return cls(feature_table_dict)

    @classmethod
    def load(cls, feature_table_fn):
        file = codecs.open(feature_table_fn, "r")
        if os.path.splitext(feature_table_fn)[1] == ".json":
            feature_table_dict = json.load(file)
        else:
            feature_table_dict = FeatureTable.get_feature_table_dict_form_csv(file)
        file.close()
        return cls(feature_table_dict)

    @staticmethod
    def get_feature_table_dict_form_csv(file):
        feature_table_dict = dict()
        feature_table_dict['feature'] = list()
        feature_table_dict['feature_table'] = dict()
        lines = file.readlines()
        lines = [x.strip() for x in lines]
        feature_label_list = lines[0][1:].split(",")  #first line, ignore firt comma (,cons, labial..)
        feature_table_dict['feature'] = list()
        for label in feature_label_list:
            feature_table_dict['feature'].append({'label': label, 'values': ['-', '+']})

        for line in lines[1:]:
            values_list = line.split(',')
            feature_table_dict['feature_table'][values_list[0]] = values_list[1:]

        return feature_table_dict


    def get_number_of_features(self):
        return len(self.feature_types_dict)

    def get_features(self):
        return list(iterkeys(self.feature_types_dict))

    def get_random_value(self, feature):
        return choice(self.feature_types_dict[feature])

    def get_alphabet(self):
        return list(iterkeys(self.feature_table_dict))

    def get_segments(self):
        return deepcopy(self.segments_list)

    def get_random_segment(self):
        return choice(self.get_alphabet())

    def get_ordered_feature_vector(self, char):
        return [self[char][self.feature_order_dict[i]] for i in range(self.get_number_of_features())]

    def is_valid_feature(self, feature_label):
        return feature_label in self.feature_types_dict

    def is_valid_symbol(self, symbol):
        return symbol in self.feature_table_dict


    def __unicode__(self):
        values_str_io = StringIO()
        print("Feature Table with {0} features and {1} segments:".format(self.get_number_of_features(),
                                                                        len(self.get_alphabet())), end="\n",
                                                                        file=values_str_io)

        print("{:20s}".format("Segment/Feature"), end="", file=values_str_io)
        for i in list(range(len(self.feature_order_dict))):
            print("{:10s}".format(self.feature_order_dict[i]), end="", file=values_str_io)
        print("", file=values_str_io)  # new line
        for segment in sorted(iterkeys(self.feature_table_dict)):
            print("{:20s}".format(segment), end="", file=values_str_io)
            for i in list(range(len(self.feature_order_dict))):
                feature = self.feature_order_dict[i]
                print("{:10s}".format(self.feature_table_dict[segment][feature]), end="", file=values_str_io)
            print("", file=values_str_io)

        return values_str_io.getvalue()


    def __getitem__(self, item):
        if isinstance(item, string_types):
            return self.feature_table_dict[item]
        if isinstance(item, integer_types):    # TODO this should support an ordered access to the feature table.
                                                #  is this a good implementation?
            return self.feature_table_dict[self.feature_order_dict[item]]
        else:
            segment, feature = item
            return self.feature_table_dict[segment][feature]




class Segment(UnicodeMixin, object):
    def __init__(self, symbol, feature_table=None):
        self.symbol = symbol   # JOKER and NULL segments need feature_table=None
        if feature_table:
            self.feature_table = feature_table
            self.feature_dict = feature_table[symbol]

        self.hash = hash(self.symbol)

    def get_encoding_length(self):
        return len(self.feature_dict)

    def has_feature_bundle(self, feature_bundle):
        return all(item in self.feature_dict.items() for item in feature_bundle.get_feature_dict().items())

    def get_symbol(self):
        return self.symbol

    @staticmethod
    def intersect(x, y):
        """ Intersect two segments, a segment and a set, or two sets.

        :type x: Segment or set
        :type y: Segment or set
        """
        if isinstance(x, set):
            x, y = y, x  # if x is a set then maybe y is a segment, switch between them so that
                         # Segment.__and__ will take affect
        return x & y

    def __and__(self, other):
        """ Based on ```(17) symbol unification```(Riggle, 2004)

        :type other: Segment or set
        """
        if self == JOKER_SEGMENT:
            return other
        elif isinstance(other, set):
            if self.symbol in other:
                return self
        else:
            if self == other:
                return self
            elif other == JOKER_SEGMENT:
                return self
        return None

    def __eq__(self, other):
        if other is None:
            return False
        return self.symbol == other.symbol

    def __hash__(self):
        return self.hash

    def __unicode__(self):
        if hasattr(self, "feature_table"):
            values_str_io = StringIO()
            ordered_feature_vector = self.feature_table.get_ordered_feature_vector(self.symbol)

            for value in ordered_feature_vector:
                print(value, end=", ", file=values_str_io)
            return "Segment {0}[{1}]".format(self.symbol, values_str_io.getvalue()[:-2])
        else:
            return self.symbol


    def __getitem__(self, item):
        return self.feature_dict[item]

#----------------------
#Special segments - required for transducer construction
NULL_SEGMENT = Segment("-")
JOKER_SEGMENT = Segment("*")

#----------------------

class FeatureType(UnicodeMixin, object):
    def __init__(self, label, values):
        self.label = label
        self.values = values

    def get_random_value(self):
        return choice(self.values)

    def __unicode__(self):
        values_str_io = StringIO()
        for value in self.values:
            print(value, end=", ", file=values_str_io)
        return "FeatureType {0} with possible values: [{1}]".format(self.label, values_str_io.getvalue()[:-2])

    def __contains__(self, item):
        return item in self.values