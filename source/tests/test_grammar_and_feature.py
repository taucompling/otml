from __future__ import absolute_import, division, print_function, unicode_literals
import unittest
import os

from tests.otml_configuration_for_testing import configurations
from corpus import Corpus
from grammar.feature_table import FeatureTable
from grammar.constraint_set import ConstraintSet, GrammarParseError
from tests.persistence_tools import get_constraint_set_fixture, get_feature_table_fixture, get_corpus_fixture


class TestGrammarAndFeature(unittest.TestCase):

    def setUp(self):
        self.feature_table = FeatureTable.load(get_feature_table_fixture("feature_table.json"))
        self.corpus = Corpus.load(get_corpus_fixture("corpus.txt"))
        self.correct_constraint_set_filename = get_constraint_set_fixture("constraint_set.json")
        self.full_feature_table_for_grammar = FeatureTable.load(get_feature_table_fixture("full_feature_table.json"))

    def test_validity_of_segments(self):
        for word_string in self.corpus.words:
            for segment in word_string:
                self.assertTrue(self.feature_table.is_valid_symbol(segment), "The word {} contains the illegal segment {}".format(word_string, segment))

    def test_grammar_with_feature_validity_missing_feature(self):
        with self.assertRaises(GrammarParseError):
            ConstraintSet.load(self.correct_constraint_set_filename, self.feature_table)

    def test_grammar_with_feature_validity_ok(self):
        grammar = ConstraintSet.load(self.correct_constraint_set_filename,
                                          self.full_feature_table_for_grammar)
        self.assertEqual(str(grammar), "Constraint Set: Phonotactic[[+cons, +labial][+cons][+cons]] "
                                          ">> Ident[-syll] >> Dep[+cons] >> Max[-cons, -syll]")
