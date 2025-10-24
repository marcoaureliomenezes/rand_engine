# Logging no rand_engine

O `rand_engine` usa o módulo padrão `logging` do Python para fornecer informações sobre operações internas, especialmente nos módulos de integração (DuckDB e SQLite).

---

## 🔇 Comportamento Padrão (Silencioso)

**Por padrão, a biblioteca não imprime nenhum log**. Ela é completamente silenciosa:

```python
from rand_engine import DataGenerator, RandSpecs
from rand_engine.integrations._duckdb_handler import DuckDBHandler

# Uso normal - SEM logs
db = DuckDBHandler(":memory:")
df = DataGenerator(RandSpecs.customers()).size(1000).get_df()
db.insert_df("customers", df, pk_cols=["customer_id"])

# ✅ Funciona perfeitamente, mas sem imprimir nada
```

---

## 📢 Habilitando Logs

### Opção 1: Configuração Básica (Recomendada)

```python
import logging

# Habilitar logs INFO para todo o projeto
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

from rand_engine.integrations._duckdb_handler import DuckDBHandler

db = DuckDBHandler(":memory:")

# Output:
# INFO:rand_engine.integrations._duckdb_handler:Created new connection to DuckDB database: :memory:
```

### Opção 2: Apenas rand_engine (Recomendada para Produção)

```python
import logging

# Configurar apenas logs do rand_engine
logger = logging.getLogger("rand_engine")
logger.setLevel(logging.INFO)

# Adicionar handler para console
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(handler)

# Agora só verá logs do rand_engine
from rand_engine.integrations._duckdb_handler import DuckDBHandler
db = DuckDBHandler("analytics.duckdb")
```

### Opção 3: Configuração Detalhada (DEBUG)

```python
import logging

# Configurar para DEBUG (mais verboso)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from rand_engine.integrations._duckdb_handler import DuckDBHandler
db = DuckDBHandler(":memory:")

# Verá logs mais detalhados de operações internas
```

---

## 📋 Logs Disponíveis

### DuckDBHandler

| Operação | Nível | Mensagem |
|----------|-------|----------|
| Criar nova conexão | INFO | `Created new connection to DuckDB database: {path}` |
| Reutilizar conexão | INFO | `Reusing existing connection to DuckDB database: {path}` |
| Criar tabela | DEBUG | `Created table {table_name}` |
| Inserir dados | DEBUG | `Inserted {n} rows into table {table_name}` |
| Consultar dados | DEBUG | `Selected {n} rows from table {table_name}` |
| Fechar conexão | INFO | `Database connection closed and removed from pool: {path}` |
| Fechar todas | INFO | `All DuckDB connections closed. Total: {n}` |

### SQLiteHandler

| Operação | Nível | Mensagem |
|----------|-------|----------|
| Criar nova conexão | INFO | `Created new connection to SQLite database: {path}` |
| Reutilizar conexão | INFO | `Reusing existing connection to SQLite database: {path}` |
| Criar tabela | DEBUG | `Created table {table_name}` |
| Inserir dados | DEBUG | `Inserted {n} rows into table {table_name}` |
| Consultar dados | DEBUG | `Selected {n} rows from table {table_name}` |
| Fechar conexão | INFO | `Database connection closed and removed from pool: {path}` |
| Fechar todas | INFO | `All SQLite connections closed. Total: {n}` |

---

## 🎯 Casos de Uso

### Desenvolvimento Local

```python
import logging
logging.basicConfig(level=logging.INFO)

# Verá logs de conexões e operações principais
```

### Debugging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Verá TODOS os logs, incluindo operações detalhadas
```

### Produção (Sem Logs)

```python
# Não configure logging - a lib será silenciosa
from rand_engine import DataGenerator
```

### Produção (Apenas Erros)

```python
import logging
logging.basicConfig(level=logging.WARNING)

# Verá apenas warnings e errors
```

---

## 📊 Exemplo Completo

```python
import logging
from rand_engine import DataGenerator, RandSpecs
from rand_engine.integrations._duckdb_handler import DuckDBHandler

# 1. Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 2. Criar database
db = DuckDBHandler("analytics.duckdb")
# Log: Created new connection to DuckDB database: analytics.duckdb

# 3. Criar tabela
db.create_table("customers", pk_def="customer_id VARCHAR(10)")

# 4. Gerar e inserir dados
df = DataGenerator(RandSpecs.customers(), seed=42).size(10000).get_df()
db.insert_df("customers", df, pk_cols=["customer_id"])
# Log: Inserted 10000 rows into table customers

# 5. Consultar dados
result = db.select_all("customers", columns=["customer_id", "name"])
# Log: Selected 10000 rows from table customers

print(f"✅ Loaded {len(result)} customers")

# 6. Fechar conexão
db.close()
# Log: Database connection closed and removed from pool: analytics.duckdb
```

---

## 🔧 Configuração Avançada

### Salvar Logs em Arquivo

```python
import logging

# Configurar para salvar em arquivo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rand_engine.log"),
        logging.StreamHandler()  # Também mostrar no console
    ]
)
```

### Filtrar Por Módulo

```python
import logging

# Apenas logs do DuckDB
duckdb_logger = logging.getLogger("rand_engine.integrations._duckdb_handler")
duckdb_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
duckdb_logger.addHandler(handler)

# SQLite permanece silencioso
sqlite_logger = logging.getLogger("rand_engine.integrations._sqlite_handler")
sqlite_logger.setLevel(logging.WARNING)
```

---

## ❓ FAQ

### P: Por que não vejo nenhum log?
**R:** A biblioteca é silenciosa por padrão. Configure o logging explicitamente:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### P: Como desabilitar logs completamente?
**R:** Não configure o logging. A biblioteca não imprimirá nada.

### P: Posso ver logs de operações de geração de dados?
**R:** Atualmente, apenas módulos de integração (DuckDB/SQLite) possuem logs. A geração de dados (DataGenerator) é silenciosa.

### P: Os logs afetam a performance?
**R:** Não. Logs em nível INFO têm impacto mínimo. Logs DEBUG podem ser ligeiramente mais custosos em operações massivas.

### P: Como usar em Jupyter Notebooks?
**R:** Configure no início do notebook:
```python
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
```

---

## 📚 Referências

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)

---

**Última Atualização:** Outubro 21, 2025  
**Versão:** 0.6.1
