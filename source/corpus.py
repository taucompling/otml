#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

import textwrap

from unicode_mixin import UnicodeMixin
from grammar.lexicon import Word, get_words_from_file
from otml_configuration_manager import OtmlConfigurationManager, OtmlConfigurationError

configurations = OtmlConfigurationManager.get_instance()
if configurations is None:
    raise OtmlConfigurationError("OtmlConfigurationManager was not initialized")

class Corpus(UnicodeMixin, object):

    def __init__(self, string_words):
        self.words = string_words

    @classmethod
    def load(cls, corpus_file_name):

        words = get_words_from_file(corpus_file_name)
        duplication_factor = configurations["CORPUS_DUPLICATION_FACTOR"]
        n = len(words)
        duplication_factor_int = int(duplication_factor)
        duplication_factor_fraction = duplication_factor - int(duplication_factor)

        words_after_duplication = words * duplication_factor_int
        words_after_duplication.extend(words[:int(n*duplication_factor_fraction)])

        return cls(words_after_duplication)


    def __unicode__(self):
        return "Corpus with {0} words".format(len(self))

    def __getitem__(self, item):
        return self.words.__getitem__(item)

    def get_words(self):
        return self.words[:]

    def get_word_objects(self, feature_table):
        return [Word(word_string, feature_table) for word_string in self.words()]

    def __len__(self):
        return len(self.words)

    def print_corpus(self):
        print("Corpus ({0} words):".format(len(self)))
        lines = textwrap.wrap(" ".join([word for word in self.words]), width=80)
        for line in lines:
            print(line)

