"""
DuckDB POC - Proof of Concept
Demonstrates basic CRUD operations with DuckDB database.
"""
import pandas as pd
import duckdb
from typing import List, Tuple


class DuckDBHandler:
    """
    Simple POC for DuckDB operations.
    Demonstrates CREATE, INSERT, SELECT, UPDATE, DELETE operations.
    """

    def __init__(self, db_path: str = ":memory:"):

        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        print(f"✓ Connected to DuckDB database: {db_path}")


    def create_table(self, table_name, pk_def):
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {pk_def} PRIMARY KEY)"""
        self.conn.execute(query)
        print(f"✓ Table '{table_name}' created successfully")


    def insert_df(self, table_name, df, pk_cols):
        # DuckDB pode ler diretamente de DataFrames pandas
        # INSERT OR IGNORE automaticamente ignora duplicatas
        columns = ", ".join(pk_cols)
        query = f"INSERT OR IGNORE INTO {table_name} SELECT {columns} FROM df"
        self.conn.execute(query)
        print(f"✓ Inserted DataFrame into '{table_name}' (duplicates ignored)")



    def select_all(self, table_name, columns=None) -> pd.DataFrame:
        if columns:
            columns_str = ", ".join(columns)
            query = f"SELECT {columns_str} FROM {table_name}"
        else:
            query = f"SELECT * FROM {table_name}"
        
        # DuckDB pode retornar diretamente um pandas DataFrame
        df = self.conn.execute(query).df()
        print(df)
        return df


    def close(self):
        """Close database connection."""
        self.conn.close()
        print("✓ Database connection closed")


    def drop_table(self, table_name):
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.conn.execute(query)
        print(f"✓ Table '{table_name}' dropped successfully")

def run_poc():
  """Run the complete DuckDB POC demonstration."""
  # Initialize database
  db = DuckDBHandler(db_path="clientes_ddb.db")

  table_name = "checkpoint_category_ids"
  col_id_name = "category_ids"
  
  try:
      # 1. Create table
      print("1. Creating table...")
      db.create_table(table_name, pk_def="category_ids VARCHAR(16)")
      print()

      # 2. Insert usando DataFrame (primeira vez)
      print("2. Inserting DataFrame (first batch - 5 records)...")
      df1 = pd.DataFrame({
          col_id_name: ["cat_1", "cat_2", "cat_3", "cat_4", "cat_576"]
      })
      db.insert_df(table_name, df1, [col_id_name])
      print()

      # 3. Select all records
      print("3. Selecting all records after first insert...")
      df = db.select_all(table_name, [col_id_name])
      print(df)


  except Exception as e:
      print(f"Error: {e}")
      import traceback
      traceback.print_exc()
  finally:
      db.close()

if __name__ == "__main__":
    run_poc()
