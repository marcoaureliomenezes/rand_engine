# Rand Engine

**High-performance synthetic data generation for testing, development, and prototyping.**

A Python library for generating millions of rows of realistic synthetic data through declarative specifications. Built on NumPy and Pandas for maximum performance.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-189%20passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-82%25-green.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

---

## 📦 Installation

```bash
pip install rand-engine
```

---

## ✅ Requirements

- **Python**: >= 3.10
- **numpy**: >= 2.1.1
- **pandas**: >= 2.2.2
- **faker**: >= 28.4.1 (optional, for realistic data)
- **duckdb**: >= 1.1.0 (optional, for database integrations)

---

## 🎯 Who Is This For?

- **Data Engineers**: Test ETL/ELT pipelines without production data dependencies
- **QA Engineers**: Generate realistic datasets for load and integration testing
- **Data Scientists**: Mock data during model development and validation
- **Backend Developers**: Populate development and staging environments
- **BI Professionals**: Create demos and POCs without exposing sensitive data

---

## 🚀 Quick Start

### 1. Simple Data Generation

```python
from rand_engine import DataGenerator

# Declarative specification
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
    },
    "is_active": {
        "method": "booleans",
        "kwargs": {"true_prob": 0.8}
    },
    "plan": {
        "method": "distincts",
        "kwargs": {"distincts": ["free", "basic", "premium", "enterprise"]}
    }
}

# Generate DataFrame
generator = DataGenerator(spec, seed=42)
df = generator.size(10000).get_df()
print(df.head())
```

**Output:**
```
   user_id  age    salary  is_active      plan
0  00000001   42  87543.21       True  premium
1  00000002   28  45621.89       True     free
2  00000003   56 132041.50      False    basic
3  00000004   33  62789.12       True  premium
4  00000005   49  98234.77       True enterprise
```

### 2. Export to Multiple Formats

```python
# CSV with gzip compression
generator.write.size(100000).format("csv").option("compression", "gzip").save("users.csv")

# Parquet with snappy compression
generator.write.size(1000000).format("parquet").option("compression", "snappy").save("users.parquet")

# JSON
generator.write.size(50000).format("json").save("users.json")
```

### 3. Streaming Data Generation

```python
# Generate continuous stream of records
stream = generator.stream_dict(min_throughput=5, max_throughput=15)

for record in stream:
    # Each record includes automatic timestamp_created field
    print(record)
    # Send to Kafka, API, database, etc.
```

### 4. Reproducible Data with Seeds

```python
# Same seed = identical data
df1 = DataGenerator(spec, seed=42).size(1000).get_df()
df2 = DataGenerator(spec, seed=42).size(1000).get_df()

assert df1.equals(df2)  # True
```

---

## 📚 Available Generation Methods

### Core Methods

| Method | Description | Example |
|--------|-------------|---------|
| **integers** | Random integers within range | `{"method": "integers", "kwargs": {"min": 0, "max": 100}}` |
| **int_zfilled** | Zero-padded numeric strings | `{"method": "int_zfilled", "kwargs": {"length": 8}}` |
| **floats** | Random floats with precision | `{"method": "floats", "kwargs": {"min": 0.0, "max": 100.0, "round": 2}}` |
| **floats_normal** | Normally distributed floats | `{"method": "floats_normal", "kwargs": {"mean": 50, "std": 10, "round": 2}}` |
| **booleans** | Boolean values with probability | `{"method": "booleans", "kwargs": {"true_prob": 0.7}}` |
| **distincts** | Random selection from list | `{"method": "distincts", "kwargs": {"distincts": ["A", "B", "C"]}}` |
| **distincts_prop** | Weighted random selection | `{"method": "distincts_prop", "kwargs": {"distincts": {"mobile": 70, "desktop": 30}}}` |
| **unix_timestamps** | Unix timestamps in range | `{"method": "unix_timestamps", "kwargs": {"start": "01-01-2020", "end": "31-12-2023", "format": "%d-%m-%Y"}}` |
| **unique_ids** | Unique identifiers | `{"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 10}}` |

### Advanced Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| **distincts_map** | Correlated 2-column pairs | Device → OS mapping |
| **distincts_map_prop** | Weighted correlated pairs | Product → Status with weights |
| **distincts_multi_map** | N-column Cartesian products | Company → Sector → Size |
| **complex_distincts** | Pattern-based generation | IP addresses, URLs, codes |

---

## � Advanced Features

### 1. Correlated Columns (2-Column Mapping)

Generate correlated data where one column determines another:

```python
spec = {
    "device_os": {
        "method": "distincts_map",
        "cols": ["device_type", "os"],
        "kwargs": {
            "distincts": {
                "smartphone": ["Android", "iOS"],
                "tablet": ["Android", "iOS", "iPadOS"],
                "desktop": ["Windows", "macOS", "Linux"]
            }
        }
    }
}

df = DataGenerator(spec).size(1000).get_df()
# Result: 2 columns (device_type, os) with valid combinations
```

