from fakemethods import *
from performance import loop_complexity
from names import *
import unittest

from performance import transform_assign 
from names import *

class TestFakeMethodsMethods(unittest.TestCase):

    size = 1000000

    def test_random_int_interval_param(self):
        def random_int_output(size):
            loop_complexity(fake_int, min=0, max=10, size=size)
            loop_complexity(fake_int, min=0, max=1000000, size=size)
        random_int_output(self.size)

    def test_random_int_algnum_param(self):
        def random_int_output(size):
            loop_complexity(fake_int, min=3, max=6, algnum=True, size=size)
            loop_complexity(fake_int, min=3, max=12, algnum=True, size=size)
            loop_complexity(fake_int, min=3, max=24, algnum=True, size=size)
        random_int_output(self.size)

    def test_random_float_interval_round_param(self):
        def random_float_output(size):
            loop_complexity(fake_float, min=0, max=10, round=2, size=size)
            loop_complexity(fake_float, min=0, max=1000000, round=2, size=size)
            loop_complexity(fake_float, min=0, max=10, round=10, size=size)
            loop_complexity(fake_float, min=0, max=1000000, round=10, size=size)
        random_float_output(self.size)

    def test_random_float_algsize_round_param(self):
        def random_float_output(size):
            loop_complexity(fake_float, min=5, max=10, algnum=True, round=2, size=size)
            loop_complexity(fake_float, min=5, max=20, algnum=True, round=10, size=size)
            loop_complexity(fake_float, min=5, max=50, algnum=True, round=10, size=size)
        random_float_output(self.size)

    def test_random_float_normal_round_param(self):
        def random_float_output(size):
            loop_complexity(fake_float, type="normal", mean=1000, std=200, size=size)
            loop_complexity(fake_float, type="normal", mean=1000, std=200, size=size)
            loop_complexity(fake_float, type="normal", mean=1000, std=200, round=2, size=size)
        random_float_output(self.size)

    def test_random_discrete_all_param(self):
        def random_discrete_output(size):
            loop_complexity(fake_discrete, size=size)
            loop_complexity(fake_discrete, distinct=["value1", "value2", "value3"], size=size)
            loop_complexity(fake_discrete, distinct=names , size=size)
            loop_complexity(fake_discrete, distinct=[names,last_names], size=size)
        random_discrete_output(self.size)

    def test_random_alphanum_all_param(self):
        def random_discrete_output(size):
            loop_complexity(fake_alphanum, size=size)
            loop_complexity(fake_alphanum, format="aa22", size=size)
            loop_complexity(fake_alphanum, format="aaaaaaa2222222", size=size)
            loop_complexity(fake_alphanum, format="aaaaaaaaaaaaaaa2222222222222222", size=size)
            loop_complexity(fake_alphanum, format="132.654.345-98", size=size)
        random_discrete_output(self.size)

    def test_random_date_all_param(self):
        def random_date_output(size):
            loop_complexity(fake_date, size=size)
            loop_complexity(fake_date, start="05/07/2021", end="10/08/2021", format="%d/%m/%Y",
                    size=size)
        random_date_output(self.size)

    def test_random_partition_all_param(self):
        def random_partition_output(size):
            loop_complexity(fake_partition, size=size)
            loop_complexity(fake_partition, start="05/07/2021", end="10/08/2021", format="%d/%m/%Y",
            num_part=3, size=size)
            loop_complexity(fake_partition, start="05/07/2021", end="10/08/2021", format="%d/%m/%Y",
            num_part=3000, size=size)
    
        random_partition_output(self.size)

if __name__ == '__main__':
    unittest.main()