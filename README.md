# Rand Engine

**Gerador de dados randômicos em escala para testes, desenvolvimento e prototipação.**

Rand Engine é uma biblioteca Python que permite gerar milhões de linhas de dados sintéticos de forma rápida e configurável através de especificações declarativas. Construída com NumPy e Pandas para máxima performance.

---

## 📦 Instalação

```bash
pip install rand-engine
```

**Requisitos:**
- Python >= 3.10
- numpy >= 2.1.1
- pandas >= 2.2.2

---

## 🎯 Público-Alvo

- **Engenheiros de Dados**: Testes de pipelines ETL/ELT sem depender de dados de produção
- **QA Engineers**: Geração de datasets realistas para testes de carga e integração
- **Data Scientists**: Mock de dados durante desenvolvimento de modelos
- **Desenvolvedores Backend**: Popular ambientes de desenvolvimento e staging
- **Profissionais de BI**: Criar demos e POCs sem expor dados sensíveis

---

## 🚀 Exemplos de Uso

### 1. Geração Básica de Dados

```python
from rand_engine.data_generator import DataGenerator
from rand_engine.core import Core

# Especificação declarativa dos dados
spec = {
    "id": {
        "method": Core.gen_unique_identifiers,
        "kwargs": {"strategy": "zint"}
    },
    "idade": {
        "method": Core.gen_ints,
        "kwargs": {"min": 18, "max": 65}
    },
    "salario": {
        "method": Core.gen_floats,
        "kwargs": {"min": 1500, "max": 15000, "round": 2}
    },
    "ativo": {
        "method": Core.gen_distincts,
        "kwargs": {"distinct": [True, False]}
    },
    "plano": {
        "method": Core.gen_distincts,
        "kwargs": {"distinct": ["free", "standard", "premium"]}
    }
}

# Gerar DataFrame Pandas
engine = DataGenerator(spec, seed=42)
engine.generate_pandas_df(size=10000)
df = engine.actual_dataframe()

print(df.head())
```

### 2. Exportar para Diferentes Formatos

```python
from rand_engine.data_generator import DataGenerator

# Gerar e salvar como CSV comprimido
DataGenerator(spec) \
    .write(size=100000) \
    .format("csv") \
    .option("compression", "gzip") \
    .mode("overwrite") \
    .load("./data/usuarios.csv")

# Gerar e salvar como Parquet
DataGenerator(spec) \
    .write(size=1000000) \
    .format("parquet") \
    .option("compression", "snappy") \
    .load("./data/usuarios.parquet")

# Gerar e salvar como JSON
DataGenerator(spec) \
    .write(size=50000) \
    .format("json") \
    .load("./data/usuarios.json")
```

### 3. Streaming de Dados

```python
from rand_engine.data_generator import DataGenerator

# Gerar stream contínuo de registros
engine = DataGenerator(spec, seed=42)
engine.generate_pandas_df(size=100)

for record in engine.stream_dict(min_throughput=10, max_throughput=50):
    # Cada registro inclui timestamp_created automaticamente
    print(record)
    # Exemplo: enviar para Kafka, API, banco de dados, etc.
```

### 4. Dados Correlacionados (Splitable Pattern)

```python
from rand_engine.core import Core
from rand_engine.utils.distincts import DistinctUtils

# Gerar dados onde colunas estão correlacionadas
spec = {
    "user_id": {
        "method": Core.gen_unique_identifiers,
        "kwargs": {"strategy": "zint"}
    },
    "device_os": {
        "method": Core.gen_distincts,
        "splitable": True,
        "cols": ["device", "os"],
        "sep": ";",
        "kwargs": {
            "distinct": ["mobile;iOS", "mobile;Android", "desktop;Windows", "desktop;MacOS"]
        }
    }
}

# Resultado: colunas 'device' e 'os' com valores correlacionados
```

### 5. Distribuições Proporcionais

```python
from rand_engine.core import Core
from rand_engine.utils.distincts import DistinctUtils

# Gerar dados com distribuições ponderadas
spec = {
    "nivel": {
        "method": Core.gen_distincts,
        "kwargs": {
            "distinct": DistinctUtils.handle_distincts_lvl_1({
                "Junior": 70,   # 70% dos registros
                "Pleno": 20,    # 20% dos registros
                "Senior": 10    # 10% dos registros
            })
        }
    }
}
```

### 6. Padrões Complexos (IPs, URLs, etc.)

```python
from rand_engine.core import Core

# Gerar endereços IP realistas
spec = {
    "ip_address": {
        "method": Core.gen_complex_distincts,
        "kwargs": {
            "pattern": "x.x.x.x",
            "replacement": "x",
            "templates": [
                {"method": Core.gen_distincts, "parms": {"distinct": ["192", "172", "10"]}},
                {"method": Core.gen_ints, "parms": {"min": 0, "max": 255}},
                {"method": Core.gen_ints, "parms": {"min": 0, "max": 255}},
                {"method": Core.gen_ints, "parms": {"min": 1, "max": 254}}
            ]
        }
    }
}
```

### 7. Timestamps e Datas

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
