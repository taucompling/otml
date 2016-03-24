import sys
import os
import unittest
import logging
import platform
from os.path import split, join, normpath, abspath

simulation_number = 1


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
from tests.simulation_test_case import SimulationTestCase

class TestOtmlWithTAspiration(SimulationTestCase):
    def setUp(self):
        configurations["CONSTRAINT_SET_MUTATION_WEIGHTS"] = {
            "insert_constraint": 1,
            "remove_constraint": 1,
            "demote_constraint": 1,
            "insert_feature_bundle_phonotactic_constraint": 1,
            "remove_feature_bundle_phonotactic_constraint": 1,
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


        configurations["INITIAL_TEMPERATURE"] = 100
        configurations["COOLING_PARAMETER"] = 0.999985
        configurations["INITIAL_NUMBER_OF_BUNDLES_IN_PHONOTACTIC_CONSTRAINT"] = 1
        configurations["MIN_FEATURE_BUNDLES_IN_PHONOTACTIC_CONSTRAINT"] = 1
        configurations["MAX_FEATURE_BUNDLES_IN_PHONOTACTIC_CONSTRAINT"] = float("INF")
        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 100
        configurations["MAX_NUMBER_OF_CONSTRAINTS_IN_CONSTRAINT_SET"] = float("INF")
        configurations["RESTRICTION_ON_ALPHABET"] = True

        configurations["DEBUG_LOGGING_INTERVAL"] = 50
        self.unit_tests_log_file_name = "../../logging/{}_td_kg_aiueo_aspiration_and_lengthening_400_INF_INF_{}.txt".format(platform.node(), simulation_number)
        self._set_up_logging()
        configurations["CORPUS_DUPLICATION_FACTOR"] = 1
        self.feature_table = FeatureTable.load(get_feature_table_fixture("td_kg_aiueo_aspiration_and_lengthening_feature_table.json"))
        corpus = Corpus.load(get_corpus_fixture("td_kg_aiueo_aspiration_and_lengthening_400_corpus.txt"))
        self.constraint_set = ConstraintSet.load(get_constraint_set_fixture("faith_constraint_set.json"),
                                                  self.feature_table)
        self.lexicon = Lexicon(corpus.get_words(), self.feature_table)
        self.grammar = Grammar(self.feature_table, self.constraint_set, self.lexicon)
        self.data = corpus.get_words()
        self.traversable_hypothesis = TraversableGrammarHypothesis(self.grammar, self.data)
        def desired_lexicon_indicator_function(words):
            number_of_long_vowels = sum([word.count(":") for word in words])
            number_of_aspirated_consonants = sum([word.count("h") for word in words])
            combined_number = number_of_long_vowels + number_of_aspirated_consonants
            return "number of long vowels and aspirated consonants in lexicon: {} (long vowels = {}, " \
                   "aspirated consonants = {})".format(combined_number, number_of_long_vowels,
                                                       number_of_aspirated_consonants)

        def convert_corpus_word_to_target_word(word):
            return word.replace('h', '').replace(':', '')

        target_energy = self.get_target_hypothesis_energy(self.feature_table, "td_kg_ai_aspiration_and_lengthening_target_constraint_set.json", corpus,
                                   convert_corpus_word_to_target_word_function=convert_corpus_word_to_target_word)
        #391689

        self.simulated_annealing = SimulatedAnnealing(self.traversable_hypothesis,
                                                      target_lexicon_indicator_function=desired_lexicon_indicator_function,
                                                      sample_target_lexicon=["ti", "ta", "ki", "ka", "id", "ad", "ig", "ag", "tu", "te"],
                                                      sample_target_outputs=["thi", "tha", "khi", "kha", "i:d", "a:d", "i:g", "a:g", "thu", "the"],
                                                      target_energy=target_energy)

    def test_run(self):
        self.simulated_annealing.run()

    def _set_up_logging(self):
        if os.path.exists(self.unit_tests_log_file_name):
            raise ValueError("log name already exits")

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        file_log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s', "%Y-%m-%d %H:%M:%S")
        dirname, filename = split(abspath(__file__))
        unit_tests_log_path = normpath(join(dirname, self.unit_tests_log_file_name))
        file_log_handler = logging.FileHandler(unit_tests_log_path, mode='w')
        file_log_handler.setFormatter(file_log_formatter)
        logger.addHandler(file_log_handler)


if __name__ == '__main__':
    simulation_number = sys.argv[1]
    sys.argv = sys.argv[:1] # leave only sys.argv[0] as sys.argv
    unittest.main()