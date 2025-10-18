import time

from rand_engine.main.data_generator import DataGenerator
from datetime import datetime as dt
from rand_engine.utils.distincts_utils import DistinctsUtils
from tests.fixtures.f2_templates import update_transformer
from tests.fixtures.f1_general import (
    rand_spec_case_1,
    rand_spec_case_2,
    rand_spec_case_1_transformer,
    rand_engine_splitable_benchmark,
    rand_engine_splitable_benchmark_baseline,
)

from tests.fixtures.f3_integrations import (
    df_size,
    microbatch_size,
    batch_size,
)


def test_pandas_df_kwargs(df_size, rand_spec_case_1):
  start_time = time.time()
  distincts_map = {"smartphone": ["android","IOS"], "desktop": ["linux", "windows"]}
  distincts_map_prop = {"OPC": [("C_OPC", 8),("V_OPC", 2)], "SWP": [("C_SWP", 6), ("V_SWP", 4)]}
  distincts_multi_map = {"OPC": [["C_OPC","V_OPC"], ["PF", "PJ"]], "SWP": (["C_SWP", "V_SWP"], [None])}
  metadata = {
    "id":        dict(method="unique_ids", kwargs=dict(strategy="zint")),
    "age":         dict(method="integers", kwargs=dict(min=0, max=100)),
    "device_plat": dict(
                    method="distincts_map", cols = ["device_type", "os_type"],
                    kwargs=dict(distincts=distincts_map)),
    "deriv_tip": dict(
                    method="distincts_map_prop", cols = ["op", "tip_op"],
                    kwargs=dict(distincts=distincts_map_prop)),
    "tipo_imposto_taxa": dict(
                    method="distincts_multi_map", cols = ["tipo", "pessoa", "taxa"],
                    kwargs=dict(distincts=distincts_multi_map)),

  }
  df_data = DataGenerator(metadata).size(10**7).get_df()
  print()
  #print(df_data)
  print(f"Elapsed time: {time.time() - start_time}")
  #assert df_data.shape[0] == df_size
  #assert rand_spec_case_1.keys() == set(df_data.columns)



# def test_pandas_df_args(df_size, rand_spec_case_2):
#   """
#   This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
#   using positional arguments.
#   """
#   df_data = DataGenerator(rand_spec_case_2).size(df_size).get_df()
#   assert df_data.shape[0] == df_size
#   assert rand_spec_case_2.keys() == set(df_data.columns)


# def test_pandas_df_internal_transformer(df_size, rand_spec_case_1_transformer):
#   """
#   This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
#   using a transformer function.
#   """
#   df_data = DataGenerator(rand_spec_case_1_transformer).size(df_size).get_df()
#   assert df_data.shape[0] == df_size


# def test_pandas_df_constant(df_size, rand_spec_case_1):
#   """
#   This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
#   using a constant seed.
#   """
#   df_data_1 = DataGenerator(rand_spec_case_1, seed=True).size(df_size).get_df()
#   df_data_2 = DataGenerator(rand_spec_case_1, seed=True).size(df_size).get_df()
#   assert df_data_1.equals(df_data_2)
#   assert df_data_1.shape == df_data_2.shape


# def test_pandas_df_constant_uuid(df_size, rand_spec_case_2):
#   """
#   This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
#   using a constant seed.
#   """
#   df_data_1 = DataGenerator(rand_spec_case_2, seed=True).size(df_size).get_df()
#   df_data_2 = DataGenerator(rand_spec_case_2, seed=True).size(df_size).get_df()
#   assert df_data_1.equals(df_data_2)
#   assert df_data_1.shape == df_data_2.shape


# def test_pandas_df_variable(df_size, rand_spec_case_1):
#   """
#   This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
#   using a variable seed.
#   """
#   df_data_1 = DataGenerator(rand_spec_case_1).size(df_size).get_df()
#   df_data_2 = DataGenerator(rand_spec_case_1).size(df_size).get_df()
#   assert df_data_1.shape == df_data_2.shape
#   assert  not df_data_1.equals(df_data_2)


# def test_pandas_df_transformer(df_size, rand_spec_case_1, update_transformer):
#   """
#   This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows 
#   using a global transformer function.
#   """
#   df_data_1 = DataGenerator(rand_spec_case_1).size(df_size).get_df()
#   transformers = [
#     lambda df: df.assign(created_at=df["created_at"].apply(
#       lambda ts: dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"))),
#   ]
#   df_data_2 = DataGenerator(rand_spec_case_1).transformers(transformers).size(df_size).get_df()
#   assert df_data_1.shape[0] == df_size
#   assert df_data_2.shape[0] == df_size
#   assert "created_at" in df_data_2.columns


# import time

# def test_splitable_benchmark_baseline(df_size, rand_engine_splitable_benchmark_baseline):
#   df_size = 10**6
#   start_time = time.time()
#   df_data = DataGenerator(rand_engine_splitable_benchmark_baseline).size(df_size).get_df()
#   print(f"Elapsed time: {time.time() - start_time} seconds")
#   assert df_data.shape[0] == df_size


# def test_splitable_benchmark(df_size, rand_engine_splitable_benchmark):
#   df_size = 10**6
#   start_time = time.time()
#   df_data = DataGenerator(rand_engine_splitable_benchmark).size(df_size).get_df()
#   print(f"Elapsed time: {time.time() - start_time} seconds")
#   assert df_data.shape[0] == df_size


# def test_create_pandas_df_wsl(df_size, rand_spec_case_wsl, wsl_transformer):
#   df_data = DataGenerator(rand_spec_case_wsl).generate_pandas_df(df_size).size(df_size).get_df()
#   pd.set_option('display.max_colwidth', None)
#   assert df_data.shape[0] == df_size



