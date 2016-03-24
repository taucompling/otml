#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from random import randint, choice
import logging

from six import StringIO, with_metaclass


from unicode_mixin import UnicodeMixin
from grammar.feature_bundle import FeatureBundle
from grammar.grammar import GrammarParseError
from transducer import CostVector, Arc, State, Transducer
from grammar.feature_table import JOKER_SEGMENT, NULL_SEGMENT
from itertools import permutations
from otml_configuration_manager import OtmlConfigurationManager, OtmlConfigurationError


logger = logging.getLogger(__name__)
configurations = OtmlConfigurationManager.get_instance()
if configurations is None:
    raise OtmlConfigurationError("OtmlConfigurationManager was not initialized")

# Global variable that holds all the names of constraint classes that inherit from ConstraintMetaClass
_all_constraints = list()

constraint_transducers = dict()

def get_number_of_constraints():
    return len(_all_constraints)


class ConstraintMetaClass(type):
    def __new__(mcs, name, bases, attributes):
        if name != 'NewBase' and name != 'Constraint':  # NewBase is a the name of the base class used
            _all_constraints.append(name)                 # in six.with_metaclass
        return type.__new__(mcs, name, bases, attributes)


class Constraint(with_metaclass(ConstraintMetaClass, UnicodeMixin)):

    def __init__(self, bundles_list, allow_multiple_bundles, feature_table):
        """ bundle_list can contain either raw dictionaries or full blown FeatureBundle """
        self.feature_table = feature_table
        if len(bundles_list) > 1 and not allow_multiple_bundles:
            raise GrammarParseError("More bundles than allowed")

        self.feature_bundles = list()  # contain FeatureBundles

        for bundle in bundles_list:
            if type(bundle) is dict:
                self.feature_bundles.append(FeatureBundle(bundle, feature_table))
            elif type(bundle) is FeatureBundle:
                self.feature_bundles.append(bundle)
            else:
                raise GrammarParseError("Not a dict or FeatureBundle")


    def augment_feature_bundle(self):
        success = choice(self.feature_bundles).augment_feature_bundle()
        if success:
            return True
        return False

    def get_encoding_length(self):
        return 1 + sum([featureBundle.get_encoding_length() for featureBundle in self.feature_bundles]) + 1


    @classmethod
    def get_constraint_class_by_name(cls, class_name):
        this_module = sys.modules[__name__]
        for constraint_class_name in _all_constraints:
            if getattr(this_module, constraint_class_name).get_constraint_name() == class_name:
                return getattr(this_module, constraint_class_name)

    def _base_faithfulness_transducer(self):
        segments = self.feature_table.get_segments()
        transducer = Transducer(segments, name=str(self))
        state = State('q0')
        transducer.set_as_single_state(state)
        return transducer, segments, state


    @classmethod
    def generate_random(cls, feature_table):
        random_feature_bundle = FeatureBundle.generate_random(feature_table)
        constraint_class = Constraint.get_constraint_class_by_name(cls.get_constraint_name())
        return constraint_class([random_feature_bundle], feature_table)

    def get_transducer(self):
        constraint_key = str(self)
        if constraint_key in constraint_transducers:
            return constraint_transducers[constraint_key]
        else:
            transducer = self._make_transducer()
            constraint_transducers[constraint_key] = transducer
            return transducer

    @staticmethod
    def clear_caching():
        global constraint_transducers
        constraint_transducers = dict()

    def __eq__(self, other):
        if type(self) == type(other):
            return self.feature_bundles == other.feature_bundles
        return False

    def __unicode__(self):
        str_io = StringIO()
        print("{0}[".format(self.get_constraint_name()), file=str_io, end="")
        for featureBundle in self.feature_bundles:
            if len(self.feature_bundles) > 1:
                print("[", file=str_io, end="")

            for i_feature, feature in enumerate(sorted(featureBundle.get_keys())):  # sorted to avoid differences in
                if i_feature != 0:                                               # implementations (esp between Py2 and
                    print(", ", file=str_io, end="")                             # Py3) - tests
                print("{0}{1}".format(featureBundle[feature], feature), file=str_io, end="")

            if len(self.feature_bundles) > 1:
                print("]", file=str_io, end="")
        print("]", file=str_io, end="")
        return str_io.getvalue()

    def __hash__(self):
        return hash(str(self))


