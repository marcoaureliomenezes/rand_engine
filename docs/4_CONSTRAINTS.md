# Constraints - Primary and Foreign Key Relationships

## 📋 Overview
`DataGenerator` supports **Primary Key (PK)** and **Foreign Key (FK)** constraints to generate **related entities** with referential integrity. This enables realistic data generation for scenarios like:
- Product ↔ Category relationships
- Customer ↔ Order relationships
- User ↔ Transaction relationships

**🆕 NEW:** Automatic checkpoint cleanup to prevent memory overflow in `:memory:` databases.

⚠️ **Note:** Constraints are **only available in DataGenerator**, not in SparkGenerator.

---

## 🎯 Key Features
- ✅ **Primary Keys (PK)** - Define parent entities
- ✅ **Foreign Keys (FK)** - Reference parent entities with watermark-based lookups
- ✅ **Checkpoint tables** - Store generated PKs for FK referencing
- ✅ **🆕 Automatic cleanup** - Prevents memory overflow with configurable retention period
- ✅ **DuckDB & SQLite support** - Persistent or in-memory checkpoints
- ✅ **Watermark control** - Define time window for FK lookups

---

## 🏗️ How Constraints Work

### 1. Basic Constraint Structure
Constraints are defined in the **`"constraints"`** key of your RandSpec:

```python
spec = {
    "category_id": {"method": "int_zfilled", "kwargs": {"length": 4}},
    "category_name": {"method": "distincts", "kwargs": {"distincts": ["Electronics", "Books"]}},
    
    "constraints": {
        "category_pk": {
            "tipo": "PK",
            "name": "category_pk",
            "fields": ["category_id VARCHAR(4)"]
        }
    }
}
```

### 2. Primary Key (PK) Definition
A **PK constraint** stores generated values in a **checkpoint table** for later reference by FK constraints.

**Structure:**
```python
"constraint_name": {
    "tipo": "PK",
    "name": "checkpoint_table_name",
    "fields": ["column_name DATA_TYPE", ...]
}
```

**Example:**
```python
"constraints": {
    "product_pk": {
        "tipo": "PK",
        "name": "product_checkpoint",
        "fields": ["product_id VARCHAR(10)"]
    }
}
```

### 3. Foreign Key (FK) Definition
An **FK constraint** references values from a **PK checkpoint table** within a time window (watermark).

**Structure:**
```python
"constraint_name": {
    "tipo": "FK",
    "name": "checkpoint_table_name",  # Must match PK's name
    "fields": ["column_name"],         # Column to populate
    "watermark": seconds               # Time window (integer)
}
```

**Example:**
```python
"constraints": {
    "product_fk": {
        "tipo": "FK",
        "name": "product_checkpoint",  # References product_pk
        "fields": ["product_id"],
        "watermark": 60  # Look back 60 seconds
    }
}
```

---

## 📝 Complete Example: Product-Category Relationship

### Define Parent Entity (Category)
```python
from rand_engine.main.data_generator import DataGenerator

# Parent entity: Categories
category_spec = {
    "category_id": {"method": "int_zfilled", "kwargs": {"length": 4}},
    "category_name": {"method": "distincts", "kwargs": {"distincts": [
        "Electronics", "Books", "Clothing", "Food"
    ]}},
    
    "constraints": {
        "category_pk": {
            "tipo": "PK",
            "name": "category_pk",
            "fields": ["category_id VARCHAR(4)"]
        }
    }
}

# Generate 100 categories (PKs stored in checkpoint)
df_categories = DataGenerator(category_spec, seed=42).size(100).get_df()
print(df_categories.head())
```

**Output:**
```
  category_id  category_name
0        0000   Electronics
1        0001        Books
2        0002      Clothing
3        0003         Food
4        0004   Electronics
```

### Define Child Entity (Products)
```python
# Child entity: Products (references category_id)
product_spec = {
    "product_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "product_name": {"method": "distincts", "kwargs": {"distincts": [
        "Laptop", "Phone", "Book", "Shirt", "Apple"
    ]}},
    "price": {"method": "floats", "kwargs": {"min": 10.0, "max": 500.0, "decimals": 2}},
    
    "constraints": {
        "category_fk": {
            "tipo": "FK",
            "name": "category_pk",  # References category_pk checkpoint
            "fields": ["category_id"],
            "watermark": 120  # Look back 120 seconds
        }
    }
}

# Generate 1000 products (category_id pulled from checkpoint)
df_products = DataGenerator(product_spec, seed=42).size(1000).get_df()
print(df_products.head())
```

