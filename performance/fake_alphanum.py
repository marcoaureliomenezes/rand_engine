import random, string
import numpy as np
from numpy import array, concatenate
from functools import reduce
from numpy.random import randint
from perform import performance 

@performance
def fake_alphanum_1(size=5, **kwargs):
    """
    Parameters:
    size (int): size of the output name array
    kwargs["min_size"] (int): min value of the floats values in the array
    kwargs["max_size"] (int): max value of the floats values in the array
    Returns:
    list(floats):Returns a list of random floats
    """
    random_alphanum = lambda **kwargs: \
        reduce(lambda a, b: a+b, [random.choice(string.ascii_letters)
        if j.isalpha() else str(randint(0,10)) for j in kwargs["format"]])
    return  [random_alphanum(**kwargs) if kwargs.get("format") else "" for i in range(size)]

@performance
def fake_alphanum_2(size=5, **kwargs):
    """
    Parameters:
    size (int): size of the output name array
    kwargs["min_size"] (int): min value of the floats values in the array
    kwargs["max_size"] (int): max value of the floats values in the array
    Returns:
    list(floats):Returns a list of random floats
    """
    random_alphanum = lambda **kwargs: \
            np.array([np.array([chr(i) for i in randint(97,123, size)]
                if i.isalpha() else [chr(i) for i in randint(48,57, size)]) 
                for i in kwargs["format"]], dtype=object)
    if kwargs.get("format"):
        return reduce(lambda a, b: [a[i] + b[i] for i in range(len(b))], random_alphanum(**kwargs))
    return ["" for i in range(size)]

import unittest

class TestCoreMethods(unittest.TestCase):

    def test_fake_alphanum_1(self):
        print(fake_alphanum_1(size=4, format="abc123"))
        fake_alphanum_1(size=1000000)
        fake_alphanum_1(size=1000000, format="abc123")
        self.assertFalse('Foo'.isupper())

    def test_fake_alphanum_2(self):
        print(fake_alphanum_2(size=5, format="abc123"))
        fake_alphanum_2(size=1000000)
        fake_alphanum_2(size=1000000, format="abc123")
        self.assertFalse('Foo'.isupper())

if __name__ == '__main__':
    unittest.main()