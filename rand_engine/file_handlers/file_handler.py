import bz2
import gzip
import lzma
import os
import zipfile
from contextlib import contextmanager
from typing import Callable

import pyarrow as pa
import pyarrow.csv as pa_csv
import pyarrow.parquet as pq
from pandas import DataFrame as PDDataFrame, DatetimeTZDtype

from rand_engine.validators.exceptions import RandEngineError


@contextmanager
def _zip_open(path: str):
  with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
    with archive.open(os.path.basename(path).removesuffix(".zip"), "w") as member:
      yield member


@contextmanager
def _zip_read(path: str):
  with zipfile.ZipFile(path) as archive:
    members = archive.namelist()
    if len(members) != 1:
      raise RandEngineError("zip output must contain exactly one data file")
    with archive.open(members[0]) as member:
      yield member


_OUTPUT_OPENERS = {
  None: lambda path: open(path, "wb"),
  "gzip": lambda path: gzip.open(path, "wb"),
  "bz2": lambda path: bz2.open(path, "wb"),
  "xz": lambda path: lzma.open(path, "wb"),
  "zip": _zip_open,
}
_INPUT_OPENERS = {
  None: lambda path: open(path, "rb"),
  "gzip": lambda path: gzip.open(path, "rb"),
  "bz2": lambda path: bz2.open(path, "rb"),
  "xz": lambda path: lzma.open(path, "rb"),
  "zip": _zip_read,
}


def _documented(format: str, write_options: dict, accepted: tuple) -> None:
  for key in write_options:
    if key not in accepted:
      raise RandEngineError(f"{format} option '{key}' is not documented; accepted: {', '.join(accepted)}")


def _arrow_table(df: PDDataFrame) -> pa.Table:
  try:
    return pa.Table.from_pandas(df, preserve_index=False)
  except (pa.ArrowInvalid, pa.ArrowTypeError):
    for column in df.columns:
      try:
        pa.array(df[column], from_pandas=True)
      except (pa.ArrowInvalid, pa.ArrowTypeError) as error:
        raise RandEngineError(f"column '{column}' mixes types; Arrow cannot write it") from error
    raise


def _field_type(
  schema: pa.Schema | None, name: str
) -> pa.DataType | None:
  if schema is None:
    return None
  index = schema.get_field_index(name)
  if index < 0:
    return None
  return schema.field(index).type


def _typed_null_table(
  df: PDDataFrame,
  current_schema: pa.Schema | None,
  declared_schema_def: Callable[[], pa.Schema | None] | None,
) -> pa.Table:
  table = _arrow_table(df)
  null_fields = [field for field in table.schema if pa.types.is_null(field.type)]
  if not null_fields:
    return table

  declared_schema = declared_schema_def() if declared_schema_def is not None else None
  for field in null_fields:
    current_type = _field_type(current_schema, field.name)
    if declared_schema_def is None:
      target = current_type
    elif declared_schema is None:
      target = current_type
      if target is None or pa.types.is_null(target):
        raise RandEngineError(
          f"schema is indeterminate for transformed null field '{field.name}'"
        )
    else:
      target = _field_type(declared_schema, field.name)
      if target is None:
        raise RandEngineError(
          f"declared schema has no field '{field.name}'"
        )
      if current_type is not None and not current_type.equals(target):
        raise RandEngineError(
          f"schema drift: expected {current_schema}, received {declared_schema}"
        )
    if target is None or pa.types.is_null(target):
      continue
    index = table.schema.get_field_index(field.name)
    typed_field = pa.field(
      field.name,
      target,
      nullable=field.nullable,
      metadata=field.metadata,
    )
    table = table.set_column(index, typed_field, table.column(index).cast(target))
  return table


def _tz_aware_as_text(df: PDDataFrame) -> PDDataFrame:
  # pyarrow formats tz-aware timestamps through an IANA database Windows lacks; pandas renders them itself.
  tz_columns = [c for c in df.columns if isinstance(df[c].dtype, DatetimeTZDtype)]
  return df.assign(**{c: df[c].astype("string") for c in tz_columns}) if tz_columns else df


