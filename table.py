# null_prop deve ser limitado de 0 a 100.
# Cria nulos entre uma coluna e returna essa coluna
from core import *
import numpy as np

def normalize_prop(num):
    return 0  if num < 0 else ( 1 if num > 1 else num)

def fake_data(size, null_prop, **kwargs):

    null_prop = normalize_prop(null_prop) 

    if kwargs.get("null_args") is not None:
        null_part = fake_null(int(size * null_prop), *kwargs.get("null_args"))
    if kwargs.get("distinct_args") is not None:
        data_part = fake_categorical(int(size * (1 - null_prop)), kwargs.get("distinct_args"))
    res = np.concatenate((null_part, data_part))
    np.random.shuffle(res)
    return res


def create_table(**kwargs):
    return kwargs