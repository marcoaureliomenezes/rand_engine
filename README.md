# Rand Engine

**High-performance synthetic data generation for testing, development, and prototyping.**

A Python library for generating millions of rows of realistic synthetic data through declarative specifications. Built on NumPy and Pandas for maximum performance.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-212%20passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

---

## 📦 Installation

```bash
pip install rand-engine
```

---

## 🎯 Who Is This For?

- **Data Engineers**: Test ETL/ELT pipelines without production data dependencies
- **QA Engineers**: Generate realistic datasets for load and integration testing
- **Data Scientists**: Mock data during model development and validation
- **Backend Developers**: Populate development and staging environments
- **BI Professionals**: Create demos and POCs without exposing sensitive data

---

## 🚀 Quick Start

### 1. Use Pre-Built Examples (Fastest Way)

Get started immediately with ready-to-use specifications:

```python
from rand_engine import DataGenerator, RandSpecs

# Generate 10,000 customer records
customers = DataGenerator(RandSpecs.customers(), seed=42).size(10000).get_df()
print(customers.head())
```

**Output:**
```
   customer_id       name  age                    email  is_active  account_balance
0    C00000001  John Smith   42    john.smith@email.com       True         15432.50
1    C00000002  Jane Brown   28   jane.brown@email.com       True          8721.33
2    C00000003   Bob Wilson   56   bob.wilson@email.com      False         42156.89
3    C00000004  Alice Davis   33  alice.davis@email.com       True         23400.12
4    C00000005   Tom Miller   49   tom.miller@email.com       True         31245.67
```

**Available Pre-Built Specs:**

```python
from rand_engine import RandSpecs

# 🛒 E-commerce & Retail
RandSpecs.customers()    # Customer profiles (6 fields)
RandSpecs.products()     # Product catalog (6 fields)
RandSpecs.orders()       # Order records with currency/country (6 fields)
RandSpecs.invoices()     # Invoice records (6 fields)
RandSpecs.shipments()    # Shipping data with carrier/destination (6 fields)

# 💰 Financial
RandSpecs.transactions() # Financial transactions (6 fields)

# 👥 HR & People
RandSpecs.employees()    # Employee records with dept/level/role (6 fields)
RandSpecs.users()        # Application users (6 fields)

# 🔧 IoT & Systems
RandSpecs.devices()      # IoT device data with status/priority (6 fields)
RandSpecs.events()       # Event logs (6 fields)
```

**Complete Example:**

```python
from rand_engine import DataGenerator, RandSpecs

# Generate products
products = DataGenerator(RandSpecs.products()).size(1000).get_df()

# Generate orders
orders = DataGenerator(RandSpecs.orders(), seed=123).size(50000).get_df()

# Generate employee data
employees = DataGenerator(RandSpecs.employees()).size(500).get_df()

# Export to files
DataGenerator(RandSpecs.customers()).write \
    .size(100000) \
    .format("parquet") \
    .option("compression", "snappy") \
    .save("customers.parquet")
```

---

### 2. Create Custom Specifications

Build your own specs for specific use cases:

```python
from rand_engine import DataGenerator

# Simple specification
spec = {
    "user_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint", "length": 8}
    },
    "age": {
        "method": "integers",
        "kwargs": {"min": 18, "max": 65}
    },
    "salary": {
        "method": "floats",
        "kwargs": {"min": 30000.0, "max": 150000.0, "round": 2}
    }
}

df = DataGenerator(spec, seed=42).size(10000).get_df()
```

---

## 📚 Core Generation Methods

| Method | Description | Example Use Case |
|--------|-------------|------------------|
| **unique_ids** | Unique identifiers | User IDs, order numbers |
| **integers** | Random integers | Ages, quantities, counts |
| **floats** | Random decimals | Prices, weights, measurements |
| **floats_normal** | Normal distribution | Heights, temperatures, scores |
| **booleans** | True/False with probability | Active flags, feature toggles |
| **distincts** | Random selection | Categories, statuses, types |
| **distincts_prop** | Weighted selection | Product mix, user tiers |
| **unix_timestamps** | Date/time values | Created dates, event times |

**Simple Example:**

```python
spec = {
    "product_id": {"method": "unique_ids", "kwargs": {"strategy": "zint"}},
    "price": {"method": "floats", "kwargs": {"min": 9.99, "max": 999.99, "round": 2}},
    "category": {"method": "distincts", "kwargs": {"distincts": ["Electronics", "Clothing", "Food"]}},
    "in_stock": {"method": "booleans", "kwargs": {"true_prob": 0.85}}
}

products = DataGenerator(spec).size(5000).get_df()
```

