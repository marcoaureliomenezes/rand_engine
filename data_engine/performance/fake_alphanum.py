import random, string
import numpy as np
from numpy import array, concatenate
from functools import reduce
from numpy.random import randint
from perform import performance
from utils import *

# @performance
def fake_alphanum_1(size=5, **kwargs):
    random_alphanum = lambda **kwargs: \
        reduce(lambda a, b: a+b, [random.choice(string.ascii_letters)
        if j.isalpha() else str(randint(0,10)) for j in kwargs["format"]])
    return  [random_alphanum(**kwargs) if kwargs.get("format") else "" for i in range(size)]

# @performance
def fake_alphanum_2(size=5, **kwargs):
    if not kwargs.get("format"):
        return ["" for i in range(size)]
    result = reduce(lambda a, b: [a[i] + b[i] for i in range(len(b))], 
    np.array([np.array([chr(i) for i in randint(97,123, size)]
                if i.isalpha() else [chr(i) for i in randint(48,57, size)]) 
                for i in kwargs["format"]], dtype=object))
    result = change_case(result, method=str.capitalize) if kwargs.get("let_case") == "cap" else result
    result = change_case(result, method=str.lower) if kwargs.get("let_case") == "lower" else result
    result = change_case(result, method=str.upper) if kwargs.get("let_case") == "upper" else result
    return result

import unittest

class TestCoreMethods(unittest.TestCase):

    def test_fake_alphanum_1(self):
        print("\ntest alphanumeric method 1: ")
        print(fake_alphanum_1(size=4, format="abc123"))
        # fake_alphanum_1(size=1000000)
        # a = fake_alphanum_1(size=1000000, format="abc123")
        # print("5 primeiros valores: ", a[0:5])
        self.assertFalse('Foo'.isupper())

    def test_fake_alphanum_2(self):
        print("\ntest alphanumeric method 2: ")
        print(fake_alphanum_2(size=5, format="abc123", let_case="upper"))
        # fake_alphanum_2(size=1000000)
        # a = fake_alphanum_2(size=1000000, format="abc123")
        # print("5 primeiros valores: ", a[0:5])
        self.assertFalse('Foo'.isupper())

if __name__ == '__main__':
    unittest.main()