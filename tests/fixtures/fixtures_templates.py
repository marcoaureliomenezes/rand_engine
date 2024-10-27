from rand_engine.core.distinct_core import CoreDistincts
from rand_engine.core.numeric_core import CoreNumeric


class RandEngineTemplates:
   
  def __init__(self, faker):
    self.faker = faker

  def gen_first_names(self, size):
    return [self.faker.first_name() for _ in range(size)]
  
  def gen_last_names(self, size):
    return [self.faker.last_name() for _ in range(size)]
  
  def gen_email_providers(self, size):
    return [self.faker.email() for _ in range(size)]
  
  def gen_jobs(self, size):
    return [self.faker.job() for _ in range(size)]

  def gen_banks(self, size):
    #[self.faker.bank() for _ in range(size)]
    return ["Santander", "Itau", "Bradesco", "Caixa Economica", "Banco do Brasil"]
  
  def gen_street_names(self, size):
    return [self.faker.street_name() for _ in range(size)]
  
  def gen_neighborhoods(self, size):
    return [self.faker.neighborhood() for _ in range(size)]

  def gen_city_names(self, size):
    return [self.faker.city() for _ in range(size)]
  
  def gen_states(self, size):
    return [self.faker.state() for _ in range(size)]
  
    
  def templ_cpf(self):
    return dict(
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
    )
  
  def templ_cnpj(self):
    return dict(
      method=CoreDistincts.gen_complex_distincts,
      parms=dict(
        pattern="x.x.x/0001-x",
        replacement="x",
        templates=[
          {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=2)},
          {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
          {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
          {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=2)}
        ]
      )
    )
  
  def templ_address(self):
    return dict(
      method=CoreDistincts.gen_complex_distincts,
      parms=dict(
        pattern="x, x, x - x",
        replacement="x",
        templates=[
          {"method": CoreDistincts.gen_distincts_typed, "parms": dict(distinct=self.gen_street_names(10))},
          {"method": CoreDistincts.gen_distincts_typed, "parms": dict(distinct=self.gen_neighborhoods(10))},
          {"method": CoreDistincts.gen_distincts_typed, "parms": dict(distinct=self.gen_city_names(10))},
          {"method": CoreDistincts.gen_distincts_typed, "parms": dict(distinct=self.gen_states(10))}

        ]
      )
    )
  
  
  def templ_cellphone(self):
    return dict(
      method=CoreDistincts.gen_complex_distincts,
      parms=dict(
        pattern="(x) 9xx-x",
        replacement="x",
        templates=[
          {"method": CoreDistincts.gen_distincts_typed, "parms": dict(distinct=[11, 12, 13, 14, 15, 16, 17, 18, 19])},
          {"method": CoreDistincts.gen_distincts_typed, "parms": dict(distinct=[5, 6, 7, 8, 9])},
          {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
          {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=4)}
        ]
      )
    )



if __name__ == '__main__':

  from faker import Faker
  fake = Faker(locale="pt_BR")
  rand_engine = RandEngineTemplates(fake)
