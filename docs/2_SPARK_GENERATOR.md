# SparkGenerator - Distributed Random Data Generation

## 📋 Overview
`SparkGenerator` generates random test data as **Spark DataFrames**, enabling distributed data generation at scale for Databricks, EMR, and other Spark environments. It uses **native Spark operations** without pandas conversion overhead.

```python
from rand_engine.main.spark_generator import SparkGenerator
from pyspark.sql import functions as F

# Generate 100 million rows distributed across cluster
df = SparkGenerator(spark, F, spec).size(100_000_000).get_df()
```

---

## 🎯 Key Features
- ✅ **Native Spark generation** - No pandas overhead
- ✅ **Databricks ready** - Works out of the box
- ✅ **Distributed at scale** - Leverage Spark cluster for massive datasets
- ✅ **Common methods supported** - integers, floats, distincts, dates, etc.
- ⚠️ **Limited advanced methods** - distincts_map, complex_distincts return NULL (dummy implementations)
- ❌ **No built-in file writing** - Use Spark's native `.write` API

---

## 🏗️ Main Methods

### `__init__(spark, F, metadata)`
Initializes the generator with Spark session, functions module, and metadata.

**Parameters:**
- `spark`: `SparkSession` - Active Spark session
- `F`: `pyspark.sql.functions` - PySpark functions module
- `metadata`: `dict` - RandSpec (same structure as DataGenerator)

**Validation:**
- Spec is **automatically validated** on initialization
- Raises `SpecValidationError` if invalid
- **Warnings** for advanced methods (returns NULL)

**Example:**
```python
from pyspark.sql import SparkSession, functions as F
from rand_engine.main.spark_generator import SparkGenerator

spark = SparkSession.builder.appName("DataGen").getOrCreate()

spec = {
    "user_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "age": {"method": "integers", "kwargs": {"min": 18, "max": 80}},
    "is_active": {"method": "booleans", "kwargs": {"true_prob": 0.7}}
}

generator = SparkGenerator(spark, F, spec)
```

### `size(size: int)`
Sets the number of rows to generate. Returns `self` for method chaining.

**Example:**
```python
generator = SparkGenerator(spark, F, spec).size(10_000_000)
```

### `get_df() -> pyspark.sql.DataFrame`
Generates and returns a Spark DataFrame with the configured size.

**Technical Details:**
- Creates base DataFrame using `spark.range(size)` (generates `id` column)
- Applies generation methods sequentially for each column
- **Removes technical `id` column** unless specified in metadata

**Example:**
```python
df = SparkGenerator(spark, F, spec).size(1_000_000).get_df()

# Typical use:
df.write.format("delta").mode("overwrite").save("/path/to/table")
```

---

## 📝 RandSpec Compatibility

`SparkGenerator` uses the **same RandSpec structure** as `DataGenerator`, but with **limited method support**.

### ✅ Supported Methods (Common Methods)

#### 🔢 Numeric Methods
| Method | Description | Example |
|--------|-------------|---------|
| `integers` | Random integers | `{"min": 0, "max": 100}` |
| `int_zfilled` | Zero-filled integers | `{"length": 8}` |
| `floats` | Random floats | `{"min": 0.0, "max": 10.0, "decimals": 2}` |
| `floats_normal` | Normal distribution | `{"mean": 100, "std": 15, "decimals": 1}` |

#### 🎲 Distinct Methods
| Method | Description | Example |
|--------|-------------|---------|
| `distincts` | Random selection | `{"distincts": ["A", "B", "C"]}` |
| `distincts_prop` | Weighted selection | `{"distincts": {"A": 70, "B": 30}}` |

#### 📅 Date/Time Methods
| Method | Description | Example |
|--------|-------------|---------|
| `dates` | Random dates | `{"start": "2020-01-01", "end": "2023-12-31"}` |
| `unix_timestamps` | Unix timestamps | `{"start": "2020-01-01", "end": "2023-12-31"}` |

#### 🆔 Other Methods
| Method | Description | Example |
|--------|-------------|---------|
| `uuid4` | UUIDs | `{}` |
| `booleans` | Boolean values | `{"true_prob": 0.5}` |

### ⚠️ Limited Support (Dummy Implementations)

These methods are **available for API compatibility** but return **NULL values**. Use them only in `DataGenerator`.

