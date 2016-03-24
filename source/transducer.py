#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

from copy import deepcopy
import functools
import itertools
import logging
from collections import defaultdict

from six import PY3, StringIO, itervalues

from unicode_mixin import UnicodeMixin
from grammar.feature_table import NULL_SEGMENT, JOKER_SEGMENT, Segment

logger = logging.getLogger(__name__)

class TransducerError(Exception):
    pass

class Transducer(UnicodeMixin, object):
    __slots__ = ["name", "states", "alphabet", "_arcs", "initial_state", "final_states", "arcs_by_state_dict", "length_of_cost_vectors"]
    def __init__(self, alphabet, name=None, length_of_cost_vectors=1):
        self.name = name
        self.states = list()
        self.alphabet = alphabet  # contains Segments
        self._arcs = list()
        self.initial_state = None
        self.final_states = list()
        self.arcs_by_state_dict = dict()
        self.length_of_cost_vectors = length_of_cost_vectors

    def set_as_single_state(self, state):
        self.initial_state = state
        self.final_states = [state]
        self.states = [state]

    def get_states(self):
        return self.states

    def get_alphabet(self):
        return self.alphabet

    def add_state(self, state):
        self.states.append(state)

    def get_final_states(self):
        return self.final_states

    def get_a_final_state(self):
        return next(iter(self.final_states))

    def set_final_state(self, state):  # sets a single state as final state
        self.final_states = [state]

    def add_final_state(self, state):
        self.final_states.append(state)

    def get_arcs(self):
        return self._arcs

    def remove_arc(self, arc):
        self.arcs_by_state_dict[arc.origin_state][arc.terminal_state].remove(arc)
        self._arcs.remove(arc)

    def add_arc(self, arc):
        if arc.origin_state not in self.arcs_by_state_dict:
            self.arcs_by_state_dict[arc.origin_state] = dict()
        if arc.terminal_state not in self.arcs_by_state_dict[arc.origin_state]:
            self.arcs_by_state_dict[arc.origin_state][arc.terminal_state] = list()

        self.arcs_by_state_dict[arc.origin_state][arc.terminal_state].append(arc)

        self._arcs.append(arc)

    def clear_dead_states(self, with_impasse_states = False):
        """
        Dead state:
        a state that cannot be reached from the initial state by following any path  (unreachable state)
        or
        a state that cannot reach a final state by following any path (impasse state)
        """
        #logger.debug("clear_dead_states: transducer before: %s", self)
        #clear unreachable states:
        state_unreachable_dict = {state: True for state in self.states}  # all states are unreachable at first
        state_unreachable_dict[self.initial_state] = False               # except for initial state

        while True:    # "do while" loop
            change_in_dict = False
            for arc in self._arcs:
                if not state_unreachable_dict[arc.origin_state] and state_unreachable_dict[arc.terminal_state]:
                    state_unreachable_dict[arc.terminal_state] = False
                    change_in_dict = True

            if not change_in_dict:
                break

        unreachable_states = [state for state in state_unreachable_dict if state_unreachable_dict[state]]


        # remove arcs from arcs_by_state_dict
        for state in unreachable_states:
             self.arcs_by_state_dict.pop(state, None)  #TODO add None for Yimas

        for origin_state in self.arcs_by_state_dict.keys():  #TODO maybe we don't need this due to the nature of cliques
            for state in unreachable_states:
                self.arcs_by_state_dict[origin_state].pop(state, None)

        #remove arcs for _arcs
        self._arcs[:] = [arc for arc in self._arcs if ((arc.origin_state not in unreachable_states) and
                                                        (arc.terminal_state not in unreachable_states))]

        #remove states
        self.states[:] = [state for state in self.states if state not in unreachable_states]
        self.final_states[:] = [state for state in self.final_states if state not in unreachable_states]


        if with_impasse_states:
            #clear impasse states:
            state_impasse_dict = {state: True for state in self.states}  # all states are impasse at first
            for final_state in self.final_states:                         # except for the final states
                state_impasse_dict[final_state] = False

            while True:    # "do while" loop
                change_in_dict = False
                for arc in self._arcs:
                    if not state_impasse_dict[arc.terminal_state] and state_impasse_dict[arc.origin_state]:
                        state_impasse_dict[arc.origin_state] = False
                        change_in_dict = True

                if not change_in_dict:
                    break

            impasse_states = [state for state in state_impasse_dict if state_impasse_dict[state]]

            # remove arcs from arcs_by_state_dict
            for state in impasse_states:
                 self.arcs_by_state_dict.pop(state, None)

            for origin_state in self.arcs_by_state_dict.keys():
                for state in impasse_states:
                    self.arcs_by_state_dict[origin_state].pop(state, None)

            #remove arcs for _arcs
            self._arcs[:] = [arc for arc in self._arcs if ((arc.origin_state not in impasse_states) and
                                                            (arc.terminal_state not in impasse_states))]

            #remove states
            self.states[:] = [state for state in self.states if state not in impasse_states]
            self.final_states[:] = [state for state in self.final_states if state not in impasse_states]

            #logger.debug("clear_dead_states: transducer after: %s", self)


    def get_length_of_cost_vectors(self):
        return self.length_of_cost_vectors


    def set_final_states(self, list_of_final_states):
        self.final_states = list_of_final_states

    def set_arcs(self, list_of_arcs):   # TODO Maybe optimization is needed - looping on arcs is costly
        self.arcs_by_state_dict = dict()
        self._arcs = list()
        for arc in list_of_arcs:
            self.add_arc(arc)

    def swap_weights_on_arcs(self, i, j):
       for arc in self._arcs:
           arc.swap_weights(i, j)


    def get_range(self):
        """
        returns a set of strings
        """
        strings_by_state = dict()

        for state in self.states:
            strings_by_state[state] = set()
        strings_by_state[self.initial_state].add('')

        active_states = set([self.initial_state])

        sets_on_arcs_flag = isinstance(self._arcs[0].output, set)

        while active_states:
            next_pass_states = set()
            for state in list(active_states):
                arcs = self.get_arcs_by_origin_state(state)
                state_strings = list(strings_by_state[state])
                for arc in arcs:
                    next_pass_states.add(arc.terminal_state)
                    for string1 in state_strings:
                        if sets_on_arcs_flag:
                            if arc.output == {''}:
                                strings_by_state[arc.terminal_state].add(string1)
                            else:
                                for string2 in arc.output:
                                    strings_by_state[arc.terminal_state].add(string1 + string2)
                        else:  # arc has a segment as output
                            if arc.output == NULL_SEGMENT:
                                strings_by_state[arc.terminal_state].add(string1)
                            elif arc.output == JOKER_SEGMENT:
                                for segment in self.alphabet:
                                    string2 = segment.get_symbol()
                                    strings_by_state[arc.terminal_state].add(string1 + string2)
                            else:
                                string2 = arc.output.get_symbol()
                                strings_by_state[arc.terminal_state].add(string1 + string2)
            active_states = next_pass_states

        strings = set()
        for state in self.get_final_states():
            strings.update(strings_by_state[state])

        return strings

    def get_arcs_by_origin_state(self, origin_state):
        arcs = list()
        if origin_state in self.arcs_by_state_dict:
            for state_arcs in itervalues(self.arcs_by_state_dict[origin_state]):
                arcs.extend(state_arcs)
        return arcs

    def get_arcs_by_terminal_state(self, terminal_state):
        arcs = list()
        for state_arcs in itervalues(self.arcs_by_state_dict):
            if terminal_state in state_arcs:
                arcs.extend(state_arcs[terminal_state])
        return arcs

    def get_arcs_by_origin_and_terminal_state(self, origin_state, terminal_state):
        if origin_state not in self.arcs_by_state_dict:
            return []
        if terminal_state not in self.arcs_by_state_dict[origin_state]:
            return []
        return self.arcs_by_state_dict[origin_state][terminal_state][:]

    def _arcs_dot_representation(self):
        def get_pretty_set_string(set_):
            if PY3:
                return str(set_)
            else:
                return str(set_)   #TODO fix from  set([u'ab']) to {'ab'}
        def get_output_str(output):
             if isinstance(output, set):
                return get_pretty_set_string(output)
             else:
                return output.get_symbol()

        str_io = StringIO()
        arcs = deepcopy(self._arcs)
        loop_arcs_by_state = defaultdict(list)
        multiple_arcs_state_tuple = defaultdict(list)
        for arc in arcs:
            if arc.origin_state == arc.terminal_state:
                    loop_arcs_by_state[arc.origin_state].append(arc)
            elif len(self.arcs_by_state_dict[arc.origin_state][arc.terminal_state]) > 1:
                multiple_arcs_state_tuple[(arc.origin_state, arc.terminal_state)].append(arc)
            else:    # singular arc
                print("\"{0}\" -> \"{1}\" [label=\"{2} : {3} {4}\\n\"];".format(
                    arc.origin_state, arc.terminal_state, arc.input.get_symbol(), get_output_str(arc.output), arc.cost_vector), file=str_io, end="\n")

        for state in loop_arcs_by_state:
            arcs_list = loop_arcs_by_state[state]
            combined_label = ""
            for arc in arcs_list:
                combined_label += "{0} : {1} {2}\\n".format(arc.input.get_symbol(), get_output_str(arc.output), arc.cost_vector)

            combined_label += "\\n" * len(arcs_list)

            print("\"{0}\" -> \"{1}\" [label=\"{2}\"];".format(
                     state, state, combined_label), file=str_io, end="\n")

        for states_tuple in multiple_arcs_state_tuple:
            arcs_list = multiple_arcs_state_tuple[states_tuple]
            state1, state2 = states_tuple
            combined_label = ""
            for arc in arcs_list:
                combined_label += "{0} : {1} {2}\\n".format(arc.input.get_symbol(), get_output_str(arc.output), arc.cost_vector)

            combined_label += "\\n" * len(arcs_list)

            print("\"{0}\" -> \"{1}\" [label=\"{2}\"];".format(
                     state1, state2, combined_label), file=str_io, end="\n")

        return str_io.getvalue()


    def dot_representation(self):
        str_io = StringIO()
        print("digraph acceptor {", file=str_io, end="\n")
        print("rankdir=LR", file=str_io, end="\n")
        print("size=\"11,5\"", file=str_io, end="\n")
        print("node [shape = ellipse];", file=str_io, end="\n")

        print("// arcs: source -> dest [label]", file=str_io, end="\n")
        print(self._arcs_dot_representation(), file=str_io, end="")

        print("// start nodes", file=str_io, end="\n")
        print("\"{0}\" [style=filled];".format(self.initial_state), file=str_io, end="\n")

        print("// final nodes", file=str_io, end="\n")
        for state in self.final_states:
            print("\"{0}\" [peripheries=2];".format(state), file=str_io, end="\n")

        print("}", file=str_io, end="")

        return str_io.getvalue()

    @classmethod
    def _binary_intersection(cls, transducer1, transducer2):
        """ Intersect two transducers

        :param transducer1: A transducer
        :type transducer1: Transducer
        :param transducer2: A transducer
        :type transducer2: Transducer
        :rtype: Transducer
        """

        alphabet = list(set(transducer1.alphabet) | set(transducer2.alphabet))
        cost_vectors_length = transducer1.length_of_cost_vectors + transducer2.length_of_cost_vectors

        transducer = Transducer(alphabet, length_of_cost_vectors=cost_vectors_length)

        transducer.initial_state = transducer1.initial_state & transducer2.initial_state

        for state1, state2 in itertools.product(transducer1.states, transducer2.states):
            transducer.states.append(state1 & state2)

        for state1, state2 in itertools.product(transducer1.final_states, transducer2.final_states):
            transducer.final_states.append(state1 & state2)

        for arc1, arc2 in itertools.product(transducer1._arcs, transducer2._arcs):
            intersected_arc = Arc.intersect(arc1, arc2)
            if intersected_arc is not None:
                transducer.add_arc(intersected_arc)

        return transducer


    @classmethod
    def intersection(cls, *transducers):
        intersected_transducer = functools.reduce(Transducer._binary_intersection, transducers)
        intersected_transducer.clear_dead_states()
        return intersected_transducer

    def __unicode__(self):
        str_io = StringIO()
        if self.name:
            print(self.name, file=str_io, end=" ")
        print("transducer:".format(), file=str_io, end="\n")
        print("initial state: {0}".format(self.initial_state), file=str_io, end="\n")
        print("final states: {0}".format([str(state) for state in self.final_states]), file=str_io, end="\n")
        print("states: {0}".format([str(state) for state in self.states]), file=str_io, end="\n")
        print("arcs:", file=str_io, end="\n")
        for arc in self._arcs:
            print(arc, file=str_io, end="\n")
        print("arcs_by_state_dict:", file=str_io, end="\n")
        for state1 in self.arcs_by_state_dict:
            for state2 in self.arcs_by_state_dict[state1]:
                print(str(state1)+" "+str(state2), file=str_io, end=": ")
                for arc in self.arcs_by_state_dict[state1][state2]:
                    print(arc, file=str_io, end=" ")
                print("", file=str_io, end="\n")

        return str_io.getvalue()

    def get_info(self):
        return "the transducer has {} arcs and {} states".format(len(self._arcs), len(self.states))


    def __eq__(self, other):
        def get_set_of_strings_from_list(list_):   #Work around for problem in PY3 concerning Unicode
            return set([str(item) for item in list_])

        result = True

        if self.initial_state != other.initial_state:
            result = False
        if get_set_of_strings_from_list(self._arcs) != get_set_of_strings_from_list(other._arcs):
            result = False
        if get_set_of_strings_from_list(self.states) != get_set_of_strings_from_list(other.states):
            result = False
        if get_set_of_strings_from_list(self.final_states) != get_set_of_strings_from_list(other.final_states):
            result = False

        return result


