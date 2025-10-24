# Constraints - Referential Integrity

O `rand_engine` suporta **constraints** (restrições) para garantir **integridade referencial** entre múltiplas especificações de dados. Constraints permitem criar relacionamentos **Primary Key (PK)** e **Foreign Key (FK)** entre datasets gerados.

---

## 🎯 Casos de Uso

- ✅ **Gerar dados relacionados** (produtos → categorias, pedidos → clientes)
- ✅ **Garantir integridade referencial** (todas FKs apontam para PKs existentes)
- ✅ **Simular sistemas reais** (e-commerce, bancos de dados transacionais)
- ✅ **Criar hierarquias de dados** (departamentos → funcionários → projetos)
- ✅ **Testes de CDC** (Change Data Capture com watermarks temporais)

---

## 📚 Conceitos

### Primary Key (PK)
- **Cria** uma tabela de checkpoint para armazenar registros gerados
- Tabela checkpoint: `checkpoint_{name}`
- Inclui automaticamente campo `creation_time` (timestamp Unix)
- Permite que outras specs referenciem esses dados via FK

### Foreign Key (FK)
- **Referencia** uma tabela de checkpoint existente (PK)
- Seleciona aleatoriamente valores válidos do checkpoint
- Suporta **watermark** para limitar janela temporal de referência
- Garante que 100% dos valores FK existem na PK

---

## 🔧 Estrutura

```python
"constraints": {
    "constraint_name": {
        "name": "table_name",        # Nome da tabela checkpoint
        "tipo": "PK" | "FK",         # Tipo da constraint
        "fields": ["field1", ...],   # Lista de campos
        "watermark": 60              # Opcional: lookback em segundos (FK only)
    }
}
```

### Campos

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `name` | `str` | ✅ Sim | Nome da tabela checkpoint |
| `tipo` | `str` | ✅ Sim | `"PK"` (Primary Key) ou `"FK"` (Foreign Key) |
| `fields` | `list[str]` | ✅ Sim | Para PK: `["field TYPE"]`, Para FK: `["field"]` |
| `watermark` | `int` | ❌ Não | Segundos de lookback (somente FK) |

---

## 📖 Exemplos

### 1. Primary Key Simples

```python
from rand_engine import DataGenerator

# Spec de CATEGORIAS (PK)
spec_categories = {
    "category_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint", "length": 4}
    },
    "constraints": {
        "category_pk": {                        # Nome da constraint
            "name": "category_pk",              # Nome da tabela checkpoint
            "tipo": "PK",                       # Primary Key
            "fields": ["category_id VARCHAR(4)"] # Campo + tipo SQL
        }
    }
}

# Gerar categorias
dg_cat = DataGenerator(spec_categories, db_path=":memory:")
df_categories = dg_cat.size(10).get_df()

# ✅ Checkpoint criado: checkpoint_category_pk
# ✅ Tabela contém: category_id, creation_time
```

### 2. Foreign Key Simples

```python
# Spec de PRODUTOS (FK referenciando categorias)
spec_products = {
    "product_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint", "length": 8}
    },
    "price": {
        "method": "floats_normal",
        "kwargs": {"mean": 50, "std": 10, "round": 2}
    },
    "constraints": {
        "category_fk": {                    # Nome da constraint
            "name": "category_pk",          # Referencia a PK criada antes
            "tipo": "FK",                   # Foreign Key
            "fields": ["category_id"],      # Campo FK (sem tipo)
            "watermark": 60                 # Últimos 60 segundos
        }
    }
}

# Gerar produtos (PRECISA usar o mesmo db_path!)
dg_prod = DataGenerator(spec_products, db_path=":memory:")
df_products = dg_prod.size(100).get_df()

# ✅ category_id será preenchido com valores válidos de checkpoint_category_pk
# ✅ 100% dos produtos terão category_id existente
```

### 3. Primary Key Composta (Composite Key)

