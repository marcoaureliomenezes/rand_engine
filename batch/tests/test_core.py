from performance import transform_assign
from batch.core import *
import unittest

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