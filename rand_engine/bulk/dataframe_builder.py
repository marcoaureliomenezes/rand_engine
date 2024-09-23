import pandas as pd


class BulkRandEngine:
    
  def handle_distincts_paired(self, distincts, sep):
    return [f"{j}{sep}{i}" for j in distincts for i in distincts[j]]

  def handle_relationships(self, distincts, sep=""):
    return [f"{j}{sep}{i}" for j in distincts for i in distincts[j]]

  def handle_distincts_proportions(self, distinct_prop, precision):
    return [ key for key, value in distinct_prop.items() for i in range(value * precision )]

  def handle_distincts_multicolumn(self, distincts, **kwargs):
    return [f"{j}{kwargs.get('sep', '')}{i}" for j in distincts for i in distincts[j]]


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

  


