import numpy as np
from numpy.random import randint
from functools import reduce
from utils import normalize_all_params, handle_num_format, fake_concat, handle_string_format, get_interval, format_date_array
import pandas as pd

#################################   INT METHODS    ###########################################

def gen_ints(min, max, size):
    return list(np.random.randint(min, max + 1, size))


def gen_ints10(min, max, size):
    size_arr = np.random.randint(min, max, size)
    rand_floats = np.random.uniform(low=0, high=10, size=size)
    return np.multiply(rand_floats, 10**size_arr).astype("int")


def fake_ints(size=5, **kwargs):
    min, max, algnum = normalize_all_params(kwargs,
                    ("min", int, 0), ("max", int, 10), ("algnum", bool, False))
    result = gen_ints(min, max, size) if not algnum else gen_ints10(min, max, size)
    return handle_num_format(result, **kwargs)


    # print(min(real_result), max(real_result), len(real_result))
#################################    FLOAT METHODS    ###########################################

def gen_floats(min, max, size, round):
    sig_part = np.random.randint(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part

def gen_floats10(min, max, size, round):
    sig_part = gen_ints10(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part

def gen_floats_normal(mean, std, size):
    return np.random.normal(loc=mean, scale=std, size=size)


def fake_float(size=5, **kwargs):
    min, max, mean, std, round, algnum, distribution = normalize_all_params(kwargs,
        ("min", int, 0), ("max", int, 10), ("mean", float, 1), ("std", float, 0.2),
        ("round", int, 2), ("algnum", bool, False), ("distribution", str, None)
    )
    result = gen_floats_normal(mean, std, size).round(round) if distribution == "normal" else \
        gen_floats(min, max, size, round) if not algnum else gen_floats10(min, max, size, round)  
    return handle_num_format(result, **kwargs)


#################################    FLOAT METHODS    ###########################################


def gen_distincts(size, distinct):
    return list(map(lambda x: distinct[x], randint(0, len(distinct), size)))


def fake_discrete(size=5, **kwargs):
    params, formato = (kwargs.get("params"), kwargs.get("formato"))
    distinct,format, key = normalize_all_params(kwargs, 
                                ("distinct", list, [None]),
                                ("format", str, None),
                                ("key", str, "x"))
    if (params and formato):
        return fake_discrete_format(size, params, format, key)
    else:
        return gen_distincts(size, distinct)

def fake_discrete_format(size, params, formato, key):
    df, counter = (pd.DataFrame(), 0)
    aux_param = params.copy()
    for counter in range(len(formato)):
        df[counter], _ = (locals()[aux_param[0]["how"]](size, **aux_param[0]), aux_param.pop(0)) if \
        formato[counter] == key else (np.array([formato[counter] for i in range(size)]), None)
    return reduce(lambda a, b: a+b, [df[i] for i in df.columns]).values


#################################    DATE METHODS    ###########################################

def gen_dates(size=5, **kwargs):
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


##################################################################################################



if __name__ == '__main__':
    pass
