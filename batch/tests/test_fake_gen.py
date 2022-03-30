from performance import transform_assign 
from utils.names import *
from batch.fake_gen import *
import unittest

class TestFakeMethodsMethods(unittest.TestCase):

    size = 10
    def test_fake_int(self):
        def fake_int_output(size):
            transform_assign(fake_int, min=0, max=10, size=size)
            transform_assign(fake_int, min=100, max=1000, size=size)
            transform_assign(fake_int, min=3, max=6, algnum=True, size=size)
            transform_assign(fake_int, min=3, max=6, algnum=True, algsize=10, size=size)
        fake_int_output(self.size)

    def test_fake_float(self):
        def fake_float_output(size):
            transform_assign(fake_float, min=0, max=10, round=2, size=size)
            transform_assign(fake_float, min=0, max=1000, round=2, size=size)
            transform_assign(fake_float, min=-1000, max=1000, round=4, size=size)
            transform_assign(fake_float, min=4, max=7, algnum=True, round=2, size=size)
            transform_assign(fake_float, min=4, max=7, algnum=True, algsize=10, round=2, size=size)
            transform_assign(fake_float, distribution="normal", mean=1000, std=200, size=size)
            transform_assign(fake_float, distribution="normal", mean=1000, std=200, round=2, size=size)
        fake_float_output(self.size)

    def test_fake_discrete(self):
        def fake_discrete_output(size):
            transform_assign(fake_discrete, size=size)
            transform_assign(fake_discrete, distinct=["value_1","value_2","value_3"], size=size)
            transform_assign(fake_discrete, distinct=names, size=size)
            transform_assign(fake_discrete, distinct=[names, last_names], size=size)
        fake_discrete_output(self.size)

    def test_random_alphanum(self):
        def random_alphanum_output(size):
            transform_assign(fake_alphanum, size=size)
            transform_assign(fake_alphanum, format="aaa.222", size=size)
            transform_assign(fake_alphanum, format="120.119.176-55", distinct=["PF","PJ"], size=size)
            transform_assign(fake_alphanum, format="120.119.176-55", sep="-",distinct=["PF","PJ"], size=size)
        random_alphanum_output(self.size)

    def test_random_date(self):
        def random_date_output(size):
            transform_assign(fake_date, size=size)
            transform_assign(fake_date, start="05/07/2021", end="10/08/2021", format="%d/%m/%Y",
            size=size)
        random_date_output(self.size)

    def test_random_partition(self):
        def random_partition_output(size):
            transform_assign(fake_partition, size=size)
            transform_assign(fake_partition, start="05/07/2021", end="10/08/2021", format="%d/%m/%Y",
            num_part=3, size=size)
        random_partition_output(self.size)

if __name__ == '__main__':

    unittest.main()