### 2. Weighted Correlated Data

```python
spec = {
    "product_status": {
        "method": "distincts_map_prop",
        "cols": ["product", "status"],
        "kwargs": {
            "distincts": {
                "laptop": [("new", 90), ("refurbished", 10)],
                "phone": [("new", 95), ("refurbished", 5)],
                "tablet": [("new", 85), ("refurbished", 15)]
            }
        }
    }
}

df = DataGenerator(spec).size(10000).get_df()
# 90% of laptops will be "new", 10% "refurbished"
```

### 3. Complex Patterns (IP Addresses, URLs)

```python
spec = {
    "ip_address": {
        "method": "complex_distincts",
        "kwargs": {
            "pattern": "x.x.x.x",
            "replacement": "x",
            "templates": [
                {"method": "distincts", "kwargs": {"distincts": ["192", "10", "172"]}},
                {"method": "integers", "kwargs": {"min": 0, "max": 255}},
                {"method": "integers", "kwargs": {"min": 0, "max": 255}},
                {"method": "integers", "kwargs": {"min": 1, "max": 254}}
            ]
        }
    }
}

df = DataGenerator(spec).size(100).get_df()
# Output: 192.168.1.45, 10.0.52.231, 172.24.133.89, etc.
```

### 4. Data Transformers

Apply transformations to generated data:

```python
from datetime import datetime

spec = {
    "timestamp": {
        "method": "unix_timestamps",
        "kwargs": {"start": "01-01-2023", "end": "31-12-2023", "format": "%d-%m-%Y"},
        # Column-level transformer
        "transformers": [
            lambda ts: datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        ]
    },
    "value": {
        "method": "integers",
        "kwargs": {"min": 100, "max": 1000}
    }
}

# DataFrame-level transformer
def add_year_column(df):
    df['year'] = df['timestamp'].str[:4]
    return df

df = (DataGenerator(spec)
    .transformers([add_year_column])
    .size(1000)
    .get_df())
```

### 5. Spec Validation

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

## 🎨 Real-World Examples

### E-commerce Orders

```python
spec = {
    "order_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint", "length": 10}
    },
    "customer_id": {
        "method": "integers",
        "kwargs": {"min": 1000, "max": 50000}
    },
    "product_category": {
        "method": "distincts_prop",
        "kwargs": {
            "distincts": {
                "electronics": 40,
                "clothing": 30,
                "home": 20,
                "sports": 10
            }
        }
    },
    "amount": {
        "method": "floats",
        "kwargs": {"min": 10.0, "max": 5000.0, "round": 2}
    },
    "payment_status": {
        "method": "distincts_prop",
        "kwargs": {
            "distincts": {
                "paid": 85,
                "pending": 10,
                "failed": 5
            }
        }
    },
    "created_at": {
        "method": "unix_timestamps",
        "kwargs": {"start": "01-01-2024", "end": "31-12-2024", "format": "%d-%m-%Y"}
    }
}

# Generate 1 million orders
orders = DataGenerator(spec, seed=42).size(1000000).get_df()
orders.to_parquet("orders.parquet", compression="snappy")
```

### IoT Sensor Data

```python
spec = {
    "sensor_id": {
        "method": "distincts",
        "kwargs": {"distincts": [f"SENSOR_{i:03d}" for i in range(1, 101)]}
    },
    "temperature": {
        "method": "floats_normal",
        "kwargs": {"mean": 22.0, "std": 3.5, "round": 2}
    },
    "humidity": {
        "method": "floats_normal",
        "kwargs": {"mean": 60.0, "std": 10.0, "round": 1}
    },
    "battery_level": {
        "method": "integers",
        "kwargs": {"min": 0, "max": 100}
    },
    "status": {
        "method": "distincts_prop",
        "kwargs": {
            "distincts": {
                "active": 95,
                "warning": 4,
                "error": 1
            }
        }
    }
}

# Stream sensor readings
stream = DataGenerator(spec).stream_dict(min_throughput=10, max_throughput=50)

for reading in stream:
    # Send to time-series database
    print(f"Sensor {reading['sensor_id']}: {reading['temperature']}°C")
```

### User Behavior Logs

```python
spec = {
    "session_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint", "length": 12}
    },
    "device_os": {
        "method": "distincts_map",
        "cols": ["device", "os"],
        "kwargs": {
            "distincts": {
                "mobile": ["Android", "iOS"],
                "tablet": ["Android", "iOS"],
                "desktop": ["Windows", "macOS", "Linux"]
            }
        }
    },
    "page_views": {
        "method": "integers",
        "kwargs": {"min": 1, "max": 50}
    },
    "duration_seconds": {
        "method": "integers",
        "kwargs": {"min": 10, "max": 3600}
    },
    "converted": {
        "method": "booleans",
        "kwargs": {"true_prob": 0.03}  # 3% conversion rate
    }
}

logs = DataGenerator(spec, seed=123).size(500000).get_df()
```

