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
        from rand_engine.examples import CommonRandSpecs
        
        spec = CommonRandSpecs.customers()
        assert isinstance(spec, dict)
        assert 'customer_id' in spec
        assert 'city' in spec  # Changed from 'name' to 'city'
        assert 'age' in spec
    
    def test_products_accessible(self):
        """Test that Spark products spec is accessible."""
        from rand_engine.examples import CommonRandSpecs
        
        spec = CommonRandSpecs.products()
        assert isinstance(spec, dict)
        assert 'product_id' in spec
        assert 'category' in spec
    
    def test_orders_accessible(self):
        """Test that Spark orders spec is accessible."""
        from rand_engine.examples import CommonRandSpecs
        
        spec = CommonRandSpecs.orders()
        assert isinstance(spec, dict)
        assert 'order_id' in spec
        assert 'status' in spec
    
    def test_employees_accessible(self):
        """Test that Spark employees spec is accessible."""
        from rand_engine.examples import CommonRandSpecs
        
        spec = CommonRandSpecs.employees()
        assert isinstance(spec, dict)
        assert 'employee_id' in spec
        assert 'salary' in spec
    
    def test_devices_accessible(self):
        """Test that Spark devices spec is accessible."""
        from rand_engine.examples import CommonRandSpecs
        
        spec = CommonRandSpecs.devices()
        assert isinstance(spec, dict)
        assert 'device_id' in spec
        assert 'serial_number' in spec  # Changed from 'device_type' to 'serial_number'


class TestSparkSpecsGeneration:
    """Test that Spark specs can generate valid Spark DataFrames."""
    
    def test_customers_generates_spark_dataframe(self, spark_session, spark_functions):
        """Test that customers spec generates a valid Spark DataFrame."""
        from rand_engine.examples import CommonRandSpecs
        from rand_engine import SparkGenerator
        
        spec = CommonRandSpecs.customers()
        generator = SparkGenerator(spark_session, spark_functions, spec)
        df = generator.size(10).get_df()
        
        # Validate DataFrame properties
        assert df.count() == 10
        assert 'customer_id' in df.columns
        assert 'city' in df.columns  # Changed from 'name' to 'city'
        assert 'age' in df.columns
        assert 'total_spent' in df.columns  # Changed from 'email_domain' to 'total_spent'
        assert 'is_premium' in df.columns  # Changed from 'is_active' to 'is_premium'
        assert 'registration_date' in df.columns  # Changed from 'account_balance' to 'registration_date'
        
        # Validate data types
        from pyspark.sql.types import StringType, IntegerType, BooleanType, DoubleType
        schema = {field.name: type(field.dataType).__name__ for field in df.schema.fields}
        
        assert 'StringType' in schema['customer_id']
        assert 'IntegerType' in schema['age']  # Spark uses IntegerType for int32
        assert 'BooleanType' in schema['is_premium']
    
    def test_products_generates_spark_dataframe(self, spark_session, spark_functions):
        """Test that products spec generates a valid Spark DataFrame with normal distribution."""
        from rand_engine.examples import CommonRandSpecs
        from rand_engine import SparkGenerator
        
        spec = CommonRandSpecs.products()
        generator = SparkGenerator(spark_session, spark_functions, spec)
        df = generator.size(100).get_df()
        
        # Validate DataFrame properties
        assert df.count() == 100
        assert 'product_id' in df.columns
        assert 'name' in df.columns  # Changed from 'product_name' to 'name'
        assert 'sku' in df.columns  # Added sku column
        assert 'category' in df.columns
        assert 'price' in df.columns
        assert 'stock_quantity' in df.columns  # Changed from 'stock' to 'stock_quantity'
        assert 'is_active' in df.columns  # Changed from 'rating' to 'is_active'
        
        # Collect data for validation
        data = df.select('price', 'category').collect()
        prices = [row['price'] for row in data]
        
        # Validate price range (price should be between 9.99 and 2999.99)
        avg_price = sum(prices) / len(prices)
        assert 9.99 <= avg_price <= 2999.99, "Price average should be in valid range"
    
    def test_orders_generates_spark_dataframe_with_dates(self, spark_session, spark_functions):
        """Test that orders spec generates Spark DataFrame with status distribution."""
        from rand_engine.examples import CommonRandSpecs
        from rand_engine import SparkGenerator
        
        spec = CommonRandSpecs.orders()
        generator = SparkGenerator(spark_session, spark_functions, spec)
        df = generator.size(50).get_df()
        
        # Validate DataFrame properties
        assert df.count() == 50
        assert 'order_id' in df.columns
        assert 'customer_id' in df.columns
        assert 'amount' in df.columns  # Changed from 'product_id' to 'amount'
        assert 'order_timestamp' in df.columns  # Changed from 'quantity' to 'order_timestamp'
        assert 'status' in df.columns
        assert 'payment_method' in df.columns  # Added payment_method
        
        # Validate UUID format (should be strings)
        from pyspark.sql.types import StringType
        schema = {field.name: type(field.dataType).__name__ for field in df.schema.fields}
        assert 'StringType' in schema['order_id']
    
    def test_employees_generates_spark_dataframe_with_salary_distribution(self, spark_session, spark_functions):
        """Test that employees spec generates Spark DataFrame with salary distribution."""
        from rand_engine.examples import CommonRandSpecs
        from rand_engine import SparkGenerator
        
        spec = CommonRandSpecs.employees()
        generator = SparkGenerator(spark_session, spark_functions, spec)
        df = generator.size(200).get_df()
        
        # Validate DataFrame properties
        assert df.count() == 200
        assert 'employee_id' in df.columns
        assert 'hire_date' in df.columns
        assert 'salary' in df.columns
        assert 'department' in df.columns
        assert 'position' in df.columns  # Changed from 'role' to 'position'
        assert 'is_remote' in df.columns
        assert 'performance_score' in df.columns  # Changed from 'bonus' to 'performance_score'
        assert 'age' in df.columns  # Added age column
        
        # Collect salary data for validation
        data = df.select('salary').collect()
        salaries = [row['salary'] for row in data]
        
        # Validate salary distribution (should be around mean=50000)
        avg_salary = sum(salaries) / len(salaries)
        assert 40000 < avg_salary < 60000, "Salary average should be around 50000"
    
    def test_devices_generates_spark_dataframe_with_weighted_types(self, spark_session, spark_functions):
        """Test that devices spec generates Spark DataFrame with weighted status."""
        from rand_engine.examples import CommonRandSpecs
        from rand_engine import SparkGenerator
        
        spec = CommonRandSpecs.devices()
        generator = SparkGenerator(spark_session, spark_functions, spec)
        df = generator.size(1000).get_df()
        
        # Validate DataFrame properties
        assert df.count() == 1000
        assert 'device_id' in df.columns
        assert 'serial_number' in df.columns  # Changed from 'device_type' to 'serial_number'
        assert 'firmware_version' in df.columns  # Added firmware_version
        assert 'uptime_hours' in df.columns  # Changed from 'temperature' to 'uptime_hours'
        assert 'status' in df.columns
        assert 'is_critical' in df.columns  # Changed from 'battery' to 'is_critical'
        assert 'last_seen' in df.columns  # Changed from 'last_ping' to 'last_seen'
        
        # Collect status data for validation
        status_counts = df.groupBy('status').count().collect()
        status_dict = {row['status']: row['count'] for row in status_counts}
        
        # Validate weighted distribution (online 80%, offline 10%, maintenance 7%, error 3%)
        # With 1000 records, online should be most common
        assert status_dict.get('online', 0) > status_dict.get('offline', 0)
        assert status_dict.get('offline', 0) >= status_dict.get('error', 0)


