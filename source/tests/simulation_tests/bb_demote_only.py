import sys
import os

FILE_PATH = os.path.abspath(os.path.join(__file__, '..'))
PROJECT_PATH = os.path.abspath(os.path.join(FILE_PATH, '../../'))
os.chdir(FILE_PATH)
sys.path.append(PROJECT_PATH)

from tests.otml_with_simualtion import run_simulation

simulation_number = 1
configurations_tuples = [
    ("CONSTRAINT_SET_MUTATION_WEIGHTS", {
            "insert_constraint": 0,
            "remove_constraint": 0,
            "demote_constraint": 1,
            "insert_feature_bundle_phonotactic_constraint": 0,
            "remove_feature_bundle_phonotactic_constraint": 0,
            "augment_feature_bundle": 0}),
    ("CONSTRAINT_INSERTION_WEIGHTS", {
            "Dep": 1,
            "Max": 1,
            "Ident": 0,
            "Phonotactic": 1}),
    ("LEXICON_MUTATION_WEIGHTS", {
            "insert_segment": 1,
            "delete_segment": 1,
            "change_segment": 0}),
    ("RANDOM_SEED", False),
    ("SEED", 3),
    ("INITIAL_TEMPERATURE", 20),
    ("COOLING_PARAMETER", 0.99),
    ("INITIAL_NUMBER_OF_BUNDLES_IN_PHONOTACTIC_CONSTRAINT", 1),
    ("MIN_FEATURE_BUNDLES_IN_PHONOTACTIC_CONSTRAINT", 1),
    ("MAX_FEATURE_BUNDLES_IN_PHONOTACTIC_CONSTRAINT", float("INF")),
    ("DATA_ENCODING_LENGTH_MULTIPLIER", 1),
    ("MAX_NUMBER_OF_CONSTRAINTS_IN_CONSTRAINT_SET", float("INF")),
    ("RESTRICTION_ON_ALPHABET", False),
    ("DEBUG_LOGGING_INTERVAL", 50),
    ("CORPUS_DUPLICATION_FACTOR", 1),
    ("LOG_LEXICON_WORDS", False)
]


log_file_template = "{}_bb_demote_only_{}.txt"

feature_table_file_name = "a_b_and_cons_feature_table.json"
corpus_file_name = "test_otml_with_demote_only_corpus.txt"
constraint_set_file_name = "test_bb_with_demote_only_constraint_set.json"


def target_lexicon_indicator_function(words):
    return "number of bab's: {}".format(sum([word.count("bab") for word in words]))

def convert_corpus_word_to_target_word_function(word):
    new_word = word
    while "bab" in new_word:
        new_word = new_word.replace("bab", "bb")
    return new_word

sample_target_lexicon=["bb", "abb"]
sample_target_outputs=["bab", "abab"]

target_constraint_set_file_name = "bb_demote_only_target_constraint_set.txt"


if __name__ == '__main__':
    if len(sys.argv) > 1:
        simulation_number = sys.argv[1]

    run_simulation(configurations_tuples, simulation_number, log_file_template, feature_table_file_name,
                   corpus_file_name, constraint_set_file_name,
                   sample_target_lexicon=sample_target_lexicon,
                   sample_target_outputs=sample_target_outputs,
                   target_lexicon_indicator_function=target_lexicon_indicator_function,
                   target_constraint_set_file_name=target_constraint_set_file_name,
                   target_lexicon_file_name=None,
                   convert_corpus_word_to_target_word_function=convert_corpus_word_to_target_word_function)