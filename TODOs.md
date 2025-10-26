
### 🔄 Testing ETL/ELT Pipelines

Generate **source data**, export to staging, run your pipeline, then generate **incremental loads** for testing CDC patterns.

```python
from rand_engine import DataGenerator, RandSpecs

# Step 1: Generate initial source data (1M records)
source_df = DataGenerator(RandSpecs.transactions(), seed=42).size(1_000_000).get_df()

# Step 2: Export to staging area
source_df.to_parquet("staging/transactions_batch_001.parquet", compression="snappy")
print(f"✅ Exported {len(source_df):,} records to staging")

# Step 3: Run your ETL pipeline (your code here)
# run_etl_pipeline("staging/transactions_batch_001.parquet", "warehouse/transactions")

# Step 4: Generate incremental data for testing updates/inserts
incremental_df = DataGenerator(RandSpecs.transactions(), seed=43).size(10_000).get_df()
incremental_df.to_parquet("staging/transactions_batch_002.parquet", compression="snappy")

# Step 5: Test incremental load
# run_etl_pipeline("staging/transactions_batch_002.parquet", "warehouse/transactions", mode="upsert")
```

**Use Cases:**
- ✅ Test full loads vs incremental loads
- ✅ Validate deduplication logic
- ✅ Benchmark pipeline performance with known data volumes
- ✅ Test error handling with edge cases

---

### 🚀 Load Testing APIs

Simulate **realistic API traffic** with controlled throughput for load testing REST endpoints.

```python
import requests
from rand_engine import DataGenerator, RandSpecs
from time import time

# Create user generator
users_stream = DataGenerator(RandSpecs.users()).stream_dict(
    min_throughput=10,  # 10 requests/sec minimum
    max_throughput=50   # 50 requests/sec maximum
)

# Load test user creation endpoint
api_url = "https://api.example.com/users"
created_count = 0
start_time = time()

for user in users_stream:
    response = requests.post(api_url, json=user, timeout=5)
    
    if response.status_code == 201:
        created_count += 1
        print(f"✅ Created user {user['user_id']} | Total: {created_count}")
    else:
        print(f"❌ Failed: {response.status_code} | {user['user_id']}")
    
    # Stop after 1000 users or 2 minutes
    if created_count >= 1000 or (time() - start_time) > 120:
        break

elapsed = time() - start_time
print(f"\n📊 Load Test Complete:")
print(f"  • Users created: {created_count}")
print(f"  • Time elapsed: {elapsed:.2f}s")
print(f"  • Avg throughput: {created_count/elapsed:.1f} req/s")
```


### 🗄️ Populating Development Databases

Seed **development** and **staging** databases with realistic data using DuckDB or SQLite integrations.

```python
from rand_engine import DataGenerator, RandSpecs
from rand_engine.integrations import DuckDBHandler

# Generate datasets
customers = DataGenerator(RandSpecs.customers(), seed=42).size(10_000).get_df()
orders = DataGenerator(RandSpecs.orders(), seed=42).size(50_000).get_df()

# Connect to database
db = DuckDBHandler("dev_database.duckdb")

# Create tables with constraints
db.create_table("customers", "customer_id VARCHAR(10) PRIMARY KEY, name VARCHAR(100), email VARCHAR(100)")
db.create_table("orders", "order_id VARCHAR(10) PRIMARY KEY, customer_id VARCHAR(10), total DECIMAL(10,2)")

# Insert data
db.insert_df("customers", customers, pk_cols=["customer_id"])
print(f"✅ Inserted {len(customers):,} customers")

db.insert_df("orders", orders, pk_cols=["order_id"])
print(f"✅ Inserted {len(orders):,} orders")

# Verify data
result = db.query("SELECT COUNT(*) as total FROM customers")
print(f"📊 Total customers in DB: {result['total'][0]}")

db.close()
```

**Benefits:**
- ✅ Fast local development without production data
- ✅ Reproducible environments (use same seed)
- ✅ Test migrations and schema changes safely
- ✅ Isolate development from production dependencies

---

### 🧪 QA Testing with Edge Cases

Generate datasets with **controlled edge case distribution** for comprehensive QA testing.

```python
from rand_engine import DataGenerator

# Spec with intentional edge cases
spec_edge_cases = {
    "value": {
        "method": "floats", 
        "kwargs": {"min": -999_999.99, "max": 999_999.99, "round": 2}
    },
    "status": {
        "method": "distincts", 
        "kwargs": {"distincts": ["active", "deleted", "suspended", "pending", "error"]}
    },
    "is_edge_case": {
        "method": "booleans", 
        "kwargs": {"true_prob": 0.05}  # 5% flagged as edge cases
    },
    "extreme_value": {
        "method": "floats", 
        "kwargs": {"min": -1e10, "max": 1e10, "round": 2}  # Extreme ranges
    }
}

# Generate test data
test_data = DataGenerator(spec_edge_cases, seed=789).size(10_000).get_df()

# Filter edge cases for targeted testing
edge_cases = test_data[test_data['is_edge_case'] == True]
print(f"📊 Generated {len(edge_cases)} edge cases out of {len(test_data)} total records")
print(f"\nEdge case examples:")
print(edge_cases.head())

# Test your system with edge cases
for _, row in edge_cases.iterrows():
    # Your QA test logic here
    pass
```

