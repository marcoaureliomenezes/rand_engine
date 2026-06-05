"""
Shared fixtures for database handler tests (DuckDB and SQLite).

These fixtures provide reusable DataFrames and test data for integration tests,
eliminating duplication between test_duckdb.py and test_sqlite.py.
"""

import pytest
import pandas as pd


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing - 5 rows with multiple columns."""
    return pd.DataFrame({
        "id": ["001", "002", "003", "004", "005"],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "age": [25, 30, 35, 28, 32],
        "city": ["NYC", "LA", "Chicago", "Houston", "Phoenix"]
    })


@pytest.fixture
def simple_id_dataframe():
    """Simple 3-row DataFrame with string IDs - for basic tests."""
    return pd.DataFrame({"id": ["001", "002", "003"]})


@pytest.fixture
def simple_int_dataframe():
    """Simple 3-row DataFrame with integer IDs - for numeric tests."""
    return pd.DataFrame({"id": [1, 2, 3]})


@pytest.fixture
def empty_dataframe():
    """Empty DataFrame with id column - for edge case tests."""
    return pd.DataFrame({"id": []})


@pytest.fixture
def products_batch1():
    """First batch of product data - for multi-batch insert tests."""
    return pd.DataFrame({
        "product_id": ["P001", "P002", "P003"],
        "name": ["Laptop", "Mouse", "Keyboard"],
        "price": [999.99, 29.99, 79.99]
    })


@pytest.fixture
def products_batch2():
    """Second batch of product data - for multi-batch insert tests."""
    return pd.DataFrame({
        "product_id": ["P004", "P005"],
        "name": ["Monitor", "Webcam"],
        "price": [299.99, 89.99]
    })
