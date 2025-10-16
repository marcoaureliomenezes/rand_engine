# TODOs - Rand Engine

Este documento lista melhorias priorizadas para tornar a biblioteca mais acessível, robusta e profissional para outros desenvolvedores.

---

## 🔥 Prioridade CRÍTICA (v0.5.0)

### 1. Adicionar Tratamento de Erros Robusto

**Problema:** Erros crípticos quando specs estão mal configuradas.

```python
# Atual - Erro genérico
spec = {
    "age": {"method": "invalid"}  # TypeError: 'str' object is not callable
}

# Desejado - Erro descritivo
spec = {
    "age": {"method": "invalid"}
}
# ValueError: Column 'age': 'method' must be a callable function, got <class 'str'>
```

**Tarefas:**
- [ ] Adicionar validação de spec em `RandGenerator.__init__()`
- [ ] Validar que `method` é callable
- [ ] Validar que `kwargs`/`args` são dicts/listas
- [ ] Adicionar mensagens de erro descritivas com nome da coluna
- [ ] Criar exceção customizada `SpecValidationError`

**Arquivo:** `rand_engine/main/rand_generator.py`

---

### 2. Criar Módulo de Validação de Specs

**Problema:** Não há feedback antes de gerar dados (falha em runtime).

```python
# Novo módulo: rand_engine/validators/spec_validator.py
from typing import Dict, List
from rand_engine.exceptions import SpecValidationError

class SpecValidator:
    
    @staticmethod
    def validate(spec: Dict) -> List[str]:
        """
        Valida spec e retorna lista de erros encontrados.
        Retorna lista vazia se spec está válida.
        """
        errors = []
        
        for col_name, col_config in spec.items():
            # Validar que tem 'method'
            if "method" not in col_config:
                errors.append(f"Column '{col_name}': missing required key 'method'")
                continue
            
            # Validar que method é callable
            if not callable(col_config["method"]):
                errors.append(f"Column '{col_name}': 'method' must be callable, got {type(col_config['method'])}")
            
            # Validar kwargs vs args
            has_kwargs = "kwargs" in col_config
            has_args = "args" in col_config
            
            if has_kwargs and has_args:
                errors.append(f"Column '{col_name}': cannot have both 'kwargs' and 'args'")
            
            if has_kwargs and not isinstance(col_config["kwargs"], dict):
                errors.append(f"Column '{col_name}': 'kwargs' must be a dict")
            
            if has_args and not isinstance(col_config["args"], (list, tuple)):
                errors.append(f"Column '{col_name}': 'args' must be a list or tuple")
            
            # Validar splitable pattern
            if col_config.get("splitable"):
                if "cols" not in col_config:
                    errors.append(f"Column '{col_name}': splitable=True requires 'cols' key")
                elif not isinstance(col_config["cols"], list):
                    errors.append(f"Column '{col_name}': 'cols' must be a list")
        
        return errors
    
    @staticmethod
    def validate_and_raise(spec: Dict):
        """Valida spec e levanta exceção se houver erros."""
        errors = SpecValidator.validate(spec)
        if errors:
            raise SpecValidationError("\n".join(errors))
```

**Tarefas:**
- [ ] Criar `rand_engine/validators/spec_validator.py`
- [ ] Criar `rand_engine/exceptions.py` com exceções customizadas
- [ ] Integrar validação no `DataGenerator.__init__()`
- [ ] Adicionar testes unitários para validador

---

### 3. Documentar Todos os Métodos do Core

**Problema:** Métodos sem docstrings dificultam descoberta de funcionalidades.

```python
# Atual
@classmethod
def gen_ints(self, size: int, min: int, max: int) -> np.ndarray:
    return np.random.randint(min, max + 1, size)

# Desejado
@classmethod
def gen_ints(cls, size: int, min: int, max: int) -> np.ndarray:
    """
    Gera array de inteiros aleatórios com distribuição uniforme.
    
    Args:
        size: Número de elementos a serem gerados
        min: Valor mínimo (inclusivo)
        max: Valor máximo (inclusivo)
    
    Returns:
        Array NumPy com inteiros aleatórios entre min e max
    
    Examples:
        >>> Core.gen_ints(size=5, min=0, max=100)
        array([42, 17, 89, 3, 56])
    
    Notes:
        - Distribuição uniforme: cada valor tem mesma probabilidade
        - Performance: O(1) via NumPy, não O(n) via loop Python
    """
    return np.random.randint(min, max + 1, size)
```