---

## 🗂️ File Export Options

### Batch Writing

```python
from rand_engine import DataGenerator

spec = {...}  # Your spec here

# CSV with compression
(DataGenerator(spec)
    .write
    .size(100000)
    .format("csv")
    .option("compression", "gzip")
    .option("index", False)
    .mode("overwrite")
    .save("output/data.csv"))

# Parquet with multiple files
(DataGenerator(spec)
    .write
    .size(5000000)
    .format("parquet")
    .option("compression", "snappy")
    .option("numFiles", 10)  # Split into 10 files
    .save("output/data.parquet"))

# JSON with pretty print
(DataGenerator(spec)
    .write
    .size(10000)
    .format("json")
    .option("indent", 2)
    .save("output/data.json"))
```

### Streaming Writing

```python
# Write data in micro-batches
(DataGenerator(spec)
    .writeStream
    .microbatch_size(1000)
    .max_microbatches(100)
    .format("csv")
    .option("compression", "gzip")
    .save("output/stream/"))
```

---

## 🔌 Database Integrations

### DuckDB Integration

```python
from rand_engine.integrations._duckdb_handler import DuckDBHandler

# Generate and insert data
spec = {...}
df = DataGenerator(spec).size(100000).get_df()

# Create handler (in-memory or file-based)
handler = DuckDBHandler(":memory:")  # or DuckDBHandler("mydb.duckdb")

# Create table
handler.create_table("users", "user_id VARCHAR(10)")

# Insert data
handler.insert_df("users", df, pk_cols=["user_id"])

# Query data
result = handler.select_all("users")
print(result.head())

# Cleanup
handler.close()
```

### SQLite Integration

```python
from rand_engine.integrations._sqlite_handler import SQLiteHandler

handler = SQLiteHandler("test.db")
handler.create_table("events", "event_id VARCHAR(10)")
handler.insert_df("events", df, pk_cols=["event_id"])

# Query with column selection
result = handler.select_all("events", columns=["event_id", "timestamp"])

handler.close()
```

---

## 🏗️ Architecture

### Design Principles

1. **Declarative Specifications**: Define what you want, not how to generate it
2. **High Performance**: Built on NumPy for vectorized operations
3. **Type Safety**: Full type hints and validation
4. **Composability**: Chain methods for fluent API
5. **Extensibility**: Easy to add custom generators and transformers

### Public API

The library exposes a single entry point:

```python
from rand_engine import DataGenerator
```

All internal modules (prefixed with `_`) are implementation details and may change.

### Key Components

- **DataGenerator**: Main class for data generation
- **SpecValidator**: Educational validator with helpful error messages
- **File Writers**: Batch and stream writers for multiple formats
- **Database Handlers**: DuckDB and SQLite integrations with connection pooling
- **Core Generators**: Stateless NumPy-based generation methods

---

## 🧪 Testing

The library has comprehensive test coverage:

- **189 tests** across all components
- **82% code coverage**
- **Unit tests**: Core generation methods
- **Integration tests**: File writers, database handlers
- **API tests**: Public interface validation

Run tests:

```bash
# All tests
pytest

# With coverage
pytest --cov=rand_engine --cov-report=html

# Specific module
pytest tests/integrations/
```

---

## 📖 Documentation

### Method Reference

All 13 generation methods are documented in the validator:

```python
from rand_engine.validators.spec_validator import SpecValidator

# See all available methods and their parameters
print(SpecValidator.METHOD_SPECS.keys())
# dict_keys(['integers', 'int_zfilled', 'floats', 'floats_normal', 'booleans', 
#            'distincts', 'distincts_prop', 'distincts_map', 'distincts_map_prop',
#            'distincts_multi_map', 'complex_distincts', 'unix_timestamps', 'unique_ids'])
```

### Getting Help

Enable validation for helpful error messages:

```python
spec = {
    "age": {
        "method": "unknown_method"  # Typo!
    }
}

try:
    DataGenerator(spec, validate=True)
except Exception as e:
    print(e)
    # Shows correct method names and examples
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 Acknowledgments

- Built with [NumPy](https://numpy.org/) and [Pandas](https://pandas.pydata.org/)
- Inspired by modern data engineering practices
- Community feedback and contributions

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/marcoaureliomenezes/rand_engine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/marcoaureliomenezes/rand_engine/discussions)
- **Email**: marco.a.menezes@gmail.com

---

## 🗺️ Roadmap

- [ ] PostgreSQL integration
- [ ] MySQL/MariaDB support
- [ ] Apache Arrow format support
- [ ] Distributed generation with Dask
- [ ] Web UI for spec building
- [ ] More pre-built templates

---

**Made with ❤️ for the data community**
