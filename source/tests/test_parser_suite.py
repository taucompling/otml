from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import os

from tests.otml_configuration_for_testing import configurations
from grammar.lexicon import Word
from grammar.feature_table import FeatureTable
from grammar.constraint_set import ConstraintSet
from grammar.lexicon import Lexicon
from grammar.grammar import Grammar
from corpus import Corpus
from traversable_grammar_hypothesis import TraversableGrammarHypothesis
from tests.persistence_tools import get_constraint_set_fixture, get_feature_table_fixture, get_corpus_fixture



dirname, filename = os.path.split(os.path.abspath(__file__))

class TestingParserSuite(unittest.TestCase):
    """ this test case is designed test the parser and related function: get_range and generate
    see: https://taucompling.atlassian.net/wiki/display/OTML/Testing+parser+suite
    """

    def setUp(self):
        self.feature_table = FeatureTable.load(get_feature_table_fixture("a_b_and_son_feature_table.json"))
        self.constraint_set = ConstraintSet.load(get_constraint_set_fixture("no_bb_Max_Dep_constraint_set.json"),
                                                  self.feature_table)
        self.corpus = Corpus.load(get_corpus_fixture("testing_parser_suite_corpus.txt"))
        self.lexicon = Lexicon(self.corpus.get_words(),self.feature_table)
        self.grammar = Grammar(self.feature_table, self.constraint_set, self.lexicon)
        self.bb = Word("bb", self.feature_table)
        self.bab = Word("bab", self.feature_table)
        self.abba = Word("abba", self.feature_table)
        self.ababa = Word("ababa", self.feature_table)


    def test_generate(self):
        self.assertEqual(self.grammar.generate(self.bb), {"bab"})
        self.assertEqual(self.grammar.generate(self.bab), {"bab"})

        self.assertEqual(self.grammar.generate(self.abba), {"ababa"})
        self.assertEqual(self.grammar.generate(self.ababa),  {"ababa"})


    def test_parser(self):
        traversable_hypothesis = TraversableGrammarHypothesis(self.grammar, ["bb"])
        self.assertEqual(traversable_hypothesis.parse_data(), {'bb': set()})

        traversable_hypothesis = TraversableGrammarHypothesis(self.grammar, ["ababa"])
        self.assertEqual(traversable_hypothesis.parse_data(), {"ababa": set([(self.abba, 1), (self.ababa, 1)])})