**Output:**
```
  product_id product_name   price category_id
0   00000000       Laptop  450.23        0042
1   00000001        Phone  299.99        0018
2   00000002         Book   25.50        0007
3   00000003        Shirt   39.99        0055
4   00000004        Apple    5.00        0091
```

**✅ Referential Integrity:** All `category_id` values in products exist in the categories checkpoint table.

---

## 🗄️ Checkpoint Tables

### What are Checkpoint Tables?
When you define a **PK constraint**, `DataGenerator` creates a table in the checkpoint database:

**Table Name:** `checkpoint_{name}`
**Schema:** `fields + creation_time TIMESTAMP`

**Example:**
```sql
CREATE TABLE checkpoint_category_pk (
    category_id VARCHAR(4),
    creation_time TIMESTAMP
);
```

### Where are Checkpoints Stored?
By default, checkpoints use **SQLite in-memory** (`:memory:`):

```python
# Default: in-memory (lost after session)
generator = DataGenerator(spec_with_constraints)
```

### Using Persistent Checkpoints
For **persistent checkpoints** across sessions, use DuckDB or SQLite file:

```python
from rand_engine.integrations.duckdb_handler import DuckDBHandler

# Persistent DuckDB database
db_conn = DuckDBHandler(db_path="checkpoints.duckdb")

df = (
    DataGenerator(spec_with_constraints)
    .db_checkpoint(db_conn)
    .size(10_000)
    .get_df()
)

# Checkpoints persist across runs
```

### Manual Checkpoint Management
```python
# View checkpoint tables (DuckDB)
db_conn.query_with_pandas("SHOW TABLES")

# Query checkpoint data
db_conn.query_with_pandas("SELECT * FROM checkpoint_category_pk LIMIT 10")

# Delete all checkpoints
generator.option("reset_checkpoint", True).get_df()
```

---

## 🆕 Automatic Checkpoint Cleanup

### The Problem: Memory Overflow
When using **`:memory:` databases** (default), checkpoint tables **grow indefinitely** as you generate data. For long-running processes or streaming scenarios, this causes **memory overflow**.

**Before (without cleanup):**
```python
# Stream 1 million records
for i in range(10_000):
    df = DataGenerator(spec_with_pk).size(100).get_df()
    # Checkpoint table grows: 100, 200, 300, ..., 1,000,000 rows
    # Eventually: MemoryError!
```

### The Solution: Automatic Cleanup
**🆕 NEW:** `ConstraintsHandler` now **automatically deletes old checkpoint records** when processing PK constraints. This prevents memory overflow while maintaining recent data for FK lookups.

**How it works:**
1. When a PK constraint is processed, records are inserted with `creation_time = NOW()`
2. **After insertion**, old records are automatically deleted:
   ```sql
   DELETE FROM checkpoint_table
   WHERE creation_time < NOW() - (watermark + retention_period)
   ```
3. Only **recent records** within the retention window are kept

### Retention Period Configuration
The **retention period** defines how long old records are kept **beyond the watermark**.

**Default:** `300 seconds` (5 minutes)

```python
from rand_engine.integrations.sqlite_handler import SQLiteHandler

# Use default retention (300 seconds)
db_conn = SQLiteHandler(":memory:")
generator = DataGenerator(spec_with_constraints).db_checkpoint(db_conn)

# Custom retention period (600 seconds = 10 minutes)
db_conn = SQLiteHandler(":memory:", retention_period=600)
generator = DataGenerator(spec_with_constraints).db_checkpoint(db_conn)
```

### Retention Period Calculation
For a given constraint with `watermark=60` seconds:

| Retention Period | Total Kept | Cleanup Threshold |
|------------------|------------|-------------------|
| 300s (default) | 360s (6 min) | `NOW() - 360s` |
| 600s | 660s (11 min) | `NOW() - 660s` |
| 0s | 60s (1 min) | `NOW() - 60s` |

