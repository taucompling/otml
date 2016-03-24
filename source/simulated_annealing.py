#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
from math import exp
from random import choice
import random
from datetime import timedelta
import time
import re
from otml_configuration_manager import OtmlConfigurationManager, OtmlConfigurationError
import subprocess
from grammar.grammar import Grammar
from grammar.constraint_set import ConstraintSet
from grammar.constraint import Constraint
from grammar.lexicon import Word
from mail import MailManager



configurations = OtmlConfigurationManager.get_instance()
if configurations is None:
    raise OtmlConfigurationError("OtmlConfigurationManager was not initialized")


logger = logging.getLogger(__name__)

process_id = os.getpid()


class SimulatedAnnealing(object):

    def __init__(self, traversable_hypothesis, target_lexicon_indicator_function=None, sample_target_lexicon=None,
                 sample_target_outputs=None, target_energy=None):
        self.current_hypothesis = traversable_hypothesis
        self.target_lexicon_indicator_function = target_lexicon_indicator_function
        self.target_energy = target_energy

        if sample_target_lexicon and sample_target_outputs:
            self.target_data = True
            self.sample_target_lexicon = sample_target_lexicon
            self.sample_target_outputs = sample_target_outputs
        else:
            self.target_data = False
        self.step = 0
        self.current_temperature = None
        self.threshold = None
        self.cooling_parameter = None
        self.current_hypothesis_energy = None
        self.neighbor_hypothesis = None
        self.neighbor_hypothesis_energy = None
        self.step_limitation = None
        self.number_of_expected_steps = None
        self.start_time = None
        self.previous_interval_time = None
        self.previous_interval_energy = None
        self.mail_manager = MailManager()
    def run(self):
        """
        staring simulated annealing
        """
        self.before_loop()

        while (self.current_temperature > self.threshold) and (self.step != self.step_limitation):
            self.make_step()

        self._after_loop()
        return self.step, self.current_hypothesis

    #@timeit
    def make_step(self):
        self.step += 1
        self.current_temperature *= self.cooling_parameter

        self._check_for_intervals()

        mutation_result, neighbor_hypothesis = self.current_hypothesis.get_neighbor()
        if not mutation_result:
            return  # mutation failed - the neighbor hypothesis is the same as current hypothesis

        self.neighbor_hypothesis = neighbor_hypothesis
        self.neighbor_hypothesis_energy = self.neighbor_hypothesis.get_energy()
        delta = self.neighbor_hypothesis_energy - self.current_hypothesis_energy

        if delta < 0:
            p = 1
        else:
            p = exp(-delta / self.current_temperature)
        if random.random() < p:
            #logger.info("switch")
            self.current_hypothesis = self.neighbor_hypothesis
            self.current_hypothesis_energy = self.neighbor_hypothesis_energy
        else:
            pass
            #logger.info("no switch")

    def before_loop(self):
        self.start_time = time.time()
        self.previous_interval_time = self.start_time
        logger.info("Process Id: {}".format(process_id))
        if configurations["RANDOM_SEED"]:
            seed = choice(range(1, 1000))
            logger.info("Seed: {} - randomly selected".format(seed))
        else:
            seed = configurations["SEED"]
            logger.info("Seed: {} - specified".format(seed))
        random.seed(seed)
        logger.info(configurations)
        logger.info(self.current_hypothesis.grammar.feature_table)
        self.step_limitation = configurations["STEPS_LIMITATION"]
        if self.step_limitation != float("inf"):
            self.number_of_expected_steps = self.step_limitation
        else:
            self.number_of_expected_steps = self._calculate_num_of_steps()

        logger.info("Number of expected steps is: {:,}".format(self.number_of_expected_steps))
        self.current_hypothesis_energy = self.current_hypothesis.get_energy()
        if self.current_hypothesis_energy == float("INF"):
            raise ValueError("first hypothesis energy can not be INF")

        self._log_hypothesis_state()
        self.previous_interval_energy = self.current_hypothesis_energy
        self.current_temperature = configurations["INITIAL_TEMPERATURE"]
        self.threshold = configurations["THRESHOLD"]
        self.cooling_parameter = configurations["COOLING_PARAMETER"]
        #logger.info("distinct_words: {}".format(self.current_hypothesis.grammar.lexicon.get_number_of_distinct_words()))

    def _check_for_intervals(self):
        if not self.step % configurations["DEBUG_LOGGING_INTERVAL"]:
            self._debug_interval()
        if not self.step % configurations["CLEAR_MODULES_CACHING_INTERVAL"]:
            self.clear_modules_caching()

    def _debug_interval(self):
        current_time = time.time()
        logger.info("\n"+"-"*125)
        percentage_completed = 100 * float(self.step)/float(self.number_of_expected_steps)
        logger.info("Step {0:,} of {1:,} ({2:.2f}%)".format(self.step, self.number_of_expected_steps,
                                                            percentage_completed))
        logger.info("-" * 80)
        elapsed_time = current_time - self.start_time
        logger.info("Time from simulation start: {}".format(_pretty_runtime_str(elapsed_time)))
        crude_expected_time = elapsed_time * (100/percentage_completed)
        logger.info("Expected simulation time: {} ".format(_pretty_runtime_str(crude_expected_time)))
        logger.info("Current temperature: {}".format(self.current_temperature))
        self._log_hypothesis_state()
        logger.info("Energy difference from last interval: {}".format(self.current_hypothesis_energy - self.previous_interval_energy))
        self.previous_interval_energy = self.current_hypothesis_energy
        time_from_last_interval = current_time - self.previous_interval_time
        logger.info("Time from last interval: {}".format(_pretty_runtime_str(time_from_last_interval)))
        logger.info("Time to finish based on current interval: {}".format(self.by_interval_time(time_from_last_interval)))
        self.previous_interval_time = current_time
        #logger.info("Memory usage: {} MB".format(self._get_memory_usage()))
        #logger.info(debug_tools.get_statistics())
        #logger.info("distinct_words: {}".format(self.current_hypothesis.grammar.lexicon.get_number_of_distinct_words()))


    def by_interval_time(self, time_from_last_interval):
        number_of_remaining_steps = self.number_of_expected_steps - self.step
        number_of_remaining_intervals = int(number_of_remaining_steps/configurations["DEBUG_LOGGING_INTERVAL"])
        expected_time = number_of_remaining_intervals * time_from_last_interval
        return _pretty_runtime_str(expected_time)


    def _after_loop(self):
        current_time = time.time()
        logger.info("*"*10 +" Final Hypothesis " + "*"*10)
        self._log_hypothesis_state()
        logger.info("simulated annealing runtime was: {}".format(_pretty_runtime_str(current_time - self.start_time)))


    def _log_hypothesis_state(self):
        logger.info("Grammar with: {}:".format(self.current_hypothesis.grammar.constraint_set))
        if configurations["RESTRICTION_ON_ALPHABET"]:
            restricted_alphabet = self.current_hypothesis.grammar.lexicon.get_distinct_segments()
            restricted_alphabet_list = [segment.symbol for segment in restricted_alphabet]
            logger.info("Alphabet: {}".format(restricted_alphabet_list))
        logger.info("{}".format(self.current_hypothesis.grammar.lexicon))
        logger.info("Parse: {}".format(self.current_hypothesis.get_recent_data_parse()))
        logger.info(self.current_hypothesis.get_recent_energy_signature())
        if self.target_energy:
            energy_delta = self.current_hypothesis.combined_energy - self.target_energy
            logger.info("Distance from target energy: {:,}".format(energy_delta))


        if self.target_lexicon_indicator_function:
            lexicon_string_words = [str(word) for word in self.current_hypothesis.grammar.lexicon.get_words()]
            logger.info(self.target_lexicon_indicator_function(lexicon_string_words))

        if self.target_data:
            outputs = self.current_hypothesis.grammar.get_all_outputs_grammar(new_string_word_list=self.sample_target_lexicon)
            string_outputs = [str(word) for word in outputs]
            outputs_set = set(string_outputs)
            desired_outputs_set = set(self.sample_target_outputs)
            target_grammar_parse_indicator = outputs_set == desired_outputs_set
            logger.info("Desired grammar: {}".format(target_grammar_parse_indicator))


    @staticmethod
    def _get_memory_usage():
        p = subprocess.Popen("ps -o rss= -p {}".format(process_id), stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        return int((int(output)/1024))  #memory usage in MB

    @staticmethod
    def _calculate_num_of_steps():
        step = 0
        temp = configurations["INITIAL_TEMPERATURE"]
        while temp > configurations["THRESHOLD"]:
            step += 1
            temp *= configurations["COOLING_PARAMETER"]
        return step

    def clear_modules_caching(self):

        if True:
            Grammar.clear_caching()
            ConstraintSet.clear_caching()
            Constraint.clear_caching()
            Word.clear_caching()

        diagnostics_flag = False
        if diagnostics_flag:
            def object_size_in_mb(object_):
                from pympler.asizeof import asizeof

                return int((asizeof(object_) / (1024 ** 2)))

            import grammar.grammar
            import grammar.constraint_set
            import grammar.constraint
            import grammar.lexicon

            outputs_by_constraint_set_and_word_size = object_size_in_mb(
                grammar.grammar.outputs_by_constraint_set_and_word)
            grammar_transducers_size = object_size_in_mb(grammar.grammar.grammar_transducers)
            constraint_set_transducers_size = object_size_in_mb(grammar.constraint_set.constraint_set_transducers)
            constraint_transducers_size = object_size_in_mb(grammar.constraint.constraint_transducers)
            word_transducers_size = object_size_in_mb(grammar.lexicon.word_transducers)

            logger.info(
                "asizeof outputs_by_constraint_set_and_word: {} MB".format(outputs_by_constraint_set_and_word_size))
            logger.info("length outputs_by_constraint_set_and_word: {}".format(
                len(grammar.grammar.outputs_by_constraint_set_and_word)))

            logger.info("asizeof grammar_transducers: {} MB".format(grammar_transducers_size))
            logger.info("length grammar_transducers: {}".format(len(grammar.grammar.grammar_transducers)))
            logger.info("asizeof constraint_set_transducers: {} MB".format(constraint_set_transducers_size))
            logger.info("asizeof constraint_transducers: {} MB".format(constraint_transducers_size))

            logger.info("asizeof word_transducers: {} MB".format(word_transducers_size))
            logger.info("length word_transducers: {}".format(len(grammar.lexicon.word_transducers)))

            sum_asizeof = outputs_by_constraint_set_and_word_size + grammar_transducers_size + \
                          constraint_set_transducers_size + constraint_transducers_size + \
                          word_transducers_size

            logger.info("sum asizeof: {} MB".format(sum_asizeof))

            logger.info("Memory usage: {} MB".format(self._get_memory_usage()))


def _pretty_runtime_str(run_time_in_seconds):
    time_delta = timedelta(seconds=run_time_in_seconds)
    timedelta_string = str(time_delta)

    m = re.search('(\d* (days|day), )?(\d*):(\d*):(\d*)', timedelta_string)
    days_string = m.group(1)
    hours = int(m.group(3))
    minutes = int(m.group(4))
    seconds = int(m.group(5))

    if days_string:
        days_string = days_string[:-2]
        return "{}, {} hours, {} minutes, {} seconds".format(days_string, hours, minutes, seconds)
    elif hours:
        return "{} hours, {} minutes, {} seconds".format(hours, minutes, seconds)
    elif minutes:
        return "{} minutes, {} seconds".format(minutes, seconds)
    else:
        return "{} seconds".format(seconds)



