import faker

from rand_engine.bulk.core_distincts import CoreDistincts
from rand_engine.bulk.core_numeric import CoreNumeric
from rand_engine.bulk.core_datetime import CoreDatetime
from rand_engine.bulk.dataframe_builder import BulkRandEngine
from rand_engine.bulk.templates import RandEngineTemplates

if __name__ == '__main__':

  bulk_rand_engine = BulkRandEngine()
  fake = faker.Faker(locale="pt_BR")
  rand_engine = RandEngineTemplates(fake)

  metadata_1 = {
    "campo_int": dict(method=CoreNumeric.gen_ints, parms=dict(min=0, max=100)),
    "campo_float": dict(method=CoreNumeric.gen_floats, parms=dict(min=0, max=10**3, round=2)),
    "campo_float_normal": dict(method=CoreNumeric.gen_floats_normal, parms=dict(mean=10**3, std=10**1, round=2)),
    "campo_booleano": dict(method=CoreDistincts.gen_distincts_typed, parms=dict(distinct=[True, False])),
    "campo_categorico": dict(method=CoreDistincts.gen_distincts_typed, parms=dict(distinct=["valor_1", "valor_2", "valor_3"])),
    "campo_categorico_faker_injection": dict(method=CoreDistincts.gen_distincts_typed, parms=dict(distinct=[fake.job() for _ in range(100)])),
    "signup_date": dict(method=CoreDatetime.gen_dates, parms=dict(start="01-01-2020", end="31-12-2020", format="%d-%m-%Y")),
    "campo_categorico_com_peso": dict(
      method=CoreDistincts.gen_distincts_typed,
      parms=dict(distinct=bulk_rand_engine.handle_distincts_proportions({"MEI": 100,"ME":23, "EPP": 12, "EMP": 13, "EGP": 1}, 1))
    ),
  
  }


  # Definição de metadados complexos
  metadata_2 = {
    "campo_cpf": dict(
      method=CoreDistincts.gen_complex_distincts,
      parms=dict(
        pattern="x.x.x-x", 
        replacement="x", 
        templates=[
          {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
          {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
          {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
          {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=2)}
        ]
      )
    ),
    # "campo_cnpj": rand_engine.templ_cnpj(),
    # "campo_telefone": rand_engine.templ_cellphone(),
    # "campo_endereco": rand_engine.templ_address(),
    "tipo_categoria": dict(
      method=CoreDistincts.gen_distincts_typed,
      splitable=True,
      cols=["categoria_produto", "tipo_produto"],
      sep=";",
      parms=dict(distinct=bulk_rand_engine.handle_distincts_multicolumn({"OPC": ["C_OPC","V_OPC"], "SWP": ["C_SWP", "V_SWP"]}, sep=";"))
    )
  }
  
  # df_1 = bulk_rand_engine.create_pandas_df(10**3, metadata_1)
  # print(df_1)

  df_2 = bulk_rand_engine.create_pandas_df(10**3, metadata_2)
  print(df_2)