**Example:**
```python
# Watermark = 120s, Retention = 300s
# Total window = 120 + 300 = 420 seconds (7 minutes)
# Records older than 7 minutes are deleted automatically

"constraints": {
    "category_fk": {
        "tipo": "FK",
        "name": "category_pk",
        "watermark": 120  # 2 minutes lookback
    }
}
```

### Why Retention Period Matters
- **Too small:** Risk deleting records still needed by FK constraints
- **Too large:** Checkpoint tables grow unnecessarily
- **Recommended:** `2-5x watermark` (default 300s works for most cases)

---

## 🧪 Real-World Example with Cleanup

### Scenario: Streaming Product-Category Data
```python
from rand_engine.main.data_generator import DataGenerator
from rand_engine.integrations.sqlite_handler import SQLiteHandler

# Configure SQLite with custom retention
db_conn = SQLiteHandler(":memory:", retention_period=600)  # 10 minutes

# Parent spec: Categories (PK)
category_spec = {
    "category_id": {"method": "int_zfilled", "kwargs": {"length": 4}},
    "category_name": {"method": "distincts", "kwargs": {"distincts": ["A", "B", "C"]}},
    "constraints": {
        "category_pk": {
            "tipo": "PK",
            "name": "category_pk",
            "fields": ["category_id VARCHAR(4)"]
        }
    }
}

# Child spec: Products (FK with 60s watermark)
product_spec = {
    "product_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "price": {"method": "floats", "kwargs": {"min": 10.0, "max": 500.0, "decimals": 2}},
    "constraints": {
        "category_fk": {
            "tipo": "FK",
            "name": "category_pk",
            "watermark": 60  # Look back 60 seconds
        }
    }
}

# Generate categories first
category_gen = DataGenerator(category_spec, seed=42).db_checkpoint(db_conn)
df_categories = category_gen.size(100).get_df()

# Stream products for extended period
product_gen = DataGenerator(product_spec, seed=42).db_checkpoint(db_conn)

for i in range(1000):
    df_products = product_gen.size(100).get_df()
    # OLD BEHAVIOR: Checkpoint grows indefinitely → MemoryError
    # NEW BEHAVIOR: Cleanup keeps only last 660s (60s watermark + 600s retention)
    
    if i % 100 == 0:
        print(f"Generated {(i+1) * 100} products. Checkpoint size stable.")
```

**Output:**
```
Generated 100 products. Checkpoint size stable.
Generated 10000 products. Checkpoint size stable.
Generated 20000 products. Checkpoint size stable.
...
Generated 100000 products. Checkpoint size stable.  # No memory overflow!
```

---

## 🔧 Technical Details

### Checkpoint Table Schema
```sql
CREATE TABLE checkpoint_{name} (
    {field1} {TYPE1},
    {field2} {TYPE2},
    ...
    creation_time TIMESTAMP  -- Added automatically
);
```

### Cleanup Implementation
Cleanup is triggered **automatically** after PK insertion:

```python
# Internal logic in ConstraintsHandler.handle_pks()
1. Insert new records with creation_time = NOW()
2. Call cleanup_old_checkpoints(table_name, watermark)
3. Execute: DELETE FROM checkpoint_table WHERE creation_time < threshold
```

### Watermark Behavior
The **watermark** defines the **time window** for FK lookups:

```python
# FK with watermark=120 seconds
SELECT {fields} FROM checkpoint_table
WHERE creation_time >= NOW() - 120
ORDER BY RANDOM()
LIMIT 1;
```

**Watermark=0:** Lookup from all records (no time filter)
**Watermark>0:** Lookup from recent N seconds only

---

## ⚠️ Important Considerations

### 1. Constraints Only in DataGenerator
```python
# ✅ CORRECT
from rand_engine.main.data_generator import DataGenerator
df = DataGenerator(spec_with_constraints).size(1000).get_df()

# ❌ WRONG - SparkGenerator doesn't support constraints
from rand_engine.main.spark_generator import SparkGenerator
df = SparkGenerator(spark, F, spec_with_constraints).size(1000).get_df()
```

### 2. Generate Parent Before Child
Always generate the **PK entity** before the **FK entity**:

