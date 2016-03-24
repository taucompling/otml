#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import os

from tests.otml_configuration_for_testing import configurations
from grammar.lexicon import Word, Lexicon
from grammar.feature_table import FeatureTable
from grammar.constraint_set import ConstraintSet
from grammar.grammar import Grammar
from traversable_grammar_hypothesis import TraversableGrammarHypothesis
from tests.persistence_tools import get_constraint_set_fixture, get_feature_table_fixture, get_corpus_fixture,\
    write_to_dot_to_file, clear_modules_caching, get_feature_table_by_fixture, get_corpus_by_fixture
from corpus import Corpus
from debug_tools import timeit
import pprint

from itertools import permutations


class TestTraversableGrammarHypothesis(unittest.TestCase):
    def setUp(self):
        clear_modules_caching()
        self.feature_table = FeatureTable.load(get_feature_table_fixture("a_b_and_son_feature_table.json"))
        self.constraint_set = ConstraintSet.load(get_constraint_set_fixture("no_bb_Max_Dep_constraint_set.json"),
                                                 self.feature_table)
        self.lexicon = Lexicon(['abb', 'bba'], self.feature_table)
        self.grammar = Grammar(self.feature_table, self.constraint_set, self.lexicon)



    def test_underspecified(self):
        feature_table = FeatureTable.load(get_feature_table_fixture("ab_0_feature_table.json"))
        constraint_set = ConstraintSet.load(get_constraint_set_fixture("bb_demote_only_target_constraint_set.txt"),
                                            feature_table)
        lexicon = Lexicon(['abb'], feature_table)
        grammar = Grammar(feature_table, constraint_set, lexicon)
        hypothesis = TraversableGrammarHypothesis(grammar, ['abab'])
        print(hypothesis.get_energy())


    def test_normal(self):
        feature_table = FeatureTable.load(get_feature_table_fixture("a_b_and_cons_feature_table.json"))
        constraint_set = ConstraintSet.load(get_constraint_set_fixture("bb_demote_only_target_constraint_set.txt"),
                                            feature_table)
        lexicon = Lexicon(['abb'], feature_table)
        grammar = Grammar(feature_table, constraint_set, lexicon)
        hypothesis = TraversableGrammarHypothesis(grammar, ['abab'])
        print(hypothesis.get_energy())

    def test_get_data_length_given_grammar_parsable_data(self):
        data = ['abab', 'baba']
        traversable_hypothesis = TraversableGrammarHypothesis(self.grammar, data)
        self.assertEqual(traversable_hypothesis.get_data_length_given_grammar(), 2)



    def test_get_data_length_given_grammar_unparsable_data(self):
        data = ['a', 'b']
        traversable_hypothesis = TraversableGrammarHypothesis(self.grammar, data)
        self.assertEqual(traversable_hypothesis.get_data_length_given_grammar(), float("inf"))

    def test_get_data_length_given_grammar_unparsable_data(self):
        data = ['a', 'b']
        traversable_hypothesis = TraversableGrammarHypothesis(self.grammar, data)
        self.assertEqual(traversable_hypothesis.get_data_length_given_grammar(), float("inf"))


    def test_bb_initial_state(self):
        traversable_hypothesis = _get_initial_hypothesis_state("a_b_and_cons_feature_table.json", "faith_constraint_set.json", "bb_corpus.txt")
        self.assertEqual(traversable_hypothesis.get_energy(), 412430)

    def test_bb_target_state(self):
        configurations["RESTRICTION_ON_ALPHABET"] = False
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 1
        traversable_hypothesis = _get_target_hypothesis_state("a_b_and_cons_feature_table.json",
                                                             "bb_target_constraint_set.json",
                                                             "bb_target_lexicon.txt",
                                                             "bb_corpus.txt")
        self.assertEqual(traversable_hypothesis.get_energy(), 12414)


    def test_bb_target_state_halfed(self):
        feature_table = FeatureTable.load(get_feature_table_fixture("a_b_and_cons_feature_table.json"))
        constraint_set = ConstraintSet.load(get_constraint_set_fixture("bb_target_constraint_set.json"),
                                            feature_table)
        target_lexicon_words = Corpus.load(get_corpus_fixture("bb_target_lexicon_halfed.txt")).get_words()
        lexicon = Lexicon(target_lexicon_words, feature_table)
        grammar = Grammar(feature_table, constraint_set, lexicon)
        corpus = Corpus.load(get_corpus_fixture("bb_corpus.txt"))
        traversable_hypothesis = TraversableGrammarHypothesis(grammar, corpus)
        self.assertEqual(traversable_hypothesis.get_energy(), 407430)


    def test_french_deletion_target_state(self):
        traversable_hypothesis = _get_target_hypothesis_state_by_simulation_name("french_deletion")
        self.assertEqual(traversable_hypothesis.get_energy(), 3415)  # used to be 3396

    def test_french_deletion_hypotheses(self):
        def mark_min(list_of_ints):
            min_value = min(list_of_ints)
            list_of_strings = []
            for value in list_of_ints:
                if value is not min_value:
                    list_of_strings.append(str(value))
                else:
                    list_of_strings.append("*{}*".format(value))
            return list_of_strings

        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 1
        configurations["RESTRICTION_ON_ALPHABET"] = True
        configurations["CORPUS_DUPLICATION_FACTOR"] = 25
        if configurations["RESTRICTION_ON_ALPHABET"]:
            list_of_files = ["french_deletion_corpus_for_with_restrictions.txt", "french_deletion_og_lexicon_for_with_restrictions.txt", "french_deletion_target_lexicon_for_with_restrictions.txt"]
            #list_of_files = ["aa.txt", "aa_og.txt", "aa_target.txt"]
        else:
            list_of_files = ["french_deletion_corpus.txt", "french_deletion_og_lexicon.txt", "french_deletion_target_lexicon.txt"]

        print("n  ident  og  target")
        for n in list(range(25, 26)):
             configurations["CORPUS_DUPLICATION_FACTOR"] = n
             print(n, end =" ")
             results = []
             for file in list_of_files:
                 traversable_hypothesis = _get_target_hypothesis_state("french_deletion_feature_table.json",
                                                             "french_deletion_target_constraint_set.json",
                                                             file,
                                                             list_of_files[0])
                 energy = traversable_hypothesis.get_energy()
                 #print(traversable_hypothesis.get_recent_energy_signature())
                 results.append(energy)

             print(mark_min(results))



    def test_t_aspiration_target_state(self):
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 25
        feature_table = FeatureTable.load(get_feature_table_fixture("t_aspiration_feature_table.json"))
        constraint_set = ConstraintSet.load(get_constraint_set_fixture("t_aspiration_target_constraint_set.json"),
                                            feature_table)
        target_lexicon_words = Corpus.load(get_corpus_fixture("t_aspiration_target_lexicon.txt")).get_words()
        lexicon = Lexicon(target_lexicon_words, feature_table)
        grammar = Grammar(feature_table, constraint_set, lexicon)
        corpus = Corpus.load(get_corpus_fixture("t_aspiration_corpus.txt"))
        traversable_hypothesis = TraversableGrammarHypothesis(grammar, corpus)
        configurations["RESTRICTION_ON_ALPHABET"] = True
        self.assertEqual(traversable_hypothesis.get_energy(), 167838)
        configurations["RESTRICTION_ON_ALPHABET"] = False
        self.assertEqual(traversable_hypothesis.get_energy(), 173676)


    def test_t_aspiration_initial_state(self):
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 25
        configurations["RESTRICTION_ON_ALPHABET"] = True
        feature_table = FeatureTable.load(get_feature_table_fixture("t_aspiration_feature_table.json"))
        corpus = Corpus.load(get_corpus_fixture("t_aspiration_corpus.txt"))
        constraint_set = ConstraintSet.load(get_constraint_set_fixture("faith_constraint_set.json"),
                                                  feature_table)
        lexicon = Lexicon(corpus.get_words(), feature_table)
        grammar = Grammar(feature_table, constraint_set, lexicon)
        data = corpus.get_words()
        traversable_hypothesis = TraversableGrammarHypothesis(grammar, data)

    def test_aspiration_and_lengthening_target_state(self):
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 100
        configurations["RESTRICTION_ON_ALPHABET"] = True
        traversable_hypothesis = _get_target_hypothesis_state_by_simulation_name("aspiration_and_lengthening")
        self.assertEqual(traversable_hypothesis.get_energy(), 100861)  # used to be 100818


    def test_aspiration_and_lengthening_extended_target_state(self):
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 100
        configurations["RESTRICTION_ON_ALPHABET"] = True
        traversable_hypothesis = _get_target_hypothesis_state("aspiration_and_lengthening_extended_feature_table.json",
                                                             "aspiration_and_lengthening_target_constraint_set.json",
                                                             "aspiration_and_lengthening_extended_target_lexicon.txt",
                                                             "aspiration_and_lengthening_extended_corpus.txt")
        self.assertEqual(traversable_hypothesis.get_energy(), 206059)


    def test_aspiration_and_lengthening_448(self):
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 100
        configurations["RESTRICTION_ON_ALPHABET"] = True
        traversable_hypothesis = _get_target_hypothesis_state("aspiration_and_lengthening_feature_table.json",
                                                             "aspiration_and_lengthening_target_constraint_set.json",
                                                             "aspiration_and_lengthening_448_target_lexicon.txt",
                                                             "aspiration_and_lengthening_448_corpus.txt")
        self.assertEqual(traversable_hypothesis.get_energy(), 412577)


    def test_aspiration_and_lengthening_extended_augmented_target_state(self):
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 100
        configurations["RESTRICTION_ON_ALPHABET"] = True
        feature_table = FeatureTable.load(
            get_feature_table_fixture("aspiration_and_lengthening_extended_augmented_feature_table.json"))
        constraint_set = ConstraintSet.load(
            get_constraint_set_fixture("aspiration_and_lengthening_augmented_target_constraint_set.json"),
            feature_table)
        target_lexicon_words = Corpus.load(get_corpus_fixture("aspiration_and_lengthening_extended_target_lexicon.txt")).get_words()
        lexicon = Lexicon(target_lexicon_words, feature_table)
        grammar = Grammar(feature_table, constraint_set, lexicon)
        corpus = Corpus.load(get_corpus_fixture("aspiration_and_lengthening_extended_corpus.txt"))
        traversable_hypothesis = TraversableGrammarHypothesis(grammar, corpus)

        #print(traversable_hypothesis.get_energy())


    def test_yimas_target_state(self):
        traversable_hypothesis = _get_target_hypothesis_state_by_simulation_name("yimas")
        print(traversable_hypothesis.grammar.constraint_set)
        self.assertEqual(traversable_hypothesis.get_energy(), 2430)

    def test_yimas_with_contiguity_target_state(self):
        traversable_hypothesis = _get_target_hypothesis_state("yimas_feature_table.json",
                                                       "yimas_with_contiguity_target_constraint_set.json",
                                                       "yimas_target_lexicon.txt",
                                                       "yimas_corpus.txt")
        self.assertEqual(traversable_hypothesis.get_energy(), 2438)

    def test_tpk_aiu_yimas_with_contiguity_initial(self):
        configurations["RESTRICTION_ON_ALPHABET"] = True
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 1
        traversable_hypothesis = _get_initial_hypothesis_state("yimas_tpk_aiu_feature_table.csv",
                                                               "yimas_tpk_aiu_contiguity_constraint_set.txt",
                                                               "yimas_tpk_aiu_corpus.txt")
        self.assertEqual(traversable_hypothesis.get_energy(), 2811)

    def test_tpk_aiu_yimas_8_initial(self):
        configurations["RESTRICTION_ON_ALPHABET"] = True
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 1
        traversable_hypothesis = _get_initial_hypothesis_state("yimas_tpk_aiu_feature_table.csv",
                                                               "yimas_tpk_aiu_constraint_set.txt",
                                                               "yimas_tpk_aiu_8_corpus.txt")
        self.assertEqual(traversable_hypothesis.get_energy(), 335)

    def test_tpk_aiu_yimas_8_target(self):
        configurations["RESTRICTION_ON_ALPHABET"] = True
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 1
        traversable_hypothesis = _get_target_hypothesis_state("yimas_tpk_aiu_feature_table.csv",
                                                               "yimas_tpk_aiu_target_constraint_set.txt",
                                                               "yimas_tpk_aiu_8_target_lexicon.txt",
                                                               "yimas_tpk_aiu_8_corpus.txt")
        self.assertEqual(traversable_hypothesis.get_energy(), 305)


    def test_tpk_aiu_yimas_initial(self):
        configurations["RESTRICTION_ON_ALPHABET"] = True
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 1
        traversable_hypothesis = _get_initial_hypothesis_state("yimas_tpk_aiu_feature_table.csv",
                                                               "yimas_tpk_aiu_constraint_set.txt",
                                                               "yimas_tpk_aiu_corpus.txt")
        self.assertEqual(traversable_hypothesis.get_energy(), 2811)
        #100: 72111

    def test_tpk_aiu_yimas_target(self):
        configurations["RESTRICTION_ON_ALPHABET"] = True
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 100
        traversable_hypothesis = _get_target_hypothesis_state("yimas_tpk_aiu_feature_table.csv",
                                                               "yimas_tpk_aiu_target_constraint_set.txt",
                                                               "yimas_tpk_aiu_target_lexicon.txt",
                                                               "yimas_tpk_aiu_corpus.txt")
        self.assertEqual(traversable_hypothesis.get_energy(), 71766)
        #100: 71766

    def test_td_kg_ai_aspiration_and_lengthening_initial(self):
        configurations["RESTRICTION_ON_ALPHABET"] = True
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 100
        traversable_hypothesis = _get_initial_hypothesis_state_by_simulation_name("td_kg_ai_aspiration_and_lengthening")
        self.assertEqual(traversable_hypothesis.get_energy(), 165943)

    def test_td_kg_ai_aspiration_and_lengthening_target(self):
        configurations["RESTRICTION_ON_ALPHABET"] = True
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 100
        traversable_hypothesis = _get_target_hypothesis_state_by_simulation_name("td_kg_ai_aspiration_and_lengthening")
        self.assertEqual(traversable_hypothesis.get_energy(), 163570)


    def tearDown(self):
        configurations.reset_to_original_configurations()


