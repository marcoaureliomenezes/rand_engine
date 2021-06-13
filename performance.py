import time
import sys
import numpy as np
import random

from numpy.random import randint

def performance(original_function):
    def wrapper_function(*args, **kwargs):
        start = time.time()
        result = original_function(*args, **kwargs)
        print(f"length: {len(result)}")
        print(f"size in bytes: {sys.getsizeof(result)}")
        print(f"time spent: {time.time() - start}")
        return result
    return wrapper_function


@performance
def create_array(size):
    return np.random.randint(0,10,size)

@performance
def create_array2(size):
    return [np.random.randint(0,10) for i in range(size)]

create_array(1000 * 1000*10)

create_array2(1000 * 1000*10)