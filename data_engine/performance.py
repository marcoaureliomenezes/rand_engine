import time

def loop_complexity(method, *args, **kwargs):
    start = time.time()
    res = method(*args, **kwargs)
    print(f"time for method {method.__name__}: {time.time() - start}")

def transform_assign(method, *args, **kwargs):
    print(f"\nMethod {method.__name__}\n\t{method(*args, **kwargs)}")


