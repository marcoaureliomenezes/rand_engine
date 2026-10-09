"""Intent: CONTRACT — writer-size-not-from-generator (generator size, int or callable read once per save and split across numFiles files; no size fails before overwrite deletes anything); writer-options-consumed-by-use (a reused writer keeps numFiles); writer-state-shared-across-chains (each .write access is a fresh writer)."""
import pytest
import gc
import os
import pandas as pd
import glob
import time
import threading
import weakref
import gzip, bz2, lzma, zipfile
from contextlib import contextmanager
import pyarrow.parquet as pq
from rand_engine.file_handlers.file_handler import FileHandler

from rand_engine.main.data_generator import DataGenerator
from rand_engine.validators.exceptions import RandEngineError
from tests.fixtures.f1_data_generator_specs_right import (
    rand_spec_with_kwargs,
    rand_spec_with_args,
    rand_spec_case_1_transformer,
    rand_engine_splitable_benchmark_baseline,
)


from tests.fixtures.f3_integrations import (
    create_output_dir,
    df_size,
    microbatch_size,
    batch_size,
    base_path_files_test,
    size_in_mb
)

READERS = {"csv": pd.read_csv, "json": lambda f: pd.read_json(f, lines=True), "parquet": pd.read_parquet}


@pytest.mark.parametrize("format_type,compression,file_path", [
    ("csv", None, "single_file/default/clients"),
    ("csv", "gzip", "single_file/gzip/clients.csv"),
    ("csv", "zip", "single_file/zip/clients.csv.zip"),
    ("csv", "bz2", "single_file/bz2/clients.csv.bz2"),
    ("csv", "xz", "single_file/xz/clients.csv.xz"),
    ("json", None, "single_file/default/clients.json"),
    ("json", "gzip", "single_file/gzip/clients.json"),
    ("json", "zip", "single_file/zip/clients.json.zip"),
    ("json", "bz2", "single_file/bz2/clients.json.bz2"),
    ("json", "xz", "single_file/xz/clients.json.xz"),
    ("parquet", None, "single_file/default/clients.parquet"),
    ("parquet", "gzip", "single_file/gzip/clients.parquet"),
    ("parquet", "snappy", "single_file/snappy/clients.parquet"),
    ("parquet", "zstd", "single_file/zstd/clients.parquet"),
    ("parquet", "brotli", "single_file/brotli/clients.parquet"),
    ("parquet", "lz4", "single_file/lz4/clients.parquet"),
])
def test_writing_single_file(
  df_size,
  rand_spec_with_kwargs,
  base_path_files_test,
  format_type,
  compression,
  file_path
):
  path = f"{base_path_files_test}/{format_type}/{file_path}"
  _ = (
    DataGenerator(rand_spec_with_kwargs)
      .size(lambda: df_size)
      .write
      .format(format_type)
      .option("compression", compression)
      .mode("overwrite")
      .save(path)
  )
  [file] = glob.glob(f"{os.path.dirname(path)}/clients*")
  assert len(READERS[format_type](file)) == df_size


def test_abandoned_chain_does_not_leak_into_next_write(df_size, rand_spec_with_kwargs, base_path_files_test):
  path = f"{base_path_files_test}/csv/abandoned_chain/clients"
  g = DataGenerator(rand_spec_with_kwargs).size(df_size)
  g.write.format("parquet").option("numFiles", 2).mode("append")
  g.write.save(path)
  [file] = glob.glob(f"{os.path.dirname(path)}/*")
  assert file.endswith("clients.csv") and len(pd.read_csv(file)) == df_size
 

