import numpy as np
import time
from numpy.random import randint
from functools import reduce
from rand_engine.utils import (
                    normalize_all_params,
                    handle_num_format,
                    handle_datatype_format,
                    get_interval,
                    format_date_array
)

import pandas as pd

#################################   INT METHODS    ###########################################
def distinct_proportion(prop_false, prop_true):
    return [False for i in range(prop_false)] + [True for i in range(prop_true)]


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
    result = handle_datatype_format(result, **kwargs)
    min, max, round, algnum = normalize_all_params(kwargs,
        ("min", int, 0), ("max", int, 10),
        ("round", int, 2), ("algnum", bool, False))

    return handle_num_format(result, **kwargs)


    # print(min(real_result), max(real_result), len(real_result))
#################################    FLOAT METHODS    ###########################################

def gen_floats(min, max, size, round=2):
    sig_part = np.random.randint(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part

def gen_floats10(min, max, size, round=2):
    sig_part = gen_ints10(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part


def fake_floats(size=5, **kwargs):
    min, max, round, algnum = normalize_all_params(kwargs,
        ("min", int, 0), ("max", int, 10),
        ("round", int, 2), ("algnum", bool, False),
    )
    result =  gen_floats(min, max, size, round) if not algnum else gen_floats10(min, max, size, round)  
    return handle_num_format(result, **kwargs)


#################################    FLOAT METHODS    ###########################################


def gen_distincts(size, distinct):
    return list(map(lambda x: distinct[x], randint(0, len(distinct), size)))


def fake_discrete(size=5, **kwargs):
    params, formato = (kwargs.get("params"), kwargs.get("formato"))
    distinct,format, key = normalize_all_params(kwargs, 
                                ("distinct", list, [None]),
                                ("formato", str, None),
                                ("key", str, "x"))
    if (params and formato):
        return fake_discrete_format(size, params, format, key)
    else:
        return gen_distincts(size, distinct)

def fake_discrete_format(size, params, formato, key):
    df, counter = (pd.DataFrame(), 0)
    aux_param = params.copy()
    for counter in range(len(formato)):
        df[counter], _ = (globals()[aux_param[0]["how"]](size, **aux_param[0]), aux_param.pop(0)) if \
        formato[counter] == key else (np.array([formato[counter] for i in range(size)]), None)
    return reduce(lambda a, b: a+b, [df[i] for i in df.columns]).values


#################################    DATE METHODS    ###########################################

def fake_dates(size=5, **kwargs):
    start, end, format = normalize_all_params(kwargs,
        ("start", str, "01-01-2020"), ("end", str, "31-12-2020"), ("format", str, "%d-%m-%Y"))
    interval = get_interval(start=start, end=end, date_format=format)
    int_array = randint(interval[0], interval[1], size)
    return format_date_array(int_array, format)

#######################################################################################

def fake_data(size, **kwargs):
    dados = globals()[kwargs["method"]](size=size, **kwargs) \
        if kwargs.get("method") else [None for i in range(size)]
    return dados

# This method creates a pandas random dataframe as you pass metadata to it.
def create_table(size, metadata):
    colunas, metadados = (list(metadata.keys()), list(metadata.values()))
    df_own_cols = pd.DataFrame({colunas[i]: fake_data(size, **metadados[i]) for i in range(len(metadata))})
    return df_own_cols


##################################################################################################

if __name__ == '__main__':

    metadata = dict(
        nome = dict(method="fake_discrete", formato="x x", key="x", 
            params=[
                {'how': "fake_discrete", 'distinct': ["marco", "jose", "pedro" "ruth", "marta", "rosa"]},
                {'how': "fake_discrete", 'distinct': ["pereira", "cardoso", "souza"]}
        ]),
        cpf = dict(method="fake_discrete", formato="x.x.x-x", key="x",
            params=[
                {"how": "fake_ints", "min": 0, "max": 999, "algsize": 3},
                {"how": "fake_ints", "min": 0, "max": 999, "algsize": 3},
                {"how": "fake_ints", "min": 0, "max": 999, "algsize": 3},
                {"how": "fake_ints", "min": 0, "max": 99, "algsize": 2}
        ]),
        possui_conta_corrente =  dict(method="fake_discrete", distinct=distinct_proportion(prop_false=0, prop_true=1)),
        possui_poupanca =  dict(method="fake_discrete", distinct=distinct_proportion(prop_false=3, prop_true=2)),
        idade = dict(method='fake_ints', min=0, max=100),
        saldo = dict(method='fake_floats', min=0, max=100),
        data_entrada = dict(method='fake_dates', start="01-01-2010",end="31-12-2020", formato="%d-%m-%Y")
    )
    start = time.time()
    table_data = create_table(10**6, metadata=metadata)
    elapsed_time = time.time() - start
    print(table_data)
    print(f"time spent: {elapsed_time}")