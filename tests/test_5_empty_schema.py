import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from rand_engine import DataGenerator
from rand_engine.validators.exceptions import RandEngineError


EMPTY_SPEC = {
    "small": {
        "method": "integers",
        "kwargs": {"min": 0, "max": 9, "int_type": "int8"},
        "null_rate": 1,
    },
    "missing": {"method": "constant", "kwargs": {"value": None}},
    "label": {"method": "constant", "kwargs": {"value": "x"}},
}

ARROW_SCHEMA = pa.schema(
    [
        pa.field("small", pa.int8(), nullable=True),
        pa.field("missing", pa.null(), nullable=True),
        pa.field("label", pa.string(), nullable=True),
    ]
)


class _ObservedRng:
    def __init__(self, rng, requests):
        self._rng = rng
        self._requests = requests

    def __getattr__(self, name):
        value = getattr(self._rng, name)
        if not callable(value):
            return value

        def observe(*args, **kwargs):
            self._requests.append(name)
            return value(*args, **kwargs)

        return observe


def _observe_numpy_requests(monkeypatch):
    requests = []
    default_rng = np.random.default_rng

    def observed_default_rng(seed=None):
        return _ObservedRng(default_rng(seed), requests)

    monkeypatch.setattr(np.random, "default_rng", observed_default_rng)
    return requests


def _save_error(writer, path):
    try:
        writer.save(str(path))
    except Exception as error:
        return error
    return None


def _outputs(path, count):
    if count == 1:
        return sorted(path.parent.glob(f"{path.name}.*"))
    return sorted(path.glob("part_*")) if path.exists() else []


def _read_empty_output(format_type, path):
    if format_type == "csv":
        frame = pd.read_csv(path)
        return (
            len(frame),
            tuple(frame.columns),
            path.read_bytes(),
        )
    if format_type == "json":
        records = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return len(records), tuple(records)

    parquet = pq.ParquetFile(path)
    frame = pd.read_parquet(path)
    schema = parquet.schema_arrow.remove_metadata()
    return (
        parquet.metadata.num_rows,
        len(frame),
        tuple(frame.columns),
        schema,
        tuple(field.nullable for field in schema),
    )


def _parquet_result(writer, path):
    error = _save_error(writer, path)
    output = path.with_suffix(".parquet")
    if error is not None or not output.exists():
        return type(error) if error else None, None, None
    table = pq.read_table(output)
    return None, table.schema.remove_metadata(), table.to_pydict()


def _expected_readback(format_type):
    if format_type == "csv":
        return (0, ("small", "missing", "label"), b'"small","missing","label"\n')
    if format_type == "json":
        return 0, ()
    return (
        0,
        0,
        ("small", "missing", "label"),
        ARROW_SCHEMA,
        (True, True, True),
    )


@pytest.mark.parametrize("format_type", ["csv", "json", "parquet"])
@pytest.mark.parametrize("file_count", [1, 3])
def test_determinate_empty_saves_repeat_with_typed_files_and_no_rng(
    tmp_path, monkeypatch, format_type, file_count
):
    requests = _observe_numpy_requests(monkeypatch)
    writer = DataGenerator(EMPTY_SPEC, seed=7).size(0).write.format(format_type)
    if file_count > 1:
        writer.option("numFiles", file_count)

    saves = []
    for repetition in ("first", "second"):
        path = tmp_path / f"{format_type}-{file_count}-{repetition}"
        error = _save_error(writer, path)
        outputs = _outputs(path, file_count)
        saves.append(
            (
                type(error) if error else None,
                len(outputs),
                tuple(_read_empty_output(format_type, output) for output in outputs),
            )
        )

    expected_output = _expected_readback(format_type)
    assert (saves, requests) == (
        [
            (None, file_count, (expected_output,) * file_count),
            (None, file_count, (expected_output,) * file_count),
        ],
        [],
    )


def test_indeterminate_empty_transform_preserves_destination_without_calls(
    tmp_path, monkeypatch
):
    path = tmp_path / "existing.parquet"
    DataGenerator(
        {"value": {"method": "constant", "kwargs": {"value": "original"}}}
    ).size(1).write.format("parquet").save(str(path))
    before = path.read_bytes()
    transform_calls = []
    requests = _observe_numpy_requests(monkeypatch)

    def arbitrary_transform(frame):
        transform_calls.append(len(frame))
        return frame.rename(columns={"small": "unknown"})

    indeterminate_spec = {
        "small": {
            "method": "integers",
            "kwargs": {"min": 0, "max": 9, "int_type": "int8"},
        },
        "label": {"method": "constant", "kwargs": {"value": "x"}},
    }
    error = _save_error(
        DataGenerator(indeterminate_spec, seed=11)
        .size(0)
        .transformers([arbitrary_transform])
        .write.format("parquet")
        .mode("overwrite"),
        path,
    )

    assert (
        type(error),
        "schema" in str(error).lower() or "indeterminate" in str(error).lower(),
        transform_calls,
        requests,
        path.read_bytes() == before,
    ) == (RandEngineError, True, [], [], True)


@pytest.mark.parametrize(
    "value, expected_type",
    [
        (datetime(2024, 1, 1, 12, 30), pa.timestamp("ns")),
        (
            datetime(2024, 1, 1, 12, 30, tzinfo=timezone.utc),
            pa.timestamp("ns", tz="UTC"),
        ),
        (datetime(3000, 1, 1), pa.timestamp("us")),
    ],
    ids=["naive", "utc-aware", "outside-nanosecond-range"],
)
def test_constant_datetime_empty_parquet_keeps_nonempty_timestamp_carrier(
    tmp_path, monkeypatch, value, expected_type
):
    spec = {"event_at": {"method": "constant", "kwargs": {"value": value}}}
    populated = _parquet_result(
        DataGenerator(spec, seed=41).size(1).write.format("parquet"),
        tmp_path / "populated",
    )
    requests = _observe_numpy_requests(monkeypatch)
    empty = _parquet_result(
        DataGenerator(spec, seed=41).size(0).write.format("parquet"),
        tmp_path / "empty",
    )
    expected_schema = pa.schema([pa.field("event_at", expected_type)])

    assert (populated, empty, requests) == (
        (None, expected_schema, {"event_at": [value]}),
        (None, expected_schema, {"event_at": []}),
        [],
    )


def test_constant_string_all_null_parquet_retains_declared_logical_type(tmp_path):
    spec = {
        "label": {
            "method": "constant",
            "kwargs": {"value": "declared"},
            "null_rate": 1,
        }
    }

    result = _parquet_result(
        DataGenerator(spec, seed=1).size(3).write.format("parquet"),
        tmp_path / "all-null",
    )

    assert result == (
        None,
        pa.schema([pa.field("label", pa.string())]),
        {"label": [None, None, None]},
    )


def test_constant_string_null_first_batch_keeps_schema_for_later_values(tmp_path):
    spec = {
        "label": {
            "method": "constant",
            "kwargs": {"value": "declared"},
            "null_rate": 0.5,
        }
    }
    writer = (
        DataGenerator(spec, seed=3)
        .size(4)
        .write.format("parquet")
        .option("maxRowsPerBatch", 2)
    )

    result = _parquet_result(writer, tmp_path / "mixed-null")

    assert result == (
        None,
        pa.schema([pa.field("label", pa.string())]),
        {"label": [None, None, "declared", "declared"]},
    )
