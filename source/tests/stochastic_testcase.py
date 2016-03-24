#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

from copy import deepcopy
from unittest import TestCase



class StochasticTestError(Exception):
    pass

class StochasticTestCase(TestCase):
    def stochastic_object_method_testing(self, object_, method_name, possible_results, num_of_tests, possible_result_threshold,
                                         all_possible_result_flag=False, method_args=()):
        results = []
        for i in range(num_of_tests):
            copy_of_Object = deepcopy(object_)
            if not method_args:
                getattr(copy_of_Object, method_name)()
            else:
                getattr(copy_of_Object, method_name)(method_args)
            results.append(str(copy_of_Object))
        self.__result_checker(results, possible_results, possible_result_threshold, all_possible_result_flag)

    def stochastic_class_generate_random_testing(self, class_, possible_results, num_of_tests, possible_result_threshold,
                                                 all_possible_result_flag=False):

        results = []
        for i in range(num_of_tests):
            results.append(str(class_.generate_random(self.feature_table)))
        self.__result_checker(results, possible_results, possible_result_threshold, all_possible_result_flag)

    def __result_checker(self, results, possible_results, possible_result_threshold, all_possible_result_flag):
        if all_possible_result_flag:     # checks if there are no unexpected results
            for result in results:
                self.assertIn(result, possible_results)

        for result in possible_results:  # checks uniformity of distribution
            possible_results_count = results.count(result)
            self.assertGreaterEqual(possible_results_count, possible_result_threshold,
                                    "This is a stochastic test that may fail sometimes, "
                                    "readjust parameters if it fails too often: {0} < {1} for {2}".
                                    format(str(results.count(result)), str(possible_result_threshold), str(result)))

    def _return_number_of_different_results(self, object_, method_name, number_of_runs=300):
        results = set()
        for i in range(number_of_runs):
            copy_of_object = deepcopy(object_)
            getattr(copy_of_object, method_name)()   # getting the method and invoking it
            results.add(str(copy_of_object))
        print(results)
        return len(results)





