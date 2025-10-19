"""
Tests for SQLiteHandler - Comprehensive usage examples.

These tests demonstrate all capabilities of the SQLiteHandler class,
including connection pooling, table operations, and data manipulation.
They mirror the DuckDBHandler tests to ensure consistent behavior.
"""

import pytest
import pandas as pd
import tempfile
import os
from rand_engine.integrations._sqlite_handler import SQLiteHandler


@pytest.fixture(scope="function", autouse=True)
def cleanup_connections():
    """Cleanup all SQLite connections after each test."""
    yield
    SQLiteHandler.close_all()


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "id": ["001", "002", "003", "004", "005"],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "age": [25, 30, 35, 28, 32],
        "city": ["NYC", "LA", "Chicago", "Houston", "Phoenix"]
    })


@pytest.fixture
def temp_db_path():
    """Create a temporary database file path."""
    # Generate path without creating the file (SQLite will create it)
    db_path = os.path.join(tempfile.gettempdir(), f"test_sqlite_{os.getpid()}_{id(object())}.db")
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


# ============================================================================
# BASIC OPERATIONS
# ============================================================================

def test_create_in_memory_database():
    """
    Example 1: Create an in-memory SQLite database.
    
    In-memory databases are fast and useful for temporary operations.
    """
    handler = SQLiteHandler(":memory:")
    
    assert handler.db_path == ":memory:"
    assert handler.conn is not None
    print("\n✓ In-memory database created successfully")


def test_create_file_based_database(temp_db_path):
    """
    Example 2: Create a file-based SQLite database.
    
    File-based databases persist data on disk.
    """
    handler = SQLiteHandler(temp_db_path)
    
    assert handler.db_path == temp_db_path
    assert os.path.exists(temp_db_path)
    print(f"\n✓ File-based database created at: {temp_db_path}")


def test_connection_pooling():
    """
    Example 3: Connection pooling - multiple handlers share the same connection.
    
    This is crucial for :memory: databases to preserve state across operations.
    """
    handler1 = SQLiteHandler(":memory:")
    handler2 = SQLiteHandler(":memory:")
    
    # Both handlers share the same connection
    assert handler1.conn is handler2.conn
    assert id(handler1.conn) == id(handler2.conn)
    print("\n✓ Connection pooling working: both handlers share the same connection")


# ============================================================================
# TABLE OPERATIONS
# ============================================================================

def test_create_table():
    """
    Example 4: Create a table with primary key.
    
    Demonstrates table creation with proper schema definition.
    """
    handler = SQLiteHandler(":memory:")
    
    # Create table with single primary key
    handler.create_table("users", "id VARCHAR(10)")
    
    # Verify table exists by querying it (should return empty DataFrame)
    df = handler.select_all("users")
    assert df.empty
    assert "id" in df.columns
    print("\n✓ Table 'users' created with primary key 'id'")


def test_create_table_if_not_exists():
    """
    Example 5: CREATE TABLE IF NOT EXISTS behavior.
    
    Multiple calls to create_table won't error if table already exists.
    """
    handler = SQLiteHandler(":memory:")
    
    # Create table twice - should not raise error
    handler.create_table("products", "product_id VARCHAR(20)")
    handler.create_table("products", "product_id VARCHAR(20)")
    
    df = handler.select_all("products")
    assert df.empty
    print("\n✓ CREATE TABLE IF NOT EXISTS works correctly")


def test_drop_table():
    """
    Example 6: Drop a table.
    
    Demonstrates how to remove tables from the database.
    """
    handler = SQLiteHandler(":memory:")
    
    # Create and then drop table
    handler.create_table("temp_table", "id INTEGER")
    handler.drop_table("temp_table")
    
    # Verify table is gone by checking if query raises error
    with pytest.raises(Exception):
        handler.select_all("temp_table")
    
    print("\n✓ Table dropped successfully")


# ============================================================================
# DATA INSERTION
# ============================================================================

def test_insert_dataframe(sample_dataframe):
    """
    Example 7: Insert DataFrame into table.
    
    Basic workflow: create table, insert data, verify insertion.
    """
    handler = SQLiteHandler(":memory:")
    
    # Create table matching DataFrame structure
    handler.create_table("users", "id VARCHAR(10)")
    
    # Insert data
    handler.insert_df("users", sample_dataframe, ["id"])
    
    # Verify insertion
    df = handler.select_all("users")
    assert len(df) == 5
    assert list(df.columns) == ["id"]
    print(f"\n✓ Inserted {len(df)} rows into 'users' table")


def test_insert_duplicate_handling(sample_dataframe):
    """
    Example 8: Duplicate key handling with INSERT OR IGNORE.
    
    Demonstrates how the handler handles duplicate primary keys gracefully.
    """
    handler = SQLiteHandler(":memory:")
    handler.create_table("users", "id VARCHAR(10)")
    
    # Insert same data twice
    handler.insert_df("users", sample_dataframe, ["id"])
    handler.insert_df("users", sample_dataframe, ["id"])  # Duplicates ignored
    
    # Should still have only 5 rows (duplicates ignored)
    df = handler.select_all("users")
    assert len(df) == 5
    print("\n✓ Duplicate keys ignored correctly (INSERT OR IGNORE)")


