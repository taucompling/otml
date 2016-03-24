#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

from six import iterkeys
import logging

from random import choice
from grammar.lexicon import Word
from transducer import Transducer
from transducers_optimization_tools import optimize_transducer_grammar_for_word, make_optimal_paths
from unicode_mixin import UnicodeMixin
from randomization_tools import get_weighted_list
from otml_configuration_manager import OtmlConfigurationManager, OtmlConfigurationError
from debug_tools import write_to_dot, timeit



logger = logging.getLogger(__name__)
configurations = OtmlConfigurationManager.get_instance()
if configurations is None:
    raise OtmlConfigurationError("OtmlConfigurationManager was not initialized")


outputs_by_constraint_set_and_word = dict()

grammar_transducers = dict()



class GrammarParseError(Exception):
    pass


class Grammar(UnicodeMixin, object):
    """This class represents an Optimality Theory grammar."""
    def __init__(self, feature_table, constraint_set, lexicon):
        self.feature_table = feature_table
        self.constraint_set = constraint_set
        self.lexicon = lexicon

    def get_encoding_length(self):
        return self.constraint_set.get_encoding_length() + self.lexicon.get_encoding_length()

    def make_mutation(self):
        mutation_weights = [(self.lexicon, configurations["LEXICON_SELECTION_WEIGHT"]),
                            (self.constraint_set, configurations["CONSTRAINT_SET_SELECTION_WEIGHT"])]

        weighted_mutatable_object_list = get_weighted_list(mutation_weights)
        object_to_mutate = choice(weighted_mutatable_object_list)
        mutation_result = object_to_mutate.make_mutation()
        return mutation_result

    def get_transducer(self):
            constraint_set_key = str(self.constraint_set) # constraint_set is the identifier of the grammar transducer
            if constraint_set_key in grammar_transducers:
                return grammar_transducers[constraint_set_key]
            else:
                transducer = self._make_transducer()
                grammar_transducers[constraint_set_key] = transducer
                return transducer

    def _make_transducer(self):
        constraint_set_transducer = self.constraint_set.get_transducer()
        try:
            make_optimal_paths_result = make_optimal_paths(constraint_set_transducer, self.feature_table)
        except Exception as ex:
            logger.error("make_optimal_paths failed. transducer dot are being printed")
            #write_to_dot(constraint_set_transducer,"constraint_set_transducer")
            for constraint in self.constraint_set.constraints:
                pass
                #write_to_dot(constraint.get_transducer(), str(constraint))
            raise ex

        return make_optimal_paths_result

    def generate(self, word):
        constraint_set_and_word_key = str(self.constraint_set) + str(word)
        if constraint_set_and_word_key in outputs_by_constraint_set_and_word:
            return outputs_by_constraint_set_and_word[constraint_set_and_word_key]
        else:
            outputs = self._get_outputs(word)
            outputs_by_constraint_set_and_word[constraint_set_and_word_key] = outputs
            return outputs


    def _get_outputs(self, word):
        grammar_transducer = self.get_transducer()
        word_transducer = word.get_transducer()
        write_to_dot(grammar_transducer, "grammar_transducer")
        write_to_dot(word_transducer, "word_transducer")
        intersected_transducer = Transducer.intersection(word_transducer,    # a transducer with NULLs on inputs and JOKERs on outputs
                                                         grammar_transducer) # a transducer with segments on inputs and sets on outputs

        intersected_transducer.clear_dead_states()
        intersected_transducer = optimize_transducer_grammar_for_word(word, intersected_transducer)
        outputs = intersected_transducer.get_range()
        return outputs


    def get_all_outputs_grammar(self, new_string_word_list=[]):
        """
        used for testing
        """
        outputs = list()
        if new_string_word_list:
            words = [Word(word, self.feature_table) for word in new_string_word_list]
        else:
            words = self.lexicon.get_words()

        for word in words:
            outputs.extend(self._get_outputs(word))

        return outputs


    def __unicode__(self):
        return "Grammar with [{0}]; and [{1}]".format(self.constraint_set, self.lexicon)

    def __hash__(self):
        return hash(str(self))

    @staticmethod
    def clear_caching():
            global outputs_by_constraint_set_and_word
            outputs_by_constraint_set_and_word = dict()

            global grammar_transducers
            grammar_transducers = dict()