from random import randint, shuffle
import numpy as np
from numpy import array, concatenate, dtype, random
import time
from functools import reduce
from numpy.random import randint

# Esse método cria uma coluna de identificadores únicos
def fake_num_1(size=5, min_size=5, max_size=10):
    aux = list(np.random.randint(min_size, max_size + 1, size))
    return ["".join([str(random.randint(0,10)) for j in range(i)]) for i in aux]


# Esse método cria uma coluna de identificadores únicos
def fake_num_2(size=5, min_size=5, max_size=10):
    complement = []
    delta = max_size - min_size
    sizes = randint(0, delta, size)
    base = list(randint(0,10, [size, min_size]).astype(str))
    for i in sizes:
        complement.append(randint(0,10, i).astype(str))
    bases = [list(i) for i in base]
    complement = [list(i) for i in complement]
    for i in range(size):
        bases[i].extend(complement[i])
    return [ reduce(lambda a, b: a+b, base) for base in bases ]

# Esse método cria uma coluna de identificadores únicos
def fake_num_3(size=5, **kwargs):
    tam = randint(kwargs["min_size"],kwargs["max_size"]) \
            if kwargs.get("min_size") is not None and kwargs.get("min_size") is not None else None
    return [ str(randint(0,10 ** tam)).zfill(tam) for i in range(size) ]

#############################################################################
