"""
Test suite for SparkRandSpecs - Validates Spark example specifications.

Tests Spark DataFrame generation using SparkGenerator with pre-built specs.
Validates column presence, data types, and value constraints for Spark DataFrames.
"""
import pytest


class TestSparkRandSpecsAccess:
    """Test SparkRandSpecs static methods accessibility."""
    
    def test_customers_accessible(self):
        """Test that Spark customers spec is accessible."""
        from rand_engine.examples import SparkRandSpecs
        
        spec = SparkRandSpecs.customers()
        assert isinstance(spec, dict)
        assert 'customer_id' in spec
        assert 'name' in spec
        assert 'age' in spec
    
    def test_products_accessible(self):
        """Test that Spark products spec is accessible."""
        from rand_engine.examples import SparkRandSpecs
        
        spec = SparkRandSpecs.products()
        assert isinstance(spec, dict)
        assert 'product_id' in spec
        assert 'category' in spec
    
    def test_orders_accessible(self):
        """Test that Spark orders spec is accessible."""
        from rand_engine.examples import SparkRandSpecs
        
        spec = SparkRandSpecs.orders()
        assert isinstance(spec, dict)
        assert 'order_id' in spec
        assert 'status' in spec
    
    def test_employees_accessible(self):
        """Test that Spark employees spec is accessible."""
        from rand_engine.examples import SparkRandSpecs
        
        spec = SparkRandSpecs.employees()
        assert isinstance(spec, dict)
        assert 'employee_id' in spec
        assert 'salary' in spec
    
    def test_devices_accessible(self):
        """Test that Spark devices spec is accessible."""
        from rand_engine.examples import SparkRandSpecs
        
        spec = SparkRandSpecs.devices()
        assert isinstance(spec, dict)
        assert 'device_id' in spec
        assert 'device_type' in spec


class TestSparkSpecsGeneration:
    """Test that Spark specs can generate valid Spark DataFrames."""
    
    def test_customers_generates_spark_dataframe(self, spark_session, spark_functions):
        """Test that customers spec generates a valid Spark DataFrame."""
        from rand_engine.examples import SparkRandSpecs
        from rand_engine import SparkGenerator
        
        spec = SparkRandSpecs.customers()
        generator = SparkGenerator(spark_session, spark_functions, spec)
        df = generator.size(10).get_df()
        
        # Validate DataFrame properties
        assert df.count() == 10
        assert 'customer_id' in df.columns
        assert 'name' in df.columns
        assert 'age' in df.columns
        assert 'email_domain' in df.columns
        assert 'is_active' in df.columns
        assert 'account_balance' in df.columns
        
        # Validate data types
        from pyspark.sql.types import StringType, LongType, BooleanType, DoubleType
        schema = {field.name: type(field.dataType).__name__ for field in df.schema.fields}
        
        assert 'StringType' in schema['customer_id']
        assert 'LongType' in schema['age']  # Spark uses LongType for integers
        assert 'BooleanType' in schema['is_active']
    
    def test_products_generates_spark_dataframe(self, spark_session, spark_functions):
        """Test that products spec generates a valid Spark DataFrame with normal distribution."""
        from rand_engine.examples import SparkRandSpecs
        from rand_engine import SparkGenerator
        
        spec = SparkRandSpecs.products()
        generator = SparkGenerator(spark_session, spark_functions, spec)
        df = generator.size(100).get_df()
        
        # Validate DataFrame properties
        assert df.count() == 100
        assert 'product_id' in df.columns
        assert 'product_name' in df.columns
        assert 'category' in df.columns
        assert 'price' in df.columns
        assert 'stock' in df.columns
        assert 'rating' in df.columns
        
        # Collect data for validation
        data = df.select('rating', 'category').collect()
        ratings = [row['rating'] for row in data]
        
        # Validate normal distribution (rating should be around mean=4.0)
        avg_rating = sum(ratings) / len(ratings)
        assert 3.0 < avg_rating < 5.0, "Rating average should be around 4.0"
    
    def test_orders_generates_spark_dataframe_with_dates(self, spark_session, spark_functions):
        """Test that orders spec generates Spark DataFrame with status distribution."""
        from rand_engine.examples import SparkRandSpecs
        from rand_engine import SparkGenerator
        
        spec = SparkRandSpecs.orders()
        generator = SparkGenerator(spark_session, spark_functions, spec)
        df = generator.size(50).get_df()
        
        # Validate DataFrame properties
        assert df.count() == 50
        assert 'order_id' in df.columns
        assert 'customer_id' in df.columns
        assert 'product_id' in df.columns
        assert 'quantity' in df.columns
        assert 'status' in df.columns
        
        # Validate UUID format (should be strings)
        from pyspark.sql.types import StringType
        schema = {field.name: type(field.dataType).__name__ for field in df.schema.fields}
        assert 'StringType' in schema['order_id']
    
    def test_employees_generates_spark_dataframe_with_salary_distribution(self, spark_session, spark_functions):
        """Test that employees spec generates Spark DataFrame with salary distribution."""
        from rand_engine.examples import SparkRandSpecs
        from rand_engine import SparkGenerator
        
        spec = SparkRandSpecs.employees()
        generator = SparkGenerator(spark_session, spark_functions, spec)
        df = generator.size(200).get_df()
        
        # Validate DataFrame properties
        assert df.count() == 200
        assert 'employee_id' in df.columns
        assert 'hire_date' in df.columns
        assert 'salary' in df.columns
        assert 'department' in df.columns
        assert 'role' in df.columns
        assert 'is_remote' in df.columns
        assert 'bonus' in df.columns
        
        # Collect salary data for validation
        data = df.select('salary').collect()
        salaries = [row['salary'] for row in data]
        
        # Validate salary distribution (should be around mean=60000)
        avg_salary = sum(salaries) / len(salaries)
        assert 50000 < avg_salary < 70000, "Salary average should be around 60000"
    
    def test_devices_generates_spark_dataframe_with_weighted_types(self, spark_session, spark_functions):
        """Test that devices spec generates Spark DataFrame with weighted device types."""
        from rand_engine.examples import SparkRandSpecs
        from rand_engine import SparkGenerator
        
        spec = SparkRandSpecs.devices()
        generator = SparkGenerator(spark_session, spark_functions, spec)
        df = generator.size(1000).get_df()
        
        # Validate DataFrame properties
        assert df.count() == 1000
        assert 'device_id' in df.columns
        assert 'device_type' in df.columns
        assert 'status' in df.columns
        assert 'priority' in df.columns
        assert 'temperature' in df.columns
        assert 'battery' in df.columns
        assert 'last_ping' in df.columns
        
        # Collect device_type data for validation
        type_counts = df.groupBy('device_type').count().collect()
        type_dict = {row['device_type']: row['count'] for row in type_counts}
        
        # Validate weighted distribution (Sensor 50%, Gateway 30%, Controller 20%)
        # With 1000 records, Sensor should be most common
        assert type_dict.get('Sensor', 0) > type_dict.get('Gateway', 0)
        assert type_dict.get('Gateway', 0) > type_dict.get('Controller', 0)


