#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

import codecs
import unittest
import os



from tests.otml_configuration_for_testing import configurations
from grammar.lexicon import Word
from grammar.feature_table import FeatureTable
from grammar.constraint_set import ConstraintSet
from grammar.lexicon import Lexicon
from grammar.grammar import Grammar
from tests.stochastic_testcase import StochasticTestCase
from tests.persistence_tools import get_constraint_set_fixture, get_feature_table_fixture


class TestGrammar(StochasticTestCase):

    def setUp(self):
        self.feature_table = FeatureTable.load(get_feature_table_fixture("full_feature_table.json"))
        self.constraint_set = ConstraintSet.load(get_constraint_set_fixture("constraint_set.json"),
                                                  self.feature_table)
        self.constraint_set_with_faith = ConstraintSet.load(
            get_constraint_set_fixture("faith_constraint_set.json"),
            self.feature_table)
        self.lexicon = Lexicon(['abb', 'bba'], self.feature_table)
        self.grammar = Grammar(self.feature_table, self.constraint_set, self.lexicon)


    def test_parse_data(self):
        pass # see TestingParserSuite.test_parser

    def test_generate(self):
        pass  #see TestingParserSuite.generate


    def test_grammar_str(self):
        self.assertEqual(str(self.grammar), "Grammar with [Constraint Set: Phonotactic[[+cons, +labial]"
                                               "[+cons][+cons]] >> Ident[-syll] >> Dep[+cons] >> Max[-cons, -syll]]; "
                                               "and [Lexicon, number of words: 2, number of segments: 6, ['abb', 'bba']]")


    def test_grammar_make_mutation(self):
        pass
        #around 125 posible results
        #print(self._return_number_of_different_results(self.grammar,"make_mutation",number_of_runs=10000))
       # mutation1 = "Grammar with [Constraint Set: Phonotactic[[+cons, +labial][+cons][+cons]] >> Max[+syll] >> Ident[-syll] >> Dep[+cons] >> Max[-cons, -syll]]; and [Lexicon with 2 words: ['abb', 'bba']]"
       # mutation2 = "Grammar with [Constraint Set: Phonotactic[[+cons, +labial][+cons][+cons]] >> Ident[-syll] >> Dep[+cons] >> Max[-cons, -syll]]; and [Lexicon with 2 words: ['abb', 'bbda']]"
       # self.stochastic_object_method_testing(self.grammar, "make_mutation", [mutation1,mutation2],
       #                                       num_of_tests=1800, possible_result_threshold=1)

    def test_grammar_get_encoding_length(self):
        lexicon = Lexicon(['abb', 'bba'], self.feature_table)
        grammar = Grammar(self.feature_table, self.constraint_set, lexicon)
        self.assertEqual(grammar.get_encoding_length(), 154)