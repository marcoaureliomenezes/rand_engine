# DataGenerator - Pandas-Based Random Data Generation

## 📋 Overview
`DataGenerator` is the core class for generating random test data as **pandas DataFrames**. It provides a fluent API for configuring and generating structured random data with validation, transformers, constraints (PK/FK), and built-in file writing capabilities.

```python
from rand_engine.main.data_generator import DataGenerator

# Generate 1 million rows with seed for reproducibility
df = DataGenerator(spec, seed=42).size(1_000_000).get_df()
```

---

## 🎯 Key Features
- ✅ **All generation methods** - Full support for common + advanced methods
- ✅ **Validation** - Automatic spec validation with **actionable error messages**
- ✅ **Transformers** - Apply custom functions to enrich generated data
- ✅ **Constraints** - Primary Keys (PK) and Foreign Keys (FK) with automatic checkpoint management
- ✅ **Streaming** - Generate continuous data streams for real-time scenarios
- ✅ **File Writing** - Batch and streaming writers abstracted from pandas

---

## 🏗️ Main Methods

### `__init__(random_spec, seed=None)`
Initializes the generator with a RandSpec (dict or callable) and optional seed.

**Parameters:**
- `random_spec`: `dict | Callable[[], dict]` - Data generation specification
- `seed`: `int | None` - Random seed for reproducibility (default: None)

**Validation:**
- Spec is **automatically validated** on initialization
- Raises `SpecValidationError` with clear correction examples if invalid

**Example:**
```python
from rand_engine.main.data_generator import DataGenerator

spec = {
    "user_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}
}

# Validates spec immediately
generator = DataGenerator(spec, seed=42)
```

### `size(size: int)`
Sets the number of rows to generate. Returns `self` for method chaining.

**Example:**
```python
generator = DataGenerator(spec).size(50_000)
```

### `transformers(transformers: List[Callable])`
Applies custom transformation functions to the generated DataFrame. Transformers receive the DataFrame as input and return the modified DataFrame.

**Example:**
```python
def add_full_name(df):
    df["full_name"] = df["first_name"] + " " + df["last_name"]
    return df

df = (
    DataGenerator(spec)
    .size(1000)
    .transformers([add_full_name])
    .get_df()
)
```

### `db_checkpoint(db_conn)`
Overrides the default SQLite in-memory database for constraint checkpoints with a persistent database connection (DuckDB or SQLite).

**Example:**
```python
from rand_engine.integrations.duckdb_handler import DuckDBHandler

# Use persistent DuckDB for checkpoints
db_conn = DuckDBHandler(db_path="checkpoints.duckdb")

df = (
    DataGenerator(spec_with_constraints)
    .db_checkpoint(db_conn)
    .size(10_000)
    .get_df()
)
```

### `option(key: str, value: Any)`
Sets configuration options. Currently supports:
- `reset_checkpoint=True` - Deletes all checkpoint tables before generation

**Example:**
```python
df = (
    DataGenerator(spec_with_constraints)
    .option("reset_checkpoint", True)
    .size(5000)
    .get_df()
)
```

### `get_df() -> pd.DataFrame`
Generates and returns a pandas DataFrame with the configured size and transformations.

**Use Case:** Single batch generation - get all data at once.

**Example:**
```python
df = DataGenerator(spec).size(100_000).get_df()
print(df.shape)  # (100000, N_columns)
```

### `stream_dict(min_throughput: int, max_throughput: int) -> Generator`
Generates an **infinite stream** of records as dictionaries. Each record includes a `timestamp_created` field with the current timestamp.

**Parameters:**
- `min_throughput`: Minimum records per second
- `max_throughput`: Maximum records per second

**Use Case:** Continuous data generation for streaming scenarios (Kafka, Kinesis, real-time APIs).

**Example:**
```python
# Stream records with controlled throughput (1-5 records/second)
for record in generator.stream_dict(min_throughput=1, max_throughput=5):
    print(record)  # {"user_id": "00012345", "age": 42, "timestamp_created": 1699999999.123}
    send_to_kafka(record)
```

**⚠️ Important:** `stream_dict()` runs **indefinitely** - use with timeout or break condition.

### `write` (property)
Returns a `FileBatchWriter` instance for batch file writing. See [3_WRITING_FILES.md](3_WRITING_FILES.md) for details.