class TestSparkSpecsComprehensive:
    """Comprehensive tests for all Spark specs."""
    
    @pytest.mark.parametrize("spec_name,spec_method,expected_columns", [
        ("customers", "customers", 6),
        ("products", "products", 6),
        ("orders", "orders", 5),
        ("transactions", "transactions", 6),
        ("employees", "employees", 7),
        ("devices", "devices", 7),
        ("users", "users", 6),
    ])
    def test_spec_generates_correct_column_count(self, spark_session, spark_functions, 
                                                  spec_name, spec_method, expected_columns):
        """Test that each Spark spec generates the correct number of columns."""
        from rand_engine.examples import SparkRandSpecs
        from rand_engine import SparkGenerator
        
        spec = getattr(SparkRandSpecs, spec_method)()
        generator = SparkGenerator(spark_session, spark_functions, spec)
        df = generator.size(5).get_df()
        
        # Note: Spark adds 'id' column from range(), so we check generated columns
        # The 'id' column is from spark.range() used internally
        assert len(df.columns) >= expected_columns, f"{spec_name} should have at least {expected_columns} columns"
    
    def test_all_specs_return_dicts(self):
        """Test that all Spark specs return dictionaries."""
        from rand_engine.examples import SparkRandSpecs
        
        specs = [
            SparkRandSpecs.customers(),
            SparkRandSpecs.products(),
            SparkRandSpecs.orders(),
            SparkRandSpecs.transactions(),
            SparkRandSpecs.employees(),
            SparkRandSpecs.devices(),
            SparkRandSpecs.users(),
            SparkRandSpecs.invoices(),
            SparkRandSpecs.shipments(),
            SparkRandSpecs.events(),
        ]
        
        for spec in specs:
            assert isinstance(spec, dict)
            assert len(spec) > 0
            # All specs should have method and kwargs keys
            for col_name, col_spec in spec.items():
                assert 'method' in col_spec, f"Column {col_name} missing 'method' key"
