# Rand Engine

**Gerador de dados randômicos em escala para testes, desenvolvimento e prototipação.**

Biblioteca Python para gerar milhões de linhas de dados sintéticos através de especificações declarativas. Construída com NumPy e Pandas para máxima performance.

---

## 📦 Instalação

```bash
pip install rand-engine
```

---

## ✅ Requisitos

- **Python**: >= 3.10
- **numpy**: >= 2.1.1
- **pandas**: >= 2.2.2
- **faker**: >= 28.4.1 (opcional, para dados realistas)
- **duckdb**: >= 1.4.1 (opcional, para integrações)

---

## 🎯 Público Alvo

- **Engenheiros de Dados**: Testes de pipelines ETL/ELT sem depender de dados de produção
- **QA Engineers**: Geração de datasets realistas para testes de carga e integração
- **Data Scientists**: Mock de dados durante desenvolvimento de modelos
- **Desenvolvedores Backend**: Popular ambientes de desenvolvimento e staging
- **Profissionais de BI**: Criar demos e POCs sem expor dados sensíveis

---

## 🚀 Quick Start

### 1. Geração Básica com Identificadores String

```python
from rand_engine.main.data_generator import DataGenerator

# Especificação declarativa usando identificadores string
spec = {
    "id": {
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

# Gerar DataFrame
df = DataGenerator(spec).size(10000).get_df()
print(df.head())
```

### 2. Usando Args (Argumentos Posicionais)

```python
spec = {
    "id": {"method": "unique_ids", "args": ["zint", 8]},
    "age": {"method": "integers", "args": [18, 65]},
    "salary": {"method": "floats", "args": [1500, 15000, 2]},
    "plan": {"method": "distincts", "args": [["free", "standard", "premium"]]}
}

df = DataGenerator(spec).size(5000).get_df()
```

### 3. Exportar para Diferentes Formatos

```python
# CSV comprimido
(DataGenerator(spec)
    .write
    .size(100000)
    .format("csv")
    .option("compression", "gzip")
    .mode("overwrite")
    .save("./data/users.csv"))

# Parquet com múltiplos arquivos
(DataGenerator(spec)
    .write
    .size(1000000)
    .format("parquet")
    .option("compression", "snappy")
    .option("numFiles", 5)
    .save("./data/users.parquet"))

# JSON
(DataGenerator(spec)
    .write
    .size(50000)
    .format("json")
    .save("./data/users.json"))
```

### 4. Streaming de Dados

```python
import time

# Gerar stream contínuo de registros
stream = DataGenerator(spec).size(1000).stream_dict(
    min_throughput=5, 
    max_throughput=10
)

for record in stream:
    # Cada registro inclui timestamp_created automaticamente
    print(record)
    # Exemplo: enviar para Kafka, API, banco de dados, etc.
```

### 5. Transformadores (Pós-processamento)

```python
from datetime import datetime as dt

spec = {
    "id": {"method": "unique_ids", "args": ["zint"]},
    "created_at": {
        "method": "unix_timestamps",
        "args": ["01-01-2020", "31-12-2020", "%d-%m-%Y"],
        # Transformador inline na coluna
        "transformers": [
            lambda ts: dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        ]
    }
}

# Transformador global (aplicado ao DataFrame completo)
transformers = [
    lambda df: df.assign(year=df["created_at"].str[:4])
]

df = (DataGenerator(spec)
    .transformers(transformers)
    .size(1000)
    .get_df())
```

### 6. Seed para Reprodutibilidade

```python
# Mesmo seed = mesmos dados
df1 = DataGenerator(spec, seed=42).size(1000).get_df()
df2 = DataGenerator(spec, seed=42).size(1000).get_df()

assert df1.equals(df2)  # True
```

---

## 📚 Métodos de Geração Disponíveis

### Identificadores String (Recomendado)

| Método | Descrição | Exemplo |
|--------|-----------|---------|
| `integers` | Inteiros uniformes | `{"method": "integers", "kwargs": {"min": 0, "max": 100}}` |
| `int_zfilled` | Inteiros com zeros à esquerda | `{"method": "int_zfilled", "kwargs": {"min": 0, "max": 999, "length": 5}}` |
| `floats` | Floats uniformes | `{"method": "floats", "kwargs": {"min": 0.0, "max": 100.0, "round": 2}}` |
| `floats_normal` | Floats com distribuição normal | `{"method": "floats_normal", "kwargs": {"mean": 50, "std": 10}}` |
| `distincts` | Valores de lista | `{"method": "distincts", "kwargs": {"distincts": ["A", "B", "C"]}}` |
| `complex_distincts` | Padrões complexos (IPs, URLs) | Ver exemplo acima |
| `unix_timestamps` | Timestamps Unix | `{"method": "unix_timestamps", "kwargs": {"start": "01-01-2020", "end": "31-12-2020"}}` |
| `unique_ids` | IDs únicos | `{"method": "unique_ids", "kwargs": {"strategy": "zint"}}` |
| `booleans` | Valores booleanos | `{"method": "booleans", "kwargs": {"true_prob": 0.7}}` |

