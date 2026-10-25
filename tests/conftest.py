"""
Pytest configuration file.

Automatically loads all fixtures from the fixtures/ directory.

IMPORTANT - Spark Testing Compatibility:
- PySpark tests are automatically skipped on Windows with Python 3.12+ due to worker crashes
- This is handled in f2_spark_generator_specs_right.py via pytest.skip()
- For CI/CD: run Spark tests on Windows with a Python below 3.12
- Linux/macOS: All Python versions supported
"""
import warnings
from datetime import datetime

import pandas as pd
import pytest

pytest_plugins = [
    "tests.fixtures.f2_spark_generator_specs_right",
]

# Note: Other fixture files can be imported here as needed
# "tests.fixtures.f1_data_generator_specs_right",
# "tests.fixtures.f3_integrations",


def natural_datetime_unit():
    """Unit (`ns`, `us`) the installed pandas gives a naive Python datetime."""
    return pd.Series([datetime(2026, 1, 1)]).dt.unit


def pytest_configure(config):
    """
    Configure pytest settings.
    
    - Filters PySpark deprecation warnings (known issues with pandas/distutils)
    - Spark compatibility handled in fixtures
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
