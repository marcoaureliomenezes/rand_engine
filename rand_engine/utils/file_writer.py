import os
from typing import Callable
from pandas import DataFrame as PDDataFrame

class FileWriter:


  def __init__(self, microbatch_def):
    self.microbatch_def = microbatch_def
    self.write_format = "csv"
    self.write_mode = "overwrite"
    self.write_options = {}
    self.dict_format = {
        "csv": self.to_csv,
        "parquet": self.to_parquet,
        "json": self.to_json
    }

  def __handle_fs(self, path, flag=True) -> None:
    """
    This method handles the file system operations.
    :param path: str: Path of the file to be written.
    """
    if self.write_mode == "overwrite":
      try:
        if os.path.exists(path):
          for file in os.listdir(path):
            os.remove(os.path.join(path, file))
      except Exception as e: pass
    if flag == True: to_create = os.path.dirname(path)
    else: to_create = path
    os.makedirs(to_create, exist_ok=True)  


  def __get_dir_size(self, folder_path: str) -> int:
    """
    This method calculates the size in bytes of a directory.
    :param folder_path: str: Path of the directory.
    :return: int: Size of the directory in bytes.
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
      for filename in filenames:
        file_path = os.path.join(dirpath, filename)
        if not os.path.islink(file_path):
          total_size += os.path.getsize(file_path)
    return total_size
  

  def mode(self, write_mode: str) -> Callable:
    """
    This method sets the write mode of the file.
    :param write_mode: str: Write mode of the file. Default is overwrite.
    :return: FileWriter: Instance of the fileWriter class for method chaining.
    """
    self.write_mode = write_mode
    return self


  def format(self, format):
    """
    This method sets the write format of the file.
    :param format: str: Write format of the file. Default is csv. Supported formats are csv and parquet.
    :return: FileWriter: Instance of the fileWriter class for method chaining.
    """
    self.write_format = format
    return self
  

  def option(self, key, value):
    """
    This method sets the write options of the file.
    :param key: str: Key of the write option.
    :param value: Any: Value of the write option.
    :return: FileWriter: Instance of the fileWriter class for method chaining
    """
    self.write_options[key] = value
    return self
  

  def to_csv(self, dataframe, full_path) -> Callable:
    """
    This method writes a pandas DataFrame to a csv file.
    :param dataframe: pd.DataFrame: DataFrame to be written.
    :param full_path: str: Full path of the file to be written.
    :return: Callable: Function to write the Pandas DataFrame to a csv file.
    """
    if self.write_options.get("compression"):
      full_path= full_path.replace("csv", f"csv.{self.write_options['compression']}")
    writer = lambda: dataframe().to_csv(full_path, index=False, **self.write_options)
    return writer
  
  def to_json(self, dataframe, full_path) -> Callable:
    """
    This method writes a pandas DataFrame to a json file.
    :param dataframe: pd.DataFrame: DataFrame to be written.
    :param full_path: str: Full path of the file to be written.
    :return: Callable: Function to write the Pandas DataFrame to a json file.
    """
    if self.write_options.get("compression"):
      full_path= full_path.replace("json", f"json.{self.write_options['compression']}")
    def writer():
      dataframe().to_json(full_path, orient='records', lines=True)
    return writer

  def to_parquet(self, dataframe, full_path):
    """
    This method writes a pandas DataFrame to a parquet file.
    :param dataframe: pd.DataFrame: DataFrame to be written.
    :param full_path: str: Full path of the file to be written.
    :return: Callable: Function to write the Pandas DataFrame to a parquet file.
    """
    if self.write_options.get("compression"):
      full_path= full_path.replace(".parquet", f".{self.write_options['compression']}.parquet")
    writer = lambda: dataframe().to_parquet(full_path, index=False, engine='pyarrow', **self.write_options)
    return writer


  def load(self, path: str) -> None:
    """
    This method writes a pandas DataFrame to a file.
    :param path: str: Path of the file to be written.
    """
    self.__handle_fs(path)
    dataframe = self.microbatch_def()
    self.dict_format[self.write_format](dataframe, path)()


  def incr_load(self, path, size_in_mb=4):
    """
    This method writes a pandas DataFrame to a file in incremental mode.
    :param path: str: Path of the file to be written.
    :param size_in_mb: int: Size in MB of the file to be written.
    """
    self.__handle_fs(path, flag=False)
    counter = 0
    while True:
      full_path = f"{path}/part-{str(counter).zfill(6)}.{self.write_format}"
      dataframe = self.microbatch_def()
      self.dict_format[self.write_format](dataframe, full_path)()
      size_bytes = self.__get_dir_size(path)
      if counter % 100 == 0: print(f"Size: {size_bytes/2**20:.2f} MB")
      if self.__get_dir_size(path) >= size_in_mb*2**20: break
      counter += 1
