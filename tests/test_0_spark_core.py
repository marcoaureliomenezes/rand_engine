"""
Unit tests for SparkCore methods.

Tests the low-level Spark generation methods in rand_engine/core/_spark_core.py.
Each method is tested in isolation with direct Spark DataFrame manipulation.

Note: PySpark is a test-only dependency.
"""
import re
import time
import pytest
from rand_engine.core._spark_core import SparkCore
from rand_engine.main.spark_generator import SparkGenerator



class _NoExecutionFrame:
    def withColumn(self, *_args, **_kwargs):
        raise AssertionError("Spark expression construction reached the frame")


class TestSparkCoreNumeric:
    """Test numeric generation methods."""
    
    def test_gen_ints_basic(self, spark_session, spark_functions, small_spark_df):
        """Test basic integer generation."""
        df = small_spark_df
        F = spark_functions
        
        result = SparkCore.gen_ints(spark_session, F, df, "test_col", min=10, max=20)
        
        # Collect data
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        # Assertions
        assert len(values) == 10
        assert all(isinstance(v, int) for v in values)
        assert all(10 <= v <= 20 for v in values)
    
    def test_gen_ints_default_params(self, spark_session, spark_functions, small_spark_df):
        """Test integer generation with default parameters."""
        df = small_spark_df
        F = spark_functions
        
        result = SparkCore.gen_ints(spark_session, F, df, "test_col")
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        assert all(0 <= v <= 10 for v in values)
    
    def test_gen_ints_negative_range(self, spark_session, spark_functions, small_spark_df):
        """Test integer generation with negative range."""
        df = small_spark_df
        F = spark_functions
        
        result = SparkCore.gen_ints(spark_session, F, df, "test_col", min=-50, max=-10)
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        assert all(-50 <= v <= -10 for v in values)
    
    @pytest.mark.parametrize("min, max", [(0, 1), (-1, 0)])
    def test_gen_ints_max_inclusive(self, spark_session, spark_functions, empty_spark_df, min, max):
        result = SparkCore.gen_ints(spark_session, spark_functions, empty_spark_df, "test_col", min=min, max=max)
        assert {row["test_col"] for row in result.select("test_col").collect()} == {min, max}

    @pytest.mark.parametrize("method, kwargs", [
        ("gen_ints", {"min": 1, "max": 0}),
        ("gen_floats", {"min": 1.01, "max": 1.0}),
        ("gen_unix_timestamps", {"start": "9999-12-31", "end": "9999-12-31"}),
        ("gen_dates", {"start": "1965-01-01", "end": "1960-01-01"}),
    ])
    def test_empty_range_raises_like_npcore(self, spark_session, spark_functions, empty_spark_df, method, kwargs):
        with pytest.raises(ValueError, match=r"must be <= max"):
            getattr(SparkCore, method)(spark_session, spark_functions, empty_spark_df, "c", **kwargs)

    @pytest.mark.parametrize("start, end, lo, hi", [
        ("1950-01-01", "1960-01-01", -631152000, -315619200),
        ("1969-12-31", "1970-01-02", -86400, 86400),
    ])
    def test_gen_unix_timestamps_and_dates_before_1970_stay_in_range(self, spark_session, spark_functions, small_spark_df, start, end, lo, hi):
        args = (spark_session, spark_functions, small_spark_df, "c")
        ts = [r["c"] for r in SparkCore.gen_unix_timestamps(*args, start=start, end=end).collect()]
        assert ts and all(lo <= t < hi for t in ts)
        dates = [r["c"] for r in SparkCore.gen_dates(*args, start=start, end=end).collect()]
        assert dates and all(start <= d < end for d in dates)

    def test_gen_unix_timestamps_end_exclusive(self, spark_session, spark_functions, empty_spark_df):
        result = SparkCore.gen_unix_timestamps(spark_session, spark_functions, empty_spark_df, "ts",
                                               start="2024-01-01 00:00:00", end="2024-01-01 00:00:01",
                                               date_format="%Y-%m-%d %H:%M:%S")
        assert len({row["ts"] for row in result.select("ts").collect()}) == 1
    
    @pytest.mark.skipif(not hasattr(time, "tzset"), reason="time.tzset is Unix-only")
    @pytest.mark.parametrize("tz", ["UTC", "America/New_York", "Asia/Tokyo"])
    @pytest.mark.parametrize("start, end, fmt, ts, rendered", [
        ("2024-07-01 00:00:00", "2024-07-01 00:00:01", "%Y-%m-%d %H:%M:%S", range(1719792000, 1719792001), "2024-07-01 00:00:00"),
        ("2024-03-10 02:30:00", "2024-03-10 02:30:01", "%Y-%m-%d %H:%M:%S", range(1710037800, 1710037801), "2024-03-10 02:30:00"),
        ("2024-03-10 05:00:00", "2024-03-10 05:00:01", "%Y-%m-%d %H:%M:%S", range(1710046800, 1710046801), "2024-03-10 05:00:00"),
        ("2024-07-01T00:00:00", "2024-07-01T00:00:01", "%Y-%m-%dT%H:%M:%S", range(1719792000, 1719792001), "2024-07-01T00:00:00"),
        ("01/07/2024 000000.000000", "01/07/2024 000001.000000", "%d/%m/%Y %H%M%S.%f", range(1719792000, 1719792001), "01/07/2024 000000.000000"),
        ("2100-06-01 00:00:00", "2100-06-01 00:00:01", "%Y-%m-%d %H:%M:%S", range(4115491200, 4115491201), "2100-06-01 00:00:00"),
        ("01/07/2024", "02/07/2024", "%d/%m/%Y", range(1719792000, 1719878400), "01/07/2024"),
    ])
    def test_gen_unix_timestamps_and_dates_ignore_timezone(self, spark_session, spark_functions, small_spark_df, tz, monkeypatch,
                                                         start, end, fmt, ts, rendered):
        session_tz = spark_session.conf.get("spark.sql.session.timeZone")
        monkeypatch.setenv("TZ", tz)
        time.tzset()
        spark_session.conf.set("spark.sql.session.timeZone", tz)
        try:
            args = (spark_session, spark_functions, small_spark_df, "c")
            kwargs = dict(start=start, end=end, date_format=fmt)
            assert {r["c"] for r in SparkCore.gen_unix_timestamps(*args, **kwargs).collect()} <= set(ts)
            assert {r["c"] for r in SparkCore.gen_dates(*args, **kwargs).collect()} == {rendered}
        finally:
            spark_session.conf.set("spark.sql.session.timeZone", session_tz)
            monkeypatch.undo()
            time.tzset()

    def test_gen_ints_zfill(self, spark_session, spark_functions, small_spark_df):
        """Test zero-filled integer generation."""
        df = small_spark_df
        F = spark_functions
        
        result = SparkCore.gen_ints_zfilled(spark_session, F, df, "test_col", length=8)
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        # All should be strings of length 8
        assert all(isinstance(v, str) for v in values)
        assert all(len(v) == 8 for v in values)
        # All should be numeric strings (can convert back to int)
        assert all(v.isdigit() for v in values)
        # All should be valid integers within range
        assert all(0 <= int(v) <= 99999999 for v in values)
    
    def test_gen_floats_basic(self, spark_session, spark_functions, small_spark_df):
        """Test basic float generation."""
        df = small_spark_df
        F = spark_functions
        
        result = SparkCore.gen_floats(spark_session, F, df, "test_col", min=0.0, max=100.0, decimals=2)
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        assert len(values) == 10
        assert all(isinstance(v, float) for v in values)
        assert all(0.0 <= v <= 100.0 for v in values)
    
    def test_gen_floats_decimals(self, spark_session, spark_functions, empty_spark_df):
        """Test float generation respects decimal places."""
        df = empty_spark_df
        F = spark_functions
        
        result = SparkCore.gen_floats(spark_session, F, df, "test_col", min=0.0, max=10.0, decimals=3)
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        # Check that values respect decimal precision
        for v in values:
            # Convert to string and check decimal places
            str_v = str(v)
            if "." in str_v:
                decimal_part = str_v.split(".")[1]
                assert len(decimal_part) <= 3
    
    def test_gen_floats_normal_distribution(self, spark_session, spark_functions, large_spark_df):
        """Test normal distribution float generation."""
        df = large_spark_df
        F = spark_functions
        
        mean = 100.0
        std = 15.0
        
        result = SparkCore.gen_floats_normal(
            spark_session, F, df, "test_col",
            mean=mean, std=std, decimals=2
        )
        
        # Calculate statistics
        stats = result.agg(
            F.mean("test_col").alias("mean"),
            F.std("test_col").alias("std")
        ).collect()[0]
        
        # Check that mean and std are close to expected (within 10% tolerance)
        assert abs(stats["mean"] - mean) < mean * 0.1
        assert abs(stats["std"] - std) < std * 0.2  # More tolerance for std

    def test_supported_integer_domains_keep_exact_singleton_bounds(
        self, spark_session, spark_functions,
    ):
        cases = [
            ("int8", -128),
            ("int8", 127),
            ("int16", -32768),
            ("int16", 32767),
            ("int32", -2147483648),
            ("int32", 2147483647),
            ("uint8", 0),
            ("uint8", 255),
            ("uint16", 65535),
            ("uint32", 4294967295),
            ("int64", -9223372036854775808),
            ("int64", 9007199254740993),
            ("int64", 9223372036854775807),
        ]
        actual = []
        for int_type, bound in cases:
            result = SparkCore.gen_ints(
                spark_session,
                spark_functions,
                spark_session.range(1),
                "value",
                min=bound,
                max=bound,
                int_type=int_type,
            )
            actual.append((int_type, result.select("value").first()["value"]))

        assert actual == cases

    @pytest.mark.parametrize(("int_type", "minimum", "maximum"), [
        ("uint64", 0, 1),
        (True, 0, 1),
        ("int8", -129, 0),
        ("int8", 0, 128),
        ("uint8", -1, 0),
        ("uint16", 0, 65536),
        ("uint32", 0, 4294967296),
        ("int64", -9223372036854775809, 0),
        ("int64", 0, 9223372036854775808),
    ])
    def test_unsupported_integer_domains_are_refused_before_frame_execution(
        self, spark_session, spark_functions, int_type, minimum, maximum,
    ):
        try:
            SparkCore.gen_ints(
                spark_session,
                spark_functions,
                _NoExecutionFrame(),
                "value",
                min=minimum,
                max=maximum,
                int_type=int_type,
            )
        except Exception as error:
            actual = type(error)
        else:
            actual = None

        assert actual is ValueError

    def test_float_decimal_lattice_and_empty_domains(
        self, spark_session, spark_functions,
    ):
        try:
            SparkCore.gen_floats(
                spark_session,
                spark_functions,
                spark_session.range(1),
                "value",
                min=9.991,
                max=9.991,
                decimals=2,
            )
        except Exception as error:
            empty_domain_result = type(error)
        else:
            empty_domain_result = None

        assert empty_domain_result is ValueError

        cases = [
            (9.991, 10.009, 2, 10.0),
            (-10.009, -9.991, 2, -10.0),
            (11, 29, -1, 20.0),
        ]
        for minimum, maximum, decimals, expected in cases:
            result = SparkCore.gen_floats(
                spark_session,
                spark_functions,
                spark_session.range(10**4),
                "value",
                min=minimum,
                max=maximum,
                decimals=decimals,
            )
            assert {row["value"] for row in result.select("value").collect()} == {expected}

    @pytest.mark.parametrize(("minimum", "maximum", "decimals"), [
        (float("nan"), 1.0, 2),
        (0.0, float("inf"), 2),
        (0.0, 1.0, True),
        (9.991, 9.991, 2),
    ])
    def test_invalid_float_lattices_fail_before_frame_execution(
        self, spark_session, spark_functions, minimum, maximum, decimals,
    ):
        try:
            SparkCore.gen_floats(
                spark_session,
                spark_functions,
                _NoExecutionFrame(),
                "value",
                min=minimum,
                max=maximum,
                decimals=decimals,
            )
        except Exception as error:
            actual = type(error)
        else:
            actual = None

        assert actual is ValueError

    def test_generator_keeps_bigint_literal_and_uses_no_python_udf(
        self, spark_session, spark_functions,
    ):
        generator = SparkGenerator(
            spark_session,
            spark_functions,
            {
                "value": {
                    "method": "integers",
                    "kwargs": {
                        "min": 9007199254740993,
                        "max": 9007199254740993,
                        "int_type": "int64",
                    },
                }
            },
        )
        result = generator.size(3).get_df()
        values = [row["value"] for row in result.collect()]
        executed_plan = result._jdf.queryExecution().executedPlan().toString().lower()
        assert values == [9007199254740993, 9007199254740993, 9007199254740993]
        assert "pythonudf" not in executed_plan
        assert "batchevalpython" not in executed_plan

    @pytest.mark.parametrize(("minimum", "maximum"), [
        (0, 2**53),
        (-2**63, 2**63 - 1),
        (-2**53, 2**53),
    ])
    def test_integer_width_above_2_pow_53_is_refused_before_frame_execution(
        self, spark_session, spark_functions, minimum, maximum,
    ):
        with pytest.raises(ValueError):
            SparkCore.gen_ints(
                spark_session, spark_functions, _NoExecutionFrame(),
                "value", min=minimum, max=maximum, int_type="int64",
            )

    @pytest.mark.parametrize(("minimum", "maximum"), [
        (0, 2**53 - 1),
        (-2**53, -1),
    ])
    def test_integer_width_exactly_2_pow_53_is_generated_within_bounds(
        self, spark_session, spark_functions, minimum, maximum,
    ):
        result = SparkCore.gen_ints(
            spark_session, spark_functions, spark_session.range(100),
            "value", min=minimum, max=maximum, int_type="int64",
        )
        values = [row["value"] for row in result.collect()]
        assert len(values) == 100
        assert all(minimum <= value <= maximum for value in values)

    @pytest.mark.parametrize(("minimum", "maximum", "decimals"), [
        (1e19, 1e19, 0),
        (1e6, 1e6 + 1, 13),
        (-1e19, -1e19 + 1e5, 0),
        (0, 10**20, 0),
        (-10**19, 10**19, 0),
    ])
    def test_float_fine_grid_or_int64_overflow_endpoint_draws_within_bounds(
        self, spark_session, spark_functions, minimum, maximum, decimals,
    ):
        result = SparkCore.gen_floats(
            spark_session, spark_functions, spark_session.range(100),
            "value", min=minimum, max=maximum, decimals=decimals,
        )
        values = [row["value"] for row in result.collect()]
        assert result.schema["value"].dataType.simpleString() == "double"
        assert len(values) == 100
        assert all(minimum <= value <= maximum for value in values)

    @pytest.mark.parametrize(("mean", "std", "decimals"), [
        (10**20, 1, 0),
        (0, 10**20, 0),
    ])
    def test_floats_normal_int_kwargs_beyond_int64_generate_finite_doubles(
        self, spark_session, spark_functions, mean, std, decimals,
    ):
        import math
        result = SparkCore.gen_floats_normal(
            spark_session, spark_functions, spark_session.range(100),
            "value", mean=mean, std=std, decimals=decimals,
        )
        values = [row["value"] for row in result.collect()]
        assert result.schema["value"].dataType.simpleString() == "double"
        assert len(values) == 100
        assert all(math.isfinite(value) for value in values)

    def test_float_lattice_width_exactly_2_pow_53_is_generated_within_bounds(
        self, spark_session, spark_functions,
    ):
        result = SparkCore.gen_floats(
            spark_session, spark_functions, spark_session.range(100),
            "value", min=0.0, max=9007199254740991.0, decimals=0,
        )
        values = [row["value"] for row in result.collect()]
        assert len(values) == 100
        assert all(0.0 <= value <= 9007199254740991.0 and value.is_integer() for value in values)

    def test_narrow_float_grid_on_an_empty_frame_keeps_double_type(
        self, spark_session, spark_functions,
    ):
        result = SparkCore.gen_floats(
            spark_session, spark_functions, spark_session.range(0),
            "value", min=0.0, max=10.0, decimals=2,
        )
        assert result.collect() == []
        assert result.schema["value"].dataType.simpleString() == "double"

    def test_float_lattice_plan_has_one_rand_seed_and_no_folding_expressions(
        self, spark_session, spark_functions,
    ):
        result = SparkCore.gen_floats(
            spark_session, spark_functions, spark_session.range(5),
            "value", min=0.0, max=10.0, decimals=2,
        )
        executed_plan = result._jdf.queryExecution().executedPlan().toString().lower()
        assert len(re.findall(r"rand\(", executed_plan)) == 1
        for word in ("aggregate", "getbit", "transform"):
            assert word not in executed_plan


