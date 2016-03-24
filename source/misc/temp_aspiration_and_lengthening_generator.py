
from misc.corpus_generator import CorpusGenerator
import itertools
from random import choice


def main():
    #english syllable structure:  (C)(C)(C)V(C)(C)(C)(C)

    consonants = ['t','p','k']
    vowels = ['i','a','u']


    #consonants = ['d','t']
    #vowels = ['i','a']


    corpus_generator = CorpusGenerator()

    one_syllable = ["CV", "VC", "CVC"]
    #two_syllables = [x+y for x, y in itertools.product(one_syllable,one_syllable)]
    two_syllables = ["CVCV","VCVC","CVCCV","CVCVC","CVVC"]
    #three__syllable = ["CVCVCV", "VCVCVC", "CVCVCCV","VCVCVC"]
    syllables = one_syllable + two_syllables

    corpus_generator.add_syllables(consonants, vowels, syllables)

    print(len(corpus_generator.words))

    corpus_generator.remove_duplicates()

    print(len(corpus_generator.words))
    string = corpus_generator.get_words_as_string()


    alternations_list = [('ad', 'a:d'), ('id', 'i:d'), ('ud', 'u:d'),
                         ('ab', 'a:b'), ('ib', 'i:b'), ('ub', 'u:b'),
                         ('ag', 'a:g'), ('ig', 'i:g'), ('ug', 'u:g'),

                         ('ta', 'tha'), ('ti', 'thi'), ('tu', 'thu'),
                         ('pa', 'pha'), ('pi', 'phi'), ('pu', 'phu'),
                         ('ka', 'kha'), ('ki', 'khi'), ('ku', 'khu')]

    all_words = string.split(" ")

    selected_words = []
    for i in range(200):
        word = choice(all_words)
        selected_words.append(word)
        all_words.remove(word)

    selected_words_string = " ".join(selected_words)

    print(selected_words_string)

    for alteration in alternations_list:
        selected_words_string = selected_words_string.replace(*alteration)

    selected_alternated_words_string = selected_words_string

    print(selected_alternated_words_string)


if __name__ == '__main__':
    main()

