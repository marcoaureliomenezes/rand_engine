import time

def loop_complexity(method, *args, **kwargs):
    start = time.time()
    res = method(*args, **kwargs)
    time_elapsed= time.time() - start
    print(f"Time_elapsed  for method {method.__name__}: {time_elapsed}")
    return time_elapsed, len(res)

def transform_assign(method, *args, **kwargs):
    print(f"\nMethod {method.__name__}\n\t{method(*args, **kwargs)}")