---

## 🔧 Recursos Avançados

### Splitable Pattern (Colunas Correlacionadas)

Gere múltiplas colunas correlacionadas a partir de uma única coluna:

```python
from rand_engine.utils.distincts_utils import DistinctsUtils

spec_handle = {
    "mobile": ["iOS", "Android"],
    "desktop": ["Windows", "MacOS", "Linux"]
}

spec = {
    "device_os": {
        "method": "distincts",
        "splitable": True,
        "cols": ["device", "os"],
        "sep": ";",
        "kwargs": {
            "distincts": DistinctsUtils.handle_distincts_lvl_2(spec_handle)
        }
    }
}

# Resultado:
# | device  | os      |
# |---------|---------|
# | mobile  | iOS     |
# | desktop | Windows |
# | mobile  | Android |
```

### Distribuições Proporcionais

```python
# Nível 1: Proporções simples
spec_level_1 = {"free": 70, "standard": 20, "premium": 10}
distincts = DistinctsUtils.handle_distincts_lvl_1(spec_level_1)

# Nível 2: Correlação entre categorias
spec_level_2 = {
    "mobile": ["iOS", "Android"],
    "desktop": ["Windows", "MacOS"]
}
distincts = DistinctsUtils.handle_distincts_lvl_2(spec_level_2)

# Nível 3: Correlação com proporções
spec_level_3 = {
    "GET /home": [("200", 7), ("400", 2), ("500", 1)],
    "POST /login": [("201", 5), ("404", 3)]
}
distincts = DistinctsUtils.handle_distincts_lvl_3(spec_level_3)
```

### Integração com Faker

```python
import faker

fake = faker.Faker(locale="pt_BR")
fake.seed_instance(42)

spec = {
    "name": {
        "method": "distincts",
        "kwargs": {"distincts": [fake.name() for _ in range(1000)]}
    },
    "job": {
        "method": "distincts",
        "kwargs": {"distincts": [fake.job() for _ in range(100)]}
    }
}
```

---

## 📝 Formato da Especificação

### Estrutura Básica

```python
spec = {
    "nome_coluna": {
        "method": "identificador_string",  # ou callable
        "kwargs": {...},                   # argumentos nomeados
        "args": [...],                     # ou argumentos posicionais
        "transformers": [...],             # transformadores inline (opcional)
        "splitable": True,                 # para colunas correlacionadas (opcional)
        "cols": [...],                     # nomes das colunas split (se splitable)
        "sep": ";"                         # separador (se splitable)
    }
}
```

### Opções de Formato

- **kwargs**: Dicionário de argumentos nomeados
- **args**: Lista de argumentos posicionais (alternativa a kwargs)
- **transformers**: Lista de funções lambda para transformar valores
- **splitable**: Habilita divisão de uma coluna em múltiplas
- **cols**: Nomes das colunas resultantes (obrigatório se splitable=True)
- **sep**: Separador usado para split (obrigatório se splitable=True)

---

## ⚙️ API de Escrita de Arquivos

### Fluent API

```python
(DataGenerator(spec)
    .write
    .size(1000000)                    # Quantidade de registros
    .format("parquet")                # csv, json, parquet
    .option("compression", "gzip")    # Opções específicas do formato
    .option("numFiles", 10)           # Dividir em múltiplos arquivos
    .mode("overwrite")                # overwrite ou append
    .save("/path/to/output"))
```

### Opções por Formato

**CSV:**
- `compression`: None, "gzip", "zip"
- `numFiles`: Número de arquivos a gerar

**JSON:**
- `compression`: None, "gzip"
- `numFiles`: Número de arquivos a gerar

**Parquet:**
- `compression`: None, "gzip", "snappy"
- `numFiles`: Número de arquivos a gerar

---

## 🧪 Casos de Uso

### 1. Testes de ETL

```python
# Gerar dados de entrada para pipeline
input_data = DataGenerator(input_spec).size(100000).get_df()

# Executar pipeline
result = etl_pipeline(input_data)

# Validar saída
assert result.shape[0] == 100000
assert "processed_at" in result.columns
```

### 2. Testes de Carga

```python
# Gerar 10 milhões de registros em Parquet
(DataGenerator(spec)
    .write
    .size(10_000_000)
    .format("parquet")
    .option("compression", "snappy")
    .option("numFiles", 50)
    .save("/data/load_test"))
```

### 3. Mock de API

```python
# Endpoint simulado
@app.get("/users")
def get_users(limit: int = 100):
    df = DataGenerator(user_spec).size(limit).get_df()
    return df.to_dict(orient="records")
```

### 4. Demos e Apresentações

```python
# Dataset realista para demo
demo_spec = {
    "customer_id": {"method": "unique_ids", "args": ["zint"]},
    "name": {"method": "distincts", "kwargs": {...}},  # usar faker
    "revenue": {"method": "floats_normal", "kwargs": {"mean": 5000, "std": 2000}},
    "segment": {"method": "distincts", "kwargs": {...}}
}

df = DataGenerator(demo_spec, seed=42).size(1000).get_df()
```