### `writeStream` (property)
Returns a `FileStreamWriter` instance for streaming file writing. See [3_WRITING_FILES.md](3_WRITING_FILES.md) for details.

---

## 📝 RandSpec Structure

A **RandSpec** is a dictionary where:
- **Keys** = column names
- **Values** = generation configuration `{"method": "...", "kwargs": {...}}`

### Basic Example
```python
spec = {
    "customer_id": {
        "method": "int_zfilled",
        "kwargs": {"length": 10}
    },
    "age": {
        "method": "integers",
        "kwargs": {"min": 18, "max": 80}
    },
    "score": {
        "method": "floats",
        "kwargs": {"min": 0.0, "max": 100.0, "decimals": 2}
    },
    "is_active": {
        "method": "booleans",
        "kwargs": {"true_prob": 0.7}
    }
}
```

### Available Methods (DataGenerator)

#### 🔢 Numeric Methods
| Method | Description | Example |
|--------|-------------|---------|
| `integers` | Random integers | `{"min": 0, "max": 100}` |
| `int_zfilled` | Zero-filled integers | `{"length": 8}` → `"00012345"` |
| `floats` | Random floats | `{"min": 0.0, "max": 10.0, "decimals": 2}` |
| `floats_normal` | Normal distribution | `{"mean": 100, "std": 15, "decimals": 1}` |

#### 🎲 Distinct Methods
| Method | Description | Example |
|--------|-------------|---------|
| `distincts` | Random selection from list | `{"distincts": ["A", "B", "C"]}` |
| `distincts_prop` | Weighted selection | `{"distincts": {"A": 70, "B": 30}}` |

#### 🔗 Advanced Methods (DataGenerator ONLY)
| Method | Description | Columns Generated | Example |
|--------|-------------|-------------------|---------|
| `distincts_map` | Correlated pairs | **2 columns** | `{"distincts": {"smartphone": ["android", "ios"]}}` |
| `distincts_map_prop` | Weighted pairs | **2 columns** | `{"distincts": {"laptop": [("new", 80), ("used", 20)]}}` |
| `distincts_multi_map` | Cartesian combinations | **N columns** | `{"distincts": {"tech": [["soft", "hard"], ["small", "large"]]}}` |
| `complex_distincts` | Pattern-based strings | **1 column** | IP addresses, URLs, custom patterns |

#### 📅 Date/Time Methods
| Method | Description | Example |
|--------|-------------|---------|
| `dates` | Random dates | `{"start": "2020-01-01", "end": "2023-12-31"}` |
| `unix_timestamps` | Unix timestamps | `{"start": "2020-01-01", "end": "2023-12-31"}` |

#### 🆔 Other Methods
| Method | Description | Example |
|--------|-------------|---------|
| `uuid4` | UUIDs | `{}` (no parameters) |
| `booleans` | Boolean values | `{"true_prob": 0.5}` |

---

## ✅ Validation & Error Messages

`DataGenerator` **automatically validates** your RandSpec on initialization and provides **actionable error messages** to help you fix problems quickly.

### Example: Missing Required Parameter
```python
spec = {
    "age": {
        "method": "integers",
        "kwargs": {}  # Missing 'min' and 'max'
    }
}

generator = DataGenerator(spec)
```

**Error Output:**
```
SpecValidationError: Specification has 1 error:

❌ Column 'age': method 'integers' requires parameter 'min'
   Expected type: int
   Correct example:
   {
      "age": {
         "method": "integers",
         "kwargs": {
            "min": 0,
            "max": 100
         }
      }
   }
```

### Example: Invalid Method Name
```python
spec = {
    "user_id": {
        "method": "int_zero_filled",  # Typo!
        "kwargs": {"length": 8}
    }
}
```

**Error Output:**
```
❌ Column 'user_id': method 'int_zero_filled' does not exist
   Available methods: 'integers', 'int_zfilled', 'floats', 'floats_normal', 'distincts', ...
```

### Example: Wrong Parameter Type
```python
spec = {
    "score": {
        "method": "floats",
        "kwargs": {
            "min": "0.0",  # String instead of float
            "max": 100.0
        }
    }
}
```

**Error Output:**
```
⚠️  Column 'score': parameter 'min' must be float
   Got: str
```