@pytest.mark.parametrize("format_type,compression,file_path", [
    ("csv", None, "multi_files_overwrite/default/clients"),
    ("csv", "gzip", "multi_files_overwrite/gzip/clients.csv"),
    ("csv", "zip", "multi_files_overwrite/zip/clients.csv.zip"),
    ("csv", "bz2", "multi_files_overwrite/bz2/clients.csv.bz2"),
    ("csv", "xz", "multi_files_overwrite/xz/clients.csv.xz"),
    ("json", None, "multi_files_overwrite/default/clients.json"),
    ("json", "gzip", "multi_files_overwrite/gzip/clients.json"),
    ("json", "zip", "multi_files_overwrite/zip/clients.json.zip"),
    ("json", "bz2", "multi_files_overwrite/bz2/clients.json.bz2"),
    ("json", "xz", "multi_files_overwrite/xz/clients.json.xz"),
    ("parquet", None, "multi_files_overwrite/default/clients.parquet"),
    ("parquet", "gzip", "multi_files_overwrite/gzip/clients.parquet"),
    ("parquet", "snappy", "multi_files_overwrite/snappy/clients.parquet"),
    ("parquet", "zstd", "multi_files_overwrite/zstd/clients.parquet"),
    ("parquet", "brotli", "multi_files_overwrite/brotli/clients.parquet"),
    ("parquet", "lz4", "multi_files_overwrite/lz4/clients.parquet"),
    # ("parquet", "snappy", "arquivo.parquet")
])
def test_writing_multiple_files(
  df_size,
  rand_spec_with_kwargs,
  base_path_files_test,
  format_type,
  compression,
  file_path
):
  path = f"{base_path_files_test}/{format_type}/{file_path}"
  _ = (
    DataGenerator(rand_spec_with_kwargs)
      .size(df_size)
      .write
      .format(format_type)
      .option("compression", compression)
      .option("numFiles", 2)
      .mode("overwrite")
      .save(path)
  )
  _ = (
    DataGenerator(rand_spec_with_kwargs)
      .size(df_size)
      .write
      .format(format_type)
      .option("compression", compression)
      .option("numFiles", 2)
      .mode("overwrite")
      .save(path)
  )
  base_path = os.path.dirname(path)
  file_name = os.path.basename(path).split(".")[0]
  full_path = f"{base_path}/{file_name}"
  files = glob.glob(f"{full_path}/part_*")
  assert len(files) == 2


@pytest.mark.parametrize("format_type,compression,file_path", [
    ("csv", None, "multi_files_append/default/clients"),
    ("csv", "gzip", "multi_files_append/gzip/clients.csv"),
    ("csv", "zip", "multi_files_append/zip/clients.csv.zip"),
    ("csv", "bz2", "multi_files_append/bz2/clients.csv.bz2"),
    ("csv", "xz", "multi_files_append/xz/clients.csv.xz"),
    ("json", None, "multi_files_append/default/clients.json"),
    ("json", "gzip", "multi_files_append/gzip/clients.json"),
    ("json", "zip", "multi_files_append/zip/clients.json.zip"),
    ("json", "bz2", "multi_files_append/bz2/clients.json.bz2"),
    ("json", "xz", "multi_files_append/xz/clients.json.xz"),
    ("parquet", None, "multi_files_append/default/clients.parquet"),
    ("parquet", "gzip", "multi_files_append/gzip/clients.parquet"),
    ("parquet", "snappy", "multi_files_append/snappy/clients.parquet"),
    ("parquet", "zstd", "multi_files_append/zstd/clients.parquet"),
    ("parquet", "brotli", "multi_files_append/brotli/clients.parquet"),
    ("parquet", "lz4", "multi_files_append/lz4/clients.parquet"),
])
def test_writing_multiple_files_append(
  df_size,
  rand_spec_with_kwargs,
  base_path_files_test,
  format_type,
  compression,
  file_path
):
  path = f"{base_path_files_test}/{format_type}/{file_path}"
  sizes = iter([3, 4])
  writer = (
    DataGenerator(rand_spec_with_kwargs)
      .size(lambda: next(sizes))
      .write
      .format(format_type)
      .option("compression", compression)
      .option("numFiles", 2)
  )
  writer.mode("overwrite").save(path)
  writer.mode("append").save(path)
  base_path = os.path.dirname(path)
  file_name = os.path.basename(path).split(".")[0]
  files = glob.glob(f"{base_path}/{file_name}/part_*")
  assert sorted(len(READERS[format_type](f)) for f in files) == [1, 2, 2, 2]  # callable size read once per save, split across numFiles


def test_no_size_fails_before_overwrite_deletes(rand_spec_with_kwargs, base_path_files_test):
  path = f"{base_path_files_test}/csv/no_size/clients"
  os.makedirs(path, exist_ok=True)
  open(f"{path}/keep.csv", "w").close()
  with pytest.raises(RandEngineError, match=r"\.size\(n\)"):
    DataGenerator(rand_spec_with_kwargs).write.option("numFiles", 2).mode("overwrite").save(path)
  assert os.listdir(path) == ["keep.csv"]


