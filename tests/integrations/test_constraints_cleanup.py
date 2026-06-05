"""
Tests for ConstraintsHandler automatic checkpoint cleanup.

Verifies that old checkpoint records are automatically deleted
to prevent memory overflow in :memory: databases.
"""
import pytest
import pandas as pd
import time
from rand_engine.integrations._duckdb_handler import DuckDBHandler
from rand_engine.integrations._sqlite_handler import SQLiteHandler
from rand_engine.main._constraints_handler import ConstraintsHandler


@pytest.fixture
def sample_df():
    """Sample DataFrame with PK columns."""
    return pd.DataFrame({
        'id': ['A', 'B', 'C'],
        'name': ['Alice', 'Bob', 'Charlie']
    })


@pytest.fixture(params=['duckdb', 'sqlite'])
def db_handler(request):
    """Parametrized fixture for both database handlers."""
    if request.param == 'duckdb':
        return DuckDBHandler(":memory:")
    return SQLiteHandler(":memory:")


class TestCheckpointCleanup:
    """Test automatic cleanup of old checkpoint records."""

    def test_cleanup_deletes_old_records(self, db_handler):
        """Test that records older than retention period are deleted."""
        handler = ConstraintsHandler(db_handler, retention_period=5)
        
        checkpoint_table = "checkpoint_test_table"
        pk_def = "id TEXT, creation_time BIGINT"
        db_handler.create_table(checkpoint_table, pk_def)
        
        # Insert old record (11 seconds ago) and recent record (1 second ago)
        old_time = int(time.time()) - 11
        recent_time = int(time.time()) - 1
        df = pd.DataFrame({
            'id': ['OLD', 'RECENT'],
            'creation_time': [old_time, recent_time]
        })
        db_handler.insert_df(checkpoint_table, df, pk_cols=['id', 'creation_time'])
        
        # Run cleanup with watermark of 5 seconds
        handler.cleanup_old_checkpoints(checkpoint_table, watermark=5)
        
        # Verify only recent record remains
        remaining = db_handler.query_with_pandas(f"SELECT * FROM {checkpoint_table}")
        assert len(remaining) == 1
        assert remaining['id'].iloc[0] == 'RECENT'

    def test_cleanup_preserves_recent_records(self, db_handler):
        """Test that records within retention period are preserved."""
        handler = ConstraintsHandler(db_handler, retention_period=300)
        
        checkpoint_table = "checkpoint_preserve_test"
        pk_def = "id TEXT, creation_time BIGINT"
        db_handler.create_table(checkpoint_table, pk_def)
        
        # Insert records from last 10 seconds
        recent_times = [int(time.time()) - i for i in range(5)]
        df = pd.DataFrame({
            'id': [f'ID_{i}' for i in range(5)],
            'creation_time': recent_times
        })
        db_handler.insert_df(checkpoint_table, df, pk_cols=['id', 'creation_time'])
        
        # Run cleanup with watermark of 60 seconds
        handler.cleanup_old_checkpoints(checkpoint_table, watermark=60)
        
        # All records should be preserved
        remaining = db_handler.query_with_pandas(f"SELECT * FROM {checkpoint_table}")
        assert len(remaining) == 5

    def test_handle_primary_keys_triggers_automatic_cleanup(self, db_handler, sample_df):
        """Test that handle_primary_keys() automatically calls cleanup."""
        handler = ConstraintsHandler(db_handler, retention_period=5)
        
        checkpoint_table = "checkpoint_products"
        pk_def = "id TEXT, creation_time BIGINT"
        db_handler.create_table(checkpoint_table, pk_def)
        
        # Manually insert old record
        old_time = int(time.time()) - 20
        old_df = pd.DataFrame({'id': ['OLD_RECORD'], 'creation_time': [old_time]})
        db_handler.insert_df(checkpoint_table, old_df, pk_cols=['id', 'creation_time'])
        
        # Call handle_primary_keys (should insert new + cleanup old)
        handler.handle_primary_keys(sample_df, table_name=checkpoint_table, fields=['id TEXT'], watermark=5)
        
        # Verify old record was cleaned up
        all_records = db_handler.query_with_pandas(f"SELECT * FROM {checkpoint_table}")
        assert len(all_records) == 3
        assert 'OLD_RECORD' not in all_records['id'].values


class TestConstraintsHandlerInitialization:
    """Test ConstraintsHandler initialization with retention_period."""

    def test_default_retention_period(self, db_handler):
        """Test that default retention period is 300 seconds."""
        handler = ConstraintsHandler(db_handler)
        assert handler.retention_period == 300

    def test_custom_retention_period(self, db_handler):
        """Test that custom retention period is set correctly."""
        handler = ConstraintsHandler(db_handler, retention_period=600)
        assert handler.retention_period == 600