class TestSparkCoreIdentifiers:
    """Test identifier generation methods."""
    
    def test_gen_uuid4(self, spark_session, spark_functions, small_spark_df):
        """Test UUID4 generation."""
        df = small_spark_df
        F = spark_functions
        
        result = SparkCore.gen_uuid4(spark_session, F, df, "test_col")
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        # All should be strings
        assert all(isinstance(v, str) for v in values)
        # All should be unique
        assert len(values) == len(set(values))
        # All should have UUID format (36 chars with dashes)
        assert all(len(v) == 36 for v in values)
        assert all(v.count("-") == 4 for v in values)


class TestSparkCoreSelection:
    """Test selection/choice generation methods."""
    
    def test_gen_distincts_basic(self, spark_session, spark_functions, empty_spark_df):
        """Test basic distinct value generation."""
        df = empty_spark_df
        F = spark_functions
        
        distincts = ["A", "B", "C"]
        result = SparkCore.gen_distincts(spark_session, F, df, "test_col", distincts=distincts)
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        # All values should be from distincts list
        assert all(v in distincts for v in values)
        # Should have variety (not all the same)
        assert len(set(values)) > 1
    
    def test_gen_distincts_single_value(self, spark_session, spark_functions, small_spark_df):
        """Test distinct generation with single value."""
        df = small_spark_df
        F = spark_functions
        
        distincts = ["OnlyOne"]
        result = SparkCore.gen_distincts(spark_session, F, df, "test_col", distincts=distincts)
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        assert all(v == "OnlyOne" for v in values)
    
    def test_gen_distincts_prop_basic(self, spark_session, spark_functions, empty_spark_df):
        """Test proportional distinct value generation."""
        df = empty_spark_df
        F = spark_functions
        
        distincts_prop = {"A": 70, "B": 20, "C": 10}
        result = SparkCore.gen_distincts_prop(spark_session, F, df, "test_col", distincts=distincts_prop)
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        # All values should be from distincts keys
        assert all(v in distincts_prop.keys() for v in values)
        # Should have variety
        assert len(set(values)) > 1
    
    def test_gen_booleans_default(self, spark_session, spark_functions, large_spark_df):
        """Test boolean generation with default probability."""
        df = large_spark_df
        F = spark_functions
        
        result = SparkCore.gen_booleans(spark_session, F, df, "test_col", true_prob=0.5)
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        # Count True values
        true_count = sum(values)
        true_ratio = true_count / len(values)
        
        # Should be approximately 50% (within 10% tolerance)
        assert 0.4 < true_ratio < 0.6
    
    def test_gen_booleans_high_probability(self, spark_session, spark_functions, large_spark_df):
        """Test boolean generation with high true probability."""
        df = large_spark_df
        F = spark_functions
        
        result = SparkCore.gen_booleans(spark_session, F, df, "test_col", true_prob=0.9)
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        true_count = sum(values)
        true_ratio = true_count / len(values)
        
        # Should be approximately 90% (within 10% tolerance)
        assert 0.8 < true_ratio < 1.0


