#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals


import unittest

import tests.log_configuration_for_testing
from tests.otml_configuration_for_testing import configurations
from grammar.lexicon import Lexicon
from grammar.feature_table import FeatureTable
from grammar.constraint_set import ConstraintSet
from grammar.grammar import Grammar
from traversable_grammar_hypothesis import TraversableGrammarHypothesis
from corpus import Corpus
from simulated_annealing import SimulatedAnnealing, _pretty_runtime_str
from tests.persistence_tools import get_constraint_set_fixture, get_feature_table_fixture, get_corpus_fixture, clear_modules_caching


class TestSimulatedAnnealing(unittest.TestCase):
    def setUp(self):
        clear_modules_caching()
        feature_table = FeatureTable.load(get_feature_table_fixture("a_b_and_cons_feature_table.json"))
        corpus = Corpus.load(get_corpus_fixture("test_otml_with_demote_only_corpus.txt"))
        constraint_set = ConstraintSet.load(get_constraint_set_fixture("test_bb_with_demote_only_constraint_set.json"),
                                              feature_table)
        lexicon = Lexicon(corpus.get_words(), feature_table)
        self.grammar = Grammar(feature_table, constraint_set, lexicon)

        self.data = corpus.get_words()
        self.traversable_hypothesis = TraversableGrammarHypothesis(self.grammar, self.data)
        self.simulated_annealing = SimulatedAnnealing(self.traversable_hypothesis)

    def test_pretty_runtime_str(self):
        self.assertEqual(_pretty_runtime_str(10), "10 seconds")
        self.assertEqual(_pretty_runtime_str(100), "1 minutes, 40 seconds")
        self.assertEqual(_pretty_runtime_str(1000), "16 minutes, 40 seconds")
        self.assertEqual(_pretty_runtime_str(10000), "2 hours, 46 minutes, 40 seconds")
        self.assertEqual(_pretty_runtime_str(100000), "1 day, 3 hours, 46 minutes, 40 seconds")
        self.assertEqual(_pretty_runtime_str(1000000), "11 days, 13 hours, 46 minutes, 40 seconds")

    def test_calculate_num_of_steps(self):
        configurations["INITIAL_TEMPERATURE"] = 100
        configurations["THRESHOLD"] = 0.01
        configurations["COOLING_PARAMETER"] = 0.999
        self.assertEqual(SimulatedAnnealing._calculate_num_of_steps(), 9206)

        configurations["INITIAL_TEMPERATURE"] = 100
        configurations["THRESHOLD"] = 0.01
        configurations["COOLING_PARAMETER"] = 0.9995
        print(SimulatedAnnealing._calculate_num_of_steps())



