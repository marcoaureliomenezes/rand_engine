from functools import reduce
import faker
import pandas as pd
import numpy as np

from core_distincts import CoreDistincts
from core_numeric import CoreNumeric
from templates import RandEngineTemplates

# from rand_engine.bulk.utils import normalize_all_params, handle_num_format, handle_datatype_format, \
#                                                     get_interval, format_date_array


class BulkRandomEngine:
    
  # def fake_discrete(size=5, **kwargs):
  #   parms, formato, key, distincts = [kwargs.get(parm) for parm in ('parms','formato','key','distinct')]
  #   distincts = handle_distinct(distincts, sep=kwargs.get("sep", ""), precision=kwargs.get("precision",1))
  #   if (parms and formato and key): return fake_discrete_format(size, parms, formato, key)
  #   else: return gen_distincts(size, distincts)


  def handle_distincts_paired(self, distincts, sep):
    return [f"{j}{sep}{i}" for j in distincts for i in distincts[j]]

  def handle_relationships(self, distincts, sep=""):
    return [f"{j}{sep}{i}" for j in distincts for i in distincts[j]]


  def handle_distincts_proportions(self, distinct_prop, precision):
    return [ key for key, value in distinct_prop.items() for i in range(value * precision )]
  

  def handle_distincts_multicolumn(self, distincts, **kwargs):
    return [f"{j}{kwargs.get('sep', '')}{i}" for j in distincts for i in distincts[j]]


  # This method creates a pandas random dataframe as you pass metadata to it.
  def create_table(self, size, metadata):
    df_own_cols = pd.DataFrame({key: value["method"](size, **value["parms"]) for key, value in metadata.items()})
    return df_own_cols


if __name__ == '__main__':

  bulk_rand_engine = BulkRandomEngine()
  fake = faker.Faker(locale="pt_BR")
  rand_engine = RandEngineTemplates(fake)
  metadata = dict(
    age= dict(method=CoreNumeric.gen_ints, parms=dict(min=0, max=100)),
    balance= dict(method=CoreNumeric.gen_floats, parms=dict(min=0, max=10**4, round=2)),
    salary= dict(method=CoreNumeric.gen_floats_normal, parms=dict(mean=10**3, std=10**1, round=2)),
    job= dict(method=CoreDistincts.gen_distincts_typed, parms=dict(distinct=rand_engine.gen_jobs(10))),
    date_entry= dict(method=CoreNumeric.gen_dates, parms=dict(start="01-01-2020", end="31-12-2020", format="%d-%m-%Y")),
    datetime_last_purchase= dict(method=CoreNumeric.gen_datetimes, parms=dict(start="01-01-2020", end="31-12-2020", format="%d-%m-%Y")),
    is_active= dict(method=CoreDistincts.gen_distincts_typed, parms=dict(distinct=[True, False])),
    cpf = rand_engine.templ_cpf(),
    cnpj = rand_engine.templ_cnpj(),
    cell_phone = rand_engine.templ_cellphone(),
    address = rand_engine.templ_address(),
    # tipo_emp = dict(method=CoreDistincts.gen_distincts_typed,
    #   parms=dict(distinct=bulk_rand_engine.handle_distincts_proportions({"MEI": 100,"ME":23, "EPP": 12, "EMP": 13, "EGP": 1}, 1))),
    # tipo_categoria = dict(method=CoreDistincts.gen_distincts_typed, 
    #   parms=dict(distinct=bulk_rand_engine.handle_distincts_multicolumn({"OPC": ["C_OPC","V_OPC"], "SWP": ["C_SWP", "V_SWP"]}, sep=";")))
    )

  df = bulk_rand_engine.create_table(10**3, metadata)
  print(df)

  #df = bulk_rand_engine.create_table(10**1, metadata)
  #print(df)
  # def fake_floats(size=5, **kwargs):
  #     min, max, round, algnum = normalize_all_params(kwargs,
  #         ("min", int, 0), ("max", int, 10),
  #         ("round", int, 2), ("algnum", bool, False),
  #     )
  #     result =  gen_floats(min, max, size, round) if not algnum else gen_floats10(min, max, size, round)  
  #     return handle_num_format(result, **kwargs)

  # def handle_proportions(distinct_prop, precision):
  #     return [ key for key, value in distinct_prop.items() for i in range(value * precision)]





  # def fake_dates(size=5, **kwargs):
  #     start, end, format = normalize_all_params(kwargs,
  #         ("start", str, "01-01-2020"), ("end", str, "31-12-2020"), ("format", str, "%d-%m-%Y"))
  #     interval = get_interval(start=start, end=end, date_format=format)
  #     int_array = randint(interval[0], interval[1], size)
  #     return format_date_array(int_array, format)
  #
##################################################################################################
  #
  # metadata = dict(
  #     nome = dict(method="fake_discrete", distinct=["OPC", "SWP"]),
  #     cnpj= template_batch("cnpj"),

  # start = time.time()
  # table_data = create_table(10, metadata=metadata)
  # elapsed_time = time.time() - start
  # print(table_data)
  # print(f"time spent: {elapsed_time}")