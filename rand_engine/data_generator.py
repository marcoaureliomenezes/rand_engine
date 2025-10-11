import os
import time
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Generator, Callable, Any
from rand_engine.main.rand_generator import RandGenerator
from rand_engine.main.file_writer import FileWriter
from rand_engine.utils.stream_handler import StreamHandler

  


class DataGenerator:
      
  def __init__(self, random_spec, seed: int = None):
    np.random.seed(seed)
    self.actual_dataframe: Optional[Callable[[], pd.DataFrame]] = None
    self.data_generator = RandGenerator(random_spec)
    self._mode = "pandas"
    self._size = 1000
    self._transformers: List[Optional[Callable]] = []

 
  def generate_pandas_df(self, size: int) -> pd.DataFrame:
    """
    This method generates a pandas DataFrame based on random data specified in the metadata parameter.
    :param size: int: Number of rows to be generated.
    :param transformer: Optional[Callable]: Function to transform the generated data.
    :return: pd.DataFrame: DataFrame with the generated data.
    """
    def wrapped_lazy_dataframe():
      df_pandas = self.data_generator.generate_first_level(size=size)
      df_pandas = self.data_generator.handle_splitable(df_pandas)
      df_pandas = self.data_generator.apply_embedded_transformers(df_pandas)
      df_pandas = self.data_generator.apply_global_transformers(df_pandas, self._transformers)
      return df_pandas
    self.actual_dataframe = wrapped_lazy_dataframe
  

  def transformers(self, transformers: List[Optional[Callable]]):
    self._transformers = transformers
    return self

  def generate_spark_df(self, spark, size: int) -> Any:
    """
    This method generates a Spark DataFrame based on random data specified in the random_spec parameter.
    :param spark: SparkSession: SparkSession object.
    :param size: int: Number of rows to be generated.
    :param transformer: Optional[Callable]: Function to transform the generated data."""
    def wrapped_lazy_dataframe():
      self.generate_pandas_df(size=size)
      df_spark = spark.createDataFrame(self.actual_dataframe())
      return df_spark
    self.actual_dataframe = wrapped_lazy_dataframe

  def mode(self, mode: str):
    assert mode in ["pandas", "spark"], "Mode not recognized. Use 'pandas' or 'spark'."
    self._mode = mode
    return self

  def size(self, size: int):
    self._size = size
    return self

  def get_df(self, spark=None):
    if self._mode == "pandas":
      self.generate_pandas_df(size=self._size)
    elif self._mode == "spark":
      self.generate_spark_df(spark=spark, size=self._size)
    assert self.actual_dataframe is not None, "You need to generate a DataFrame first."
    return self.actual_dataframe()


  def stream_dict(self, min_throughput: int=1, max_throughput: int = 10) -> Generator:
    """
    This method creates a generator of records to be used in a streaming context.
    :param min_throughput: int: Minimum throughput to be generated.
    :param max_throughput: int: Maximum throughput to be generated.
    :return: Generator: Generator of records.
    """
    self.generate_pandas_df(size=self._size)
    assert self.actual_dataframe is not None, "You need to generate a DataFrame first."
    while True:
      df_data_microbatch = self.actual_dataframe()
      df_data_parsed = StreamHandler.convert_dt_to_str(df_data_microbatch)
      list_of_records = df_data_parsed.to_dict('records')
      for record in list_of_records:
        record["timestamp_created"] = round(time.time(), 3)
        yield record
        StreamHandler.sleep_to_contro_throughput(min_throughput, max_throughput)
  

  def write(self, size):
    self.generate_pandas_df(size=size)
    microbatch_def = lambda: self.actual_dataframe
    return FileWriter(microbatch_def)
   


if __name__ == '__main__':

  pass
