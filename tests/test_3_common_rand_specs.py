"""
Tests for CommonRandSpecs - Cross-compatible specifications for DataGenerator and SparkGenerator.

This test suite validates that CommonRandSpecs work correctly in both pandas (DataGenerator)
and PySpark (SparkGenerator) environments. Each spec is tested with both generators to ensure
true cross-compatibility.
"""

import pytest
import pandas as pd
from rand_engine.main.data_generator import DataGenerator
from rand_engine.main.spark_generator import SparkGenerator
from rand_engine.examples.spark_rand_specs import CommonRandSpecs


class TestCommonRandSpecsAccess:
    """Test that all CommonRandSpecs are accessible and return valid dicts."""

    def test_customers_accessible(self):
        """Test customers spec is accessible."""
        spec = CommonRandSpecs.customers()
        assert isinstance(spec, dict)
        assert len(spec) == 6  # 6 fields

    def test_products_accessible(self):
        """Test products spec is accessible."""
        spec = CommonRandSpecs.products()
        assert isinstance(spec, dict)
        assert len(spec) == 7  # 7 fields

    def test_orders_accessible(self):
        """Test orders spec is accessible."""
        spec = CommonRandSpecs.orders()
        assert isinstance(spec, dict)
        assert len(spec) == 6  # 6 fields

    def test_transactions_accessible(self):
        """Test transactions spec is accessible."""
        spec = CommonRandSpecs.transactions()
        assert isinstance(spec, dict)
        assert len(spec) == 7  # 7 fields

    def test_employees_accessible(self):
        """Test employees spec is accessible."""
        spec = CommonRandSpecs.employees()
        assert isinstance(spec, dict)
        assert len(spec) == 8  # 8 fields

    def test_sensors_accessible(self):
        """Test sensors spec is accessible."""
        spec = CommonRandSpecs.sensors()
        assert isinstance(spec, dict)
        assert len(spec) == 7  # 7 fields

    def test_users_accessible(self):
        """Test users spec is accessible."""
        spec = CommonRandSpecs.users()
        assert isinstance(spec, dict)
        assert len(spec) == 7  # 7 fields

    def test_events_accessible(self):
        """Test events spec is accessible."""
        spec = CommonRandSpecs.events()
        assert isinstance(spec, dict)
        assert len(spec) == 6  # 6 fields

    def test_sales_accessible(self):
        """Test sales spec is accessible."""
        spec = CommonRandSpecs.sales()
        assert isinstance(spec, dict)
        assert len(spec) == 8  # 8 fields

    def test_devices_accessible(self):
        """Test devices spec is accessible."""
        spec = CommonRandSpecs.devices()
        assert isinstance(spec, dict)
        assert len(spec) == 7  # 7 fields


class TestDataGeneratorCompatibility:
    """Test CommonRandSpecs work correctly with DataGenerator (pandas)."""

    @pytest.mark.parametrize("spec_name,expected_cols", [
        ("customers", 6),
        ("products", 7),
        ("orders", 6),
        ("transactions", 7),
        ("employees", 8),
        ("sensors", 7),
        ("users", 7),
        ("events", 6),
        ("sales", 8),
        ("devices", 7)
    ])
    def test_spec_generates_pandas_dataframe(self, spec_name, expected_cols):
        """Test each spec generates valid pandas DataFrame."""
        spec = getattr(CommonRandSpecs, spec_name)()
        generator = DataGenerator(spec, seed=42)
        df = generator.size(50).get_df()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 50
        assert len(df.columns) == expected_cols
        assert df.isnull().sum().sum() == 0  # No nulls

    def test_customers_column_names(self):
        """Test customers spec generates correct column names."""
        spec = CommonRandSpecs.customers()
        df = DataGenerator(spec, seed=42).size(10).get_df()
        expected_columns = ["customer_id", "age", "city", "total_spent", "is_premium", "registration_date"]
        assert list(df.columns) == expected_columns

    def test_products_column_names(self):
        """Test products spec generates correct column names."""
        spec = CommonRandSpecs.products()
        df = DataGenerator(spec, seed=42).size(10).get_df()
        expected_columns = ["product_id", "sku", "name", "price", "stock_quantity", "category", "is_active"]
        assert list(df.columns) == expected_columns

    def test_employees_column_names(self):
        """Test employees spec generates correct column names."""
        spec = CommonRandSpecs.employees()
        df = DataGenerator(spec, seed=42).size(10).get_df()
        expected_columns = ["employee_id", "department", "position", "salary", "hire_date", "age", "is_remote", "performance_score"]
        assert list(df.columns) == expected_columns


