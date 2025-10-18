import sqlite3
from typing import Dict, List, Tuple
from datetime import datetime as dt    

from rand_engine.main.data_generator import DataGenerator
from rand_engine.utils.distincts_utils import DistinctsUtils

from rand_engine.core._np_core import Core
import faker
import random
from datetime import datetime as dt, timedelta
from rand_engine.integrations.duckdb_handler import DuckDBHandler

class Ecommerce:
  
  
  def __init__(self):
    self.faker = faker.Faker(locale="pt_BR")

  def metadata_category(self):
    return {
      "category_id":  dict(
        method=Core.gen_unique_identifiers,
        kwargs=dict(strategy="zint", length=4),
        pk=dict(name="categories", datatype="VARCHAR(4)")), 
    }

  def transformer_category(self, **kwargs):
    max_delay = kwargs.get("max_delay", 100)
    return [
      lambda df: df.assign(name=df.index.map(lambda idx: f"cat_name_{str(idx).zfill(4)}")),
      lambda df: df.assign(created_at=df["category_id"].apply(
        lambda x: dt.now() -timedelta(seconds=random.randint(0, max_delay))))
      ]
  

  def metadata_client(self):
    return {
      "client_id":  dict(
        method=Core.gen_unique_identifiers,
        kwargs=dict(strategy="zint", length=8),
        pk=dict(name="clients", datatype="VARCHAR(8)")), 
    }
  
  def metadata_products(self, **kwargs):
    return {
      "product_id":       dict(method=Core.gen_unique_identifiers, kwargs=dict(strategy="zint", length=8)),
      "price":            dict(method=Core.gen_floats_normal, kwargs=dict(mean=50, std=10**1, round=2)),
      "category_id":      dict(
        method=Core.gen_distincts,
        kwargs=dict(distinct=DistinctsUtils.handle_foreign_keys(table="categories", pk_fields=["category_id"]))),
      "client_id":      dict(
        method=Core.gen_distincts,
        kwargs=dict(distinct=DistinctsUtils.handle_foreign_keys(table="clients", pk_fields=["client_id"])))
      }


  def create_dataset(self, size=10**6):
    df_category = DataGenerator(self.metadata_category()).transformers(self.transformer_category()).size(10**1).get_df()
    print(df_category)
    df_client = DataGenerator(self.metadata_client()).size(10**2).get_df()
    print(df_client)

    print("PRODUCTS")
    df_products = DataGenerator(self.metadata_products()).size(10**2).get_df()
    print(df_products)


                               
generator = Ecommerce()
generator.create_dataset()
                                                                      

# def test_pandas_df_kwargs(df_size, rand_spec_case_1):
#   """
#   This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
#   using keyword arguments.
#   """
#   df_data = DataGenerator(rand_spec_case_1).size(df_size).get_df()
#   assert df_data.shape[0] == df_size








