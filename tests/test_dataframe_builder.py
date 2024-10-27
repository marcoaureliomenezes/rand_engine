from datetime import datetime as dt

import faker
import numpy as np
import pandas as pd

from rand_engine.core.distinct_core import DistinctCore
from rand_engine.core.numeric_core import NumericCore
from rand_engine.core.datetime_core import DatetimeCore
from rand_engine.main.dataframe_builder import BulkRandEngine
from rand_engine.core.distinct_utils import DistinctUtils

from tests.fixtures.fixtures_transformers import web_server_log_transformer
from tests.fixtures.fixtures_metadata import (
    dataframe_size,
    metadata_case_constant,
    metadata_cases_variable_simple,
    metadata_cases_variable_complex,
    metadata_case_web_log_server
)




def test_rand_engine_const(dataframe_size, metadata_case_constant):
  bulk_rand_engine = BulkRandEngine()
  df = bulk_rand_engine.create_pandas_df(dataframe_size, metadata_case_constant)
  print(df)
  assert df.shape[0] == dataframe_size


def test_rand_engine_variable(dataframe_size, metadata_cases_variable_simple):
  bulk_rand_engine = BulkRandEngine()
  df = bulk_rand_engine.create_pandas_df(dataframe_size, metadata_cases_variable_simple)
  print(df)
  assert df.shape[0] == dataframe_size


def test_rand_engine_complex(dataframe_size, metadata_cases_variable_complex):
  bulk_rand_engine = BulkRandEngine()
  df = bulk_rand_engine.create_pandas_df(dataframe_size, metadata_cases_variable_complex)
  print(df)
  assert df.shape[0] == dataframe_size



def test_web_log_server(dataframe_size, metadata_case_web_log_server, web_server_log_transformer):
  bulk_rand_engine = BulkRandEngine()
  
  df = bulk_rand_engine.create_pandas_df(dataframe_size, metadata_case_web_log_server)
  df_transformer = web_server_log_transformer(df)
  pd.set_option('display.max_colwidth', None)
  print(df_transformer)
  assert df.shape[0] == dataframe_size


def test_rand_rand_engine_simple_streaming(dataframe_size, metadata_case_constant):
  bulk_rand_engine = BulkRandEngine()
  df = bulk_rand_engine.create_pandas_df(dataframe_size, metadata_case_constant)
  for record in bulk_rand_engine.create_streaming_df(df):
    print(record)
    

def test_web_log_server_streaming(dataframe_size, metadata_case_web_log_server, web_server_log_transformer):
  bulk_rand_engine = BulkRandEngine()
  df = bulk_rand_engine.create_pandas_df(dataframe_size, metadata_case_web_log_server)
  df_transformed = web_server_log_transformer(df)
  for record in bulk_rand_engine.create_streaming_series(df_transformed):
      print(record)


def test_create_file(metadata_case_web_log_server, web_server_log_transformer):
    bulk_rand_engine = BulkRandEngine()
    path_test = './test_outputs/test.log'
    bulk_rand_engine.microbatch_file_with_streaming(path_test, metadata_case_web_log_server, web_server_log_transformer, 10**3, 10**9)

