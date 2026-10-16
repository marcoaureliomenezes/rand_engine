"""File writer state shared by the batch and stream writers: format, mode and options."""
from typing import Any, Callable
from rand_engine.file_handlers.file_handler import FileHandler

class FileWriter:
  """
  Base class for file writers.

  Contains common attributes and methods shared by FileBatchWriter and FileStreamWriter.

  Examples
  --------
  >>> import pandas as pd
  >>> from rand_engine import DataGenerator
  >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
  >>> DataGenerator(spec, seed=42).size(10).write.format("csv").save("out/class.csv")
  >>> len(pd.read_csv("out/class.csv"))
  10
  """

  def __init__(self, size_def, microbatch_def, schema_def=None):
    self.size_def = size_def
    self.microbatch_def = microbatch_def
    self.schema_def = schema_def
    self.write_format = "csv"
    self.write_mode = "overwrite"
    self.write_options = {}
    self.writer_method = self._FileWriter__map_methods()

  
  def __map_methods(self):
    """Map file formats to their corresponding FileHandler methods."""
    return {
      "csv": FileHandler.to_csv,
      "parquet": FileHandler.to_parquet,
      "json": FileHandler.to_json
    }
  

  def mode(self, write_mode: str) -> Callable:
    """
    Set the write mode of the next ``save``.

    Parameters
    ----------
    write_mode : str
        ``"overwrite"`` (default) replaces the file; ``"append"`` adds rows to it.

    Returns
    -------
    FileWriter
        This writer, for chaining.

    Examples
    --------
    >>> import pandas as pd
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> gen = DataGenerator(spec, seed=42).size(10)
    >>> gen.write.format("csv").save("out/mode.csv")
    >>> gen.write.mode("append").format("csv").save("out/mode.csv")
    >>> len(pd.read_csv("out/mode.csv"))
    20
    """
    self.write_mode = write_mode
    return self


  def format(self, format: str) :
    """
    Set the output file format of the next ``save``.

    Parameters
    ----------
    format : str
        ``"csv"``, ``"parquet"`` or ``"json"``.

    Returns
    -------
    FileWriter
        This writer, for chaining.

    Examples
    --------
    >>> import pandas as pd
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> DataGenerator(spec, seed=42).size(10).write.format("parquet").save("out/format.parquet")
    >>> len(pd.read_parquet("out/format.parquet"))
    10
    """
    self.write_format = format
    return self
  

  def option(self, key: str, value: Any):
    """
    Set one write option of the next ``save``.

    Parameters
    ----------
    key : str
        Option name, such as ``"numFiles"`` (parts per ``save``) or ``"maxRowsPerBatch"``.
    value : Any
        Option value.

    Returns
    -------
    FileWriter
        This writer, for chaining.

    Examples
    --------
    >>> import os
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> DataGenerator(spec, seed=42).size(10).write.option("numFiles", 2).format("csv").save("out/parts")
    >>> len(os.listdir("out/parts"))
    2
    """
    self.write_options[key] = value
    return self
  

  def options(self, **kwargs):
    """
    Set several write options of the next ``save`` at once.

    Parameters
    ----------
    **kwargs : Any
        Option names and values, such as ``numFiles=2``.

    Returns
    -------
    FileWriter
        This writer, for chaining.

    Examples
    --------
    >>> import os
    >>> import pandas as pd
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> gen = DataGenerator(spec, seed=42).size(10).write.options(numFiles=2, maxRowsPerBatch=3)
    >>> gen.format("csv").save("out/options")
    >>> sum(len(pd.read_csv(f"out/options/{name}")) for name in os.listdir("out/options"))
    10
    """
    for key, value in kwargs.items():
      self.write_options[key] = value
    return self