---

## 🔍 Validação de Specs

A biblioteca valida automaticamente as especificações:

```python
# Spec inválida - método não existe
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

Para desabilitar validação:

```python
df = DataGenerator(spec, validate=False).size(100).get_df()
```

---

## 🚀 Performance

Benchmarks em um laptop comum (i5, 16GB RAM):

| Operação | Tamanho | Tempo |
|----------|---------|-------|
| Geração em memória | 1M linhas, 8 colunas | ~2s |
| Export CSV gzip | 1M linhas | ~5s |
| Export Parquet snappy | 1M linhas | ~3s |
| Export múltiplos arquivos | 1M linhas, 10 arquivos | ~6s |

**Dicas de Performance:**
- Use `integers` e `floats` para melhor performance (NumPy nativo)
- Prefira Parquet para grandes volumes
- Use `numFiles` para paralelizar I/O
- Evite transformadores complexos em grandes datasets

---

## 📖 Exemplos Completos

Veja exemplos completos em:
- `tests/test_3_main.py` - Testes de geração
- `tests/test_4_write_batch_files.py` - Testes de escrita
- `tests/fixtures/f1_general.py` - Specs de exemplo
- `rand_engine/templates/` - Templates prontos para uso

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:
1. Fork o repositório
2. Crie uma branch para sua feature
3. Adicione testes
4. Envie um Pull Request

---

## 📄 Licença

MIT License - veja LICENSE para detalhes

---

## 🔗 Links

- **GitHub**: https://github.com/marcoaureliomenezes/rand_engine
- **PyPI**: https://pypi.org/project/rand-engine/
- **Documentação**: Em construção

---

**Desenvolvido com ❤️ para a comunidade de dados**

```python
from rand_engine.core import Core
from datetime import datetime as dt

# Gerar timestamps Unix com transformação
spec = {
    "created_at": {
        "method": Core.gen_unix_timestamps,
        "kwargs": {
            "start": "01-01-2024",
            "end": "31-12-2024",
            "format": "%d-%m-%Y"
        },
        "transformers": [
            lambda ts: dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        ]
    }
}
```

### 8. Geração Incremental por Tamanho

```python
from rand_engine.data_generator import DataGenerator

# Gerar múltiplos arquivos até atingir tamanho total desejado
DataGenerator(spec) \
    .write(size=10000) \
    .format("parquet") \
    .option("compression", "snappy") \
    .incr_load("./data/lotes/", size_in_mb=50)

# Gera arquivos de 10k linhas até totalizar ~50MB
```

---

## 📊 Principais Recursos

✅ **Performance**: Geração vetorizada com NumPy  
✅ **Declarativo**: Configuração via dicionários Python  
✅ **Flexível**: Suporte a transformers customizados  
✅ **Escalável**: Gere milhões de registros em segundos  
✅ **Formatos**: CSV, JSON, Parquet com compressão  
✅ **Streaming**: Geração contínua para testes de throughput  
✅ **Reprodutível**: Controle de seed para resultados consistentes  
✅ **Correlações**: Dados relacionados com splitable pattern  

---

## 🔄 Processo de Release CI/CD

O projeto utiliza **GitHub Actions** para automação completa do processo de release:

### Workflow de Release

1. **Trigger**: Push de tag com versionamento semântico
   ```bash
   git tag 0.4.7
   git push origin --tags
   ```

2. **Validação**: Verifica se a versão é maior que a publicada no PyPI

3. **Build**: 
   - Atualiza versão no `pyproject.toml` via Poetry
   - Instala dependências
   - Gera distribuições `sdist` e `wheel`

4. **Testes**: Executa suite completa de testes via pytest

5. **Publicação**: 
   - Upload automático para PyPI
   - Criação de GitHub Release com artifacts

6. **Deploy**: Pacote disponível via `pip install rand-engine`

### Versionamento

O projeto segue **Semantic Versioning** (semver):
- `MAJOR.MINOR.PATCH` (ex: `0.4.7`)
- Suporte a pre-releases: `0.5.0a1`, `0.5.0b2`, `0.5.0rc1`

**⚠️ Importante**: A versão é gerenciada automaticamente pela tag Git. Não edite manualmente o `pyproject.toml`.

---

## 📚 Documentação Adicional

Para informações detalhadas sobre a arquitetura interna, padrões de desenvolvimento e contribuições, consulte:

- [Copilot Instructions](/.github/copilot-instructions.md) - Guia completo da arquitetura

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga o processo:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🔗 Links

- **PyPI**: [https://pypi.org/project/rand-engine/](https://pypi.org/project/rand-engine/)
- **GitHub**: [https://github.com/marcoaureliomenezes/rand_engine](https://github.com/marcoaureliomenezes/rand_engine)
- **Issues**: [https://github.com/marcoaureliomenezes/rand_engine/issues](https://github.com/marcoaureliomenezes/rand_engine/issues)

---

**Desenvolvido com ❤️ por Marco Menezes**
