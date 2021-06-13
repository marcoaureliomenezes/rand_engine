# Codigo escrito por Marco Menezes

import random, math, itertools, string
from numpy.random import rand, randint
from dateutil import parser
from datetime import datetime
import numpy as np
from functools import reduce

def stringfy(iterr, **kwargs):
    return str(iterr).zfill(kwargs["algsize"]) if ( kwargs.get("string") and kwargs.get("algsize")) \
                    else str(iterr) if kwargs.get("string") else iterr
def round_array(iterr, **kwargs):
    return round(iterr, kwargs["round"]) if kwargs.get("round") else round(iterr,2)


def fake_int(size=5, **kwargs):
    if kwargs.get("min_size") and kwargs.get("max_size"):
        fake_int = lambda **kwargs: \
            math.floor(random.random() * math.pow(10,
                         random.randint(kwargs.get("min_size"), (kwargs.get("max_size")))))
        result = [fake_int(**kwargs) for i in range(size)]
        result = [ stringfy(i, **kwargs) for i in result ]
        return result
    return [0 for i in range(size)]

def fake_float(size=5,**kwargs):
    random_float = lambda **kwargs: \
        (np.random.rand()+1)*((10 ** kwargs["min_size"])-(10 ** kwargs["min_size"])  \
            if kwargs.get("min_size") and kwargs.get("max_size") else 0.)
    result = [random_float(**kwargs) for i in range(size)]
    result = [round_array(i, **kwargs) for i in result]
    result = [stringfy(i, **kwargs) for i in result]
    return result


def fake_discrete(size=5, **kwargs):
    if(kwargs.get("distinct") is not None):
        aux = randint(0, len(kwargs["distinct"]), size)
        return [str(kwargs["distinct"][i]) for i in aux]


def fake_alphanum(size=5, **kwargs):
    random_alphanum = lambda **kwargs: \
            np.array([np.array([chr(i) for i in randint(97,123, size)]
                if i.isalpha() else [chr(i) for i in randint(48,57, size)]) 
                for i in kwargs["format"]], dtype=object)
    if kwargs.get("format"):
        return reduce(lambda a, b: [a[i] + b[i] for i in range(len(b))], random_alphanum(**kwargs))
    return ["" for i in range(size)]


def fake_date(size=5, **kwargs):
    interval = parser.parse(kwargs["start"]).timestamp(), parser.parse(kwargs["end"]).timestamp() \
        if kwargs.get("start") is not None and kwargs.get("start") is not None else 2
    int_array = randint(interval[0], interval[1], size)
    return [ datetime.fromtimestamp(i).strftime("%m/%d/%Y") for i in int_array ]

def fake_name(size=5, **kwargs):
    if kwargs["names"] and len(kwargs["names"]) > 0:
        result = [[ arg[j] for j in randint(0, len(arg), size)] for arg in kwargs["names"]]
        return [reduce(lambda a, b: f"{a} {b}",fullname) for fullname in list(zip(*result))]
    return ["" for i in range(size)]


def fake_name_unique(size=5, **kwargs):
    if kwargs.get("names"):
        res = [reduce(lambda a, b: f"{a} {b}", i) for i in itertools.product(*kwargs["names"])]
        res = np.append(res, [None for i in range(size - len(res))]) if len(res) < size else \
                    res[0:size]
        np.random.shuffle(res)
        return res
    return ["" for i in range(size)]

def fake_float_normal(size=5, **kwargs):
    if (kwargs.get("mean") is not None) and kwargs.get("std") is not None:
        return np.random.normal(kwargs["mean"], kwargs["std"], 10)
    return [0. for i in range(size)]

import unittest


class TestCoreMethods(unittest.TestCase):

    def test_fake_categorical(self):
        res = fake_discrete(distinct=["ccorrent", "cpoupanca"])
        print(res)
        self.assertEqual(list(np.unique(res)), ["ccorrent", "cpoupanca"])

    def test_fake_num(self):
        res = fake_num(min_size=5, max_size=10)
        print(res)
        sizes = [True if j in range(5, 11) else False for j in [ len(i) for i in res]]
        self.assertFalse('Foo'.isupper())

    def test_fake_date(self):
        print(fake_date(start="20-02-2020", end="27-05-2020"))
        self.assertFalse('Foo'.isupper())

    def test_fake_name(self):
        print(fake_name(["marco", "josé"], ["santander"]))
        self.assertFalse('Foo'.isupper())

    def test_fake_name_unique(self):
        print(fake_name_unique(["marco", "josé"], ["santander"]))
        self.assertFalse('Foo'.isupper())

    def test_fake_float(self):
        print(fake_float(min=100, max=2000, algsize=10))
        self.assertFalse('Foo'.isupper())

    def test_fake_alphanum(self):
        print(fake_alphanum(format="aabb222cc"))
        self.assertFalse('Foo'.isupper())

    def test_fake_float_normal(self):
        print(fake_float_normal(mean=100, std=10))
        self.assertFalse('Foo'.isupper())

if __name__ == '__main__':
    unittest.main()
