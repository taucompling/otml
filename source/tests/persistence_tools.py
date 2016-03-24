from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import split, abspath, join
from os import listdir, remove

from grammar.feature_table import FeatureTable
from grammar.constraint_set import ConstraintSet
from corpus import Corpus


import pickle

from six import PY3, StringIO

tests_dir_path, filename = split(abspath(__file__))

#dot
dot_files_folder_path = join(tests_dir_path, "dot_files")


def clear_dot_folder():
    dot_files = [dot_file_name for dot_file_name in listdir(dot_files_folder_path) if dot_file_name.endswith(".dot")]
    for dot_file_name in dot_files:
        remove(join(dot_files_folder_path, dot_file_name))

def write_to_dot_to_file(transducer, file_name):
            open(join(dot_files_folder_path, file_name+".dot"), "w").write(transducer.dot_representation())

#pickle

pickled_results_folder_path = join(tests_dir_path, "pickled_results")

if PY3:
    pickled_results_folder_path = join(pickled_results_folder_path, "py3.3")
else:
    pickled_results_folder_path = join(pickled_results_folder_path, "py2.7")

def write_pickle(obj, file_name):
    file = open(_get_pickle_full_path(file_name), "wb")
    pickle.dump(obj, file)
    file.close()


def get_pickle(file_name):
    file = open(_get_pickle_full_path(file_name), "rb")
    obj = pickle.load(file)
    file.close()
    return obj


def _get_pickle_full_path(file_name):
    return join(pickled_results_folder_path, file_name+".pkl")


#fixtures

fixtures_dir_path = join(tests_dir_path, "fixtures")

constraint_sets_dir_path = join(fixtures_dir_path, "constraint_sets")
corpora_dir_path = join(fixtures_dir_path, "corpora")
feature_table_dir_path = join(fixtures_dir_path, "feature_table")


def get_constraint_set_fixture(constraint_set_file_name):
    return join(constraint_sets_dir_path, constraint_set_file_name)


def get_corpus_fixture(corpus_file_name):
    return join(corpora_dir_path, corpus_file_name)


def get_feature_table_fixture(feature_table_file_name):
    return join(feature_table_dir_path, feature_table_file_name)


def get_feature_table_by_fixture(feature_table_file_name):
    return FeatureTable.load(get_feature_table_fixture(feature_table_file_name))


def get_corpus_by_fixture(corpus_file_name):
    return Corpus.load(get_corpus_fixture(corpus_file_name))



def clear_modules_caching():
    """ clears caching dictionaries of modules in order to allow testing of
        different hypothesis
    """
    import grammar.lexicon
    import grammar.constraint
    import grammar.constraint_set
    import grammar.grammar

    del grammar.lexicon.word_transducers
    del grammar.constraint.constraint_transducers
    del grammar.constraint_set.constraint_set_transducers
    del grammar.grammar.grammar_transducers

    grammar.lexicon.word_transducers = dict()
    grammar.constraint.constraint_transducers = dict()
    grammar.constraint_set.constraint_set_transducers = dict()
    grammar.grammar.grammar_transducers = dict()


def get_module_caching_status():
    import grammar.lexicon
    import grammar.constraint
    import grammar.constraint_set
    import grammar.grammar

    values_str_io = StringIO()

    print("Module caching status:", end="\n", file=values_str_io)

    print("word_transducers: {}".format(len(grammar.lexicon.word_transducers)), end="\n", file=values_str_io)
    print("constraint_transducers: {}".format(len(grammar.constraint.constraint_transducers)), end="\n", file=values_str_io)
    print("constraint_set_transducers: {}".format(len(grammar.constraint_set.constraint_set_transducers)), end="\n", file=values_str_io)
    print("grammar_transducers: {}".format(len(grammar.grammar.grammar_transducers)), end="\n", file=values_str_io)

    return values_str_io.getvalue()



