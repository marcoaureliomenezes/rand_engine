# Rand Engine: Gerando Milhões de Dados Sintéticos em Segundos com Python

## O Desafio dos Dados de Teste na Engenharia Moderna

Se você já trabalhou com desenvolvimento de pipelines de dados, sabe o quanto é frustrante:

- 🚫 Esperar horas para copiar dados de produção para ambientes de teste
- 🔐 Lidar com compliance e LGPD ao usar dados reais
- 🐛 Descobrir bugs apenas em produção porque não havia dados suficientes para testar
- 📊 Criar apresentações e demos sem poder expor dados sensíveis

**E se você pudesse gerar 1 milhão de registros de teste em menos de 2 segundos?**

Essa foi a pergunta que me motivou a criar o **Rand Engine**, uma biblioteca Python que transforma a geração de dados sintéticos em algo simples, rápido e declarativo.

---

## O Que é Rand Engine?

Rand Engine é uma biblioteca Python de código aberto para geração de dados sintéticos em escala. Construída sobre NumPy e Pandas, ela permite criar milhões de linhas de dados realistas através de especificações declarativas.

```bash
pip install rand-engine
```

### Por Que Mais Uma Biblioteca de Dados Sintéticos?

Existem várias ferramentas por aí, mas o Rand Engine se destaca por:

1. **Performance**: Geração vetorizada com NumPy (1M linhas em ~2s)
2. **Declarativo**: Configure tudo via dicionários Python
3. **Flexibilidade**: Suporte a correlações, distribuições e transformações
4. **Zero Configuração**: Sem dependências de bancos de dados ou frameworks pesados
5. **Streaming**: Gere dados continuamente para testes de throughput

---

## Quick Start: Seu Primeiro Dataset em 30 Segundos

Vamos criar um dataset de usuários com diferentes atributos:

```python
from rand_engine.main.data_generator import DataGenerator

# Especificação declarativa
spec = {
    "user_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint"}
    },
    "age": {
        "method": "integers",
        "kwargs": {"min": 18, "max": 65}
    },
    "salary": {
        "method": "floats",
        "kwargs": {"min": 1500.0, "max": 15000.0, "round": 2}
    },
    "is_active": {
        "method": "booleans",
        "kwargs": {"true_prob": 0.7}
    },
    "plan": {
        "method": "distincts",
        "kwargs": {"distincts": ["free", "standard", "premium"]}
    }
}

# Gerar 100.000 registros
df = DataGenerator(spec).size(100000).get_df()
print(df.head())
```

**Output:**
```
   user_id  age    salary  is_active      plan
0  0000001   42  8734.52       True  standard
1  0000002   28  3421.89      False      free
2  0000003   55 12453.67       True   premium
3  0000004   31  5678.23       True  standard
4  0000005   47  9012.45       True      free
```

---

## Recursos Que Vão Além do Básico

### 1. Exportação Direta para Múltiplos Formatos

Não precisa gerar DataFrame e depois salvar. Faça tudo em uma linha:

```python
# CSV comprimido
(DataGenerator(spec)
    .write
    .size(1_000_000)
    .format("csv")
    .option("compression", "gzip")
    .mode("overwrite")
    .save("./data/users.csv"))

# Parquet com particionamento
(DataGenerator(spec)
    .write
    .size(10_000_000)
    .format("parquet")
    .option("compression", "snappy")
    .option("numFiles", 20)  # Divide em 20 arquivos
    .save("./data/users.parquet"))
```

### 2. Dados Correlacionados (O Poder do Splitable Pattern)

Na vida real, dados estão correlacionados. Por exemplo, se um usuário tem device "mobile", o OS provavelmente é "iOS" ou "Android", não "Windows".

```python
from rand_engine.utils.distincts_utils import DistinctsUtils

spec_devices = {
    "mobile": ["iOS", "Android"],
    "desktop": ["Windows", "MacOS", "Linux"]
}

spec = {
    "session_id": {"method": "unique_ids", "args": ["zint"]},
    "device_os": {
        "method": "distincts",
        "splitable": True,  # Mágica acontece aqui
        "cols": ["device", "os"],
        "sep": ";",
        "kwargs": {
            "distincts": DistinctsUtils.handle_distincts_lvl_2(spec_devices)
        }
    }
}

df = DataGenerator(spec).size(1000).get_df()
```

