import os
import time
import random
import pandas as pd
from typing import List, Dict, Optional, Generator, Callable, Any


class DataGenerator:
      

  def handle_splitable(self, metadata, df):
    for key, value in metadata.items():
      if value.get("splitable"):
        sep = value.get("sep", ";")
        cols = value.get("cols")
        df[cols] = df[key].str.split(sep, expand=True)
        df.drop(columns=[key], inplace=True)
    return df


  def __convert_dt_to_str(self, dataframe: pd.DataFrame) -> pd.DataFrame:
      df_result = dataframe.copy()
      for column in df_result.columns:
          if 'datetime64' in str(df_result[column].dtype):
              df_result[column] = df_result[column].astype(str)
      return df_result
  
      
  def __sleep_to_contro_throughput(self, min_throughput: int, max_throughput: int):
    sleep_time = 1 / random.uniform(min_throughput, max_throughput)
    time.sleep(sleep_time)


  def create_pandas_df(self, size: int, metadata: dict, transformer: Optional[Callable]=None) -> pd.DataFrame:
    dict_data = {key: value["method"](size, **value["parms"]) for key, value in metadata.items()}
    df_data = pd.DataFrame(dict_data)
    df_data_final = self.handle_splitable(metadata, df_data)
    if transformer: df_data_final = transformer(df_data_final)
    return df_data_final
  

  def create_spark_df(self, spark, size: int, metadata: dict, transformer: Optional[Callable]=None) -> Any:
    df_data = self.create_pandas_df(size=size, metadata=metadata, transformer=transformer)
    df_final = spark.createDataFrame(df_data)
    return df_final


  def create_streaming_records(self, microbatch_size:int, metadata: dict, transformer: Optional[Callable]=None, min_throughput: int=1, max_throughput: int = 10) -> Generator:
    while True:
      df_data_microbatch = self.create_pandas_df(size=microbatch_size, metadata=metadata, transformer=transformer)
      df_data_parsed = self.__convert_dt_to_str(df_data_microbatch)
      list_of_records = df_data_parsed.to_dict('records')
      for record in list_of_records:
          record["timestamp_created"] = round(time.time(), 3)
          yield record
          self.__sleep_to_contro_throughput(min_throughput, max_throughput)
  

  def create_csv_file(self, microbatch_size: int, size_in_mb: int, metadata: dict, path: str, transformer: Optional[Callable]=None) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    while True:
      df = self.create_pandas_df(size=microbatch_size, metadata=metadata, transformer=transformer)
      df.to_csv(path, mode='a', header=False, index=False)
      if os.path.getsize(path) > size_in_mb * 1024 * 1024: break




   

if __name__ == '__main__':
  pass