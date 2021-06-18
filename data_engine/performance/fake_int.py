from array import ArrayType
import math, random
import numpy as np
from numpy import array, concatenate
from functools import reduce
from numpy.random import rand, randint
from perform import performance 


def stringify(input_array, **kwargs):
    return [ str(iterr).zfill(kwargs["algsize"]) if  kwargs.get("algsize") \
                    else str(iterr) for iterr in input_array ]

def intify(input_array):
    return [int(i) for i in input_array]

@performance
def fake_int_1(size=5, **kwargs):
    if kwargs.get("min_size") and kwargs.get("min_size"):
        fake_int = lambda iterr, **kwargs: \
            randint(math.pow(10,(kwargs["min_size"] - 1)), math.pow(10, iterr))
        length_array = np.random.randint(kwargs["min_size"], kwargs["max_size"] + 1, size)
        result = [fake_int(length, **kwargs) for length in length_array]
        return stringify(result, **kwargs) if kwargs.get("array_type") == "string" else result
    return [0 for i in range(size)]

# Esse método cria uma coluna de identificadores únicos
@performance
def fake_int_2(size=5, **kwargs):
    if kwargs.get("min_size") and kwargs.get("max_size"):
        fake_int = lambda **kwargs: \
            math.floor(random.random() * math.pow(10,
                         random.randint(kwargs.get("min_size"), (kwargs.get("max_size")))))
        result = [fake_int(**kwargs) for i in range(size)]
        return stringify(result, **kwargs) if kwargs.get("array_type") == "string" else result
    return [0 for i in range(size)]


@performance
def fake_int_3(size=5, **kwargs):
    if kwargs.get("min_size") and kwargs.get("max_size"):
        sizes = randint(kwargs["min_size"], kwargs["max_size"] + 1, size)
        result = list(map(lambda x: randint(kwargs["min_size"], 10 ** x), sizes))
        return stringify(result, **kwargs) if kwargs.get("array_type") == "string" else result
    return [0 for i in range(size)]

@performance
def fake_int(size=5, **kwargs):
    if not (kwargs.get("min") and kwargs.get("max")):
        result = [random.randint(0, 9) for i in range(size)]
    elif kwargs.get("algnum") is not True:
        result = list(randint(kwargs["min"], kwargs["max"] + 1, size))
    else:
        def random_int(size, **kw):
            return [math.floor(
                random.random() * math.pow(10, random.randint(kw.get("min"), (kw.get("max")))))
                for i in range(size)]
        result = random_int(size, **kwargs)
    return stringify(result, **kwargs) if kwargs.get("array_type") == "string" else \
            intify(result) if kwargs.get("array_type") == "int" else result

import unittest

built_max = max
built_min = min

class TestCoreMethods(unittest.TestCase):

    def test_fake_int(self):
        # SEM ARGUMENTOS
        # fake_int1 = fake_int()
        # print("Teste sem parâmetros:\t", fake_int1)
        # fake_int(1000000)
        fake_int(1000000, min=5, max=7, algnum=True)
        fake_int(1000000, min=5, max=7, algnum=True, array_type="string")
 
if __name__ == '__main__':
    unittest.main()