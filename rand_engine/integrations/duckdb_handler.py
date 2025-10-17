"""
DuckDB Handler - Database operations with connection pooling
Maintains shared connections to avoid losing state in :memory: databases.
"""
import pandas as pd
import duckdb
from typing import Dict, Optional


class DuckDBHandler:
    """
    DuckDB Handler with connection pooling.
    Maintains shared connections per db_path to preserve state.
    
    For :memory: databases, all instances share the same connection.
    For file-based databases, connections are reused per path.
    """
    
    # Class-level connection pool
    _connections: Dict[str, duckdb.DuckDBPyConnection] = {}

    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize DuckDB handler with connection pooling.
        
        Args:
            db_path: Path to database file. Use ':memory:' for in-memory database.
                     All handlers with the same db_path share the same connection.
        """
        self.db_path = db_path
        
        # Reutiliza conexão existente ou cria nova
        if db_path not in self._connections:
            self._connections[db_path] = duckdb.connect(db_path)
            print(f"✓ Created new connection to DuckDB database: {db_path}")
        else:
            print(f"✓ Reusing existing connection to DuckDB database: {db_path}")
        
        self.conn = self._connections[db_path]


    def create_table(self, table_name, pk_def):
        """Create table with primary key definition. Creates if not exists."""
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {pk_def} PRIMARY KEY)"""
        self.conn.execute(query)


    def insert_df(self, table_name, df, pk_cols):
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
        
        columns = ", ".join(pk_cols)
        query = f"INSERT OR IGNORE INTO {table_name} SELECT {columns} FROM df"  # nosec B608
        self.conn.execute(query)



    def select_all(self, table_name, columns=None) -> pd.DataFrame:
        # Validate table_name to prevent SQL injection
        if not table_name.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {table_name}")
        
        if columns:
            columns_str = ", ".join(columns)
            query = f"SELECT {columns_str} FROM {table_name}"  # nosec B608
        else:
            query = f"SELECT * FROM {table_name}"  # nosec B608
        
        # DuckDB pode retornar diretamente um pandas DataFrame
        df = self.conn.execute(query).df()
        return df


    def close(self):
        """
        Close database connection and remove from pool.
        Note: This closes the connection for ALL handlers using the same db_path.
        """
        if self.db_path in self._connections:
            self._connections[self.db_path].close()
            del self._connections[self.db_path]
            print(f"✓ Database connection closed and removed from pool: {self.db_path}")


    @classmethod
    def close_all(cls):
        """Close all pooled connections. Useful for cleanup in tests."""
        for db_path, conn in cls._connections.items():
            conn.close()
            print(f"✓ Closed connection: {db_path}")
        cls._connections.clear()
        print("✓ All connections closed")


    def drop_table(self, table_name):
        """Drop table if exists."""
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.conn.execute(query)



if __name__ == "__main__":
    pass
