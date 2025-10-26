# Rand Engine

**High-performance synthetic data generation for testing, development, and prototyping.**

A Python library for generating millions of rows of realistic synthetic data through declarative specifications. Built on NumPy and Pandas for maximum performance.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-236%20passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
[![Version](https://img.shields.io/badge/version-0.6.1-orange.svg)]()

---

## 🔥 What's New in v0.6.1

- ✅ **Constraints System**: Primary Keys (PK) and Foreign Keys (FK) for referential integrity between specs
- ✅ **Composite Keys**: Support for multi-column primary and foreign keys
- ✅ **Watermarks**: Temporal windows for realistic time-based relationships
- ✅ **Enhanced Validation**: Educational error messages with examples
- ✅ **Logging System**: Transparent logging with Python's built-in logger
- ✅ **Windows Support**: Full cross-platform compatibility (Linux, macOS, Windows)

📖 **Complete documentation:** [CONSTRAINTS.md](./docs/CONSTRAINTS.md) | [EXAMPLES.md](./EXAMPLES.md)

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

### 1. Pre-Built Examples (Fastest Way to Start)

DataGenerator produces synthetic datasets in seconds. It leverages **NumPy** and **Pandas** for blazing-fast random data generation.

Creating 1 million rows is as simple as:
- Choose a built-in **RandSpec** (e.g., `customers`, `orders`, `transactions`)
- Set the **size** (number of rows)
- Optionally set a **seed** for reproducibility
- Call `.get_df()` to obtain a pandas DataFrame

**What's a RandSpec?** A declarative specification dictionary that defines your dataset's structure and generation rules. 

Rand Engine includes **10+ ready-to-use RandSpecs** covering common business domains—no configuration needed.

```python
from rand_engine import DataGenerator, RandSpecs

# Generate 1 million customer records in seconds
customers_spec = RandSpecs.customers()  # Pre-built specification
df_customers = DataGenerator(customers_spec, seed=42).size(1_000_000).get_df()

print(df_customers.head())
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

---

Size parameter can be an integer or a callable function that returns an integer.

```python
from rand_engine import DataGenerator, RandSpecs
from random import randint

lambda_size = lambda: randint(500_000, 2_000_000)
# Generate 1 million customer records in seconds
customers_spec = RandSpecs.customers()  # Pre-built specification
df_customers = DataGenerator(customers_spec, seed=42).size(lambda_size).get_df()

print(df_customers.shape)
```

### 2. Databricks Integration

Seamlessly integrate with **Databricks** and other Spark environments. Generate synthetic data and convert to Spark DataFrames with zero friction.

```python
from rand_engine import DataGenerator, RandSpecs

# Generate synthetic data for Databricks
transactions_spec = RandSpecs.transactions()
df_pandas = DataGenerator(transactions_spec, seed=42).size(1_000_000).get_df()

# Option 1: Display pandas DataFrame
display(df_pandas)

# Option 2: Convert to Spark DataFrame for distributed processing
df_spark = spark.createDataFrame(df_pandas)
display(df_spark)

# Write directly to Delta Lake, Parquet, or any Spark-supported format
df_spark.write.format("delta").mode("overwrite").save("/path/to/delta/table")
```

---

### 3. Explore Built-In RandSpecs

Rand Engine provides **10+ production-ready specifications** across multiple business domains. Each spec generates realistic, correlated data with 6+ fields.

```python
from rand_engine import DataGenerator, RandSpecs

# 🛍️ E-Commerce & Retail
builtin_specs = [
    RandSpecs.customers(),    # Customer profiles with contact info
    RandSpecs.products(),     # Product catalog with pricing
    RandSpecs.orders(),       # Orders with currency/country correlation
    RandSpecs.invoices(),     # Invoice records with payment details
    RandSpecs.shipments(),    # Shipping data with carrier/destination
]

# 💰 Financial Services
builtin_specs += [
    RandSpecs.transactions(), # Financial transactions with amounts
]

# 👥 HR & User Management
builtin_specs += [
    RandSpecs.employees(),    # Employee records (dept/level/role)
    RandSpecs.users(),        # Application users with auth data
]

# 🔧 IoT & System Monitoring
builtin_specs += [
    RandSpecs.devices(),      # IoT device telemetry
    RandSpecs.events(),       # System event logs
]

# Generate millions of rows from any spec
for spec in builtin_specs:
    df = DataGenerator(spec, seed=42).size(1_000_000).get_df()
    print(f"\n{spec['__meta__']['name']}:")
    print(df.head())
```

**💡 Pro Tip:** These specs include realistic correlations (e.g., `orders.currency` matches `orders.country`, `employees.level` correlates with `salary`). Perfect for testing real-world scenarios!

---

### 4. File Writing Capabilities

Generate and write synthetic data directly to files—no intermediate DataFrames needed. Supports **CSV**, **Parquet**, and **JSON** with advanced options.

#### 4.1. Supported Formats & Compression

| Format | Compression Options | Use Case |
|--------|---------------------|----------|
| **CSV** | None, gzip, zip, bz2 | Human-readable, spreadsheet imports |
| **Parquet** | None, snappy, gzip | Columnar analytics, data lakes |
| **JSON** | None, gzip, zip, bz2 | APIs, document stores, config files |

---

#### 4.2. Batch Writing Mode

Write synthetic data in **single** or **multiple** files with full control over format, compression, and write modes.

- As rand-engine generates pandas DataFrames under the hood, data can be written efficiently using Pandas' built-in I/O capabilities.
- Although users can easily obtain DataFrames via `.get_df()` and write them manually, the built-in `.write` interface simplifies the process significantly.

**📝 Single File Writing**

Write an entire dataset to a single file—ideal for small to medium datasets or when you need one consolidated output.


```python
from rand_engine import DataGenerator, RandSpecs

# Write 10,000 customer records to a single CSV file
local_path = "./data/customers"
# Or Databricks: "/Volumes/prd/demo_volumes/rand_engine_data/customers"

(
    DataGenerator(RandSpecs.customers())
    .write
    .size(10_000)
    .format("csv")                    # Format: csv, json, or parquet
    .mode("overwrite")                # Mode: overwrite or append
    .option("compression", None)      # Optional: gzip, zip, bz2
    .save(local_path)
)
```

**Key Features:**
- ✅ **Auto file extension**: `customers` → `customers.csv` automatically
- ✅ **Overwrite mode**: Replaces existing file
- ✅ **Append mode**: Adds new records to existing file
- ✅ **Full path control**: Specify exact output location

**Result:** Single file created at `./data/customers.csv` with 10,000 rows.

---

**📦 Multiple Files Writing**

- Write large datasets using **multiple batches**. 
- Perfect for generating massive datasets on disk without overwhelming memory.

```python
from rand_engine import DataGenerator, RandSpecs

# Write 500,000 records split across 5 CSV files (100,000 rows each)
(
    DataGenerator(RandSpecs.customers())
    .write
    .size(100_000)
    .format("csv")
    .mode("overwrite")
    .option("numFiles", 5)           # Split into 5 files
    .option("compression", "gzip")   # Compress each file
    .save("./data/customers_multi")
)
```

**Output Structure:**
```
data/
└── customers_multi/
    ├── part_a3f2c91e.csv.gz    (10,000 rows)
    ├── part_b7e4d23a.csv.gz    (10,000 rows)
    ├── part_c1f8e45b.csv.gz    (10,000 rows)
    ├── part_d9a2f67c.csv.gz    (10,000 rows)
    └── part_e5b3g89d.csv.gz    (10,000 rows)
```

**Important Behaviors:**
- 🗂️ **Folder creation**: `numFiles > 1` automatically creates a directory
- ➕ **Append mode**: Adds new files to existing folder without removing old ones
- 🔄 **Overwrite mode**: Clears folder contents before writing new files
- 🎲 **Random names**: Files get unique identifiers (`part_<hash>.<ext>`)

---

**🎯 Advanced Example: Testing All Format/Compression Combinations**

Easy for Data Engineers to generate synthetic data for **learning**, **development**, and **testing**.
- Test your entire data pipeline with different format and compression options.
- Users can quickly understand different performance and storage trade-offs.
- Great for benchmarking read/write speeds and compression ratios.

```python
from rand_engine import DataGenerator, RandSpecs

base_path = "./data/batch_tests"

# Define all format and compression combinations to test
test_configs = [
    # CSV variations
    {"format": "csv", "compression": None,     "path": f"{base_path}/csv/default/customers"},
    {"format": "csv", "compression": "gzip",   "path": f"{base_path}/csv/gzip/customers"},
    {"format": "csv", "compression": "zip",    "path": f"{base_path}/csv/zip/customers"},
    {"format": "csv", "compression": "bz2",    "path": f"{base_path}/csv/bz2/customers"},
    
    # JSON variations
    {"format": "json", "compression": None,    "path": f"{base_path}/json/default/customers"},
    {"format": "json", "compression": "gzip",  "path": f"{base_path}/json/gzip/customers"},
    {"format": "json", "compression": "zip",   "path": f"{base_path}/json/zip/customers"},
    {"format": "json", "compression": "bz2",   "path": f"{base_path}/json/bz2/customers"},
    
    # Parquet variations
    {"format": "parquet", "compression": None,    "path": f"{base_path}/parquet/default/customers"},
    {"format": "parquet", "compression": "snappy", "path": f"{base_path}/parquet/snappy/customers"},
    {"format": "parquet", "compression": "gzip",   "path": f"{base_path}/parquet/gzip/customers"},
]

# Test 1: Write single files (10,000 rows each)
print("📝 Writing single files...")
for config in test_configs:
    (
        DataGenerator(RandSpecs.customers())
        .write
        .size(10_000)
        .format(config["format"])
        .mode("overwrite")
        .option("compression", config["compression"])
        .save(config["path"])
    )
    print(f"  ✅ {config['format']} ({config['compression'] or 'none'}) → {config['path']}")

# Test 2: Write multiple files (5 files × 10,000 rows = 50,000 total)
print("\n📦 Writing multiple files...")
for config in test_configs:
    multi_path = config["path"].replace("/batch_tests/", "/batch_tests/multi_")
    (
        DataGenerator(RandSpecs.customers())
        .write
        .size(50_000)
        .format(config["format"])
        .mode("overwrite")
        .option("numFiles", 5)
        .option("compression", config["compression"])
        .save(multi_path)
    )
    print(f"  ✅ {config['format']} ({config['compression'] or 'none'}) → {multi_path}/ (5 files)")
```

**Use Cases:**
- 🧪 **Testing data pipelines** with different file formats
- 📊 **Benchmarking** compression ratios and read/write performance
- 🔄 **CI/CD validation** of file processing workflows
- 📁 **Data lake ingestion** testing with various formats

---

#### 4.3. Streaming Write Mode

Generate and write data **continuously** with controlled throughput—perfect for testing real-time pipelines, Kafka producers, or event-driven systems.

```python
from rand_engine import DataGenerator, RandSpecs

# Stream customer records at 20k records/second
(
    DataGenerator(RandSpecs.customers())
    .size(10**5)
    .writeStream
    .format("json")
    .mode("overwrite")
    .option("compression", "gzip")
    .option("timeout", 100)
    .trigger(frequency=5)
    .start(path="./data/stream/customers")
)
```

**Key Features:**
- 🕐 **Controlled throughput**: Simulate realistic event rates (20k records/sec)
- ♾️ **Continuous generation**: Runs indefinitely until stopped or timeout reached
- ⏱️ **Auto timestamps**: Each record includes `timestamp_created` field
- 📂 **Append mode**: New files created every N records (configurable)
- 🔄 **Databricks integration**: Perfect to feed Auto loader on Databricks

**Output Structure:**
```
data/stream/customers/
├── stream_2025-10-25_14-30-05.json.gz   (1,000 records)
├── stream_2025-10-25_14-31-12.json.gz   (1,000 records)
├── stream_2025-10-25_14-32-18.json.gz   (1,000 records)
└── ... (continues streaming)
```

**Use Cases:**
- 🌊 **Kafka testing**: Simulate producers with realistic data
- 🔄 **CDC pipelines**: Test change data capture workflows
- 📊 **Real-time analytics**: Feed data to streaming platforms (Spark Streaming, Flink)
- 🧪 **Load testing**: Stress-test event ingestion systems

---

### 5. Build Custom Specifications

Ready to create your own specs? Define custom data structures with full control over generation logic.

```python
from rand_engine import DataGenerator

# Define your custom specification
custom_spec = {
    "user_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint", "length": 8}  # Zero-padded integers: 00000001
    },
    "age": {
        "method": "integers",
        "kwargs": {"min": 18, "max": 65}             # Random integers
    },
    "salary": {
        "method": "floats",
        "kwargs": {"min": 30_000.0, "max": 150_000.0, "round": 2}  # Decimals
    },
    "is_premium": {
        "method": "booleans",
        "kwargs": {"true_prob": 0.15}                # 15% will be True
    },
    "department": {
        "method": "distincts",
        "kwargs": {"distincts": ["Engineering", "Sales", "Marketing", "HR"]}
    }
}

