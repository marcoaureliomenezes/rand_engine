"""
DuckDB Handler - Database operations with connection pooling
Maintains shared connections to avoid losing state in :memory: databases.
"""
import pandas as pd
import duckdb
from typing import Dict, List, Optional
from ._base_handler import BaseDBHandler
from rand_engine.utils.logger import get_logger

logger = get_logger(__name__)


class DuckDBHandler(BaseDBHandler):
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
        super().__init__(db_path)
        
        # Reutiliza conexão existente ou cria nova
        if db_path not in self._connections:
            self._connections[db_path] = duckdb.connect(db_path)
            logger.info(f"Created new connection to DuckDB database: {db_path}")
        else:
            logger.info(f"Reusing existing connection to DuckDB database: {db_path}")
        
        self.conn = self._connections[db_path]


    def list_tables(self) -> List[str]:
        """List all tables in the database."""
        query = "SHOW TABLES"
        result = self.conn.execute(query).fetchall()
        return [row[0] for row in result]

    def create_table(self, table_name: str, pk_def: str):
        cols_pk = ",".join([col.split()[0] for col in pk_def.split(',')])
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {pk_def}, PRIMARY KEY ({cols_pk}) )"""
        self.conn.execute(query)


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
        
        columns = ", ".join(pk_cols)
        query = f"INSERT OR IGNORE INTO {table_name} SELECT {columns} FROM df"  # nosec B608
        self.conn.execute(query)



    def select_all(self, table_name: str, columns: Optional[List[str]] = None) -> pd.DataFrame:
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

    def query_with_pandas(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
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
            logger.info(f"Database connection closed and removed from pool: {self.db_path}")


    @classmethod
    def close_all(cls):
        """Close all pooled connections. Useful for cleanup in tests."""
        for db_path, conn in cls._connections.items():
            conn.close()
            logger.debug(f"Closed connection: {db_path}")
        cls._connections.clear()
        logger.info("All DuckDB connections closed")


    def drop_table(self, table_name: str):
        """Drop table if exists."""
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.conn.execute(query)



if __name__ == "__main__":
    pass
