from fakemethods import *
from performance import loop_complexity
from names import *

def test_core_method_performance(size):
    loop_complexity(fake_int, min=0, max=10, size=size)
    loop_complexity(fake_int, min=0, max=1000000, size=size)

    loop_complexity(fake_int, min=3, max=6, algnum=True, size=size)
    loop_complexity(fake_int, min=3, max=12, algnum=True, size=size)
    loop_complexity(fake_int, min=3, max=24, algnum=True, size=size)

    loop_complexity(fake_float, min=0, max=10, round=2, size=size)
    loop_complexity(fake_float, min=0, max=1000000, round=2, size=size)
    loop_complexity(fake_float, min=0, max=10, round=10, size=size)
    loop_complexity(fake_float, min=0, max=1000000, round=10, size=size)

    loop_complexity(fake_float, min=5, max=10, algnum=True, round=2, size=size)
    loop_complexity(fake_float, min=5, max=20, algnum=True, round=10, size=size)
    loop_complexity(fake_float, min=5, max=50, algnum=True, round=10, size=size)
    loop_complexity(fake_float, type="normal", mean=1000, std=200, size=size)
    loop_complexity(fake_float, type="normal", mean=1000, std=200, round=2, size=size)

    loop_complexity(fake_discrete, distinct=["value1", "value2", "value3"], size=size)
    loop_complexity(fake_discrete, distinct=names , size=size)
    loop_complexity(fake_discrete, distinct=[names,last_names], size=size)

    loop_complexity(fake_alphanum, format="aa", size=size)
    loop_complexity(fake_alphanum, format="aa22", size=size)
    loop_complexity(fake_alphanum, format="aaaaaaa2222222", size=size)
    loop_complexity(fake_alphanum, format="aaaaaaaaaaaaaaa2222222222222222", size=size)

    loop_complexity(fake_alphanum, format="aa", size=size)
    loop_complexity(fake_alphanum, format="aa22", size=size)
    loop_complexity(fake_alphanum, format="aaaaaaa2222222", size=size)
    loop_complexity(fake_alphanum, format="aaaaaaaaaaaaaaa2222222222222222", size=size)

test_core_method_performance(1000000)