| Method | Status | DataGenerator | SparkGenerator |
|--------|--------|---------------|----------------|
| `distincts_map` | Dummy | ✅ Works | ⚠️ Returns NULL |
| `distincts_map_prop` | Dummy | ✅ Works | ⚠️ Returns NULL |
| `distincts_multi_map` | Dummy | ✅ Works | ⚠️ Returns NULL |
| `complex_distincts` | Dummy | ✅ Works | ⚠️ Returns NULL |
| `distincts_external` | Not Available | ✅ Works | ❌ Not supported |

**Example - Validation Warning:**
```python
spec = {
    "device_os": {
        "method": "distincts_map",  # Advanced method
        "cols": ["device", "os"],
        "kwargs": {"distincts": {"smartphone": ["android", "ios"]}}
    }
}

generator = SparkGenerator(spark, F, spec)
```

**Warning Output:**
```
⚠️  Column 'device_os': method 'distincts_map' is a dummy in SparkGenerator (returns NULL)
   This method is only fully implemented in DataGenerator
   Available SparkGenerator methods: integers, int_zfilled, floats, distincts, dates, ...
```

---

## ✅ Validation & Error Messages

`SparkGenerator` uses the **same validation** as `DataGenerator`, ensuring RandSpec correctness.

### Example: Invalid Method
```python
spec = {
    "age": {
        "method": "random_integers",  # Typo!
        "kwargs": {"min": 0, "max": 100}
    }
}

generator = SparkGenerator(spark, F, spec)
```

**Error Output:**
```
❌ Column 'age': method 'random_integers' does not exist
   Available methods: 'integers', 'int_zfilled', 'floats', 'floats_normal', 'distincts', ...
```

### Example: Missing Required Parameter
```python
spec = {
    "score": {
        "method": "floats",
        "kwargs": {"min": 0.0}  # Missing 'max'
    }
}
```

**Error Output:**
```
❌ Column 'score': method 'floats' requires parameter 'max'
   Expected type: float
   Correct example:
   {
      "score": {
         "method": "floats",
         "kwargs": {
            "min": 0.0,
            "max": 100.0,
            "decimals": 2
         }
      }
   }
```

---

## 🚀 Spark-Specific Considerations

### 1. No Built-In File Writing
Unlike `DataGenerator`, `SparkGenerator` does **not** provide `.write` or `.writeStream` methods. Use Spark's native API:

```python
# Generate Spark DataFrame
df = SparkGenerator(spark, F, spec).size(10_000_000).get_df()

# Write using Spark API
df.write.format("parquet").mode("overwrite").save("/path/to/output")
df.write.format("delta").mode("append").saveAsTable("my_table")
df.write.format("json").save("s3://bucket/data/")
```

### 2. Distributed Execution
Spark distributes generation across cluster nodes:

```python
# 100M rows distributed across executors
df = SparkGenerator(spark, F, spec).size(100_000_000).get_df()

# Control partitioning
df = df.repartition(200)  # 200 partitions
df.write.parquet("/output")
```

### 3. Type Mapping (NPCore → Spark)
Spark automatically maps NPCore integer types to Spark types:

| NPCore Type | Spark Type |
|-------------|------------|
| `int8`, `int16`, `int32` | `int` |
| `int64`, `uint64` | `bigint` |
| `uint8`, `uint16`, `uint32` | Mapped automatically |

### 4. No Transformers Support
`SparkGenerator` does **not** support `.transformers()`. Apply transformations using Spark:

```python
# Generate base data
df = SparkGenerator(spark, F, spec).size(1_000_000).get_df()

# Apply Spark transformations
df = df.withColumn("age_group", F.when(F.col("age") >= 18, "adult").otherwise("minor"))
df = df.withColumn("created_at", F.current_timestamp())
```

### 5. No Constraints (PK/FK)
`SparkGenerator` does **not** support constraints. For related entities, use `DataGenerator` to generate checkpoints, then convert to Spark:

```python
from rand_engine.main.data_generator import DataGenerator
from rand_engine.integrations.duckdb_handler import DuckDBHandler

# Generate with constraints using DataGenerator
db_conn = DuckDBHandler(db_path="checkpoints.duckdb")
df_pandas = DataGenerator(spec_with_constraints).db_checkpoint(db_conn).size(1_000_000).get_df()

# Convert to Spark
df_spark = spark.createDataFrame(df_pandas)
df_spark.write.format("delta").save("/path/to/table")
```

---

## 🧪 Real-World Examples

