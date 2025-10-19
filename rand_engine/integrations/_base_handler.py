"""
Base Database Handler - Abstract base class for database operations
Defines common interface for DuckDB, SQLite, and other database handlers.
"""
from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Optional


class BaseDBHandler(ABC):
    """
    Abstract base class for database handlers.
    
    All database handlers (DuckDB, SQLite, etc.) should implement this interface
    to ensure consistency across different database backends.
    """
    
    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize database handler.
        
        Args:
            db_path: Path to database file. Use ':memory:' for in-memory database.
        """
        self.db_path = db_path
    
    @abstractmethod
    def create_table(self, table_name: str, pk_def: str):
        """
        Create table with primary key definition.
        
        Args:
            table_name: Name of the table to create
            pk_def: Primary key definition (e.g., "id VARCHAR(10)")
        """
        pass
    
    @abstractmethod
    def insert_df(self, table_name: str, df: pd.DataFrame, pk_cols: List[str]):
        """
        Insert DataFrame into table, ignoring duplicate primary keys.
        
        Args:
            table_name: Target table name
            df: Pandas DataFrame to insert
            pk_cols: List of primary key column names
        """
        pass
    
    @abstractmethod
    def select_all(self, table_name: str, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Select data from table.
        
        Args:
            table_name: Name of the table to query
            columns: Optional list of columns to select. If None, select all columns.
            
        Returns:
            DataFrame with query results
        """
        pass
    
    @abstractmethod
    def drop_table(self, table_name: str):
        """
        Drop table if exists.
        
        Args:
            table_name: Name of the table to drop
        """
        pass
    
    @abstractmethod
    def close(self):
        """
        Close database connection and cleanup resources.
        """
        pass