# Generate 10 million rows
df = DataGenerator(custom_spec, seed=42).size(10_000_000).get_df()
print(df.head())
```

**Spec Anatomy:**
- `"method"`: Core generation function (see table below)
- `"kwargs"`: Method-specific parameters
- **Declarative**: Define _what_ you want, not _how_ to generate it

---

## 📚 Core Generation Methods Reference

Complete API for building custom specifications:

| Method | Description | Parameters | Example |
|--------|-------------|------------|---------|
| **`unique_ids`** | Unique identifiers | `strategy`: `"zint"`, `"uuid4"`, `"sequence"`<br>`length`: digits (zint only) | User IDs, order numbers, SKUs |
| **`integers`** | Random integers | `min`: minimum value<br>`max`: maximum value | Ages, quantities, counts |
| **`floats`** | Random decimals | `min`: minimum value<br>`max`: maximum value<br>`round`: decimal places | Prices, weights, percentages |
| **`floats_normal`** | Normal distribution | `mean`: center value<br>`std`: spread<br>`round`: decimals | Heights, test scores, temperatures |
| **`booleans`** | True/False flags | `true_prob`: probability of True (0.0-1.0) | Active flags, feature toggles |
| **`distincts`** | Random selection | `distincts`: list of values | Categories, statuses, types |
| **`distincts_prop`** | Weighted selection | `distincts`: `{value: weight, ...}` | Product mix (70% A, 30% B) |
| **`unix_timestamps`** | Date/time values | `start`: start date (YYYY-MM-DD)<br>`end`: end date<br>`formato`: output format | Created dates, event times |

**Quick Example:**

```python
# Product catalog with realistic distributions
product_spec = {
    "product_id": {
        "method": "unique_ids", 
        "kwargs": {"strategy": "zint", "length": 10}
    },
    "price": {
        "method": "floats", 
        "kwargs": {"min": 9.99, "max": 999.99, "round": 2}
    },
    "category": {
        "method": "distincts", 
        "kwargs": {"distincts": ["Electronics", "Clothing", "Food", "Books"]}
    },
    "in_stock": {
        "method": "booleans", 
        "kwargs": {"true_prob": 0.85}  # 85% in stock
    },
    "rating": {
        "method": "floats_normal",
        "kwargs": {"mean": 4.2, "std": 0.8, "round": 1}  # Bell curve around 4.2★
    }
}

