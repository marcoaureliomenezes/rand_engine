"""
Integration tests for SparkGenerator.

Tests the high-level SparkGenerator class in rand_engine/main/spark_generator.py.
These tests validate end-to-end workflow: metadata → DataFrame generation.

Note: PySpark is a test-only dependency.
"""
import pytest
from rand_engine import DataGenerator
from rand_engine.main.spark_generator import SparkGenerator
from rand_engine.validators.advanced_validator import AdvancedValidator
from rand_engine.validators.exceptions import RandEngineError, SpecValidationError


class TestSparkGeneratorBasic:
    """Test basic SparkGenerator functionality."""
    
    def test_initialization(self, spark_session, spark_functions, spark_metadata_simple):
        """Test SparkGenerator initialization."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_simple)
        
        assert generator.spark == spark_session
        assert generator.F == spark_functions
        assert generator.metadata == spark_metadata_simple
    
    def test_map_methods(self, spark_session, spark_functions, spark_metadata_simple):
        """Test that map_methods returns correct method mapping."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_simple)
        
        methods = generator.map_methods()
        
        # Check all expected methods exist
        assert "integers" in methods
        assert "int_zfilled" in methods
        assert "floats" in methods
        assert "floats_normal" in methods
        assert "distincts" in methods
        assert "booleans" in methods
        assert "dates" in methods
        assert "uuid4" in methods
    
    def test_size_method(self, spark_session, spark_functions, spark_metadata_simple):
        """Test size() method sets _size attribute."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_simple)
        
        result = generator.size(100)
        
        assert result == generator  # Should return self for chaining
        assert generator._size == 100
    
    def test_get_df_without_size_names_size(self, spark_session, spark_functions, spark_metadata_simple):
        """get_df() without .size(n) raises RandEngineError naming .size(n)."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_simple)

        with pytest.raises(RandEngineError, match=r"\.size\(n\)"):
            generator.get_df()

    def test_get_df_simple(self, spark_session, spark_functions, spark_metadata_simple):
        """Test get_df() with simple metadata."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_simple)
        
        df = generator.size(50).get_df()
        
        # Check row count
        assert df.count() == 50
        
        # Check columns exist
        columns = df.columns
        assert "id" in columns  # From spark.range()
        assert "name" in columns
        assert "score" in columns
        
        # Check data types
        sample = df.limit(1).collect()[0]
        assert isinstance(sample["id"], int)
        assert isinstance(sample["name"], str)
        assert isinstance(sample["score"], float)


class TestSparkGeneratorComplex:
    """Test SparkGenerator with complex metadata."""
    
    def test_get_df_complex(self, spark_session, spark_functions, spark_metadata_complex):
        """Test get_df() with complex metadata covering all types."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_complex)
        
        df = generator.size(100).get_df()
        
        # Check row count
        assert df.count() == 100
        
        # Check all expected columns (id is technical and removed if not in metadata)
        columns = df.columns
        assert "user_id" in columns
        assert "age" in columns
        assert "height_cm" in columns
        assert "is_active" in columns
        assert "category" in columns
        assert "registration_date" in columns
        assert "code" in columns
    
    def test_data_types_complex(self, spark_session, spark_functions, spark_metadata_complex):
        """Test that generated data has correct types."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_complex)
        
        df = generator.size(10).get_df()
        sample = df.limit(1).collect()[0]
        
        # Validate types
        assert isinstance(sample["user_id"], str)  # UUID
        assert isinstance(sample["age"], int)
        assert isinstance(sample["height_cm"], float)
        assert isinstance(sample["is_active"], bool)
        assert isinstance(sample["category"], str)
        assert isinstance(sample["registration_date"], str)
        assert isinstance(sample["code"], str)
    
    def test_data_ranges_complex(self, spark_session, spark_functions, spark_metadata_complex):
        """Test that generated data respects specified ranges."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_complex)
        
        df = generator.size(100).get_df()
        data = df.collect()
        
        # Check age range
        ages = [row["age"] for row in data]
        assert all(18 <= age <= 80 for age in ages)
        
        # Check category values
        categories = [row["category"] for row in data]
        assert all(cat in ["A", "B", "C", "D", "E"] for cat in categories)
        
        # Check code length (zint)
        codes = [row["code"] for row in data]
        assert all(len(code) == 8 for code in codes)