```python
# ✅ CORRECT ORDER
df_categories = DataGenerator(category_spec).size(100).get_df()  # PK first
df_products = DataGenerator(product_spec).size(1000).get_df()    # FK second

# ❌ WRONG ORDER
df_products = DataGenerator(product_spec).size(1000).get_df()    # FK first → No PKs available!
df_categories = DataGenerator(category_spec).size(100).get_df()
```

### 3. Shared Checkpoint Database
Use the **same database connection** for related entities:

```python
from rand_engine.integrations.duckdb_handler import DuckDBHandler

db_conn = DuckDBHandler(db_path="checkpoints.duckdb")

# Both generators share the same checkpoint database
df_categories = DataGenerator(category_spec).db_checkpoint(db_conn).size(100).get_df()
df_products = DataGenerator(product_spec).db_checkpoint(db_conn).size(1000).get_df()
```

### 4. Watermark Must Cover Generation Time
If generating large batches, ensure **watermark > generation time**:

```python
# Generating 1M products takes ~30 seconds
# Watermark should be >= 30 seconds to ensure PK availability

"constraints": {
    "category_fk": {
        "watermark": 60  # Safe: covers 30s generation + 30s buffer
    }
}
```

### 5. Retention Period Tuning
- **Streaming:** Use larger retention (600s+) for long-running processes
- **Batch:** Default 300s is sufficient for most cases
- **High-frequency:** Reduce retention (60-120s) to minimize memory

---

## 📊 Comparison: With vs Without Cleanup

| Scenario | Without Cleanup | With Cleanup (NEW) |
|----------|----------------|---------------------|
| **Memory Usage** | Grows indefinitely | Stable (bounded) |
| **Long-running streams** | ❌ MemoryError after ~1M records | ✅ Stable indefinitely |
| **Checkpoint size** | Proportional to total generated | Proportional to watermark+retention |
| **Performance** | Degrades over time (large tables) | ✅ Consistent performance |

---

## 🧪 Advanced Example: Multi-Level Hierarchy

### Scenario: Client → Order → OrderItem
```python
from rand_engine.main.data_generator import DataGenerator
from rand_engine.integrations.duckdb_handler import DuckDBHandler

db_conn = DuckDBHandler(db_path="ecommerce.duckdb", retention_period=300)

# Level 1: Clients (PK)
client_spec = {
    "client_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "name": {"method": "distincts", "kwargs": {"distincts": ["Alice", "Bob", "Charlie"]}},
    "constraints": {
        "client_pk": {
            "tipo": "PK",
            "name": "client_pk",
            "fields": ["client_id VARCHAR(8)"]
        }
    }
}

# Level 2: Orders (FK to clients, PK for items)
order_spec = {
    "order_id": {"method": "int_zfilled", "kwargs": {"length": 10}},
    "total": {"method": "floats", "kwargs": {"min": 50.0, "max": 500.0, "decimals": 2}},
    "constraints": {
        "client_fk": {
            "tipo": "FK",
            "name": "client_pk",
            "fields": ["client_id"],
            "watermark": 60
        },
        "order_pk": {
            "tipo": "PK",
            "name": "order_pk",
            "fields": ["order_id VARCHAR(10)"]
        }
    }
}

# Level 3: OrderItems (FK to orders)
item_spec = {
    "item_id": {"method": "int_zfilled", "kwargs": {"length": 12}},
    "quantity": {"method": "integers", "kwargs": {"min": 1, "max": 10}},
    "constraints": {
        "order_fk": {
            "tipo": "FK",
            "name": "order_pk",
            "fields": ["order_id"],
            "watermark": 120
        }
    }
}

# Generate hierarchy
df_clients = DataGenerator(client_spec).db_checkpoint(db_conn).size(1000).get_df()
df_orders = DataGenerator(order_spec).db_checkpoint(db_conn).size(5000).get_df()
df_items = DataGenerator(item_spec).db_checkpoint(db_conn).size(20000).get_df()

print(f"Clients: {len(df_clients)}, Orders: {len(df_orders)}, Items: {len(df_items)}")
```

---

## 📚 Related Documentation
- **[1_DATA_GENERATOR.md](1_DATA_GENERATOR.md)** - DataGenerator methods and RandSpecs
- **[2_SPARK_GENERATOR.md](2_SPARK_GENERATOR.md)** - SparkGenerator (no constraints)
- **[3_WRITING_FILES.md](3_WRITING_FILES.md)** - File batch and streaming writers
