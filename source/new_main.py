import codecs
from otml_configuration_manager import OtmlConfigurationManager


configuration_file_path = "/Users/iddoberger/Documents/MercurialRepositories/otml/source/tests/fixtures/configuration/otml_configuration.json"

configuration_json_str = codecs.open(configuration_file_path, 'r').read()
OtmlConfigurationManager(configuration_json_str)

from grammar.lexicon import Lexicon
from grammar.feature_table import FeatureTable
from grammar.constraint_set import ConstraintSet
from grammar.grammar import Grammar
from traversable_grammar_hypothesis import TraversableGrammarHypothesis
from corpus import Corpus
from simulated_annealing import SimulatedAnnealing






feature_table_file_path = "/Users/iddoberger/Documents/MercurialRepositories/otml/source/tests/fixtures/feature_table/french_deletion_feature_table.json"
corpus_file_path = "/Users/iddoberger/Documents/MercurialRepositories/otml/source/tests/fixtures/corpora/french_deletion_corpus.txt"
constraint_set_file_path = "/Users/iddoberger/Documents/MercurialRepositories/otml/source/tests/fixtures/constraint_sets/french_deletion_constraint_set.json"


configuration_json_str = codecs.open(configuration_file_path, 'r').read()
OtmlConfigurationManager(configuration_json_str)


feature_table = FeatureTable.load(feature_table_file_path)
corpus = Corpus.load(corpus_file_path)
constraint_set = ConstraintSet.load(constraint_set_file_path, feature_table)
lexicon = Lexicon(corpus.get_words(), feature_table)
grammar = Grammar(feature_table, constraint_set, lexicon)
data = corpus.get_words()
traversable_hypothesis = TraversableGrammarHypothesis(grammar, data)
simulated_annealing = SimulatedAnnealing(traversable_hypothesis)
simulated_annealing.run()
