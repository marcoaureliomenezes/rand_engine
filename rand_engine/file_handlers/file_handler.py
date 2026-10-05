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


_CSV_OPENERS = {
  None: lambda path: open(path, "wb"), "gzip": lambda path: gzip.open(path, "wb"),
  "bz2": lambda path: bz2.open(path, "wb"), "xz": lambda path: lzma.open(path, "wb"), "zip": _zip_open,
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


def _tz_aware_as_text(df: PDDataFrame) -> PDDataFrame:
  # pyarrow formats tz-aware timestamps through an IANA database Windows lacks; pandas renders them itself.
  tz_columns = [c for c in df.columns if isinstance(df[c].dtype, DatetimeTZDtype)]
  return df.assign(**{c: df[c].astype(str).where(df[c].notna()) for c in tz_columns}) if tz_columns else df


class FileHandler:

  @staticmethod
  def to_csv(dataframe: PDDataFrame, full_path: str, write_options: dict, writer_keys: tuple = ()) -> Callable:
    _documented("csv", write_options, ("index", "sep", "compression", *writer_keys))
    if write_options.get("index", False) is not False:
      raise RandEngineError("csv option 'index' accepts only False")
    compression = write_options.get("compression")
    if compression not in _CSV_OPENERS:
      raise RandEngineError(f"csv compression '{compression}' is not documented; accepted: gzip, bz2, xz, zip")
    opener = _CSV_OPENERS[compression]
    options = pa_csv.WriteOptions(delimiter=write_options.get("sep", ","))
    def write():
      table = _arrow_table(_tz_aware_as_text(dataframe()))
      with opener(full_path) as file:
        pa_csv.write_csv(table, file, options)
    return write

  @staticmethod
  def to_json(dataframe: PDDataFrame, full_path: str, write_options: dict, writer_keys: tuple = ()) -> Callable:
    _documented("json", write_options, ("orient", "force_ascii", "indent", "compression", *writer_keys))
    if write_options.get("orient", "records") != "records":
      raise RandEngineError("json option 'orient' accepts only 'records'")
    options = {k: v for k, v in write_options.items() if k != "orient"}
    return lambda: dataframe().to_json(full_path, orient='records', lines=True, **options)

  @staticmethod
  def to_parquet(dataframe: PDDataFrame, full_path: str, write_options: dict, writer_keys: tuple = ()) -> Callable:
    _documented("parquet", write_options, ("compression", *writer_keys))
    return lambda: pq.write_table(_arrow_table(dataframe()), full_path, compression=write_options.get("compression", "snappy"))


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