class TestSparkGeneratorCompatibility:
    """Test CommonRandSpecs work correctly with SparkGenerator (PySpark)."""

    @pytest.mark.parametrize("spec_name,expected_cols", [
        ("customers", 6),
        ("products", 7),
        ("orders", 6),
        ("transactions", 7),
        ("employees", 8),
        ("sensors", 7),
        ("users", 7),
        ("events", 6),
        ("sales", 8),
        ("devices", 7)
    ])
    def test_spec_generates_spark_dataframe(self, spark_session, spark_functions, spec_name, expected_cols):
        """Test each spec generates valid Spark DataFrame."""
        spec = getattr(CommonRandSpecs, spec_name)()
        generator = SparkGenerator(spark_session, spark_functions, spec)
        df = generator.size(50).get_df()
        
        assert df.count() == 50
        assert len(df.columns) == expected_cols
        
        # Check for nulls in any column
        from pyspark.sql import functions as F
        null_counts = [df.filter(F.col(col).isNull()).count() for col in df.columns]
        assert sum(null_counts) == 0  # No nulls

    def test_customers_column_names_spark(self, spark_session, spark_functions):
        """Test customers spec generates correct column names in Spark."""
        spec = CommonRandSpecs.customers()
        df = SparkGenerator(spark_session, spark_functions, spec).size(10).get_df()
        expected_columns = ["customer_id", "age", "city", "total_spent", "is_premium", "registration_date"]
        assert df.columns == expected_columns

    def test_products_column_names_spark(self, spark_session, spark_functions):
        """Test products spec generates correct column names in Spark."""
        spec = CommonRandSpecs.products()
        df = SparkGenerator(spark_session, spark_functions, spec).size(10).get_df()
        expected_columns = ["product_id", "sku", "name", "price", "stock_quantity", "category", "is_active"]
        assert df.columns == expected_columns

    def test_employees_column_names_spark(self, spark_session, spark_functions):
        """Test employees spec generates correct column names in Spark."""
        spec = CommonRandSpecs.employees()
        df = SparkGenerator(spark_session, spark_functions, spec).size(10).get_df()
        expected_columns = ["employee_id", "department", "position", "salary", "hire_date", "age", "is_remote", "performance_score"]
        assert df.columns == expected_columns


class TestCrossGeneratorConsistency:
    """Test that specs generate consistent data structures across both generators."""

    @pytest.mark.parametrize("spec_name", [
        "customers",
        "products",
        "orders",
        "transactions",
        "employees",
        "sensors",
        "users",
        "events",
        "sales",
        "devices"
    ])
    def test_same_columns_both_generators(self, spark_session, spark_functions, spec_name):
        """Test that both generators produce DataFrames with same columns."""
        spec = getattr(CommonRandSpecs, spec_name)()
        
        # Generate with DataGenerator
        pandas_df = DataGenerator(spec, seed=42).size(10).get_df()
        pandas_columns = set(pandas_df.columns)
        
        # Generate with SparkGenerator
        spark_df = SparkGenerator(spark_session, spark_functions, spec).size(10).get_df()
        spark_columns = set(spark_df.columns)
        
        assert pandas_columns == spark_columns, f"{spec_name}: Column mismatch"

    def test_customers_data_types_consistency(self, spark_session, spark_functions):
        """Test customers generates compatible data types in both generators."""
        spec = CommonRandSpecs.customers()
        
        # Pandas generation
        pandas_df = DataGenerator(spec, seed=42).size(100).get_df()
        
        # Spark generation
        spark_df = SparkGenerator(spark_session, spark_functions, spec).size(100).get_df()
        spark_pandas = spark_df.toPandas()
        
        # Check key columns exist and have reasonable values
        assert pandas_df['age'].min() >= 18
        assert pandas_df['age'].max() <= 80
        assert spark_pandas['age'].min() >= 18
        assert spark_pandas['age'].max() <= 80
        
        assert pandas_df['is_premium'].dtype == bool
        assert spark_pandas['is_premium'].dtype == bool

    def test_products_weighted_distribution_both_generators(self, spark_session, spark_functions):
        """Test products category distribution works in both generators."""
        spec = CommonRandSpecs.products()
        
        # Pandas generation
        pandas_df = DataGenerator(spec, seed=42).size(500).get_df()
        pandas_dist = pandas_df['category'].value_counts(normalize=True)
        
        # Spark generation
        spark_df = SparkGenerator(spark_session, spark_functions, spec).size(500).get_df()
        spark_pandas = spark_df.toPandas()
        spark_dist = spark_pandas['category'].value_counts(normalize=True)
        
        # Both should have same categories (order may differ)
        assert set(pandas_dist.index) == set(spark_dist.index)
        assert 'Electronics' in pandas_dist.index
        assert 'Accessories' in pandas_dist.index


