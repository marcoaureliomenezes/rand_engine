# Codigo escrito por Marco Menezes

import random, math, itertools, unittest
from numpy.random import rand, randint
from dateutil import parser
from datetime import datetime
import numpy as np
from functools import reduce


def stringify(iterr, **kwargs):
    return str(iterr).zfill(kwargs["algsize"]) if ( kwargs.get("string") and kwargs.get("algsize")) \
                    else str(iterr) if kwargs.get("string") else iterr


def round_array(iterr, **kwargs):
    return round(iterr, kwargs["round"]) if kwargs.get("round") else round(iterr, 2)


def fake_int(size=5, **kwargs):
    if kwargs.get("min_size") and kwargs.get("max_size"):
        def random_int(**kw):
            return math.floor(random.random() * math.pow(10,
                         random.randint(kw.get("min_size"), (kw.get("max_size")))))
        result = [random_int(**kwargs) for i in range(size)]
        result = [stringify(i, **kwargs) for i in result]
        return result
    return [0 for i in range(size)]

def fake_float(size=5, **kwargs):
    if kwargs.get("min_size") and kwargs.get("max_size"):
        if kwargs.get("round"):
            return [int(i) / kwargs["round"] for i in
                fake_int(size=size, min_size=kwargs["min_size"] + kwargs["round"],
                    max_size=kwargs["max_size"] + kwargs["round"])]
        return [int(i)/2 for i in fake_int(size=size, min_size=kwargs["min_size"] + 2,
                                                    max_size=kwargs["max_size"] + 2)]
    return [0. for i in range(size)]


def fake_float_normal(size=5, **kwargs):
    def random_float_normal(**kw):
        return np.random.normal(kw["mean"], kw["std"]) if (kw.get("mean") and kw.get("std")) else 0.
    result = [random_float_normal(**kwargs) for i in range(size)]
    result = [round_array(i, **kwargs) for i in result]
    result = [stringify(i, **kwargs) for i in result]
    return result


def fake_alphanum(size=5, **kwargs):
    def random_alphanum(**kw):
        return np.array([np.array([chr(i) for i in randint(97, 123, size)]
            if i.isalpha() else [chr(i) for i in randint(48, 57, size)])
            for i in kw["format"]], dtype=object)
    if kwargs.get("format"):
        return reduce(lambda a, b: [a[i] + b[i] for i in range(len(b))], random_alphanum(**kwargs))
    return ["" for i in range(size)]


def fake_discrete(size=5, **kwargs):
    if(kwargs.get("distinct") is not None):
        aux = randint(0, len(kwargs["distinct"]), size)
        return [str(kwargs["distinct"][i]) for i in aux]


def fake_alphanum(size=5, **kwargs):
    def random_alphanum(**kw):
        return np.array([np.array([chr(i) for i in randint(97, 123, size)]
                if i.isalpha() else [chr(i) for i in randint(48, 57, size)])
                for i in kw["format"]], dtype=object)

    if kwargs.get("format"):
        return reduce(lambda a, b: [a[i] + b[i] for i in range(len(b))], random_alphanum(**kwargs))
    return ["" for i in range(size)]


def fake_date(size=5, **kwargs):
    interval = parser.parse(kwargs["start"]).timestamp(), parser.parse(kwargs["end"]).timestamp() \
        if kwargs.get("start") is not None and kwargs.get("start") is not None else (100000000, 100010000)
    int_array = randint(interval[0], interval[1], size)
    return [ datetime.fromtimestamp(i).strftime("%m/%d/%Y") for i in int_array ]


def fake_name(size=5, **kwargs):
    if kwargs["names"] and len(kwargs["names"]) > 0:
        result = [[arg[j] for j in randint(0, len(arg), size)] for arg in kwargs["names"]]
        return [reduce(lambda a, b: f"{a} {b}", fullname) for fullname in list(zip(*result))]
    return ["" for i in range(size)]


def fake_unique_name(size=5, **kwargs):
    if kwargs.get("names"):
        res = [reduce(lambda a, b: f"{a} {b}", i) for i in itertools.product(*kwargs["names"])]
        res = np.append(res, [None for i in range(size - len(res))]) if len(res) < size else res[0:size]
        np.random.shuffle(res)
        return res
    return ["" for i in range(size)]


class TestCoreMethods(unittest.TestCase):

    def test_fake_int(self):
        print("\n\nResults for FAKE_INT with different parameters")
        print(fake_int())
        print(fake_int(size=5, min_size=5, max_size=8))
        print(fake_int(size=5, min_size=5, max_size=8, string=True))
        print(fake_int(size=5, min_size=5, max_size=8, string=True, algsize=12))
        self.assertFalse('Foo'.isupper())

    def test_fake_float(self):
        print("\n\nResults for FAKE_FLOAT method with different parameters")
        # print(fake_float(size=5))
        print(fake_float(size=5, min_size=2, max_size=4))
        print(fake_float(size=5, min_size=2, max_size=4, round=2))
        print(fake_float(size=5, min_size=2, max_size=4, string=True, algsize=12))
        self.assertFalse('Foo'.isupper())

    def test_fake_float_normal(self):
        print("\n\nResults for FAKE_FLOAT_NORMAL with different parameters")
        print(fake_float_normal(size=5))
        print(fake_float_normal(size=5, mean=10000, std=3000))
        print(fake_float_normal(size=5, mean=10000, std=3000, round=2))
        print(fake_float_normal(size=10, mean=10000, std=3000, string=True, algsize=12))
        self.assertFalse('Foo'.isupper())

    def test_fake_discrete(self):
        print("\n\nResults for FAKE_DISCRETE with different parameters")
        print(fake_discrete(size=5, distinct=["valor1","valor2","valor3"]))
        print(fake_discrete(size=5, distinct=[1, 2, "NULL"]))
        print(fake_discrete(size=5, distinct=["gado", "etherium", "bitcoin"]))
        self.assertFalse('Foo'.isupper())

    def test_fake_alphanum(self):
        print("\n\nResults for FAKE_ALPHANUM with different parameters")
        print(fake_alphanum(size=5, format="abc123"))
        print(fake_alphanum(size=5, format="22123"))
        print(fake_alphanum(size=5, format="abcb"))
        self.assertFalse('Foo'.isupper())

    def test_fake_date(self):
        print("\n\nResults for FAKE_ALPHANUM with different parameters")
        print(fake_date(size=5, start="06-02-2020", end="08-02-2020"))
        print(fake_date(size=5, start="06-02/2020", end="08/02-2020"))
        print(fake_date(size=5, start="01/20/2021", end="12-20-2021"))
        self.assertFalse('Foo'.isupper())


    def test_fake_name(self):
        print("\n\nResults for FAKE_NAME with different parameters")
        print("\n", fake_name(size=10, names=[["marco","fabio","henrique"],["santander"]]))
        print("\n", fake_name(size=10, names=[["marco","henrique"],["barbosa","reis"],["lima","menezes"]]))
        self.assertFalse('Foo'.isupper())


    def test_fake_unique_name(self):
        print("\n\nResults for FAKE_UNIQUE_NAME with different parameters")
        print("\n", fake_unique_name(size=10, names=[["marco","fabio","henrique"],["santander"]]))
        print("\n", fake_unique_name(size=10, names=[["marco","henrique"],["barbosa","reis"],["lima","menezes"]]))
        self.assertFalse('Foo'.isupper())
if __name__ == '__main__':
    unittest.main()