### Example: Multi-column Method Without `cols`
```python
spec = {
    "device_os": {
        "method": "distincts_map",
        # Missing 'cols' field!
        "kwargs": {
            "distincts": {
                "smartphone": ["android", "ios"]
            }
        }
    }
}
```

**Error Output:**
```
❌ Column 'device_os': Method 'distincts_map' requires 'cols' field
   Example:
   {
      "device_os": {
         "method": "distincts_map",
         "cols": ["device_type", "os_type"],
         "kwargs": {
            "distincts": {
               "smartphone": ["android", "ios"],
               "desktop": ["windows", "linux"]
            }
         }
      }
   }
```

---

## 🔄 get_df() vs stream_dict()

### `get_df()` - Batch Generation
**Use when:** You need a **complete DataFrame** all at once.

```python
# Generate 1 million rows in one batch
df = DataGenerator(spec).size(1_000_000).get_df()

# Typical use cases:
# - Training ML models
# - Batch processing
# - One-time data exports
# - Testing with fixed datasets
```

### `stream_dict()` - Continuous Streaming
**Use when:** You need **continuous, infinite data generation**.

```python
# Stream records indefinitely with controlled throughput
generator = DataGenerator(spec).size(100)  # Batch size per iteration

for record in generator.stream_dict(min_throughput=10, max_throughput=50):
    # Each record is a dict with timestamp_created
    print(record)
    
    # Typical use cases:
    # - Kafka/Kinesis producers
    # - Real-time API testing
    # - Event stream simulation
    # - IoT sensor data simulation
```

**Key Difference:**
- `get_df()` → **Returns once** with full DataFrame
- `stream_dict()` → **Never returns**, yields records forever

---

## 🧪 Real-World Examples

### Example 1: E-commerce Transactions
```python
from rand_engine.main.data_generator import DataGenerator

spec = {
    "transaction_id": {"method": "int_zfilled", "kwargs": {"length": 12}},
    "customer_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "amount": {"method": "floats_normal", "kwargs": {"mean": 150.0, "std": 50.0, "decimals": 2}},
    "status": {"method": "distincts_prop", "kwargs": {"distincts": {
        "completed": 85,
        "pending": 10,
        "cancelled": 5
    }}},
    "created_at": {"method": "dates", "kwargs": {
        "start": "2023-01-01",
        "end": "2023-12-31",
        "date_format": "%Y-%m-%d %H:%M:%S"
    }}
}

# Generate 500k transactions
df = DataGenerator(spec, seed=42).size(500_000).get_df()
```

### Example 2: Correlated Device/OS Data
```python
spec = {
    "device_os": {
        "method": "distincts_map",
        "cols": ["device_type", "operating_system"],
        "kwargs": {
            "distincts": {
                "smartphone": ["android", "ios"],
                "desktop": ["windows", "macos", "linux"],
                "tablet": ["android", "ios"]
            }
        }
    },
    "user_id": {"method": "int_zfilled", "kwargs": {"length": 8}}
}

# Generates 2 correlated columns: device_type + operating_system
df = DataGenerator(spec).size(10_000).get_df()
```

### Example 3: Complex IP Addresses
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

# Generates: 192.168.1.45, 10.0.0.123, etc.
df = DataGenerator(spec).size(1000).get_df()
```

---

## 🛠️ Transformers

Transformers allow **post-generation enrichment** of your DataFrame.

```python
from datetime import datetime, timedelta
import random

def add_calculated_fields(df):
    """Add derived columns based on existing data."""
    df["created_at"] = datetime.now() - timedelta(days=random.randint(0, 365))
    df["age_group"] = df["age"].apply(lambda x: "adult" if x >= 18 else "minor")
    return df

def uppercase_names(df):
    """Convert name column to uppercase."""
    df["name"] = df["name"].str.upper()
    return df

# Apply multiple transformers in order
df = (
    DataGenerator(spec)
    .size(10_000)
    .transformers([add_calculated_fields, uppercase_names])
    .get_df()
)
```

---

## 📚 Related Documentation
- **[2_SPARK_GENERATOR.md](2_SPARK_GENERATOR.md)** - Spark DataFrame generation
- **[3_WRITING_FILES.md](3_WRITING_FILES.md)** - File batch and streaming writers
- **[4_CONSTRAINTS.md](4_CONSTRAINTS.md)** - Primary/Foreign key constraints with cleanup
