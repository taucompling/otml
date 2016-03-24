import sys
from tests.otml_with_simualtion import run_simulation


simulation_number = 1
configurations_tuples = [
    ("CONSTRAINT_SET_MUTATION_WEIGHTS", {
            "insert_constraint": 1,
            "remove_constraint": 1,
            "demote_constraint": 1,
            "insert_feature_bundle_phonotactic_constraint": 1,
            "remove_feature_bundle_phonotactic_constraint": 1,
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
    ("INITIAL_TEMPERATURE", 100),
    ("COOLING_PARAMETER", 0.999985),
    ("INITIAL_NUMBER_OF_BUNDLES_IN_PHONOTACTIC_CONSTRAINT", 1),
    ("MIN_FEATURE_BUNDLES_IN_PHONOTACTIC_CONSTRAINT", 1),
    ("MAX_FEATURE_BUNDLES_IN_PHONOTACTIC_CONSTRAINT", float("INF")),
    ("DATA_ENCODING_LENGTH_MULTIPLIER", 100),
    ("MAX_NUMBER_OF_CONSTRAINTS_IN_CONSTRAINT_SET", float("INF")),
    ("RESTRICTION_ON_ALPHABET", True),
    ("DEBUG_LOGGING_INTERVAL", 50),
    ("CORPUS_DUPLICATION_FACTOR", 1)
]

feature_table_file_name = "td_aiu_aspiration_and_lengthening_feature_table.json"
corpus_file_name = "td_aiu_aspiration_and_lengthening_200_corpus.txt"
constraint_set_file_name = "faith_constraint_set.json"
log_file_template = "{}_td_aiu_aspiration_and_lengthening_200_INF_INF_{}.txt"


def target_lexicon_indicator_function(words):
    number_of_long_vowels = sum([word.count(":") for word in words])
    number_of_aspirated_consonants = sum([word.count("h") for word in words])
    combined_number = number_of_long_vowels + number_of_aspirated_consonants
    return "number of long vowels and aspirated consonants in lexicon: {} (long vowels = {}, " \
           "aspirated consonants = {})".format(combined_number, number_of_long_vowels,
                                               number_of_aspirated_consonants)

sample_target_lexicon=["ti", "ta", "id", "ad", "tu"]
sample_target_outputs=["thi", "tha", "i:d", "a:d", "thu"]


#target
def convert_corpus_word_to_target_word_function(word):
    return word.replace('h', '').replace(':', '')

target_constraint_set_file_name = "td_kg_ai_aspiration_and_lengthening_target_constraint_set.json"


if __name__ == '__main__':
    if len(sys.argv) > 1:
        simulation_number = sys.argv[1]

    run_simulation(configurations_tuples, simulation_number, log_file_template, feature_table_file_name,
                   corpus_file_name, constraint_set_file_name, sample_target_lexicon=sample_target_lexicon,
                   sample_target_outputs=sample_target_outputs,
                   target_lexicon_indicator_function=target_lexicon_indicator_function,
                   target_constraint_set_file_name=target_constraint_set_file_name,
                   target_lexicon_file_name=None,
                   convert_corpus_word_to_target_word_function=convert_corpus_word_to_target_word_function)
