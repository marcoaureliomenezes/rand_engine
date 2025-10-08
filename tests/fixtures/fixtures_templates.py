from rand_engine.core import Core
from rand_engine.interfaces.i_random_spec import IRandomSpec
from rand_engine.utils.distincts import DistinctUtils
import faker
import numpy as np
from typing import Callable
from pandas import DataFrame as PandasDF


class RSCustomer(IRandomSpec):

  def __init__(self):
    self.faker = faker.Faker(locale="pt_BR")

  def metadata(self):
    return {
    "user_id": {
      "method": Core.gen_ints_zfilled,
      "parms": dict(length=14)
    },
    "user_type": {   
      "method": Core.gen_distincts_untyped,
      "parms": dict(distinct=DistinctUtils.handle_distincts_lvl_1({"standard": 80,"premium":15, "gold": 5, None: 7}, 1))
    },
    "first_name": {
      "method": Core.gen_distincts_typed,
      "parms": dict(distinct=[self.faker.first_name() for _ in range(1000)])
    },
    "last_name": {
      "method": Core.gen_distincts_typed,
      "parms": dict(distinct=[f"{self.faker.last_name()} {self.faker.last_name()}" for _ in range(10000)])
    },
    "income": {
      "method": Core.gen_floats_normal,
      "parms": dict(mean=10000, std=3000, round=2)
    },
    "balance": {
      "method": Core.gen_floats_normal,
      "parms": dict(mean=5000, std=3000, round=2)
    },
    "profession": {
      "method": Core.gen_distincts_typed,
      "parms": dict(distinct=[self.faker.job() for _ in range(100)])
    },
    "birth_date": dict(
      method=Core.gen_datetimes,
      parms=dict(start='1971-07-05', end='2013-07-06', format_in="%Y-%m-%d", format_out="%d/%m/%Y")
    ),
    "signup_date": dict(
      method=Core.gen_timestamps,
      parms=dict(start="01-01-2021", end="31-12-2025", format="%d-%m-%Y")
    )
  }

  def transformer(self, **kwargs) -> Callable:
    def wrapped_transformer(df: PandasDF) -> PandasDF:
      df["income"] = np.where(df["income"] < 0, 0, df["income"])
      for k, v in kwargs.items(): df[k] = v
      for col in df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns:
        df[col] = df[col].dt.strftime('%Y-%m-%dT%H:%M:%S')
      return df
    return wrapped_transformer















# from rand_engine.core.distinct_core import CoreDistincts
# from rand_engine.core.numeric_core import CoreNumeric


# class RandEngineTemplates:
  
#  def __init__(self, faker):
#   self.faker = faker

#  def gen_first_names(self, size):
#   return [self.faker.first_name() for _ in range(size)]
 
#  def gen_last_names(self, size):
#   return [self.faker.last_name() for _ in range(size)]
 
#  def gen_email_providers(self, size):
#   return [self.faker.email() for _ in range(size)]
 
#  def gen_jobs(self, size):
#   return [self.faker.job() for _ in range(size)]

#  def gen_banks(self, size):
#   #[self.faker.bank() for _ in range(size)]
#   return ["Santander", "Itau", "Bradesco", "Caixa Economica", "Banco do Brasil"]
 
#  def gen_street_names(self, size):
#   return [self.faker.street_name() for _ in range(size)]
 
#  def gen_neighborhoods(self, size):
#   return [self.faker.neighborhood() for _ in range(size)]

#  def gen_city_names(self, size):
#   return [self.faker.city() for _ in range(size)]
 
#  def gen_states(self, size):
#   return [self.faker.state() for _ in range(size)]
 
  
#  def templ_cpf(self):
#   return dict(
#    method=CoreDistincts.gen_complex_distincts,
#      parms=dict(
#         pattern="x.x.x-x", 
#         replacement="x", 
#         templates=[
#           {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
#           {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
#           {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
#           {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=2)}
#         ]
#       )
#     )
  
#   def templ_cnpj(self):
#     return dict(
#       method=CoreDistincts.gen_complex_distincts,
#       parms=dict(
#         pattern="x.x.x/0001-x",
#         replacement="x",
#         templates=[
#           {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=2)},
#           {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
#           {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
#           {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=2)}
#         ]
#       )
#     )
  
#   def templ_address(self):
#     return dict(
#       method=CoreDistincts.gen_complex_distincts,
#       parms=dict(
#         pattern="x, x, x - x",
#         replacement="x",
#         templates=[
#           {"method": CoreDistincts.gen_distincts_typed, "parms": dict(distinct=self.gen_street_names(10))},
#           {"method": CoreDistincts.gen_distincts_typed, "parms": dict(distinct=self.gen_neighborhoods(10))},
#           {"method": CoreDistincts.gen_distincts_typed, "parms": dict(distinct=self.gen_city_names(10))},
#           {"method": CoreDistincts.gen_distincts_typed, "parms": dict(distinct=self.gen_states(10))}

#         ]
#       )
#     )
  
  
#   def templ_cellphone(self):
#     return dict(
#       method=CoreDistincts.gen_complex_distincts,
#       parms=dict(
#         pattern="(x) 9xx-x",
#         replacement="x",
#         templates=[
#           {"method": CoreDistincts.gen_distincts_typed, "parms": dict(distinct=[11, 12, 13, 14, 15, 16, 17, 18, 19])},
#           {"method": CoreDistincts.gen_distincts_typed, "parms": dict(distinct=[5, 6, 7, 8, 9])},
#           {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
#           {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=4)}
#         ]
#       )
#     )



# if __name__ == '__main__':

#   from faker import Faker
#   fake = Faker(locale="pt_BR")
#   rand_engine = RandEngineTemplates(fake)
