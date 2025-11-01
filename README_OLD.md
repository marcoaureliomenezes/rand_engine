<div align="center">

# 🎲 Rand Engine

**Generate millions of rows of synthetic data in seconds**

*High-performance random data generation for testing, development, and prototyping*

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.o📖 **Complete guide with examples:** [BUILD_RAND_SPECS.md](./docs/BUILD_RAND_SPECS.md)/downloads/)
[![Tests](https://img.shields.io/badge/tests-494%20passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
[![Version](https://img.shields.io/badge/version-0.7.0-orange.svg)](https://pypi.org/project/rand-engine/)
[![PyPI](https://img.shields.io/badge/PyPI-rand--engine-blue.svg)](https://pypi.org/project/rand-engine/)

[Quick Start](#-quick-start) • [Features](#-key-features) • [Examples](#-usage-examples) • [Documentation](#-documentation) • [Benchmarks](#-performance-benchmarks)

</div>

---

## 🎯 What is Rand Engine?

**Rand Engine** is a Python library that generates **realistic synthetic data at scale** through simple declarative specifications. Built on NumPy and Pandas for maximum performance.

**Perfect for:**
- 🧪 Testing ETL/ELT pipelines without production data
- 📊 Load testing and stress testing data systems
- 🎓 Learning data engineering without complex setups
- 🚀 Prototyping applications with realistic datasets
- 🔐 Demos and POCs without exposing sensitive data

---

## 🚀 Quick Start

### Installation

```bash
pip install rand-engine
```

### Generate Your First Dataset (3 Lines!)

```python
from rand_engine.main.data_generator import DataGenerator
from rand_engine.examples.common_rand_specs import CommonRandSpecs

# Generate 1 million customer records in seconds
df = DataGenerator(CommonRandSpecs.customers(), seed=42).size(1_000_000).get_df()
print(df.head())
```

**Output:**
```
   customer_id  age           city  total_spent  is_premium registration_date
0    uuid-001    42      São Paulo      1523.50        True        2023-05-12
1    uuid-002    28  Rio de Janeiro       872.33       False        2024-01-08
2    uuid-003    56  Belo Horizonte      4215.89       False        2022-11-23
```

**That's it!** You just generated 1 million rows of realistic customer data. 🎉

---

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 🐼 **Pandas DataFrames**
```python
from rand_engine.main.data_generator import DataGenerator

df = DataGenerator(spec, seed=42).size(1_000_000).get_df()
```
✅ All methods (common + advanced)  
✅ Correlated columns  
✅ Complex patterns  
✅ PK/FK constraints  

</td>
<td width="50%">

### ⚡ **Spark DataFrames**
```python
from rand_engine.main.spark_generator import SparkGenerator

df = SparkGenerator(spark, F, spec).size(100_000_000).get_df()
```
✅ Native Spark generation  
✅ Databricks ready  
✅ Distributed at scale  
⚠️ Common methods only  

</td>
</tr>
</table>

### 🎁 **17+ Pre-Built RandSpecs**

No configuration needed! Start generating data immediately:

| **CommonRandSpecs** (Work Everywhere) | **AdvancedRandSpecs** (Pandas Only) |
|---------------------------------------|-------------------------------------|
| `customers()` `products()` `orders()` | `employees()` `devices()` `invoices()` |
| `transactions()` `employees()` `sensors()` | `shipments()` `network_devices()` `vehicles()` |
| `users()` | `real_estate()` `healthcare()` |

```python
# Use any pre-built spec instantly
from rand_engine.examples.common_rand_specs import CommonRandSpecs
from rand_engine.examples.advanced_rand_specs import AdvancedRandSpecs

df_orders = DataGenerator(CommonRandSpecs.orders()).size(50_000).get_df()
df_employees = DataGenerator(AdvancedRandSpecs.employees()).size(1_000).get_df()
```

### 📝 **Write to Files**

```python
# Write to CSV, Parquet, JSON with compression
DataGenerator(spec).size(1_000_000).write() \
    .format("parquet") \
    .compression("snappy") \
    .mode("overwrite") \
    .save("./data/customers")
```

### 🌊 **Stream Data**

```python
# Simulate real-time data streams
DataGenerator(spec).stream() \
    .throughput(min=1000, max=5000) \
    .format("json") \
    .start("./data/stream/events")
```

---

## 💡 Usage Examples

### 1️⃣ **Local Development (Pandas)**

```python
from rand_engine.main.data_generator import DataGenerator
from rand_engine.examples.common_rand_specs import CommonRandSpecs

# Generate and explore
df = DataGenerator(CommonRandSpecs.transactions(), seed=42).size(100_000).get_df()
print(df.describe())
```

### 2️⃣ **Databricks / Spark Environments**

```python
from rand_engine.main.spark_generator import SparkGenerator
from rand_engine.examples.common_rand_specs import CommonRandSpecs
from pyspark.sql import functions as F

# Generate Spark DataFrame with 100M rows
df_spark = SparkGenerator(spark, F, CommonRandSpecs.orders()).size(100_000_000).get_df()

# Write to Delta Lake
df_spark.write.format("delta").mode("overwrite").save("/path/to/delta/table")
```

### 3️⃣ **Custom Specifications**

```python
# Define your own data structure
custom_spec = {
    "user_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "uuid4"}
    },
    "age": {
        "method": "integers",
        "kwargs": {"min": 18, "max": 80}
    },
    "salary": {
        "method": "floats",
        "kwargs": {"min": 30000, "max": 150000, "round": 2}
    }
}

df = DataGenerator(custom_spec).size(50_000).get_df()
```

📖 **Learn more:** [BUILD_RAND_SPECS.md](./docs/BUILD_RAND_SPECS.md) | [50+ Examples](./EXAMPLES.md)

---

## � Performance Benchmarks

Real-world performance tests across different environments:

| Environment | Dataset | Rows | Time | Throughput |
|------------|---------|------|------|------------|
| **Local (Python 3.12)** | Customers | 1M | 81.5s | ~12K rows/sec |
| **Databricks (Standard)** | Customers | 1M | 7.4s | ~135K rows/sec |
| **Databricks (Spark)** | Orders | 100M | 19.4s | ~5.1M rows/sec |
| **Databricks (Custom)** | Custom Spec | 100M | 19.4s | ~5.1M rows/sec |

💡 **Tip:** Spark generation scales linearly with cluster size for massive datasets (100M+ rows).

---

## 🔑 Advanced Features

### 🔗 **Constraints System** - Referential Integrity

Generate **multiple related tables** with Primary Keys (PK) and Foreign Keys (FK) to ensure referential integrity:

```python
from rand_engine.main.data_generator import DataGenerator

# Define specs with constraints
customers_spec = {
    "customer_id": {"method": "unique_ids", "kwargs": {"strategy": "sequence"}},
    "name": {"method": "distincts", "kwargs": {"distincts": ["Alice", "Bob", "Charlie"]}},
    "constraints": {
        "pk_customer": {"tipo": "PK", "fields": ["customer_id"]}
    }
}

orders_spec = {
    "order_id": {"method": "unique_ids", "kwargs": {"strategy": "sequence"}},
    "customer_id": {"method": "integers", "kwargs": {"min": 1, "max": 1000}},
    "amount": {"method": "floats", "kwargs": {"min": 10, "max": 1000, "round": 2}},
    "constraints": {
        "fk_customer": {
            "tipo": "FK",
            "fields": ["customer_id"],
            "references": {"spec_name": "customers", "pk_name": "pk_customer"}
        }
    }
}

# Generate with referential integrity
generator = DataGenerator({"customers": customers_spec, "orders": orders_spec})
dfs = generator.size({"customers": 1000, "orders": 5000}).get_dfs()

# Validate: All order customer_ids exist in customers
assert set(dfs["orders"]["customer_id"]).issubset(set(dfs["customers"]["customer_id"]))
```

📖 **Complete guide:** [CONSTRAINTS.md](./docs/CONSTRAINTS.md) (900+ lines with examples)

### 🎨 **Advanced Methods** - Correlated Data

Generate correlated columns for realistic data patterns:

```python
# Currency-Country correlations
orders_spec = {
    "order_id": {"method": "unique_ids", "kwargs": {"strategy": "sequence"}},
    "currency_country": {
        "method": "distincts_map",  # Correlated pairs
        "splitable": True,
        "cols": ["currency", "country"],
        "sep": ";",
        "kwargs": {"distincts": ["USD;US", "EUR;DE", "BRL;BR", "JPY;JP"]}
    }
}

df = DataGenerator(orders_spec).size(10_000).get_df()
# Result: USD always paired with US, EUR with DE, etc.
- `"kwargs"`: Method-specific parameters
- **Declarative**: Define _what_ you want, not _how_ to generate it

---

## �️ How to Build Custom RandSpecs

**Common Methods** (Both DataGenerator & SparkGenerator):
- `unique_ids` - Unique identifiers (UUID, sequences, zero-padded ints)
- `integers` - Random integers with min/max
- `floats` - Random decimals with rounding
- `floats_normal` - Normal distribution (bell curve)
- `booleans` - True/False with probability
- `distincts` - Random selection from list
- `distincts_prop` - Weighted random selection
- `unix_timestamps` - Date/time generation

**Advanced Methods** (DataGenerator Only):
- `distincts_map` - Correlated pairs (currency ↔ country)
- `distincts_multi_map` - Hierarchical combinations (dept → level → role)
- `distincts_map_prop` - Weighted correlated pairs
- `complex_distincts` - Pattern-based strings (IPs, SKUs, URLs)

df = DataGenerator(orders_spec).size(10_000).get_df()
# Result: USD always paired with US, EUR with DE, etc.
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

📖 **Learn more:** Check the full documentation for detailed examples and advanced patterns.

---

## 💡 Quick Tips

<table>
<tr>
<td width="50%">

### 🎯 **For Data Engineers**
- Use `seed` for reproducible tests
- Export to Parquet for large datasets
- Use constraints for multi-table integrity
- Stream mode for real-time testing

</td>
<td width="50%">

### 🧪 **For QA Engineers**
- Start with pre-built specs
- Generate edge cases with probabilities
- Multiple seeds = multiple test scenarios
- Test PK/FK relationships

</td>
</tr>
</table>

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[BUILD_RAND_SPECS.md](./docs/BUILD_RAND_SPECS.md)** | Complete guide to building custom specifications |
| **[EXAMPLES.md](./EXAMPLES.md)** | 50+ production-ready examples |
| **[CONSTRAINTS.md](./docs/CONSTRAINTS.md)** | PK/FK system and referential integrity |
| **[API_REFERENCE.md](./docs/API_REFERENCE.md)** | Full method reference |
| **[LOGGING.md](./docs/LOGGING.md)** | Logging configuration |

---

## 🧪 Testing

**494 tests passing** with comprehensive coverage:

```bash
pytest                                    # Run all tests
pytest tests/test_2_data_generator.py -v # Test DataGenerator
pytest tests/test_3_spark_generator.py -v # Test SparkGenerator
pytest tests/test_8_consistency.py -v    # Test constraints
```

---

## � Requirements

- **Python** >= 3.10
- **numpy** >= 2.1.1
- **pandas** >= 2.2.2
- **faker** >= 28.4.1 (optional)
- **duckdb** >= 1.1.0 (optional)

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- � Report bugs via [Issues](https://github.com/marcoaureliomenezes/rand_engine/issues)
- 💡 Suggest features via [Discussions](https://github.com/marcoaureliomenezes/rand_engine/discussions)
- 🔧 Submit pull requests

---

## 📞 Support

- **GitHub Issues**: [Report bugs](https://github.com/marcoaureliomenezes/rand_engine/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/marcoaureliomenezes/rand_engine/discussions)
- **Email**: marcourelioreislima@gmail.com

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

### 🌟 Star the project if you find it useful!

[![Star History Chart](https://api.star-history.com/svg?repos=marcoaureliomenezes/rand_engine&type=Date)](https://star-history.com/#marcoaureliomenezes/rand_engine&Date)

**Built with ❤️ for Data Engineers and the data community**

[⬆ Back to top](#-rand-engine)

</div>
