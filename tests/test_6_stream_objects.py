
from datetime import date, datetime as dt
from itertools import islice

import numpy as np
import pandas as pd
import pyarrow as pa
import pytest

import rand_engine.main.data_generator as data_generator_module
import rand_engine.utils.stream_handler as stream_handler_module
from rand_engine.main.data_generator import DataGenerator
from tests.fixtures.f1_data_generator_specs_right import rand_spec_with_args

from tests.fixtures.f3_integrations import (
    df_size,
    batch_size,
)


def test_pandas_df_kwargs(df_size, rand_spec_with_args):
  """
  This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
  using keyword arguments.
  """
  df_data = DataGenerator(rand_spec_with_args).size(df_size).get_df()
  assert df_data.shape[0] == df_size




@pytest.mark.parametrize("size", [3, lambda: 3])
def test_create_stream_dict(size, rand_spec_with_args):
  """Intent: CONTRACT — writer-size-not-from-generator: stream_dict resolves int and callable size."""
  stream = DataGenerator(rand_spec_with_args).size(size).stream_dict(min_throughput=1000, max_throughput=1000)
  records = list(islice(stream, 3))
  assert [set(r) for r in records] == [set(rand_spec_with_args) | {"timestamp_created"}] * 3


def test_stream_dict_normalizes_missing_values_to_none():
  """Intent: AC3.4 — stream records expose Python None and preserve ordinary values."""
  def with_missing_values(frame):
    return pd.DataFrame(
      {
        "integer": pd.array([7, pd.NA], dtype="Int64"),
        "boolean": pd.array([True, pd.NA], dtype="boolean"),
        "floating": [1.5, float("nan")],
        "datetime": [pd.Timestamp(dt(2025, 1, 2, 3, 4, 5)), pd.NaT],
        "object": ["kept", None],
        "date": [date(2025, 1, 2), None],
      },
      index=frame.index,
    )

  stream = (
    DataGenerator({"source": {"method": "constant", "kwargs": {"value": 1}}})
    .size(2)
    .transformers([with_missing_values])
    .stream_dict(min_throughput=1000, max_throughput=1000)
  )
  records = list(islice(stream, 2))
  timestamps = [record.pop("timestamp_created") for record in records]

  assert all(isinstance(timestamp, float) for timestamp in timestamps)
  assert records == [
    {
      "integer": 7,
      "boolean": True,
      "floating": 1.5,
      "datetime": "2025-01-02 03:04:05",
      "object": "kept",
      "date": date(2025, 1, 2),
    },
    {
      "integer": None,
      "boolean": None,
      "floating": None,
      "datetime": None,
      "object": None,
      "date": None,
    },
  ]


def _record_arrow_boundary(monkeypatch, action):
  """Record conversion at the external Arrow boundary without replacing its result."""
  table = data_generator_module.pa.Table
  calls = []

  class RecordedTable:
    @staticmethod
    def from_pandas(frame, preserve_index):
      calls.append((frame.copy(), preserve_index))
      return action(table, frame, preserve_index)

  monkeypatch.setattr(data_generator_module.pa, "Table", RecordedTable)
  return calls


def _safe_stream_frame(frame):
  """Return normalized-safe values that pass through a global transformer."""
  return pd.DataFrame(
    {
      "integer": pd.array([7, pd.NA], dtype="Int64"),
      "boolean": pd.array([True, pd.NA], dtype="boolean"),
      "floating": [1.5, float("nan")],
      "datetime": [pd.Timestamp(dt(2025, 1, 2, 3, 4, 5)), pd.NaT],
      "text": ["event-a", "event-b" * 8],
      "date": [date(2025, 1, 2), None],
      "transformed": ["safe-7", "safe-8"],
    },
    index=frame.index,
  )


def _stream_for_frame(transformer, size=2):
  return (
    DataGenerator({"source": {"method": "constant", "kwargs": {"value": 1}}})
    .size(size)
    .transformers([transformer])
    .stream_dict(min_throughput=10**9, max_throughput=10**9)
  )


def test_stream_dict_uses_arrow_after_normalization_for_lossless_records(monkeypatch):
  """Normalized scalar records take Arrow and keep their exact public values."""
  calls = _record_arrow_boundary(
    monkeypatch,
    lambda table, frame, preserve_index: table.from_pandas(frame, preserve_index=preserve_index),
  )

  records = list(islice(_stream_for_frame(_safe_stream_frame), 2))
  timestamps = [record.pop("timestamp_created") for record in records]

  assert [(list(frame.columns), preserve_index) for frame, preserve_index in calls] == [
    (["integer", "boolean", "floating", "datetime", "text", "date", "transformed"], False)
  ]
  assert all(type(timestamp) is float for timestamp in timestamps)
  assert records == [
    {
      "integer": 7,
      "boolean": True,
      "floating": 1.5,
      "datetime": "2025-01-02 03:04:05",
      "text": "event-a",
      "date": date(2025, 1, 2),
      "transformed": "safe-7",
    },
    {
      "integer": None,
      "boolean": None,
      "floating": None,
      "datetime": None,
      "text": "event-b" * 8,
      "date": None,
      "transformed": "safe-8",
    },
  ]
  assert {name: type(value) for name, value in records[0].items()} == {
    "integer": int,
    "boolean": bool,
    "floating": float,
    "datetime": str,
    "text": str,
    "date": date,
    "transformed": str,
  }