def _logical_schema(schema: pa.Schema) -> pa.Schema:
  metadata = dict(schema.metadata or {})
  metadata.pop(b"pandas", None)
  return schema.with_metadata(metadata or None)


def _empty_table(schema: pa.Schema) -> pa.Table:
  return pa.Table.from_batches([], schema=schema)


def _copy_bytes(source, destination) -> tuple[int, bytes]:
  total = 0
  last = b""
  while chunk := source.read(1024 * 1024):
    destination.write(chunk)
    total += len(chunk)
    last = chunk[-1:]
  return total, last


def _require_same_schema(current: pa.Schema | None, table: pa.Table) -> pa.Schema:
  candidate = _logical_schema(table.schema)
  if current is not None and not current.equals(candidate, check_metadata=False):
    raise RandEngineError(f"schema drift: expected {current}, received {candidate}")
  return candidate


class _CsvFile:

  def __init__(self, path: str, options: dict, *, append_from=None, expected_schema=None):
    _documented("csv", options, ("index", "sep", "compression"))
    if options.get("index", False) is not False:
      raise RandEngineError("csv option 'index' accepts only False")
    self._compression = options.get("compression")
    if self._compression not in _OUTPUT_OPENERS:
      raise RandEngineError(f"csv compression '{self._compression}' is not documented; accepted: gzip, bz2, xz, zip")
    try:
      self._write_options = pa_csv.WriteOptions(delimiter=options.get("sep", ","))
    except (TypeError, ValueError, pa.ArrowInvalid) as error:
      raise RandEngineError(f"csv option 'sep' is invalid: {error}") from error
    self._path = path
    self._append_from = append_from
    self._schema = _logical_schema(expected_schema) if expected_schema is not None else None
    self._file = None
    self._file_context = None
    self._closed = False
    self._has_content = False

  @property
  def schema(self) -> pa.Schema | None:
    return self._schema

  def __enter__(self):
    return self

  def __exit__(self, exc_type, _exc, _tb):
    if exc_type is None:
      self.close()
    else:
      self._close_stream()

  def _open(self):
    if self._file is not None:
      return
    self._file_context = _OUTPUT_OPENERS[self._compression](self._path)
    self._file = self._file_context.__enter__()
    if self._append_from is not None:
      with _INPUT_OPENERS[self._compression](self._append_from) as source:
        total, last = _copy_bytes(source, self._file)
      self._has_content = total > 0
      if self._has_content and last != b"\n":
        self._file.write(b"\n")

  def _close_stream(self):
    if self._file is not None:
      self._file_context.__exit__(None, None, None)
      self._file = None
      self._file_context = None
    self._closed = True

  def write(
    self,
    frame: PDDataFrame,
    declared_schema_def: Callable[[], pa.Schema | None] | None = None,
  ) -> None:
    if self._closed:
      raise RandEngineError("csv file session is closed")
    table = _typed_null_table(
      _tz_aware_as_text(frame), self._schema, declared_schema_def
    )
    self._schema = _require_same_schema(self._schema, table)
    self._open()
    options = pa_csv.WriteOptions(
      delimiter=self._write_options.delimiter,
      include_header=not self._has_content,
    )
    pa_csv.write_csv(table, self._file, options)
    self._has_content = True

  def close(self) -> None:
    if self._closed:
      return
    if not self._has_content:
      if self._schema is None and self._append_from is None:
        self._closed = True
        raise RandEngineError("csv schema is indeterminate for an empty file")
      self._open()
      if not self._has_content:
        pa_csv.write_csv(_empty_table(self._schema), self._file, self._write_options)
        self._has_content = True
    self._close_stream()


