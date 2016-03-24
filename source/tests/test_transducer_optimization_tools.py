from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import os
from copy import deepcopy
import pickle

from six import PY3

import tests.log_configuration_for_testing
from tests.otml_configuration_for_testing import configurations
from tests.persistence_tools import get_pickle
from transducers_optimization_tools import remove_suboptimal_paths, make_optimal_paths, optimize_transducer_grammar_for_word
from transducer import CostVector, Arc, State, Transducer
from grammar.constraint import PhonotacticConstraint
from grammar.feature_table import FeatureTable, Segment, NULL_SEGMENT
from grammar.lexicon import Word
from tests.persistence_tools import get_feature_table_fixture



class TestingTransducerOptimizationTools(unittest.TestCase):
    """ this test case is designed to visually test the transducers generated on different stages in OTML
    compered with the same one in Riggle 2004.
    see: https://taucompling.atlassian.net/wiki/display/OTML/Testing+transducer+algorithms
    """
    def setUp(self):
        self.feature_table = FeatureTable.load(get_feature_table_fixture("a_b_and_son_feature_table.json"))
        self.DEP = _manually_create_DEP(self.feature_table)
        self.IDENT_son =_manually_create_IDENT_son(self.feature_table)
        self.MAX = _manually_create_MAX(self.feature_table)
        self.no_CC = PhonotacticConstraint([{'son': '-'}, {'son': '-'}], self.feature_table).get_transducer() # p.43 fig. 22
        self.bba = Word("bba", self.feature_table).get_transducer() #p.38 fig.15

        self.no_CC_DEP_MAX = Transducer.intersection(self.no_CC, self.DEP, self.MAX)  # p. 47 fig.27
        bb = Word("bb", self.feature_table).get_transducer()
        self.bb_no_CC_DEP_MAX = Transducer.intersection(bb, self.no_CC_DEP_MAX)  #p. 57 fig. 39

        self.no_CC_MAX_DEP = Transducer.intersection(self.no_CC, self.MAX, self.DEP)  # p. 143 fig.164
        self.bb_no_CC_DEP_MAX_removed_suboptimal_paths = remove_suboptimal_paths(deepcopy(self.bb_no_CC_DEP_MAX))


    def test_intersection_constraints_only(self):
        self.assertEqual(self.no_CC_DEP_MAX, get_pickle("no_CC_DEP_MAX"))

    def test_intersection_constraints_and_word(self):
        self.assertEqual(self.bb_no_CC_DEP_MAX, get_pickle("bb_no_CC_DEP_MAX"))

    def test_remove_suboptimal_paths(self):
        self.assertEqual(self.bb_no_CC_DEP_MAX_removed_suboptimal_paths, get_pickle("bb_no_CC_DEP_MAX_removed_suboptimal_paths"))


    def test_remove_suboptimal_paths_and_clear_dead_states_with_impasse(self):
        self.bb_no_CC_DEP_MAX_removed_suboptimal_paths.clear_dead_states(with_impasse_states=True)
        self.bb_no_CC_DEP_MAX_removed_suboptimal_paths_and_cleared_dead_states = self.bb_no_CC_DEP_MAX_removed_suboptimal_paths
        pickled_transducer = get_pickle("bb_no_CC_DEP_MAX_removed_suboptimal_paths_and_cleared_dead_states")
        self.assertEqual(self.bb_no_CC_DEP_MAX_removed_suboptimal_paths_and_cleared_dead_states, pickled_transducer)


    def test_make_optimal_paths(self):
        no_CC_MAX_DEP_with_optimal_paths = make_optimal_paths(self.no_CC_MAX_DEP, self.feature_table) # p. 143 fig.164
        self.assertEqual(no_CC_MAX_DEP_with_optimal_paths, get_pickle("no_CC_MAX_DEP_with_optimal_paths"))


    def test_optimize_transducer_grammar_for_word(self):
        abab = Word("abab", self.feature_table)
        no_CC_MAX_DEP_with_optimal_paths = make_optimal_paths(self.no_CC_MAX_DEP, self.feature_table)
        abab_acceptor = abab.get_transducer()
        new_transducer = Transducer.intersection(abab_acceptor, no_CC_MAX_DEP_with_optimal_paths)
        new_transducer.clear_dead_states()
        self.optimized_no_CC_MAX_DEP_for_abab = optimize_transducer_grammar_for_word(abab, new_transducer)
        self.assertEqual(self.optimized_no_CC_MAX_DEP_for_abab, get_pickle("optimized_no_CC_MAX_DEP_for_abab"))