class MaxConstraint(Constraint):
    def __init__(self, bundles_list, feature_table):
        super(MaxConstraint, self).__init__(bundles_list, False, feature_table)
        self.feature_bundle = self.feature_bundles[0]

    def _make_transducer(self):
        transducer, segments, state = super(MaxConstraint, self)._base_faithfulness_transducer()
        for segment in segments:
            transducer.add_arc(Arc(state, segment, segment, CostVector.get_vector(1, 0), state))
            transducer.add_arc(Arc(state, NULL_SEGMENT, segment, CostVector.get_vector(1, 0), state))
            if segment.has_feature_bundle(self.feature_bundle):
                transducer.add_arc(Arc(state, segment, NULL_SEGMENT, CostVector.get_vector(1, 1), state))
            else:
                transducer.add_arc(Arc(state, segment, NULL_SEGMENT, CostVector.get_vector(1, 0), state))

        if configurations["ALLOW_CANDIDATES_WITH_CHANGED_SEGMENTS"]:
            for first_segment, second_segment in permutations(segments, 2):
                transducer.add_arc(Arc(state, first_segment, second_segment, CostVector.get_vector(1, 0), state))

        return transducer

    @classmethod
    def get_constraint_name(cls):
        return "Max"


class DepConstraint(Constraint):
    def __init__(self, bundles_list, feature_table):
        super(DepConstraint, self).__init__(bundles_list, False, feature_table)
        self.feature_bundle = self.feature_bundles[0]

    def _make_transducer(self):
        transducer, segments, state = super(DepConstraint, self)._base_faithfulness_transducer()
        for segment in segments:
            transducer.add_arc(Arc(state, segment, segment, CostVector.get_vector(1, 0), state))
            transducer.add_arc(Arc(state, segment, NULL_SEGMENT, CostVector.get_vector(1, 0), state))
            if segment.has_feature_bundle(self.feature_bundle):
                transducer.add_arc(Arc(state, NULL_SEGMENT, segment, CostVector.get_vector(1, 1), state))
            else:
                transducer.add_arc(Arc(state, NULL_SEGMENT, segment, CostVector.get_vector(1, 0), state))

        if configurations["ALLOW_CANDIDATES_WITH_CHANGED_SEGMENTS"]:
            for first_segment, second_segment in permutations(segments, 2):
                transducer.add_arc(Arc(state, first_segment, second_segment, CostVector.get_vector(1, 0), state))

        return transducer

    @classmethod
    def get_constraint_name(cls):
        return "Dep"


class IdentConstraint(Constraint):
    def __init__(self, bundles_list, feature_table):
        super(IdentConstraint, self).__init__(bundles_list, False, feature_table)
        self.feature_bundle = self.feature_bundles[0]

    def _make_transducer(self):
        transducer, segments, state = super(IdentConstraint, self)._base_faithfulness_transducer()
        for segment in segments:
            transducer.add_arc(Arc(state, segment, segment, CostVector.get_vector(1, 0), state))
            transducer.add_arc(Arc(state, segment, NULL_SEGMENT, CostVector.get_vector(1, 0), state))
            transducer.add_arc(Arc(state, NULL_SEGMENT, segment, CostVector.get_vector(1, 0), state))
            input_segment = segment
            if input_segment.has_feature_bundle(self.feature_bundle):
                for output_segment in segments:
                    if output_segment.has_feature_bundle(self.feature_bundle):
                        transducer.add_arc(Arc(state, input_segment, output_segment, CostVector.get_vector(1, 0), state))
                    else:
                        transducer.add_arc(Arc(state, input_segment, output_segment, CostVector.get_vector(1, 1), state))
            else:
                for output_segment in segments:
                    transducer.add_arc(Arc(state, input_segment, output_segment, CostVector.get_vector(1, 0), state))
        return transducer

    @classmethod
    def get_constraint_name(cls):
        return "Ident"

class FaithConstraint(Constraint):
    """
    This constraint has no feature bundle list
    """
    def __init__(self, bundles_list, feature_table):
        super(FaithConstraint, self).__init__([], False, feature_table)

    def _make_transducer(self):
        transducer, segments, state = super(FaithConstraint, self)._base_faithfulness_transducer()
        for segment in segments:
            transducer.add_arc(Arc(state, NULL_SEGMENT, segment, CostVector.get_vector(1, 1), state))
            transducer.add_arc(Arc(state, segment, NULL_SEGMENT, CostVector.get_vector(1, 1), state))
            transducer.add_arc(Arc(state, segment, segment, CostVector.get_vector(1, 0), state))

        if configurations["ALLOW_CANDIDATES_WITH_CHANGED_SEGMENTS"]:
            for first_segment, second_segment in permutations(segments, 2):
                transducer.add_arc(Arc(state, first_segment, second_segment, CostVector.get_vector(1, 1), state))

        return transducer


    @classmethod
    def get_constraint_name(cls):
        return "Faith"

