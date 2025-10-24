"""
Pytest configuration file.

Automatically loads all fixtures from the fixtures/ directory.
"""
import warnings
import pytest

pytest_plugins = [
    "tests.fixtures.f5_spark_fixtures",
]

# Note: Other fixture files can be imported here as needed
# "tests.fixtures.f1_right_specs",
# "tests.fixtures.f3_integrations",


def pytest_configure(config):
    """Configure pytest to filter PySpark deprecation warnings."""
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
