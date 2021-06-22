import random, unittest
import numpy as np
from numpy.random import randint
from functools import reduce
from datetime import datetime
from dateutil import parser

def replace_duplicate(lista, replace):
    result = list(set(lista))
    result.extend([replace for i in range(len(lista)-len(list(set(lista))))])
    random.shuffle(result)
    return result

def nonefy(array_input=[1,2,3,4,5,6,7,8,9], chance=0, distinct=[None]):
    chance = 0  if chance < 0 else ( 1 if chance > 1 else chance)
    return [i if random.random() > chance else distinct[np.random.randint(0,len(distinct))] \
                                     for i in array_input]

def lottery(array_input):
    return [i * 10 if round(random.random(),2) < 0.2 else \
        i * 100 if round(random.random(),2) < 0.09 else \
        i * 1000 if round(random.random(),2) < 0.01 else i \
        for i in array_input]


def default_array(array_input, parser):
    return [parser(valor) for valor in array_input]

def change_case(array_input, **kwargs):
    return [kwargs["method"](valor) for valor in array_input]

def zfilling(lista, qtd):
    return [str(valor).zfill(qtd) for valor in lista]

def round_array(lista, by):
    return [round(valor, by) for valor in lista]

def get_interval(start, end):
    return parser.parse(start).timestamp(), parser.parse(end).timestamp()

def expand_array(size=10, base_array=[]):
    return [base_array[int(i % len(base_array))] for i in range(size)]

def reduce_array(size=10, base_array=[1,2,3,4,5,6,7,8,9]):
    int_array = [int(i) for i in np.linspace(0, size-1, len(base_array))]
    reduced = [int_array.index(i) for i in range(size)]
    result = [base_array[i] for i in reduced]
    return result

def format_date_array(date_array, format):
    return [datetime.fromtimestamp(i).strftime(format) for i in date_array]

def spaced_array(interval, num_part=2):
    return list(np.linspace(interval[0], interval[1], num_part + 1))

def handle_format(format):
    return format[randint(0, len(format))] if format == list else \
            format if format == str else "%d-%m-%Y"

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