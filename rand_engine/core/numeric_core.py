import numpy as np


class NumericCore:


  @classmethod
  def gen_ints(self, size: int, min: int, max: int) -> np.ndarray:
    """
    This method generates an array of random integers.
    :param size: int: Number of elements to be generated.
    :param min: int: Minimum value of the generated numbers.
    :param max: int: Maximum value of the generated numbers.
    :return: np.ndarray: Array of random integers.
    """
    return np.random.randint(min, max + 1, size)


  @classmethod
  def gen_ints_zfilled(self, size: int, length: int) -> np.ndarray:
    """
    This method generates an array of random integers with a fixed length.
    :param size: int: Number of elements to be generated.
    :param length: int: Length of the generated numbers.
    :return: np.ndarray: Array of random integers.
    """
    str_arr = np.random.randint(0, 10**length, size).astype('str')
    return np.char.zfill(str_arr, length)
  
  
  @classmethod
  def gen_floats(self, size: int, min: int, max: int, round: int = 2):
    """
    This method generates an array of random floats.
    :param size: int: Number of elements to be generated.
    :param min: int: Minimum value of the generated numbers.
    :param max: int: Maximum value of the generated numbers.
    :param round: int: Number of decimal places to round the generated numbers. Default is 2.
    :return: np.ndarray: Array of random floats.
    """
    sig_part = np.random.randint(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part


  @classmethod
  def gen_floats_normal(self, size: int, mean: int, std: int, round: int = 2):
    """
    This method generates an array of random floats with a normal distribution.
    :param size: int: Number of elements to be generated.
    :param mean: int: Mean of the distribution.
    :param std: int: Standard deviation of the distribution.
    :param round: int: Number of decimal places to round the generated numbers. Default is 2.
    :return: np.ndarray: Array of random floats.
    """
    return np.round(np.random.normal(mean, std, size), round)




if __name__ == '__main__':
  pass