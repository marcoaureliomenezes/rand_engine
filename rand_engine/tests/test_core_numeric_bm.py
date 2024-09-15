import time


from rand_engine.bulk.core_numeric import CoreNumeric


def test_gen_ints():

  kwargs = dict(size=10**7, min=0, max=10**4)
  start_time = time.time()
  real_result = CoreNumeric.gen_ints(**kwargs)
  elapsed_time = time.time() - start_time
  print(f"Elapsed time test_gen_ints: {elapsed_time}")


def test_gen_ints10():
    kwargs = dict(size=10**7, min=0, max=3)
    start_time = time.time()
    real_result = CoreNumeric.gen_ints10(**kwargs)
    elapsed_time = time.time() - start_time
    print(f"Elapsed time test_gen_ints10: {elapsed_time}")

def test_gen_floats():
    kwargs = dict(size=10**7, min=0, max=10**4)
    start_time = time.time()
    real_result = CoreNumeric.gen_floats(**kwargs)
    elapsed_time = time.time() - start_time
    print(f"Elapsed time test_gen_floats: {elapsed_time}")

def test_gen_floats10():
    kwargs = dict(size=10**7, min=0, max=3)
    start_time = time.time()
    real_result = CoreNumeric.gen_floats10(**kwargs)
    elapsed_time = time.time() - start_time
    print(f"Elapsed time test_gen_floats10: {elapsed_time}")

def test_gen_datetimes():
    kwargs = dict(size=10**7, start="2020-01-01", end="2021-01-01", format="%Y-%m-%d")
    start_time = time.time()
    real_result = CoreNumeric.gen_datetimes(**kwargs)
    elapsed_time = time.time() - start_time
    print(f"Elapsed time test_gen_datetimes: {elapsed_time}")


def test_gen_dates():
    kwargs = dict(size=10**7, start="2020-01-01", end="2021-01-01", format="%Y-%m-%d")
    start_time = time.time()
    real_result = CoreNumeric.gen_dates(**kwargs)
    elapsed_time = time.time() - start_time
    print(f"Elapsed time test_gen_dates: {elapsed_time}")