**Tarefas:**
- [ ] Adicionar docstrings em TODOS os métodos de `Core`
- [ ] Adicionar docstrings em `DataGenerator`
- [ ] Adicionar docstrings em `RandGenerator`
- [ ] Adicionar docstrings em `FileWriter`
- [ ] Adicionar docstrings em `DistinctsUtils`
- [ ] Usar formato Google Style ou NumPy Style (consistente)

---

### 4. Corrigir `self` → `cls` em Classmethods

**Problema:** Classmethods usando `self` como primeiro parâmetro (convenção errada).

```python
# Atual (ERRADO)
@classmethod
def gen_ints(self, size: int, min: int, max: int):
    return np.random.randint(min, max + 1, size)

# Correto
@classmethod
def gen_ints(cls, size: int, min: int, max: int):
    return np.random.randint(min, max + 1, size)
```

**Tarefas:**
- [ ] Substituir `self` por `cls` em todos os `@classmethod` de `Core`
- [ ] Substituir `self` por `cls` em todos os `@classmethod` de `DistinctsUtils`
- [ ] Executar testes para garantir que nada quebrou

**Arquivos:** `rand_engine/core.py`, `rand_engine/utils/distincts.py`

---

## ⚠️ Prioridade ALTA (v0.6.0)

### 5. Adicionar Logging ao Invés de Prints Silenciosos

**Problema:** Difícil debugar problemas sem visibilidade interna.

```python
import logging

# Configurar logger
logger = logging.getLogger("rand_engine")

# Usar em DataGenerator
class DataGenerator:
    def __init__(self, random_spec, seed: int = None):
        logger.debug(f"Initializing DataGenerator with seed={seed}")
        np.random.seed(seed)
        # ... resto do código
        
    def generate_pandas_df(self, size: int):
        logger.info(f"Generating DataFrame with {size} rows")
        logger.debug(f"Spec has {len(self.random_spec)} columns")
        # ... resto do código
```

**Tarefas:**
- [ ] Criar `rand_engine/logging.py` com configuração padrão
- [ ] Adicionar logs em pontos críticos (init, geração, escrita)
- [ ] Usar níveis apropriados: DEBUG, INFO, WARNING, ERROR
- [ ] Documentar como usuário pode configurar logging

---

### 6. Criar Exemplos Completos (Pasta `examples/`)

**Problema:** README tem snippets, mas faltam scripts completos executáveis.

```bash
examples/
├── 01_basic_generation.py          # Geração simples
├── 02_multiple_formats.py          # CSV, Parquet, JSON
├── 03_streaming_kafka.py           # Streaming (mock Kafka)
├── 04_correlated_data.py           # Splitable pattern
├── 05_web_server_logs.py           # Caso real completo
├── 06_ecommerce_orders.py          # E-commerce dataset
├── 07_iot_sensors.py               # Sensor readings
├── 08_custom_transformers.py       # Transformers avançados
└── README.md                        # Índice dos exemplos
```

**Tarefas:**
- [ ] Criar pasta `examples/` na raiz do projeto
- [ ] Criar 8 scripts de exemplo completos e comentados
- [ ] Cada exemplo deve ter header com descrição e caso de uso
- [ ] Adicionar `examples/README.md` explicando cada exemplo
- [ ] Linkar `examples/` no README principal

---

### 7. Melhorar Interface `IRandomSpec`

**Problema:** `debugger()` é obrigatório mas não tem uso claro.

