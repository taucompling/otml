from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
from copy import deepcopy

from tests.otml_configuration_for_testing import configurations
from grammar.lexicon import Word, Lexicon
from tests.stochastic_testcase import StochasticTestCase
from tests.persistence_tools import get_feature_table_by_fixture




class TestLexicon(StochasticTestCase):
    def setUp(self):
        self.feature_table = get_feature_table_by_fixture("feature_table.json")
        self.lexicon = Lexicon(['abb', 'bbaa'], self.feature_table)

    #lexicon tests:
    def test_lexicon(self):
        self.assertEqual(str(self.lexicon), "Lexicon, number of words: 2, number of segments: 7")
        self.assertEqual(str([str(s) for s in self.lexicon[0]]), "['Segment a[+, -]', 'Segment b[-, -]', 'Segment b[-, -]']")


    def test_lexicon_make_mutation(self):
        #print('\n'.join(sys.modules.keys()))
        pass
    #    original_lexicon = deepcopy(self.lexicon)
    #    self.lexicon.make_mutation()
    #    print(self.lexicon)
    #    print(_find_out_mutation_type(original_lexicon.words, self.lexicon.words))
    #
    #    params.lexicon_mutation_weights["insert_segment"] = 0
    #    params.lexicon_mutation_weights["delete_segment"] = 1
    #
    #    Lexicon.INSERT_SEGMENT_WEIGHT = 0
    #    Lexicon.DELETE_SEGMENT_WEIGHT = 1
    #    self.lexicon = Lexicon([['abb', 'bbaa']], self.feature_table)
    #    original_lexicon = deepcopy(self.lexicon)
    #    self.lexicon.make_mutation()
    #    print(self.lexicon)
    #    print(_find_out_mutation_type(original_lexicon.words, self.lexicon.words))


    def test_lexicon_change_segment(self):
        lexicon = Lexicon(['ab', 'ba'], self.feature_table) # 12 possible results
        lexicon_str1 = str(Lexicon(['ab', 'ca'], self.feature_table))
        lexicon_str2 = str(Lexicon(['ab', 'bd'], self.feature_table))
        lexicon_str3 = str(Lexicon(['db', 'ba'], self.feature_table))
        possible_results = [lexicon_str1, lexicon_str2, lexicon_str3]

        self.stochastic_object_method_testing(lexicon, "_change_segment", possible_results, num_of_tests=200,
                                              possible_result_threshold=5)

    def test_lexicon_insert_segment(self):
        lexicon = Lexicon(['ab', 'ba'], self.feature_table) # 18 possible results
        lexicon_str1 = str(Lexicon(['ab', 'cba'], self.feature_table))
        lexicon_str2 = str(Lexicon(['ab', 'baa'], self.feature_table))
        lexicon_str3 = str(Lexicon(['ab', 'ba', 'a'], self.feature_table))

        possible_results = [lexicon_str1, lexicon_str2, lexicon_str3]
        self.stochastic_object_method_testing(lexicon, "_insert_segment", possible_results, num_of_tests=400,
                                              possible_result_threshold=5, all_possible_result_flag=False)

    def test_lexicon_delete_segment(self):
        lexicon = Lexicon(['abb', 'a'], self.feature_table)

        lexicon_str1 = str(Lexicon(['abb'], self.feature_table))
        lexicon_str2 = str(Lexicon(['ab', 'a'], self.feature_table))
        lexicon_str3 = str(Lexicon(['bb', 'a'], self.feature_table))

        possible_results = [lexicon_str1, lexicon_str2, lexicon_str3]
        self.stochastic_object_method_testing(lexicon, "_delete_segment", possible_results, num_of_tests=100,
                                              possible_result_threshold=5, all_possible_result_flag=True)

    def test_lexicon_encoding_length(self):
        lexicon = Lexicon(['abb', 'a'], self.feature_table)
        self.assertEqual(lexicon.get_encoding_length(), 22)


    #word tests:
    def test_word(self):
        word = Word('abb', self.feature_table)
        self.assertEqual(str(word), 'abb')
        self.assertEqual(str([str(s) for s in word.get_segments()]), "['Segment a[+, -]', 'Segment b[-, -]', "
                                                                     "'Segment b[-, -]']")

    def test_word_change_segment(self):
        word = Word('ab', self.feature_table)

        word_str1 = str(Word('aa', self.feature_table))
        word_str2 = str(Word('ac', self.feature_table))
        word_str3 = str(Word('ad', self.feature_table))
        word_str4 = str(Word('bb', self.feature_table))
        word_str5 = str(Word('cb', self.feature_table))
        word_str6 = str(Word('db', self.feature_table))

        self.stochastic_object_method_testing(word, "change_segment",
                                              [word_str1, word_str2, word_str3, word_str4, word_str5, word_str6],
                                              num_of_tests=200, possible_result_threshold=10,
                                              all_possible_result_flag=True)

    def test_word_insert_segment(self):
        word = Word('abc', self.feature_table)
        segmentToInsert = 'd'
        word_str1 = str(Word('dabc', self.feature_table))
        word_str2 = str(Word('adbc', self.feature_table))
        word_str3 = str(Word('abdc', self.feature_table))
        word_str4 = str(Word('abcd', self.feature_table))

        self.stochastic_object_method_testing(word, "insert_segment",
                                              [word_str1, word_str2, word_str3, word_str4],
                                              num_of_tests=100, possible_result_threshold=10,
                                              all_possible_result_flag=True, method_args=(segmentToInsert))

    def test_word_delete_segment(self):
        word = Word('abab', self.feature_table)

        word_str1 = str(Word('aba', self.feature_table))
        word_str2 = str(Word('bab', self.feature_table))
        word_str3 = str(Word('aab', self.feature_table))
        word_str4 = str(Word('abb', self.feature_table))

        self.stochastic_object_method_testing(word, "delete_segment", [word_str1, word_str2, word_str3, word_str4],
                                              num_of_tests=200, possible_result_threshold=30,
                                              all_possible_result_flag=True)
    def test_is_appropriate(self):
        feature_table = get_feature_table_by_fixture("yimas_tpk_aiu_feature_table.csv")
        word = Word("pit'uk", feature_table)
        for i in range(0, 100):
            word2 = deepcopy(word)
            word2.delete_segment()
            print(word2)


    def test_word_encoding_length(self):
        word = Word('abb', self.feature_table)
        self.assertEqual(word.get_encoding_length(), 7)

    def test_word_slots(self):
        word = Word('abb', self.feature_table)
        print(dir(word))
        print(word.__dict__)
        print(word.__slots__)


def _find_out_mutation_type(original_lexicon, mutated_lexicon):
    if len(original_lexicon) < len(mutated_lexicon):
        return "insert"
    elif len(original_lexicon) > len(mutated_lexicon):
        return "delete"
    else:
        n = len(original_lexicon) & len(mutated_lexicon)
        for i in range(n):
            if original_lexicon[i] != mutated_lexicon[i]:
                if len(original_lexicon[i]) < len(mutated_lexicon[i]):
                    return "insert"
                elif len(original_lexicon[i]) > len(mutated_lexicon[i]):
                    return "delete"
                else:
                    return "change"