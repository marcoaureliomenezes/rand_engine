from rand_engine.main.data_generator import DataGenerator
from rand_engine.templates.retail import Ecommerce




def test_pk_fk_keys_create_dataset():
  spec_categories = Ecommerce().metadata_category()
  transf_categories = Ecommerce().transformer_category()
  spec_clients = Ecommerce().metadata_client()
  spec_products = Ecommerce().metadata_products()


  df_category = DataGenerator(spec_categories).transformers(transf_categories).size(10**1).get_df()
  df_client = DataGenerator(spec_clients).size(10**1).get_df()
  df_products = DataGenerator(spec_products).size(10**1).get_df()


  print(df_category)
  print(df_client)
  print(df_products)
  set_cat_ids_1 = set(df_products["category_id"].to_list())
  set_cat_ids_2 = set(df_category["category_id"].to_list())

  set_client_ids_1 = set(df_client["client_id"].to_list())
  set_client_ids_2 = set(df_products["client_id"].to_list())
  #assert set_cat_ids_1.issubset(set_cat_ids_2)
  #assert set_client_ids_1.issubset(set_client_ids_2)

                               

       







