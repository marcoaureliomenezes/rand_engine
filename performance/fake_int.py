import math, random
import numpy as np
from numpy import array, concatenate
from functools import reduce
from numpy.random import rand, randint
from perform import performance 


def stringfy(iterr, **kwargs):
    return str(iterr).zfill(kwargs["algsize"]) if ( kwargs.get("string") and kwargs.get("algsize")) \
                    else str(iterr) if kwargs.get("string") else iterr 

@performance
def fake_int_1(size=5, **kwargs):
    """
    Parameters:
    size (int): size of the output integer array
    kwargs["min_size"] (int): min value of the floats values in the array
    kwargs["max_size"] (int): max value of the floats values in the array
    Returns:
    list(floats):Returns a list of random floats
    """
    if kwargs.get("min_size") and kwargs.get("min_size"):
        fake_int = lambda iterr, **kwargs: \
            randint(math.pow(10,(kwargs["min_size"] - 1)), math.pow(10, iterr))
        length_array = np.random.randint(kwargs["min_size"], kwargs["max_size"] + 1, size)
        result = [fake_int(length, **kwargs) for length in length_array]
        result = [ stringfy(i, **kwargs) for i in result ]
        return result
    return [0 for i in range(size)]

# Esse método cria uma coluna de identificadores únicos
@performance
def fake_int_2(size=5, **kwargs):
    """
    Parameters:
    size (int): size of the output name array
    kwargs["min_size"] (int): min value of the floats values in the array
    kwargs["max_size"] (int): max value of the floats values in the array
    Returns:
    list(floats):Returns a list of random floats
    """
    if kwargs.get("min_size") and kwargs.get("max_size"):
        fake_int = lambda **kwargs: \
            math.floor(random.random() * math.pow(10,
                         random.randint(kwargs.get("min_size"), (kwargs.get("max_size")))))
        result = [fake_int(**kwargs) for i in range(size)]
        result = [ stringfy(i, **kwargs) for i in result ]
        return result
    return [0 for i in range(size)]


@performance
def fake_int_3(size=5, **kwargs):
    """
    Parameters:
    size (int): size of the output name array
    kwargs["min_size"] (int): min value of the floats values in the array
    kwargs["max_size"] (int): max value of the floats values in the array
    Returns:
    list(integer): Returns a list of random floats
    """
    if kwargs.get("min_size") and kwargs.get("max_size"):
        sizes = randint(kwargs["min_size"], kwargs["max_size"] + 1, size)
        result = list(map(lambda x: randint(kwargs["min_size"], 10 ** x), sizes))
        result = [ stringfy(i, **kwargs) for i in result ]
        return result
    return [0 for i in range(size)]


import unittest

class TestCoreMethods(unittest.TestCase):

    def test_fake_int_1(self):
        # print(fake_int_1(size=5, min_size=5, max_size=8))
        # print(fake_int_1(size=5, min_size=5, max_size=8, string=True))
        # print(fake_int_1(size=5, min_size=5, max_size=8, string=True, algsize=12))
        fake_int_1(size=1000000, min_size=5, max_size=8, string=True, algsize=12)
        self.assertFalse('Foo'.isupper())


    def test_fake_int_2(self):
        # print(fake_int_2(size=5, min_size=5, max_size=8))
        # print(fake_int_2(size=5, min_size=5, max_size=8, string=True))
        # print(fake_int_2(size=5, min_size=5, max_size=8, string=True, algsize=12))
        fake_int_2(size=1000000, min_size=5, max_size=8, string=True, algsize=12)
        self.assertFalse('Foo'.isupper())

    def test_fake_int_3(self):
        # print(fake_int_3(size=5, min_size=5, max_size=8))
        # print(fake_int_3(size=5, min_size=5, max_size=8, string=True))
        # print(fake_int_3(size=5, min_size=5, max_size=8, string=True, algsize=12))
        fake_int_3(size=1000000, min_size=5, max_size=8, string=True, algsize=12)
        self.assertFalse('Foo'.isupper())


if __name__ == '__main__':
    unittest.main()