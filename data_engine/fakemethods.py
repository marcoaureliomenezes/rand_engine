from numpy.random import randint
import random, unittest
from numpy.random import rand, randint
import numpy as np
from numpy.random import rand, randint
from functools import reduce
from core import *
from utils import *


def fake_int(size=5, **kwargs):
    min = normalize_param(kwargs, "min", int, 0)
    max = normalize_param(kwargs, "max", int, 10)
    algnum = normalize_param(kwargs, "algnum", bool, False)
    if not algnum:
        result = random_int(min, max, size)
    else:  
        result = random_int10(min, max, size)
    return handle_num_format(result, **kwargs)

def fake_float(size=5, **kwargs):
    min = normalize_param(kwargs, "min", int, 0)
    max = normalize_param(kwargs, "max", int, 10)
    mean = normalize_param(kwargs, "mean", float, 1)
    std = normalize_param(kwargs, "std", float, 0.2)
    round = normalize_param(kwargs, "round", int, 0)
    algnum = normalize_param(kwargs, "algnum", bool, False)
    if kwargs.get("type") == "normal":
        result = random_float_normal(mean, std, size).round(round)
    elif not algnum:
        result = random_float(min, max, size, round)
    else:
        result = random_float10(min, max, size, round)
    return handle_num_format(result, **kwargs)


def fake_discrete(size=5, **kwargs):
    distinct = normalize_param(kwargs, "distinct", list, None)
    distinct_elem = distinct[0]
    if not distinct:
        return ["" for i in range(size)]
    if len(distinct) > 0 and type(distinct_elem) is list:
        result = random_multi_word(size, values=distinct)
    elif type(distinct_elem is str):
        result = random_single_word(size, distinct)
    return handle_string_format(result, **kwargs)


def fake_alphanum(size=5, **kwargs):
    format = normalize_param(kwargs, "format", str, "2222")
    distinct = normalize_param(kwargs, "distinct", list, None)
    sep = normalize_param(kwargs, "sep", str, "")
    if not format:
        return ["" for i in range(size)]
    result = random_alphanum(size, format)
    result = fake_concat(sep, fake_discrete(size=size, **kwargs), result) if distinct else result
    return handle_string_format(result, **kwargs)


def fake_date(size=5, **kwargs):
    start = normalize_param(kwargs, "start", str, "01-01-2020")
    end = normalize_param(kwargs, "end", str, "31-12-2020")
    format = normalize_param(kwargs, "format", str, "%d-%m-%Y")
    interval = get_interval(start=start, end=end, date_format=format)
    int_array = randint(interval[0], interval[1], size)
    return format_date_array(int_array, format)

def fake_partition(size=5, **kwargs):
    start = normalize_param(kwargs, "start", str, "01-01-2020")
    end = normalize_param(kwargs, "end", str, "31-12-2020")
    format = normalize_param(kwargs, "format", str, "%d-%m-%Y")
    num_part = normalize_param(kwargs, "num_part", int, 2)
    interval = get_interval(start, end, format)  
    times = spaced_array(interval, num_part)
    result = reduce_array(size, base_array=times) if num_part >= size \
        else expand_array(size=size, base_array=times)
    result.sort()
    return format_date_array(result, format)


from performance import transform_assign 
from names import *

class TestFakeMethodsMethods(unittest.TestCase):

    size = 10
    # def test_fake_int(self):
    #     def fake_int_output(size):
    #         transform_assign(fake_int, min=0, max=10, size=size)
    #         transform_assign(fake_int, min=100, max=1000, size=size)
    #         transform_assign(fake_int, min=3, max=6, algnum=True, size=size)
    #         transform_assign(fake_int, min=3, max=6, algnum=True, algsize=10, size=size)
    #     fake_int_output(self.size)

    # def test_fake_float(self):
    #     def fake_float_output(size):
    #         transform_assign(fake_float, min=0, max=10, round=2, size=size)
    #         transform_assign(fake_float, min=0, max=1000, round=2, size=size)
    #         transform_assign(fake_float, min=-1000, max=1000, round=4, size=size)
    #         transform_assign(fake_float, min=4, max=7, algnum=True, round=2, size=size)
    #         transform_assign(fake_float, min=4, max=7, algnum=True, algsize=10, round=2, size=size)
    #         transform_assign(fake_float, type="normal", mean=1000, std=200, size=size)
    #         transform_assign(fake_float, type="normal", mean=1000, std=200, round=2, size=size)
    #     fake_float_output(self.size)

    # def test_fake_discrete(self):
    #     def fake_discrete_output(size):
    #         transform_assign(random_single_word, values=["value_1","value_2","value_3"], size=size)
    #         transform_assign(random_single_word, values=names, size=size)
    #         transform_assign(random_multi_word, values=[names, last_names], size=size)
    #     fake_discrete_output(self.size)

    # def test_random_alphanum(self):
    #     def random_alphanum_output(size):
    #         transform_assign(random_alphanum, format="aaa222", size=size)
    #     random_alphanum_output(self.size)

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