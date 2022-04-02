import numpy as np
from numpy.random import randint
from functools import reduce
from utils import normalize_all_params, handle_num_format, fake_concat, handle_string_format, get_interval, format_date_array
import pandas as pd

#################################   INT METHODS    ###########################################

def random_int(min, max, size):
    return list(np.random.randint(min, max + 1, size))


def random_int10(min, max, size):
    size_arr = np.random.randint(min, max, size)
    rand_floats = np.random.uniform(low=0, high=10, size=size)
    return np.multiply(rand_floats, 10**size_arr).astype("int")


def fake_int(size=5, **kwargs):
    min, max, algnum = normalize_all_params(kwargs,
                    ("min", int, 0), ("max", int, 10), ("algnum", bool, False))
    result = random_int(min, max, size) if not algnum else random_int10(min, max, size)
    return handle_num_format(result, **kwargs)


if __name__ == '__main__':
    expected_size, expected_min, expected_max = (100, 5, 6)
    real_result = random_int10(size=expected_size, min=expected_min, max=expected_max)
    print(real_result)
    assert len(real_result) == expected_size
    # assert min(real_result) == expected_min
    assert max(real_result) < 10**expected_max + 1
    # print(min(real_result), max(real_result), len(real_result))
#################################    FLOAT METHODS    ###########################################

def random_float(min, max, size, round):
    sig_part = np.random.randint(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part

def random_float10(min, max, size, round):
    sig_part = random_int10(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part

def random_float_normal(mean, std, size):
    return np.random.normal(loc=mean, scale=std, size=size)


def fake_float(size=5, **kwargs):
    min, max, mean, std, round, algnum, distribution = normalize_all_params(kwargs,
        ("min", int, 0), ("max", int, 10), ("mean", float, 1), ("std", float, 0.2),
        ("round", int, 2), ("algnum", bool, False), ("distribution", str, None)
    )
    result = random_float_normal(mean, std, size).round(round) if distribution == "normal" else \
        random_float(min, max, size, round) if not algnum else random_float10(min, max, size, round)  
    return handle_num_format(result, **kwargs)


#################################    FLOAT METHODS    ###########################################


def random_single_word(size, values):
    return list(map(lambda x: values[x], randint(0, len(values), size)))

def random_multi_word(size, values):
    result_array = [[arg[j] for j in randint(0, len(arg), size)] for arg in values]
    return [reduce(lambda a, b: f"{a} {b}", fullname) for fullname in list(zip(*result_array))]


def fake_discrete(size=5, **kwargs):
    params = kwargs.get("params")
    distinct,format, key = normalize_all_params(kwargs,
    ("distinct", list, [None]),
    ("format", str, None), ("key", str, "x"))
    distinct_elem = distinct[0]
    if (params and format):
        return fake_discrete_format(size, params, format, key)
    else:
        return random_multi_word(size, distinct) if len(distinct) > 0 and type(distinct_elem) is list \
                else random_single_word(size, distinct)

def fake_discrete_format(size, params, formato, key):
    methods = {'fake_discrete': fake_discrete, 'fake_int': fake_int, 'fake_float': fake_float}
    df, counter = (pd.DataFrame(), 0)
    aux_param = params.copy()
    for counter in range(len(formato)):
        df[counter], _ = (methods[aux_param[0]["how"]](size, **aux_param[0]), aux_param.pop(0)) if \
        formato[counter] == key else (np.array([formato[counter] for i in range(size)]), None)
    return reduce(lambda a, b: a+b, [df[i] for i in df.columns]).values


#################################    DATE METHODS    ###########################################

def random_alphanum(size, format):
    def aux_method(format):
        ra = randint(0, len(format))
        res = chr(randint(48,57)) if format[ra].isdigit() else chr(randint(97, 123)) \
            if format[ra].isalpha() else format[ra]
        return format[0:ra] + res + format[ra+1:]
    return  [aux_method(format) for i in range(size)]

def fake_date(size=5, **kwargs):
    start, end, format = normalize_all_params(kwargs,
        ("start", str, "01-01-2020"), ("end", str, "31-12-2020"), ("format", str, "%d-%m-%Y"))
    interval = get_interval(start=start, end=end, date_format=format)
    int_array = randint(interval[0], interval[1], size)
    return format_date_array(int_array, format)

#######################################################################################

def fake_data(size, **kwargs):
    return globals()[kwargs["method"]](size=size, **kwargs) \
        if kwargs.get("method") else [None for i in range(size)]

# This method creates a pandas random dataframe as you pass metadata to it.
def create_table(size=5, **kwargs):
    names, data = (kwargs["names"], kwargs["data"])
    return pd.DataFrame({names[i]: fake_data(size, **data[i]) for i in range(len(data))})