def _get_target_hypothesis_state_by_simulation_name(simulation_name):
    feature_table_file_name = "{}_feature_table.json".format(simulation_name)
    constraint_set_file_mame = "{}_target_constraint_set.json".format(simulation_name)
    lexicon_file_name = "{}_target_lexicon.txt".format(simulation_name)
    corpus_file_name = "{}_corpus.txt".format(simulation_name)
    return _get_target_hypothesis_state(feature_table_file_name, constraint_set_file_mame, lexicon_file_name, corpus_file_name)

def _get_initial_hypothesis_state_by_simulation_name(simulation_name):
    feature_table_file_name = "{}_feature_table.json".format(simulation_name)
    constraint_set_file_mame = "{}_target_constraint_set.json".format(simulation_name)
    corpus_file_name = "{}_corpus.txt".format(simulation_name)
    return _get_initial_hypothesis_state(feature_table_file_name, constraint_set_file_mame, corpus_file_name)

def _get_target_hypothesis_state(feature_table_file_name, constraint_set_file_mame, lexicon_file_name, corpus_file_name):
    feature_table = get_feature_table_by_fixture(feature_table_file_name)
    constraint_set = ConstraintSet.load(get_constraint_set_fixture(constraint_set_file_mame), feature_table)
    lexicon = Lexicon(get_corpus_fixture(lexicon_file_name), feature_table)
    grammar = Grammar(feature_table, constraint_set, lexicon)
    corpus = get_corpus_by_fixture(corpus_file_name)
    traversable_hypothesis = TraversableGrammarHypothesis(grammar, corpus)
    return traversable_hypothesis

def _get_initial_hypothesis_state(feature_table_file_name, constraint_set_file_mame, corpus_file_name):
    feature_table = get_feature_table_by_fixture(feature_table_file_name)
    constraint_set = ConstraintSet.load(get_constraint_set_fixture(constraint_set_file_mame), feature_table)
    corpus = get_corpus_by_fixture(corpus_file_name)
    lexicon = Lexicon(corpus.get_words(), feature_table)
    grammar = Grammar(feature_table, constraint_set, lexicon)
    traversable_hypothesis = TraversableGrammarHypothesis(grammar, corpus)
    return traversable_hypothesis





