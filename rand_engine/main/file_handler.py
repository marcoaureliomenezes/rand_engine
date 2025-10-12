import os
from typing import Callable
from pandas import DataFrame as PDDataFrame


class FileHandler:

  @staticmethod
  def to_csv(dataframe: PDDataFrame, full_path: str, write_options: dict) -> Callable:
    return lambda: dataframe().to_csv(full_path, index=False, **write_options)

  @staticmethod
  def to_json(dataframe: PDDataFrame, full_path: str, write_options: dict) -> Callable:
    return lambda: dataframe().to_json(full_path, orient='records', lines=True, **write_options)

  @staticmethod
  def to_parquet(dataframe: PDDataFrame, full_path: str, write_options: dict) -> Callable:
    return lambda: dataframe().to_parquet(full_path, index=False, engine='pyarrow', **write_options)


  @staticmethod
  def handle_path(path: str, format: str, write_options: dict) -> str:
    file_format = format
    file_name = os.path.basename(path)
    base_path = os.path.dirname(path)
    comp_type = write_options.get("compression", None)
    file_name_cleaned = file_name.replace(f".{file_format}", "").replace(f".{comp_type}", "")
    ext = f".{file_format}.{comp_type}" if comp_type else f".{file_format}"
    return base_path, file_name_cleaned, ext
  