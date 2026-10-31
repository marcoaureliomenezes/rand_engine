"""Stream file writer: ``start`` writes one microbatch file per pass until its timeout."""
import os
import time
from typing import Generator
import uuid
from rand_engine.file_handlers.file_handler import FileHandler
from rand_engine.file_handlers.writer import FileWriter
from rand_engine.validators.exceptions import RandEngineError


class FileStreamWriter(FileWriter):
  """
  Write a DataGenerator stream to a directory, one microbatch file per pass.

  Built by ``DataGenerator.writeStream``; chain ``format``, ``trigger`` and
  ``option("timeout", seconds)`` first, then call ``start(path)``.

  Examples
  --------
  >>> from rand_engine import DataGenerator
  >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
  >>> stream = DataGenerator(spec, seed=42).size(10).writeStream
  >>> stream.format("csv").trigger(frequency=0.1).option("timeout", 0.3) is stream
  True
  """

  def __init__(self, size_def, microbatch_def):
    super().__init__(size_def, microbatch_def)
    self.freq = 1
  

  def trigger(self, frequency: float):
    """
    Set the pause between two microbatch writes of the next ``start``.

    Parameters
    ----------
    frequency : float
        Seconds to sleep after each write, fractions allowed; default 1.

    Returns
    -------
    FileStreamWriter
        This writer, for chaining.

    Examples
    --------
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> stream = DataGenerator(spec, seed=42).size(10).writeStream
    >>> stream.trigger(frequency=0.5) is stream
    True
    """
    self.freq = frequency
    return self


  def __handle_filenames(self, path: str, ext: str) -> Generator:
    while True:
      yield os.path.join(path, f"part-{uuid.uuid4()}.{ext}")

  def __writer(self, dataframe, file_gen, write_options):
    return self.writer_method[self.write_format](dataframe, next(file_gen), write_options, ("timeout",))


  def start(self, path):
    """
    Write one microbatch file per pass under ``path`` until the ``timeout`` option elapses.

    Each pass writes ``size`` rows to ``path/part-<uuid>.<ext>`` and sleeps ``trigger``
    seconds. The ``timeout`` option (default 20 seconds) ends the loop after the pass that
    crosses it. Blocks for that duration; in ``overwrite`` mode it clears ``path`` first.

    Parameters
    ----------
    path : str
        Directory to write the part files into, created if missing.

    Raises
    ------
    RandEngineError
        If ``size`` was not set.

    Examples
    --------
    >>> import os, tempfile
    >>> import pandas as pd
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> target = os.path.join(tempfile.mkdtemp(), "ages")
    >>> stream = DataGenerator(spec, seed=42).size(10).writeStream
    >>> stream.format("csv").trigger(frequency=0.1).option("timeout", 0.3).start(target)
    >>> files = os.listdir(target)
    >>> bool(files) and all(len(pd.read_csv(os.path.join(target, name))) == 10 for name in files)
    True
    """
    if self.write_format == "sqlite":
      raise RandEngineError("sqlite is available only through write.save")
    path, ext = FileHandler.handle_path(path, self.write_format, self.write_options)
    size = self.size_def()
    dataframe, offset = self.microbatch_def(size, 0), size
    write_options = dict(self.write_options)
    timeout = write_options.pop("timeout", 20)
    file_gen = self.__handle_filenames(path, ext)
    write = self.__writer(dataframe, file_gen, write_options)
    os.makedirs(path, exist_ok=True)
    if self.write_mode == "overwrite":
      if os.path.exists(path):
        for f in os.listdir(path):
          os.remove(os.path.join(path, f))
    start_time = time.time()
    while True:
      write()
      time.sleep(self.freq)
      if time.time() - start_time > timeout: break
      size = self.size_def()
      dataframe, offset = self.microbatch_def(size, offset), offset + size
      write = self.__writer(dataframe, file_gen, write_options)
