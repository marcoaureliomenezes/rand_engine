import time
import sys
import numpy as np
from numpy.random import randint
import timeit

def test_complex1(size):
    np.random.randint(0,10,size)

def test_complex2(size):
    for i in range(size):
        a=2

def test_complex3(size):
    [i for i in range(size)]


def test_complex4(size):
    for i in range(size):
        for j in range(size):
            a=2


#############################################################################################

def performance(original_function):
    def wrapper_function(*args, **kwargs):
        start = time.time()
        result = original_function(*args, **kwargs)
        print(f"length: {len(result)}")
        print(f"size in bytes: {sys.getsizeof(result)}")
        print(f"time spent: {time.time() - start}")
        return result
    return wrapper_function

def snippet_complexity(method, *args, **kwargs):
    start = time.time()
    method(*args, **kwargs)
    return time.time() - start

def loop_complexity(method, *args, **kwargs):
    start = time.time()
    method(*args, **kwargs)
    return time.time() - start


def bigO(method, max_iter):
    sizes_tested = [10 ** i for i in range(2, max_iter)]
    print
    for i in sizes_tested:
        print(loop_complexity(method, size=i))


import unittest



class TestSpeedMethods(unittest.TestCase):

    def test(self):

        bigO(test_complex1, 5)
        print("############################")
        bigO(test_complex2, 5)
        print("############################")
        bigO(test_complex3, 5)
        print("############################")
        bigO(test_complex4, 5)
        print("############################")

if __name__ == '__main__':
    unittest.main()





# def test_fake_int(self):
#     print("\n\nResults for FAKE_INT with different parameters")
#     print(fake_int())
#     print(fake_int(size=5, min_size=5, max_size=8))
#     print(fake_int(size=5, min_size=5, max_size=8, string=True))
#     print(fake_int(size=5, min_size=5, max_size=8, string=True, algsize=12))
#     self.assertFalse('Foo'.isupper())
#
#
# def test_fake_float(self):
#     print("\n\nResults for FAKE_FLOAT method with different parameters")
#     # print(fake_float(size=5))
#     print(fake_float(size=5, min_size=2, max_size=4))
#     print(fake_float(size=5, min_size=2, max_size=4, round=2))
#     print(fake_float(size=5, min_size=2, max_size=4, string=True, algsize=12))
#     self.assertFalse('Foo'.isupper())
#
#
# def test_fake_float_normal(self):
#     print("\n\nResults for FAKE_FLOAT_NORMAL with different parameters")
#     print(fake_float_normal(size=5))
#     print(fake_float_normal(size=5, mean=10000, std=3000))
#     print(fake_float_normal(size=5, mean=10000, std=3000, round=2))
#     print(fake_float_normal(size=10, mean=10000, std=3000, string=True, algsize=12))
#     self.assertFalse('Foo'.isupper())
#
#
# def test_fake_discrete(self):
#     print("\n\nResults for FAKE_DISCRETE with different parameters")
#     print(fake_discrete(size=5, distinct=["valor1", "valor2", "valor3"]))
#     print(fake_discrete(size=5, distinct=[1, 2, "NULL"]))
#     print(fake_discrete(size=5, distinct=["gado", "etherium", "bitcoin"]))
#     self.assertFalse('Foo'.isupper())
#
#
# def test_fake_alphanum(self):
#     print("\n\nResults for FAKE_ALPHANUM with different parameters")
#     print(fake_alphanum(size=5, format="abc123"))
#     print(fake_alphanum(size=5, format="22123"))
#     print(fake_alphanum(size=5, format="abcb"))
#     self.assertFalse('Foo'.isupper())
#
#
# def test_fake_date(self):
#     print("\n\nResults for FAKE_ALPHANUM with different parameters")
#     print(fake_date(size=5, start="06-02-2020", end="08-02-2020", format="%d-%m-%Y"))
#     print(fake_date(size=5, start="06-02/2020", end="08/02-2020", format="%d %m %Y"))
#     print(fake_date(size=5, start="01/20/2021", end="12-20-2021", format=["%d-%m-%Y", "%d/%m/%Y", "%d %m %Y"]))
#     self.assertFalse('Foo'.isupper())