### Example 1: Large-Scale User Dataset (100M rows)
```python
from pyspark.sql import SparkSession, functions as F
from rand_engine.main.spark_generator import SparkGenerator

spark = SparkSession.builder.appName("UserDataGen").getOrCreate()

spec = {
    "user_id": {"method": "int_zfilled", "kwargs": {"length": 10}},
    "age": {"method": "integers", "kwargs": {"min": 18, "max": 80}},
    "score": {"method": "floats_normal", "kwargs": {"mean": 75.0, "std": 10.0, "decimals": 1}},
    "is_premium": {"method": "booleans", "kwargs": {"true_prob": 0.15}},
    "signup_date": {"method": "dates", "kwargs": {
        "start": "2020-01-01",
        "end": "2023-12-31",
        "date_format": "%Y-%m-%d"
    }}
}

# Generate 100 million rows
df = SparkGenerator(spark, F, spec).size(100_000_000).get_df()

# Write to Delta Lake
df.write.format("delta").mode("overwrite").save("/mnt/data/users")
```

### Example 2: Databricks IoT Sensor Data
```python
spec = {
    "sensor_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "temperature": {"method": "floats_normal", "kwargs": {"mean": 22.0, "std": 5.0, "decimals": 1}},
    "humidity": {"method": "floats", "kwargs": {"min": 30.0, "max": 90.0, "decimals": 1}},
    "status": {"method": "distincts_prop", "kwargs": {"distincts": {
        "OK": 90,
        "WARNING": 8,
        "ERROR": 2
    }}},
    "timestamp": {"method": "unix_timestamps", "kwargs": {
        "start": "2023-01-01",
        "end": "2023-12-31"
    }}
}

df = SparkGenerator(spark, F, spec).size(50_000_000).get_df()

# Add timestamp conversion
df = df.withColumn("timestamp", F.from_unixtime("timestamp").cast("timestamp"))

# Write partitioned by date
df.write.format("delta").partitionBy("status").mode("overwrite").save("/mnt/iot/sensors")
```

### Example 3: E-commerce Transactions at Scale
```python
spec = {
    "transaction_id": {"method": "int_zfilled", "kwargs": {"length": 12}},
    "customer_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "amount": {"method": "floats_normal", "kwargs": {"mean": 150.0, "std": 75.0, "decimals": 2}},
    "payment_method": {"method": "distincts", "kwargs": {"distincts": [
        "credit_card", "debit_card", "paypal", "bank_transfer"
    ]}},
    "created_at": {"method": "dates", "kwargs": {
        "start": "2023-01-01 00:00:00",
        "end": "2023-12-31 23:59:59",
        "date_format": "%Y-%m-%d %H:%M:%S"
    }}
}

df = SparkGenerator(spark, F, spec).size(500_000_000).get_df()

# Repartition for better parallelism
df = df.repartition(500)

# Write to S3
df.write.format("parquet").mode("overwrite").save("s3://my-bucket/transactions/")
```

---

## 🔄 DataGenerator vs SparkGenerator

| Feature | DataGenerator | SparkGenerator |
|---------|---------------|----------------|
| **Output** | pandas DataFrame | Spark DataFrame |
| **Environment** | Local, single-node | Databricks, EMR, Spark clusters |
| **Scale** | Up to ~10M rows (memory-bound) | Billions of rows (distributed) |
| **Methods** | All (common + advanced) | Common only (advanced → NULL) |
| **Constraints (PK/FK)** | ✅ Yes | ❌ No |
| **Transformers** | ✅ Yes | ❌ No (use Spark transformations) |
| **File Writing** | ✅ Built-in (write, writeStream) | ❌ Use Spark `.write` |
| **Streaming** | ✅ `stream_dict()` | ❌ Use Spark Structured Streaming |
| **Seed Support** | ✅ Yes | ❌ No |

---

## 💡 When to Use SparkGenerator

**Use SparkGenerator when:**
- ✅ Generating **billions of rows** (> 10M)
- ✅ Working in **Databricks** or other Spark environments
- ✅ Need **distributed execution** across cluster
- ✅ Using **only common generation methods**
- ✅ Writing directly to **Delta Lake**, **S3**, or **HDFS**

**Use DataGenerator when:**
- ✅ Need **advanced methods** (distincts_map, complex_distincts)
- ✅ Need **constraints** (PK/FK relationships)
- ✅ Need **built-in file writing** abstractions
- ✅ Need **streaming** to Kafka/Kinesis
- ✅ Generating **< 10M rows** locally

---

## 📚 Related Documentation
- **[1_DATA_GENERATOR.md](1_DATA_GENERATOR.md)** - Pandas-based generation (full features)
- **[3_WRITING_FILES.md](3_WRITING_FILES.md)** - File writing (DataGenerator only)
- **[4_CONSTRAINTS.md](4_CONSTRAINTS.md)** - Constraints (DataGenerator only)
