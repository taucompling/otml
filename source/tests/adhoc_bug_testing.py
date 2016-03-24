from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import os
from copy import deepcopy

from tests.otml_configuration_for_testing import configurations
from grammar.feature_table import FeatureTable
from grammar.lexicon import Word
from grammar.lexicon import Lexicon
from corpus import Corpus
from grammar.constraint import MaxConstraint, DepConstraint, IdentConstraint, PhonotacticConstraint, FaithConstraint
from grammar.constraint_set import ConstraintSet
from tests.persistence_tools import write_pickle, get_pickle
from grammar.grammar import Grammar
from transducer import Transducer
from transducers_optimization_tools import make_optimal_paths
from tests.persistence_tools import get_feature_table_fixture, get_corpus_fixture, get_constraint_set_fixture, get_feature_table_by_fixture
from traversable_grammar_hypothesis import TraversableGrammarHypothesis
import cProfile

faith_8  = "Max[+voice] >> Phonotactic[[-syll][+long]] >> Dep[+syll] >> Max[+stop] >> Phonotactic[[-long][+voice]] >> Phonotactic[[+stop][+syll]] >> Dep[-syll] >> Max[+syll] >> Phonotactic[[-voice][-low]] >> Faith[]"

class TestAdhocBugs(unittest.TestCase):

    def setUp(self):
        pass

    def test_yimas(self):
        feature_table = FeatureTable.load(get_feature_table_fixture("yimas_feature_table.json"))
        yimas_final_constraint_set_string = "Phonotactic[[+stress][+cons]] >> Max[+syll] >> Max[-syll] >> HeadDep[] >> Phonotactic[[+cons][+cons]] >> MainLeft[] >> Precede[] >> Dep[-stress] >> Dep[+stress] >> Faith[]"
        #words = ["cvcv"]
        words = ["cv", "cvc", "ccv", "cvcv", "ccvc", "cvcvc", "cvvc"]
        print(_get_parse_from_strings(feature_table, yimas_final_constraint_set_string, words))


    def test_reverse_cs_yimas(self):
        feature_table = FeatureTable.load(get_feature_table_fixture("yimas_feature_table.json"))
        yimas_final_constraint_set_string = "Faith[] >> Dep[+stress] >> Dep[-stress] >> Precede[] >> MainLeft[] >> Phonotactic[[+cons][+cons]] >> HeadDep[] >> Max[-syll] >> Max[+syll] >> Phonotactic[[+stress][+cons]]"
        #words = ["cvcv"]
        words = ["c'v", "c'vc", "cvc'v", "c'vcv", "cvc'vc", "c'vcvc", "c'vvc"]
        print(_get_parse_from_strings(feature_table, yimas_final_constraint_set_string, words))







    def test_json(self):
        feature_table = FeatureTable.load(get_feature_table_fixture("aspiration_and_lengthening_feature_table.json"))
        constraint_set_string = "Phonotactic[[+long][-voice]] >> Phonotactic[[+stop][+syll]] >> Max[+long] >> Phonotactic[[-syll][+long]] >> Max[-asp] >> Phonotactic[[-long][-long]] >> Faith[] >> Phonotactic[[-low][-asp]]"
        #constraint_set_string2 = "Phonotactic[[-syll][+long]] >> Phonotactic[[+long][-voice]] >> Phonotactic[[+stop][+syll]] >> Max[-asp] >> Phonotactic[[-long][-long]] >> Dep[-low] >> Faith[] >> Phonotactic[[+voice][-voice]]"
        words = Corpus.load(get_corpus_fixture("aspiration_and_lengthening_target_lexicon.txt")).get_words()
        print(_get_parse_from_strings(feature_table, constraint_set_string, words))

    def test_halle_5(self):
        feature_table = FeatureTable.load(get_feature_table_fixture("td_kg_aiu_aspiration_and_lengthening_feature_table.json"))
        a = ""
        constraint_set_string ="Phonotactic[[+stop][+syll]] >> Max[+long] >> Max[-back] >> Max[-asp] >> Dep[+low] >> Dep[-asp] >> Max[-long] >> Faith[] >> Max[-syll] >> Dep[+stop] >> Max[+velar] >> Dep[-long] >> Phonotactic[[-voice][-stop][-syll][+low]] >> Phonotactic[[-long][-syll][-syll][-long]] >> Dep[+long]"
        words = ["tid"]
        print(_get_parse_from_strings(feature_table, constraint_set_string, words))
        #36 arcs and 2 states  0.8
        #729 arcs and 9 states 47

    def test_40s(self):
        feature_table = FeatureTable.load(get_feature_table_fixture("td_kg_aiu_aspiration_and_lengthening_feature_table.json"))
        a = ""
        constraint_set_string ="Phonotactic[[+stop][+syll]] >> Max[+long] >> Max[-back] >> Max[-asp] >> Dep[+low] >> Dep[-asp] >> Max[-long] >> Faith[] >> Max[-syll] >> Dep[+stop] >> Max[+velar] >> Dep[-long] >> Phonotactic[[-voice][-stop][-syll][+low]]"
        words = ["tid"]
        #print(_get_parse_from_strings(feature_table, constraint_set_string, words))
        def fu():
            _get_parse_from_strings(feature_table, constraint_set_string, words)
        cProfile.runctx('fu()', None, locals())
        #fu()


    def test_yimas_tpk_aiu(self):
        constraint_set_string = "Phonotactic[[+stress][+cons]] >> Max[+cons] >> HeadDep[] >> Phonotactic[[+cons][+cons]] >> MainLeft[] >> Precede[] >> Max[-cons] >> Dep[-high] >> Dep[+labial] >> Faith[]"
        feature_table = get_feature_table_by_fixture("yimas_tpk_aiu_feature_table.csv")
        words = "tti kpuk katu pakak pitip ti kuit pituk kitik pikat puk kikap ktut tapi tuip kukuk paip takak pikip ttuk kpak pipi taput kitap pupap kukik titip tapit tpu tatit tapak ppap tupa kutat paka tiup pukap papit kup paki kikak katip kakak puka tukik piku patip pip kipi tauk tiuk kapu tupat kukip pupup pkuk tutup pit kipa pakap kik kapat pupit tku pak tuit tutut tiip tuk taka pitup putu kakit tkut pa tiik pauk papuk kiap pikut pati ttak kit kipip piip kku tita taup tupit kitit paup tapuk puut kukit tpap taap tput kat puip pikup".split()
        #["t'a", "t'ip", "pit'a", "put'a", "pat'a", "t'aku"]
        #["pat'a", "pit'a", "put'a"]
        print(_get_parse_from_strings(feature_table, constraint_set_string, words))

    def test_yimas_tpk_aiu2(self):
        constraint_set_string = "Phonotactic[[+stress][+cons]] >> Max[-cons] >> HeadDep[] >> Phonotactic[[+cons][+cons]] >> Max[+cons] >> Dep[+labial] >> Precede[] >> Faith[] >> MainLeft[] >> Dep[-high]"
        feature_table = get_feature_table_by_fixture("yimas_tpk_aiu_feature_table.csv")
        words = ["pupap", "kitap", "pakak", "kikap", "kapat", "kikak", "pit", "piku", "papuk", "kipi"]
        print(_get_parse_from_strings(feature_table, constraint_set_string, words))


    def test_yimas_contiguity(self):
        constraint_set_string = "Contiguity[] >> Faith[]"
        feature_table = get_feature_table_by_fixture("yimas_feature_table.json")
        constraint_set = ConstraintSet.load_from_printed_string_representation(constraint_set_string, feature_table)
        #print(constraint_set.get_transducer().dot_representation())
        words = "c'vcv".split()
        lexicon = Lexicon(words, feature_table)
        grammar = Grammar(feature_table, constraint_set, lexicon)

        #print(grammar.get_transducer())
        print(_get_parse_from_strings(feature_table, constraint_set_string, words))

    def test_time_consuming_parse(self):
        feature_table = get_feature_table_by_fixture("td_kg_ai_aspiration_and_lengthening_feature_table.json")
        constraint_set_string = "Phonotactic[[+long][+syll]] >> Dep[-long] >> Dep[+velar] >> Dep[-syll] >> Phonotactic[[+syll][+voice]] >> Max[-asp] >> Faith[] >> Phonotactic[[-syll][-syll][-syll]] >> Dep[-velar] >> Phonotactic[+stop] >> Phonotactic[+long] >> Max[+asp] >> Phonotactic[[-velar][-low]] >> Phonotactic[[-low][+velar][-low][-long][-stop][+stop]] >> Max[+velar] >> Dep[-stop] >> Max[+voice]"
        print(_get_parse_from_strings(feature_table, constraint_set_string, ['tha:gthi']))
        #the transducer has 7944 arcs and 32 states
        #more then 40 minutes

    def test_time_consuming_parse_2(self):
        feature_table = get_feature_table_by_fixture("td_kg_ai_aspiration_and_lengthening_feature_table.json")
        constraint_set_string = "Phonotactic[[+long][+syll]] >> Dep[-long] >> Dep[+velar] >> Dep[-syll] >> Max[-asp] >> Faith[] >> Phonotactic[[-syll][-syll][-syll]] >> Dep[-velar] >> Phonotactic[+stop] >> Phonotactic[+long] >> Max[+asp] >> Phonotactic[[-low][+velar][-low][-long][-stop][+stop]] >> Max[+velar] >> Dep[-stop] >> Max[+voice]"
        print(_get_parse_from_strings(feature_table, constraint_set_string, ['tha:gthi']))


    def test_time_consuming_parse_3(self):
        feature_table = get_feature_table_by_fixture("td_kg_ai_aspiration_and_lengthening_feature_table.json")
        constraint_set_string = "Faith[] >> Phonotactic[[-syll][-syll][-syll]] >> Dep[-velar] >> Phonotactic[+stop] >> Phonotactic[+long] >> Max[+asp] >> Phonotactic[[-low][+velar][-low][-long][-stop][+stop]]"
        print(_get_parse_from_strings(feature_table, constraint_set_string, ['tha:gthi']))

    def test_time_consuming_parse_4(self):
        feature_table = get_feature_table_by_fixture("td_kg_ai_aspiration_and_lengthening_feature_table.json")
        constraint_set_string = "Phonotactic[[-low][+velar][-low][-long][-stop][+stop]] >> Faith[]"
        print(_get_parse_from_strings(feature_table, constraint_set_string, ['igiaag']))
        #the transducer has 1568 arcs and 14 states
        #145 sec

    def test_d_lengthening(self):
        feature_table = get_feature_table_by_fixture("d_lengthening_feature_table.json")
        constraint_set_string = "Phonotactic[[+syll][+voice]] >> Max[-long] >> Faith[]"
        print(_get_parse_from_strings(feature_table, constraint_set_string, ['id']))


    def test_t_aspiration(self):
        feature_table = get_feature_table_by_fixture("t_aspiration_feature_table.json")
        constraint_set_string = "Phonotactic[[+stop][-cons]] >> Max[-asp] >> Faith[]"
        print(_get_parse_from_strings(feature_table, constraint_set_string, ['ti']))



    def tearDown(self):
        configurations.reset_to_original_configurations()



def _get_parse_from_strings(feature_table, constraint_set_string, words):
    lexicon = Lexicon(words, feature_table)

    constraint_set = ConstraintSet.load_from_printed_string_representation(constraint_set_string, feature_table)

    grammar = Grammar(feature_table, constraint_set, lexicon)
    return grammar.get_all_outputs_grammar()


