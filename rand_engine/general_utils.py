import numpy as np

def expand_array(size=10, base_array=[]):
    return [base_array[int(i % len(base_array))] for i in range(size)]

def reduce_array(size=10, base_array=[]):
    int_array = [int(i) for i in np.linspace(0, size-1, len(base_array))]
    reduced = [int_array.index(i) for i in range(size)]
    result = [base_array[i] for i in reduced]
    return result


def spaced_array(interval, num_part=2):
    return list(np.linspace(interval[0], interval[1], num_part))