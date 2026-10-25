import hashlib
import gzip
import json
from datetime import datetime, timezone

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from rand_engine import DataGenerator
from rand_engine.validators.exceptions import RandEngineError


PK_SPEC = {
    "id": {
        "method": "pk",
        "kwargs": {"style": "sequence", "start": 0, "step": 1},
    }
}


def _save(generator, path, format_type, mode="overwrite", **options):
    try:
        writer = generator.write.format(format_type).mode(mode)
        for name, value in options.items():
            writer.option(name, value)
        writer.save(str(path))
    except Exception as error:
        return error
    return None


def _single_output(path):
    outputs = list(path.parent.glob(f"{path.name}*"))
    assert len(outputs) == 1
    return outputs[0]


def test_csv_preserves_timezone_text_and_single_column_null_quoting(tmp_path):
    path = tmp_path / "timezone"

    def timezone_column(frame):
        return pd.DataFrame({
            "value": pd.Series(
                [pd.Timestamp("2024-01-01", tz="UTC"), pd.NaT],
                dtype="datetime64[ns, UTC]",
            )
        })

    error = _save(
        DataGenerator(PK_SPEC).transformers([timezone_column]).size(2),
        path,
        "csv",
    )

    assert error is None
    assert _single_output(path).read_bytes() == (
        b'"value"\n"2024-01-01 00:00:00+00:00"\n\n'
    )


@pytest.mark.parametrize(
    "batch_options",
    [{}, {"maxRowsPerBatch": None}],
    ids=["absent", "none"],
)
def test_json_heterogeneous_object_rows_keep_unbatched_compatibility(
    tmp_path,
    batch_options,
):
    path = tmp_path / "mixed"
    calls = []

    def heterogeneous_column(frame):
        calls.append(len(frame))
        return pd.DataFrame({"mixed": [1, "a"]})

    error = _save(
        DataGenerator(PK_SPEC).transformers([heterogeneous_column]).size(2),
        path,
        "json",
        **batch_options,
    )
    output = _single_output(path) if error is None else None

    assert (
        type(error) if error else None,
        calls,
        output.read_text(encoding="utf-8") if output else None,
    ) == (None, [2], '{"mixed":1}\n{"mixed":"a"}\n')


def test_json_batched_indeterminate_schema_preserves_destination(tmp_path):
    path = tmp_path / "mixed"
    assert _save(DataGenerator(PK_SPEC).size(1), path, "json") is None
    output = _single_output(path)
    before = output.read_bytes()
    calls = []

    def heterogeneous_column(frame):
        calls.append(len(frame))
        return pd.DataFrame({"mixed": [1, "a"]})

    error = _save(
        DataGenerator(PK_SPEC).transformers([heterogeneous_column]).size(2),
        path,
        "json",
        maxRowsPerBatch=2,
    )

    assert (type(error), calls, output.read_bytes() == before) == (
        RandEngineError,
        [2],
        True,
    )


def test_csv_batches_share_one_compressed_stream_and_one_header(tmp_path):
    path = tmp_path / "rows"
    error = _save(
        DataGenerator(PK_SPEC).size(5),
        path,
        "csv",
        compression="gzip",
        sep=";",
        maxRowsPerBatch=2,
    )
    output = _single_output(path) if error is None else None
    content = gzip.open(output, "rt", encoding="utf-8").read() if output else ""

    assert (error, content) == (None, '"id"\n0\n1\n2\n3\n4\n')


@pytest.mark.parametrize(
    "seed, expected_rows",
    [
        (
            3,
            [
                "",
                "",
                '"2024-01-01 12:30:00+00:00"',
                '"2024-01-01 12:30:00+00:00"',
            ],
        ),
        (
            15,
            [
                '"2024-01-01 12:30:00+00:00"',
                '"2024-01-01 12:30:00+00:00"',
                "",
                "",
            ],
        ),
        (45, ['"2024-01-01 12:30:00+00:00"'] * 4),
    ],
    ids=["null-first", "null-last", "no-nulls"],
)
def test_csv_timezone_batches_keep_one_text_carrier_across_null_layouts(
    tmp_path, seed, expected_rows
):
    path = tmp_path / f"timezone-{seed}"
    spec = {
        "event_at": {
            "method": "constant",
            "kwargs": {
                "value": datetime(2024, 1, 1, 12, 30, tzinfo=timezone.utc)
            },
            "null_rate": 0.5,
        }
    }

    error = _save(
        DataGenerator(spec, seed=seed).size(4),
        path,
        "csv",
        maxRowsPerBatch=2,
    )
    output = _single_output(path) if error is None else None
    rows = output.read_text(encoding="utf-8").splitlines() if output else None

    assert (error, rows) == (None, ['"event_at"', *expected_rows])