class State(UnicodeMixin, object):
    __slots__ = ["label", "index", "hash"]
    def __init__(self, label, index=0):
        self.label = label
        self.index = index
        self.hash = hash(self.label)

    @classmethod
    def states_addition(cls, state1, state2):
        return state1 & state2

    def get_index(self):
        return self.index

    def __and__(self, other):
        new_state = State("{0}|{1}".format(self.label, other.label))
        new_state.index = max(self.index, other.index)
        return new_state

    def __eq__(self, other):
        return self.label == other.label

    def __ne__(self, other):
        return self.label != other.label

    def __hash__(self):
        return self.hash

    def __unicode__(self):
        return "({0},{1})".format(self.label, str(self.index))


class Arc(UnicodeMixin, object):
    __slots__ = ["origin_state", "input", "output", "cost_vector", "terminal_state", "hash"]
    def __init__(self, origin_state, input, output, cost_vector, terminal_state):

        self.origin_state = origin_state
        self.input = input
        self.output = output
        self.cost_vector = cost_vector
        self.terminal_state = terminal_state
        self.hash = hash((self.origin_state, self.input, self.terminal_state))

    def swap_weights(self, i, j):
        self.cost_vector.swap_weights(i, j)

    @classmethod
    def intersect(cls, arc1, arc2):
        unified_input = Segment.intersect(arc1.input, arc2.input)
        unified_output = Segment.intersect(arc1.output, arc2.output)

        if unified_input is not None and unified_output is not None:
            new_origin_state = arc1.origin_state & arc2.origin_state
            new_terminal_state = arc1.terminal_state & arc2.terminal_state
            cost_vector = arc1.cost_vector * arc2.cost_vector
            return Arc(new_origin_state, unified_input, unified_output, cost_vector, new_terminal_state)

        return None

    def __and__(self, other):
        return Arc.intersect(self, other)

    def __eq__(self, other):
        return self.origin_state == other.origin_state and \
               self.input == other.input and \
               self.output == other.output and \
               self.terminal_state == other.terminal_state

    def __hash__(self):
        return self.hash

    def __unicode__(self):
        if isinstance(self.output, set):
            output = str(self.output)
        else:
            output = str(self.output.get_symbol())

        return str([str(self.origin_state), str(self.input.get_symbol()), output, str(self.cost_vector),
                    str(self.terminal_state)])


