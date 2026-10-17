"""Settings shared by the batch and stream file writers: format, mode and options."""
from typing import Any, Callable
from rand_engine.file_handlers.file_handler import FileHandler

class FileWriter:
  """
  Configure the file format, write mode and options of ``write`` and ``writeStream``.

  SQLite is an output-only batch format with a required ``table`` option; stream writers refuse it.

  Examples
  --------
  >>> import os, tempfile
  >>> import pandas as pd
  >>> from rand_engine import DataGenerator
  >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
  >>> path = os.path.join(tempfile.mkdtemp(), "class.csv")
  >>> DataGenerator(spec, seed=42).size(10).write.format("csv").save(path)
  >>> len(pd.read_csv(path))
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
    Set the write mode of the next ``save`` or ``start``.

    Parameters
    ----------
    write_mode : str
        ``"overwrite"`` (default) replaces the output (file or folder); ``"append"`` adds to it.

    Returns
    -------
    FileWriter
        This writer, for chaining.

    Examples
    --------
    >>> import os, tempfile
    >>> import pandas as pd
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> gen = DataGenerator(spec, seed=42).size(10)
    >>> path = os.path.join(tempfile.mkdtemp(), "mode.csv")
    >>> gen.write.format("csv").save(path)
    >>> gen.write.mode("append").format("csv").save(path)
    >>> len(pd.read_csv(path))
    20
    """
    self.write_mode = write_mode
    return self


  def format(self, format: str) :
    """
    Set the output file format of the next ``save`` or ``start``.

    Parameters
    ----------
    format : str
        ``"csv"``, ``"parquet"``, ``"json"`` or batch-only ``"sqlite"``.

    Returns
    -------
    FileWriter
        This writer, for chaining.

    Examples
    --------
    >>> import os, tempfile
    >>> import pandas as pd
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> path = os.path.join(tempfile.mkdtemp(), "format.parquet")
    >>> DataGenerator(spec, seed=42).size(10).write.format("parquet").save(path)
    >>> len(pd.read_parquet(path))
    10
    """
    self.write_format = format
    return self
  

  def option(self, key: str, value: Any):
    """
    Set one write option of the next ``save`` or ``start``.

    Parameters
    ----------
    key : str
        Option name: ``"compression"`` (file codec), ``"numFiles"`` (parts per ``save``),
        ``"maxRowsPerBatch"`` (rows per write batch) or ``"timeout"`` (seconds a
        ``start`` runs, default 20). SQLite accepts only ``"table"``.
    value : Any
        Option value.

    Returns
    -------
    FileWriter
        This writer, for chaining.

    Examples
    --------
    >>> import os, tempfile
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> path = os.path.join(tempfile.mkdtemp(), "parts")
    >>> DataGenerator(spec, seed=42).size(10).write.option("numFiles", 2).format("csv").save(path)
    >>> len(os.listdir(path))
    2
    """
    self.write_options[key] = value
    return self
  

  def options(self, **kwargs):
    """
    Set several write options of the next ``save`` or ``start`` at once.

    Parameters
    ----------
    **kwargs : Any
        Option names and values, such as ``numFiles=2``; the keys are those of ``option``.

    Returns
    -------
    FileWriter
        This writer, for chaining.

    Examples
    --------
    >>> import os, tempfile
    >>> import pandas as pd
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> path = os.path.join(tempfile.mkdtemp(), "options")
    >>> gen = DataGenerator(spec, seed=42).size(10).write.options(numFiles=2, maxRowsPerBatch=3)
    >>> gen.format("csv").save(path)
    >>> sum(len(pd.read_csv(os.path.join(path, name))) for name in os.listdir(path))
    10
    """
    for key, value in kwargs.items():
      self.write_options[key] = value
    return self
