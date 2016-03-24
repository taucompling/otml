#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

import os

from tests.otml_configuration_for_testing import configurations
from grammar.feature_table import FeatureTable
from grammar.constraint import MaxConstraint, IdentConstraint, PhonotacticConstraint, DepConstraint
from grammar.constraint_set import ConstraintSet
from grammar.grammar import GrammarParseError
from tests.stochastic_testcase import StochasticTestCase
from tests.persistence_tools import get_constraint_set_fixture, get_feature_table_fixture



class TestConstraint(StochasticTestCase):

    def setUp(self):
        self.correct_constraint_set_filename = get_constraint_set_fixture("constraint_set.json")
        self.feature_table = FeatureTable.load(get_feature_table_fixture("full_feature_table.json"))
        self.constraint_set = ConstraintSet.load(self.correct_constraint_set_filename, self.feature_table)

    def test_constraint_eq(self):
        constraint = DepConstraint([{'cons': '+'}], self.feature_table)
        self.assertEqual(constraint in self.constraint_set.constraints, True)

    def test_constraint_allow_multiple_bundles(self):
        with self.assertRaises(GrammarParseError):
            DepConstraint([{'syll': '+'}, {'cons': '+'}], self.feature_table)

    def test_constraints_generate_random(self):
        possible_results = ['Max[-syll]', 'Max[+syll]', 'Max[-cons]', 'Max[+cons]', 'Max[-labial]',
                            'Max[+labial]']
        self.stochastic_class_generate_random_testing(MaxConstraint, possible_results, num_of_tests=200,
                                                      possible_result_threshold=10, all_possible_result_flag=True)

        possible_results = ['Dep[-syll]', 'Dep[+syll]', 'Dep[-cons]', 'Dep[+cons]', 'Dep[-labial]', 'Dep[+labial]']
        self.stochastic_class_generate_random_testing(DepConstraint, possible_results, num_of_tests=200,
                                                      possible_result_threshold=10, all_possible_result_flag=True)

        possible_results = ['Ident[-syll]', 'Ident[+syll]', 'Ident[-cons]', 'Ident[+cons]', 'Ident[-labial]',
                            'Ident[+labial]']
        self.stochastic_class_generate_random_testing(IdentConstraint, possible_results, num_of_tests=200,
                                                      possible_result_threshold=10, all_possible_result_flag=True)

        if configurations["INITIAL_NUMBER_OF_BUNDLES_IN_PHONOTACTIC_CONSTRAINT"]is 1:
            possible_results = ['Phonotactic[-syll]', 'Phonotactic[+syll]', 'Phonotactic[-cons]', 'Phonotactic[+cons]', 'Phonotactic[-labial]',
                                'Phonotactic[+labial]']
            self.stochastic_class_generate_random_testing(PhonotacticConstraint, possible_results, num_of_tests=200,
                                                          possible_result_threshold=10, all_possible_result_flag=True)

    def test_constraints_augment_feature_bundle(self):
        maxConstraint = MaxConstraint([{'syll': '+'}], self.feature_table)
        possible_results = ['Max[-cons, +syll]', 'Max[-labial, +syll]', 'Max[+cons, +syll]', 'Max[+labial, +syll]']
        self.stochastic_object_method_testing(maxConstraint, "augment_feature_bundle", possible_results,
                                              num_of_tests=100, possible_result_threshold=10,
                                              all_possible_result_flag=True)

        depConstraint = DepConstraint([{'syll': '+'}], self.feature_table)
        possible_results = ['Dep[-cons, +syll]', 'Dep[-labial, +syll]', 'Dep[+cons, +syll]', 'Dep[+labial, +syll]']
        self.stochastic_object_method_testing(depConstraint, "augment_feature_bundle", possible_results,
                                              num_of_tests=100, possible_result_threshold=10,
                                              all_possible_result_flag=True)

        identConstraint = IdentConstraint([{'syll': '+'}], self.feature_table)
        possible_results = ['Ident[-cons, +syll]', 'Ident[-labial, +syll]', 'Ident[+cons, +syll]',
                            'Ident[+labial, +syll]']
        self.stochastic_object_method_testing(identConstraint, "augment_feature_bundle", possible_results,
                                              num_of_tests=100, possible_result_threshold=10,
                                              all_possible_result_flag=True)

        phonotacticConstraint = PhonotacticConstraint([{'syll': '+'}], self.feature_table)
        possible_results = ['Phonotactic[-cons, +syll]', 'Phonotactic[-labial, +syll]', 'Phonotactic[+cons, +syll]',
                            'Phonotactic[+labial, +syll]']
        self.stochastic_object_method_testing(phonotacticConstraint, "augment_feature_bundle", possible_results,
                                              num_of_tests=100, possible_result_threshold=10,
                                              all_possible_result_flag=True)

    def test_phonotactic_constraint_insert_feature_bundle(self):
        # 11 possible results
        phonotactic_constraint = PhonotacticConstraint([{'syll': '+'}], self.feature_table)
        constraint_str1 = "Phonotactic[[+syll][+labial]]"
        constraint_str2 = "Phonotactic[[+syll][-cons]]"

        possible_results = [constraint_str1, constraint_str2]
        self.stochastic_object_method_testing(phonotactic_constraint, "insert_feature_bundle", possible_results,
                                              num_of_tests=200, possible_result_threshold=5)

    def test_phonotactic_constraint_remove_feature_bundle(self):
        # 3 possible results
        phonotactic_constraint = PhonotacticConstraint([{'syll': '+'}, {'labial': '+'}, {'cons': '-'}], self.feature_table)

        constraint_str1 = "Phonotactic[[+syll][-cons]]"
        constraint_str2 = "Phonotactic[[+labial][-cons]]"
        constraint_str3 = "Phonotactic[[+syll][+labial]]"

        possible_results = [constraint_str1, constraint_str2, constraint_str3]
        self.stochastic_object_method_testing(phonotactic_constraint, "remove_feature_bundle", possible_results,
                                              num_of_tests=100, possible_result_threshold=20,
                                              all_possible_result_flag=True)










