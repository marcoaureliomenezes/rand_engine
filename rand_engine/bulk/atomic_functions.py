import numpy as np
import random
from datetime import datetime as dt

def gen_booleans(prop_false, prop_true):
    return [False for i in range(prop_false)] + [True for i in range(prop_true)]


def gen_ints(min: int, max: int, size: int):
    return np.random.randint(min, max + 1, size)


def gen_ints10(min, max, size):
    size_arr = np.random.randint(min, max, size)
    rand_floats = np.random.uniform(low=0, high=10, size=size)
    return np.multiply(rand_floats, 10**size_arr).astype("int")


def gen_floats(min, max, size, round=2):
    sig_part = np.random.randint(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part

def gen_floats10(min, max, size, round=2):
    sig_part = gen_ints10(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part


def gen_distincts_untyped(size, distinct):
    return list(map(lambda x: distinct[x], np.random.randint(0, len(distinct), size)))

def gen_distinct_untyped_baseline(size, distinct):
    return [random.choice(distinct) for i in range(size)]

def gen_distinct_typed(size, distinct):
    return np.vectorize(lambda x: distinct[x])(np.random.randint(0, len(distinct), size))

def gen_distincts_typed_baseline(size, distinct):
    return np.vectorize(lambda x: random.choice(distinct))(np.arange(size))

def fake_dates(size: int, start: str, end: str, format: str):
    dt_start, dt_end = dt.strptime(start, format), dt.strptime(end, format)
    timestamp_start, timestamp_end = dt_start.timestamp(), dt_end.timestamp()
    int_array = np.random.randint(timestamp_start, timestamp_end, size)
    date_array = np.vectorize(lambda x: dt.fromtimestamp(x))(int_array)

    return date_array