class TestSparkGeneratorAllTypes:
    """Test SparkGenerator with all supported generation types."""
    
    def test_all_generation_methods(self, spark_session, spark_functions, spark_metadata_all_types):
        """Test that all generation methods work together."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_all_types)
        
        df = generator.size(50).get_df()
        
        # Should generate successfully
        assert df.count() == 50
        
        # Check all columns exist
        columns = df.columns
        assert "int_col" in columns
        assert "float_col" in columns
        assert "normal_col" in columns
        assert "uuid_col" in columns
        assert "zint_col" in columns
        assert "distinct_col" in columns
        assert "bool_col" in columns
        assert "date_col" in columns
    
    def test_all_types_data_validity(self, spark_session, spark_functions, spark_metadata_all_types):
        """Test that all generated data is valid."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_all_types)
        
        df = generator.size(20).get_df()
        data = df.collect()
        
        for row in data:
            # Numeric
            assert isinstance(row["int_col"], int)
            assert 0 <= row["int_col"] <= 1000
            assert isinstance(row["float_col"], float)
            assert 0.0 <= row["float_col"] <= 100.0
            
            # Identifiers
            assert isinstance(row["uuid_col"], str)
            assert len(row["uuid_col"]) == 36
            assert isinstance(row["zint_col"], str)
            assert len(row["zint_col"]) == 10
            
            # Selection
            assert row["distinct_col"] in ["Option1", "Option2", "Option3"]
            assert isinstance(row["bool_col"], bool)
            
            # Temporal
            assert isinstance(row["date_col"], str)


class TestSparkGeneratorDifferentSizes:
    """Test SparkGenerator with different dataset sizes."""
    
    @pytest.mark.parametrize("size", [1, 10, 100, 1000])
    def test_different_sizes(self, spark_session, spark_functions, spark_metadata_simple, size):
        """Test generation with various sizes."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_simple)
        
        df = generator.size(size).get_df()
        
        assert df.count() == size
    
    def test_large_dataset(self, spark_session, spark_functions, spark_metadata_simple):
        """Test generation with large dataset."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_simple)
        
        df = generator.size(1000).get_df()
        
        assert df.count() == 1000
        
        # Verify data distribution
        name_counts = df.groupBy("name").count().collect()
        assert len(name_counts) > 1  # Should have variety


