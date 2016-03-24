#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals
import unittest
import os
import sys

from six import StringIO

from tests.otml_configuration_for_testing import configurations
from corpus import Corpus
from grammar.lexicon import Word
from grammar.feature_table import FeatureTable
from tests.persistence_tools import  get_corpus_fixture, get_feature_table_fixture


class TestCorpus(unittest.TestCase):

    def setUp(self):
        self.feature_table = FeatureTable.load(get_feature_table_fixture("feature_table.json"))
        self.corpus = Corpus.load(get_corpus_fixture("corpus.txt"))

    def test_number_of_words(self):
        self.assertEqual(len(self.corpus), 82)

    def test_get_item(self):
        self.assertEqual(self.corpus[3], "bab")
        self.assertEqual(self.corpus[5], "aab")

    def test_unicode_str(self):
        self.assertEqual(str(self.corpus), "Corpus with 82 words")
        if sys.version_info < (3, 0):
            self.assertEqual(unicode(self.corpus), "Corpus with 82 words")

    def test_get_list_corpus(self):
        corpus = Corpus.load(get_corpus_fixture("test_list_corpus.txt"))
        self.assertEqual(len(corpus), 5)


    def test_print_corpus(self):
        self.out = StringIO()
        self.saved_stdout = sys.stdout
        sys.stdout = self.out      # temporarily take over sys.stdout
        self.corpus.print_corpus()
        self.assertEqual(len(self.out.getvalue().split("\n")), 9)
        self.out.close()
        sys.stdout = self.saved_stdout