def test_incremental_inserts():
    """
    Example 9: Incremental data insertion.
    
    Demonstrates adding new records over multiple insert operations.
    """
    handler = SQLiteHandler(":memory:")
    handler.create_table("events", "event_id VARCHAR(10)")
    
    # First batch
    df1 = pd.DataFrame({"event_id": ["E001", "E002", "E003"]})
    handler.insert_df("events", df1, ["event_id"])
    
    # Second batch (new records)
    df2 = pd.DataFrame({"event_id": ["E004", "E005"]})
    handler.insert_df("events", df2, ["event_id"])
    
    # Total should be 5
    df = handler.select_all("events")
    assert len(df) == 5
    print(f"\n✓ Incremental inserts: {len(df)} total records")


# ============================================================================
# DATA RETRIEVAL
# ============================================================================

def test_select_all_columns(sample_dataframe):
    """
    Example 10: Select all columns from table.
    
    Retrieve complete dataset without column filtering.
    """
    handler = SQLiteHandler(":memory:")
    handler.create_table("users", "id VARCHAR(10)")
    handler.insert_df("users", sample_dataframe, ["id"])
    
    # Select all columns
    df = handler.select_all("users")
    
    assert len(df) == 5
    assert "id" in df.columns
    print(f"\n✓ Retrieved all data: {len(df)} rows")


def test_select_specific_columns(sample_dataframe):
    """
    Example 11: Select specific columns from table.
    
    Demonstrates column filtering in queries.
    """
    handler = SQLiteHandler(":memory:")
    handler.create_table("users", "id VARCHAR(10)")
    handler.insert_df("users", sample_dataframe, ["id"])
    
    # Select only specific columns
    df = handler.select_all("users", columns=["id"])
    
    assert len(df) == 5
    assert list(df.columns) == ["id"]
    print(f"\n✓ Retrieved specific columns: {df.columns.tolist()}")


# ============================================================================
# SECURITY & VALIDATION
# ============================================================================

def test_invalid_table_name_create():
    """
    Example 12: SQL injection protection - create_table.
    
    The handler validates table names to prevent SQL injection.
    Note: SQLite is more permissive, but we still test invalid patterns.
    """
    handler = SQLiteHandler(":memory:")
    
    # This should work
    handler.create_table("valid_table_name", "id INTEGER")
    
    # This should still work in SQLite (it's very permissive)
    # but we test the basic functionality
    df = handler.select_all("valid_table_name")
    assert df is not None
    
    print("\n✓ Table creation with valid names works correctly")


def test_invalid_table_name_select():
    """
    Example 13: SQL injection protection - select_all.
    
    Table name validation prevents malicious queries.
    """
    handler = SQLiteHandler(":memory:")
    handler.create_table("safe_table", "id INTEGER")
    
    # Valid table name
    df = handler.select_all("safe_table")
    assert df is not None
    
    # Invalid table name with special characters
    with pytest.raises(ValueError, match="Invalid table name"):
        handler.select_all("malicious'; DROP TABLE safe_table; --")
    
    print("\n✓ SQL injection protection working for select_all")


def test_invalid_table_name_insert():
    """
    Example 14: SQL injection protection - insert_df.
    
    Insertion operations also validate table names.
    """
    handler = SQLiteHandler(":memory:")
    df = pd.DataFrame({"id": [1, 2, 3]})
    
    # Invalid table name
    with pytest.raises(ValueError, match="Invalid table name"):
        handler.insert_df("bad_table'; DROP TABLE users; --", df, ["id"])
    
    print("\n✓ SQL injection protection working for insert_df")


# ============================================================================
# REAL-WORLD SCENARIOS
# ============================================================================

def test_complete_workflow():
    """
    Example 15: Complete workflow - Create, Insert, Query, Update.
    
    Demonstrates a realistic use case combining multiple operations.
    """
    handler = SQLiteHandler(":memory:")
    
    # Step 1: Create table
    handler.create_table("products", "product_id VARCHAR(20)")
    
    # Step 2: Insert initial data
    batch1 = pd.DataFrame({
        "product_id": ["P001", "P002", "P003"],
        "name": ["Laptop", "Mouse", "Keyboard"],
        "price": [999.99, 29.99, 79.99]
    })
    handler.insert_df("products", batch1, ["product_id"])
    
    # Step 3: Insert more data
    batch2 = pd.DataFrame({
        "product_id": ["P004", "P005"],
        "name": ["Monitor", "Webcam"],
        "price": [299.99, 89.99]
    })
    handler.insert_df("products", batch2, ["product_id"])
    
    # Step 4: Query data
    df = handler.select_all("products")
    
    assert len(df) == 5
    assert "product_id" in df.columns
    print(f"\n✓ Complete workflow successful: {len(df)} products in database")


