import numpy as np
import random
from datetime import datetime as dt, timedelta


class CoreDatetime:
  
  @classmethod
  def gen_unix_timestamps(self, size: int, start: str, end: str, format: str):
    dt_start, dt_end = dt.strptime(start, format), dt.strptime(end, format)
    if dt_start > dt(1970, 1, 1): dt_start = dt(1970, 1, 1)
    timestamp_start, timestamp_end = dt_start.timestamp(), dt_end.timestamp()
    int_array = np.random.randint(timestamp_start, timestamp_end, size)
    return int_array

  @classmethod
  def gen_timestamps(self, size: int, start: str, end: str, format: str):
    date_array = self.gen_unix_timestamps(size, start, end, format).astype('datetime64[s]')
    return date_array
  

if __name__ == '__main__':

  pass



# def format_date_array(date_array, format):
#     return [datetime.fromtimestamp(i).strftime(format) for i in date_array]
# def handle_format(format):
#     return format[randint(0, len(format))] if format == list else \
#             format if format == str else "%d-%m-%Y"
# def get_interval(start, end, date_format):
#     return datetime.timestamp(datetime.strptime(start, date_format)), \
#             datetime.timestamp(datetime.strptime(end, date_format))