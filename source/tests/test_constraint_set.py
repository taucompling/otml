from __future__ import absolute_import, division, print_function, unicode_literals

import os


from tests.otml_configuration_for_testing import configurations
from grammar.feature_table import FeatureTable
from grammar.constraint_set import ConstraintSet, _parse_bundle, _parse_bundle_list, _parse_constraint
from tests.stochastic_testcase import StochasticTestCase
from tests.persistence_tools import get_constraint_set_fixture, get_feature_table_fixture



class TestConstraintSet(StochasticTestCase):
    def setUp(self):
        self.illegal_grammar_file_names = [get_constraint_set_fixture(""
                                             "illegal_constraint_set{}.json".format(i+1)) for i in range(5)]
        self.correct_constraint_set_filename = get_constraint_set_fixture("constraint_set.json")
        self.feature_table = FeatureTable.load(get_feature_table_fixture("full_feature_table.json"))
        self.constraint_set = ConstraintSet.load(self.correct_constraint_set_filename, self.feature_table)


    def test_load_from_printed_string_representation(self):
        #self.assertEqual(str(_parse_bundle("[+syll]")), "{'syll': '+'}")
        #constraint_set_string = "Faith[] >> Phonotactic[+cons] >> Max[+cons]"
        #
        #constraint_set_json = ConstraintSet.json_from_printed_string_representation(constraint_set_string)
        #constraint_set = ConstraintSet.loads(constraint_set_json, self.feature_table)
        #self.assertEqual(str(constraint_set), "Constraint Set: " + constraint_set_string)

        feature_table = FeatureTable.load(get_feature_table_fixture("full_feature_table.json"))
        constraint_set = ConstraintSet.load(get_constraint_set_fixture("constraint_set.json"), feature_table)
        constraint_set_string = str(constraint_set).replace("Constraint Set: ", "")
        constraint_set = ConstraintSet.load_from_printed_string_representation(constraint_set_string, feature_table)


    def test_constraint_set_encoding_length(self):
        self.assertEqual(self.constraint_set.get_encoding_length(), 112)

   #TODO  dependent on value of parameter: neighborMutationWeights
    #def test_constraint_set_make_mutation(self):
    #    #around 80 possible results
    #    mutation1 = "Constraint Set: Phonotactic[[+cons, +labial][+cons][+cons]] >> Ident[-syll] >> Dep[+cons] >> Phonotactic[-cons] >> Max[-cons, -syll]"
    #    self.stochastic_object_method_testing(self.constraint_set, "make_mutation", [mutation1],
    #                                          num_of_tests=1000, possible_result_threshold=2)

    def test_illegal_grammar(self):
        for fn in self.illegal_grammar_file_names:
            with self.assertRaises(Exception):
                ConstraintSet.load(fn, self.feature_table)

    def test_constraint_set_insert_constraint(self):
        # 46 possible results
        constraint_set_str1 = "Constraint Set: Phonotactic[[+cons, +labial][+cons][+cons]] >> Ident[-syll] >> " \
                              "Max[+cons] >> Dep[+cons] >> Max[-cons, -syll]"
        constraint_set_str2 = "Constraint Set: Phonotactic[[+cons, +labial][+cons][+cons]] >> Ident[-syll] >> " \
                              "Max[+syll] >> Dep[+cons] >> Max[-cons, -syll]"
        possible_results = [constraint_set_str1, constraint_set_str2]
        self.stochastic_object_method_testing(self.constraint_set, "_insert_constraint", possible_results,
                                              num_of_tests=170, possible_result_threshold=1)

    def test_constraint_set_remove_constraint(self):

        dep_deletion = "Constraint Set: Phonotactic[[+cons, +labial][+cons][+cons]] >> Ident[-syll] >> " \
                       "Max[-cons, -syll]"
        ident_deletion = "Constraint Set: Phonotactic[[+cons, +labial][+cons][+cons]] >> Dep[+cons] >> " \
                         "Max[-cons, -syll]"
        max_deletion = "Constraint Set: Phonotactic[[+cons, +labial][+cons][+cons]] >> Ident[-syll] >> Dep[+cons]"
        phonotactic__deletion = "Constraint Set: Ident[-syll] >> Dep[+cons] >> Max[-cons, -syll]"
        possible_results = [dep_deletion, ident_deletion, max_deletion, phonotactic__deletion]

        self.stochastic_object_method_testing(self.constraint_set, "_remove_constraint", possible_results,
                                              num_of_tests=200, possible_result_threshold=25,
                                              all_possible_result_flag=True)

    def test_constraint_set_demote_constraint(self):
        phonotactic_demotion = "Constraint Set: Ident[-syll] >> Phonotactic[[+cons, +labial][+cons][+cons]] >> " \
                               "Dep[+cons] >> Max[-cons, -syll]"
        ident_demotion = "Constraint Set: Phonotactic[[+cons, +labial][+cons][+cons]] >> Dep[+cons] >> " \
                         "Ident[-syll] >> Max[-cons, -syll]"
        dep_demotion = "Constraint Set: Phonotactic[[+cons, +labial][+cons][+cons]] >> Ident[-syll] >> " \
                       "Max[-cons, -syll] >> Dep[+cons]"
        possible_results = [phonotactic_demotion, ident_demotion, dep_demotion]
        self.stochastic_object_method_testing(self.constraint_set, "_demote_constraint", possible_results,
                                              num_of_tests=20, possible_result_threshold=1)

    #TODO dependent on value of parameter: params.maxFeatureBundlesInPhonotacticConstraint
    #def test_constraint_set_augment_constraint(self):
    #    old_constraints_list = str(self.constraint_set)
    #    self.constraint_set._augment_constraint()
    #    new_constraints_list = str(self.constraint_set)
    #    OTConstraintSet.maxFeatureBundlesInPhonotacticConstraint = 2
    #    #params.maxFeatureBundlesInPhonotacticConstraint = 2
    #   # self.stochastic_object_method_testing(self.constraint_set, "demote_constraint", possible_results,
    #    #                        num_of_tests=100, possible_result_threshold=25)
    #    raise NotImplementedError

    def test_constraint_set_augment_feature_bundle(self):
        # 18 possible results
        constraint_set_str1 = "Constraint Set: Phonotactic[[+cons, +labial, -syll][+cons][+cons]] >> " \
                              "Ident[-syll] >> Dep[+cons] >> Max[-cons, -syll]"
        constraint_set_str2 = "Constraint Set: Phonotactic[[+cons, +labial][+cons][+cons]] >> Ident[+labial, -syll] >> " \
                              "Dep[+cons] >> Max[-cons, -syll]"
        constraint_set_str3 = "Constraint Set: Phonotactic[[+cons, +labial][+cons][+cons, +labial]] >> Ident[-syll] >> " \
                              "Dep[+cons] >> Max[-cons, -syll]"
        constraint_set_str4 = "Constraint Set: Phonotactic[[+cons, +labial][+cons][+cons, -labial]] >> Ident[-syll] >> " \
                              "Dep[+cons] >> Max[-cons, -syll]"

        possible_results = [constraint_set_str1, constraint_set_str2, constraint_set_str3, constraint_set_str4]
        self.stochastic_object_method_testing(self.constraint_set, "_augment_feature_bundle", possible_results,
                                              num_of_tests=800, possible_result_threshold=5)
