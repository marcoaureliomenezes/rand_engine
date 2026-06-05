<div align="center">

# 🎲 Rand Engine

**Generate millions of rows of synthetic data in seconds**

*High-performance random data generation for testing, development, and prototyping*

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-494%20passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
[![Version](https://img.shields.io/badge/version-0.6.4-orange.svg)](https://pypi.org/project/rand-engine/)
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
| `transactions()` `sensors()` `users()` | `shipments()` `network_devices()` `vehicles()` |
|  | `real_estate()` `healthcare()` |

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
DataGenerator(spec).size(1_000_000).write \
    .format("parquet") \
    .mode("overwrite") \
    .option("compression", "snappy") \
    .save("./data/customers")
```

📖 **Complete guide:** [3_WRITING_FILES.md](./docs/3_WRITING_FILES.md)

### 🌊 **Stream Data**

```python
# Simulate real-time data streams
DataGenerator(spec).size(100).writeStream \
    .format("json") \
    .mode("overwrite") \
    .trigger(5) \
    .option("timeout", 60) \
    .start("./data/stream/events")
```

📖 **Complete guide:** [3_WRITING_FILES.md](./docs/3_WRITING_FILES.md)

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

📖 **Learn more:** [DataGenerator Guide](./docs/1_DATA_GENERATOR.md) | [SparkGenerator Guide](./docs/2_SPARK_GENERATOR.md) | [50+ Examples](./EXAMPLES.md)

---

## 📊 Performance Benchmarks

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

Generate **multiple related tables** with Primary Keys (PK) and Foreign Keys (FK):

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
```

📖 **Complete guide:** [4_CONSTRAINTS.md](./docs/4_CONSTRAINTS.md)

### 🎨 **Advanced Methods** - Correlated Data

Generate correlated columns for realistic patterns:

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
```

**Available Advanced Methods:**
- `distincts_map` - Correlated pairs (currency ↔ country)
- `distincts_multi_map` - Hierarchical combinations (dept → level → role)
- `distincts_map_prop` - Weighted correlated pairs
- `complex_distincts` - Pattern-based strings (IPs, SKUs, URLs)

📖 **Complete guide:** [1_DATA_GENERATOR.md](./docs/1_DATA_GENERATOR.md) | [BUILD_RAND_SPECS.md](./docs/BUILD_RAND_SPECS.md)

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

### Core Documentation
| Document | Description |
|----------|-------------|
| **[1_DATA_GENERATOR.md](./docs/1_DATA_GENERATOR.md)** | Pandas-based data generation with all features |
| **[2_SPARK_GENERATOR.md](./docs/2_SPARK_GENERATOR.md)** | Spark DataFrame generation at scale |
| **[3_WRITING_FILES.md](./docs/3_WRITING_FILES.md)** | Batch and streaming file writers |
| **[4_CONSTRAINTS.md](./docs/4_CONSTRAINTS.md)** | PK/FK constraints with automatic cleanup |

### Additional Resources
| Document | Description |
|----------|-------------|
| **[BUILD_RAND_SPECS.md](./docs/BUILD_RAND_SPECS.md)** | Complete guide to building custom specifications |
| **[EXAMPLES.md](./EXAMPLES.md)** | 50+ production-ready examples |
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

## 📦 Requirements

- **Python** >= 3.10
- **numpy** >= 2.1.1
- **pandas** >= 2.2.2
- **faker** >= 28.4.1 (optional)
- **duckdb** >= 1.1.0 (optional)

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs via [Issues](https://github.com/marcoaureliomenezes/rand_engine/issues)
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