class _JsonFile:

  def __init__(self, path: str, options: dict, *, append_from=None, expected_schema=None):
    _documented("json", options, ("orient", "force_ascii", "indent", "compression"))
    if options.get("orient", "records") != "records":
      raise RandEngineError("json option 'orient' accepts only 'records'")
    self._compression = options.get("compression")
    if self._compression not in _OUTPUT_OPENERS:
      raise RandEngineError(f"json compression '{self._compression}' is not documented; accepted: gzip, bz2, xz, zip")
    self._options = {k: v for k, v in options.items() if k not in ("orient", "compression")}
    self._path = path
    self._append_from = append_from
    self._schema = _logical_schema(expected_schema) if expected_schema is not None else None
    self._file = None
    self._file_context = None
    self._closed = False
    self._has_content = False
    self._deferred_payload = None

  @property
  def schema(self) -> pa.Schema | None:
    return self._schema

  def __enter__(self):
    return self

  def __exit__(self, exc_type, _exc, _tb):
    if exc_type is None:
      self.close()
    else:
      self._close_stream()

  def _open(self):
    if self._file is not None:
      return
    self._file_context = _OUTPUT_OPENERS[self._compression](self._path)
    self._file = self._file_context.__enter__()
    if self._append_from is not None:
      with _INPUT_OPENERS[self._compression](self._append_from) as source:
        total, last = _copy_bytes(source, self._file)
      self._has_content = total > 0
      if self._has_content and last != b"\n":
        self._file.write(b"\n")

  def _close_stream(self):
    if self._file is not None:
      self._file_context.__exit__(None, None, None)
      self._file = None
      self._file_context = None
    self._closed = True

  def write(
    self,
    frame: PDDataFrame,
    declared_schema_def: Callable[[], pa.Schema | None] | None = None,
  ) -> None:
    if self._closed:
      raise RandEngineError("json file session is closed")
    if self._deferred_payload is not None:
      raise RandEngineError("json schema is indeterminate across batches")
    payload = frame.to_json(None, orient="records", lines=True, **self._options).encode("utf-8")
    try:
      table = _typed_null_table(frame, self._schema, declared_schema_def)
    except RandEngineError as error:
      # Pandas can serialize heterogeneous object columns that Arrow cannot type.
      if self._schema is not None or not isinstance(
        error.__cause__, (pa.ArrowInvalid, pa.ArrowTypeError)
      ):
        raise
      self._deferred_payload = payload
      return
    self._schema = _require_same_schema(self._schema, table)
    self._open()
    self._file.write(payload)
    self._has_content = self._has_content or bool(payload)

  def close(self) -> None:
    if self._closed:
      return
    if self._deferred_payload is not None:
      self._open()
      self._file.write(self._deferred_payload)
      self._has_content = self._has_content or bool(self._deferred_payload)
      self._deferred_payload = None
    if not self._has_content:
      if self._schema is None and self._append_from is None:
        self._closed = True
        raise RandEngineError("json schema is indeterminate for an empty file")
      self._open()
    self._close_stream()