# AC14.2 — csv and parquet through pyarrow; documented options only.

FRAME = pd.DataFrame({
  "b": [True, False], "f": [1.0, 2.5], "g": [1.0, 2.0], "s": ["x", "é"],
  "t": pd.to_datetime(["2024-01-01 00:00:00", "2024-01-02 03:04:05"]),
})


@pytest.mark.parametrize("compression,codec", [
  (None, "UNCOMPRESSED"), ("snappy", "SNAPPY"), ("gzip", "GZIP"), ("zstd", "ZSTD"), ("brotli", "BROTLI"), ("lz4", "LZ4"),
])
def test_parquet_reads_back_equal(tmp_path, compression, codec):
  path = str(tmp_path / "f.parquet")
  FileHandler.to_parquet(lambda: FRAME.set_axis([7, 9]), path, {"compression": compression})()
  pd.testing.assert_frame_equal(pd.read_parquet(path), FRAME)  # index dropped, values and dtypes kept
  assert pq.ParquetFile(path).metadata.row_group(0).column(0).compression == codec


def test_csv_divergences_from_pandas(tmp_path):
  path = str(tmp_path / "f.csv")
  FileHandler.to_csv(lambda: FRAME, path, {"index": False})()
  with open(path, encoding="utf-8") as f:
    assert f.read() == (
      '"b","f","g","s","t"\n'
      'true,1,1,"x",2024-01-01 00:00:00.000000000\n'
      'false,2.5,2,"é",2024-01-02 03:04:05.000000000\n'
    )
  assert pd.read_csv(path)["g"].tolist() == [1, 2] and pd.read_csv(path)["g"].dtype == "int64"


@contextmanager
def _zip_member(path, mode):
  with zipfile.ZipFile(path) as archive, archive.open("f.csv") as member:
    yield member


@pytest.mark.parametrize("compression,opener", [
  ("gzip", gzip.open), ("bz2", bz2.open), ("xz", lzma.open),
  ("zip", _zip_member),
])
def test_csv_every_compression_reads_back(tmp_path, compression, opener):
  path = str(tmp_path / f"f.csv.{compression}")
  FileHandler.to_csv(lambda: FRAME, path, {"compression": compression, "sep": ";"})()
  with opener(path, "rb") as f:
    assert f.read().decode().splitlines()[1] == 'true;1;1;"x";2024-01-01 00:00:00.000000000'


def test_csv_mixed_type_column_raises_naming_it(tmp_path):
  frame = pd.DataFrame({"ok": [1, 2], "mixed": [1, "a"]})
  with pytest.raises(RandEngineError, match="'mixed'"):
    FileHandler.to_csv(lambda: frame, str(tmp_path / "f.csv"), {})()


@pytest.mark.parametrize("format_type,accepted", [
  ("csv", "index, sep, compression, numFiles"),
  ("parquet", "compression, numFiles"),
  ("json", "orient, force_ascii, indent, compression, numFiles"),
])
def test_undocumented_option_raises_naming_it_and_accepted(rand_spec_with_kwargs, tmp_path, format_type, accepted):
  with pytest.raises(RandEngineError, match=f"'engine'.*accepted: {accepted}$"):
    DataGenerator(rand_spec_with_kwargs).size(2).write.format(format_type).option("engine", "x").save(str(tmp_path / "f"))


def test_json_documented_options_apply(tmp_path):
  path = str(tmp_path / "f.json.gz")
  frame = pd.DataFrame({"s": ["é"]})
  FileHandler.to_json(lambda: frame, path, {"orient": "records", "force_ascii": False, "indent": 2, "compression": "gzip"})()
  with gzip.open(path, "rt", encoding="utf-8") as f:
    assert f.read() == '\n  {\n    "s":"é"\n  }\n\n'


def test_csv_undocumented_compression_raises(tmp_path):
  with pytest.raises(RandEngineError, match="'zstd'.*accepted: gzip, bz2, xz, zip$"):
    FileHandler.to_csv(lambda: FRAME, str(tmp_path / "f.csv"), {"compression": "zstd"})


def test_json_orient_other_than_records_raises(tmp_path):
  with pytest.raises(RandEngineError, match="'orient' accepts only 'records'"):
    FileHandler.to_json(lambda: FRAME, str(tmp_path / "f.json"), {"orient": "split"})