```python
# Atual
class IRandomSpec(ABC):
    @abstractmethod
    def metadata(self) -> Dict:
        pass
    
    @abstractmethod
    def transformer(self) -> Callable:
        pass
    
    @abstractmethod
    def debugger(self) -> Any:  # ❌ Obrigatório mas sem propósito
        pass

# Proposto
class IRandomSpec(ABC):
    """
    Interface para definir especificações de dados de forma reutilizável.
    
    Útil para criar templates de dados (logs, orders, users, etc) que
    podem ser versionados e compartilhados.
    """
    
    @abstractmethod
    def metadata(self) -> Dict[str, Dict]:
        """
        Retorna a especificação de dados (spec dict).
        
        Returns:
            Dict com formato {column_name: {method: ..., kwargs: ...}}
        """
        pass
    
    def transformers(self) -> List[Callable]:
        """
        Retorna lista de funções para transformar o DataFrame gerado.
        
        Opcional. Retorna lista vazia por padrão.
        """
        return []
    
    def validate(self) -> bool:
        """
        Valida se a spec está correta.
        
        Opcional. Útil para debugging durante desenvolvimento.
        """
        from rand_engine.validators.spec_validator import SpecValidator
        errors = SpecValidator.validate(self.metadata())
        if errors:
            print("❌ Spec validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        print("✅ Spec is valid")
        return True
```

**Tarefas:**
- [ ] Tornar `transformer()` → `transformers()` (plural, consistente)
- [ ] Remover `debugger()` como método abstrato
- [ ] Adicionar método `validate()` opcional
- [ ] Atualizar documentação da interface
- [ ] Migrar exemplos para nova interface

**Arquivo:** `rand_engine/interfaces/i_random_spec.py`

---

### 8. Adicionar Type Hints Completos

**Problema:** Type hints inconsistentes dificultam IDE support.

```python
# Atual
def generate_first_level(self, size: int):  # ❌ Sem return type
    dict_data = {}
    # ...
    return df_pandas

# Desejado
def generate_first_level(self, size: int) -> pd.DataFrame:
    dict_data: Dict[str, np.ndarray] = {}
    # ...
    return df_pandas
```

**Tarefas:**
- [ ] Adicionar return types em TODOS os métodos públicos
- [ ] Adicionar types em variáveis quando não óbvio
- [ ] Usar `Optional[T]` para valores que podem ser None
- [ ] Usar `Union[T1, T2]` quando apropriado
- [ ] Executar `mypy` para validar types (adicionar ao CI/CD)

---

### 9. Criar Testes de Integração End-to-End

**Problema:** Testes unitários ok, mas faltam testes de fluxo completo.

```python
# tests/test_e2e.py
def test_complete_workflow_csv(tmp_path):
    """Testa fluxo completo: spec → geração → escrita → leitura → validação"""
    spec = {
        "id": {"method": Core.gen_unique_identifiers, "kwargs": {"strategy": "zint"}},
        "age": {"method": Core.gen_ints, "kwargs": {"min": 18, "max": 65}},
    }
    
    output_path = tmp_path / "users.csv"
    
    # Gerar e escrever
    DataGenerator(spec, seed=42) \
        .write(size=1000) \
        .format("csv") \
        .load(str(output_path))
    
    # Ler e validar
    df = pd.read_csv(output_path)
    assert df.shape[0] == 1000
    assert df.shape[1] == 2
    assert df["age"].min() >= 18
    assert df["age"].max() <= 65
    assert df["id"].nunique() == 1000  # Todos únicos
```

**Tarefas:**
- [ ] Criar `tests/test_e2e.py`
- [ ] Testar fluxo completo para CSV, Parquet, JSON
- [ ] Testar fluxo com transformers
- [ ] Testar fluxo com splitable pattern
- [ ] Testar streaming (coletar N registros e validar)

---

## 💡 Prioridade MÉDIA (v0.7.0)

### 10. Adicionar CLI para Geração Rápida

**Problema:** Precisa escrever script Python para gerar dados simples.

```bash
# Uso proposto
rand-engine generate \
    --columns "id:uuid,age:int(18,65),salary:float(1000,10000)" \
    --size 10000 \
    --format csv \
    --output data.csv

# Ou via JSON spec
rand-engine generate \
    --spec spec.json \
    --size 100000 \
    --format parquet \
    --output data.parquet
```

**Tarefas:**
- [ ] Criar `rand_engine/cli.py` usando `click` ou `typer`
- [ ] Implementar comando `generate` com flags básicas
- [ ] Suportar specs inline ou via arquivo JSON/YAML
- [ ] Adicionar progress bar para gerações grandes
- [ ] Documentar CLI no README

---

### 11. Suporte a Schemas Externos (JSON Schema, Avro)

