
from functools import reduce


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
                   'V': vowels}

        for syllable in list_of_syllables:
            words_form_syllables += concatenate([mapping[i] for i in syllable])

        self.words += words_form_syllables
        return words_form_syllables



    def remove_duplicates(self):
        set_of_words = set(self.words)
        self.words = list(set_of_words)

    def get_words_as_string(self):
        return " ".join(self.words)