def test_parquet_default_codec_is_snappy(tmp_path):
  path = str(tmp_path / "f.parquet")
  FileHandler.to_parquet(lambda: FRAME, path, {})()
  assert pq.ParquetFile(path).metadata.row_group(0).column(0).compression == "SNAPPY"


def test_csv_zip_member_is_deflated(tmp_path):
  path = str(tmp_path / "f.csv.zip")
  FileHandler.to_csv(lambda: FRAME, path, {"compression": "zip"})()
  with zipfile.ZipFile(path) as archive:
    assert archive.getinfo("f.csv").compress_type == zipfile.ZIP_DEFLATED


def test_csv_index_other_than_false_raises(tmp_path):
  with pytest.raises(RandEngineError, match="'index' accepts only False"):
    FileHandler.to_csv(lambda: FRAME, str(tmp_path / "f.csv"), {"index": True})


def test_csv_tz_aware_in_pandas_form_nat_empty_with_lf_lines(tmp_path):
  path = str(tmp_path / "f.csv")
  frame = pd.DataFrame({
    "utc": pd.to_datetime(["2024-01-01 00:00:00", None], utc=True),
    "local": pd.to_datetime(["2024-01-01 09:00:00", "2024-01-02 03:04:05"]).tz_localize("America/Sao_Paulo"),
  })
  FileHandler.to_csv(lambda: frame, path, {})()
  with open(path, "rb") as f:
    assert f.read() == b'"utc","local"\n"2024-01-01 00:00:00+00:00","2024-01-01 09:00:00-03:00"\n,"2024-01-02 03:04:05-03:00"\n'


def test_parquet_tz_aware_round_trip_keeps_dtype(tmp_path):
  path = str(tmp_path / "f.parquet")
  frame = pd.DataFrame({"t": pd.to_datetime(["2024-01-01 09:00:00", None]).tz_localize("America/Sao_Paulo")})
  FileHandler.to_parquet(lambda: frame, path, {})()
  back = pd.read_parquet(path)
  pd.testing.assert_frame_equal(back, frame)
  assert str(back["t"].dtype) == "datetime64[ns, America/Sao_Paulo]"


def test_csv_one_column_null_is_blank_line_lost_on_read_back(tmp_path):
  path = str(tmp_path / "f.csv")
  FileHandler.to_csv(lambda: pd.DataFrame({"s": ["x", None, "y"]}), path, {})()
  with open(path, "rb") as f:
    assert f.read() == b'"s"\n"x"\n\n"y"\n'
  assert pd.read_csv(path)["s"].tolist() == ["x", "y"]


def test_undocumented_option_fails_before_overwrite_deletes(rand_spec_with_kwargs, tmp_path):
  path = str(tmp_path / "clients")
  os.makedirs(path)
  open(f"{path}/keep.csv", "w").close()
  with pytest.raises(RandEngineError, match="'engine'"):
    DataGenerator(rand_spec_with_kwargs).size(4).write.option("numFiles", 2).option("engine", "x").mode("overwrite").save(path)
  assert os.listdir(path) == ["keep.csv"]


def test_csv_all_midnight_written_in_full(tmp_path):
  path = str(tmp_path / "f.csv")
  FileHandler.to_csv(lambda: pd.DataFrame({"midnight": pd.to_datetime(["2020-01-01"])}), path, {})()
  with open(path, "rb") as f:
    assert f.read() == b'"midnight"\n2020-01-01 00:00:00.000000000\n'


PK_SPEC = {"id": {"method": "pk", "kwargs": {"style": "sequence", "start": 1, "step": 1}}}


def _save_error(writer, path):
  try:
    writer.save(str(path))
  except (AttributeError, ImportError, TypeError):
    raise
  except Exception as error:
    return error
  return None


def _directory_bytes(path):
  return {
    str(file.relative_to(path)): file.read_bytes()
    for file in sorted(path.rglob("*"))
    if file.is_file()
  }


def _existing_directory(tmp_path, name):
  path = tmp_path / name
  path.mkdir()
  (path / "part_original.csv").write_bytes(b'"id"\n999\n')
  return path, _directory_bytes(path)