class TestSparkGeneratorChaining:
    """Test method chaining in SparkGenerator."""
    
    def test_fluent_api(self, spark_session, spark_functions, spark_metadata_simple):
        """Test fluent API with method chaining."""
        df = (
            SparkGenerator(spark_session, spark_functions, spark_metadata_simple)
            .size(25)
            .get_df()
        )
        
        assert df.count() == 25
    
    def test_multiple_generations(self, spark_session, spark_functions, spark_metadata_simple):
        """Test that generator can be reused for multiple generations."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_simple)
        
        df1 = generator.size(50).get_df()
        df2 = generator.size(100).get_df()
        
        assert df1.count() == 50
        assert df2.count() == 100


class TestSparkGeneratorStatistics:
    """Test statistical properties of generated data."""
    
    def test_normal_distribution_statistics(self, spark_session, spark_functions):
        """Test that floats_normal generates proper normal distribution."""
        metadata = {
            "value": {
                "method": "floats_normal",
                "kwargs": {"mean": 100.0, "std": 15.0, "decimals": 2}
            }
        }
        
        generator = SparkGenerator(spark_session, spark_functions, metadata)
        df = generator.size(10000).get_df()
        
        # Calculate statistics
        from pyspark.sql import functions as F
        stats = df.agg(
            F.mean("value").alias("mean"),
            F.std("value").alias("std")
        ).collect()[0]
        
        # Check within tolerance (10% for mean, 20% for std)
        assert abs(stats["mean"] - 100.0) < 10.0
        assert abs(stats["std"] - 15.0) < 5.0
    
    def test_boolean_probability(self, spark_session, spark_functions):
        """Test that boolean generation respects probability."""
        metadata = {
            "flag": {
                "method": "booleans",
                "kwargs": {"true_prob": 0.7}
            }
        }
        
        generator = SparkGenerator(spark_session, spark_functions, metadata)
        df = generator.size(10000).get_df()
        
        # Calculate true ratio
        from pyspark.sql import functions as F
        true_count = df.filter(F.col("flag") == True).count()
        true_ratio = true_count / 10000
        
        # Should be approximately 70% (within 5% tolerance)
        assert 0.65 < true_ratio < 0.75
    
    def test_distinct_distribution(self, spark_session, spark_functions):
        """Test that distincts are evenly distributed."""
        metadata = {
            "category": {
                "method": "distincts",
                "kwargs": {"distincts": ["A", "B", "C", "D", "E"]}
            }
        }
        
        generator = SparkGenerator(spark_session, spark_functions, metadata)
        df = generator.size(10000).get_df()
        
        # Count each category
        counts = df.groupBy("category").count().collect()
        
        # Should have all 5 categories
        assert len(counts) == 5
        
        # Each category should have roughly 20% (within 5% tolerance)
        for row in counts:
            ratio = row["count"] / 10000
            assert 0.15 < ratio < 0.25


class TestSparkGeneratorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_metadata(self, spark_session, spark_functions):
        """Test with empty metadata should raise SpecValidationError."""
        from rand_engine.validators.exceptions import SpecValidationError
        
        # Empty metadata should fail validation
        with pytest.raises(SpecValidationError) as exc_info:
            SparkGenerator(spark_session, spark_functions, {})
        
        assert "cannot be empty" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()
    
    def test_single_column_metadata(self, spark_session, spark_functions):
        """Test with single column metadata."""
        metadata = {
            "value": {
                "method": "integers",
                "kwargs": {"min": 1, "max": 100}
            }
        }
        
        generator = SparkGenerator(spark_session, spark_functions, metadata)
        df = generator.size(20).get_df()
        
        # Technical 'id' column is removed when not in metadata
        assert "value" in df.columns
        assert df.count() == 20
        assert len(df.columns) == 1  # Only 'value' column
    
    def test_zero_size(self, spark_session, spark_functions, spark_metadata_simple):
        """Test generation with size 0."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_simple)
        
        df = generator.size(0).get_df()
        
        assert df.count() == 0
    
    def test_invalid_method_name(self, spark_session, spark_functions):
        """Test with invalid method name should raise SpecValidationError during init."""
        from rand_engine.validators.exceptions import SpecValidationError
        
        metadata = {
            "value": {
                "method": "invalid_method",
                "kwargs": {}
            }
        }
        
        # Validation catches invalid method during initialization
        with pytest.raises(SpecValidationError) as exc_info:
            generator = SparkGenerator(spark_session, spark_functions, metadata)
        
        assert "method" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


class TestSparkGeneratorDataQuality:
    """Test data quality aspects."""
    
    def test_no_nulls_generated(self, spark_session, spark_functions, spark_metadata_all_types):
        """Test that no null values are generated."""
        generator = SparkGenerator(spark_session, spark_functions, spark_metadata_all_types)
        
        df = generator.size(50).get_df()
        
        # Check for nulls in each column
        from pyspark.sql import functions as F
        for col in df.columns:
            null_count = df.filter(F.col(col).isNull()).count()
            assert null_count == 0, f"Column {col} has {null_count} nulls"
    
    def test_uuid_uniqueness(self, spark_session, spark_functions):
        """Test that UUIDs are unique."""
        metadata = {
            "uuid": {
                "method": "uuid4",
                "kwargs": {}
            }
        }
        
        generator = SparkGenerator(spark_session, spark_functions, metadata)
        df = generator.size(1000).get_df()
        
        # Count distinct UUIDs
        distinct_count = df.select("uuid").distinct().count()
        
        # All should be unique
        assert distinct_count == 1000
    
    def test_int_zfilled_format_consistency(self, spark_session, spark_functions):
        """Test that int_zfilled maintains consistent format."""
        metadata = {
            "code": {
                "method": "int_zfilled",
                "kwargs": {"length": 6}
            }
        }
        
        generator = SparkGenerator(spark_session, spark_functions, metadata)
        df = generator.size(100).get_df()
        
        codes = df.select("code").collect()
        
        # All should be 6 characters
        for row in codes:
            assert len(row["code"]) == 6
            # All should be numeric strings
            assert row["code"].isdigit()


