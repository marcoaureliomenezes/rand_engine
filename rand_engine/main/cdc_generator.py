import time
from uuid import uuid4
from datetime import datetime as dt
from random import randint
from typing import List

import pandas as pd
from pandas import DataFrame as PandasDF

from rand_engine.main.i_random_spec import IRandomSpec
from rand_engine.main.data_generator import RandGenerator
from rand_engine.file_handlers.fs_utils import FSUtils, DBFSUtils

from pyspark.sql.functions import coalesce



class FilesGenerator:

  def __init__(self, footprint: IRandomSpec, fs_utils: FSUtils=DBFSUtils()):
    self.footprint = footprint
    self.fs_utils = fs_utils
    self.min_secs, self.max_secs = 10, 20
    self.base_path, self.file_name, self.ext = None, None, None 


  def setup_output(self, base_path: str, file_name: str, ext: str):
    self.base_path = f"{base_path}/{file_name}/{ext}"
    self.file_name = file_name
    self.ext = ext
    return self


  def _get_file_path(self) -> str:
    return f"{self.base_path}/{self.file_name}_{str(uuid4())[:8]}.{self.ext}"
  
  
  def generate_sample(self, size: int=100) -> PandasDF:
    return (
      RandGenerator(self.footprint.metadata())
        .generate_pandas_df(size, transformer=self.footprint.transformer())
        .get_df()
    )

  def list_files(self):
    assert self.base_path, "Base path not configured. Run the method setup_output."
    return self.fs_utils.ls(self.base_path)
    

  def delete_files(self):
    assert self.base_path, "Base path not configured. Run the method setup_output."
    self.fs_utils.rm(self.base_path, recursive=True)

 
  def write_file(self, size: int=100, const_cols={}):
    file_path = self._get_file_path()
    _ = (
      RandGenerator(self.footprint.metadata()) \
        .generate_pandas_df(size, transformer=self.footprint.transformer(**const_cols))
        .write() \
        .mode("overwrite") \
        .format(f"{self.ext}") \
        .option("compression", None) \
        .load(file_path))
    print(f"File {file_path} created with {size} records.")


  def stream_files(self, size=100, period=10, rounds=10):
    for i in range(rounds):
      self.write_file(size)
      time.sleep(period)




class CDCGenerator(FilesGenerator):

  def __init__(self, spark, footprint: IRandomSpec, pk_cols: List=[], fs_utils: FSUtils=DBFSUtils(), ):
    self.spark = spark
    self.footprint = footprint
    self.fs_utils = fs_utils
    self.pk_cols = pk_cols
    self.cdc_props = self.default_cdc_properties()

  def default_cdc_properties(self):
    return {
      "INSERT": dict(min_size=100, max_size=200),
      "UPDATE":dict(sample_rate=0.3, null_rate=0.9),
      "DELETE": dict(sample_rate=0.1)
    }

  def set_cdc_properties(self, cdc_properties):
    self.cdc_props = cdc_properties
    return self


  def calculate_rows_to_change(self, sample):
    df = self.spark.read.format(self.ext).load(self.base_path).filter(coalesce(*self.pk_cols).isNotNull())
    df_ids_inserted = df.select(*self.pk_cols).filter("operation = 'INSERT'").distinct()
    df_ids_deleted = df.select(*self.pk_cols).filter("operation = 'DELETE'").distinct()
    df_pks_to_change = df_ids_inserted.join(df_ids_deleted, on=self.pk_cols, how="leftanti")
    df_pks_to_change = df_pks_to_change.sample(sample).toPandas()
    return df_pks_to_change


  def generate_changes(self, sample, const_cols, null_rate):
    df_pks_to_change = self.calculate_rows_to_change(sample=sample)
    metadata = self.footprint.metadata()
    size = df_pks_to_change.shape[0]
    transformer = self.footprint.transformer_cdc_update(null_rate=null_rate, **const_cols)
    df_data = RandGenerator(metadata).generate_pandas_df(size, transformer).get_df()
    for coluna in self.pk_cols: df_data[coluna] = df_pks_to_change[coluna]
    if null_rate != 1: 
      cols_to_check = [col for col in df_data.columns if col not in self.pk_cols + list(const_cols.keys())]
      mask = ~df_data[cols_to_check].isnull().all(axis=1)
      df_data = df_data[mask]
    return df_data


  def generate_inserts(self):
    const_cols={"operation": "INSERT", "updated_at": dt.now().strftime("%Y-%m-%dT%H:%M:%S")}
    insert_conf = self.cdc_props["INSERT"]
    rand_size = randint(insert_conf["min_size"], insert_conf["max_size"])
    self.write_file(size=rand_size, const_cols=const_cols)


  def generate_cdc(self):
    self.generate_inserts()
    update_conf = self.cdc_props["UPDATE"]
    delete_conf = self.cdc_props["DELETE"]
    update_const_cols ={"operation": "UPDATE", "updated_at": dt.now().strftime("%Y-%m-%dT%H:%M:%S")}
    delete_const_cols ={"operation": "DELETE", "updated_at": dt.now().strftime("%Y-%m-%dT%H:%M:%S")}
    df_update = self.generate_changes(update_conf["sample_rate"], update_const_cols, update_conf["null_rate"])
    df_delete = self.generate_changes(delete_conf["sample_rate"], delete_const_cols, 1)
    df_changes = pd.concat([df_update, df_delete], ignore_index=True)
    file_path = self._get_file_path()
    df_changes.to_json(file_path, orient="records", lines=True)
    print(f"File {file_path} created with {df_changes.shape[0]} records.")

  def generate_cdc_stream(self, period=5, rounds=15):
    for i in range(rounds):
      self.generate_cdc()
      time.sleep(period)