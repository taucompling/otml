
from misc.corpus_generator import CorpusGenerator
import itertools
from random import choice, shuffle
from collections import namedtuple
import re



SyllablesTypeBase = namedtuple('SyllableType', ['aspiration_and_lengthening', 'aspiration_only', 'lengthening_only', 'nothing'])
class SyllablesType(SyllablesTypeBase):
    def __add__(self, other):
        return SyllablesType(self.aspiration_and_lengthening+other.aspiration_and_lengthening,
                             self.aspiration_only+other.aspiration_only,
                             self.lengthening_only+other.lengthening_only,
                             self.nothing+other.nothing)

    def get_a_minimal_property(self):
        min_index = 0
        for i in range(len(self)):
            if self[min_index] > self[i]:
                min_index = i
        return min_index

    def get_a_maximal_property(self):
        max_index = 0
        for i in range(len(self)):
            if self[max_index] < self[i]:
                max_index = i
        return max_index


consonants = ['t', 'd']#, 'k', 'g']
vowels = ['i', 'a', 'u']

alternations_list = [('ad', 'a:d'), ('id', 'i:d'), ('ud', 'u:d'), ('ed', 'e:d'), ('od', 'o:d'),
                     ('ab', 'a:b'), ('ib', 'i:b'), ('ub', 'u:b'), ('eb', 'e:b'), ('ob', 'o:b'),
                     ('ag', 'a:g'), ('ig', 'i:g'), ('ug', 'u:g'), ('eg', 'e:g'), ('og', 'o:g'),

                     ('ta', 'tha'), ('ti', 'thi'), ('tu', 'thu'), ('te', 'the'), ('to', 'tho'),
                     ('pa', 'pha'), ('pi', 'phi'), ('pu', 'phu'), ('pe', 'phe'), ('po', 'pho'),
                     ('ka', 'kha'), ('ki', 'khi'), ('ku', 'khu'), ('ke', 'khe'), ('ko', 'kho')]

#english syllable structure:  (C)(C)(C)V(C)(C)(C)(C)
one_syllable = ["CV", "VC", "CVC"]
two_syllables = ["CVCV","VCVC","CVCCV","CVCVC","VCCVC"]
#three__syllable = ["CVCVCV", "VCVCVC", "CVCVCCV","VCVCVC"]
syllables = one_syllable + two_syllables


def get_word_syllables_type(word, vowels_list=vowels):
    aspiration_and_lengthening_num = 0
    aspiration_only_num = 0
    lengthening_only_num = 0
    nothing_num = 0

    aspiration_and_lengthening_pattern = "h{}:"
    aspiration_only_pattern = "h{}[^:]"
    lengthening_only_pattern = "[^h]{}:"
    nothing_pattern = "[^h]{}[^:]"

    for vowel in vowels_list:
        aspiration_and_lengthening_num += len(re.findall(aspiration_and_lengthening_pattern.format(vowel), " {} ".format(word)))
        aspiration_only_num += len(re.findall(aspiration_only_pattern.format(vowel), " {} ".format(word)))
        lengthening_only_num += len(re.findall(lengthening_only_pattern.format(vowel), " {} ".format(word)))
        nothing_num += len(re.findall(nothing_pattern.format(vowel), " {} ".format(word)))

    return(SyllablesType(aspiration_and_lengthening_num, aspiration_only_num, lengthening_only_num, nothing_num))


assert get_word_syllables_type("tha:dtadthadta:d") == SyllablesType(aspiration_and_lengthening=1, aspiration_only=1, lengthening_only=1, nothing=1)


def generate_words(num_of_words=0):
    corpus_generator = CorpusGenerator()
    corpus_generator.add_syllables(consonants, vowels, syllables)
    corpus_generator.remove_duplicates()

    all_words_string = corpus_generator.get_words_as_string()
    all_words = all_words_string.split()
    print(len(all_words))

    if num_of_words:
        shuffle(all_words)

        all_words = all_words[:num_of_words]
        all_words_string = " ".join(all_words)

    alternated_words_string = all_words_string
    for alteration in alternations_list:
        alternated_words_string = alternated_words_string.replace(*alteration)

    return alternated_words_string


def create_even_corpus():
    alternated_words_string = generate_words()
    alternated_words = alternated_words_string.split()
    st_sum = SyllablesType(0, 0, 0, 0)

    selected_words = []

    while len(selected_words) < 200:
        candidate_word = choice(alternated_words)
        if get_word_syllables_type(candidate_word)[3] > 1:
           continue
        selected_words.append(candidate_word)
        alternated_words.remove(candidate_word)
        st_sum += get_word_syllables_type(candidate_word)



    print(selected_words)
    print(st_sum)



if __name__ == '__main__':
    create_even_corpus()

