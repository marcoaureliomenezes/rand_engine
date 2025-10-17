"""
SQLite Handler - Database operations with pandas integration
Demonstrates basic CRUD operations with SQLite database and pandas DataFrames.
"""
import sqlite3
import pandas as pd
from typing import List, Tuple, Optional


class SQLiteHandler:
    """
    SQLite Handler with pandas integration.
    Provides the same interface as DuckDBHandler for consistency.
    """

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        print(f"✓ Connected to SQLite database: {db_path}")


    def create_table(self, table_name: str, pk_def: str):
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {pk_def} PRIMARY KEY
        )
        """
        self.cursor.execute(query)
        self.conn.commit()
        print(f"✓ Table '{table_name}' created successfully")


    def insert_df(self, table_name: str, df: pd.DataFrame, pk_cols: List[str]):
        # Validar que o DataFrame tem as colunas necessárias
        missing_cols = set(pk_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"DataFrame is missing columns: {missing_cols}")
  
        df_to_insert = df[pk_cols].copy()
        columns_str = ", ".join(pk_cols)
        placeholders = ", ".join(["?"] * len(pk_cols))
        query = f"INSERT OR IGNORE INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        records = [tuple(row) for row in df_to_insert.values]
        self.cursor.executemany(query, records)
        self.conn.commit()
        print(f"✓ Inserted DataFrame into '{table_name}' (duplicates ignored)")



    def select_all(self, table_name: str, columns: Optional[List[str]] = None) -> pd.DataFrame:
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
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.cursor.execute(query)
        self.conn.commit()
        print(f"✓ Table '{table_name}' dropped successfully")



    def close(self):
        """Close database connection."""
        self.conn.close()
        print("✓ Database connection closed")