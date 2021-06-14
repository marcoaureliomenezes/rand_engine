import time, sys

def performance(original_function):
    def wrapper_function(*args, **kwargs):
        start = time.time()
        result = original_function(*args, **kwargs)
        print(f"\tlength: {len(result)}")
        print(f"\tsize in bytes: {sys.getsizeof(result)}")
        print(f"\ttime spent: {time.time() - start}")
        return result
    return wrapper_function