def test_json_batches_keep_lines_options_unicode_and_null(tmp_path):
    path = tmp_path / "rows"

    def nullable_text(frame):
        return frame.assign(value=frame["id"].map(lambda value: "é" if value % 2 == 0 else None))

    error = _save(
        DataGenerator(PK_SPEC).transformers([nullable_text]).size(3),
        path,
        "json",
        compression="gzip",
        force_ascii=False,
        orient="records",
        maxRowsPerBatch=2,
    )
    output = _single_output(path) if error is None else None
    records = (
        [json.loads(line) for line in gzip.open(output, "rt", encoding="utf-8")]
        if output else []
    )

    assert (error, records) == (
        None,
        [
            {"id": 0, "value": "é"},
            {"id": 1, "value": None},
            {"id": 2, "value": "é"},
        ],
    )


def test_parquet_batches_keep_nullable_schema_when_first_batch_is_all_null(tmp_path):
    path = tmp_path / "rows"

    def nullable_int8(frame):
        return frame.assign(value=frame["id"].where(frame["id"] >= 2).astype("Int8"))

    error = _save(
        DataGenerator(PK_SPEC).transformers([nullable_int8]).size(4),
        path,
        "parquet",
        maxRowsPerBatch=2,
    )
    output = _single_output(path) if error is None else None
    parquet = pq.ParquetFile(output) if output else None
    frame = pd.read_parquet(output) if output else None

    assert (
        error,
        parquet.metadata.num_row_groups if parquet else 0,
        parquet.schema_arrow.field("value").type if parquet else None,
        frame["value"].tolist() if frame is not None else [],
    ) == (None, 2, pa.int8(), [pd.NA, pd.NA, 2, 3])


@pytest.mark.parametrize("format_type", ["csv", "json", "parquet"])
def test_append_preserves_existing_rows_and_bounded_batch_layout(tmp_path, format_type):
    path = tmp_path / f"rows-{format_type}"
    first_error = _save(
        DataGenerator(PK_SPEC).size(3),
        path,
        format_type,
        maxRowsPerBatch=2,
    )
    second_error = _save(
        DataGenerator(PK_SPEC).size(2),
        path,
        format_type,
        mode="append",
        maxRowsPerBatch=1,
    )
    output = _single_output(path) if first_error is second_error is None else None

    if format_type == "csv" and output:
        text = output.read_text(encoding="utf-8")
        values, layout = pd.read_csv(output)["id"].tolist(), text.count('"id"')
    elif format_type == "json" and output:
        lines = output.read_text(encoding="utf-8").splitlines()
        values, layout = [json.loads(line)["id"] for line in lines], len(lines)
    elif output:
        parquet = pq.ParquetFile(output)
        values = pd.read_parquet(output)["id"].tolist()
        layout = [parquet.metadata.row_group(i).num_rows for i in range(parquet.metadata.num_row_groups)]
    else:
        values, layout = [], None

    expected_layout = {"csv": 1, "json": 5, "parquet": [2, 1, 1, 1]}[format_type]
    assert (first_error, second_error, values, layout) == (
        None,
        None,
        [0, 1, 2, 0, 1],
        expected_layout,
    )


def test_zero_row_partitions_are_typed_without_generation_pipeline_calls(tmp_path):
    path = tmp_path / "parts"
    calls = []

    def record_non_empty_batches(frame):
        calls.append(len(frame))
        return frame

    spec = {
        "value": {
            "method": "integers",
            "kwargs": {"min": 0, "max": 9, "int_type": "int8"},
        }
    }
    error = _save(
        DataGenerator(spec, seed=7).transformers([record_non_empty_batches]).size(2),
        path,
        "parquet",
        numFiles=4,
    )
    outputs = sorted(path.glob("part_*")) if error is None else []
    rows = sorted(pq.ParquetFile(output).metadata.num_rows for output in outputs)
    schemas = [pq.ParquetFile(output).schema_arrow for output in outputs]

    assert (
        error,
        calls,
        len(outputs),
        rows,
        [schema.field("value").type for schema in schemas],
    ) == (None, [1, 1], 4, [0, 0, 1, 1], [pa.int8()] * 4)


