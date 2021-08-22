import unittest
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
    return reduce(lambda a, b: [a[i] + b[i] for i in range(len(b))], 
    np.array([np.array([chr(i) for i in randint(97,123, size)]
                if i.isalpha() else [chr(i) for i in randint(48,57, size)]) 
                for i in format], dtype=object))


from performance import transform_assign 
from names import *

class TestCoreMethods(unittest.TestCase):

    size = 10

    def test_random_int(self):
        def random_int_output(size):
            transform_assign(random_int, min=100, max=1000, size=size)
            transform_assign(random_int10, min=5, max=10, size=size)
        random_int_output(self.size)

    def test_random_float(self):
        def random_float_output(size):
            transform_assign(random_float, min=100, max=1000, round=2, size=size)
            transform_assign(random_float10, min=5, max=10, round=2, size=size)
            transform_assign(random_float_normal, mean=1000, std=200, size=size)
        random_float_output(self.size)

    def test_random_discrete(self):
        def random_discrete_output(size):
            transform_assign(random_single_word, values=["value_1","value_2","value_3"], size=size)
            transform_assign(random_single_word, values=names, size=size)
            transform_assign(random_multi_word, values=[names, last_names], size=size)
        random_discrete_output(self.size)

    def test_random_alphanum(self):
        def random_alphanum_output(size):
            transform_assign(random_alphanum, format="aaa222", size=size)
        random_alphanum_output(self.size)

if __name__ == '__main__':
    unittest.main()