df_products = DataGenerator(product_spec, seed=123).size(1_000_000).get_df()
print(df_products)
```

📖 **For advanced examples:** See [EXAMPLES.md](./EXAMPLES.md) for correlated columns, composite keys, and more.

---

## 🎨 Real-World Use Cases

### 🛒 E-Commerce with Referential Integrity

Create **realistic multi-level datasets** with proper Primary Key (PK) and Foreign Key (FK) relationships. Rand Engine uses an internal checkpoint database (DuckDB/SQLite) to ensure 100% referential integrity.

```python
from rand_engine import DataGenerator

# Level 1: Categories (Primary Key)
spec_categories = {
    "category_id": {
        "method": "unique_ids", 
        "kwargs": {"strategy": "zint", "length": 4}
    },
    "category_name": {
        "method": "distincts", 
        "kwargs": {"distincts": ["Electronics", "Books", "Clothing", "Home"]}
    },
    "constraints": {
        "category_pk": {
            "name": "category_pk",
            "tipo": "PK",
            "fields": ["category_id VARCHAR(4)"]
        }
    }
}

# Level 2: Products (Foreign Key → Categories)
spec_products = {
    "product_id": {
        "method": "unique_ids", 
        "kwargs": {"strategy": "zint", "length": 8}
    },
    "product_name": {
        "method": "distincts", 
        "kwargs": {"distincts": [f"Product {i:03d}" for i in range(100)]}
    },
    "price": {
        "method": "floats", 
        "kwargs": {"min": 10.0, "max": 1000.0, "round": 2}
    },
    "constraints": {
        "product_pk": {
            "name": "product_pk",
            "tipo": "PK",
            "fields": ["product_id VARCHAR(8)"]
        },
        "category_fk": {
            "name": "category_pk",  # References category_pk constraint
            "tipo": "FK",
            "fields": ["category_id"],
            "watermark": 60  # Only reference categories created in last 60 records
        }
    }
}

