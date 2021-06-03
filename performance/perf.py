import time

def measure_performance(fuction, size, **kwargs):
    start = time.time()
    fakeIdList = fuction(size=size, **kwargs)
    return time.time() - start