class PhonotacticConstraint(Constraint):
    def __init__(self, bundles_list, feature_table):
        super(PhonotacticConstraint, self).__init__(bundles_list, True, feature_table)

    def insert_feature_bundle(self):
        if len(self.feature_bundles) < configurations["MAX_FEATURE_BUNDLES_IN_PHONOTACTIC_CONSTRAINT"]:
            new_feature_bundle = FeatureBundle.generate_random(self.feature_table)
            if configurations["RANDOM_POSITION_FOR_FEATURE_BUNDLE_INSERTION_IN_PHONOTACTIC"]:
                self.feature_bundles.insert(randint(0, len(self.feature_bundles)), new_feature_bundle)
            else:
                self.feature_bundles.append(new_feature_bundle)
            return True
        else:
            return False

    def remove_feature_bundle(self):
        if len(self.feature_bundles) > configurations["MIN_FEATURE_BUNDLES_IN_PHONOTACTIC_CONSTRAINT"]:
            if configurations["RANDOM_POSITION_FOR_FEATURE_BUNDLE_REMOVAL_IN_PHONOTACTIC"]:

                self.feature_bundles.pop(randint(0, len(self.feature_bundles)-1))
            else:
                self.feature_bundles.pop()
            return True
        else:
            return False

    def _make_transducer(self):

        def compute_num_of_max_satisfied_bundle(segment):
            i = 0
            while i < n and symbol_bundle_characteristic_matrix[segment][i]:
                i += 1
            return i

        def compute_highest_num_of_satisfied_bundle(segment, j):
            for k in range(j + 1, 0,-1):
                if symbol_bundle_characteristic_matrix[segment][k-1]:
                    return k
            else:
                return 0

        n = len(self.feature_bundles) - 1
        segments = self.feature_table.get_segments()
        transducer = Transducer(segments, name=str(self))

        symbol_bundle_characteristic_matrix = {segment: [segment.has_feature_bundle(self.feature_bundles[i])
                                                         for i in range(n+1)]
                                               for segment in segments}


        states = {i: {j: 0 for j in range(i)} for i in range(n+1)}

        initial_state = State('q0|0')    # here we use a tuple as label. it will change at the end of this function
        states[0][0] = initial_state

        transducer.set_as_single_state(initial_state)


        if not n:
            for segment in segments:
                transducer.add_arc(Arc(states[0][0], JOKER_SEGMENT, segment, CostVector([int(symbol_bundle_characteristic_matrix[segment][0])]), states[0][0]))
            transducer.add_arc(Arc(states[0][0], JOKER_SEGMENT, NULL_SEGMENT, CostVector([0]), states[0][0]))

        else:
            for i in range(0, n+1):
                for j in range(i):
                    state = State('q{0}|{1}'.format(i,j))
                    states[i][j] = state
                    transducer.add_state(state)
            max_num_of_satisfied_bundle_by_segment = {segment: compute_num_of_max_satisfied_bundle(segment)
                                                      for segment in segments}
            for segment in segments:
                transducer.add_arc(Arc(states[0][0], JOKER_SEGMENT, segment, CostVector([0]),
                                       states[symbol_bundle_characteristic_matrix[segment][0]][0]))
            for i in range(n+1):
                for j in range(i):
                    state = states[i][j]
                    transducer.add_final_state(state)
                    if i != n:
                        for segment in segments:
                            if symbol_bundle_characteristic_matrix[segment][i]:
                                new_state_level = i+1
                                new_state_mem = min([j+1, max_num_of_satisfied_bundle_by_segment[segment]])
                            else:
                                new_state_level = compute_highest_num_of_satisfied_bundle(segment, j)
                                new_state_mem = min([max_num_of_satisfied_bundle_by_segment[segment],
                                                     abs(new_state_level - 1)])
                            new_terminus = states[new_state_level][new_state_mem]
                            transducer.add_arc(Arc(state, JOKER_SEGMENT, segment, CostVector([0]), new_terminus))
                    else:  # i = n
                        for segment in segments:
                            new_state_level = compute_highest_num_of_satisfied_bundle(segment, j)
                            new_state_mem = min([max_num_of_satisfied_bundle_by_segment[segment],
                                                 abs(new_state_level - 1)])
                            new_terminus = states[new_state_level][new_state_mem]
                            transducer.add_arc(Arc(state, JOKER_SEGMENT, segment,
                                                   CostVector([int(symbol_bundle_characteristic_matrix[segment][i])]), new_terminus))

        transducer.clear_dead_states()
        for state in transducer.states:
            transducer.add_arc(Arc( state, JOKER_SEGMENT, NULL_SEGMENT, CostVector([0]), state))

        return transducer

    @classmethod
    def get_constraint_name(cls):
        return "Phonotactic"

    def get_encoding_length(self):
        return 1 + sum([featureBundle.get_encoding_length() for featureBundle in self.feature_bundles]) \
                 + len(self.feature_bundles) + 1

    @classmethod
    def generate_random(cls, feature_table):
        bundles = list()
        for i in range(configurations["INITIAL_NUMBER_OF_BUNDLES_IN_PHONOTACTIC_CONSTRAINT"]):
            bundles.append(FeatureBundle.generate_random(feature_table))
        return PhonotacticConstraint(bundles, feature_table)



