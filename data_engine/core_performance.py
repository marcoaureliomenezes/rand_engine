from core import *
from performance import loop_complexity

def test_core_method_performance(size):
    loop_complexity(random_int, min=100, max=1000, size=size)
    loop_complexity(random_int10, min=5, max=10, size=size)
    loop_complexity(random_float, min=100, max=1000, round=2, size=size)
    loop_complexity(random_float10, min=5, max=10, round=2, size=size)
    loop_complexity(random_float_normal, mean=1000, std=200, size=size)
    loop_complexity(random_single_word, values=["value_1","value_2","value_3"],size=size)
    loop_complexity(random_multi_word, values=[["cod_1","cod_2","cod_3"],["prod_1","prod_2","prod3"]], size=size)
    loop_complexity(random_alphanum, format="aaa222", size=size)

test_core_method_performance(1000000)