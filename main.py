from  table_gen.core import *

import numpy as np

def normalize_prop(num):
    return 0  if num < 0 else ( 1 if num > 1 else num)

def fake_data(size, **kwargs):
    null_rate = normalize_prop(kwargs["null_rate"])
    null_size = int(size * null_rate)
    data_size = int(size - null_size)

    null_part = fake_discrete(size=null_size, distinct=kwargs.get("null_args")) \
        if kwargs.get("null_args") is not None else []

    if kwargs.get("categorical") is not None:
        data_part = fake_discrete(size=data_size, distinct=kwargs["distinct"])

    elif kwargs.get("identif") is not None:
        data_part = fake_num(size=data_size, \
                             min_size=kwargs["min_size"], max_size=kwargs["max_size"] ) 
     
    elif kwargs.get("interval") is not None:
        data_part = fake_date(size=data_size, start=kwargs["start"], end=kwargs["end"])

    res = np.concatenate((null_part, data_part))
    np.random.shuffle(res)
    return res

def create_table(size=6, **kwargs):
    vect = []
    res_data=[]
    for i in range(len(kwargs["data"])):
        aux = [str(item) for item in fake_data(size=size, **kwargs["data"][i])]
        vect.append(aux)
    
    for i in range(len(vect[0])):
        res_data.append((vect[0][i], vect[1][i], vect[2][i]))
    return res_data, kwargs["names"]













# print(
#     fake_data(null_rate=0.1, null_args=[None], categorical=True),
#     fake_data(null_rate=0.1, null_args=[None], identif=True),
#     fake_data(null_rate=0.1, null_args=[None], interval=True)
#     )


    # if kwargs.get("distinct_args") is not None:

    #     data_part = fake_discrete(int(size * (1 - null_prop)), kwargs.get("distinct_args"))
    # res = np.concatenate((null_part, data_part))
    # np.random.shuffle(res)
    # return res
