import random
import numpy as np
from numpy import array, concatenate
import time
from functools import reduce
from numpy.random import randint
from perform import performance 


def round_array(iterr, **kwargs):
    return round(iterr, kwargs["round"]) if kwargs.get("round") else round(iterr,2)

def stringfy(iterr, **kwargs):
    return str(iterr).zfill(kwargs["algsize"]) if ( kwargs.get("string") and kwargs.get("algsize")) \
                    else str(iterr) if kwargs.get("string") else iterr 

# Esse método cria uma coluna de identificadores únicos
@performance
def fake_float_1(size=5,**kwargs):
    """ 
    Parameters:
    size (int): size of the output name array
    kwargs["min"] (int): min value of the floats values in the array

    Returns:
    list(floats):Returns a list of random floats
    """
    random_float = lambda **kwargs: (np.random.rand()+1)*(kwargs["max"]-kwargs["min"]) if \
        kwargs.get("min") and kwargs.get("max") else 0.
    result = [random_float(**kwargs) for i in range(size)]
    result = [round_array(i, **kwargs) for i in result]
    result = [ stringfy(i, **kwargs) for i in result ]
    return result

@performance
def fake_float_2(size=5,**kwargs):
    """
    Parameters:
    size (int): size of the output name array
    kwargs["min_size"] (int): min value of the floats values in the array
    kwargs["max_size"] (int): max value of the floats values in the array
    Returns:
    list(floats):Returns a list of random floats
    """
    random_float = lambda **kwargs: \
        (np.random.rand()+1)*((10 ** kwargs["min_size"])-(10 ** kwargs["min_size"])  \
            if kwargs.get("min_size") and kwargs.get("max_size") else 0.)
    result = [random_float(**kwargs) for i in range(size)]
    result = [round_array(i, **kwargs) for i in result]
    result = [stringfy(i, **kwargs) for i in result]
    return result

@performance
def fake_float_normal(size=5, **kwargs):
    """
    Parameters:
    size (int): size of the output name array
    kwargs["min_size"] (int): min value of the floats values in the array
    kwargs["max_size"] (int): max value of the floats values in the array
    Returns:
    list(floats):Returns a list of random normal floats
    """
    random_float = lambda **kwargs: np.random.normal(kwargs["mean"], kwargs["std"]) \
        if (kwargs.get("mean") and kwargs.get("std")) else 0.
    result = [random_float(**kwargs) for i in range(size)] 
    result = [round_array(i, **kwargs) for i in result]
    result = [ stringfy(i, **kwargs) for i in result]
    return result

import unittest

class TestCoreMethods(unittest.TestCase):

    def test_fake_float1(self):
        # print(fake_float_1(size=10, min=200, max=1000, round= 2, string=True, algsize=12))
        print("######################################################################")
        fake_float_1(size=1000000)
        fake_float_1(size=1000000, min=200, max=1000)
        fake_float_1(size=1000000, min=200, max=1000, round= 2)
        fake_float_1(size=1000000, min=200, max=1000, round= 2, string=True, algsize=12)
        self.assertFalse('Foo'.isupper())

    def test_fake_float_2(self):
        # print(fake_float_2(size=10, min_size=2, max_size=4, string=True, algsize=12))
        print("######################################################################")
        fake_float_1(size=1000000)
        fake_float_1(size=1000000, min_size=200, max_size=1000)
        fake_float_1(size=1000000, min_size=200, max_size=1000, round=2)
        fake_float_2(size=1000000, min_size=2, max_size=4, string=True, algsize=12)
        self.assertFalse('Foo'.isupper())

    def test_fake_float_normal(self):
        # print(fake_float_normal(size=5, mean=10, std=2, string=True, algsize=12))
        print("######################################################################")
        fake_float_normal(size=1000000)
        fake_float_normal(size=1000000, mean=10, std=2)
        fake_float_normal(size=1000000, mean=10, std=2, string=True, algsize=12)
        self.assertFalse('Foo'.isupper())

    # def test_fake_float_normal2(self):
    #     print(fake_float_normal(size=5, mean=10, std=2))
    #     fake_float_normal(size=1000000, mean=10, std=2)
    #     self.assertFalse('Foo'.isupper())

if __name__ == '__main__':
    unittest.main()