def test_indeterminate_empty_transform_fails_without_call_or_destination_mutation(tmp_path):
    path = tmp_path / "rows"
    assert _save(DataGenerator(PK_SPEC).size(1), path, "parquet") is None
    output = _single_output(path)
    before = output.read_bytes()
    calls = []

    def arbitrary_transform(frame):
        calls.append(len(frame))
        return frame.assign(value=frame["value"].map(object))

    spec = {"value": {"method": "constant", "kwargs": {"value": "x"}}}
    error = _save(
        DataGenerator(spec).transformers([arbitrary_transform]).size(0),
        path,
        "parquet",
        maxRowsPerBatch=2,
    )

    assert (
        type(error),
        calls,
        output.read_bytes() == before,
        "schema" in str(error).lower() or "indeterminate" in str(error).lower(),
    ) == (RandEngineError, [], True, True)


def test_schema_drift_fails_before_replacing_existing_destination(tmp_path):
    path = tmp_path / "rows"
    assert _save(DataGenerator(PK_SPEC).size(1), path, "parquet") is None
    output = _single_output(path)
    before = output.read_bytes()
    calls = []

    def drifting_transform(frame):
        calls.append(len(frame))
        value = frame["id"] if len(calls) == 1 else frame["id"].astype(str)
        return frame.assign(value=value)

    error = _save(
        DataGenerator(PK_SPEC).transformers([drifting_transform]).size(4),
        path,
        "parquet",
        maxRowsPerBatch=2,
    )

    assert (
        type(error),
        calls,
        output.read_bytes() == before,
        "schema" in str(error).lower(),
    ) == (RandEngineError, [2, 2], True, True)


@pytest.mark.parametrize("format_type", ["csv", "parquet"])
def test_unbatched_save_accepts_transformer_added_null_column(tmp_path, format_type):
    path = tmp_path / "rows"
    spec = {"a": {"method": "integers", "kwargs": {"min": 0, "max": 9}}}

    error = _save(
        DataGenerator(spec, seed=1)
        .size(3)
        .transformers([lambda df: df.assign(note=None)]),
        path,
        format_type,
    )
    output = _single_output(path) if error is None else None
    frame = (
        pd.read_csv(output) if format_type == "csv" else pd.read_parquet(output)
    ) if output else None

    assert (
        error,
        list(frame.columns) if frame is not None else None,
        frame["note"].isna().tolist() if frame is not None else None,
    ) == (None, ["a", "note"], [True, True, True])


def test_unbatched_json_save_keeps_transformer_added_null_column(tmp_path):
    path = tmp_path / "rows"
    spec = {"a": {"method": "constant", "kwargs": {"value": 1}}}

    error = _save(
        DataGenerator(spec).size(2).transformers([lambda df: df.assign(note=None)]),
        path,
        "json",
    )
    output = _single_output(path) if error is None else None

    assert (error, output.read_text(encoding="utf-8") if output else None) == (
        None,
        '{"a":1,"note":null}\n{"a":1,"note":null}\n',
    )


@pytest.mark.parametrize(
    "size, options, expected_calls",
    [
        (4, {"maxRowsPerBatch": 2}, [1, 2]),
        (4, {"numFiles": 2, "maxRowsPerBatch": 1}, [1, 2, 3]),
        (4, {}, [1, 2]),
        (0, {}, [1, 2]),
        (1, {"numFiles": 3}, [1, 2]),
    ],
    ids=["one-file-batched", "two-files-batch-1", "unbatched", "empty", "size-lt-files"],
)
def test_callable_spec_is_evaluated_once_per_final_file(
    tmp_path, size, options, expected_calls
):
    calls = []

    def counting_spec():
        calls.append(len(calls) + 1)
        return {"a": {"method": "integers", "kwargs": {"min": 0, "max": 9}}}

    error = _save(
        DataGenerator(counting_spec, seed=2).size(size),
        tmp_path / "rows",
        "parquet",
        **options,
    )

    assert (error, calls) == (None, expected_calls)



