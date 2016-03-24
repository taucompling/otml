#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals


import sys
import os
import unittest
import random
import logging
from os.path import split, join, normpath, abspath
import platform

IT = 50
CF = 0.999984

unit_tests_log_file_name = "../../logging/{}_extended_augmented_demote_only_{}_{}.txt".format(platform.node(), IT, CF)

#if os.path.exists(unit_tests_log_file_name):
#    raise ValueError("log name already exits")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s', "%Y-%m-%d %H:%M:%S")
dirname, filename = split(abspath(__file__))
unit_tests_log_path = normpath(join(dirname, unit_tests_log_file_name))
file_log_handler = logging.FileHandler(unit_tests_log_path, mode='w')
file_log_handler.setFormatter(file_log_formatter)
logger.addHandler(file_log_handler)

FILE_PATH = os.path.abspath(os.path.join(__file__, '..'))
PROJECT_PATH = os.path.abspath(os.path.join(FILE_PATH, '../../'))
os.chdir(FILE_PATH)
sys.path.append(PROJECT_PATH)

from tests.otml_configuration_for_testing import configurations
from grammar.lexicon import Lexicon
from grammar.feature_table import FeatureTable
from grammar.constraint_set import ConstraintSet
from grammar.grammar import Grammar
from traversable_grammar_hypothesis import TraversableGrammarHypothesis
from corpus import Corpus
from simulated_annealing import SimulatedAnnealing
from tests.persistence_tools import get_constraint_set_fixture, get_feature_table_fixture, get_corpus_fixture

class TestOtmlWithAspirationAndLengtheningExtendedDemoteOnly(unittest.TestCase):
    def setUp(self):
        configurations["CORPUS_DUPLICATION_FACTOR"] = 2
        self.feature_table = FeatureTable.load(get_feature_table_fixture("aspiration_and_lengthening_extended_augmented_feature_table.json"))
        corpus = Corpus.load(get_corpus_fixture("aspiration_and_lengthening_extended_demote_only_250_corpus.txt"))
        self.constraint_set = ConstraintSet.load(get_constraint_set_fixture("aspiration_and_lengthening_augmented_demote_only_constraint_set.json"),
                                                  self.feature_table)
        self.lexicon = Lexicon(corpus.get_words(), self.feature_table)
        self.grammar = Grammar(self.feature_table, self.constraint_set, self.lexicon)
        self.data = corpus.get_words()
        self.traversable_hypothesis = TraversableGrammarHypothesis(self.grammar, self.data)

        def function(words):
            number_of_long_vowels = sum([word.count(":") for word in words])
            number_of_aspirated_consonants = sum([word.count("h") for word in words])
            combined_number = number_of_long_vowels + number_of_aspirated_consonants
            return "number of long vowels and aspirated consonants in lexicon: {} (long vowels = {}, " \
                   "aspirated consonants = {})".format(combined_number, number_of_long_vowels,
                                                       number_of_aspirated_consonants)
        self.simulated_annealing = SimulatedAnnealing(self.traversable_hypothesis,
                                                      target_lexicon_indicator_function=function,
                                                      sample_target_lexicon=["dati", "pitip", "batag"],
                                                      sample_target_outputs=["dathi", "phithip", "batha:g"])

    run_test = True
    @unittest.skipUnless(run_test, "long running test skipped")
    def test_run(self):
        #random.seed(1)
        configurations["CONSTRAINT_SET_MUTATION_WEIGHTS"] = {
            "insert_constraint": 0,
            "remove_constraint": 0,
            "demote_constraint": 1,
            "insert_feature_bundle_phonotactic_constraint": 0,
            "remove_feature_bundle_phonotactic_constraint": 0,
            "augment_feature_bundle": 0}

        configurations["CONSTRAINT_INSERTION_WEIGHTS"] = {
            "Dep": 1,
            "Max": 1,
            "Ident": 0,
            "Phonotactic": 1}

        configurations["LEXICON_MUTATION_WEIGHTS"] = {
            "insert_segment": 1,
            "delete_segment": 1,
            "change_segment": 0}

        configurations["INITIAL_TEMPERATURE"] = IT
        configurations["COOLING_PARAMETER"] = CF
        configurations["INITIAL_NUMBER_OF_BUNDLES_IN_PHONOTACTIC_CONSTRAINT"] = 2
        configurations["MAX_FEATURE_BUNDLES_IN_PHONOTACTIC_CONSTRAINT"] = 2
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 100
        configurations["MAX_NUMBER_OF_CONSTRAINTS_IN_CONSTRAINT_SET"] = 12
        configurations["RESTRICTION_ON_ALPHABET"] = True

        configurations["DEBUG_LOGGING_INTERVAL"] = 50
        configurations["RANDOM_SEED"] = False
        configurations["SEED"] = 76



        number_of_steps_performed, hypothesis = self.simulated_annealing.run()


if __name__ == '__main__':
    unittest.main()