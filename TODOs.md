Sim. Após as alterações nos métodos core, para deixas as APIs mais consistentes é necessário que você faça um trabalho nos validadores.

Existem 2 casos que precisa considerar.

Alguns arquivos para ler e entender melhor o contexto:

- /home/marco/workspace/projects/rand_engine/rand_engine/core/_np_core.py
- /home/marco/workspace/projects/rand_engine/rand_engine/core/_spark_core.py

Onde validações são aplicadas:
- /home/marco/workspace/projects/rand_engine/rand_engine/main/data_generator.py
- /home/marco/workspace/projects/rand_engine/rand_engine/main/spark_generator.py

Quando as especificações recebem os mesmos valores, então você só precisa alterar os validadores para refletir as mudanças feitas nos métodos core.

Exemplo:

  @classmethod
  def gen_distincts(cls, size: int, distincts: List[Any]) -> np.ndarray:
    assert len(list(set([type(x) for x in distincts]))) == 1
    return np.random.choice(distincts, size)

  @staticmethod
  def gen_distincts(spark, F, df, col_name, distincts=[]):

  Ambos os métodos agora usam o parâmetro "distincts". Então você só precisa alterar os validadores para refletir essa mudança.

  Ja para os métodos que geram inteiros:

  @classmethod
  def gen_ints(cls, size: int, min: int, max: int, int_type: str = 'int32') -> np.ndarray:
    allowed_integers = ['int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64']
    assert int_type in allowed_integers, f"int_type must be one of {allowed_integers}"
    return np.random.randint(min, max + 1, size, dtype=np.int64).astype(int_type)

  @staticmethod
  def gen_ints(spark, F, df, col_name, min=0, max=10, dtype="long"):
    allowed_integers = ["int", "bigint", "long", "integer"]
    assert dtype in allowed_integers, f"dtype must be one of {allowed_integers}"
    return df.withColumn(col_name, (F.rand() * (max - min) + min).cast(dtype))

Os parametros são diferentes: "int_type" no método numpy e "dtype" no método spark. Podem receber valores diferentes. Acredito que isso tem que ser validado de forma diferente.

Gostaria também que pudessemos unificar as validações que são comuns entre os validadores numpy e spark, para evitar duplicação de código.

Os validadores estão em:
- /home/marco/workspace/projects/rand_engine/rand_engine/validators/spark_spec_validator.py
- /home/marco/workspace/projects/rand_engine/rand_engine/validators/spec_validator.py

Na atual abordagem um valida as especificações de SparkGenerator e outro as do DataGenerator. Gostaria de mudar a estratégia para 

- /home/marco/workspace/projects/rand_engine/rand_engine/validators/common_validator.py (novo arquivo)
- /home/marco/workspace/projects/rand_engine/rand_engine/validators/advanced_validator.py (novo arquivo)

O advanced_validator.py terá as validaçẽos de métodos específicos somente de DataGenerator.
Por exemplo:
      "distincts_map": PyCore.gen_distincts_map,
      "distincts_multi_map": PyCore.gen_distincts_multi_map,
      "distincts_map_prop": PyCore.gen_distincts_map_prop,
      "complex_distincts": PyCore.gen_complex_distincts,

E ao serem aplicados. nos arquivos DataGenerator e SparkGenerator, ambos irão importar o common_validator.py e o advanced_validator.py (somente o DataGenerator).
Acha que pode fazer essas alterações?

Vamos trabalhar forte nessas validações para garantir que tudo esteja consistente e funcionando perfeitamente!