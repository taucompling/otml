#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

from configuration_manager import ConfigurationManager
from copy import deepcopy

from six import StringIO

from unicode_mixin import UnicodeMixin

class OtmlConfigurationError(Exception):
    pass

class OtmlConfigurationManager(ConfigurationManager, UnicodeMixin):
    def __init__(self, json_str):
        ConfigurationManager.__init__(self, json_str, mapping_function=OtmlConfigurationManager.mapping_function)
        self.initial_configurations_dict = deepcopy(self.configurations)
        self.initial_derived_configurations_dict = deepcopy(self.derived_configurations)

    def reset_to_original_configurations(self):
        self.configurations = deepcopy(self.initial_configurations_dict)
        self.derived_configurations = deepcopy(self.initial_derived_configurations_dict)


    @staticmethod
    def mapping_function(string_value):
        if string_value == "True":
            return True
        elif string_value == "False":
            return False
        elif string_value == 'INF':
            return float('inf')
        elif "**" in string_value:  #convert "x**y" literal to x**y
            power_symbol_index = string_value.index("**")
            power_symbol_length = len("**")
            return int(string_value[:power_symbol_index])**int(string_value[power_symbol_index+power_symbol_length:])
        else:
            return string_value

    def validate_configurations(self):
        dictionary_configuration_names = ["LEXICON_MUTATION_WEIGHTS", "CONSTRAINT_SET_MUTATION_WEIGHTS",
                                          "CONSTRAINT_INSERTION_WEIGHTS"]
        for dictionary_configuration_name in dictionary_configuration_names:
            if type(self.configurations[dictionary_configuration_name]) is not dict:
                raise OtmlConfigurationError("{} should be a dictionary".format(dictionary_configuration_name))

        for dictionary_configuration_name in dictionary_configuration_names:
            _check_weight_values_validity(self.configurations[dictionary_configuration_name])

        _check_weights_total_is_not_zero(self.configurations["LEXICON_MUTATION_WEIGHTS"],
                                         self.configurations["CONSTRAINT_SET_MUTATION_WEIGHTS"])
        _check_weights_total_is_not_zero(self.configurations["CONSTRAINT_INSERTION_WEIGHTS"])

        if self.configurations["CONSTRAINT_SET_MUTATION_WEIGHTS"]["augment_feature_bundle"] is 1:
            raise NotImplementedError

        if self.configurations["LEXICON_MUTATION_WEIGHTS"]["change_segment"] is 1:
            raise NotImplementedError

        if self.configurations["ALLOW_CANDIDATES_WITH_CHANGED_SEGMENTS"] is True:
            raise NotImplementedError

        if self.configurations["MIN_FEATURE_BUNDLES_IN_PHONOTACTIC_CONSTRAINT"] > self.configurations["INITIAL_NUMBER_OF_FEATURES"]:
            raise OtmlConfigurationError("MIN_FEATURE_BUNDLES_IN_PHONOTACTIC_CONSTRAINT is bigger then INITIAL_NUMBER_OF_FEATURES")

        #TODO link between ["LEXICON_MUTATION_WEIGHTS"]["change_segment"] and ["ALLOW_CANDIDATES_WITH_CHANGED_SEGMENTS"]


    def derive_configurations(self):
        lexicon_mutation_weights = self.configurations["LEXICON_MUTATION_WEIGHTS"]
        constraint_set_mutation_weights = self.configurations["CONSTRAINT_SET_MUTATION_WEIGHTS"]
        constraint_insertion_weights = self.configurations["CONSTRAINT_INSERTION_WEIGHTS"]

        self.derived_configurations["LEXICON_SELECTION_WEIGHT"] = sum(lexicon_mutation_weights.values())
        self.derived_configurations["CONSTRAINT_SET_SELECTION_WEIGHT"] = sum(constraint_set_mutation_weights.values())

        self.derived_configurations["INSERT_SEGMENT_WEIGHT"] = lexicon_mutation_weights['insert_segment']
        self.derived_configurations["DELETE_SEGMENT_WEIGHT"] = lexicon_mutation_weights['delete_segment']
        self.derived_configurations["CHANGE_SEGMENT_WEIGHT"] = lexicon_mutation_weights['change_segment']

        self.derived_configurations["INSERT_CONSTRAINT_WEIGHT"] = constraint_set_mutation_weights['insert_constraint']
        self.derived_configurations["REMOVE_CONSTRAINT_WEIGHT"] = constraint_set_mutation_weights['remove_constraint']
        self.derived_configurations["DEMOTE_CONSTRAINT_WEIGHT"] = constraint_set_mutation_weights['demote_constraint']
        self.derived_configurations["INSERT_FEATURE_BUNDLE_PHONOTACTIC_CONSTRAINT_WEIGHT"] = constraint_set_mutation_weights['insert_feature_bundle_phonotactic_constraint']
        self.derived_configurations["REMOVE_FEATURE_BUNDLE_PHONOTACTIC_CONSTRAINT_WEIGHT"] = constraint_set_mutation_weights['remove_feature_bundle_phonotactic_constraint']
        self.derived_configurations["AUGMENT_FEATURE_BUNDLE_WEIGHT"] = constraint_set_mutation_weights['augment_feature_bundle']

        self.derived_configurations["DEP_WEIGHT_FOR_INSERT"] = constraint_insertion_weights['Dep']
        self.derived_configurations["MAX_WEIGHT_FOR_INSERT"] = constraint_insertion_weights['Max']
        self.derived_configurations["IDENT_WEIGHT_FOR_INSERT"] = constraint_insertion_weights['Ident']
        self.derived_configurations["PHONOTACTIC_WEIGHT_FOR_INSERT"] = constraint_insertion_weights['Phonotactic']

    def __unicode__(self):
        values_str_io = StringIO()
        print("Otml configuration manager with:", end="\n", file=values_str_io)
        for (key, value) in sorted(self.configurations.items()):
            value_string = ""
            if type(value) is dict:
                for (secondary_key, secondary_value) in self.configurations[key].items():
                    value_string += (len(key)+2) * " " + "{}: {}\n".format(secondary_key, secondary_value) #manual justification
                value_string = value_string.strip()
            else:
                value_string = str(value)
            print("{}: {}".format(key, value_string), end="\n", file=values_str_io)

        return values_str_io.getvalue().strip()


def _check_weight_values_validity(weight_dict):
    for weight in weight_dict.values():
        if not isinstance(weight, int):
            raise OtmlConfigurationError("weight {} is not an int".format(weight))
        elif weight < 0:
            raise OtmlConfigurationError("weight {} is negative".format(weight))


def _check_weights_total_is_not_zero(*weight_dicts):
    total = 0
    for weight_dict in weight_dicts:
        total = total + sum(weight_dict.values())
    if total == 0:
        raise OtmlConfigurationError("sum of weights is zero")

#
