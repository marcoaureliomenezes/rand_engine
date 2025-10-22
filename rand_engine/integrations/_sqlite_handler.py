"""
SQLite Handler - Database operations with connection pooling
Maintains shared connections to avoid losing state in :memory: databases.
Provides the same interface as DuckDBHandler for consistency.
"""
import sqlite3
import pandas as pd
from typing import Dict, List, Optional
from ._base_handler import BaseDBHandler
from rand_engine.utils.logger import get_logger

logger = get_logger(__name__)


class SQLiteHandler(BaseDBHandler):
    """
    SQLite Handler with connection pooling.
    Maintains shared connections per db_path to preserve state.
    
    For :memory: databases, all instances share the same connection.
    For file-based databases, connections are reused per path.
    """
    
    # Class-level connection pool
    _connections: Dict[str, sqlite3.Connection] = {}

    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize SQLite handler with connection pooling.
        
        Args:
            db_path: Path to database file. Use ':memory:' for in-memory database.
                     All handlers with the same db_path share the same connection.
        """
        super().__init__(db_path)
        
        # Reuse existing connection or create new one
        if db_path not in self._connections:
            self._connections[db_path] = sqlite3.connect(db_path, check_same_thread=False)
            logger.info(f"Created new connection to SQLite database: {db_path}")
        else:
            logger.info(f"Reusing existing connection to SQLite database: {db_path}")
        
        self.conn = self._connections[db_path]


    def create_table(self, table_name: str, pk_def: str):
        """Create table with primary key definition. Creates if not exists."""
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {pk_def} PRIMARY KEY
        )
        """
        self.conn.execute(query)
        self.conn.commit()


    def insert_df(self, table_name: str, df: pd.DataFrame, pk_cols: List[str]):
        """
        Insert DataFrame into table, ignoring duplicate primary keys.
        
        Args:
            table_name: Target table name
            df: Pandas DataFrame to insert
            pk_cols: List of primary key column names
        """
        # Validate table_name to prevent SQL injection
        if not table_name.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {table_name}")
        
        # Validate DataFrame has required columns
        missing_cols = set(pk_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"DataFrame is missing columns: {missing_cols}")
        
        df_to_insert = df[pk_cols].copy()
        columns_str = ", ".join(pk_cols)
        placeholders = ", ".join(["?"] * len(pk_cols))
        query = f"INSERT OR IGNORE INTO {table_name} ({columns_str}) VALUES ({placeholders})"  # nosec B608
        records = [tuple(row) for row in df_to_insert.values]
        self.conn.executemany(query, records)
        self.conn.commit()


    def select_all(self, table_name: str, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Select data from table.
        
        Args:
            table_name: Name of the table to query
            columns: Optional list of columns to select. If None, select all columns.
            
        Returns:
            DataFrame with query results
        """
        # Validate table_name to prevent SQL injection
        if not table_name.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {table_name}")
        
        if columns:
            columns_str = ", ".join(columns)
            query = f"SELECT {columns_str} FROM {table_name}"  # nosec B608
        else:
            query = f"SELECT * FROM {table_name}"  # nosec B608
        
        df = pd.read_sql(query, self.conn)
        return df


    def drop_table(self, table_name: str):
        """Drop table if exists."""
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.conn.execute(query)
        self.conn.commit()


    def close(self):
        """
        Close database connection and remove from pool.
        Note: This closes the connection for ALL handlers using the same db_path.
        """
        if self.db_path in self._connections:
            self._connections[self.db_path].close()
            del self._connections[self.db_path]
            logger.info(f"Database connection closed and removed from pool: {self.db_path}")


    @classmethod
    def close_all(cls):
        """Close all pooled connections. Useful for cleanup in tests."""
        for db_path, conn in cls._connections.items():
            conn.close()
            logger.debug(f"Closed connection: {db_path}")
        cls._connections.clear()
        logger.info("All SQLite connections closed")


if __name__ == "__main__":
    pass