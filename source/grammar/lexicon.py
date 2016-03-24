#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

from random import choice, randint
import logging
from math import log, ceil
import codecs
from ast import literal_eval

from unicode_mixin import UnicodeMixin


from grammar.feature_table import Segment
from transducer import CostVector, Arc, State, Transducer, NULL_SEGMENT, JOKER_SEGMENT
from randomization_tools import get_weighted_list
from otml_configuration_manager import OtmlConfigurationManager, OtmlConfigurationError



logger = logging.getLogger(__name__)
configurations = OtmlConfigurationManager.get_instance()
if configurations is None:
    raise OtmlConfigurationError("OtmlConfigurationManager was not initialized")


word_transducers = dict()

class Word(UnicodeMixin, object):
    __slots__ = ["word_string", "feature_table", "segments"]
    def __init__(self, word_string, feature_table):
        """
        word_string and segment should be in sync at any time

        """
        self.word_string = word_string
        self.feature_table = feature_table
        self.segments = [Segment(char, self.feature_table) for char in self.word_string]

    def change_segment(self):
        """changing the word_string and therefore the segments composing it
           and making sure the new segment is not identical to segment being replaced"""
        logging.debug("change_segment")
        word_string_list = list(self.word_string)  # Making a mutable list from immutable string
        index_of_change = randint(0, len(self.word_string)-1)
        old_segment = word_string_list[index_of_change]

        segment_options_list = self.feature_table.get_alphabet()
        segment_options_list.remove(old_segment)  # Making sure that the new segment is not identical to segment being replaced

        if not segment_options_list:  # there are no change candidates
            return False

        new_segment = choice(segment_options_list)
        word_string_list[index_of_change] = new_segment
        new_word_string = ''.join(word_string_list)
        self._set_word_string(new_word_string)
        return True

    @staticmethod
    def is_appropriate(word_string):
        # for forbidden_sequence in ["'p", "'t", "'k"]:
        #     if forbidden_sequence in word_string:
        #         return False
        return True


    def insert_segment(self, segment_to_insert):
        logging.debug("insert_segment")
        old_word_string = self.word_string
        index_of_insertion = randint(0, len(self.word_string))
        new_word_string = self.word_string[:index_of_insertion] + segment_to_insert + \
                          self.word_string[index_of_insertion:]

        if self.is_appropriate(new_word_string):
            self._set_word_string(new_word_string)
            #logger.info("insert_segment: put {} in {} (at position {}) ".format(segment_to_insert, new_word_string,
            #                                                               index_of_insertion))
            return True
        else:
            return False


    def delete_segment(self):
        logging.debug("delete_segment")
        old_word_string = self.word_string
        index_of_deletion = randint(0, len(self.word_string)-1)
        new_word_string = self.word_string[:index_of_deletion] + self.word_string[index_of_deletion+1:]
        if self.is_appropriate(new_word_string):
            self._set_word_string(new_word_string)
           #print("delete segment: {} -> {}".format(old_word_string, new_word_string))
            return True
        else:
            return False

    def _set_word_string(self, new_word_string):
        self.word_string = new_word_string
        self.segments = [Segment(char, self.feature_table) for char in self.word_string]

    def get_transducer(self):
        word_key = str(self)
        if word_key in word_transducers:
            return word_transducers[word_key]
        else:
            transducer = self._make_transducer()
            word_transducers[word_key] = transducer
            return transducer


    def _make_transducer(self):
        segments = self.feature_table.get_segments()
        transducer = Transducer(segments, length_of_cost_vectors=0)
        word_segments = self.get_segments()
        n = len(self.word_string)
        states = [State("q{}".format(i), i) for i in range(n+1)]
        for i, state in enumerate(states):
            transducer.add_state(state)
            transducer.add_arc(Arc(state, NULL_SEGMENT, JOKER_SEGMENT, CostVector.get_empty_vector(), state))
            if i != n:
                transducer.add_arc(Arc(states[i], word_segments[i], JOKER_SEGMENT, CostVector.get_empty_vector(), states[i+1]))

        transducer.initial_state = states[0]
        transducer.add_final_state(states[n])
        return transducer

    def get_encoding_length(self):
        return sum(segment.get_encoding_length() for segment in self.get_segments()) + 1

    def get_segments(self):
        return self.segments

    @staticmethod
    def clear_caching():
        global word_transducers
        word_transducers = dict()

    def __unicode__(self):
        return self.word_string

    def __len__(self):
        return len(self.word_string)

    def __eq__(self, other):
        return self.word_string == other.word_string

    def __hash__(self):
        return hash(self.word_string)


