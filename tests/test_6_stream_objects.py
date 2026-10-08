
from datetime import date, datetime as dt
from itertools import islice

import pandas as pd
import pytest

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
