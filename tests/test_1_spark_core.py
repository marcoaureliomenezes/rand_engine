"""
Unit tests for SparkCore methods.

Tests the low-level Spark generation methods in rand_engine/core/_spark_core.py.
Each method is tested in isolation with direct Spark DataFrame manipulation.

Note: PySpark is a test-only dependency.
"""
import pytest
from rand_engine.core._spark_core import SparkCore


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
    
    def test_gen_ints_zfill(self, spark_session, spark_functions, small_spark_df):
        """Test zero-filled integer generation."""
        df = small_spark_df
        F = spark_functions
        
        result = SparkCore.gen_ints_zfill(spark_session, F, df, "test_col", length=8)
        
        data = result.select("test_col").collect()
        values = [row["test_col"] for row in data]
        
        # All should be strings of length 8
        assert all(isinstance(v, str) for v in values)
        assert all(len(v) == 8 for v in values)
        # All should start with zeros (at least some)
        assert any(v.startswith("0") for v in values)
    
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
        stddev = 15.0
        
        result = SparkCore.gen_floats_normal(
            spark_session, F, df, "test_col",
            mean=mean, stddev=stddev, decimals=2
        )
        
        # Calculate statistics
        stats = result.agg(
            F.mean("test_col").alias("mean"),
            F.stddev("test_col").alias("stddev")
        ).collect()[0]
        
        # Check that mean and stddev are close to expected (within 10% tolerance)
        assert abs(stats["mean"] - mean) < mean * 0.1
        assert abs(stats["stddev"] - stddev) < stddev * 0.2  # More tolerance for stddev


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
            formato="%Y-%m-%d"
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
            formato="%Y-%m-%d %H:%M:%S"
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
        df = spark_session.range(100000)
        F = spark_functions
        
        result = df
        result = SparkCore.gen_ints(spark_session, F, result, "col1", min=1, max=1000)
        result = SparkCore.gen_floats(spark_session, F, result, "col2", min=0.0, max=100.0, decimals=2)
        result = SparkCore.gen_distincts(spark_session, F, result, "col3", distincts=["A", "B", "C", "D", "E"])
        
        # Just count to trigger computation
        count = result.count()
        assert count == 100000
