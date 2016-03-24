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
    ("RANDOM_SEED", True),
    ("INITIAL_TEMPERATURE", 0.01),
    ("COOLING_PARAMETER", 0.9997),
    ("INITIAL_NUMBER_OF_BUNDLES_IN_PHONOTACTIC_CONSTRAINT", 1),
    ("MIN_FEATURE_BUNDLES_IN_PHONOTACTIC_CONSTRAINT", 1),
    ("MAX_FEATURE_BUNDLES_IN_PHONOTACTIC_CONSTRAINT", float("INF")),
    ("DATA_ENCODING_LENGTH_MULTIPLIER", 100),
    ("MAX_NUMBER_OF_CONSTRAINTS_IN_CONSTRAINT_SET", float("INF")),
    ("RESTRICTION_ON_ALPHABET", True),
    ("DEBUG_LOGGING_INTERVAL", 50),
    ("CORPUS_DUPLICATION_FACTOR", 1),
    ("LOG_LEXICON_WORDS", True),
    ("THRESHOLD", 10**-4)
]


log_file_template = "{}_tpk_aiu_yimas_100_no_cicic_from_middle_{}.txt"

feature_table_file_name = "yimas_tpk_aiu_feature_table.csv"
corpus_file_name = "yimas_tpk_aiu_no_cicic_corpus.txt"
constraint_set_file_name = "yimas_tpk_aiu_from_middle_constraint_set.txt"
initial_lexicon_file_name = "yimas_tpk_aiu_no_cicic_initial_lexicon.txt"

def target_lexicon_indicator_function(words):
    return "number of stress segments: {}".format(sum([word.count("'") for word in words]))

sample_target_lexicon = ["ti", "katu"]
sample_target_outputs = ["t'i", "k'atu"]

target_constraint_set_file_name = "yimas_tpk_aiu_target_constraint_set.txt"
target_lexicon_file_name = "yimas_tpk_aiu_no_cicic_target_lexicon.txt"


if __name__ == '__main__':
    if len(sys.argv) > 1:
        simulation_number = sys.argv[1]

    run_simulation(configurations_tuples, simulation_number, log_file_template, feature_table_file_name,
                   corpus_file_name, constraint_set_file_name,
                   sample_target_lexicon=sample_target_lexicon,
                   sample_target_outputs=sample_target_outputs,
                   target_lexicon_indicator_function=target_lexicon_indicator_function,
                   target_constraint_set_file_name=target_constraint_set_file_name,
                   target_lexicon_file_name=target_lexicon_file_name,
                   convert_corpus_word_to_target_word_function=None,
                   initial_lexicon_file_name=initial_lexicon_file_name)