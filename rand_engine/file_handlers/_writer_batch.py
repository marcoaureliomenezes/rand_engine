"""Batch file writer: one ``save`` generates the rows and writes one file or several parts."""
import os
from pathlib import Path
import shutil
import tempfile
from typing import Iterator
import uuid

import pyarrow as pa

from rand_engine.file_handlers.file_handler import FileHandler
from rand_engine.file_handlers.writer import FileWriter
from rand_engine.validators.exceptions import RandEngineError


class FileBatchWriter(FileWriter):
  """
  Write the rows of a DataGenerator to files, once per ``save``.

  Built by ``DataGenerator.write``; chain ``format``, ``mode`` and ``option`` first.

  Examples
  --------
  >>> import os, tempfile
  >>> import pandas as pd
  >>> from rand_engine import DataGenerator
  >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
  >>> path = os.path.join(tempfile.mkdtemp(), "batch_ages.csv")
  >>> DataGenerator(spec, seed=42).size(10).write.format("csv").save(path)
  >>> len(pd.read_csv(path))
  10
  """

  def __init__(self, size_def, microbatch_def, file_def=None):
    super().__init__(size_def, microbatch_def)
    # file_def() -> (catalog schema def, batch factory), evaluated once per final file.
    self.file_def = file_def or (
      lambda: (lambda exact=False: None, lambda size, offset: microbatch_def(size, offset)())
    )


  @staticmethod
  def _positive_integer(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
      raise RandEngineError(f"writer option '{name}' must be a positive integer")
    return value


  @staticmethod
  def _resolved_size(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
      raise RandEngineError("resolved size must be a non-negative integer")
    return value


  @staticmethod
  def _file_sizes(total: int, count: int) -> list[int]:
    rows, extra = divmod(total, count)
    return [rows + (index < extra) for index in range(count)]


  @staticmethod
  def _batches(size: int, limit: int | None) -> Iterator[int]:
    if size == 0:
      return
    if limit is None:
      yield size
      return
    remaining = size
    while remaining:
      batch_size = min(limit, remaining)
      yield batch_size
      remaining -= batch_size


  @staticmethod
  def _part_path(staging: Path, extension: str) -> Path:
    while True:
      path = staging / f"part_{str(uuid.uuid4())[:18]}.{extension}"
      if not path.exists():
        return path


  @staticmethod
  def _add_parts(staging: Path, destination: Path) -> None:
    if not destination.is_dir():
      raise RandEngineError(f"append destination '{destination}' is not a directory")
    moved = []
    try:
      for part in staging.iterdir():
        os.replace(part, destination / part.name)
        moved.append(destination / part.name)
    except Exception:
      for path in moved:
        path.unlink(missing_ok=True)
      raise


  @staticmethod
  def _commit_directory(staging: Path, destination: Path) -> None:
    backup = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.previous")
    moved_old = False
    try:
      if destination.exists():
        os.rename(destination, backup)
        moved_old = True
      os.rename(staging, destination)
    except Exception:
      if moved_old and backup.exists() and not destination.exists():
        os.rename(backup, destination)
      raise
    if moved_old:
      shutil.rmtree(backup)


  def _open_session(
    self,
    path: Path,
    options: dict,
    *,
    append_from: Path | None = None,
    expected_schema: pa.Schema | None = None,
  ):
    factory = {
      "csv": FileHandler.open_csv,
      "json": FileHandler.open_json,
      "parquet": FileHandler.open_parquet,
    }.get(self.write_format)
    if factory is None:
      raise RandEngineError(f"unsupported write format '{self.write_format}'")
    return factory(
      str(path),
      options,
      append_from=str(append_from) if append_from is not None else None,
      expected_schema=expected_schema,
    )


  def _stage_files(
    self,
    staging: Path,
    file_sizes: list[int],
    extension: str,
    options: dict,
    offset: int,
    batch_limit: int | None,
    single_append_from: Path | None,
  ) -> None:
    single = len(file_sizes) == 1
    stable_schema = None
    for file_size in file_sizes:
      file_path = staging / f"output.{extension}" if single else self._part_path(staging, extension)
      # One spec evaluation per final file; a row-less file reuses the previous file's schema.
      catalog_def, batch = self.file_def() if file_size or stable_schema is None else (None, None)
      if not file_size:
        expected_schema = stable_schema or catalog_def(True)
      else:
        expected_schema = stable_schema if batch_limit else None
      with self._open_session(
        file_path,
        options,
        append_from=single_append_from if single else None,
        expected_schema=expected_schema,
      ) as session:
        for batch_size in self._batches(file_size, batch_limit):
          session.write(batch(batch_size, offset), catalog_def)
          offset += batch_size
          if batch_limit is not None and session.schema is None:
            raise RandEngineError("schema is indeterminate when row batching is enabled")
      if session.schema is not None:
        stable_schema = session.schema.remove_metadata()


  def save(self, path: str) -> None:
    """
    Generate ``size`` rows and write them to ``path``.

    Writes one file at ``path`` by default; with the ``numFiles`` option, a directory of
    that many part files. ``mode("append")`` adds the rows to what is already there.

    Parameters
    ----------
    path : str
        Relative or absolute path; a single file gets the format's extension.

    Raises
    ------
    RandEngineError
        If ``size`` was not set, or ``numFiles`` or ``maxRowsPerBatch`` is not a positive integer.

    Examples
    --------
    >>> import os, tempfile
    >>> import pandas as pd
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> path = os.path.join(tempfile.mkdtemp(), "save_parts")
    >>> DataGenerator(spec, seed=42).size(10).write.option("numFiles", 2).format("csv").save(path)
    >>> len(os.listdir(path))
    2
    >>> sum(len(pd.read_csv(os.path.join(path, name))) for name in os.listdir(path))
    10
    """
    write_options = dict(self.write_options)
    num_files = self._positive_integer("numFiles", write_options.pop("numFiles", 1))
    batch_limit = write_options.pop("maxRowsPerBatch", None)
    if batch_limit is not None:
      batch_limit = self._positive_integer("maxRowsPerBatch", batch_limit)
    total = self._resolved_size(self.size_def())

    base_path, file_name, extension = FileHandler.handle_path(
      path, self.write_format, write_options
    )
    parent = Path(base_path or ".")
    destination = parent / file_name if num_files > 1 else parent / f"{file_name}.{extension}"
    file_sizes = self._file_sizes(total, num_files)
    self.writer_method[self.write_format](
      lambda: None, str(destination), write_options, ("numFiles",)
    )

    parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", suffix=".staging", dir=parent))
    committed = False
    try:
      append = self.write_mode == "append"
      append_from = destination if num_files == 1 and append and destination.exists() else None
      self._stage_files(
        staging,
        file_sizes,
        extension,
        write_options,
        0,
        batch_limit,
        append_from,
      )

      if num_files == 1:
        os.replace(staging / f"output.{extension}", destination)
        committed = True
      elif append and destination.exists():
        self._add_parts(staging, destination)
        committed = True
      else:
        self._commit_directory(staging, destination)
        committed = True
    finally:
      if staging.exists() and (not committed or num_files == 1 or append):
        shutil.rmtree(staging)