**Resultado:**
```
  session_id   device        os
0    0000001   mobile       iOS
1    0000002  desktop   Windows
2    0000003   mobile   Android
3    0000004  desktop     MacOS
```

Note que nunca teremos `mobile + Windows` ou `desktop + iOS`!

### 3. Distribuições Proporcionais Realistas

Em ambientes reais, dados seguem distribuições. 70% dos usuários são "free", 20% "standard", 10% "premium":

```python
spec = {
    "user_id": {"method": "unique_ids", "args": ["zint"]},
    "plan": {
        "method": "distincts",
        "kwargs": {
            "distincts": DistinctsUtils.handle_distincts_lvl_1({
                "free": 70,      # 70% dos registros
                "standard": 20,  # 20% dos registros
                "premium": 10    # 10% dos registros
            })
        }
    }
}

df = DataGenerator(spec).size(10000).get_df()
print(df['plan'].value_counts(normalize=True))
```

**Output:**
```
plan
free         0.7012
standard     0.1989
premium      0.0999
```

### 4. Transformadores: Do Unix Timestamp para Data Legível

```python
from datetime import datetime as dt

spec = {
    "order_id": {"method": "unique_ids", "args": ["zint"]},
    "created_at": {
        "method": "unix_timestamps",
        "args": ["01-01-2024", "31-12-2024", "%d-%m-%Y"],
        "transformers": [
            lambda ts: dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        ]
    }
}

df = DataGenerator(spec).size(100).get_df()
```

**Output:**
```
  order_id          created_at
0  0000001  2024-03-15 14:23:45
1  0000002  2024-07-22 09:12:33
2  0000003  2024-11-08 18:45:12
```

### 5. Streaming: Testes de Throughput em Tempo Real

Para testar sistemas de streaming (Kafka, Kinesis, etc.):

```python
import time

# Simular 5-10 registros por segundo
stream = DataGenerator(spec).size(1000).stream_dict(
    min_throughput=5,
    max_throughput=10
)

for record in stream:
    # Cada record já vem com timestamp_created
    send_to_kafka(record)
    print(f"Enviado: {record}")
```

### 6. Padrões Complexos: IPs, URLs, Códigos

Precisa gerar IPs realistas? Códigos de rastreamento? URLs?

```python
spec = {
    "ip_address": {
        "method": "complex_distincts",
        "kwargs": {
            "pattern": "x.x.x.x",
            "replacement": "x",
            "templates": [
                {"method": "distincts", "parms": {"distincts": ["192", "172", "10"]}},
                {"method": "integers", "parms": {"min": 0, "max": 255}},
                {"method": "integers", "parms": {"min": 0, "max": 255}},
                {"method": "integers", "parms": {"min": 1, "max": 254}}
            ]
        }
    }
}

df = DataGenerator(spec).size(100).get_df()
```

**Output:**
```
    ip_address
0   192.168.1.45
1   172.16.254.1
2   10.0.0.23
3   192.168.0.102
```

---

## Caso Real: Testando Pipeline de E-commerce

Vamos simular um cenário real: testar um pipeline de e-commerce com 3 tabelas relacionadas.

### Passo 1: Criar Categorias

```python
from rand_engine.main.data_generator import DataGenerator

spec_categories = {
    "category_id": {"method": "unique_ids", "args": ["zint"]},
    "category_name": {
        "method": "distincts",
        "kwargs": {"distincts": ["Electronics", "Books", "Clothing", "Home"]}
    }
}

df_categories = DataGenerator(spec_categories).size(4).get_df()

# Salvar em DuckDB para foreign keys
from rand_engine.integrations.duckdb_handler import DuckDBHandler

db = DuckDBHandler(":memory:")
db.insert_dataframe(df_categories, "categories")
```

### Passo 2: Criar Produtos (com Foreign Keys)

