import random
import pytest
from rand_engine.templates.web_server_logs import WebServerLogs, Changer



@pytest.fixture(scope="module")
def web_server_logs():
  return WebServerLogs()




@pytest.fixture(scope="function")
def update_transformer():
  transformer = Changer(cols_to_change=["campo_float", "campo_int"]).updater
  return transformer


import faker
from datetime import datetime as dt, timedelta


class Ecommerce:
  
  
  def __init__(self):
    self.faker = faker.Faker(locale="pt_BR")
    self.db_path = ":memory:"

  def metadata_category(self):
    return lambda: {
      "category_id":  dict(
        method="unique_ids",
        kwargs=dict(strategy="zint", length=4),
        pk=dict(name="categories", datatype="VARCHAR(4)", checkpoint=self.db_path))
    }


  def transformer_category(self, **kwargs):
    max_delay = kwargs.get("max_delay", 100)
    return [
      lambda df: df.assign(name=df.index.map(lambda idx: f"cat_name_{str(idx).zfill(4)}")),
      lambda df: df.assign(created_at=df["category_id"].apply(
        lambda x: dt.now() - timedelta(seconds=random.randint(0, max_delay))))
    ]
  

  def metadata_client(self):
    return lambda: {
      "client_id":  dict(
        method="unique_ids",
        kwargs=dict(strategy="zint", length=8),
        pk=dict(name="clients", datatype="VARCHAR(8)", checkpoint=self.db_path)), 
    }
  
  
  def metadata_products(self):
    return lambda: {
      "product_id":       dict(method="unique_ids", kwargs=dict(strategy="zint", length=8)),
      "price":            dict(method="floats_normal", kwargs=dict(mean=50, std=10**1, round=2)),
      "category_id":      dict(
        method="distincts_external",
        kwargs=dict(table="categories", pk_fields=["category_id"], db_path=self.db_path)
      ),
      "client_id":      dict(
        method="distincts_external",
        kwargs=dict(table="clients", pk_fields=["client_id"], db_path=self.db_path)
      )
    }