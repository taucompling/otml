"""
This is the entry point of the otml project
The working directory for activating this file should be "otml"

"""
#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals


import sys
import platform
from os import getcwd
from os.path import dirname, join, split, basename, splitext, exists
from optparse import OptionParser
from otml_configuration_manager import OtmlConfigurationManager, OtmlConfigurationError
import codecs
from base64 import urlsafe_b64encode
from uuid import uuid4

class OtmlError(Exception):
    pass

#--configuration simulations/bb/bb_configuration.json


def main():
    parser = OptionParser() #test
    parser.add_option("--configuration", dest="configuration_file_relative_path")
    parser.add_option("--sub-configuration", dest="sub_configuration_file_relative_path")
    parser.add_option("--from_middle", dest="middle_file_relative_path")
    (options, args) = parser.parse_args()

    if options.configuration_file_relative_path and options.middle_file_relative_path:
        raise OtmlError("can not handle both: --configuration and --from_middle")
    elif not (options.configuration_file_relative_path or options.middle_file_relative_path):
        raise OtmlError("must have one: --configuration or --from_middle")

    current_dir = getcwd()
    current_working_directory_name = basename(current_dir)
    #validate current directory
    if current_working_directory_name != "otml":
        raise OtmlError("this file should be called from the otml directory")


    if options.middle_file_relative_path:
        raise NotImplementedError

    if options.configuration_file_relative_path:
        configuration_file_path = join(current_dir, options.configuration_file_relative_path)
        configuration_files_dir_path = dirname(configuration_file_path)
        configuration_files_dir_name = basename(configuration_files_dir_path)

        #load configurations
        configuration_json_str = codecs.open(configuration_file_path, 'r').read()
        OtmlConfigurationManager(configuration_json_str)
        configurations = OtmlConfigurationManager.get_instance()

        if options.sub_configuration_file_relative_path:
            pass

        #validate simulation name
        if configuration_files_dir_name != configurations["SIMULATION_NAME"]:
            raise OtmlConfigurationError("SIMULATION_NAME should match configuration file containing directory")

        constraint_set_file_name = configurations["CONSTRAINT_SET_FILE_NAME"]
        feature_table_file_name = configurations["FEATURE_TABLE_FILE_NAME"]
        corpus_file_name = configurations["CORPUS_FILE_NAME"]

        #check existence of data files
        constraint_set_file_path = join(configuration_files_dir_path, constraint_set_file_name)
        if not exists(constraint_set_file_path):
            raise OtmlConfigurationError("CONSTRAINT_SET_FILE_NAME does not exist where it should")

        feature_table_file_path = join(configuration_files_dir_path, feature_table_file_name)
        if not exists(feature_table_file_path):
            raise OtmlConfigurationError("FEATURE_TABLE_FILE_NAME does not exist where it should")

        corpus_file_path = join(configuration_files_dir_path, corpus_file_name)
        if not exists(corpus_file_path):
            raise OtmlConfigurationError("CORPUS_FILE_NAME does not exist where it should")

        load_modules_and_run(feature_table_file_path, corpus_file_path, constraint_set_file_path,
                             configuration_files_dir_path)


def load_modules_and_run(feature_table_file_path, corpus_file_path, constraint_set_file_path,
                         configuration_files_dir_path):
    #TODO finish the loading from file
    #file, path, desc = imp.find_module("bb", [configuration_files_dir_path])
    #
    #module = imp.load_module("bb", file, path, desc)
    #print(type(module))
    #print(dir(module))
    #module.print_()

    #importing in here because it is after OtmlConfigurationManager initialization
    from grammar.lexicon import Lexicon
    from grammar.feature_table import FeatureTable
    from grammar.constraint_set import ConstraintSet
    from grammar.grammar import Grammar
    from traversable_grammar_hypothesis import TraversableGrammarHypothesis
    from corpus import Corpus
    from simulated_annealing import SimulatedAnnealing

    feature_table = FeatureTable.load(feature_table_file_path)
    corpus = Corpus.load(corpus_file_path)
    constraint_set = ConstraintSet.load(constraint_set_file_path, feature_table)
    lexicon = Lexicon(corpus.get_words(), feature_table)
    grammar = Grammar(feature_table, constraint_set, lexicon)
    data = corpus.get_words()
    traversable_hypothesis = TraversableGrammarHypothesis(grammar, data)
    simulated_annealing = SimulatedAnnealing(traversable_hypothesis)
    simulated_annealing.run()




def get_log_name():
    short_random_identifier = urlsafe_b64encode(uuid4().bytes)[:4].decode("utf-8")  # length 4 of base64
                                                                                    # is more than 16M possibilities
    log_name = "_".join()




def create_simulation_directory(simulation_name, sub_name):
    computer_name = platform.node()
    #logging




if __name__ == "__main__":
    main()
    #get_log_name()