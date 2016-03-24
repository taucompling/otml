import os
import time
from collections import defaultdict

dirname, filename = os.path.split(os.path.abspath(__file__))
dot_files_folder_path = os.path.join(dirname, "logging/dot_files")


def write_to_dot(transducer, file_name):
            open(os.path.join(dot_files_folder_path, file_name+".dot"), "w").write(transducer.dot_representation())

run_times_by_function_names = defaultdict(list)


def timeit(method):

    def timed(*args, **kw):
        start_time = time.time()
        result = method(*args, **kw)
        end_time = time.time()
        delta = end_time - start_time
        run_times_by_function_names[method.__name__].append(delta)

        return result

    return timed




def get_time_string(time):
    if time > 1:
        time_string = "{0:.1f} seconds".format(time)
        if time > 60:
            from simulated_annealing import _pretty_runtime_str
            time_string = _pretty_runtime_str(time)
    else:
        time *= 1000
        if time > 1:
            time_string = "{0:.0f} milliseconds".format(time)
        else:
            time *= 1000
            time_string = "{0:.0f} microseconds".format(time)

    return time_string


def get_statistics():
    statistics = dict()
    for function_name in run_times_by_function_names:
        statistics[function_name] = get_time_string(sum(run_times_by_function_names[function_name]))
    return statistics

N = (10**1)

@timeit
def function_to_time():
    x = 0
    for i in range(N):
        x += 1
    return x

if __name__ == "__main__":
    function_to_time()


