import numpy as np
import random
from datetime import datetime as dt, timedelta


class DatetimeCore:
  
  @classmethod
  def gen_unix_timestamps(self, size: int, start: str, end: str, format: str) -> np.ndarray:
    """
    This method generates an array of random unix timestamps.
    :param size: int: Number of elements to be generated.
    :param start: str: Start date of the generated timestamps.
    :param end: str: End date of the generated timestamps.
    :param format: str: Format of the input dates."""
    dt_start, dt_end = dt.strptime(start, format), dt.strptime(end, format)
    if dt_start < dt(1970, 1, 1): dt_start = dt(1970, 1, 1)
    timestamp_start, timestamp_end = dt_start.timestamp(), dt_end.timestamp()
    int_array = np.random.randint(timestamp_start, timestamp_end, size)
    return int_array


  @classmethod
  def gen_timestamps(self, size: int, start: str, end: str, format: str) -> np.ndarray:
    """
    This method generates an array of random timestamps.
    :param size: int: Number of elements to be generated.
    :param start: str: Start date of the generated timestamps.
    :param end: str: End date of the generated timestamps.
    :param format: str: Format of the input dates.
    :return: np.ndarray: Array of random timestamps."""

    date_array = self.gen_unix_timestamps(size, start, end, format).astype('datetime64[s]')
    return date_array
  
  
  @classmethod
  def gen_datetimes(self, size: int, start: str, end: str, format_in: str, format_out: str):
    timestamp_array = self.gen_unix_timestamps(size, start, end, format_in)
    return [dt.fromtimestamp(i).strftime(format_out) for i in timestamp_array]



if __name__ == '__main__':
  pass