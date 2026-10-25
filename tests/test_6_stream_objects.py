
from datetime import date, datetime as dt
from itertools import islice

import numpy as np
import pandas as pd
import pytest

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


def _safe_stream_frame(frame):
  """Return normalized-safe values that pass through a global transformer."""
  return pd.DataFrame(
    {
      "integer": pd.array([7, pd.NA], dtype="Int64"),
      "nullable_integer": pd.array([8, 9], dtype="Int64"),
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


def test_stream_dict_preserves_normalized_record_values_and_types():
  """Normalized scalar records retain their exact public values and types."""
  records = list(islice(_stream_for_frame(_safe_stream_frame), 2))
  timestamps = [record.pop("timestamp_created") for record in records]

  assert all(type(timestamp) is float for timestamp in timestamps)
  assert records == [
    {
      "integer": 7,
      "nullable_integer": 8,
      "boolean": True,
      "floating": 1.5,
      "datetime": "2025-01-02 03:04:05",
      "text": "event-a",
      "date": date(2025, 1, 2),
      "transformed": "safe-7",
    },
    {
      "integer": None,
      "nullable_integer": 9,
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
    "nullable_integer": int,
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
def test_stream_dict_preserves_object_values(value, assert_value):
  """Containers and custom values retain their representation."""
  records = list(islice(_stream_for_frame(lambda frame: pd.DataFrame({"value": pd.Series([value], dtype=object, index=frame.index[:1])}, index=frame.index[:1]), 1), 1))

  assert assert_value(records[0]["value"])


def test_stream_dict_preserves_mixed_object_values():
  """One nested value keeps the complete mixed object column lossless."""
  records = list(islice(
    _stream_for_frame(lambda frame: pd.DataFrame({"value": ["safe", (1, 2)]}, index=frame.index)),
    2,
  ))

  assert records[0]["value"] == "safe"
  assert type(records[1]["value"]) is tuple
  assert records[1]["value"] == (1, 2)


@pytest.mark.parametrize(
  ("frame_factory", "expected_records"),
  [
    (
      lambda index: pd.DataFrame({"value": pd.Series([1, 2.5], dtype="object")}, index=index),
      [{"value": 1}, {"value": 2.5}],
    ),
    (
      lambda index: pd.DataFrame(
        {"value": pd.Series([np.complex128(1 + 2j), np.complex128(3 + 4j)])}, index=index
      ),
      [{"value": 1 + 2j}, {"value": 3 + 4j}],
    ),
    (
      lambda index: pd.DataFrame({"value": pd.Series([date(2025, 1, 2), 1], dtype="object")}, index=index),
      [{"value": date(2025, 1, 2)}, {"value": 1}],
    ),
    (
      lambda index: pd.DataFrame({"value": pd.Series([2**63, 1], dtype="object")}, index=index),
      [{"value": 2**63}, {"value": 1}],
    ),
    (
      lambda index: pd.DataFrame(
        {"value": pd.Series(pd.Categorical(pd.Series([_TaggedText("kept"), _TaggedText("two")], dtype=object)))}, index=index
      ),
      [{"value": _TaggedText("kept")}, {"value": _TaggedText("two")}],
    ),
    (
      lambda index: pd.DataFrame(
        {"value": pd.Series([_TaggedText("kept"), _TaggedText("two")], dtype=pd.StringDtype("python"))}, index=index
      ),
      [{"value": _TaggedText("kept")}, {"value": _TaggedText("two")}],
    ),
    (
      lambda index: pd.DataFrame(
        {"value": pd.Series([pd.Period("2025-01", freq="M"), pd.Period("2025-02", freq="M")])},
        index=index,
      ),
      [{"value": pd.Period("2025-01", freq="M")}, {"value": pd.Period("2025-02", freq="M")}],
    ),
    (
      lambda index: pd.DataFrame(
        {"value": pd.Series([pd.Interval(1, 2), pd.Interval(3, 4)])}, index=index
      ),
      [{"value": pd.Interval(1, 2)}, {"value": pd.Interval(3, 4)}],
    ),
    (
      lambda index: pd.DataFrame([[7], [8]], columns=[1], index=index),
      [{1: 7}, {1: 8}],
    ),
  ],
  ids=[
    "heterogeneous-numbers",
    "complex",
    "date-and-int",
    "large-integer",
    "category-string-subclass",
    "extension-string-subclass",
    "period-extension",
    "interval-extension",
    "non-string-label",
  ],
)
def test_stream_dict_preserves_scalar_and_label_partitions(frame_factory, expected_records):
  """Scalar and label partitions retain their existing records."""
  stream = _stream_for_frame(lambda frame: frame_factory(frame.index))
  records = list(islice(stream, 2))
  for record in records:
    record.pop("timestamp_created")

  assert records == expected_records
  for record, expected in zip(records, expected_records):
    assert {key: type(value) for key, value in record.items()} == {
      key: type(value) for key, value in expected.items()
    }


def test_stream_dict_batches_keep_order_and_cadence(monkeypatch):
  """Ordered stream microbatches retain continuous keys and cadence."""
  sleeps = []
  monkeypatch.setattr(stream_handler_module.time, "sleep", sleeps.append)
  spec = {"id": {"method": "pk", "kwargs": {"style": "sequence", "start": 1, "step": 1}}}

  records = list(islice(DataGenerator(spec).size(2).stream_dict(50, 100), 5))

  assert [record["id"] for record in records] == [1, 2, 3, 4, 5]
  assert all(type(record["timestamp_created"]) is float for record in records)
  assert len(sleeps) == 4
  assert all(1 / 100 <= duration <= 1 / 50 for duration in sleeps)


def _timestamp_transformer_spec():
  return {"d": {"method": "dates", "kwargs": {"start": "2024-01-01", "end": "2024-01-31"},
                "transformers": [pd.Timestamp]}}


def test_timestamp_transformer_column_has_datetime_dtype_and_streams_text():
  """A transformer's pd.Timestamp output keeps pandas' own datetime dtype and streams as text."""
  df = DataGenerator(_timestamp_transformer_spec(), seed=3).size(4).get_df()
  assert pd.api.types.is_datetime64_any_dtype(df["d"].dtype)
  assert not isinstance(df["d"].dtype, pd.ArrowDtype)

  record = next(DataGenerator(_timestamp_transformer_spec(), seed=3).size(4)
                .stream_dict(min_throughput=10**9, max_throughput=10**9))
  assert isinstance(record["d"], str)
  assert record["d"].startswith("2024-01-")