def _manually_create_DEP(feature_table):
    """ manually creates a DEP constraint transducer that is featured in Riggle 2004 p.34 fig. 10

 :param feature_table: feature_table used for the transducer
 :type feature_table: FeatureTable
 :returns: Transducer - DEP constraint transducer
    """

    transducer = Transducer(feature_table.get_segments())
    state = State('dep')
    transducer.set_as_single_state(state)
    transducer.add_arc(Arc(state, NULL_SEGMENT, Segment('a'), CostVector([1]), state))
    transducer.add_arc(Arc(state, NULL_SEGMENT, Segment('b'), CostVector([1]), state))
    transducer.add_arc(Arc(state, Segment('a'), Segment('a'), CostVector([0]), state))
    transducer.add_arc(Arc(state, Segment('a'), NULL_SEGMENT, CostVector([0]), state))
    transducer.add_arc(Arc(state, Segment('b'), Segment('b'), CostVector([0]), state))
    transducer.add_arc(Arc(state, Segment('b'), NULL_SEGMENT, CostVector([0]), state))
    return transducer


def _manually_create_IDENT_son(feature_table):
    """ manually creates a IDENT(son) constraint transducer that is featured in Riggle 2004 p.38 fig. 15

 :param feature_table: feature_table used for the transducer
 :type feature_table: FeatureTable
 :returns: Transducer - IDENT(son) constraint transducer
    """

    transducer = Transducer(feature_table.get_segments())
    state = State('id-son')
    transducer.set_as_single_state(state)
    transducer.add_arc(Arc(state, NULL_SEGMENT, Segment('a'), CostVector([0]), state))
    transducer.add_arc(Arc(state, NULL_SEGMENT, Segment('b'), CostVector([0]), state))
    transducer.add_arc(Arc(state, Segment('a'), Segment('a'), CostVector([0]), state))
    transducer.add_arc(Arc(state, Segment('a'), Segment('b'), CostVector([1]), state))
    transducer.add_arc(Arc(state, Segment('a'), NULL_SEGMENT, CostVector([0]), state))
    transducer.add_arc(Arc(state, Segment('b'), Segment('a'), CostVector([1]), state))
    transducer.add_arc(Arc(state, Segment('b'), Segment('b'), CostVector([0]), state))
    transducer.add_arc(Arc(state, Segment('b'), NULL_SEGMENT, CostVector([0]), state))
    return transducer


def _manually_create_MAX(feature_table):
    """ manually creates a MAX constraint transducer that is featured in Riggle 2004 p.42 fig. 22

 :param feature_table: feature_table used for the transducer
 :type feature_table: FeatureTable
 :returns: Transducer - MAX constraint transducer
    """

    transducer = Transducer(feature_table.get_segments())
    state = State('max')
    transducer.set_as_single_state(state)
    transducer.add_arc(Arc(state, NULL_SEGMENT, Segment('a'), CostVector([0]), state))
    transducer.add_arc(Arc(state, NULL_SEGMENT, Segment('b'), CostVector([0]), state))
    transducer.add_arc(Arc(state, Segment('a'), Segment('a'), CostVector([0]), state))
    transducer.add_arc(Arc(state, Segment('a'), NULL_SEGMENT, CostVector([1]), state))
    transducer.add_arc(Arc(state, Segment('b'), Segment('b'), CostVector([0]), state))
    transducer.add_arc(Arc(state, Segment('b'), NULL_SEGMENT, CostVector([1]), state))
    return transducer
