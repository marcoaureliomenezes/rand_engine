from typing import Any, Callable
from rand_engine.file_handlers.file_handler import FileHandler

class FileWriter:
  """
  Base class for file writers.
  Contains common attributes and methods shared by FileBatchWriter and FileStreamWriter.
  """

  def __init__(self, microbatch_def):
    self.microbatch_def = microbatch_def
    self.write_format = "csv"
    self.write_mode = "overwrite"
    self._size = 1000
    self.write_options = {}
    self.writer_method = self._FileWriter__map_methods()

  
  def __map_methods(self):
    """Maps file formats to their corresponding FileHandler methods."""
    return {
      "csv": FileHandler.to_csv,
      "parquet": FileHandler.to_parquet,
      "json": FileHandler.to_json
    }
  

  def size(self, size: int):
    """Set the size of the dataframe to be generated."""
    self._size = size
    return self


  def mode(self, write_mode: str) -> Callable:
    """Set the write mode (overwrite, append, etc)."""
    self.write_mode = write_mode
    return self


  def format(self, format: str) :
    """Set the output file format (csv, parquet, json)."""
    self.write_format = format
    return self
  

  def option(self, key: str, value: Any):
    """Set a single write option."""
    self.write_options[key] = value
    return self
  

  def options(self, **kwargs):
    """Set multiple write options at once."""
    for key, value in kwargs.items():
      self.write_options[key] = value
    return self