```python
from rand_engine.utils.distincts_utils import DistinctsUtils

spec_products = {
    "product_id": {"method": "unique_ids", "args": ["zint"]},
    "category_id": {
        "method": "distincts",
        "kwargs": {
            "distincts": DistinctsUtils.handle_foreign_keys(
                table="categories",
                pk_fields=["category_id"],
                db_path=":memory:"
            )
        }
    },
    "price": {"method": "floats", "kwargs": {"min": 10, "max": 1000, "round": 2}},
    "stock": {"method": "integers", "kwargs": {"min": 0, "max": 500}}
}

df_products = DataGenerator(spec_products).size(1000).get_df()
db.insert_dataframe(df_products, "products")
```

### Passo 3: Criar Pedidos

```python
spec_orders = {
    "order_id": {"method": "unique_ids", "args": ["zint"]},
    "product_id": {
        "method": "distincts",
        "kwargs": {
            "distincts": DistinctsUtils.handle_foreign_keys(
                table="products",
                pk_fields=["product_id"],
                db_path=":memory:"
            )
        }
    },
    "quantity": {"method": "integers", "kwargs": {"min": 1, "max": 10}},
    "order_date": {
        "method": "unix_timestamps",
        "args": ["01-01-2024", "31-12-2024", "%d-%m-%Y"]
    }
}

df_orders = DataGenerator(spec_orders).size(10000).get_df()
```

**Pronto!** Você tem um dataset completo e relacionado para testar seu pipeline.

---

## Integração com Faker: Dados Ainda Mais Realistas

```python
import faker

fake = faker.Faker(locale="pt_BR")
fake.seed_instance(42)

spec = {
    "customer_id": {"method": "unique_ids", "args": ["zint"]},
    "name": {
        "method": "distincts",
        "kwargs": {"distincts": [fake.name() for _ in range(1000)]}
    },
    "email": {
        "method": "distincts",
        "kwargs": {"distincts": [fake.email() for _ in range(1000)]}
    },
    "city": {
        "method": "distincts",
        "kwargs": {"distincts": [fake.city() for _ in range(50)]}
    },
    "job": {
        "method": "distincts",
        "kwargs": {"distincts": [fake.job() for _ in range(200)]}
    }
}

df = DataGenerator(spec).size(10000).get_df()
```

---

## Benchmarks: Números Reais

Testado em laptop comum (Intel i5, 16GB RAM):

| Operação | Registros | Colunas | Tempo |
|----------|-----------|---------|-------|
| Geração em memória | 1.000.000 | 8 | ~2s |
| Export CSV gzip | 1.000.000 | 8 | ~5s |
| Export Parquet snappy | 1.000.000 | 8 | ~3s |
| Export 10 arquivos | 1.000.000 | 8 | ~6s |
| Streaming (10/s) | Contínuo | 8 | Real-time |

---

## Casos de Uso na Vida Real

### 1. **Engenharia de Dados**: Testes de Pipeline

```python
# Gerar dados de input
input_data = DataGenerator(input_spec).size(100000).get_df()

# Testar transformações
result = spark.createDataFrame(input_data).transform(my_pipeline)

# Validar output
assert result.count() == 100000
assert "processed_at" in result.columns
```

### 2. **QA**: Testes de Carga

```python
# Gerar 10GB de dados para teste de carga
(DataGenerator(spec)
    .write
    .size(50_000_000)
    .format("parquet")
    .option("compression", "snappy")
    .option("numFiles", 100)
    .save("s3://my-bucket/load-test/"))
```

### 3. **Data Science**: Mock de Dados para Desenvolvimento

```python
# Desenvolver modelo sem acesso a produção
train_data = DataGenerator(train_spec, seed=42).size(100000).get_df()
test_data = DataGenerator(test_spec, seed=42).size(20000).get_df()

model.fit(train_data)
metrics = model.evaluate(test_data)
```

### 4. **DevOps**: Popular Ambientes de Staging

```python
# Script de setup do ambiente
def setup_staging():
    specs = load_all_table_specs()
    
    for table_name, spec in specs.items():
        (DataGenerator(spec)
            .write
            .size(10000)
            .format("parquet")
            .save(f"./staging/{table_name}"))
```

### 5. **Apresentações**: Demos com Dados Sintéticos

```python
# Dashboard demo sem expor dados reais
demo_data = DataGenerator(dashboard_spec, seed=42).size(1000).get_df()
save_to_bi_tool(demo_data)
```

