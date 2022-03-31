from numpy.random import randint
from functools import reduce
from core import *
from utils import *


def fake_int(size=5, **kwargs):
    min, max, algnum = normalize_all_params(kwargs,
                    ("min", int, 0), ("max", int, 10), ("algnum", bool, False))
    result = random_int(min, max, size) if not algnum else random_int10(min, max, size)
    return handle_num_format(result, **kwargs)

def fake_float(size=5, **kwargs):
    min, max, mean, std, round, algnum, distribution = normalize_all_params(kwargs,
        ("min", int, 0), ("max", int, 10), ("mean", float, 1), ("std", float, 0.2),
        ("round", int, 2), ("algnum", bool, False), ("distribution", str, None)
    )
    result = random_float_normal(mean, std, size).round(round) if distribution == "normal" else \
        random_float(min, max, size, round) if not algnum else random_float10(min, max, size, round)  
    return handle_num_format(result, **kwargs)


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

def fake_alphanum(size=5, **kwargs):
    format, distinct, sep = normalize_all_params(kwargs,
        ("format", str, "2222"), ("distinct", list, None), ( "sep", str, ""))
    result = random_alphanum(size, format)
    result = fake_concat(sep, fake_discrete(size=size, **kwargs), result) if distinct else result
    return handle_string_format(result, **kwargs)


def fake_date(size=5, **kwargs):
    start, end, format = normalize_all_params(kwargs,
        ("start", str, "01-01-2020"), ("end", str, "31-12-2020"), ("format", str, "%d-%m-%Y"))
    interval = get_interval(start=start, end=end, date_format=format)
    int_array = randint(interval[0], interval[1], size)
    return format_date_array(int_array, format)

def fake_partition(size=5, **kwargs):
    start, end, format, num_part = normalize_all_params(kwargs, ("start", str, "01-01-2020"), ("end", str, "31-12-2020"), ("format", str, "%d-%m-%Y"), ("num_part", int, 2))
    interval = get_interval(start, end, format)  
    times = spaced_array(interval, num_part)
    result = reduce_array(size, base_array=times) if num_part >= size \
        else expand_array(size=size, base_array=times)
    result.sort()
    return format_date_array(result, format)


if __name__ == '__main__':
    pass