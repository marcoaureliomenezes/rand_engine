import numpy as np


class CoreNumeric:


  @classmethod
  def gen_ints(self, size: int, min: int, max: int):
    return np.random.randint(min, max + 1, size)


  @classmethod
  def gen_ints_zfilled(self, size: int, length: int) -> np.ndarray:
    str_arr = np.random.randint(0, 10**length, size).astype('str')
    return np.strings.zfill(str_arr, length)
  

  @classmethod
  def gen_floats(self, size: int, min: int, max: int, round: int = 2):
    sig_part = np.random.randint(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part


  @classmethod
  def gen_floats_normal(self, size: int, mean: int, std: int, round: int = 2):
    return np.round(np.random.normal(mean, std, size), round)


  @classmethod
  def gen_floats10(self, size: int, min: int, max: int, round: int = 2):
    sig_part = self.gen_ints10(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part



if __name__ == '__main__':
  
  import time
  start_date = '01-01-1020'
  end_date = '01-01-2021'
  format_date = '%d-%m-%Y'

  print(f"TESTE 1. Vendo os dados")
  print(CoreNumeric.gen_ints_zfilled(size=5*10**0, length=10))

  #### BENCHMARK PARMS
  benchmark_parms = {"size": 10**6,"length": 10}
  print(f"TESTE 1. Benchmark para parâmetros {benchmark_parms}")
  start_time = time.time()
  result = CoreNumeric.gen_ints_zfilled(**benchmark_parms)
  elapsed_time = time.time() - start_time
  print(f"Elapsed time teste 1: {elapsed_time} seconds")

  print(f"TESTE 2. Vendo os dados")
  print(CoreNumeric.gen_ints_zfilled(size=5*10**0, length=10))
  print(f"TESTE 2. Benchmark para parâmetros {benchmark_parms}")
  start_time = time.time()
  result = CoreNumeric.gen_ints_zfilled_2(**benchmark_parms)
  elapsed_time = time.time() - start_time
  print(f"Elapsed time: {elapsed_time} seconds")

  # print(result)

  

# def lottery(array_input):
#     return [i * 10 if round(random.random(),2) < 0.2 else \
#         i * 100 if round(random.random(),2) < 0.09 else \
#         i * 1000 if round(random.random(),2) < 0.01 else i \
#         for i in array_input]