def test_batched_plan_writes_four_final_files_with_literal_offsets_and_bound(tmp_path):
  observed = []

  def observe(frame):
    observed.append((len(frame), frame["id"].tolist()))
    return frame

  path = tmp_path / "parts"
  error = _save_error(
    DataGenerator(PK_SPEC, seed=7)
      .size(23)
      .transformers([observe])
      .write
      .format("parquet")
      .options(numFiles=4, maxRowsPerBatch=3),
    path,
  )
  files = sorted(path.glob("part_*")) if path.exists() else []
  frames = [pd.read_parquet(file) for file in files]

  assert error is None
  assert len(files) == 4
  assert sorted(len(frame) for frame in frames) == [5, 6, 6, 6]
  assert sorted(pd.concat(frames)["id"].tolist()) == list(range(1, 24))
  assert observed == [
    (3, [1, 2, 3]), (3, [4, 5, 6]),
    (3, [7, 8, 9]), (3, [10, 11, 12]),
    (3, [13, 14, 15]), (3, [16, 17, 18]),
    (3, [19, 20, 21]), (2, [22, 23]),
  ]


def test_unbatched_save_keeps_one_frame_and_one_transformer_call(tmp_path):
  observed = []

  def observe(frame):
    observed.append(len(frame))
    return frame

  path = tmp_path / "unbatched.parquet"
  DataGenerator(PK_SPEC).size(23).transformers([observe]).write.format("parquet").save(str(path))

  assert observed == [23]
  assert pd.read_parquet(path)["id"].tolist() == list(range(1, 24))


def test_none_batch_limit_keeps_old_unbatched_cadence(tmp_path):
  observed = []

  def observe(frame):
    observed.append(len(frame))
    return frame

  path = tmp_path / "none-limit.parquet"
  error = _save_error(
    DataGenerator(PK_SPEC)
      .size(23)
      .transformers([observe])
      .write
      .format("parquet")
      .option("maxRowsPerBatch", None),
    path,
  )

  assert error is None
  assert observed == [23]
  assert pd.read_parquet(path)["id"].tolist() == list(range(1, 24))


@pytest.mark.parametrize("invalid", [0, -1, True, 1.5, "3"])
def test_invalid_batch_limit_is_refused_before_destination_changes(tmp_path, invalid):
  path = tmp_path / f"invalid-{invalid!s}.csv"
  path.write_bytes(b'"id"\n999\n')

  error = _save_error(
    DataGenerator(PK_SPEC)
      .size(2)
      .write
      .format("csv")
      .option("maxRowsPerBatch", invalid),
    path,
  )

  assert isinstance(error, RandEngineError)
  assert path.read_bytes() == b'"id"\n999\n'


def test_batch_control_options_do_not_reach_the_format_adapter(tmp_path):
  path = tmp_path / "control-options.csv"
  error = _save_error(
    DataGenerator(PK_SPEC)
      .size(5)
      .write
      .format("csv")
      .options(numFiles=1, maxRowsPerBatch=2),
    path,
  )

  assert error is None
  assert pd.read_csv(path)["id"].tolist() == [1, 2, 3, 4, 5]


def test_zero_row_final_partitions_skip_generation_and_transformers(tmp_path):
  observed = []

  def observe(frame):
    observed.append(len(frame))
    return frame

  path = tmp_path / "sparse-parts"
  error = _save_error(
    DataGenerator(PK_SPEC)
      .size(2)
      .transformers([observe])
      .write
      .format("parquet")
      .options(numFiles=4, maxRowsPerBatch=3),
    path,
  )
  files = sorted(path.glob("part_*")) if path.exists() else []

  assert error is None
  assert len(files) == 4
  assert observed == [1, 1]
  assert sorted(len(pd.read_parquet(file)) for file in files) == [0, 0, 1, 1]


def test_batched_generation_releases_each_frame_before_consuming_the_next(tmp_path):
  prior_frames = []
  observed = []

  def observe(frame):
    gc.collect()
    if prior_frames:
      assert prior_frames[-1]() is None
    prior_frames.append(weakref.ref(frame))
    observed.append(len(frame))
    return frame

  error = _save_error(
    DataGenerator(PK_SPEC)
      .size(8)
      .transformers([observe])
      .write
      .format("parquet")
      .option("maxRowsPerBatch", 3),
    tmp_path / "lazy.parquet",
  )

  assert error is None
  assert observed == [3, 3, 2]


