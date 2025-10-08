import os
import time
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Generator, Callable, Any
from rand_engine.utils.file_writer import FileWriter
from rand_engine.utils.stream_handler import StreamHandler

class DataGenerator:
      
  def __init__(self, random_spec, seed: Optional[int]=None):
    self.random_spec = random_spec
    self.actual_dataframe = None
    if seed is not None:
      np.random.seed(seed)


  def handle_splitable(self, metadata, df):
    for key, value in metadata.items():
      if value.get("splitable"):
        sep = value.get("sep", ";")
        cols = value.get("cols")
        df[cols] = df[key].str.split(sep, expand=True)
        df.drop(columns=[key], inplace=True)
    return df

  def apply_embedded_transformers(self, metadata, df):
    cols_with_transformers = {key: value["transformers"] for key, value in metadata.items() if value.get("transformers")}
    for col, transformers in cols_with_transformers.items():
      for transformer in transformers:
        df[col] = df[col].apply(transformer)
    return df
  
  def apply_global_transformers(self, df, transformers: List[Optional[Callable]]):
    if transformers:
      if len(transformers) > 0: 
        for transformer in transformers:
          df = transformer(df)
    return df

  def generate_pandas_df(self, size: int, transformers: List[Optional[Callable]] = []) -> pd.DataFrame:
    """
    This method generates a pandas DataFrame based on random data specified in the metadata parameter.
    :param size: int: Number of rows to be generated.
    :param transformer: Optional[Callable]: Function to transform the generated data.
    :return: pd.DataFrame: DataFrame with the generated data.
    """
    assert type(self.random_spec) is dict, "You need to pass a random_spec parameter to generate the random data."
    def first_level():
      dict_data = {key: value["method"](size, **value["parms"]) for key, value in self.random_spec.items()}
      df_pandas = pd.DataFrame(dict_data)
      df_pandas = self.handle_splitable(self.random_spec, df_pandas)
      df_pandas = self.apply_embedded_transformers(self.random_spec, df_pandas)
      df_pandas = self.apply_global_transformers(df_pandas, transformers)
    #   if transformers:
    #     if len(transformers) > 0: 
    #       for transformer in transformers:
    #         df_pandas = transformer(df_pandas)
      return df_pandas
    self.actual_dataframe = first_level
    return self
  

  def generate_spark_df(self, spark, size: int, transformer: Optional[Callable]=None) -> Any:
    """
    This method generates a Spark DataFrame based on random data specified in the random_spec parameter.
    :param spark: SparkSession: SparkSession object.
    :param size: int: Number of rows to be generated.
    :param transformer: Optional[Callable]: Function to transform the generated data."""
    def second_level():
      self.generate_pandas_df(size=size, transformer=transformer)
      df_spark = spark.createDataFrame(self.actual_dataframe())
      return df_spark
    self.actual_dataframe = second_level
    return self


  def get_df(self):
    assert self.actual_dataframe is not None, "You need to generate a DataFrame first."
    return self.actual_dataframe()


  def stream_dict(self, min_throughput: int=1, max_throughput: int = 10) -> Generator:
    """
    This method creates a generator of records to be used in a streaming context.
    :param min_throughput: int: Minimum throughput to be generated.
    :param max_throughput: int: Maximum throughput to be generated.
    :return: Generator: Generator of records.
    """
    assert self.actual_dataframe is not None, "You need to generate a DataFrame first."
    while True:
      df_data_microbatch = self.actual_dataframe()
      df_data_parsed = StreamHandle.convert_dt_to_str(df_data_microbatch)
      list_of_records = df_data_parsed.to_dict('records')
      for record in list_of_records:
        record["timestamp_created"] = round(time.time(), 3)
        yield record
        StreamHandle.sleep_to_contro_throughput(min_throughput, max_throughput)
  

  def write(self):
    microbatch_def = lambda: self.actual_dataframe
    return FileWriter(microbatch_def)
   


if __name__ == '__main__':
  
  pass