class TestSparkSpecsComprehensive:
    """Comprehensive tests for all Spark specs."""
    
    @pytest.mark.parametrize("spec_name,spec_method,expected_columns", [
        ("customers", "customers", 6),
        ("products", "products", 7),  # Changed from 6 to 7 (added sku column)
        ("orders", "orders", 6),  # Changed from 5 to 6
        ("transactions", "transactions", 7),  # Changed from 6 to 7
        ("employees", "employees", 8),  # Changed from 7 to 8 (added age, performance_score)
        ("devices", "devices", 7),
        ("users", "users", 7),  # Changed from 6 to 7
    ])
    def test_spec_generates_correct_column_count(self, spark_session, spark_functions, 
                                                  spec_name, spec_method, expected_columns):
        """Test that each Spark spec generates the correct number of columns."""
        from rand_engine.examples import CommonRandSpecs
        from rand_engine import SparkGenerator
        
        spec = getattr(CommonRandSpecs, spec_method)()  # Changed from SparkRandSpecs to CommonRandSpecs
        generator = SparkGenerator(spark_session, spark_functions, spec)
        df = generator.size(5).get_df()
        
        # Note: Spark adds 'id' column from range(), so we check generated columns
        # The 'id' column is from spark.range() used internally
        assert len(df.columns) >= expected_columns, f"{spec_name} should have at least {expected_columns} columns"
    
    def test_all_specs_return_dicts(self):
        """Test that all Spark specs return dictionaries."""
        from rand_engine.examples import CommonRandSpecs
        
        specs = [
            CommonRandSpecs.customers(),
            CommonRandSpecs.products(),
            CommonRandSpecs.orders(),
            CommonRandSpecs.transactions(),
            CommonRandSpecs.employees(),
            CommonRandSpecs.sensors(),  # Changed from devices to sensors
            CommonRandSpecs.users(),
            CommonRandSpecs.events(),  # Removed invoices and shipments
            CommonRandSpecs.sales(),  # Added sales
            CommonRandSpecs.devices(),  # Moved devices here
        ]
        
        for spec in specs:
            assert isinstance(spec, dict)
            assert len(spec) > 0
            # All specs should have method and kwargs keys
            for col_name, col_spec in spec.items():
                assert 'method' in col_spec, f"Column {col_name} missing 'method' key"
