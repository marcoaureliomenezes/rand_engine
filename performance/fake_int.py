""" fake_num_1 creates an array of randomic integer values between a specific interval
    of digit size.
    Strategy:

Parameters:
size (int): size of the output name array
kwargs["min_size"] (int): integer representing the min number of characters of the number
kwargs["max_size"] (int): integer representing the max number of characters of the number

Returns:
list(int):Returns a list of random integer numbers


fake_num_1 creates an array of randomic integer values between a specific interval
    of digit size.
    Strategy:

Parameters:
size (int): size of the output name array
kwargs["min_size"] (int): integer representing the min number of characters of the number
kwargs["max_size"] (int): integer representing the max number of characters of the number

Returns:
list(int):Returns a list of random integer numbers

fake_num_2 creates an array of randomic integer values between a specific interval
    of digit size.
    Strategy:

Parameters:
size (int): size of the output name array
kwargs["min_size"] (int): integer representing the min number of characters of the number
kwargs["max_size"] (int): integer representing the max number of characters of the number

Returns:
list(int):Returns a list of random integer numbers

fake_alphanum_1 creates an array of randomic alphanumeric strings with a specific format
    or "" in case of format not being passed.
    Strategy:

Parameters:
size (int): size of the output name array
kwargs["format"] (string): a string representing the format (numbers and letters) of the
output

Returns:
list(string):Returns a list of random alphanumeric characters
"""
import random
import numpy as np
from numpy import array, concatenate
from functools import reduce
from numpy.random import randint
from perform import performance 

# Esse método cria uma coluna de identificadores únicos
# @performance
def fake_int_1(size=5, **kwargs):
    """
    Parameters:
    size (int): size of the output name array
    kwargs["min_size"] (int): min value of the floats values in the array
    kwargs["max_size"] (int): max value of the floats values in the array
    Returns:
    list(floats):Returns a list of random floats
    """
    if kwargs.get("min_size") and kwargs.get("min_size"):
        length_array = np.random.randint(kwargs["min_size"], kwargs["max_size"], size)
        return [randint(0, 10 ** length) for length in length_array]

# Esse método cria uma coluna de identificadores únicos
# @performance
def fake_int_2(size=5, **kwargs):
    """
    Parameters:
    size (int): size of the output name array
    kwargs["min_size"] (int): min value of the floats values in the array
    kwargs["max_size"] (int): max value of the floats values in the array
    Returns:
    list(floats):Returns a list of random floats
    """
    tam = randint(kwargs["min_size"],kwargs["max_size"]) \
            if kwargs.get("min_size") and kwargs.get("max_size")  else None
    return [ randint(0,10 ** tam) for i in range(size) ]

# Esse método cria uma coluna de identificadores únicos
# @performance
def fake_int_3(size=5, **kwargs):
    """
    Parameters:
    size (int): size of the output name array
    kwargs["min_size"] (int): min value of the floats values in the array
    kwargs["max_size"] (int): max value of the floats values in the array
    Returns:
    list(floats):Returns a list of random floats
    """
    if kwargs.get("min_size") and kwargs.get("max_size"):
        return list(randint(10 ** kwargs["min_size"], 10 ** kwargs["max_size"], size))


def fake_int_4(size=5, **kwargs):
    """
    Parameters:
    size (int): size of the output name array
    kwargs["min_size"] (int): min value of the floats values in the array
    kwargs["max_size"] (int): max value of the floats values in the array
    Returns:
    list(floats):Returns a list of random floats
    """
    
    return [0 for i in range(size)]
import unittest

class TestCoreMethods(unittest.TestCase):

    # def test_fake_int_1(self):
    #     print(fake_int_1(size=3, min_size=5, max_size=7))
    #     # fake_int_1(size=100000, min_size=5, max_size=10)
    #     self.assertFalse('Foo'.isupper())


    # def test_fake_int_2(self):
    #     print(fake_int_2(size=5, min_size=5, max_size=7))
    #     # fake_int_2(size=100000, min_size=5, max_size=10)
    #     self.assertFalse('Foo'.isupper())

    def test_fake_int_3(self):
        print(fake_int_3(size=5, min_size=5, max_size=7))
        # fake_int_3(size=100000, min_size=5, max_size=10)
        self.assertFalse('Foo'.isupper())

    def test_fake_int_4(self):
        print(fake_int_4(size=5, min_size=5, max_size=7))
        # fake_int_4(size=100000, min_size=5, max_size=10)
        self.assertFalse('Foo'.isupper())

if __name__ == '__main__':
    unittest.main()