# Level 3: Orders (Foreign Key → Products)
spec_orders = {
    "order_id": {
        "method": "unique_ids", 
        "kwargs": {"strategy": "uuid4"}
    },
    "quantity": {
        "method": "integers", 
        "kwargs": {"min": 1, "max": 10}
    },
    "total": {
        "method": "floats", 
        "kwargs": {"min": 10.0, "max": 5000.0, "round": 2}
    },
    "constraints": {
        "product_fk": {
            "name": "product_pk",  # References product_pk constraint
            "tipo": "FK",
            "fields": ["product_id"],
            "watermark": 120
        }
    }
}

# Generate datasets (order matters: Categories → Products → Orders)
df_categories = DataGenerator(spec_categories).size(10).get_df()
df_products = DataGenerator(spec_products).size(100).get_df()
df_orders = DataGenerator(spec_orders).size(1_000).get_df()

# Verify referential integrity
print(f"✅ All products reference valid categories: {set(df_products['category_id']).issubset(set(df_categories['category_id']))}")
print(f"✅ All orders reference valid products: {set(df_orders['product_id']).issubset(set(df_products['product_id']))}")
```

📖 **Complete constraints guide:** [CONSTRAINTS.md](./docs/CONSTRAINTS.md)

---



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

- **236 tests** passing (20 new constraint tests in v0.6.1)
- **Comprehensive coverage** of all generation methods
- **Validated** on millions of generated records
- **Battle-tested** in production ETL pipelines
- **Constraint validation** with 100% integrity checks

```bash
# Run tests
pytest