class TestSpecValidation:
    """Test that CommonRandSpecs pass validation in both generators."""

    @pytest.mark.parametrize("spec_name", [
        "customers", "products", "orders", "transactions",
        "employees", "sensors", "users", "events", "sales", "devices"
    ])
    def test_spec_passes_pandas_validation(self, spec_name):
        """Test specs pass DataGenerator validation."""
        spec = getattr(CommonRandSpecs, spec_name)()
        # Should not raise validation error
        generator = DataGenerator(spec)
        assert generator is not None

    @pytest.mark.parametrize("spec_name", [
        "customers", "products", "orders", "transactions",
        "employees", "sensors", "users", "events", "sales", "devices"
    ])
    def test_spec_passes_spark_validation(self, spark_session, spark_functions, spec_name):
        """Test specs pass SparkGenerator validation."""
        spec = getattr(CommonRandSpecs, spec_name)()
        # Should not raise validation error
        generator = SparkGenerator(spark_session, spark_functions, spec)
        assert generator is not None


class TestDataQuality:
    """Test generated data quality across both generators."""

    def test_no_duplicate_uuids_pandas(self):
        """Test UUID fields generate unique values in pandas."""
        spec = CommonRandSpecs.products()  # Has UUID product_id
        df = DataGenerator(spec, seed=42).size(100).get_df()
        assert df['product_id'].nunique() == 100

    def test_no_duplicate_uuids_spark(self, spark_session, spark_functions):
        """Test UUID fields generate unique values in Spark."""
        spec = CommonRandSpecs.products()  # Has UUID product_id
        df = SparkGenerator(spark_session, spark_functions, spec).size(100).get_df()
        assert df.select('product_id').distinct().count() == 100

    def test_zero_padded_format_pandas(self):
        """Test zero-padded fields maintain format in pandas."""
        spec = CommonRandSpecs.products()  # Has 8-digit sku with int_zfilled
        df = DataGenerator(spec, seed=42).size(50).get_df()
        # All should be 8 characters
        assert all(len(str(x)) == 8 for x in df['sku'])

    def test_zero_padded_format_spark(self, spark_session, spark_functions):
        """Test zero-padded fields maintain format in Spark."""
        spec = CommonRandSpecs.products()  # Has 8-digit sku with int_zfilled
        df = SparkGenerator(spark_session, spark_functions, spec).size(50).get_df()
        spark_pandas = df.toPandas()
        # All should be 8 characters
        assert all(len(str(x)) == 8 for x in spark_pandas['sku'])

    def test_boolean_probability_pandas(self):
        """Test boolean probability works correctly in pandas."""
        spec = CommonRandSpecs.products()  # is_active with 85% prob_true
        df = DataGenerator(spec, seed=42).size(1000).get_df()
        true_ratio = df['is_active'].sum() / len(df)
        # Should be close to 0.85 (within 10% tolerance)
        assert 0.75 <= true_ratio <= 0.95

    def test_boolean_probability_spark(self, spark_session, spark_functions):
        """Test boolean probability works correctly in Spark."""
        spec = CommonRandSpecs.products()  # is_active with 85% prob_true
        df = SparkGenerator(spark_session, spark_functions, spec).size(1000).get_df()
        spark_pandas = df.toPandas()
        true_ratio = spark_pandas['is_active'].sum() / len(spark_pandas)
        # Should be close to 0.85 (within 10% tolerance)
        assert 0.75 <= true_ratio <= 0.95


class TestDocumentation:
    """Test that CommonRandSpecs has proper documentation."""

    def test_class_has_docstring(self):
        """Test CommonRandSpecs class has docstring."""
        assert CommonRandSpecs.__doc__ is not None
        assert "cross-compatible" in CommonRandSpecs.__doc__.lower()

    @pytest.mark.parametrize("spec_name", [
        "customers", "products", "orders", "transactions",
        "employees", "sensors", "users", "events", "sales", "devices"
    ])
    def test_methods_have_docstrings(self, spec_name):
        """Test all spec methods have docstrings."""
        method = getattr(CommonRandSpecs, spec_name)
        assert method.__doc__ is not None
        assert "Fields" in method.__doc__  # Should document fields
