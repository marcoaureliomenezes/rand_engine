import random
from perform import performance 
from utils import *


@performance
def fake_int(size=5, **kwargs):
    if not (kwargs.get("min") and kwargs.get("max")):
        result = [random.randint(0, 9) for i in range(size)]
    elif kwargs.get("algnum") is not True:
        result = random_int(size, **kwargs)
    else:
        result = random_int10(size, **kwargs)

    result = default_array(result, int) if kwargs.get("array_type") == "int" else result
    result = default_array(result, str) if kwargs.get("array_type") == "string" else result
    result = zfilling(result, qtd=kwargs["algsize"]) \
                                    if type(kwargs.get("algsize")) is int else result
    return result

@performance
def fake_float(size=5, **kwargs):
    if not (kwargs.get("min") and kwargs.get("max")):
        result = [random.random() * 10 for i in range(size)]
    elif kwargs.get("algnum") is not True:
        result = random_float(size, **kwargs)
    else:
        result = random_float10(size, **kwargs)


    result = round_array(result, by=kwargs["round"]) if kwargs.get("round") else result
    result = default_array(result, int) if kwargs.get("array_type") == "int" else result
    result = default_array(result, str) if kwargs.get("array_type") == "string" else result
    result = zfilling(result, qtd=kwargs["algsize"]) \
                                        if type(kwargs.get("algsize")) is int else result
    return result

@performance
def fake_float_normal(size=5, **kwargs):
    result = random_float_normal(size, **kwargs)

    result = round_array(result, by=kwargs["round"]) if kwargs.get("round") else result
    result = default_array(result, int) if kwargs.get("array_type") == "int" else result
    result = default_array(result, str) if kwargs.get("array_type") == "string" else result
    result = zfilling(result, qtd=kwargs["algsize"]) \
                                        if type(kwargs.get("algsize")) is int else result
    return result

import unittest

class TestCoreMethods(unittest.TestCase):

    def test_fake_int(self):
        print("\nTeste int")
        # print(fake_float(size=5, min=5, max=10, round=2))
        # print(fake_int(size=5, min=5, max=10))
        # print(fake_int(size=5, min=5, max=10, algnum=True))
        # print(fake_int(size=5, min=5, max=10, algnum=True, array_type="string"))
        # print(fake_int(size=5, min=5, max=10, algnum=True, array_type="int"))
        # print(fake_int(size=5, min=5, max=10, algnum=True, algsize=12))
        fake_int(size=1000000, min=5, max=10, algnum=True, algsize=12)
        self.assertFalse('Foo'.isupper())

        
    def test_fake_float(self):
        print("\nTeste float")
        # print(fake_float(size=5, min=5, max=10, round=2))
        # print(fake_float(size=5, min=5, max=10, round=2, algnum=True))
        # print(fake_float(size=5, min=5, max=10, round=2, algnum=True, array_type="string"))
        # print(fake_float(size=5, min=5, max=10, round=2, algnum=True, array_type="int"))
        # print(fake_float(size=5, min=5, max=10, round=2, algnum=True, algsize=12))
        fake_float(size=1000000, min=5, max=10, round=2, algnum=True, algsize=12)
        self.assertFalse('Foo'.isupper())

    def test_fake_float_normal(self):
        print("\nTeste float normal")
        # print(fake_float_normal(size=5, mean=10, std=2, round=2))
        # print(fake_float_normal(size=5, mean=10, std=2, round=2, array_type="int"))
        # print(fake_float_normal(size=5, mean=10, std=2, round=2, array_type="string"))
        # print(fake_float_normal(size=5, mean=10, std=2, round=2,algsize=12))
        fake_float_normal(size=1000000, mean=10, std=2, round=2,algsize=12)
        self.assertFalse('Foo'.isupper())

    

if __name__ == '__main__':
    unittest.main()