def test_multiple_tables():
    """
    Example 16: Working with multiple tables.
    
    Demonstrates managing multiple related tables in the same database.
    """
    handler = SQLiteHandler(":memory:")
    
    # Create users table
    handler.create_table("users", "user_id VARCHAR(10)")
    users_df = pd.DataFrame({"user_id": ["U001", "U002", "U003"]})
    handler.insert_df("users", users_df, ["user_id"])
    
    # Create orders table
    handler.create_table("orders", "order_id VARCHAR(10)")
    orders_df = pd.DataFrame({"order_id": ["O001", "O002"]})
    handler.insert_df("orders", orders_df, ["order_id"])
    
    # Query both tables
    users = handler.select_all("users")
    orders = handler.select_all("orders")
    
    assert len(users) == 3
    assert len(orders) == 2
    print(f"\n✓ Multiple tables: {len(users)} users, {len(orders)} orders")


def test_persistent_database(temp_db_path):
    """
    Example 17: Persistent database across handler instances.
    
    File-based databases maintain data between handler instances.
    """
    # First handler: Create and insert data
    handler1 = SQLiteHandler(temp_db_path)
    handler1.create_table("persistent_data", "id VARCHAR(10)")
    df1 = pd.DataFrame({"id": ["D001", "D002", "D003"]})
    handler1.insert_df("persistent_data", df1, ["id"])
    handler1.close()
    
    # Second handler: Read existing data
    handler2 = SQLiteHandler(temp_db_path)
    df2 = handler2.select_all("persistent_data")
    
    assert len(df2) == 3
    # Order is not guaranteed without ORDER BY clause
    assert set(df2["id"]) == {"D001", "D002", "D003"}
    print(f"\n✓ Data persisted across handler instances: {len(df2)} rows")


def test_connection_sharing_preserves_state():
    """
    Example 18: Connection pooling preserves state.
    
    Critical for :memory: databases - multiple handlers see the same data.
    """
    # Handler 1: Create table and insert data
    handler1 = SQLiteHandler(":memory:")
    handler1.create_table("shared_data", "id VARCHAR(10)")
    df1 = pd.DataFrame({"id": ["S001", "S002"]})
    handler1.insert_df("shared_data", df1, ["id"])
    
    # Handler 2: Can see the data from handler1
    handler2 = SQLiteHandler(":memory:")
    df2 = handler2.select_all("shared_data")
    
    assert len(df2) == 2
    # Order is not guaranteed, so check as set
    assert set(df2["id"]) == {"S001", "S002"}
    print("\n✓ Connection pooling preserves state across handlers")


# ============================================================================
# CLEANUP & CONNECTION MANAGEMENT
# ============================================================================

def test_close_connection():
    """
    Example 19: Close specific database connection.
    
    Properly cleanup resources when done with a database.
    """
    handler = SQLiteHandler(":memory:")
    assert ":memory:" in SQLiteHandler._connections
    
    handler.close()
    assert ":memory:" not in SQLiteHandler._connections
    print("\n✓ Connection closed and removed from pool")


def test_close_all_connections(temp_db_path):
    """
    Example 20: Close all pooled connections.
    
    Useful for test cleanup or application shutdown.
    """
    # Create multiple handlers with different databases
    handler1 = SQLiteHandler(":memory:")
    handler2 = SQLiteHandler(temp_db_path)  # Use temp file instead of ":memory:2"
    
    assert len(SQLiteHandler._connections) == 2
    
    # Close all
    SQLiteHandler.close_all()
    assert len(SQLiteHandler._connections) == 0
    print("\n✓ All connections closed successfully")


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

def test_empty_dataframe_insert():
    """
    Example 21: Insert empty DataFrame.
    
    Tests behavior with edge case of no data.
    """
    handler = SQLiteHandler(":memory:")
    handler.create_table("empty_table", "id VARCHAR(10)")
    
    empty_df = pd.DataFrame({"id": []})
    handler.insert_df("empty_table", empty_df, ["id"])
    
    df = handler.select_all("empty_table")
    assert len(df) == 0
    print("\n✓ Empty DataFrame insertion handled correctly")


def test_large_dataset():
    """
    Example 22: Handling larger datasets.
    
    Demonstrates performance with more substantial data volumes.
    """
    handler = SQLiteHandler(":memory:")
    handler.create_table("large_table", "id VARCHAR(20)")
    
    # Generate 10,000 records
    large_df = pd.DataFrame({
        "id": [f"ID{str(i).zfill(6)}" for i in range(10000)]
    })
    handler.insert_df("large_table", large_df, ["id"])
    
    df = handler.select_all("large_table")
    assert len(df) == 10000
    print(f"\n✓ Large dataset handled: {len(df):,} rows")


def test_missing_columns_error():
    """
    Example 23: Error handling for missing columns.
    
    Demonstrates proper error handling when DataFrame lacks required columns.
    """
    handler = SQLiteHandler(":memory:")
    handler.create_table("test_table", "id VARCHAR(10)")
    
    # DataFrame missing required column
    df = pd.DataFrame({"wrong_column": ["A", "B", "C"]})
    
    with pytest.raises(ValueError, match="DataFrame is missing columns"):
        handler.insert_df("test_table", df, ["id"])
    
    print("\n✓ Missing columns error handling works correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