class CostVectorOperationError(Exception):
    pass



class CostVector(UnicodeMixin, object):
    def __init__(self, vector):
        self.vector = vector
        self.hash = hash(str(self.vector))

    def _verify_equal_length(self, other):
        if len(self.vector) != len(other.vector):
                raise CostVectorOperationError

    def swap_weights(self, i, j):
        self.vector[i], self.vector[j] = self.vector[j], self.vector[i]
        self.hash = hash(str(self.vector))

    def __add__(self, other):
        """Vector pointwise addition - must have the same length"""
        self._verify_equal_length(other)
        return CostVector([a+b for a, b in zip(self.vector, other.vector)])

    def __sub__(self, other):
        """Vector pointwise subtraction - must have the same length"""
        self._verify_equal_length(other)
        return CostVector([a-b for a, b in zip(self.vector, other.vector)])

    def __mul__(self, other):
        """Vector concatenation"""
        return CostVector(self.vector + other.vector)

    def __unicode__(self):
        return str(self.vector)

    def __len__(self):
        return len(self.vector)

    def __eq__(self, other):
        return self.vector == other.vector

    def __ne__(self, other):
        return self.vector != other.vector

    def __hash__(self):
        return self.hash

    def __lt__(self, other):
        return not __gt__ and not self == other

    def __gt__(self, other):
        if self == CostVector.get_inf_vector():
            return False
        if other == CostVector.get_inf_vector():
            return True
        else:
            self._verify_equal_length(other)
            difference = self - other
            for i in difference.vector:
                if i == 0:
                    continue
                if i < 0:
                    return True
                else:
                    return False
    @staticmethod
    def get_inf_vector():
        return CostVector(float("inf"))  #TODO create static variable

    @staticmethod
    def get_empty_vector():
        return CostVector(list())

    @staticmethod
    def get_vector(size, value):
        return CostVector([value] * size)