---

## Arquitetura: Como Funciona Por Baixo dos Panos

O Rand Engine segue uma arquitetura em 3 camadas:

### 1. **Core Layer** (Geração Vetorizada)
- `NPCore`: Métodos NumPy para performance máxima
- `PyCore`: Métodos Python nativos para casos complexos
- Todos são `@classmethod` e stateless

### 2. **Main Layer** (Orquestração)
- `DataGenerator`: Ponto de entrada, coordena geração
- `RandGenerator`: Processa specs e chama Core
- Suporte a transformadores e validação

### 3. **Integration Layer** (I/O e Extensões)
- `FileBatchWriter`: Exportação para arquivos
- `FileStreamWriter`: Streaming contínuo
- `DuckDBHandler`: Integração com DuckDB
- `SpecValidator`: Validação de especificações

---

## Validação Automática: Evite Erros Antes de Executar

```python
# Spec inválida
spec = {
    "age": {"method": "invalid_method"}
}

try:
    df = DataGenerator(spec).size(100).get_df()
except SpecValidationError as e:
    print(e)
    # Output: "invalid method identifier 'invalid_method'.
    #          Valid identifiers are: 'integers', 'floats', ..."
```

O validador verifica:
- ✅ Métodos válidos (strings ou callables)
- ✅ Conflitos entre `args` e `kwargs`
- ✅ Configuração correta de `splitable`
- ✅ Tipos de parâmetros

---

## Reprodutibilidade: Mesma Seed, Mesmos Dados

```python
# Útil para testes determinísticos
df1 = DataGenerator(spec, seed=42).size(1000).get_df()
df2 = DataGenerator(spec, seed=42).size(1000).get_df()

assert df1.equals(df2)  # True
```

---

## Roadmap: O Que Vem Por Aí

- 🚀 Suporte a mais formatos (Avro, ORC)
- 🎲 Geração baseada em schemas (JSON Schema, Protobuf)
- 🌐 API REST para geração remota
- 📊 UI web para criar specs visualmente
- 🔗 Integração nativa com Airflow/Prefect
- 🧠 Geração baseada em dados reais (sampling inteligente)

---

## Como Contribuir

O projeto é open source e aceita contribuições:

1. **GitHub**: [marcoaureliomenezes/rand_engine](https://github.com/marcoaureliomenezes/rand_engine)
2. **Issues**: Reporte bugs ou sugira features
3. **Pull Requests**: Adicione novos geradores ou melhore a documentação
4. **Exemplos**: Compartilhe seus casos de uso

---

## Conclusão: Por Que Você Deveria Usar Rand Engine

Se você:


- ✅ Testa pipelines de dados regularmente
- ✅ Precisa criar demos sem expor dados reais
- ✅ Quer popular ambientes de desenvolvimento rapidamente
- ✅ Faz testes de carga e performance
- ✅ Desenvolve modelos de ML sem acesso a produção

**Então Rand Engine foi feito para você.**

### Comece Agora

```bash
pip install rand-engine
```

```python
from rand_engine.main.data_generator import DataGenerator

spec = {"id": {"method": "unique_ids", "args": ["zint"]}}
df = DataGenerator(spec).size(1000).get_df()
print(df)
```

---

## Links Úteis

- 📦 **PyPI**: [pypi.org/project/rand-engine](https://pypi.org/project/rand-engine/)
- 💻 **GitHub**: [github.com/marcoaureliomenezes/rand_engine](https://github.com/marcoaureliomenezes/rand_engine)
- 📖 **Documentação**: README completo no repositório
- 🐛 **Issues**: Reporte bugs ou sugira features

---

## Sobre o Autor

**Marco Menezes** - Engenheiro de Dados apaixonado por ferramentas que tornam o desenvolvimento mais rápido e confiável. Criador do Rand Engine e entusiasta de código aberto.

---

**Se este artigo foi útil, deixe um 👏 e compartilhe com sua equipe!**

*Vamos juntos transformar a forma como geramos dados de teste na engenharia moderna.*

---

#DataEngineering #Python #OpenSource #Testing #SyntheticData #DataScience #ETL #BigData #DevOps #DataQuality