class Lexicon(UnicodeMixin, object):

    def __init__(self, input_words, feature_table):
        """
        input_words is either a list of words or a file than contains a list of words
        """
        if type(input_words) is list:
            string_words = input_words
        else:
            string_words = get_words_from_file(input_words)
        self.words = [Word(word_string, feature_table) for word_string in string_words]
        self.feature_table = feature_table

    def make_mutation(self):
        """
        rtype: boolean - the mutation success
        """
        mutation_weights = [(self._insert_segment, configurations["INSERT_SEGMENT_WEIGHT"]),
                            (self._delete_segment, configurations["DELETE_SEGMENT_WEIGHT"]),
                            (self._change_segment, configurations["CHANGE_SEGMENT_WEIGHT"])]

        weighted_mutation_function_list = get_weighted_list(mutation_weights)
        return choice(weighted_mutation_function_list)()


    def _change_segment(self):
        return choice(self.words).change_segment()

    def _insert_segment(self):
        segment_to_insert = self.feature_table.get_random_segment()
        n = len(self.words)
        index_of_word_to_change = randint(0, n)
        if index_of_word_to_change == n:
            w = Word(segment_to_insert, self.feature_table)  # create a new monosegmental word
            self.words.append(w)
            return True
        else:
            return self.words[index_of_word_to_change].insert_segment(segment_to_insert)

    def _delete_segment(self):
        selected_word = choice(self.words)
        if len(selected_word) == 1:
            self.words.remove(selected_word)
            return True
        else:
            return selected_word.delete_segment()

    def get_encoding_length(self):
        if configurations["RESTRICTION_ON_ALPHABET"]:
            alphabet_size = len(self.feature_table.get_alphabet())
            restricted_alphabet_size = len(self.get_distinct_segments())
            number_of_bits = ceil(log(alphabet_size + 1, 2))
            restriction_set_length = number_of_bits * (restricted_alphabet_size + 1)
            number_of_bits = ceil(log(restricted_alphabet_size + 1, 2))
            lexicon_length = number_of_bits * (sum((len(word) + 1) for word in self.words) + 1)
            return restriction_set_length + lexicon_length
        else:
            number_of_bits = 2
            return number_of_bits * (sum(word.get_encoding_length() for word in self.words) + 1)


    def get_distinct_segments(self):
        distinct_segments = set()
        for word in self.words:
            distinct_segments = distinct_segments | set(word.get_segments())
        return distinct_segments

    def get_words(self):
        return self.words

    def get_number_of_distinct_words(self):
        return len(set(self.words))

    def _get_number_of_segments(self):
        return sum([len(word) for word in self.words])

    def __unicode__(self):
        if configurations["LOG_LEXICON_WORDS"]:
            return "Lexicon, number of words: {0}, number of segments: {1}, {2}".format(len(self.words),
                                                                     self._get_number_of_segments(),
                                                                     [str(w.word_string) for w in self.words])
        else:
            return "Lexicon, number of words: {0}, number of segments: {1}".format(len(self.words),
                                                                         self._get_number_of_segments())

    # we can optimize this by creating dict
    def __getitem__(self, item):
        return self.words[item].get_segments()

    def __len__(self):
        return len(self.words)

def get_words_from_file(corpus_file_name):
        with codecs.open(corpus_file_name, "r") as f:
            corpus_string = f.read()

        if "[" not in corpus_string:
            words = corpus_string.split()
        else:
            words = literal_eval(corpus_string)

        return words