class HeadDepConstraint(Constraint):
    def __init__(self, bundles_list, feature_table):
        super(HeadDepConstraint, self).__init__(bundles_list, True, feature_table)

    def _make_transducer(self):
        segments = self.feature_table.get_segments()
        transducer = Transducer(segments, name=str(self))

        state1 = State('Dep1')
        state2 = State('Dep2')
        transducer.add_state(state1)
        transducer.add_state(state2)
        transducer.initial_state = state1
        transducer.add_final_state(state1)
        transducer.add_final_state(state2)
        for segment in segments:
            transducer.add_arc(Arc(state1, segment, NULL_SEGMENT, CostVector([0]), state1))
            transducer.add_arc(Arc(state2, segment, NULL_SEGMENT, CostVector([0]), state2))


            segment_symbol = segment.get_symbol()
            if segment_symbol in yimas_cons:  # segment is consonant
                transducer.add_arc(Arc(state1, NULL_SEGMENT, segment, CostVector([0]), state1))
                transducer.add_arc(Arc(state1, segment, segment, CostVector([0]), state1))
                transducer.add_arc(Arc(state2, segment, segment, CostVector([0]), state1))
                transducer.add_arc(Arc(state2, NULL_SEGMENT, segment, CostVector([0]), state1))
            elif segment_symbol in yimas_vowels:   # segment is vowel
                transducer.add_arc(Arc(state1, NULL_SEGMENT, segment, CostVector([0]), state1))
                transducer.add_arc(Arc(state1, segment, segment, CostVector([0]), state1))
                transducer.add_arc(Arc(state2, segment, segment, CostVector([0]), state1))
                transducer.add_arc(Arc(state2, NULL_SEGMENT, segment, CostVector([1]), state1))
            elif segment_symbol == "'":  # segment is stress
                transducer.add_arc(Arc(state1, NULL_SEGMENT, segment, CostVector([0]), state2))
                transducer.add_arc(Arc(state1, segment, segment, CostVector([0]), state2))
                transducer.add_arc(Arc(state2, segment, segment, CostVector([0]), state2))
                transducer.add_arc(Arc(state2, NULL_SEGMENT, segment, CostVector([0]), state2))
            else:
                raise ConstraintError("{} not supported in this constraint".format(segment_symbol))


        return transducer

    @classmethod
    def get_constraint_name(cls):
        return "HeadDep"


class MainLeftConstraint(Constraint):
    def __init__(self, bundles_list, feature_table):
        super(MainLeftConstraint, self).__init__(bundles_list, True, feature_table)

    def _make_transducer(self):
        segments = self.feature_table.get_segments()
        transducer = Transducer(segments, name=str(self))

        state1 = State('1')
        state2 = State('2')
        state3 = State('3')

        transducer.add_state(state1)
        transducer.add_state(state2)
        transducer.add_state(state3)

        transducer.add_final_state(state1)
        transducer.add_final_state(state2)
        transducer.add_final_state(state3)

        transducer.initial_state = state1

        for segment in segments:
            segment_symbol = segment.get_symbol()
            if segment_symbol in yimas_vowels:   # segment is vowel
                transducer.add_arc(Arc(state1, JOKER_SEGMENT, segment, CostVector([1]), state3))
                transducer.add_arc(Arc(state2, JOKER_SEGMENT, segment, CostVector([0]), state3))
                transducer.add_arc(Arc(state3, JOKER_SEGMENT, segment, CostVector([0]), state3))
            elif segment_symbol in yimas_cons:  # segment is consonant
                transducer.add_arc(Arc(state1, JOKER_SEGMENT, segment, CostVector([0]), state1))
                transducer.add_arc(Arc(state2, JOKER_SEGMENT, segment, CostVector([0]), state1))
                transducer.add_arc(Arc(state3, JOKER_SEGMENT, segment, CostVector([0]), state3))
            elif segment_symbol == "'":  # segment is stress
                transducer.add_arc(Arc(state1, JOKER_SEGMENT, segment, CostVector([0]), state2))
                transducer.add_arc(Arc(state2, JOKER_SEGMENT, segment, CostVector([0]), state2))
                transducer.add_arc(Arc(state3, JOKER_SEGMENT, segment, CostVector([0]), state3))
            else:
                raise ConstraintError("{} not supported in this constraint".format(segment_symbol))

        for state in transducer.states:
            transducer.add_arc(Arc(state, JOKER_SEGMENT, NULL_SEGMENT, CostVector([0]), state))
        return transducer

    @classmethod
    def get_constraint_name(cls):
        return "MainLeft"


