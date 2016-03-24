#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals


import sys
import os
import unittest
import logging
import platform
from os.path import split, join, normpath, abspath

simulation_number = 1

log_file_name = "../../logging/{}_french_deletion_50_{}.txt"

FILE_PATH = os.path.abspath(os.path.join(__file__, '..'))
PROJECT_PATH = os.path.abspath(os.path.join(FILE_PATH, '../../'))
os.chdir(FILE_PATH)
sys.path.append(PROJECT_PATH)


import logging
from tests.otml_configuration_for_testing import configurations
from grammar.lexicon import Lexicon
from grammar.feature_table import FeatureTable
from grammar.constraint_set import ConstraintSet
from grammar.grammar import Grammar
from traversable_grammar_hypothesis import TraversableGrammarHypothesis
from corpus import Corpus
from simulated_annealing import SimulatedAnnealing
from tests.persistence_tools import get_constraint_set_fixture, get_feature_table_fixture, get_corpus_fixture


class TestOtmlWithFrenchDeletion(unittest.TestCase):
    def setUp(self):
        self._set_up_logging()
        configurations["CORPUS_DUPLICATION_FACTOR"] = 50
        self.feature_table = FeatureTable.load(get_feature_table_fixture("french_deletion_feature_table.json"))
        corpus = Corpus.load(get_corpus_fixture("french_deletion_corpus.txt"))
        self.constraint_set = ConstraintSet.load(get_constraint_set_fixture("french_deletion_constraint_set.json"),
                                                  self.feature_table)
        self.lexicon = Lexicon(get_corpus_fixture("french_deletion_corpus.txt"), self.feature_table)
        self.grammar = Grammar(self.feature_table, self.constraint_set, self.lexicon)
        self.data = corpus.get_words()
        self.traversable_hypothesis = TraversableGrammarHypothesis(self.grammar, self.data)
        self.simulated_annealing = SimulatedAnnealing(self.traversable_hypothesis)


    run_test = True
    @unittest.skipUnless(run_test, "long running test skipped")
    def test_run(self):
        configurations["CONSTRAINT_SET_MUTATION_WEIGHTS"] = {
            "insert_constraint": 0,
            "remove_constraint": 0,
            "demote_constraint": 1,
            "insert_feature_bundle_phonotactic_constraint": 0,
            "remove_feature_bundle_phonotactic_constraint": 0,
            "augment_feature_bundle": 0}

        configurations["LEXICON_MUTATION_WEIGHTS"]= {
            "insert_segment": 1,
            "delete_segment": 1,
            "change_segment": 0}

        configurations["DATA_ENCODING_LENGTH_MULTIPLIER"] = 1
        configurations["INITIAL_TEMPERATURE"] = 100
        configurations["COOLING_PARAMETER"] = 0.9999
        configurations["RESTRICTION_ON_ALPHABET"] = False


        configurations["DEBUG_LOGGING_INTERVAL"] = 50

        number_of_steps_performed, hypothesis = self.simulated_annealing.run()

    def _set_up_logging(self):
        unit_tests_log_file_name = log_file_name.format(platform.node(), simulation_number)

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


if __name__ == '__main__':
    unittest.main()