import random
import time
import pandas as pd

class StreamHandler:
  
  @staticmethod
  def convert_dt_to_str(dataframe: pd.DataFrame) -> pd.DataFrame:
    df_result = dataframe.copy()
    for column in df_result.columns:
      missing = df_result[column].isna()
      if 'datetime64' in str(df_result[column].dtype):
        df_result[column] = df_result[column].astype(str)
      if missing.any():
        df_result[column] = df_result[column].astype(object).mask(missing, None)
    return df_result
  
  @staticmethod
  def sleep_to_contro_throughput(min_throughput: int, max_throughput: int):
    sleep_time = 1 / random.uniform(min_throughput, max_throughput)
    time.sleep(sleep_time)