---

## 🔥 Advanced Features

### 🔗 Constraints & Referential Integrity ⭐ NEW in v0.6.1

**The most powerful feature!** Create realistic datasets with proper Primary Key (PK) and Foreign Key (FK) relationships, composite keys, and temporal watermarks.

**Key Capabilities:**
- ✅ **Primary Keys (PK)**: Generate unique identifiers with checkpoint tracking
- ✅ **Foreign Keys (FK)**: Reference values from PK tables with 100% integrity
- ✅ **Composite Keys**: Multi-column PKs and FKs (e.g., `client_id + client_type`)
- ✅ **Watermarks**: Temporal windows for realistic time-based relationships
- ✅ **Backend Storage**: DuckDB (in-memory/disk) or SQLite for checkpoint tables
    "constraints": {
        "category_pk": {
            "name": "category_pk",
            "tipo": "PK",
            "fields": ["category_id VARCHAR(4)"]
        }
    }
}

# Generate categories
df_categories = (
    DataGenerator(spec_categories, seed=42)
    .checkpoint(":memory:")
    .size(10)
    .get_df()
)

# 2. Create PRODUCTS (Foreign Key → categories)
spec_products = {
    "product_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 8}},
    "product_name": {"method": "distincts", "kwargs": {"distincts": [f"Product {i}" for i in range(100)]}},
    "price": {"method": "floats", "kwargs": {"min": 10.0, "max": 1000.0, "round": 2}},
    "constraints": {
        "category_fk": {
            "name": "category_pk",
            "tipo": "FK",
            "fields": ["category_id"],
            "watermark": 60  # Reference records from last 60 seconds
        }
    }
}

# Generate products
df_products = (
    DataGenerator(spec_products, seed=42)
    .checkpoint(":memory:")
    .size(1000)
    .get_df()
)

# ✅ RESULT: 100% referential integrity
# All products reference valid categories
print(f"Valid integrity: {set(df_products['category_id']).issubset(set(df_categories['category_id']))}")
# Output: Valid integrity: True
```

**Key Features:**
- **Primary Keys (PK)**: Create checkpoint tables with generated records
- **Foreign Keys (FK)**: Reference values from PK checkpoint tables
- **Composite Keys**: Multi-column PKs and FKs (e.g., `client_id + client_type`)
- **Watermarks**: Temporal windows for realistic time-based relationships
- **DuckDB/SQLite**: Checkpoint tables stored in memory or disk

📖 **Complete guide with 3-level examples:** [CONSTRAINTS.md](./docs/CONSTRAINTS.md)

---

### Correlated Columns

Generate related data (device → OS, product → status, etc.):

```python
# Example: orders() spec includes correlated currency & country
orders = DataGenerator(RandSpecs.orders()).size(1000).get_df()

# Result: 
# order_id  amount  currency  country
#       001  100.50      USD       US
#       002   85.30      EUR       DE
#       003  120.75      GBP       UK
```

### Weighted Distributions

```python
# Example: products() uses weighted categories
products = DataGenerator(RandSpecs.products()).size(10000).get_df()

# Result distribution:
# Electronics: ~40%
# Clothing: ~30%  
# Food: ~20%
# Books: ~10%
```

### Streaming Generation

```python
from rand_engine import DataGenerator, RandSpecs

# Generate continuous data stream
stream = DataGenerator(RandSpecs.events()).stream_dict(
    min_throughput=5,   # Minimum records/second
    max_throughput=15   # Maximum records/second
)

for event in stream:
    # Each record includes automatic timestamp_created
    print(f"[{event['timestamp_created']}] Event: {event['event_type']}")
    # Send to Kafka, Kinesis, etc.
```

### Multiple Export Formats

```python
from rand_engine import DataGenerator, RandSpecs

spec = RandSpecs.transactions()

# CSV with compression
DataGenerator(spec).write.size(100000).format("csv").option("compression", "gzip").save("data.csv.gz")

# Parquet with Snappy
DataGenerator(spec).write.size(1000000).format("parquet").option("compression", "snappy").save("data.parquet")

# JSON
DataGenerator(spec).write.size(50000).format("json").save("data.json")
```

### Reproducible Data

```python
from rand_engine import DataGenerator, RandSpecs