ALL_METHODS_SPEC = {
    "uuid": {"method": "uuid4", "kwargs": {}},
    "code": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "day": {"method": "dates", "kwargs": {"start": "2024-01-01", "end": "2024-12-31", "date_format": "%Y-%m-%d"}},
    "ip": {
        "method": "complex_distincts",
        "kwargs": {
            "pattern": "x.x.x.x",
            "replacement": "x",
            "templates": [
                {"method": "distincts", "kwargs": {"distincts": ["192", "172", "10"]}},
                {"method": "integers", "kwargs": {"min": 0, "max": 255}},
                {"method": "integers", "kwargs": {"min": 0, "max": 255}},
                {"method": "integers", "kwargs": {"min": 1, "max": 254}},
            ],
        },
    },
    "device_os": {
        "method": "distincts_map",
        "cols": ["device", "os"],
        "kwargs": {"distincts": {"mobile": ["android", "ios"], "desktop": ["windows", "macos", "linux"]}},
    },
    "trade_details": {
        "method": "distincts_map_prop",
        "cols": ["trade_type", "trade_side"],
        "kwargs": {"distincts": {"EQUITY": [("BUY", 6), ("SELL", 4)], "FX": [("BUY", 5), ("SELL", 5)]}},
    },
    "company_data": {
        "method": "distincts_multi_map",
        "cols": ["industry", "sub_industry", "company_size"],
        "kwargs": {"distincts": {"tech": [["software", "hardware"], ["small", "medium", "large"]]}},
    },
    "category": {"method": "distincts", "kwargs": {"distincts": ["A", "B", "C"]}},
    "tier": {"method": "distincts_prop", "kwargs": {"distincts": {"gold": 10, "silver": 30, "bronze": 60}}},
    "fixed": {"method": "constant", "kwargs": {"value": "fixed"}},
}
TEXT_COLUMNS = [
    "uuid", "code", "day", "ip", "device", "os", "trade_type", "trade_side",
    "industry", "sub_industry", "company_size", "category", "tier", "fixed",
]
# SHA-256 of the files written by the closed 0.8.0 release.
GUARD_SHA256 = {
    "csv": "322794c12b31ae617174e036a03892b3b31ad6a90feaa52f744a86d3e2c8fe06",
    "json": "968f1dafdd92cafafce7dd8e4572019c5e2ac594aed011c80cff531dd71ce2e9",
}


def _write_all_methods(tmp_path, format_type):
    generator = DataGenerator(ALL_METHODS_SPEC, seed=7).size(50)
    path = tmp_path / format_type
    assert _save(generator, path, format_type) is None
    return generator, _single_output(path)


@pytest.mark.parametrize("format_type", ["csv", "json"])
def test_all_methods_csv_json_bytes_equal_0_8_0(tmp_path, format_type):
    """The written bytes hash to the literals recorded from the 0.8.0 release."""
    _, output = _write_all_methods(tmp_path, format_type)

    assert hashlib.sha256(output.read_bytes()).hexdigest() == GUARD_SHA256[format_type]


def test_all_methods_parquet_values_and_string_type_unchanged_and_reads_back_arrow(tmp_path):
    """Values and the BYTE_ARRAY/String type match 0.8.0; Arrow read-back keeps the frame dtype."""
    _, output = _write_all_methods(tmp_path, "parquet")
    frame = DataGenerator(ALL_METHODS_SPEC, seed=7).size(50).get_df()

    schema = pq.ParquetFile(output).schema
    for column in TEXT_COLUMNS:
        parquet_column = schema.column(schema.names.index(column))
        assert parquet_column.physical_type == "BYTE_ARRAY"
        assert parquet_column.logical_type.type == "STRING"
    default = pd.read_parquet(output)
    assert default[TEXT_COLUMNS].values.tolist() == frame[TEXT_COLUMNS].values.tolist()

    arrow = pd.read_parquet(output, dtype_backend="pyarrow")
    for column in TEXT_COLUMNS:
        assert arrow[column].tolist() == frame[column].tolist()
        assert arrow[column].dtype == frame[column].dtype