class TestSparkIntegerWidthRefusedAtConstruction:
    def test_max_2_53_raises_collected_spec_error(self, spark_session, spark_functions):
        from rand_engine.validators.exceptions import SpecValidationError

        metadata = {"value": {"method": "integers", "kwargs": {"min": 0, "max": 2**53}}}
        with pytest.raises(SpecValidationError) as exc_info:
            SparkGenerator(spark_session, spark_functions, metadata)
        assert "'value'" in str(exc_info.value)
        assert "2**53" in str(exc_info.value)


class TestSparkIntegerWidthExactly2Pow53:
    def test_values_stay_within_bounds(self, spark_session, spark_functions):
        metadata = {"value": {"method": "integers", "kwargs": {"min": 0, "max": 2**53 - 1}}}
        df = SparkGenerator(spark_session, spark_functions, metadata).size(200).get_df()
        values = [row["value"] for row in df.collect()]
        assert (len(values), min(values) >= 0, max(values) <= 2**53 - 1) == (200, True, True)


def _key_parity_spec():
    return {
        "id": {"method": "pk", "kwargs": {"style": "sequence", "start": 41, "step": 3}},
        "kind": {"method": "distincts", "kwargs": {"distincts": ["account"]}},
        "__rand_engine_source_index": {
            "method": "pk",
            "kwargs": {"style": "sequence", "start": -20, "step": 2},
        },
        "permuted_id": {
            "method": "pk",
            "kwargs": {"style": "permuted", "domain": 64, "start": 1000, "key": 9},
        },
        "formatted_id": {
            "method": "pk",
            "kwargs": {"style": "sequence", "start": 12, "step": 2, "format": "ORD-{:04d}"},
        },
        "uniform_parent": {
            "method": "fk",
            "kwargs": {
                "parent": {"method": "pk", "kwargs": {"style": "sequence", "start": 700, "step": 5}},
                "parent_size": 9,
            },
        },
        "skewed_parent": {
            "method": "fk",
            "kwargs": {
                "parent": {
                    "method": "pk",
                    "kwargs": {"style": "permuted", "domain": 9, "start": 900, "key": 2, "format": "P-{:04d}"},
                },
                "parent_size": 9,
                "skew": 1.2,
            },
        },
        "eligible_parent": {
            "method": "fk",
            "kwargs": {
                "parent": {"method": "pk", "kwargs": {"style": "sequence", "start": 4, "step": 2}},
                "parent_size": 9,
                "born_before": {
                    "parent_start": 0,
                    "parent_rate": 1,
                    "child_start": 0,
                    "child_rate": 2,
                },
            },
        },
    }


@pytest.mark.parametrize("partitions", [2, 3])
def test_spark_key_vectors_match_pandas_across_noncontiguous_partition_batches(
    spark_session, spark_functions, monkeypatch, partitions
):
    """Keys use source indexes rather than a partition-local Arrow batch offset."""
    spec = _key_parity_spec()
    expected = DataGenerator(spec, seed=123).size(12).get_df().to_dict("records")
    range_ = spark_session.range

    def repartitioned_range(size):
        return range_(size).repartition(
            partitions,
            spark_functions.pmod(spark_functions.col("id"), spark_functions.lit(partitions)),
        )

    monkeypatch.setattr(spark_session, "range", repartitioned_range)
    dataframe = SparkGenerator(spark_session, spark_functions, spec, seed=123).size(12).get_df()

    assert dataframe.columns == list(spec)
    assert "__rand_engine_source_index" in dataframe.columns
    assert dataframe.orderBy("id").toPandas().to_dict("records") == expected