```python
# Spec de CLIENTES com PK composta (client_id + tp_pes)
spec_clients = {
    "client_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint", "length": 8}
    },
    "tp_pes": {
        "method": "distincts",
        "kwargs": {"distincts": ["PF", "PJ"]}  # Pessoa Física/Jurídica
    },
    "constraints": {
        "clients_pk": {
            "name": "clients_pk",
            "tipo": "PK",
            "fields": [
                "client_id VARCHAR(8)",  # Campo 1
                "tp_pes VARCHAR(2)"      # Campo 2
            ]
        }
    }
}

dg_clients = DataGenerator(spec_clients, db_path="analytics.duckdb")
df_clients = dg_clients.size(50).get_df()

# ✅ Checkpoint criado: checkpoint_clients_pk
# ✅ PK composta: (client_id, tp_pes)
```

### 4. Foreign Key Composta

```python
# Spec de TRANSAÇÕES com FK composta (referencia clients_pk)
spec_transactions = {
    "transaction_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint", "length": 8}
    },
    "amount": {
        "method": "floats_normal",
        "kwargs": {"mean": 500, "std": 200, "round": 2}
    },
    "constraints": {
        "clients_fk": {
            "name": "clients_pk",           # Referencia PK composta
            "tipo": "FK",
            "fields": [
                "client_id",                # Campo 1 (ordem importa!)
                "tp_pes"                    # Campo 2
            ],
            "watermark": 3600               # Últimos 60 minutos
        }
    }
}

dg_trans = DataGenerator(spec_transactions, db_path="analytics.duckdb")
df_transactions = dg_trans.size(200).get_df()

# ✅ (client_id, tp_pes) preenchidos com pares válidos
# ✅ Todas transações referenciando clientes existentes
```

---

## ⏱️ Watermarks

O **watermark** limita a janela temporal de referência para FKs. É **altamente recomendado** para:

- ✅ **Evitar sobrecarga** de memória (não carrega todos os registros)
- ✅ **Simular dados realistas** (relacionamentos recentes)
- ✅ **Testes de CDC** (apenas dados novos)

### Sem Watermark (Not Recommended)

```python
"constraints": {
    "category_fk": {
        "name": "category_pk",
        "tipo": "FK",
        "fields": ["category_id"]
        # ⚠️ Sem watermark: carrega TODOS os registros da PK
    }
}
```

### Com Watermark (Recommended)

```python
"constraints": {
    "category_fk": {
        "name": "category_pk",
        "tipo": "FK",
        "fields": ["category_id"],
        "watermark": 60  # ✅ Apenas últimos 60 segundos
    }
}
```

**Query executada com watermark:**
```sql
SELECT category_id 
FROM checkpoint_category_pk 
WHERE creation_time >= UNIX_TIMESTAMP(NOW()) - 60
```

---

## 🔄 Workflow Completo

### Exemplo: E-commerce (Categorias → Produtos → Pedidos)

```python
from rand_engine import DataGenerator

# 1. Criar categorias (PK)
spec_categories = {
    "category_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 4}},
    "name": {"method": "distincts", "kwargs": {"distincts": ["Electronics", "Books", "Clothing"]}},
    "constraints": {
        "category_pk": {"name": "category_pk", "tipo": "PK", "fields": ["category_id VARCHAR(4)"]}
    }
}

dg_cat = DataGenerator(spec_categories, db_path="ecommerce.duckdb")
df_cat = dg_cat.size(10).get_df()
print(f"✅ {len(df_cat)} categorias criadas")

# 2. Criar produtos (FK → categorias)
spec_products = {
    "product_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 8}},
    "price": {"method": "floats_normal", "kwargs": {"mean": 100, "std": 50, "round": 2}},
    "constraints": {
        "product_pk": {"name": "product_pk", "tipo": "PK", "fields": ["product_id VARCHAR(8)"]},
        "category_fk": {"name": "category_pk", "tipo": "FK", "fields": ["category_id"], "watermark": 300}
    }
}

dg_prod = DataGenerator(spec_products, db_path="ecommerce.duckdb")
df_prod = dg_prod.size(100).get_df()
print(f"✅ {len(df_prod)} produtos criados")

# 3. Criar pedidos (FK → produtos)
spec_orders = {
    "order_id": {"method": "unique_ids", "kwargs": {"strategy": "uuid4"}},
    "quantity": {"method": "integers", "kwargs": {"min": 1, "max": 10}},
    "constraints": {
        "product_fk": {"name": "product_pk", "tipo": "FK", "fields": ["product_id"], "watermark": 600}
    }
}

dg_orders = DataGenerator(spec_orders, db_path="ecommerce.duckdb")
df_orders = dg_orders.size(500).get_df()
print(f"✅ {len(df_orders)} pedidos criados")

# 4. Validar integridade
print("\n📊 Validação de Integridade:")
print(f"Produtos únicos nos pedidos: {df_orders['product_id'].nunique()}")
print(f"Categorias únicas nos produtos: {df_prod['category_id'].nunique()}")
```

