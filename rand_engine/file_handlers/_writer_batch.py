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

  def __init__(
    self,
    size_def,
    microbatch_def,
    schema_def=None,
    *,
    evaluated_batch_def=None,
  ):
    super().__init__(size_def, microbatch_def, schema_def)
    self.evaluated_batch_def = evaluated_batch_def


  def _generated_batch(self, size: int, offset: int):
    if self.evaluated_batch_def is None:
      return self.microbatch_def(size, offset)(), self.schema_def
    batch = self.evaluated_batch_def(size, offset)
    return batch.frame, batch.declared_schema_def

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
  def _copy_existing(source: Path, staging: Path) -> None:
    if not source.exists():
      return
    if not source.is_dir():
      raise RandEngineError(f"append destination '{source}' is not a directory")
    for entry in source.iterdir():
      target = staging / entry.name
      if entry.is_dir():
        shutil.copytree(entry, target)
      else:
        shutil.copy2(entry, target)


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
    stable_schema: pa.Schema | None,
    single_append_from: Path | None,
  ) -> pa.Schema | None:
    single = len(file_sizes) == 1
    use_declared_schema = not (
      self.write_format == "json" and batch_limit is None
    )
    for file_size in file_sizes:
      file_path = staging / f"output.{extension}" if single else self._part_path(staging, extension)
      append_from = single_append_from if single else None
      with self._open_session(
        file_path,
        options,
        append_from=append_from,
        expected_schema=stable_schema,
      ) as session:
        for batch_size in self._batches(file_size, batch_limit):
          frame, declared_schema_def = self._generated_batch(batch_size, offset)
          session.write(
            frame,
            declared_schema_def if use_declared_schema else None,
          )
          offset += batch_size
          del frame
          del declared_schema_def
          if batch_limit is not None and session.schema is None:
            raise RandEngineError("schema is indeterminate when row batching is enabled")
          if session.schema is not None:
            stable_schema = session.schema.remove_metadata()
        if session.schema is not None:
          stable_schema = session.schema.remove_metadata()
    return stable_schema


  def save(self, path: str) -> None:
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
    stable_schema = self.schema_def() if total == 0 else None
    self.writer_method[self.write_format](
      lambda: None, str(destination), write_options, ("numFiles",)
    )

    parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", suffix=".staging", dir=parent))
    committed = False
    try:
      append = self.write_mode == "append"
      if num_files > 1 and append:
        self._copy_existing(destination, staging)
      append_from = destination if num_files == 1 and append and destination.exists() else None
      self._stage_files(
        staging,
        file_sizes,
        extension,
        write_options,
        0,
        batch_limit,
        stable_schema,
        append_from,
      )

      if num_files == 1:
        os.replace(staging / f"output.{extension}", destination)
        committed = True
      else:
        self._commit_directory(staging, destination)
        committed = True
    finally:
      if not committed and staging.exists():
        shutil.rmtree(staging)
      elif num_files == 1 and staging.exists():
        shutil.rmtree(staging)