class PrecedeConstraint(Constraint):
    def __init__(self, bundles_list, feature_table):
        super(PrecedeConstraint, self).__init__(bundles_list, True, feature_table)

    def _make_transducer(self):
        segments = self.feature_table.get_segments()
        transducer = Transducer(segments, name=str(self))

        state1 = State('Precede1')
        state2 = State('Precede2')   # After seeing +stress (now it is okay to see +vowel)
        transducer.add_state(state1)
        transducer.add_state(state2)
        transducer.initial_state = state1
        transducer.add_final_state(state1)
        transducer.add_final_state(state2)

        for segment in segments:
            segment_symbol = segment.get_symbol()
            if segment_symbol in yimas_vowels:   # segment is vowel
                transducer.add_arc(Arc(state1, JOKER_SEGMENT, segment, CostVector([1]), state1))
                transducer.add_arc(Arc(state2, JOKER_SEGMENT, segment, CostVector([0]), state2))
            elif segment_symbol == "'":  # segment is stress
                transducer.add_arc(Arc(state1, JOKER_SEGMENT, segment, CostVector([0]), state2))
                transducer.add_arc(Arc(state2, JOKER_SEGMENT, segment, CostVector([0]), state2))
            elif segment_symbol in yimas_cons:  # segment is consonant
                transducer.add_arc(Arc(state1, JOKER_SEGMENT, segment, CostVector([0]), state1))
                transducer.add_arc(Arc(state2, JOKER_SEGMENT, segment, CostVector([0]), state2))
            else:
                raise ConstraintError("{} not supported in this constraint".format(segment_symbol))
        for state in transducer.states:
            transducer.add_arc(Arc(state, JOKER_SEGMENT, NULL_SEGMENT, CostVector([0]), state))

        return transducer

    @classmethod
    def get_constraint_name(cls):
        return "Precede"


class ContiguityConstraint(Constraint):
    def __init__(self, bundles_list, feature_table):
        super(ContiguityConstraint, self).__init__(bundles_list, True, feature_table)

    def _make_transducer(self):
        segments = self.feature_table.get_segments()
        transducer = Transducer(segments, name=str(self))

        state1 = State('Contiguity1')
        state2 = State('Contiguity2')
        transducer.add_state(state1)
        transducer.add_state(state2)
        transducer.initial_state = state1
        transducer.add_final_state(state1)
        transducer.add_final_state(state2)

        for segment in segments:
            transducer.add_arc(Arc(state1, NULL_SEGMENT, segment, CostVector([0]), state1))
            transducer.add_arc(Arc(state1, segment, NULL_SEGMENT, CostVector([0]), state1))
            transducer.add_arc(Arc(state2, NULL_SEGMENT, segment, CostVector([1]), state1))
            transducer.add_arc(Arc(state2, segment, NULL_SEGMENT, CostVector([1]), state1))
            segment_symbol = segment.get_symbol()
            if segment_symbol in yimas_vowels:   # segment is vowel
                transducer.add_arc(Arc(state1, segment, segment, CostVector([0]), state1))
                transducer.add_arc(Arc(state2, segment, segment, CostVector([0]), state1))
            elif segment_symbol == "'":  # segment is stress
                transducer.add_arc(Arc(state1, segment, segment, CostVector([0]), state2))
                transducer.add_arc(Arc(state2, segment, segment, CostVector([0]), state2))
            elif segment_symbol in yimas_cons:  # segment is consonant
                transducer.add_arc(Arc(state1, segment, segment, CostVector([0]), state1))
                transducer.add_arc(Arc(state2, segment, segment, CostVector([0]), state1))
            else:
                raise ConstraintError("{} not supported in this constraint".format(segment_symbol))


        return transducer

    @classmethod
    def get_constraint_name(cls):
        return "Contiguity"



yimas_cons = ['t', 'p', 'k', 'c']
yimas_vowels = ['a', 'i', 'u', 'v']

class ConstraintError(Exception):
    pass