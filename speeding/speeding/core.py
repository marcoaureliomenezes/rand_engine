# Codigo escrito por Marco Menezes

import random
from numpy.random import rand, randint
from dateutil import parser
from datetime import datetime
import numpy as np
from functools import reduce
import itertools, string


def fake_discrete(size=5, **kwargs):
    if(kwargs.get("distinct") is not None):
        aux = randint(0, len(kwargs["distinct"]), size)
        return [str(kwargs["distinct"][i]) for i in aux]


def fake_num(size=5, **kwargs):
    tam = randint(kwargs["min_size"],kwargs["max_size"] + 1, size) \
            if kwargs.get("min_size") is not None and kwargs.get("max_size") is not None else None
    return [ str(randint(0,10 ** tam[i])).zfill(tam[i]) for i in range(size) ]


def fake_date(size=5, **kwargs):
    interval = parser.parse(kwargs["start"]).timestamp(), parser.parse(kwargs["end"]).timestamp() \
        if kwargs.get("start") is not None and kwargs.get("start") is not None else 2
    int_array = randint(interval[0], interval[1], size)
    return [ datetime.fromtimestamp(i).strftime("%m/%d/%Y") for i in int_array ]


def fake_date(size=5, **kwargs):
    interval = parser.parse(kwargs["start"]).timestamp(), parser.parse(kwargs["end"]).timestamp() \
        if kwargs.get("start") is not None and kwargs.get("start") is not None else 2
    int_array = randint(interval[0], interval[1], size)
    return [ datetime.fromtimestamp(i).strftime("%m/%d/%Y") for i in int_array ]


def fake_name(*args, size=5, **kwargs):
    if len(args) > 0:
        concat_name = [[ arg[j] for j in randint(0, len(arg), size)] for arg in args]
        return [reduce(lambda a, b: f"{a} {b}",nometodo) for nometodo in list(zip(*concat_name))]
    return ["" for i in range(size)]


def fake_name_unique(*args, size=5, **kwargs):
    if len(args) > 0:
        return [reduce(lambda a,b: f"{a} {b}", i) for i in itertools.product(*args)]
    return ["" for i in range(size)]

def fake_float(size=5,**kwargs):
    if kwargs.get("min") is not None and kwargs.get("max") is not None:
        result = [round((np.random.rand()+1)*(kwargs["max"]-kwargs["min"]), 2) for i in range(size)]
        if kwargs.get("lzero") is not None:
            return [str(i).zfill(kwargs["lzero"]) for i in result]
        return result
    return [0. for i in range(size)]

def fake_float_normal(size=5, min=10, max=20, **kwargs):
    return np.random.normal(200000, 40000, 10)


def fake_string(size=5, formata="a2b3", **kwargs):
    return  [reduce(lambda a, b: a+b, [random.choice(string.ascii_letters)
                    if i.isalpha() else str(randint(0,10)) for i in formata])
                    for i in range(size)]
    
    

import unittest


class TestCoreMethods(unittest.TestCase):

    # def test_fake_categorical(self):
    #     res = fake_discrete(distinct=["ccorrent", "cpoupanca"])
    #     self.assertEqual(list(np.unique(res)), ["ccorrent", "cpoupanca"])

    # def test_fake_num(self):
    #     res = fake_num(min_size=5, max_size=10)
    #     sizes = [True if j in range(5, 11) else False for j in [ len(i) for i in res]]
    #     self.assertFalse('Foo'.isupper())

    # def test_fake_date(self):
    #     print(fake_date(start="20-02-2020", end="27-05-2020"))
    #     self.assertFalse('Foo'.isupper())

    # def test_fake_name(self):
    #     print(fake_name(["marco", "josé"], ["santander"],size=20))
    #     self.assertFalse('Foo'.isupper())

    # def test_fake_name_unique(self):
    #     print(fake_name_unique(["marco", "josé"], ["santander", "schmidt"], ["ribeiro", "golçalves"],size=20))
    #     self.assertFalse('Foo'.isupper())

    # def test_fake_float(self):
    #     print(fake_float(min=100, max=2000, lzero=10))
    #     self.assertFalse('Foo'.isupper())

    def test_fake_string(self):
        a = fake_string(size=2000000)
        self.assertFalse('Foo'.isupper())

if __name__ == '__main__':
    unittest.main()