---

## 🧪 Validação Automática

O `SpecValidator` valida constraints automaticamente:

```python
from rand_engine.validators.spec_validator import SpecValidator

spec = {
    "id": {"method": "unique_ids", "kwargs": {"strategy": "zint"}},
    "constraints": {
        "test_pk": {
            "name": "test_pk",
            "tipo": "PK",
            "fields": ["id VARCHAR(12)"]
        }
    }
}

# Validar e mostrar erros formatados
is_valid = SpecValidator.validate_with_warnings(spec)

# Ou levantar exceção se inválido
SpecValidator.validate_and_raise(spec)
```

### Erros Comuns Detectados

❌ **Tipo inválido:**
```
❌ Constraint 'my_fk': 'tipo' must be 'PK' or 'FK', got 'UNIQUE'
   • 'PK' = Primary Key (creates checkpoint table)
   • 'FK' = Foreign Key (references checkpoint table)
```

❌ **Fields vazio:**
```
❌ Constraint 'my_pk': 'fields' cannot be empty
```

⚠️ **FK sem watermark:**
```
⚠️  Constraint 'my_fk': FK without 'watermark' will query ALL records
   Recommendation: Add 'watermark' to limit lookback period
   Example: 'watermark': 60  (only records from last 60 seconds)
```

---

## 🗄️ Gerenciamento de Checkpoints

### Listar Tabelas Checkpoint

```python
from rand_engine.integrations._duckdb_handler import DuckDBHandler

db = DuckDBHandler("ecommerce.duckdb")
tables = db.list_tables()
checkpoints = [t for t in tables if t.startswith("checkpoint_")]
print(f"Checkpoints: {checkpoints}")
```

### Consultar Checkpoint

```python
df_checkpoint = db.select_all("checkpoint_category_pk")
print(df_checkpoint.head())

# Output:
#   category_id  creation_time
# 0        0001    1729533600
# 1        0002    1729533601
# 2        0003    1729533602
```

### Limpar Checkpoints

```python
from rand_engine.main._constraints_handler import ConstraintsHandler

handler = ConstraintsHandler(db_path="ecommerce.duckdb")
handler.delete_state()  # Deleta TODAS tabelas checkpoint_*
print("✅ Todos checkpoints removidos")
```

---

## 🔍 Boas Práticas

### ✅ DO

1. **Use watermarks em FKs** para limitar janela temporal
2. **Reutilize o mesmo `db_path`** entre PK e FK relacionadas
3. **Gere PKs ANTES de FKs** (ordem importa!)
4. **Use tipos SQL adequados** nos fields de PK: `VARCHAR(8)`, `INTEGER`, `BIGINT`
5. **Nomeie constraints descritivamente**: `users_pk`, `orders_fk_users`

### ❌ DON'T

