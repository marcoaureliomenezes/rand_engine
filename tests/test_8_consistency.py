import pandas as pd
import time
import pytest
import logging
from rand_engine.main.data_generator import DataGenerator
from tests.fixtures.f3_data_generator_constraints import ProductCategory, ClientsProductsCategoriesTransactions


def configure_logger():
  logger = logging.getLogger("rand_engine")
  logger.setLevel(logging.INFO)
  logger.handlers.clear()
  console_handler = logging.StreamHandler()
  console_handler.setLevel(logging.INFO)
  formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)

  # Garantir que logs não sejam propagados para root logger
  logger.propagate = False


@pytest.mark.parametrize("size_clients, size_products",[
  (100, 1000),
  (100, 10000),
  (100, 100000),
  (100, 1000000)
])
def test_simple_two_relationship(size_clients, size_products):

  prod_cat = ProductCategory()
  df_category = (
    DataGenerator(prod_cat.metadata_category())
      .checkpoint(":memory:")
      .option("reset_checkpoint", True)
      .transformers(prod_cat.transformer_category())
      .size(size_clients).get_df()
  )

  df_products = DataGenerator(prod_cat.metadata_products()).size(size_products).get_df()
  df_category_pks = df_category[["category_id"]].drop_duplicates().values
  df_products_pks = df_products[["category_id"]].values
  is_valid = set(map(tuple, df_products_pks)).issubset(set(map(tuple, df_category_pks)))
  assert is_valid


@pytest.mark.parametrize("size_clients, size_products",[
  (100, 1000),
  (100, 10000),
  (100, 100000),
  (100, 1000000)
])
def test_simple_two_relationship_with_watermark(size_clients, size_products):

  prod_cat = ProductCategory()
  df_category_1 = (
    DataGenerator(prod_cat.metadata_category())
      .option("reset_checkpoint", True)
      .transformers(prod_cat.transformer_category())
      .size(size_clients).get_df())

  df_category_2 = (
    DataGenerator(prod_cat.metadata_category())
      .transformers(prod_cat.transformer_category())
      .size(size_clients).get_df()
  )

  df_category = pd.concat([df_category_1, df_category_2], ignore_index=True)
  df_products = DataGenerator(prod_cat.metadata_products()).size(size_products).get_df()
  df_category_pks = df_category[["category_id"]].drop_duplicates().values
  df_products_pks = df_products[["category_id"]].values
  is_valid = set(map(tuple, df_products_pks)).issubset(set(map(tuple, df_category_pks)))
  assert is_valid


@pytest.mark.parametrize("size_clients, size_products",[
  (100, 1000),
  (100, 10000),
  (100, 100000),
  (100, 1000000)
])
def test_simple_two_relationship_with_watermark_expires(size_clients, size_products):

  prod_cat = ProductCategory()
  df_category_1 = (
    DataGenerator(prod_cat.metadata_category())
      .option("reset_checkpoint", True)
      .transformers(prod_cat.transformer_category())
      .size(size_clients).get_df())

  time.sleep(3)
  df_category_2 = (
    DataGenerator(prod_cat.metadata_category())
      .transformers(prod_cat.transformer_category())
      .size(size_clients).get_df()
  )

  df_products = DataGenerator(prod_cat.metadata_products()).size(size_products).get_df()
  df_category_pks = df_category_2[["category_id"]].drop_duplicates().values
  df_products_pks = df_products[["category_id"]].values
  is_valid = set(map(tuple, df_products_pks)).issubset(set(map(tuple, df_category_pks)))
  assert is_valid

@pytest.mark.parametrize("size_clients, size_categories, size_products, size_transactions",[
  (10, 10, 10, 10),
  # (100, 100, 1000, 1000),
  # (100, 100, 10000, 10000),
  # (10000, 100, 100000, 1000000)
])
def test_four_relationships_consistency(size_clients, size_categories, size_products, size_transactions):
  cpc_tx = ClientsProductsCategoriesTransactions()
  
  df_category = (
    DataGenerator(cpc_tx.metadata_category())
      .transformers(cpc_tx.transformer_category())
      .checkpoint(":memory:")
      .option("reset_checkpoint", True)
      .size(size_categories).get_df()
  )
  
  df_products = DataGenerator(cpc_tx.metadata_products()).checkpoint(":memory:").size(size_products).get_df()
  df_clients = DataGenerator(cpc_tx.metadata_clients()).size(size_clients).get_df()
  df_transactions = DataGenerator(cpc_tx.metadata_transactions()).size(size_transactions).get_df()

  prod_cat_pks = df_products[["category_id"]].drop_duplicates().values
  category_pks = df_category[["category_id"]].values
  clients_pks = df_clients[["client_id"]].values
  products_pks = df_products[["product_id"]].drop_duplicates().values
  tx_prod_pks = df_transactions[["product_id"]].drop_duplicates().values
  tx_client_pks = df_transactions[["client_id"]].drop_duplicates().values
  
  assert set(map(tuple, prod_cat_pks)).issubset(set(map(tuple, category_pks)))
  assert set(map(tuple, tx_client_pks)).issubset(set(map(tuple, clients_pks)))
  assert set(map(tuple, tx_prod_pks)).issubset(set(map(tuple, products_pks)))


# @pytest.mark.parametrize("size_clients, size_txs",[
#   (10, 50),
#   (20, 100),
#   (50, 200)
# ])
# def test_simple_two_relationship_watermark(size_clients, size_txs): 
#   tx_clients = TransactionsClients()
#   df_clients= (
#     DataGenerator(tx_clients.metadata_client())
#       .checkpoint(":memory:")
#       .option("reset_checkpoint", True)
#       .transformers(tx_clients.transformer_client())
#       .size(size_clients).get_df())
#   df_txs = DataGenerator(tx_clients.metadata_transactions()).size(size_txs).get_df()
#   df_txs_pks = df_txs[["client_id", "tp_pes"]].drop_duplicates().values
#   df_clients_pks = df_clients[["client_id", "tp_pes"]].values
#   assert set(map(tuple, df_txs_pks)).issubset(set(map(tuple, df_clients_pks)))


# def test_simple_two_relationship_watermark_2(): 
#   tx_clients = TransactionsClients()
#   df_clients= (
#     DataGenerator(tx_clients.metadata_client())
#       .transformers(tx_clients.transformer_client())
#       .size(10**1).get_df())
#   df_txs = DataGenerator(tx_clients.metadata_transactions()).size(10**1).get_df()
  
#   df_txs_pks = df_txs[["client_id", "tp_pes"]].drop_duplicates().values
#   df_clients_pks = df_clients[["client_id", "tp_pes"]].values
#   assert set(map(tuple, df_txs_pks)).issubset(set(map(tuple, df_clients_pks)))

  # assert all(df_txs["client_id"].isin(df_clients["client_id"]))
  # assert df_txs["client_id"].nunique() <= df_clients["client_id"].nunique()

# def test_simple_three_relationship  ():
  
#   ecommerce = Ecommerce()
#   df_category = DataGenerator(ecommerce.metadata_category()).transformers(ecommerce.transformer_category()).size(10**1).get_df()
#   print(df_category)
#   df_client = DataGenerator(ecommerce.metadata_client()).size(10**1).get_df()
#   print(df_client)
#   df_products = DataGenerator(ecommerce.metadata_products()).size(10**1).get_df()
#   print(df_products)
       