class _ParquetFile:

  def __init__(self, path: str, options: dict, *, append_from=None, expected_schema=None):
    _documented("parquet", options, ("compression",))
    self._path = path
    self._append_from = append_from
    self._compression = options.get("compression", "snappy")
    try:
      compression_available = self._compression is None or pa.Codec.is_available(self._compression)
    except ValueError as error:
      raise RandEngineError(f"parquet compression '{self._compression}' is not documented") from error
    if not compression_available:
      raise RandEngineError(f"parquet compression '{self._compression}' is not available")
    self._schema = _logical_schema(expected_schema) if expected_schema is not None else None
    self._physical_schema = expected_schema
    self._writer = None
    self._closed = False

  @property
  def schema(self) -> pa.Schema | None:
    return self._schema

  def __enter__(self):
    return self

  def __exit__(self, exc_type, _exc, _tb):
    if exc_type is None:
      self.close()
    else:
      self._close_writer()

  def _open(self, table: pa.Table | None = None):
    if self._writer is not None:
      return
    source = pq.ParquetFile(self._append_from) if self._append_from is not None else None
    source_schema = _logical_schema(source.schema_arrow) if source is not None else None
    candidate = self._schema or source_schema
    if candidate is None:
      raise RandEngineError("parquet schema is indeterminate for an empty file")
    if source_schema is not None and not candidate.equals(source_schema, check_metadata=False):
      raise RandEngineError(f"schema drift: expected {source_schema}, received {candidate}")
    physical = source.schema_arrow if source is not None else self._physical_schema
    if physical is None and table is not None:
      physical = table.schema
    if physical is None:
      physical = candidate
    self._schema = candidate
    self._physical_schema = physical
    self._writer = pq.ParquetWriter(self._path, physical, compression=self._compression)
    if source is not None:
      for row_group in range(source.metadata.num_row_groups):
        self._writer.write_table(source.read_row_group(row_group))

  def _close_writer(self):
    if self._writer is not None:
      self._writer.close()
      self._writer = None
    self._closed = True

  def write(
    self,
    frame: PDDataFrame,
    declared_schema_def: Callable[[], pa.Schema | None] | None = None,
  ) -> None:
    if self._closed:
      raise RandEngineError("parquet file session is closed")
    table = _typed_null_table(frame, self._schema, declared_schema_def)
    self._schema = _require_same_schema(self._schema, table)
    if self._physical_schema is None:
      self._physical_schema = table.schema
    self._open(table)
    table = table.replace_schema_metadata(self._physical_schema.metadata)
    self._writer.write_table(table)

  def close(self) -> None:
    if self._closed:
      return
    self._open()
    self._close_writer()


class FileHandler:

  @staticmethod
  def open_csv(path: str, options: dict, *, append_from=None, expected_schema=None):
    return _CsvFile(path, dict(options), append_from=append_from, expected_schema=expected_schema)

  @staticmethod
  def open_json(path: str, options: dict, *, append_from=None, expected_schema=None):
    return _JsonFile(path, dict(options), append_from=append_from, expected_schema=expected_schema)

  @staticmethod
  def open_parquet(path: str, options: dict, *, append_from=None, expected_schema=None):
    return _ParquetFile(path, dict(options), append_from=append_from, expected_schema=expected_schema)

  @staticmethod
  def to_csv(dataframe: PDDataFrame, full_path: str, write_options: dict, writer_keys: tuple = ()) -> Callable:
    _documented("csv", write_options, ("index", "sep", "compression", *writer_keys))
    options = {key: value for key, value in write_options.items() if key not in writer_keys}
    session = FileHandler.open_csv(full_path, options)
    def write():
      with session:
        session.write(dataframe())
    return write

  @staticmethod
  def to_json(dataframe: PDDataFrame, full_path: str, write_options: dict, writer_keys: tuple = ()) -> Callable:
    _documented("json", write_options, ("orient", "force_ascii", "indent", "compression", *writer_keys))
    options = {key: value for key, value in write_options.items() if key not in writer_keys}
    session = FileHandler.open_json(full_path, options)
    def write():
      with session:
        session.write(dataframe())
    return write

  @staticmethod
  def to_parquet(dataframe: PDDataFrame, full_path: str, write_options: dict, writer_keys: tuple = ()) -> Callable:
    _documented("parquet", write_options, ("compression", *writer_keys))
    options = {key: value for key, value in write_options.items() if key not in writer_keys}
    session = FileHandler.open_parquet(full_path, options)
    def write():
      with session:
        session.write(dataframe())
    return write

  @staticmethod
  def handle_path(path: str, format: str, write_options: dict) -> str:
    file_format = format
    file_name = os.path.basename(path)
    base_path = os.path.dirname(path)
    comp_type = write_options.get("compression", None)
    comp_type = "gz" if comp_type == "gzip" else comp_type
    file_name_cleaned = file_name.replace(f".{file_format}", "").replace(f".{comp_type}", "")
    if comp_type and file_format != "parquet":
      ext = f"{file_format}.{comp_type}"
    else:
      ext = file_format
    return base_path, file_name_cleaned, ext
