from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from tests.otml_configuration_for_testing import configurations
from grammar.feature_table import FeatureTable
from grammar.lexicon import Word
from grammar.lexicon import Lexicon
from corpus import Corpus
from grammar.constraint import MaxConstraint, DepConstraint, IdentConstraint, PhonotacticConstraint, FaithConstraint
from grammar.constraint import HeadDepConstraint, MainLeftConstraint, PrecedeConstraint, ContiguityConstraint
from grammar.constraint_set import ConstraintSet
from tests.persistence_tools import get_pickle
from grammar.grammar import Grammar
from tests.persistence_tools import get_constraint_set_fixture, get_feature_table_fixture, get_corpus_fixture,\
    write_to_dot_to_file, clear_dot_folder
from traversable_grammar_hypothesis import TraversableGrammarHypothesis

class TestTransducerRepresentations(unittest.TestCase):

    def setUp(self):
        self.phonotactic_test_feature_table = FeatureTable.load(get_feature_table_fixture("phonotactic_test_feature_table"
                                                                     ".json"))
        self.feature_table = FeatureTable.load(get_feature_table_fixture("minimal_feature_table.json"))
        self.constraint_set_filename = get_constraint_set_fixture("minimal_constraint_set.json")
        self.corpus = Corpus.load(get_corpus_fixture("small_ab_corpus.txt"))
        self.constraint_set = ConstraintSet.load(self.constraint_set_filename, self.feature_table)
        self.lexicon = Lexicon(self.corpus.get_words(), self.feature_table)
        self.grammar = Grammar(self.feature_table, self.constraint_set, self.lexicon)

    def test_base_faithfulness_transducer(self):
        max_constraint = MaxConstraint([{'syll': '+'}], self.feature_table)
        transducer, segments, state = super(MaxConstraint, max_constraint)._base_faithfulness_transducer()
        self.assertEqual(transducer, get_pickle("base_faithfulness_transducer"))


    def test_faithfulness_constraints_get_transducer(self):
        ident_transducer = IdentConstraint([{'syll': '+'}], self.feature_table).get_transducer()
        max_transducer = MaxConstraint([{'syll': '+'}], self.feature_table).get_transducer()
        dep_transducer = DepConstraint([{'syll': '+'}], self.feature_table).get_transducer()

        self.assertEqual(ident_transducer, get_pickle("ident_transducer"))

        if not configurations["ALLOW_CANDIDATES_WITH_CHANGED_SEGMENTS"]:
            self.assertEqual(max_transducer, get_pickle("max_transducer"))
            self.assertEqual(dep_transducer, get_pickle("dep_transducer"))
        else:
            self.assertEqual(max_transducer, get_pickle("max_transducer_with_changed_segments"))
            self.assertEqual(dep_transducer, get_pickle("dep_transducer_with_changed_segments"))


    def test_phonotactic_constraint_get_transducer(self):
        phonotactic_constraint = PhonotacticConstraint([{'cons': '+'}, {'labial': '+'}, {'voice': '+'}], self.phonotactic_test_feature_table)
        phonotactic_transducer = phonotactic_constraint.get_transducer()
        self.assertEqual(phonotactic_transducer, get_pickle("phonotactic_transducer"))


    def test_faith_constraint_get_transducer(self):
        faith_constraint = FaithConstraint([], self.feature_table)

        faith_transducer = faith_constraint.get_transducer()
        if not configurations["ALLOW_CANDIDATES_WITH_CHANGED_SEGMENTS"]:
            self.assertEqual(faith_transducer, get_pickle("faith_transducer"))
        else:
            self.assertEqual(faith_transducer, get_pickle("faith_transducer_with_changed_segments"))


    def test_word_make_transducer(self):
        word = Word('abb', self.feature_table)
        word_transducer = word.get_transducer()
        self.assertEqual(word_transducer, get_pickle("word_transducer"))


    def test_constraint_set_make_transducer(self):
        constraint_set_transducer = self.constraint_set.get_transducer()
        self.assertEqual(constraint_set_transducer, get_pickle("constraint_set_transducer"))


    #HeadDep[+syll#+cons#+stress]
    #MainLeft[+syll#+cons#+stress]
    #Precede[+syll#+stress]

    def test_yimas_transducers(self):
        feature_table = FeatureTable.load(get_feature_table_fixture("yimas_feature_table.json"))
        head_dep_transducer = HeadDepConstraint([], feature_table).get_transducer()
        main_left_transducer = MainLeftConstraint([], feature_table).get_transducer()
        precede_transducer = PrecedeConstraint([], feature_table).get_transducer()
        contiguity_transducer = ContiguityConstraint([], feature_table).get_transducer()

        write_to_dot_to_file(precede_transducer,"precede_transducer")
        write_to_dot_to_file(main_left_transducer, "main_left_transducer")
        write_to_dot_to_file(head_dep_transducer, "head_dep_transducer")
        write_to_dot_to_file(contiguity_transducer, "contiguity_transducer")


    #TODO finish testing
    #def test_grammar_make_transducer(self):
    #    grammar_transducer = self.grammar.make_transducer()
    #    _write_pickle(grammar_transducer, "grammar_transducer")













