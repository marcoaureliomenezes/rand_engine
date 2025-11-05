import time
from typing import Optional, List, Dict
from rand_engine.integrations._base_handler import BaseDBHandler
from rand_engine.core._py_core import PyCore
from rand_engine.utils.logger import get_logger

logger = get_logger(__name__)


class ConstraintsHandler:
  """
  Handles PK/FK constraints with automatic checkpoint cleanup.
  
  Manages checkpoint tables to ensure data consistency while preventing
  memory overflow by automatically cleaning up old records.
  """

  def __init__(self, db_conn: BaseDBHandler, retention_period: int = 300):
    """
    Initialize ConstraintsHandler.
    
    Args:
        db_conn: Database handler instance (DuckDB or SQLite)
        retention_period: Time in seconds to keep old checkpoints (default: 300s = 5 minutes)
    """
    self.db_conn = db_conn
    self.retention_period = retention_period



  def cleanup_old_checkpoints(self, table_name: str, watermark: int) -> None:
    """
    Delete checkpoint records older than watermark + retention_period.
    
    Args:
        table_name: Name of the checkpoint table
        watermark: Time window in seconds (from constraints config)
    """
    cutoff_time = int(time.time()) - watermark - self.retention_period
    delete_query = f"DELETE FROM {table_name} WHERE creation_time < {cutoff_time}"
    self.db_conn.conn.execute(delete_query)

  def handle_primary_keys(self, dataframe, table_name, fields, watermark=0):
    """Handle primary key constraints with automatic cleanup."""
    dataframe = dataframe.copy()
    constraints_list = [*fields, "creation_time BIGINT"]
    constraints_fields = [s.split(" ")[0] for s in constraints_list]
    constraints_str = ",".join(constraints_list)
    self.db_conn.create_table(table_name, pk_def=constraints_str)
    if "creation_time" not in dataframe.columns:
      dataframe['creation_time'] = int(time.time())
    self.db_conn.insert_df(table_name, dataframe, pk_cols=constraints_fields)
    
    # Cleanup old records to prevent memory overflow
    self.cleanup_old_checkpoints(table_name, watermark)
    return True


  def handle_foreign_keys(self, dataframe, table_name, fields, watermark):
    now = int(time.time())
    cols_pk = ", ".join(fields)
    query = f"SELECT {cols_pk} FROM {table_name} WHERE creation_time >= {now} - {watermark}"
  
    df_2 = self.db_conn.query_with_pandas(query)
    result = PyCore.gen_distincts_untyped(dataframe.shape[0], df_2.values.tolist())
    dataframe[fields] = result
    return dataframe


  def generate_consistency(self, dataframe, constraints):
    for _, v in constraints.items():
      if v["tipo"] == "PK":
        table_name = f"checkpoint_{v['name']}"
        fields = v["fields"]
        watermark = v.get("watermark", 0)
        self.handle_primary_keys(dataframe, table_name, fields, watermark)
      if v["tipo"] == "FK":
        table_name = f"checkpoint_{v['name']}"
        fields = v["fields"]
        watermark = v.get("watermark", 10)
        dataframe = self.handle_foreign_keys(dataframe, table_name, fields, watermark)
    return dataframe
  


  def delete_state(self):
    # Deletes all checkpoint tables from the database
    tables = self.db_conn.list_tables()
    for table in tables:
      if table.startswith("checkpoint_"):
        self.db_conn.drop_table(table)
    return True