def test_bad_format_option_preserves_destination_bytes(tmp_path):
  path, before = _existing_directory(tmp_path, "bad-option")
  error = _save_error(
    DataGenerator(PK_SPEC)
      .size(4)
      .write
      .format("csv")
      .mode("overwrite")
      .options(numFiles=2, engine="unknown"),
    path,
  )

  assert isinstance(error, RandEngineError)
  assert _directory_bytes(path) == before


def test_invalid_resolved_size_preserves_destination_bytes(tmp_path):
  path, before = _existing_directory(tmp_path, "bad-size")
  error = _save_error(
    DataGenerator(PK_SPEC)
      .size(-1)
      .write
      .format("csv")
      .mode("overwrite")
      .option("numFiles", 2),
    path,
  )

  assert error is not None
  assert _directory_bytes(path) == before


def test_transformer_failure_preserves_destination_bytes(tmp_path):
  path, before = _existing_directory(tmp_path, "transform-failure")

  def fail(_frame):
    raise RuntimeError("transform failed")

  error = _save_error(
    DataGenerator(PK_SPEC)
      .size(4)
      .transformers([fail])
      .write
      .format("csv")
      .mode("overwrite")
      .option("numFiles", 2),
    path,
  )

  assert isinstance(error, RuntimeError)
  assert _directory_bytes(path) == before


def test_anomaly_compatibility_failure_preserves_destination_bytes(tmp_path):
  path, before = _existing_directory(tmp_path, "anomaly-failure")
  spec = {
    "value": {
      "method": "integers",
      "kwargs": {"min": 0, "max": 2},
      "anomaly_rate": 1,
      "anomaly_values": [1],
    }
  }

  def strings(frame):
    return frame.astype({"value": "string"})

  error = _save_error(
    DataGenerator(spec)
      .size(4)
      .transformers([strings])
      .write
      .format("csv")
      .mode("overwrite")
      .option("numFiles", 2),
    path,
  )

  assert isinstance(error, RandEngineError)
  assert _directory_bytes(path) == before


def test_arrow_schema_failure_preserves_destination_bytes(tmp_path):
  path, before = _existing_directory(tmp_path, "schema-failure")

  def mixed(frame):
    frame["id"] = pd.Series([1, "bad"] * (len(frame) // 2), dtype=object)
    return frame

  error = _save_error(
    DataGenerator(PK_SPEC)
      .size(4)
      .transformers([mixed])
      .write
      .format("csv")
      .mode("overwrite")
      .option("numFiles", 2),
    path,
  )

  assert isinstance(error, RandEngineError)
  assert _directory_bytes(path) == before


def test_single_file_commit_failure_preserves_destination_bytes(tmp_path, monkeypatch):
  path = tmp_path / "commit.csv"
  path.write_bytes(b'"id"\n999\n')
  real_replace = os.replace

  def fail_commit(source, destination):
    if os.path.abspath(destination) == os.path.abspath(path):
      raise OSError("commit failed")
    return real_replace(source, destination)

  monkeypatch.setattr(os, "replace", fail_commit)
  error = _save_error(
    DataGenerator(PK_SPEC).size(3).write.format("csv").mode("overwrite"),
    path,
  )

  assert isinstance(error, OSError)
  assert path.read_bytes() == b'"id"\n999\n'


def test_directory_commit_failure_rolls_the_old_destination_back(tmp_path, monkeypatch):
  path, before = _existing_directory(tmp_path, "rollback")
  real_rename, real_replace = os.rename, os.replace
  moves = []
  failed_commit = False

  def guarded_move(real_move):
    def move(source, destination):
      nonlocal failed_commit
      moves.append((os.path.abspath(source), os.path.abspath(destination)))
      if os.path.abspath(destination) == os.path.abspath(path) and not failed_commit:
        failed_commit = True
        raise OSError("staging commit failed")
      return real_move(source, destination)
    return move

  monkeypatch.setattr(os, "rename", guarded_move(real_rename))
  monkeypatch.setattr(os, "replace", guarded_move(real_replace))
  error = _save_error(
    DataGenerator(PK_SPEC)
      .size(4)
      .write
      .format("csv")
      .mode("overwrite")
      .option("numFiles", 2),
    path,
  )

  assert isinstance(error, OSError)
  assert len(moves) >= 3
  assert _directory_bytes(path) == before
