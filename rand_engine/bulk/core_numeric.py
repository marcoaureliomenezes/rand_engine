import numpy as np
import random
from datetime import datetime as dt, timedelta


class CoreNumeric:

  @classmethod
  def gen_booleans(self, prop_false, prop_true):
    return [False for i in range(prop_false)] + [True for i in range(prop_true)]

  @classmethod
  def gen_ints(self, size: int, min: int, max: int):
    return np.random.randint(min, max + 1, size)

  @classmethod
  def gen_ints_zfilled(self, size: int, length: int) -> np.ndarray:
    return np.array([str(random.randint(0, 10**length - 1)).zfill(length) for _ in range(size)])

  @classmethod
  def gen_ints10(self, size: int, min: int, max: int):
    size_arr = np.random.randint(min, max, size)
    rand_floats = np.random.uniform(low=0, high=10, size=size)
    return np.multiply(rand_floats, 10**size_arr).astype("int")

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

  @classmethod
  def gen_datetimes(self, size: int, start: str, end: str, format: str):
    dt_start, dt_end = dt.strptime(start, format), dt.strptime(end, format)
    timestamp_start, timestamp_end = dt_start.timestamp(), dt_end.timestamp()
    int_array = np.random.randint(timestamp_start, timestamp_end, size)
    date_array = np.vectorize(lambda x: dt.fromtimestamp(x))(int_array)
    return date_array

  @classmethod
  def gen_dates(self, size: int, start: str, end: str, format: str):
    dt_start, dt_end = dt.strptime(start, format), dt.strptime(end, format)
    possible_dates = [dt.strftime(dt_start + timedelta(days=i), format)for i in range((dt_end - dt_start).days)]
    return np.random.choice(possible_dates, size)

if __name__ == '__main__':
  
  start_date = '01-01-1020'
  end_date = '01-01-2021'
  format_date = '%d-%m-%Y'
  size = 10**1
  result = CoreNumeric.gen_dates(size, start_date, end_date, format_date)
  print(result)