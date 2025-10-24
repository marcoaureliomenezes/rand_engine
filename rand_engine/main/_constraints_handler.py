import time
from rand_engine.integrations._duckdb_handler import DuckDBHandler
from rand_engine.core._py_core import PyCore


class ConstraintsHandler:


  def __init__(self, db_path):
    self.db_conn = DuckDBHandler(db_path=db_path)



  def handle_pks(self, dataframe, table_name, fields):
    dataframe = dataframe.copy()
    constraints_list = [*fields, "creation_time BIGINT"]
    constraints_fields = [s.split(" ")[0] for s in constraints_list]
    constraints_str = ",".join(constraints_list)
    self.db_conn.create_table(table_name, pk_def=constraints_str)
    if "creation_time" not in dataframe.columns:
      dataframe['creation_time'] = int(time.time())
    self.db_conn.insert_df(table_name, dataframe, pk_cols=constraints_fields)
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
        self.handle_pks(dataframe, table_name, fields)
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