---

## 🎨 Real-World Use Cases

### Testing ETL Pipelines

```python
from rand_engine import DataGenerator, RandSpecs

# Generate source data
source_df = DataGenerator(RandSpecs.transactions(), seed=42).size(1_000_000).get_df()

# Export to staging
source_df.to_parquet("staging/transactions.parquet")

# Run your ETL pipeline
# ...

# Generate more data for incremental loads
incremental_df = DataGenerator(RandSpecs.transactions()).size(10_000).get_df()
```

### Load Testing APIs

```python
import requests
from rand_engine import DataGenerator, RandSpecs

# Generate test users
stream = DataGenerator(RandSpecs.users()).stream_dict(min_throughput=10, max_throughput=50)

for user in stream:
    response = requests.post("https://api.example.com/users", json=user)
    print(f"Created user {user['user_id']}: {response.status_code}")
```

### Populating Development Databases

```python
from rand_engine import DataGenerator, RandSpecs
from rand_engine.integrations._duckdb_handler import DuckDBHandler

# Generate data
customers = DataGenerator(RandSpecs.customers()).size(10_000).get_df()
orders = DataGenerator(RandSpecs.orders()).size(50_000).get_df()

# Insert into database
db = DuckDBHandler("dev_database.duckdb")
db.create_table("customers", "customer_id VARCHAR(10) PRIMARY KEY")
db.insert_df("customers", customers, pk_cols=["customer_id"])
db.create_table("orders", "order_id VARCHAR(10) PRIMARY KEY")
db.insert_df("orders", orders, pk_cols=["order_id"])
db.close()
```

### QA Testing with Edge Cases

```python
from rand_engine import DataGenerator

# Mix of normal and edge cases
spec = {
    "value": {"method": "floats", "kwargs": {"min": -999999.99, "max": 999999.99, "round": 2}},
    "status": {"method": "distincts", "kwargs": {"distincts": ["active", "deleted", "suspended", "pending"]}},
    "edge_case": {"method": "booleans", "kwargs": {"true_prob": 0.05}}  # 5% edge cases
}

test_data = DataGenerator(spec, seed=789).size(1000).get_df()
edge_cases = test_data[test_data['edge_case'] == True]
```

---

## 🔥 Advanced Features

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
generator.write.size(1000000).num_files(10).format("parquet").save("orders/")
```

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

---

## 🏗️ Architecture

### Design Philosophy

- **Declarative**: Specify what you want, not how to generate it
- **Performance**: Built on NumPy for vectorized operations (millions of rows/second)
- **Simplicity**: Pre-built examples for immediate use
- **Extensibility**: Easy to create custom specifications

### Public API

```python
from rand_engine import DataGenerator, RandSpecs

# That's it! Simple and clean.
```

All internal modules (prefixed with `_`) are implementation details.

---

## 🧪 Quality & Testing

- **212 tests** passing
- **Comprehensive coverage** of all generation methods
- **Validated** on millions of generated records
- **Battle-tested** in production ETL pipelines

```bash
# Run tests
pytest

# With coverage report
pytest --cov=rand_engine --cov-report=html
```

---

## 💡 Tips & Best Practices

### For Data Engineers

- Use `seed` parameter for reproducible test data
- Export to Parquet with compression for large datasets
- Use streaming mode for continuous data generation
- Leverage pre-built specs to quickly scaffold test environments

### For QA Engineers

- Start with pre-built specs (RandSpecs)
- Use validation mode (`validate=True`) during development
- Generate edge cases with low probability booleans
- Create multiple test datasets with different seeds

### Performance Tips

- Generate data in batches for optimal memory usage
- Use Parquet format for large datasets (10x smaller than CSV)
- Enable compression for file exports
- Reuse DataGenerator instances when generating multiple datasets

---

## 📄 Requirements

- **Python**: >= 3.10
- **numpy**: >= 2.1.1
- **pandas**: >= 2.2.2
- **faker**: >= 28.4.1 (optional)
- **duckdb**: >= 1.1.0 (optional)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/marcoaureliomenezes/rand_engine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/marcoaureliomenezes/rand_engine/discussions)
- **Email**: marcourelioreislima@gmail.com

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🌟 Star History

If you find this project useful, consider giving it a ⭐ on GitHub!

---

**Built with ❤️ for Data Engineers, QA Engineers, and the entire data community**