**Problema:** Integração com sistemas existentes que usam schemas.

```python
from rand_engine.schema import AvroSchemaEngine

# Gerar dados a partir de schema Avro
engine = AvroSchemaEngine.from_file("user_events.avsc")
df = engine.generate(size=10000)

# Ou JSON Schema
from rand_engine.schema import JSONSchemaEngine
engine = JSONSchemaEngine.from_dict({
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0, "maximum": 120}
    }
})
df = engine.generate(size=5000)
```

**Tarefas:**
- [ ] Criar módulo `rand_engine/schema/`
- [ ] Implementar `AvroSchemaEngine`
- [ ] Implementar `JSONSchemaEngine`
- [ ] Mapear tipos de schema para métodos do Core
- [ ] Adicionar testes e documentação

---

### 12. Performance Benchmarks e Otimizações

**Problema:** Não há dados sobre performance esperada.

```python
# tests/benchmarks/bench_generation.py
import pytest
from rand_engine.data_generator import DataGenerator

@pytest.mark.benchmark
def test_benchmark_1M_rows(benchmark):
    spec = {...}  # Spec típica
    engine = DataGenerator(spec)
    
    result = benchmark(lambda: engine.generate_pandas_df(1_000_000))
    
    # Assertar tempo máximo aceitável
    assert benchmark.stats.mean < 5.0  # < 5 segundos
```

**Tarefas:**
- [ ] Criar `tests/benchmarks/` com pytest-benchmark
- [ ] Benchmark para 100k, 1M, 10M rows
- [ ] Comparar performance NumPy vs loops Python
- [ ] Documentar performance esperada no README
- [ ] Identificar e otimizar gargalos

---

### 13. Suporte a Constraints e Dependências Entre Colunas

**Problema:** Não há forma nativa de criar dados onde colunas dependem umas das outras.

```python
# Caso de uso: end_date deve ser maior que start_date
from rand_engine.constraints import ColumnConstraint

spec = {
    "start_date": {
        "method": Core.gen_unix_timestamps,
        "kwargs": {"start": "2024-01-01", "end": "2024-12-31", "format": "%Y-%m-%d"}
    },
    "end_date": {
        "method": ColumnConstraint.after_column("start_date"),
        "kwargs": {"min_delta_days": 1, "max_delta_days": 90}
    }
}
```

**Tarefas:**
- [ ] Criar módulo `rand_engine/constraints/`
- [ ] Implementar constraints básicos (after, before, greater_than, etc)
- [ ] Permitir referencias a outras colunas na spec
- [ ] Adicionar validação de dependências circulares
- [ ] Documentar padrão de constraints

---

### 14. Melhorar Documentação com MkDocs/Sphinx

**Problema:** Documentação apenas no README, difícil navegar.

```bash
docs/
├── index.md
├── getting-started/
│   ├── installation.md
│   ├── quickstart.md
│   └── basic-concepts.md
├── user-guide/
│   ├── core-methods.md
│   ├── transformers.md
│   ├── file-formats.md
│   └── streaming.md
├── api-reference/
│   ├── core.md
│   ├── data-generator.md
│   └── file-writer.md
├── examples/
│   ├── web-logs.md
│   ├── ecommerce.md
│   └── iot-sensors.md
└── contributing.md
```

**Tarefas:**
- [ ] Escolher entre MkDocs ou Sphinx
- [ ] Criar estrutura de docs/
- [ ] Gerar API reference automaticamente
- [ ] Configurar GitHub Pages para hosting
- [ ] Adicionar badge no README linkando para docs

---

## 📚 Prioridade BAIXA (v0.8.0+)

### 15. Integração com Ferramentas de BI (Tableau, Power BI)

```python
from rand_engine.connectors import TableauConnector

# Publicar dataset diretamente no Tableau Server
connector = TableauConnector(server_url="...", token="...")
df = DataGenerator(spec).mode("pandas").size(100000).get_df()
connector.publish(df, dataset_name="sales_mock_data")
```

---

### 16. ML-Aware Generation (Differential Privacy)

