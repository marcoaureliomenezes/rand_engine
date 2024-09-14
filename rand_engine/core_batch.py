import numpy as np
import time
from numpy.random import randint
from functools import reduce
from templates import template_batch
from utils import normalize_all_params, handle_num_format, handle_datatype_format, \
                                                    get_interval, format_date_array

import pandas as pd

#################################   INT METHODS    ###########################################

    


    # print(min(real_result), max(real_result), len(real_result))
#################################    FLOAT METHODS    ###########################################
def fake_ints(size=5, **kwargs):
    min, max, algnum, zfill = (kwargs.get(arg) for arg in ("min", "max", "algnum", "zfill"))
    result = gen_ints(min, max, size) if not algnum else gen_ints10(min, max, size)
    return [str(valor).zfill(zfill) for valor in result] if zfill else result


def fake_floats(size=5, **kwargs):
    min, max, round, algnum = normalize_all_params(kwargs,
        ("min", int, 0), ("max", int, 10),
        ("round", int, 2), ("algnum", bool, False),
    )
    result =  gen_floats(min, max, size, round) if not algnum else gen_floats10(min, max, size, round)  
    return handle_num_format(result, **kwargs)


###############################    DISCRETE METHODS    ####################################
def gen_distincts(size, distinct):
    return list(map(lambda x: distinct[x], randint(0, len(distinct), size)))


def handle_proportions(distinct_prop, precision):
    return [ key for key, value in distinct_prop.items() for i in range(value * precision)]


def handle_relationships(distincts, sep=""):
    return [f"{j}{sep}{i}" for j in distincts for i in distincts[j]]


def handle_distinct(distincts, sep, precision):
    cond_dict, cond_list = (type(distincts) == dict, type(distincts) == list)
    if cond_dict:
        cond_value = type(list(distincts.values())[0])
        if cond_value == list: return handle_relationships(distincts, sep)
        elif cond_value == int: return handle_proportions(distincts, precision)
        else: return [None]
    elif cond_list: return distincts
    else: return [None]


def fake_discrete(size=5, **kwargs):
    parms, formato, key, distincts = [kwargs.get(parm) for parm in ('parms','formato','key','distinct')]
    distincts = handle_distinct(distincts, sep=kwargs.get("sep", ""), precision=kwargs.get("precision",1))
    if (parms and formato and key): return fake_discrete_format(size, parms, formato, key)
    else: return gen_distincts(size, distincts)
 

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
        nome = dict(method="fake_discrete", distinct=["OPC", "SWP"]),
        cnpj= template_batch("cnpj"),
        tipo_emp = dict(method="fake_discrete", distinct={"MEI": 100,"ME":23, "EPP": 12, "EMP": 13, "EGP": 1}),
        agencia = dict(method="fake_ints", min=0, max=10**7, zfill=8),
        # tipo_categoria = dict(
        #     method = "fake_discrete", sep="@@@",
        #     distinct={"OPC": ["C_OPC","V_OPC"], "SWP": ["C_SWP", "V_SWP"]}
        # ),
        
        )
           
    start = time.time()
    table_data = create_table(10, metadata=metadata)
    elapsed_time = time.time() - start
    print(table_data)
    print(f"time spent: {elapsed_time}")