from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import os
from copy import deepcopy

from tests.otml_configuration_for_testing import configurations
from transducer import CostVector, Arc, State, Transducer, JOKER_SEGMENT, NULL_SEGMENT, CostVectorOperationError
from grammar.feature_table import FeatureTable, Segment
from grammar.constraint import PhonotacticConstraint, MaxConstraint, IdentConstraint, DepConstraint, FaithConstraint
from tests.persistence_tools import get_pickle, get_feature_table_fixture, write_to_dot_to_file

class TestTransducer(unittest.TestCase):

    def setUp(self):
        self.feature_table = FeatureTable.load(get_feature_table_fixture("feature_table.json"))
        self.phonotactic_test_feature_table = FeatureTable.load(get_feature_table_fixture(
            "phonotactic_test_feature_table.json"))
        self.transducer = Transducer(self.feature_table.get_segments())
        self.state1 = State('q1')
        self.state2 = State('q2')
        self.transducer.add_state(self.state1)
        self.transducer.add_state(self.state2)
        self.transducer.initial_state = self.state1
        self.transducer.add_final_state(self.state2)
        self.cost_vector1 = CostVector([3, 1, 0])
        self.cost_vector2 = CostVector([2, 0, 0])
        self.arc = Arc(self.state1, Segment('a', self.feature_table), Segment('b', self.feature_table), CostVector([0, 1, 0]), self.state2)
        self.transducer.add_arc(self.arc)

        self.simple_transducer = self.transducer
        self.loops_transducer = deepcopy(self.transducer)
        zero_cost_vector = CostVector([0])
        segment_a = Segment('a', self.feature_table)
        segment_b = Segment('b', self.feature_table)
        self.loops_transducer.add_arc(Arc(self.state1, JOKER_SEGMENT, segment_a, zero_cost_vector, self.state1))
        self.loops_transducer.add_arc(Arc(self.state1, JOKER_SEGMENT, segment_b, zero_cost_vector,self.state1))
        self.loops_transducer.add_arc(Arc(self.state2, NULL_SEGMENT, segment_a, zero_cost_vector,self.state2))
        self.loops_transducer.add_arc(Arc(self.state2, NULL_SEGMENT, segment_b, zero_cost_vector,self.state2))

        phonotactic = PhonotacticConstraint([{'cons': '+'}, {'voice': '+'}, {'labial': '+'}],
                                                         self.phonotactic_test_feature_table).get_transducer()
        dep = DepConstraint([{'labial': '-'}], self.phonotactic_test_feature_table).get_transducer()
        max = MaxConstraint([{'voice': '-'}], self.phonotactic_test_feature_table).get_transducer()

        self.intersection_test_transducer = Transducer.intersection(phonotactic, dep, max)


    #Transducer tests:
    def test_transducer_equality(self):
        feature_table = FeatureTable.load(get_feature_table_fixture("a_b_and_cons_feature_table.json"))
        faith = FaithConstraint([],feature_table).get_transducer()
        phonotactic = PhonotacticConstraint([{'cons': '+'}], feature_table).get_transducer()
        max = MaxConstraint([{'cons': '+'}], feature_table).get_transducer()
        transducer1 = Transducer.intersection(faith, phonotactic, max)
        temp_transducer = Transducer.intersection(phonotactic, max)
        transducer2 = Transducer.intersection(faith, temp_transducer)

        self.assertEqual(transducer1, transducer2)
        #write_to_dot_to_file(transducer1, "transducer1")
        #write_to_dot_to_file(transducer2, "transducer2")




    #one with constraint set

    #create with manual intersection


    def test_transducer_equality_with_deepcopy(self):
        phonotactic_transducer = PhonotacticConstraint([{'cons': '+'}, {'voice': '+'}, {'labial': '+'}],
                                                         self.phonotactic_test_feature_table).get_transducer()
        phonotactic_transducer_copy = deepcopy(phonotactic_transducer)
        self.assertEqual(phonotactic_transducer, phonotactic_transducer_copy)

    def test_transducer_equality_with_pickle(self):
        phonotactic_transducer = PhonotacticConstraint([{'cons': '+'}, {'voice': '+'}, {'labial': '+'}],
                                                         self.phonotactic_test_feature_table).get_transducer()
        pickled_phonotactic_transducer = get_pickle("equality_with_pickle_transducer")
        phonotactic_transducer == pickled_phonotactic_transducer
        self.assertEqual(phonotactic_transducer, pickled_phonotactic_transducer)

    def test_transducer_intersection(self):
        self.assertEqual(self.intersection_test_transducer, get_pickle("intersection_test_transducer"))

    def test_transducer_clear_dead_states(self):
        transducer = Transducer(self.feature_table.get_segments())
        state1 = State('q1')
        state2 = State('q2')
        state3 = State('q3')
        state4 = State('q4')
        transducer.add_state(state1)
        transducer.add_state(state2)
        transducer.add_state(state3)
        transducer.add_state(state4)
        transducer.initial_state = state1
        transducer.add_final_state(state2)
        transducer.add_arc(Arc(state1, JOKER_SEGMENT, NULL_SEGMENT, CostVector([]), state2))
        transducer.add_arc(Arc(state1, JOKER_SEGMENT, NULL_SEGMENT, CostVector([]), state1))
        transducer.add_arc(Arc(state2, JOKER_SEGMENT, NULL_SEGMENT, CostVector([]), state2))
        transducer.add_arc(Arc(state3, JOKER_SEGMENT, NULL_SEGMENT, CostVector([]), state3))
        transducer.add_arc(Arc(state4, JOKER_SEGMENT, NULL_SEGMENT, CostVector([]), state3))
        transducer.clear_dead_states()
        self.assertEqual(transducer, get_pickle("clear_dead_states_test_transducer"))

    def test_get_arcs_by_origin_state(self):
        initial_state = self.intersection_test_transducer.initial_state
        arc_list = self.intersection_test_transducer.get_arcs_by_origin_state(initial_state)
        pickled_arc_list = get_pickle("get_arcs_by_origin_state_arc_list")
        self.assertTrue(_are_lists_equal(arc_list, pickled_arc_list))

    def test_get_arcs_by_terminal_state(self):
        initial_state = self.intersection_test_transducer.initial_state
        arc_list = self.intersection_test_transducer.get_arcs_by_origin_state(initial_state)
        pickled_arc_list = get_pickle("get_arcs_by_terminal_state_arc_list")
        self.assertTrue(_are_lists_equal(arc_list, pickled_arc_list))

    def test_get_range(self):
        pass  # see TestingParserSuite.test_geneare

    #State tests:
    def test_state_str(self):
        self.assertEqual(str(self.state1), "(q1,0)")

    def test_states_addition(self):
        new_state = State.states_addition(self.state1, self.state2)
        self.assertEqual(str(new_state), "(q1|q2,0)")
        new_state = State.states_addition(self.state1, self.state2)
        self.assertEqual(str(new_state), "(q1|q2,0)")

    #Arcs tests:
    def test_arc_str(self):
        self.assertEqual(str(self.arc), "['(q1,0)', 'a', 'b', '[0, 1, 0]', '(q2,0)']")

    #CostVector tests:
    def test_costVector_operations(self):
        self.assertEqual(self.cost_vector1 + self.cost_vector2, CostVector([5, 1, 0]))
        self.assertEqual(self.cost_vector1 * self.cost_vector2, CostVector([3, 1, 0, 2, 0, 0]))
        self.assertEqual(self.cost_vector1 - self.cost_vector2, CostVector([1, 1, 0]))

    def test_costVector_comparison(self):
        self.assertTrue(CostVector([0, 0, 0, 0, 0]) > CostVector([0, 0, 1, 0, 0]))
        self.assertFalse(CostVector([1, 0, 1]) > CostVector([0, 2, 0]))
        self.assertTrue(CostVector([1000, 0, 76]) > CostVector.get_inf_vector())
        self.assertFalse(CostVector.get_inf_vector() > CostVector([0, 1, 2]))
        self.assertFalse(CostVector.get_inf_vector() > CostVector.get_inf_vector())

    def test_costVector_get_vector_with_size_n_and_number_m(self):
        self.assertEqual(CostVector.get_vector(4, 0), CostVector([0, 0, 0, 0]))
        self.assertEqual(CostVector.get_vector(1, 1), CostVector([1]))
        self.assertEqual(CostVector.get_vector(0, 0), CostVector([]))
        self.assertEqual(CostVector.get_empty_vector(), CostVector([]))

    def test_costVector_str(self):
        self.assertEqual(str(CostVector([1, 1, 0])), "[1, 1, 0]")

    def test_costVector_illegal_operation(self):
        with self.assertRaises(CostVectorOperationError):
            CostVector([1,1]) + CostVector([1])

    def test_costVector_concatenation_with_empty_vector(self):
        cost_vector3 = CostVector([])
        self.assertEqual(self.cost_vector1 * cost_vector3, CostVector([3, 1, 0]))
        self.assertEqual(cost_vector3 * self.cost_vector1, CostVector([3, 1, 0]))



def _are_lists_equal(list1, list2):  #in order to compare lists without hash
        if len(list1) != len(list2):
            return False
        else:
            values = []
            for arc in list1:
                for arc2 in list2:
                    values.append(arc==arc2)

            if values.count(True) == len(list1):
                return True