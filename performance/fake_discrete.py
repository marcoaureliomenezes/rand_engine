from numpy.random import randint
import sys, time
import numpy as np
from perform import performance 



@performance
def fake_discrete_1(size=5, **kwargs):
    random_word = lambda **kwargs: \
            kwargs["distinct"][randint(0, len(kwargs["distinct"]))]
    if kwargs.get("distinct"):
        return [random_word(**kwargs) for i in range(size)]
    return ["" for i in range(size)]

@performance
def fake_discrete_2(size=5, **kwargs):
    if kwargs.get("distinct"):
        aux = randint(0, len(kwargs["distinct"]), size)
        return [kwargs["distinct"] for i in range(size)]
   
    return ["" for i in range(size)]


import unittest

class TestCoreMethods(unittest.TestCase):

    def test_fake_discrete_1(self):
        print("######################################################################")
        # print(fake_discrete_1(size=10, distinct=["val-1", "val-2"]))
        fake_discrete_1(size=1000000)
        fake_discrete_1(size=1000000, distinct=["val-1", "val-2"])
        self.assertFalse('Foo'.isupper())


    def test_fake_discrete_2(self):
        print("######################################################################")
        # print(fake_discrete_2(size=5, distinct=["val-1", "val-2"]))
        fake_discrete_2(size=1000000)
        fake_discrete_2(size=1000000, distinct=["val-1", "val-2"])
        self.assertFalse('Foo'.isupper())


if __name__ == '__main__':
    unittest.main()