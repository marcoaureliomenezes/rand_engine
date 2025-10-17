import faker
from datetime import datetime as dt, timedelta
import random
from rand_engine.integrations.duckdb_handler import DuckDBHandler
from rand_engine.main.data_generator import DataGenerator
from rand_engine.utils.distincts_utils import DistinctsUtils

class Ecommerce:
  
  
  def __init__(self):
    self.faker = faker.Faker(locale="pt_BR")

  def metadata_category(self):
    return lambda: {
      "category_id":  dict(
        method="unique_ids",
        kwargs=dict(strategy="zint", length=4),
        pk=dict(name="categories", datatype="VARCHAR(4)", checkpoint=":memory:")), 
    }

  def transformer_category(self, **kwargs):
    max_delay = kwargs.get("max_delay", 100)
    return [
      lambda df: df.assign(name=df.index.map(lambda idx: f"cat_name_{str(idx).zfill(4)}")),
      lambda df: df.assign(created_at=df["category_id"].apply(
        lambda x: dt.now() -timedelta(seconds=random.randint(0, max_delay))))
      ]
  

  def metadata_client(self):
    return lambda: {
      "client_id":  dict(
        method="unique_ids",
        kwargs=dict(strategy="zint", length=8),
        pk=dict(name="clients", datatype="VARCHAR(8)", checkpoint=":memory:")), 
    }
  
  def metadata_products(self, **kwargs):
    return lambda: {
      "product_id":       dict(method="unique_ids", kwargs=dict(strategy="zint", length=8)),
      "price":            dict(method="floats_normal", kwargs=dict(mean=50, std=10**1, round=2)),
      "category_id":      dict(
        method="distincts",
        kwargs=dict(distincts=DistinctsUtils.handle_foreign_keys(table="categories", pk_fields=["category_id"], db_path=":memory:"))),
      "client_id":      dict(
        method="distincts",
        kwargs=dict(distincts=DistinctsUtils.handle_foreign_keys(table="clients", pk_fields=["client_id"], db_path=":memory:")))
      }