```python
from rand_engine.ml import MLEngine

# Gerar dados que seguem distribuições de um CSV real
# mas com garantias de privacidade
engine = MLEngine.fit("real_sales_data.csv")
synthetic = engine.generate(
    size=10000,
    privacy_budget=1.0,  # Epsilon para differential privacy
    preserve_correlations=True
)
```

---

### 17. Suporte a Dados Temporais/Séries Temporais

```python
from rand_engine.timeseries import TimeSeriesEngine

# Gerar séries temporais com padrões sazonais
spec = {
    "timestamp": {...},
    "sensor_reading": {
        "method": TimeSeriesEngine.gen_seasonal,
        "kwargs": {
            "base": 20.0,
            "amplitude": 5.0,
            "period": "daily",
            "noise": 0.5
        }
    }
}
```

---

### 18. Dashboard Web para Configuração Visual de Specs

Interface web (Streamlit/Gradio) para construir specs visualmente:
- Drag & drop de colunas
- Configuração de parâmetros via forms
- Preview de dados em tempo real
- Export de spec como JSON/Python

---

## 🔧 Melhorias de Infraestrutura

### 19. Adicionar Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

**Tarefas:**
- [ ] Configurar black para formatação
- [ ] Configurar isort para imports
- [ ] Configurar flake8 para linting
- [ ] Adicionar mypy para type checking
- [ ] Documentar setup em CONTRIBUTING.md

---

### 20. Adicionar Code Coverage no CI/CD

```yaml
# .github/workflows/test_build_and_publish.yml
- name: Run tests with coverage
  run: |
    poetry run pytest --cov=rand_engine --cov-report=xml --cov-report=html

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

**Tarefas:**
- [ ] Configurar pytest-cov
- [ ] Integrar com Codecov ou Coveralls
- [ ] Adicionar badge de coverage no README
- [ ] Definir threshold mínimo (ex: 80%)

---

### 21. Suporte a Python 3.13+

```toml
[tool.poetry.dependencies]
python = "^3.10"  # Atual

# Futuro
python = "^3.10 | ^3.13"
```

**Tarefas:**
- [ ] Testar biblioteca com Python 3.13
- [ ] Adicionar Python 3.13 na matrix de testes do CI/CD
- [ ] Verificar compatibilidade de dependências
- [ ] Atualizar documentação

---

## 📊 Métricas de Sucesso

Para considerar a biblioteca "pronta para produção", alcançar:

- [ ] **95%+ test coverage**
- [ ] **Documentação completa** (API reference + guias)
- [ ] **10+ exemplos completos** executáveis
- [ ] **Zero warnings** no mypy/flake8
- [ ] **Performance benchmarks** documentados
- [ ] **50+ stars** no GitHub (indicador de adoção)
- [ ] **Issues respondidas** em < 48h
- [ ] **Release notes** para cada versão

---

## 🗺️ Roadmap Visual

```
v0.5.0 (Crítico - 2 semanas)
├── Tratamento de erros robusto
├── Validação de specs
├── Documentação completa (docstrings)
└── Correção de convenções (self → cls)

v0.6.0 (Alta - 1 mês)
├── Logging estruturado
├── Exemplos completos (8+)
├── Interface IRandomSpec melhorada
├── Type hints completos
└── Testes E2E

v0.7.0 (Média - 2 meses)
├── CLI para geração rápida
├── Suporte a schemas (Avro, JSON Schema)
├── Performance benchmarks
├── Constraints entre colunas
└── Documentação online (MkDocs)

v0.8.0+ (Baixa - Futuro)
├── Integração BI (Tableau, Power BI)
├── ML-aware generation
├── Séries temporais
└── Dashboard web
```

---

## 🚀 Quick Wins (Implementar Primeiro)

Se tiver tempo limitado, comece por:

1. **Docstrings em todos os métodos do Core** (2h) → Melhora muito UX
2. **Validação de specs** (4h) → Previne 80% dos erros de usuário
3. **8 exemplos completos** (6h) → Facilita onboarding
4. **Corrigir self → cls** (1h) → Fix técnico simples
5. **README melhorado** (já feito!) → Primeira impressão

**Total: ~13h de trabalho para transformar a biblioteca** ✨

---

**Última atualização:** 2025-10-10  
**Versão atual:** 0.4.7  
**Próximo milestone:** 0.5.0