1. ❌ Não use FK sem criar PK correspondente primeiro
2. ❌ Não use `db_path` diferente entre PK e FK relacionadas
3. ❌ Não use watermark em PK (é ignorado)
4. ❌ Não esqueça tipos SQL nos fields de PK: `["id"]` → `["id VARCHAR(8)"]`
5. ❌ Não deixe fields vazio

---

## 📊 Performance

### DuckDB (Recomendado)

- ✅ **In-memory** (`:memory:`) para testes rápidos
- ✅ **Persistente** (`analytics.duckdb`) para grandes volumes
- ✅ Suporta **queries analíticas** complexas
- ✅ Até **10-50x mais rápido** que SQLite para agregações

```python
# In-memory (fast, não persistente)
dg = DataGenerator(spec, db_path=":memory:")

# Persistente (disk, reusável)
dg = DataGenerator(spec, db_path="warehouse.duckdb")
```

### SQLite (Alternativa)

- ✅ Mais compatível (built-in Python)
- ⚠️ Mais lento para queries analíticas
- ⚠️ Não suporta tipos avançados (TIMESTAMP → INTEGER)

---

## 🧩 Integração com Ferramentas

### Apache Kafka (Streaming)

```python
from rand_engine import DataGenerator

spec = {
    "user_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 8}},
    "constraints": {
        "users_pk": {"name": "users_pk", "tipo": "PK", "fields": ["user_id VARCHAR(8)"]}
    }
}

dg = DataGenerator(spec, db_path="kafka_state.duckdb")

# Gerar stream de eventos
for record in dg.stream_dict(min_throughput=10, max_throughput=50):
    producer.send("users_topic", value=record)
```

### Apache Spark

```python
from rand_engine import DataGenerator

# Gerar DataFrame pandas
dg = DataGenerator(spec, db_path="spark_checkpoints.duckdb")
df_pandas = dg.size(1000000).get_df()

# Converter para Spark DataFrame
spark_df = spark.createDataFrame(df_pandas)
spark_df.write.parquet("s3://bucket/users/")
```

---

## ❓ FAQ

### P: Posso ter múltiplas constraints no mesmo spec?
**R:** ✅ Sim! Um spec pode ter múltiplas PKs e FKs:
```python
"constraints": {
    "users_pk": {...},
    "department_fk": {...}
}
```

### P: Preciso usar DuckDB?
**R:** ✅ Não obrigatório, mas **fortemente recomendado**. SQLite também funciona mas é mais lento.

### P: O que acontece se a PK não existir quando gero FK?
**R:** ❌ Erro! Sempre gere PKs ANTES de FKs. A FK busca na tabela checkpoint da PK.

### P: Posso usar constraints com streaming?
**R:** ✅ Sim! Use `DataGenerator.stream_dict()` normalmente. Checkpoints são atualizados em tempo real.

### P: Como deletar checkpoints antigos?
**R:** Use `ConstraintsHandler.delete_state()` ou delete manualmente as tabelas `checkpoint_*`.

### P: Watermark usa segundos ou milissegundos?
**R:** **Segundos**. Exemplo: `60` = últimos 60 segundos.

### P: Posso ter FK referenciando FK?
**R:** ✅ Sim! Basta garantir que a primeira FK também seja PK:
```python
# Spec 1: PK
"constraints": {"cat_pk": {...}}

# Spec 2: FK + PK
"constraints": {
    "cat_fk": {"name": "cat_pk", "tipo": "FK", ...},
    "prod_pk": {"name": "prod_pk", "tipo": "PK", ...}
}

# Spec 3: FK (referencia prod_pk)
"constraints": {"prod_fk": {"name": "prod_pk", "tipo": "FK", ...}}
```

---

## 📚 Referências

- [DuckDB Documentation](https://duckdb.org/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SpecValidator API](/docs/API_REFERENCE.md#specvalidator)
- [ConstraintsHandler Implementation](/rand_engine/main/_constraints_handler.py)
- [Examples](/docs/EXAMPLES.md#referential-integrity)

---

**Última Atualização:** Outubro 21, 2025  
**Versão:** 0.6.1
