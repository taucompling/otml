
from misc.corpus_generator import CorpusGenerator
import itertools
from random import choice


def main():
    #english syllable structure:  (C)(C)(C)V(C)(C)(C)(C)
    consonants = ['p','t']
    vowels = ['i','a']


    corpus_generator = CorpusGenerator()

    one_syllable = ["CV", "VC", "CVC", "CVCC"]
    #two_syllables = [x+y for x, y in itertools.product(one_syllable,one_syllable)]
    two_syllables = ["CVCV","VCVC","CVCCV","CVCVC","CVCCVC","CVCVVC"]
    #three_syllables = ["CVCVCV", "CVCVCVC"]
    syllables = one_syllable + two_syllables #+ three_syllables

    corpus_generator.add_syllables(consonants, vowels, syllables)

    print(len(corpus_generator.words))

    corpus_generator.remove_duplicates()

    print(len(corpus_generator.words))
    string = corpus_generator.get_words_as_string()


    #string = string.replace('id','i:d')
    #string = string.replace('ad','a:d')
    string = string.replace('ta','tha')
    string = string.replace('ti','thi')
    string = string.replace('pa','pha')
    string = string.replace('pi','phi')





    print(string)

    words = string.split()
    selected_words = []
    for i in range(200):
        word = choice(words)
        selected_words.append(word)
        words.remove(word)

    selected_words_string = " ".join(selected_words)

    print(selected_words_string)


if __name__ == '__main__':
    main()

