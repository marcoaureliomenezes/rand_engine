import random, unittest
import numpy as np
from numpy.random import randint
from functools import reduce
from datetime import datetime

def sort_array(array_input):
        array_input.sort()
        return array_input


def concat_arrays(*args):
    result = []
    [result.extend(arr)for arr in args]
    return result

def fake_concat(sep="", *args):
    return [reduce(lambda a, b: f"{a}{sep}{b}", i) for i in list(zip(*args))]

def replace_duplicate(array_input, replace):
    result = list(set(array_input))
    result.extend([replace for i in range(len(array_input)-len(list(set(array_input))))])
    random.shuffle(result)
    return result

def lottery(array_input):
    return [i * 10 if round(random.random(),2) < 0.2 else \
        i * 100 if round(random.random(),2) < 0.09 else \
        i * 1000 if round(random.random(),2) < 0.01 else i \
        for i in array_input]

def zfilling(array_input, num_zeros):
    num = len(str(array_input[0]).split(".")[1]) + 1 if type(array_input[1]) == float  else 0
    return [str(valor).zfill(num_zeros + num) for valor in array_input]

def handle_num_format(array_input, **kwargs):
    result = lottery(array_input) if kwargs.get("outlier")==True else array_input
    result = zfilling(result, kwargs["algsize"]) \
                                        if type(kwargs.get("algsize")) is int else result
    return result

def handle_string_format(array_input, **kwargs):
    return replace_duplicate(array_input, np.nan) \
                if kwargs.get("rm_dupl") else array_input
    
def get_interval(start, end, date_format):
    return datetime.timestamp(datetime.strptime(start, date_format)), \
            datetime.timestamp(datetime.strptime(end, date_format))

def expand_array(size=10, base_array=[]):
    return [base_array[int(i % len(base_array))] for i in range(size)]

def reduce_array(size=10, base_array=[]):
    int_array = [int(i) for i in np.linspace(0, size-1, len(base_array))]
    reduced = [int_array.index(i) for i in range(size)]
    result = [base_array[i] for i in reduced]
    return result

def format_date_array(date_array, format):
    return [datetime.fromtimestamp(i).strftime(format) for i in date_array]

def spaced_array(interval, num_part=2):
    return list(np.linspace(interval[0], interval[1], num_part))

def handle_format(format):
    return format[randint(0, len(format))] if format == list else \
            format if format == str else "%d-%m-%Y"
    
# This method receives an list of names and a list of dicts. Its goal is to concatenate
# values inside 
def concat_dict_arrays(arr_names, dicts):
    res = {i: [] for i in arr_names}
    for i in dicts:
        [ res[j].extend(i[j]) for j in res]
    return res

def normalize_param(dic, arg, tipo, default): 
    return dic[arg] if type(dic.get(arg)) is tipo else default

def normalize_all_params(dic, *args):
    return [normalize_param(dic, *i) for i in args]
    
class TestCoreMethods(unittest.TestCase):

    def sort_array(self, array_input):
        array_input.sort()
        return array_input


if __name__ == '__main__':
    unittest.main()