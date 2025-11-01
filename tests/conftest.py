"""
Pytest configuration file.

Automatically loads all fixtures from the fixtures/ directory.

IMPORTANT - Spark Testing Compatibility:
- PySpark tests are automatically skipped on Windows with Python 3.12+ due to worker crashes
- This is handled in f2_spark_generator_specs_right.py via pytest.skip()
- For CI/CD: Use Python 3.10 or 3.11 for Spark tests on Windows
- Linux/macOS: All Python versions supported
"""
import warnings
import pytest

pytest_plugins = [
    "tests.fixtures.f2_spark_generator_specs_right",
]

# Note: Other fixture files can be imported here as needed
# "tests.fixtures.f1_data_generator_specs_right",
# "tests.fixtures.f3_integrations",


def pytest_configure(config):
    """
    Configure pytest settings.
    
    - Filters PySpark deprecation warnings (known issues with pandas/distutils)
    - Spark compatibility handled in fixtures (see f5_spark_fixtures.py)
    """
    warnings.filterwarnings(
        "ignore",
        message=".*distutils Version classes are deprecated.*",
        category=DeprecationWarning,
        module="pyspark.sql.pandas.utils"
    )
    warnings.filterwarnings(
        "ignore",
        message=".*is_datetime64tz_dtype is deprecated.*",
        category=DeprecationWarning,
        module="pyspark.sql.pandas.conversion"
    )
