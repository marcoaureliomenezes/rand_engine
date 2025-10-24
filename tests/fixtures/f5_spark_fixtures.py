"""
Fixtures for PySpark tests.

Note: PySpark is only a test dependency, not a runtime dependency.
These fixtures provide SparkSession and common test data for Spark-based tests.
"""
import pytest


@pytest.fixture(scope="session")
def spark_session():
    """
    Create a SparkSession for testing.
    
    Scope: session - Reused across all tests for performance.
    
    Note: Configured with limited resources for CI/CD compatibility,
    especially on Windows and with Python 3.12+.
    """
    import sys
    import platform
    
    try:
        from pyspark.sql import SparkSession
    except ImportError:
        pytest.skip("PySpark not installed - skipping Spark tests")
    
    # Skip Spark tests on Windows with Python 3.12+ due to compatibility issues
    if platform.system() == "Windows" and sys.version_info >= (3, 12):
        pytest.skip("Spark tests not supported on Windows with Python 3.12+ (worker crashes)")
    
    spark = (
        SparkSession.builder
        .appName("rand-engine-tests")
        .master("local[2]")  # 2 cores local mode
        # Memory configuration for CI environments (prevents worker crashes)
        .config("spark.driver.memory", "1g")
        .config("spark.executor.memory", "1g")
        .config("spark.driver.maxResultSize", "512m")
        # Reduce partitions for faster tests
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.default.parallelism", "2")
        # Disable UI and unnecessary features
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        # Warehouse directory (cross-platform)
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse" if platform.system() != "Windows" else "C:/temp/spark-warehouse")
        # Python worker configuration for stability
        .config("spark.python.worker.reuse", "true")
        .config("spark.python.worker.memory", "512m")
        .getOrCreate()
    )
    
    # Set log level to ERROR to reduce noise
    spark.sparkContext.setLogLevel("ERROR")
    
    yield spark
    
    # Cleanup
    try:
        spark.stop()
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture(scope="session")
def spark_functions(spark_session):
    """
    Provide pyspark.sql.functions module.
    
    This is used for dependency injection in SparkCore methods.
    """
    from pyspark.sql import functions as F
    return F


@pytest.fixture
def empty_spark_df(spark_session):
    """
    Create an empty Spark DataFrame with 100 rows.
    
    Useful as starting point for generation methods.
    """
    return spark_session.range(100)


@pytest.fixture
def small_spark_df(spark_session):
    """
    Create a small Spark DataFrame with 10 rows.
    
    Useful for quick tests and debugging.
    """
    return spark_session.range(10)


@pytest.fixture
def large_spark_df(spark_session):
    """
    Create a large Spark DataFrame with 10,000 rows.
    
    Useful for performance and distribution tests.
    """
    return spark_session.range(10000)


@pytest.fixture
def spark_metadata_simple():
    """
    Simple metadata for basic Spark generation tests.
    """
    return {
        "id": {
            "method": "integers",
            "kwargs": {"min": 1, "max": 100}
        },
        "name": {
            "method": "distincts",
            "kwargs": {"distincts": ["Alice", "Bob", "Charlie", "Diana"]}
        },
        "score": {
            "method": "floats",
            "kwargs": {"min": 0.0, "max": 100.0, "decimals": 2}
        }
    }


@pytest.fixture
def spark_metadata_complex():
    """
    Complex metadata for advanced Spark generation tests.
    """
    return {
        "user_id": {
            "method": "uuid4",
            "kwargs": {}
        },
        "age": {
            "method": "integers",
            "kwargs": {"min": 18, "max": 80}
        },
        "height_cm": {
            "method": "floats_normal",
            "kwargs": {"mean": 170.0, "stddev": 10.0, "decimals": 1}
        },
        "is_active": {
            "method": "booleans",
            "kwargs": {"true_prob": 0.75}
        },
        "category": {
            "method": "distincts",
            "kwargs": {"distincts": ["A", "B", "C", "D", "E"]}
        },
        "registration_date": {
            "method": "dates",
            "kwargs": {
                "start": "2020-01-01",
                "end": "2024-12-31",
                "formato": "%Y-%m-%d"
            }
        },
        "code": {
            "method": "zint",
            "kwargs": {"length": 8}
        }
    }


@pytest.fixture
def spark_metadata_all_types():
    """
    Metadata covering all SparkCore generation methods.
    
    Useful for comprehensive integration tests.
    """
    return {
        # Numeric
        "int_col": {
            "method": "integers",
            "kwargs": {"min": 0, "max": 1000}
        },
        "float_col": {
            "method": "floats",
            "kwargs": {"min": 0.0, "max": 100.0, "decimals": 3}
        },
        "normal_col": {
            "method": "floats_normal",
            "kwargs": {"mean": 50.0, "stddev": 15.0, "decimals": 2}
        },
        
        # Identifiers
        "uuid_col": {
            "method": "uuid4",
            "kwargs": {}
        },
        "zint_col": {
            "method": "zint",
            "kwargs": {"length": 10}
        },
        
        # Selection
        "distinct_col": {
            "method": "distincts",
            "kwargs": {"distincts": ["Option1", "Option2", "Option3"]}
        },
        "bool_col": {
            "method": "booleans",
            "kwargs": {"true_prob": 0.5}
        },
        
        # Temporal
        "date_col": {
            "method": "dates",
            "kwargs": {
                "start": "2023-01-01",
                "end": "2023-12-31",
                "formato": "%Y-%m-%d"
            }
        }
    }


@pytest.fixture
def expected_spark_columns():
    """
    Expected column names for spark_metadata_all_types fixture.
    """
    return [
        "id",  # From spark.range()
        "int_col",
        "float_col",
        "normal_col",
        "uuid_col",
        "zint_col",
        "distinct_col",
        "bool_col",
        "date_col"
    ]
