from random import shuffle
import numpy as np
from numpy.random import randint
from performance.perf import measure_performance
from functools import reduce
from datetime import datetime
from dateutil import parser



def fake_categorical_data(size, **kwargs):
    if(kwargs.get("distinct") is not None):
        aux = randint(0, len(kwargs["distinct"]), size)
        return [kwargs["distinct"][i] for i in aux]

def fake_null_prop(size, *args): 
    args = [None] if len(args) == 0 else args
    return fake_categorical_data(size, distinct = args)


# print(fake_date(2,2))

# Esse método cria uma coluna de identificadores únicos
def aleatory_num(min_size, max_size):
    tam = randint(min_size,max_size)
    return str(randint(0,10 ** tam)).zfill(tam)

def fake_identif_really_fast(size=5, min_size=5, max_size=10):
    return [aleatory_num(min_size,max_size) for i in range(size)]


#format # dia mes ano
def random_date(size, start, end):
    interval = parser.parse(start).timestamp(), parser.parse(end).timestamp()
    int_array = randint(interval[0], interval[1], size)
    return [ datetime.fromtimestamp(i).strftime("%m/%d/%Y") for i in int_array ]

# print(random_date(10 , "4-12-2019", "5/7/2020"))


# null_prop deve ser limitado de 0 a 100.
def normalize_prop(num):
    return 0  if num < 0 else ( 1 if num > 1 else num)

def fake_data(size, null_prop, **kwargs):

    null_prop = normalize_prop(null_prop)  
    if kwargs.get("null_args") is not None:
        null_part = fake_null_prop(int(size * null_prop), *kwargs.get("null_args"))
    if kwargs.get("distinct_args") is not None:
        data_part = fake_categorical_data(int(size * (1 - null_prop)), kwargs.get("distinct_args"))
    res = np.concatenate((null_part, data_part))
    np.random.shuffle(res)
    return res


#######################################################################################################




def test_fake_categorical_data():
    sample = fake_categorical_data2(10, distinct=["seg_1", "seg_2"])
    print("Sample date dataset\t", sample)
    print("time elapsed: ", measure_performance(fake_categorical_data2, 10))

def test_fake_null_data():
    sample = fake_categorical_data2(10, distinct=["seg_1", "seg_2"])
    print("Sample Categorical dataset\t", sample)
    print("time elapsed: ", measure_performance(fake_categorical_data2, 10))


def test_fake_categorical_data():
    sample = fake_categorical_data2(10, distinct=["seg_1", "seg_2"])
    print("Sample Categorical dataset\t", sample)
    print("time elapsed: ", measure_performance(fake_categorical_data2, 1000000))
# Categorical Data Random Vector Test



test_fake_categorical_data()
# # Null data Random vector test
# print("Test Nulls dataset\t", fake_categorical_data(5,distinct=["seg_1", "seg_2"]))
# # Null Data Random Vector Time Test
# start = time.time()
# fakeNullList = fake_null_prop(100000,"NULL", None)
# end = time.time()
# print(f"Nulls time test : Time elapsed:\t{end - start}")


