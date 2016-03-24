from random import choice
from functools import reduce



def main():
    #english syllable structure:  (C)(C)(C)V(C)(C)(C)(C)
    consonants = ['p','t','k']
    vowels = ['i','a','u']

    corpus_generator = CorpusGenerator()


    #syllables = ["C'V", "C'VC", "CVC'V", "C'VCV","CVC'VC", "C'VCVC","C'VVC"]

    syllables = "CV CVC CCV CVCV CCVC CVCVC CVVC".split()

    corpus_generator.add_syllables(consonants, vowels, syllables)

    print(len(corpus_generator.words))

    corpus_generator.remove_duplicates()

    print(len(corpus_generator.words))
    string = corpus_generator.get_words_as_string()


    print(string)

    words = string.split()
    selected_words = []
    for i in range(100):
        word = choice(words)
        selected_words.append(word)
        words.remove(word)

    selected_words_string = " ".join(selected_words)

    print(selected_words_string)


class CorpusGenerator:
    def __init__(self):
        self.words = []

    def add_syllables(self, consonants, vowels, list_of_syllables):
        def binary_concatenation(A, B):
            return [a+b for a in A for b in B]
        def concatenate(sets):
            return reduce(binary_concatenation, sets)

        words_form_syllables = []

        mapping = {'C': consonants,
                   'V': vowels, "'":["'"]}

        for syllable in list_of_syllables:
            words_form_syllables += concatenate([mapping[i] for i in syllable])

        self.words += words_form_syllables
        return words_form_syllables



    def remove_duplicates(self):
        set_of_words = set(self.words)
        self.words = list(set_of_words)

    def get_words_as_string(self):
        return " ".join(self.words)


if __name__ == '__main__':
    main()