class TestSparkCoreTemporal:
    """Test temporal/date generation methods."""
    
    def test_gen_dates_basic(self, spark_session, spark_functions, small_spark_df):
        """Test basic date generation."""
        df = small_spark_df
        F = spark_functions
        
        result = SparkCore.gen_dates(
            spark_session, F, df, "test_col",
            start="2020-01-01",
            end="2023-12-31",
            date_format="%Y-%m-%d"
        )
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        # All should be strings
        assert all(isinstance(v, str) for v in values)
        # All should have correct format (YYYY-MM-DD)
        assert all(len(v) == 10 for v in values)
        assert all(v[4] == "-" and v[7] == "-" for v in values)
    
    def test_gen_dates_custom_format(self, spark_session, spark_functions, small_spark_df):
        """Test date generation with custom format."""
        df = small_spark_df
        F = spark_functions
        
        result = SparkCore.gen_dates(
            spark_session, F, df, "test_col",
            start="2020-01-01 00:00:00",
            end="2020-01-31 23:59:59",
            date_format="%Y-%m-%d %H:%M:%S"
        )
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        # All should match datetime format
        assert all(isinstance(v, str) for v in values)
        assert all(len(v) == 19 for v in values)  # YYYY-MM-DD HH:MM:SS


class TestSparkCoreChaining:
    """Test chaining multiple generation methods."""
    
    def test_multiple_columns(self, spark_session, spark_functions, empty_spark_df):
        """Test generating multiple columns in sequence."""
        df = empty_spark_df
        F = spark_functions
        
        result = df
        result = SparkCore.gen_ints(spark_session, F, result, "col1", min=1, max=10)
        result = SparkCore.gen_floats(spark_session, F, result, "col2", min=0.0, max=1.0, decimals=2)
        result = SparkCore.gen_distincts(spark_session, F, result, "col3", distincts=["X", "Y", "Z"])
        result = SparkCore.gen_booleans(spark_session, F, result, "col4", true_prob=0.5)
        
        # Check all columns exist
        columns = result.columns
        assert "col1" in columns
        assert "col2" in columns
        assert "col3" in columns
        assert "col4" in columns
        
        # Check data types
        data = result.limit(1).collect()[0]
        assert isinstance(data["col1"], int)
        assert isinstance(data["col2"], float)
        assert isinstance(data["col3"], str)
        assert isinstance(data["col4"], bool)


class TestSparkCoreEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_gen_ints_equal_min_max(self, spark_session, spark_functions, small_spark_df):
        """Test integer generation when min equals max."""
        df = small_spark_df
        F = spark_functions
        
        result = SparkCore.gen_ints(spark_session, F, df, "test_col", min=42, max=42)
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        # All should be 42
        assert all(v == 42 for v in values)
    
    def test_gen_floats_zero_range(self, spark_session, spark_functions, small_spark_df):
        """Test float generation with zero range."""
        df = small_spark_df
        F = spark_functions
        
        result = SparkCore.gen_floats(spark_session, F, df, "test_col", min=10.5, max=10.5, decimals=1)
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        # All should be 10.5
        assert all(abs(v - 10.5) < 0.01 for v in values)
    
    def test_gen_distincts_empty_list(self, spark_session, spark_functions, small_spark_df):
        """Test distinct generation with empty list."""
        df = small_spark_df
        F = spark_functions
        
        # Should handle empty list gracefully (returns None or raises error)
        with pytest.raises((IndexError, Exception)):
            result = SparkCore.gen_distincts(spark_session, F, df, "test_col", distincts=[])
    
    def test_large_dataset_performance(self, spark_session, spark_functions):
        """Test generation performance with large dataset."""
        df = spark_session.range(10**4)
        F = spark_functions
        
        result = df
        result = SparkCore.gen_ints(spark_session, F, result, "col1", min=1, max=1000)
        result = SparkCore.gen_floats(spark_session, F, result, "col2", min=0.0, max=100.0, decimals=2)
        result = SparkCore.gen_distincts(spark_session, F, result, "col3", distincts=["A", "B", "C", "D", "E"])
        
        # Just count to trigger computation
        count = result.count()
        assert count == 10**4
