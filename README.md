# Rand Engine

**High-performance synthetic data generation for testing, development, and prototyping.**

A Python library for generating millions of rows of realistic synthetic data through declarative specifications. Built on NumPy and Pandas for maximum performance.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-494%20passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
[![Version](https://img.shields.io/badge/version-0.7.0-orange.svg)]()

---

## 🔥 What's New in v0.7.0

- ✅ **Simplified Validators**: Architecture streamlined from 4 to 2 validator files (37% code reduction)
- ✅ **Clear Separation**: `CommonValidator` for common methods, `AdvancedValidator` for advanced patterns
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

## 🎯 Core Capabilities

Rand Engine provides two powerful generators for different use cases:

### 1. **DataGenerator** - Pandas DataFrames
Generate **pandas DataFrames** for local development, testing, and data analysis. Supports all common methods **plus advanced patterns** like correlated columns, complex patterns, and foreign keys.

```python
from rand_engine.main.data_generator import DataGenerator
from rand_engine.examples.common_rand_specs import CommonRandSpecs

# Generate pandas DataFrame with 1 million rows
df = DataGenerator(CommonRandSpecs.customers(), seed=42).size(1_000_000).get_df()
print(df.head())
```

**Key Features:**
- ✅ **Common Methods**: integers, floats, booleans, dates, distincts, etc.
- ✅ **Advanced Methods**: `distincts_map`, `distincts_multi_map`, `distincts_map_prop`, `complex_distincts`
- ✅ **Constraints System**: Primary Keys (PK) and Foreign Keys (FK) for referential integrity
- ✅ **File Writing**: Direct export to CSV, Parquet, JSON with compression
- ✅ **Transformers**: Apply custom functions to columns or entire DataFrames

---

### 2. **SparkGenerator** - Spark DataFrames
Generate **Spark DataFrames** directly for distributed environments like **Databricks**, **AWS EMR**, or **Azure Synapse**. Perfect for testing big data pipelines.

```python
from rand_engine.main.spark_generator import SparkGenerator
from rand_engine.examples.common_rand_specs import CommonRandSpecs

# In Databricks or any Spark environment
from pyspark.sql import functions as F

df_spark = SparkGenerator(spark, F, CommonRandSpecs.orders()).size(10_000_000).get_df()
display(df_spark)
```

**Key Features:**
- ✅ **Common Methods**: All standard generation methods (integers, floats, dates, etc.)
- ✅ **Distributed Generation**: Leverages Spark's parallelism for massive datasets
- ✅ **Databricks Ready**: Works seamlessly in Databricks notebooks
- ⚠️ **Advanced Methods**: Not yet supported (returns NULL for compatibility)

**Important:** SparkGenerator uses **common methods only**. For advanced patterns (correlated columns, complex patterns), use DataGenerator and convert to Spark:

```python
# Generate with DataGenerator, then convert to Spark
from rand_engine.main.data_generator import DataGenerator
from rand_engine.examples.advanced_rand_specs import AdvancedRandSpecs

df_pandas = DataGenerator(AdvancedRandSpecs.products()).size(100_000).get_df()
df_spark = spark.createDataFrame(df_pandas)
```

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
from rand_engine.main.data_generator import DataGenerator
from rand_engine.examples.common_rand_specs import CommonRandSpecs

# Generate 1 million customer records in seconds
df_customers = DataGenerator(CommonRandSpecs.customers(), seed=42).size(1_000_000).get_df()
print(df_customers.head())
```

**Output:**
```
   customer_id  age           city  total_spent  is_premium registration_date
0    uuid-001    42      São Paulo      1523.50        True        2023-05-12
1    uuid-002    28  Rio de Janeiro       872.33        False       2024-01-08
2    uuid-003    56  Belo Horizonte      4215.89        False       2022-11-23
3    uuid-004    33      São Paulo      2340.12        True        2023-09-17
4    uuid-005    49      Curitiba       3124.67        True        2024-02-05
```

---

Size parameter can be an integer or a callable function that returns an integer.

```python
from rand_engine.main.data_generator import DataGenerator
from rand_engine.examples.common_rand_specs import CommonRandSpecs
from random import randint

lambda_size = lambda: randint(500_000, 2_000_000)
df_customers = DataGenerator(CommonRandSpecs.customers(), seed=42).size(lambda_size).get_df()
print(df_customers.shape)
```

### 2. Databricks Integration

Seamlessly integrate with **Databricks** and other Spark environments. Generate synthetic data and convert to Spark DataFrames with zero friction.

```python
from rand_engine.main.spark_generator import SparkGenerator
from rand_engine.examples.common_rand_specs import CommonRandSpecs
from pyspark.sql import functions as F

# Option 1: Native Spark generation (common methods only)
df_spark = SparkGenerator(spark, F, CommonRandSpecs.transactions()).size(10_000_000).get_df()
display(df_spark)

# Option 2: Generate with DataGenerator and convert (for advanced methods)
from rand_engine.main.data_generator import DataGenerator
from rand_engine.examples.advanced_rand_specs import AdvancedRandSpecs

df_pandas = DataGenerator(AdvancedRandSpecs.orders()).size(1_000_000).get_df()
df_spark = spark.createDataFrame(df_pandas)

# Write directly to Delta Lake, Parquet, or any Spark-supported format
df_spark.write.format("delta").mode("overwrite").save("/path/to/delta/table")
```

---

### 3. Explore Built-In RandSpecs

Rand Engine provides **two types of pre-built specifications** to cover different use cases:

#### 3.1. **CommonRandSpecs** - Cross-Compatible Specs

These specs work with **both DataGenerator and SparkGenerator**. They use only common methods (integers, floats, booleans, dates, distincts, etc.).

```python
from rand_engine.main.data_generator import DataGenerator
from rand_engine.main.spark_generator import SparkGenerator
from rand_engine.examples.common_rand_specs import CommonRandSpecs
from pyspark.sql import functions as F

# Works with DataGenerator
df_pandas = DataGenerator(CommonRandSpecs.customers(), seed=42).size(100_000).get_df()

# Also works with SparkGenerator
df_spark = SparkGenerator(spark, F, CommonRandSpecs.customers()).size(100_000).get_df()
```

**Available Common Specs (7 ready-to-use):**

| Spec | Fields | Domain | Description |
|------|--------|--------|-------------|
| `customers()` | 6 | E-Commerce | Customer profiles with age, city, spending |
| `products()` | 7 | Retail | Product catalog with SKU, price, stock |
| `orders()` | 6 | E-Commerce | Orders with amounts, status, timestamps |
| `transactions()` | 7 | Finance | Financial transactions with fees |
| `employees()` | 8 | HR | Employee records with salary, department |
| `sensors()` | 7 | IoT | Sensor readings with temperature, humidity |
| `users()` | 7 | SaaS | Application users with subscription plans |

---

#### 3.2. **AdvancedRandSpecs** - DataGenerator Only

These specs use **advanced methods** for correlated data, complex patterns, and hierarchical relationships. They work **only with DataGenerator**.

```python
from rand_engine.main.data_generator import DataGenerator
from rand_engine.examples.advanced_rand_specs import AdvancedRandSpecs

# Advanced specs with correlated columns
df_products = DataGenerator(AdvancedRandSpecs.products()).size(100_000).get_df()
df_orders = DataGenerator(AdvancedRandSpecs.orders()).size(500_000).get_df()
df_employees = DataGenerator(AdvancedRandSpecs.employees()).size(1_000).get_df()
```

**Available Advanced Specs (10 ready-to-use):**

| Spec | Fields | Advanced Methods Used | Key Features |
|------|--------|----------------------|--------------|
| `products()` | 6 | `complex_distincts` | Pattern-based SKUs (PRD-1234) |
| `orders()` | 7 | `distincts_map` | Currency-country correlations |
| `employees()` | 8 | `distincts_multi_map` | Department-level-role hierarchy |
| `devices()` | 7 | `distincts_map_prop` | Status-priority weighted pairs |
| `invoices()` | 7 | `complex_distincts` | Invoice numbering patterns |
| `shipments()` | 8 | `distincts_map` | Carrier-destination correlations |
| `network_devices()` | 7 | `complex_distincts` | IP address patterns (192.168.x.x) |
| `vehicles()` | 8 | `distincts_multi_map` | Make-model-year combinations |
| `real_estate()` | 8 | `distincts_map` | Location-type correlations |
| `healthcare()` | 8 | `distincts_map_prop` | Diagnosis-treatment patterns |

**Example - Correlated Columns:**

```python
from rand_engine.main.data_generator import DataGenerator
from rand_engine.examples.advanced_rand_specs import AdvancedRandSpecs

# Orders with currency-country correlations
df = DataGenerator(AdvancedRandSpecs.orders()).size(10_000).get_df()
print(df[['currency', 'country']].drop_duplicates())

# Output shows realistic correlations:
#   currency country
# 0      USD      US
# 1      EUR      DE
# 2      BRL      BR
# 3      JPY      JP
```

**💡 Pro Tip:** If you need advanced patterns in Spark, generate with DataGenerator first, then convert:

```python
df_pandas = DataGenerator(AdvancedRandSpecs.employees()).size(100_000).get_df()
df_spark = spark.createDataFrame(df_pandas)
```

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

## 🔧 Advanced Methods (DataGenerator Only)

Beyond common methods, **DataGenerator** supports advanced patterns for correlated data and complex string generation. These methods are **not available in SparkGenerator**.

### 1. **`distincts_map`** - Correlated Pairs

Generate **2 correlated columns** where values depend on each other (e.g., currency ↔ country).

```python
spec = {
    "order_data": {
        "method": "distincts_map",
        "cols": ["currency", "country"],  # Must specify 2 columns
        "kwargs": {
            "distincts": {
                "USD": ["US", "EC", "PA"],      # USD → US, Ecuador, Panama
                "EUR": ["DE", "FR", "IT"],      # EUR → Eurozone countries
                "BRL": ["BR"],                   # BRL → Brazil
                "JPY": ["JP"]                    # JPY → Japan
            }
        }
    }
}

df = DataGenerator(spec).size(10_000).get_df()
print(df[['currency', 'country']].value_counts())
```

---

### 2. **`distincts_multi_map`** - Hierarchical Combinations

Generate **N correlated columns** with Cartesian combinations (e.g., department → level → role).

```python
spec = {
    "employee": {
        "method": "distincts_multi_map",
        "cols": ["department", "level", "role"],  # 3 columns
        "kwargs": {
            "distincts": {
                "Engineering": [
                    ["Junior", "Mid", "Senior"],          # Levels
                    ["Backend", "Frontend", "DevOps"]     # Roles
                ],
                "Sales": [
                    ["Junior", "Senior"],
                    ["Inside", "Field"]
                ]
            }
        }
    }
}

df = DataGenerator(spec).size(1_000).get_df()
# Possible combinations: (Engineering, Junior, Backend), (Engineering, Mid, Frontend), etc.
```

---

### 3. **`distincts_map_prop`** - Weighted Correlated Pairs

Generate **2 correlated columns with probabilities** (e.g., product → status with weights).

```python
spec = {
    "product_data": {
        "method": "distincts_map_prop",
        "cols": ["product_type", "condition"],
        "kwargs": {
            "distincts": {
                "laptop": [("new", 90), ("refurbished", 10)],       # 90% new
                "smartphone": [("new", 95), ("refurbished", 5)],    # 95% new
                "tablet": [("new", 85), ("refurbished", 15)]        # 85% new
            }
        }
    }
}

df = DataGenerator(spec).size(10_000).get_df()
print(df.groupby(['product_type', 'condition']).size())
```

---

### 4. **`complex_distincts`** - Pattern-Based Generation

Generate **complex strings** by replacing placeholders (IPs, SKUs, URLs, serial numbers).

**Example 1: IP Addresses**
```python
spec = {
    "ip_address": {
        "method": "complex_distincts",
        "kwargs": {
            "pattern": "x.x.x.x",
            "replacement": "x",
            "templates": [
                {"method": "distincts", "kwargs": {"distincts": ["192", "172", "10"]}},
                {"method": "integers", "kwargs": {"min": 0, "max": 255, "int_type": "int32"}},
                {"method": "integers", "kwargs": {"min": 0, "max": 255, "int_type": "int32"}},
                {"method": "integers", "kwargs": {"min": 1, "max": 254, "int_type": "int32"}}
            ]
        }
    }
}

df = DataGenerator(spec).size(1_000).get_df()
# Output: 192.168.1.45, 172.16.0.123, 10.0.1.89, ...
```

**Example 2: Product SKUs**
```python
spec = {
    "sku": {
        "method": "complex_distincts",
        "kwargs": {
            "pattern": "PRD-x-x",
            "replacement": "x",
            "templates": [
                {"method": "distincts", "kwargs": {"distincts": ["ELEC", "CLTH", "FOOD"]}},
                {"method": "integers", "kwargs": {"min": 1000, "max": 9999, "int_type": "int32"}}
            ]
        }
    }
}

df = DataGenerator(spec).size(100).get_df()
# Output: PRD-ELEC-1234, PRD-CLTH-5678, PRD-FOOD-9012, ...
```

---

### Advanced Methods Summary

| Method | Columns | Key Use Case | Example |
|--------|---------|--------------|---------|
| `distincts_map` | 2 | Currency-country, device-OS | USD → US, EUR → DE |
| `distincts_multi_map` | N | Hierarchies (dept-level-role) | Engineering → Senior → Backend |
| `distincts_map_prop` | 2 | Weighted correlations | Laptop → 90% new, 10% refurbished |
| `complex_distincts` | 1 | IPs, SKUs, URLs, serial numbers | 192.168.x.x, PRD-ELEC-1234 |

**⚠️ Important:** These methods are **DataGenerator only**. For Spark environments, generate with DataGenerator first, then convert:

```python
df_pandas = DataGenerator(AdvancedRandSpecs.products()).size(1_000_000).get_df()
df_spark = spark.createDataFrame(df_pandas)
```

📖 **For complete examples:** See [AdvancedRandSpecs](./rand_engine/examples/advanced_rand_specs.py) for 10+ production-ready specs.

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
