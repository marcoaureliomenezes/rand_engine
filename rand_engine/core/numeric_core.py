import numpy as np


class NumericCore:


  @classmethod
  def gen_ints(self, size: int, min: int, max: int):
    return np.random.randint(min, max + 1, size)


  @classmethod
  def gen_ints_zfilled(self, size: int, length: int) -> np.ndarray:
    str_arr = np.random.randint(0, 10**length, size).astype('str')
    return np.char.zfill(str_arr, length)
  
  
  @classmethod
  def gen_floats(self, size: int, min: int, max: int, round: int = 2):
    sig_part = np.random.randint(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part


  @classmethod
  def gen_floats_normal(self, size: int, mean: int, std: int, round: int = 2):
    return np.round(np.random.normal(mean, std, size), round)




if __name__ == '__main__':
  pass