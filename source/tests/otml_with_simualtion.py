import sys
import os
import logging
import platform
from os.path import split, join, abspath


#TODO this lines are for running test_otml outside pycharm
FILE_PATH = os.path.abspath(os.path.join(__file__, '..'))
PROJECT_PATH = os.path.abspath(os.path.join(FILE_PATH, '../..//'))
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





def run_simulation(configurations_tuples, simulation_number, log_file_template, feature_table_file_name, corpus_file_name, constraint_set_file_name,
                  sample_target_lexicon=None, sample_target_outputs=None, target_lexicon_indicator_function=None,
                  target_constraint_set_file_name=None, target_lexicon_file_name=None, convert_corpus_word_to_target_word_function=None,
                  initial_lexicon_file_name=None):

    for configurations_tuple in configurations_tuples:
        configurations[configurations_tuple[0]] = configurations_tuple[1]

    log_file_name = log_file_template.format(platform.node(), simulation_number)
    dirname, filename = split(abspath(__file__))
    log_file_path = join(dirname, "../logging/", log_file_name)

    # if os.path.exists(log_file_path):
    #     raise ValueError("log name already exits")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s', "%Y-%m-%d %H:%M:%S")
    file_log_handler = logging.FileHandler(log_file_path, mode='w')
    file_log_handler.setFormatter(file_log_formatter)
    logger.addHandler(file_log_handler)

    feature_table = FeatureTable.load(get_feature_table_fixture(feature_table_file_name))
    corpus = Corpus.load(get_corpus_fixture(corpus_file_name))
    constraint_set = ConstraintSet.load(get_constraint_set_fixture(constraint_set_file_name),
                                              feature_table)

    if initial_lexicon_file_name:
        corpus_for_lexicon = Corpus.load(get_corpus_fixture(initial_lexicon_file_name))
        lexicon = Lexicon(corpus_for_lexicon.get_words(), feature_table)
    else:
        lexicon = Lexicon(corpus.get_words(), feature_table)
    grammar = Grammar(feature_table, constraint_set, lexicon)
    data = corpus.get_words()
    traversable_hypothesis = TraversableGrammarHypothesis(grammar, data)

    keyargs_dict = {}
    
    if sample_target_lexicon and sample_target_outputs and target_lexicon_indicator_function:
        keyargs_dict["sample_target_lexicon"] = sample_target_lexicon
        keyargs_dict["sample_target_outputs"] = sample_target_outputs
        keyargs_dict["target_lexicon_indicator_function"] = target_lexicon_indicator_function

    if target_constraint_set_file_name and (target_lexicon_file_name or convert_corpus_word_to_target_word_function):
        target_energy = get_target_hypothesis_energy(feature_table, target_constraint_set_file_name, corpus,
                                                     target_lexicon_file_name, convert_corpus_word_to_target_word_function)
        keyargs_dict["target_energy"] = target_energy

    simulated_annealing = SimulatedAnnealing(traversable_hypothesis, **keyargs_dict)
    simulated_annealing.run()

def get_target_hypothesis_energy(feature_table, target_constraint_set_file_name, corpus,
                                 target_lexicon_file_name=None,
                                 convert_corpus_word_to_target_word_function=None):
    constraint_set = ConstraintSet.load(get_constraint_set_fixture(target_constraint_set_file_name), feature_table)
    if target_lexicon_file_name:
        lexicon = Lexicon(get_corpus_fixture(target_lexicon_file_name), feature_table)
    elif convert_corpus_word_to_target_word_function:
        lexicon_words = [convert_corpus_word_to_target_word_function(word) for word in corpus]
        lexicon = Lexicon(lexicon_words, feature_table)
    grammar = Grammar(feature_table, constraint_set, lexicon)
    traversable_hypothesis = TraversableGrammarHypothesis(grammar, corpus)
    return traversable_hypothesis.get_energy()