#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import itertools
from functools import reduce
import pickle

from transducer import Transducer, CostVector, Arc
from grammar.lexicon import Word
import random


logger = logging.getLogger(__name__)

class TransducerOptimizationError(Exception):
    pass


def get_cheapest_state(list_of_states, cost_by_state_dict):

    most_harmonic_state = random.choice(list_of_states)
    try:   #TODO for debug prints
        most_harmonic_cost_vector = cost_by_state_dict[most_harmonic_state]
    except KeyError as ex:
        #print(cost_by_state_dict)
        raise ex
    for state in list_of_states:
        if cost_by_state_dict[state] > most_harmonic_cost_vector:
            most_harmonic_cost_vector = cost_by_state_dict[state]
            most_harmonic_state = state
    return most_harmonic_state

def remove_suboptimal_paths(transducer):
    active_states = set(transducer.states)
    costs = {state: CostVector.get_inf_vector() for state in active_states}
    costs[transducer.initial_state] = CostVector.get_vector(transducer.get_length_of_cost_vectors(), 0)

    while active_states:
        cheapest_state = get_cheapest_state(list(active_states), costs)
        active_states.remove(cheapest_state)
        for state in active_states:
            for arc in transducer.get_arcs_by_origin_and_terminal_state(cheapest_state, state):
                costs[state] = max(costs[state], costs[cheapest_state] + arc.cost_vector)
    try:    #TODO for debug prints
        most_harmonic_final = get_cheapest_state(transducer.get_final_states(), costs)
    except KeyError as ex:
        #print(transducer.get_final_states())
        #print(transducer.dot_representation())
        raise ex
    transducer.set_final_state(most_harmonic_final)

    new_arcs = []
    for arc in transducer.get_arcs():
        if costs[arc.origin_state] + arc.cost_vector == costs[arc.terminal_state]:
            new_arcs.append(arc)
    transducer.set_arcs(new_arcs)

    #logger.debug("remove_suboptimal_paths: transducer output: %s", transducer)
    return transducer


def _get_path_cost(transducer):
    #logger.debug("_get_path_cost: transducer input: %s", transducer)
    current_state = transducer.get_a_final_state()
    path_cost = CostVector.get_vector(transducer.get_length_of_cost_vectors(), 0)
    initial_state = transducer.initial_state
    while current_state != initial_state:
        arcs_to_current_state = transducer.get_arcs_by_terminal_state(current_state)
        if arcs_to_current_state:
            arc = arcs_to_current_state[0]
            if arc.origin_state == current_state:
                raise TransducerOptimizationError('Cyclic Transducer')
        else:
            raise TransducerOptimizationError("No arcs leading to the current state. It is a dead state.")
        current_state = arc.origin_state
        path_cost += arc.cost_vector

    return path_cost


def make_optimal_paths(transducer_input, feature_table):
    transducer = pickle.loads(pickle.dumps(transducer_input, -1))
    alphabet = transducer.get_alphabet()
    new_arcs = list()
    for segment in alphabet:
        word = Word(segment.get_symbol(), feature_table)
        word_transducer = word.get_transducer()
        # (word_transducer.dot_representation())
        intersected_machine = Transducer.intersection(word_transducer, transducer)
        states = transducer.get_states()
        for state1, state2 in itertools.product(states, states):
            initial_state = word_transducer.initial_state & state1
            final_state = word_transducer.get_a_final_state() & state2
            temp_transducer = pickle.loads(pickle.dumps(intersected_machine, -1))
            temp_transducer.initial_state = initial_state
            temp_transducer.set_final_state(final_state)
            temp_transducer.clear_dead_states()
            if final_state in temp_transducer.get_final_states():  # otherwise no path.
                try:
                    temp_transducer = remove_suboptimal_paths(temp_transducer)
                    #write_to_dot(temp_transducer, "temp_transducer")
                    range = temp_transducer.get_range()
                    arc = Arc(state1, segment, range, _get_path_cost(temp_transducer), state2)
                    new_arcs.append(arc)
                except KeyError:
                    pass
                #print("****")
                #print(temp_transducer.dot_representation())

    transducer.set_arcs(new_arcs)
    return transducer


def _best_arcs(arcs_from_current_index, state_costs):
    best_arcs_by_state = {}
    for arc in arcs_from_current_index:
        current_cost = state_costs[arc.origin_state] + arc.cost_vector
        if arc.terminal_state in best_arcs_by_state.keys():
            terminus_cost = state_costs[arc.terminal_state]
            if current_cost > terminus_cost:
                best_arcs_by_state[arc.terminal_state] = [arc]
                state_costs[arc.terminal_state] = current_cost
            elif current_cost == terminus_cost:
                best_arcs_by_state[arc.terminal_state].append(arc)
        else: # arc.terminus is newly introduced
            best_arcs_by_state[arc.terminal_state] = [arc]
            state_costs[arc.terminal_state] = current_cost
    return reduce(lambda a, b: a+b, best_arcs_by_state.values())

def optimize_transducer_grammar_for_word(word, eval):
    states_by_index = {}
    for state in eval.states:
        if state.index in states_by_index.keys():
            states_by_index[state.index].append(state)
        else:
            states_by_index[state.index] = [state]

    arcs_by_index = {}
    for arc in eval._arcs:
        if arc.origin_state.index in arcs_by_index.keys():
            arcs_by_index[arc.origin_state.index].append(arc)
        else:
            arcs_by_index[arc.origin_state.index] = [arc]

    new_transducer = Transducer(eval.get_alphabet())

    state_costs = {}
    new_transducer.add_state(eval.initial_state)
    new_transducer.initial_state = eval.initial_state
    state_costs[eval.initial_state] = CostVector.get_vector(eval.get_length_of_cost_vectors(), 0)

    for index in range(len(word.get_segments())):
        new_arcs = _best_arcs(arcs_by_index[index], state_costs)
        for arc in new_arcs:
            new_transducer.add_arc(arc)
            new_transducer.add_state(arc.terminal_state)
            state_costs[arc.terminal_state] = state_costs[arc.origin_state] + arc.cost_vector

    new_final_states = [eval.final_states[0]]
    for state in eval.final_states[1:]:
        state_cost = state_costs[state]
        final_cost = state_costs[new_final_states[0]]
        if state_cost > final_cost:
            new_final_states = [state]
        elif state_cost == final_cost:
            new_final_states.append(state)

    for state in new_final_states:
        new_transducer.add_final_state(state)

    #new_transducer.clear_dead_states(with_impasse_states=True) #TODO give it a try

    return new_transducer