# Same seed = identical data
df1 = DataGenerator(RandSpecs.customers(), seed=42).size(1000).get_df()
df2 = DataGenerator(RandSpecs.customers(), seed=42).size(1000).get_df()

assert df1.equals(df2)  # True - perfect reproducibility
```

---

## 🗂️ Export & Integration

### File Formats

```python
from rand_engine import DataGenerator, RandSpecs

generator = DataGenerator(RandSpecs.orders())

# CSV
generator.write.size(10000).format("csv").save("orders.csv")

# Parquet (recommended for large datasets)
generator.write.size(1000000).format("parquet").save("orders.parquet")

# JSON
generator.write.size(5000).format("json").save("orders.json")

# Multiple files (partitioned)
generator.write.size(1000000).option("numFiles", 10).format("parquet").save("orders/")
```

### Writing Modes: Batch vs Streaming

`rand_engine` supports two distinct writing modes:

**Batch Mode** (`.write`): Generate all data at once

```python
# Single file
DataGenerator(spec).write \
    .size(10000) \
    .format("parquet") \
    .option("compression", "snappy") \
    .save("output/data.parquet")

# Multiple files (parallel processing)
DataGenerator(spec).write \
    .size(1000000) \
    .option("numFiles", 5) \
    .format("parquet") \
    .save("output/data.parquet")
# Creates: part_uuid1.parquet, part_uuid2.parquet, ...
```

**Streaming Mode** (`.writeStream`): Continuous generation over time

```python
# Stream for 1 hour, new file every minute
DataGenerator(spec).writeStream \
    .size(500) \
    .format("json") \
    .option("compression", "gzip") \
    .option("timeout", 3600) \
    .trigger(frequency=60) \
    .start("output/events")
# Creates 60 files over 1 hour
```

**Compression Support:**
- **CSV/JSON**: gzip, bz2, zip, xz
- **Parquet**: snappy (default), gzip, zstd, lz4, brotli

📖 **Complete guide with examples:** [WRITING_FILES.md](./docs/WRITING_FILES.md)

### Database Integration

**DuckDB:**

```python
from rand_engine import DataGenerator, RandSpecs
from rand_engine.integrations._duckdb_handler import DuckDBHandler

# Generate data
df = DataGenerator(RandSpecs.employees()).size(10000).get_df()

# Insert into DuckDB
db = DuckDBHandler("analytics.duckdb")
db.create_table("employees", "employee_id VARCHAR(10) PRIMARY KEY")
db.insert_df("employees", df, pk_cols=["employee_id"])

# Query
result = db.select_all("employees")
print(result.head())

db.close()
```

**SQLite:**

```python
from rand_engine.integrations._sqlite_handler import SQLiteHandler

db = SQLiteHandler("test.db")
db.create_table("users", "user_id VARCHAR(10) PRIMARY KEY")
db.insert_df("users", df, pk_cols=["user_id"])
db.close()
```

---

## 📖 Exploring Available Specs

Want to see what's inside each pre-built spec?

```python
from rand_engine import RandSpecs
import json

# View any spec structure
spec = RandSpecs.customers()
print(json.dumps(spec, indent=2))

# Output shows all fields and generation methods:
# {
#   "customer_id": {
#     "method": "unique_ids",
#     "kwargs": {"strategy": "zint", "prefix": "C"}
#   },
#   "name": {
#     "method": "distincts",
#     "kwargs": {"distincts": ["John Smith", "Jane Brown", ...]}
#   },
#   ...
# }
```

**Try different specs:**

```python
# See all available specs
print(RandSpecs.products())
print(RandSpecs.transactions())
print(RandSpecs.devices())
print(RandSpecs.events())
```

Each spec demonstrates different generation techniques - use them as templates for your own custom specs!

---

## 🛠️ Creating Custom Specs

### Basic Template

```python
from rand_engine import DataGenerator

my_spec = {
    "id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint"}
    },
    "name": {
        "method": "distincts",
        "kwargs": {"distincts": ["Alice", "Bob", "Charlie"]}
    },
    "value": {
        "method": "floats",
        "kwargs": {"min": 0.0, "max": 100.0, "round": 2}
    }
}

df = DataGenerator(my_spec).size(1000).get_df()
```

### Spec Validation

Enable validation to catch errors early:

```python
invalid_spec = {
    "age": {
        "method": "integers"  # Missing required "min" and "max"
    }
}

try:
    generator = DataGenerator(invalid_spec, validate=True)
except Exception as e:
    print(e)
    # ❌ Column 'age': Missing required parameter 'min'
    #    Correct example:
    #    {
    #        "age": {
    #            "method": "integers",
    #            "kwargs": {"min": 18, "max": 65}
    #        }
    #    }
```

**Validates:**
- Required parameters for each method
- Constraints structure (PK/FK, fields, watermark)
- Data types and ranges
- Provides educational error messages with examples