# Run constraint tests only
pytest tests/test_8_consistency.py -v

# With coverage report
pytest --cov=rand_engine --cov-report=html
```

---

## 💡 Tips & Best Practices

### For Data Engineers

- Use `seed` parameter for reproducible test data
- Export to Parquet with compression for large datasets
- Use streaming mode for continuous data generation
- Leverage **constraints** for multi-table data generation with referential integrity
- Use `.checkpoint(":memory:")` for in-memory databases or `.checkpoint("path/to/db.duckdb")` for persistence

### For QA Engineers

- Start with pre-built specs (RandSpecs)
- Use validation mode (`validate=True`) during development
- Generate edge cases with low probability booleans
- Create multiple test datasets with different seeds
- Test PK/FK relationships with constraints for realistic scenarios

### Performance Tips

- Generate data in batches for optimal memory usage
- Use Parquet format for large datasets (10x smaller than CSV)
- Enable compression for file exports
- Reuse DataGenerator instances when generating multiple datasets
- Use watermarks to control FK relationship size (avoid loading entire checkpoint tables)

### Constraints Best Practices

- Use **composite keys** for complex relationships (e.g., `client_id + client_type`)
- Set appropriate **watermarks** (60-3600 seconds) based on data freshness requirements
- Use **in-memory databases** (`:memory:`) for testing, disk-based for production
- Generate PK specs before FK specs to ensure checkpoint tables exist
- Validate integrity with set operations: `set(fk_values).issubset(set(pk_values))`

📖 **50+ production-ready examples:** [EXAMPLES.md](./EXAMPLES.md)

---

## 📄 Requirements

- **Python**: >= 3.10
- **numpy**: >= 2.1.1
- **pandas**: >= 2.2.2
- **faker**: >= 28.4.1 (optional, for realistic names/addresses)
- **duckdb**: >= 1.1.0 (optional, for constraints with DuckDB)
- **sqlite3**: Built-in Python (for constraints with SQLite)

---

## 📚 Documentation

- **[EXAMPLES.md](./EXAMPLES.md)**: 50+ production-ready examples (1,600+ lines)
- **[CONSTRAINTS.md](./docs/CONSTRAINTS.md)**: Complete guide to PK/FK system (900+ lines)
- **[API_REFERENCE.md](./docs/API_REFERENCE.md)**: Full method reference
- **[LOGGING.md](./docs/LOGGING.md)**: Logging configuration guide

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