class _CustomValue:
  def __init__(self, value):
    self.value = value


class _TaggedText(str):
  pass


@pytest.mark.parametrize(
  ("value", "assert_value"),
  [
    ((1, "two"), lambda actual: actual == (1, "two")),
    (np.array([1, 2]), lambda actual: type(actual) is np.ndarray and actual.tolist() == [1, 2]),
    (_TaggedText("kept"), lambda actual: type(actual) is _TaggedText and actual == "kept"),
    (_CustomValue("kept"), lambda actual: type(actual) is _CustomValue and actual.value == "kept"),
  ],
  ids=["tuple", "numpy-array", "string-subclass", "custom-object"],
)
def test_stream_dict_keeps_unproved_object_values_on_pandas_path(monkeypatch, value, assert_value):
  """Containers and custom values never enter Arrow's lossy representation."""
  calls = _record_arrow_boundary(
    monkeypatch,
    lambda table, frame, preserve_index: pytest.fail("unproved object values must not enter Arrow"),
  )

  records = list(islice(_stream_for_frame(lambda frame: pd.DataFrame({"value": [value]}, index=frame.index[:1]), 1), 1))

  assert calls == []
  assert assert_value(records[0]["value"])


def test_stream_dict_keeps_mixed_object_column_on_pandas_path(monkeypatch):
  """One nested value keeps the complete mixed object column lossless."""
  calls = _record_arrow_boundary(
    monkeypatch,
    lambda table, frame, preserve_index: pytest.fail("mixed object columns must not enter Arrow"),
  )

  records = list(islice(
    _stream_for_frame(lambda frame: pd.DataFrame({"value": ["safe", (1, 2)]}, index=frame.index)),
    2,
  ))

  assert calls == []
  assert records[0]["value"] == "safe"
  assert type(records[1]["value"]) is tuple
  assert records[1]["value"] == (1, 2)


def test_stream_dict_falls_back_only_for_arrow_representation_error(monkeypatch):
  """An Arrow representation failure retains pandas records unchanged."""
  calls = _record_arrow_boundary(
    monkeypatch,
    lambda table, frame, preserve_index: (_ for _ in ()).throw(pa.ArrowInvalid("cannot represent value")),
  )

  records = list(islice(_stream_for_frame(_safe_stream_frame), 2))
  for record in records:
    record.pop("timestamp_created")

  assert len(calls) == 1
  assert records[0]["integer"] == 7
  assert records[1]["integer"] is None
  assert records[0]["date"] == date(2025, 1, 2)


def test_stream_dict_propagates_non_representation_arrow_failure(monkeypatch):
  """Unrelated conversion failures remain visible to the caller."""
  calls = _record_arrow_boundary(
    monkeypatch,
    lambda table, frame, preserve_index: (_ for _ in ()).throw(RuntimeError("unexpected Arrow failure")),
  )

  stream = _stream_for_frame(_safe_stream_frame)

  with pytest.raises(RuntimeError, match="unexpected Arrow failure"):
    next(stream)
  assert len(calls) == 1


def test_stream_dict_arrow_batches_keep_order_and_cadence(monkeypatch):
  """Arrow conversion stays one conversion per ordered stream microbatch."""
  calls = _record_arrow_boundary(
    monkeypatch,
    lambda table, frame, preserve_index: table.from_pandas(frame, preserve_index=preserve_index),
  )
  sleeps = []
  monkeypatch.setattr(stream_handler_module.time, "sleep", sleeps.append)
  spec = {"id": {"method": "pk", "kwargs": {"style": "sequence", "start": 1, "step": 1}}}

  records = list(islice(DataGenerator(spec).size(2).stream_dict(50, 100), 5))

  assert [record["id"] for record in records] == [1, 2, 3, 4, 5]
  assert all(type(record["timestamp_created"]) is float for record in records)
  assert [(len(frame), preserve_index) for frame, preserve_index in calls] == [(2, False)] * 3
  assert len(sleeps) == 4
  assert all(1 / 100 <= duration <= 1 / 50 for duration in sleeps)
