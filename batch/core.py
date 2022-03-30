import numpy as np
from numpy.random import randint
from functools import reduce

def random_int(min, max, size):
    return list(np.random.randint(min, max + 1, size))

def random_int10(min, max, size):
    size_arr = np.random.randint(min, max, size)
    rand_floats = np.random.uniform(low=0, high=10, size=size)
    return np.multiply(rand_floats, 10**size_arr).astype("int")

def random_float(min, max, size, round):
    sig_part = np.random.randint(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part

def random_float10(min, max, size, round):
    sig_part = random_int10(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part

def random_float_normal(mean, std, size):
    return np.random.normal(loc=mean, scale=std, size=size)

def random_single_word(size, values):
    return list(map(lambda x: values[x], randint(0, len(values), size)))

def random_multi_word(size, values):
    result_array = [[arg[j] for j in randint(0, len(arg), size)] for arg in values]
    return [reduce(lambda a, b: f"{a} {b}", fullname) for fullname in list(zip(*result_array))]

def random_alphanum(size, format):
    def aux_method(format):
        ra = randint(0, len(format))
        res = chr(randint(48,57)) if format[ra].isdigit() else chr(randint(97, 123)) \
            if format[ra].isalpha() else format[ra]
        return format[0:ra] + res + format[ra+1:]
    return  [aux_method(format) for i in range(size)]

