from datetime import datetime as dt

import faker
import numpy as np
import pandas as pd

from rand_engine.core.distinct_core import DistinctCore
from rand_engine.core.numeric_core import NumericCore
from rand_engine.core.datetime_core import DatetimeCore
from rand_engine.main.dataframe_builder import BulkRandEngine
from rand_engine.core.distinct_utils import DistinctUtils

from tests.fixtures.fixtures_df_builder import (
    dataframe_size,
    metadata_case_constant,
    metadata_cases_variable_simple,
    metadata_cases_variable_complex,
    metadata_case_web_log_server
)



def test_rand_engine_const(dataframe_size, metadata_case_constant):
  bulk_rand_engine = BulkRandEngine()
  df = bulk_rand_engine.create_pandas_df(dataframe_size, metadata_case_constant)
  assert df.shape[0] == dataframe_size


def test_rand_engine_variable(dataframe_size, metadata_cases_variable_simple):
  bulk_rand_engine = BulkRandEngine()
 

  df = bulk_rand_engine.create_pandas_df(dataframe_size, metadata_cases_variable_simple)
  assert df.shape[0] == dataframe_size


def test_rand_engine_complex(dataframe_size, metadata_cases_variable_complex):
  bulk_rand_engine = BulkRandEngine()
  df = bulk_rand_engine.create_pandas_df(dataframe_size, metadata_cases_variable_complex)
  assert df.shape[0] == dataframe_size



def test_web_log_server(dataframe_size, metadata_case_web_log_server):
  bulk_rand_engine = BulkRandEngine()
  
  df = bulk_rand_engine.create_pandas_df(dataframe_size, metadata_case_web_log_server)
  df_web_server_log = df['ip_address'] + ' ' + df['identificador'] + ' ' + df['user'] + ' [' + df['datetime'] + ' -0700] "' + \
                      df['http_request'] + ' ' + df['http_version'] + '" ' + df['http_status'] + ' ' + df['object_size'].astype(str)
  
  pd.set_option('display.max_colwidth', None)
  print(df_web_server_log)