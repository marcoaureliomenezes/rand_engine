import random, unittest
import numpy as np
from numpy.random import randint
from functools import reduce


# Remove all duplicated items, but the replacement is not in the same position.
# it's perfect to random data.
def replace_duplicate(lista, replace):
    result = list(set(lista))
    result.extend([replace for i in range(len(lista)-len(list(set(lista))))])
    random.shuffle(result)
    return result


def default_array(array_input, parser):
    return [parser(valor) for valor in array_input]

def change_case(array_input, **kwargs):
    return [kwargs["method"](valor) for valor in array_input]

def zfilling(lista, qtd):
    return [str(valor).zfill(qtd) for valor in lista]

def round_array(lista, by):
    return [round(valor, by) for valor in lista]

######################################################################################################

# CORE
def random_float(size, **kwargs):
    return [kwargs["min"] + random.random() * (kwargs["max"] - kwargs["min"]) for i in range(size)]

def random_float10(size, **kwargs):
    return [random.random() * (10 ** random.randint(kwargs.get("min"), (kwargs.get("max")))) for i in range(size)]

def random_int(size, **kwargs):
    return list(np.random.randint(kwargs["min"], kwargs["max"] + 1, size))

def random_int10(size, **kwargs):
    return [int(random.random() * (10 ** random.randint(kwargs.get("min"), (kwargs.get("max")))))
                for i in range(size)]

def random_float_normal(size, **kwargs):
    return [np.random.normal(kwargs["mean"], kwargs["std"]) for valor in range(size)] \
        if (kwargs.get("mean") and kwargs.get("std")) else [0. for valor in range(size)]


def random_single_word(size, values):
    return list(map(lambda x: values[x], randint(0, len(values), size)))

def random_multi_word(size, values):
    result_array = [[arg[j] for j in randint(0, len(arg), size)] for arg in values]
    return [reduce(lambda a, b: f"{a} {b}", fullname) for fullname in list(zip(*result_array))]


def random_alphanum(size, format):
    return reduce(lambda a, b: [a[i] + b[i] for i in range(len(b))], 
    np.array([np.array([chr(i) for i in randint(97,123, size)]
                if i.isalpha() else [chr(i) for i in randint(48,57, size)]) 
                for i in format], dtype=object))
                
if __name__ == '__main__':
    unittest.main()