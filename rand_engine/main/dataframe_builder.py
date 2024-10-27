import pandas as pd


class BulkRandEngine:
      
  def handle_splitable(self, metadata, df):
    for key, value in metadata.items():
      if value.get("splitable"):
        sep = value.get("sep", ";")
        cols = value.get("cols")
        df[cols] = df[key].str.split(sep, expand=True)
        df.drop(columns=[key], inplace=True)
    return df

  def create_pandas_df(self, size, metadata):
    df_pandas = pd.DataFrame({key: value["method"](size, **value["parms"]) for key, value in metadata.items()})
    df_pandas = self.handle_splitable(metadata, df_pandas)
    return df_pandas
  
  def create_spark_df(self, spark, size, metadata):
    df_pandas = self.create_pandas_df(size, metadata)
    df_spark = spark.createDataFrame(df_pandas)
    return df_spark


if __name__ == '__main__':
  pass

  # from core.core_distincts import CoreDistincts

  # bulk_engine = BulkRandEngine()

  # distinct_prop = {"MEI": 6,"ME":3, "EPP": 1}
  # print(bulk_engine.handle_distincts_lvl_1(distinct_prop, 1))


  # distinct = {"OPC": ["C_OPC","V_OPC"], "SWP": ["C_SWP", "V_SWP"]}
  # print(bulk_engine.handle_distincts_lvl_2(distinct, sep=";"))

  # distinct_2 = {"OPC": [("C_OPC", 8),("V_OPC", 2)], "SWP": [("C_SWP", 6), ("V_SWP", 4)]}
  # print(bulk_engine.handle_distincts_lvl_3(distinct_2, sep=";"))

  # metadata = {
  #   "tipo_categoria": dict(
  #     method=CoreDistincts.gen_distincts_typed,
  #     splitable=True,
  #     cols=["categoria_produto", "tipo_produto"],
  #     sep=";",
  #     parms=dict(distinct=bulk_engine.handle_distincts_lvl_3(distinct_2, sep=";"))
  #   )
  # }
  # df = bulk_engine.create_pandas_df(10**7, metadata)
  # print(df)

  