@pytest.mark.parametrize(
    ("ordinary_column", "ordinary_messages"),
    [
        (None, ()),
        (
            {"method": "integers", "kwargs": {"min": 1}},
            ("method 'integers' requires parameter 'max'",),
        ),
    ],
)
def test_spark_key_validation_reuses_the_pandas_key_semantics(
    spark_session, spark_functions, ordinary_column, ordinary_messages
):
    """Malformed key and ordinary columns report every issue before Spark runs."""
    spec = {
        "parent_id": {
            "method": "fk",
            "kwargs": {
                "parent": {"method": "pk", "kwargs": {"style": "not-a-style"}},
                "parent_size": 0,
                "born_before": {
                    "parent_start": 0,
                    "parent_rate": 1,
                    "child_start": 0,
                    "child_rate": False,
                },
            },
        },
    }
    if ordinary_column is not None:
        spec["age"] = ordinary_column
    pandas_errors = AdvancedValidator.validate(spec)

    assert pandas_errors
    with pytest.raises(SpecValidationError) as exc_info:
        SparkGenerator(spark_session, spark_functions, spec, seed=123)

    error_text = str(exc_info.value)
    assert "SPARKGENERATOR SPEC VALIDATION ERROR" in error_text
    for message in (
        "pk 'style' is unknown",
        "'parent_size' must be an integer >= 1",
        "born_before.child_rate",
        *ordinary_messages,
    ):
        assert message in error_text
        assert any(message in error for error in pandas_errors)


def test_spark_key_validation_keeps_the_existing_top_level_shape_error(spark_session, spark_functions):
    """Selecting key columns never bypasses full Spark RandSpec intake validation."""
    with pytest.raises(SpecValidationError, match="Spec must be a dictionary"):
        SparkGenerator(spark_session, spark_functions, ["not", "a", "RandSpec"], seed=123)


@pytest.mark.parametrize(
    ("column", "problem"),
    [
        ({"method": "pk", "args": [1], "kwargs": {}}, "args"),
        ({"method": "pk", "kwargs": {}, "null_rate": 0.25}, "null_rate"),
    ],
)
def test_spark_key_validation_reports_each_generic_key_problem_once(
    spark_session, spark_functions, column, problem
):
    """A generic key error has one column diagnostic from Spark validation."""
    with pytest.raises(SpecValidationError) as exc_info:
        SparkGenerator(spark_session, spark_functions, {"account_id": column}, seed=123)

    error_text = str(exc_info.value)
    assert error_text.count("❌ Column 'account_id'") == 1
    assert problem in error_text


def test_spark_key_zero_size_keeps_the_requested_schema(spark_session, spark_functions):
    """A zero-row key frame is valid and does not expose an implementation index."""
    spec = {"account_id": {"method": "pk", "kwargs": {"start": 9, "step": 4}}}

    dataframe = SparkGenerator(spark_session, spark_functions, spec, seed=123).size(0).get_df()

    assert dataframe.columns == ["account_id"]
    assert dataframe.count() == 0


def test_spark_zero_eligible_foreign_key_raises_the_declared_driver_error(spark_session, spark_functions):
    """A known empty eligibility range fails with its FK column before executor wrapping."""
    spec = {
        "parent_id": {
            "method": "fk",
            "kwargs": {
                "parent": {"method": "pk", "kwargs": {"start": 1}},
                "parent_size": 3,
                "born_before": {
                    "parent_start": 10,
                    "parent_rate": 1,
                    "child_start": 0,
                    "child_rate": 1,
                },
            },
        },
    }

    with pytest.raises(RandEngineError, match="parent_id"):
        SparkGenerator(spark_session, spark_functions, spec, seed=123).size(1).get_df()


def test_spark_seed_only_extends_key_generation(spark_session, spark_functions):
    """An explicit key seed leaves the existing native ordinary path usable."""
    spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}

    values = SparkGenerator(spark_session, spark_functions, spec, seed=123).size(20).get_df().toPandas()["age"]

    assert values.between(18, 80).all()
