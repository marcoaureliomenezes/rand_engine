import faker
from datetime import datetime as dt, timedelta
import random
import time




class ProductCategory:
  
  
  def __init__(self):
    self.faker = faker.Faker(locale="pt_BR")


  def metadata_category(self):
    return lambda: {
      "category_id":  dict(
        method="unique_ids",
        kwargs=dict(strategy="zint", length=4)),
      "constraints": {
          "category_pk": dict(
            name="category_pk",
            tipo="PK",
            fields=["category_id VARCHAR(4)"])
        }
    }


  def transformer_category(self, **kwargs):
    max_delay = kwargs.get("max_delay", 100)
    return [
      lambda df: df.assign(name=df.index.map(lambda idx: f"cat_name_{str(idx).zfill(4)}")),
      lambda df: df.assign(created_at=df["category_id"].apply(
        lambda x: dt.now() - timedelta(seconds=random.randint(0, max_delay))))]
  
  
  def metadata_products(self):
    return lambda: {
      "product_id":       dict(method="unique_ids", kwargs=dict(strategy="zint", length=8)),
      "price":            dict(method="floats_normal", kwargs=dict(mean=50, std=10**1, round=2)),
      "constraints": {
        "category_fk": dict(
          name="category_pk",
          tipo="FK",
          fields=["category_id"],
          watermark=2
        )
      }
    }
  


class ClientsProductsCategoriesTransactions:
  
  
  def __init__(self):
    self.faker = faker.Faker(locale="pt_BR")


  def metadata_category(self):
    return lambda: {
      "category_id":  dict(
        method="unique_ids",
        kwargs=dict(strategy="zint", length=4)),
      "constraints": {
          "categories_pk": dict(
            name="categories_pk",
            tipo="PK",
            fields=["category_id VARCHAR(4)"])
        }
    }


  def transformer_category(self, **kwargs):
    max_delay = kwargs.get("max_delay", 100)
    return [
      lambda df: df.assign(name=df.index.map(lambda idx: f"cat_name_{str(idx).zfill(4)}")),
      lambda df: df.assign(created_at=df["category_id"].apply(
        lambda x: dt.now() - timedelta(seconds=random.randint(0, max_delay))))]
  
  
  def metadata_products(self):
    return lambda: {
      "product_id":       dict(method="unique_ids", kwargs=dict(strategy="zint", length=8)),
      "price":            dict(method="floats_normal", kwargs=dict(mean=50, std=10**1, round=2)),
      "constraints": {
        "products_pk": dict(
          name="products_pk",
          tipo="PK",
          fields=["product_id VARCHAR(8)"]
        ),
        "categories_fk": dict(
          name="categories_pk",
          tipo="FK",
          fields=["category_id"],
          watermark=60
        )
      }
    }


  def metadata_clients(self):
    return lambda: {
      "client_id":  dict(method="unique_ids", kwargs=dict(strategy="zint", length=8)),
      "tp_pes":  dict(method="distincts", kwargs=dict(distincts=["PF", "PJ"])),
      "constraints": {
        "clients_pk": dict(
          name="clients_pk",
          tipo="PK",
          fields=["client_id VARCHAR(8)", "tp_pes VARCHAR(2)"]
        )
      }
    }


  def transformer_client(self, **kwargs):
    max_delay = kwargs.get("max_delay", 1)
    return [
      lambda df: df.assign(creation_time=df["client_id"].apply(
        lambda x: int(time.time()) - random.randint(0, max_delay)))
    ]

      
  def metadata_transactions(self):
    return lambda: {
      "transaction_id":   dict(method="unique_ids", kwargs=dict(strategy="zint", length=8)),
      "price":            dict(method="floats_normal", kwargs=dict(mean=50, std=10**1, round=2)),
      "amount":           dict(method="integers", kwargs=dict(min=1, max=100)),
      "constraints": {
        "clients_fk": dict(
          name="clients_pk",
          tipo="FK",
          fields=["client_id", "tp_pes"],
          watermark=60,
        ),
        "products_fk": dict(
          name="products_pk",
          tipo="FK",
          fields=["product_id"],
          watermark=60
        )
      }
    }
  
  