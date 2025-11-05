# Writing Files - Batch and Streaming Writers

## 📋 Overview
`DataGenerator` provides built-in **file writing abstractions** that simplify exporting generated data to files without directly dealing with pandas `.to_csv()`, `.to_json()`, or `.to_parquet()`. The library offers two writer modes:

1. **`write`** - Batch writing (single or multiple files)
2. **`writeStream`** - Streaming writing (continuous file generation with time-based triggers)

⚠️ **Note:** `SparkGenerator` does **NOT** have built-in file writing. Use Spark's native `.write` API.

---

## 🎯 Key Features
- ✅ **Fluent API** - Method chaining for configuration
- ✅ **Multiple formats** - CSV, JSON, Parquet support
- ✅ **Batch & streaming** - Single batch or continuous file generation
- ✅ **Overwrite/Append modes** - Control file handling behavior
- ✅ **Multi-file generation** - Generate multiple parts in one call
- ✅ **Streaming triggers** - Control file generation frequency

---

## 🏗️ Batch Writer (`write`)

### Basic Usage
```python
from rand_engine.main.data_generator import DataGenerator

spec = {
    "user_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}
}

# Generate and write to CSV
(
    DataGenerator(spec)
    .size(10_000)
    .write
    .format("csv")
    .mode("overwrite")
    .save("/path/to/output.csv")
)
```

### Methods

#### `format(format: str)`
Sets the output file format. Supported formats:
- `"csv"` - Comma-separated values
- `"json"` - JSON format
- `"parquet"` - Apache Parquet

**Example:**
```python
.write.format("parquet")
```

#### `mode(mode: str)`
Sets the write mode:
- `"overwrite"` - Delete existing files and create new ones
- `"append"` - Add to existing files

**Example:**
```python
.write.mode("overwrite")
```

#### `option(key: str, value: Any)`
Sets format-specific options. Common options:

**CSV Options:**
- `index=False` - Don't write row index
- `sep=";"` - Use semicolon as delimiter
- `compression="gzip"` - Compress output

**JSON Options:**
- `orient="records"` - JSON format (default)
- `force_ascii=False` - Support Unicode characters
- `indent=2` - Pretty-print JSON

**Parquet Options:**
- `engine="fastparquet"` - Parquet engine
- `compression="snappy"` - Compression codec

**Multi-file Options:**
- `numFiles=10` - Generate 10 separate files

**Example:**
```python
.write.format("csv").option("sep", ";").option("compression", "gzip")
```

#### `save(path: str)`
Executes the write operation and saves to the specified path.

**Example:**
```python
.save("/data/users.csv")
```

---

## 📦 Batch Writing Examples

### Example 1: Write Single CSV File
```python
from rand_engine.main.data_generator import DataGenerator

spec = {
    "transaction_id": {"method": "int_zfilled", "kwargs": {"length": 12}},
    "amount": {"method": "floats", "kwargs": {"min": 10.0, "max": 1000.0, "decimals": 2}}
}

(
    DataGenerator(spec, seed=42)
    .size(50_000)
    .write
    .format("csv")
    .mode("overwrite")
    .option("index", False)
    .option("compression", "gzip")
    .save("/data/transactions.csv")
)

# Creates: /data/transactions.csv.gz
```

### Example 2: Write Multiple Parquet Files
```python
(
    DataGenerator(spec)
    .size(100_000)
    .write
    .format("parquet")
    .mode("overwrite")
    .option("numFiles", 5)  # Generate 5 separate files
    .option("compression", "snappy")
    .save("/data/users")
)

# Creates:
# /data/users/part_xxxxx-xxxx-xxxx.parquet
# /data/users/part_yyyyy-yyyy-yyyy.parquet
# ... (5 files total)
```

### Example 3: Write JSON with Unicode Support
```python
spec = {
    "name": {"method": "distincts", "kwargs": {"distincts": ["José", "María", "François"]}},
    "email": {"method": "distincts", "kwargs": {"distincts": ["user@example.com"]}}
}

(
    DataGenerator(spec)
    .size(1_000)
    .write
    .format("json")
    .mode("overwrite")
    .option("force_ascii", False)  # Support Unicode characters
    .option("indent", 2)  # Pretty-print
    .save("/data/users.json")
)
```

### Example 4: Append Mode (Add to Existing File)
```python
# First write
(
    DataGenerator(spec)
    .size(5_000)
    .write
    .format("csv")
    .mode("overwrite")
    .save("/data/logs.csv")
)

# Later: append more data
(
    DataGenerator(spec)
    .size(5_000)
    .write
    .format("csv")
    .mode("append")  # Adds to existing file
    .save("/data/logs.csv")
)
```

---

## 🌊 Streaming Writer (`writeStream`)

### Basic Usage
```python
from rand_engine.main.data_generator import DataGenerator

spec = {
    "sensor_id": {"method": "int_zfilled", "kwargs": {"length": 6}},
    "temperature": {"method": "floats_normal", "kwargs": {"mean": 22.0, "std": 5.0, "decimals": 1}}
}

# Generate files every 5 seconds for 60 seconds
(
    DataGenerator(spec)
    .size(100)  # 100 rows per file
    .writeStream
    .format("json")
    .mode("overwrite")
    .trigger(5)  # Generate file every 5 seconds
    .option("timeout", 60)  # Stop after 60 seconds
    .start("/data/stream")
)
```

### Methods

#### `trigger(frequency: int)`
Sets the time interval (in seconds) between file generations.

**Example:**
```python
.writeStream.trigger(10)  # Generate file every 10 seconds
```

#### `option(key: str, value: Any)`
Sets format and streaming options:
- `timeout=60` - Stop streaming after N seconds (default: 20)
- All format-specific options from batch writer apply

**Example:**
```python
.writeStream.option("timeout", 120).option("force_ascii", False)
```

#### `start(path: str)`
Starts the streaming write operation. **Blocks until timeout is reached.**

**Example:**
```python
.start("/data/stream")
```

---

## 🌊 Streaming Writing Examples

### Example 1: IoT Sensor Data Stream
```python
spec = {
    "sensor_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "temperature": {"method": "floats_normal", "kwargs": {"mean": 25.0, "std": 3.0, "decimals": 1}},
    "humidity": {"method": "floats", "kwargs": {"min": 40.0, "max": 80.0, "decimals": 1}},
    "timestamp": {"method": "unix_timestamps", "kwargs": {
        "start": "2023-01-01",
        "end": "2023-12-31"
    }}
}

# Generate 200 rows every 3 seconds for 5 minutes
(
    DataGenerator(spec, seed=42)
    .size(200)
    .writeStream
    .format("json")
    .mode("overwrite")
    .trigger(3)  # Every 3 seconds
    .option("timeout", 300)  # 5 minutes total
    .option("force_ascii", False)
    .start("/data/iot_stream")
)

# Creates files continuously:
# /data/iot_stream/part-xxxxx.json
# /data/iot_stream/part-yyyyy.json
# ... (100 files over 5 minutes)
```

### Example 2: Web Server Logs Streaming
```python
spec = {
    "ip_address": {"method": "complex_distincts", "kwargs": {
        "pattern": "x.x.x.x",
        "replacement": "x",
        "templates": [
            {"method": "distincts", "kwargs": {"distincts": ["192", "10"]}},
            {"method": "integers", "kwargs": {"min": 0, "max": 255}},
            {"method": "integers", "kwargs": {"min": 0, "max": 255}},
            {"method": "integers", "kwargs": {"min": 1, "max": 254}}
        ]
    }},
    "http_method": {"method": "distincts_prop", "kwargs": {"distincts": {
        "GET": 70,
        "POST": 20,
        "PUT": 5,
        "DELETE": 5
    }}},
    "status_code": {"method": "distincts_prop", "kwargs": {"distincts": {
        "200": 80,
        "404": 10,
        "500": 10
    }}}
}

# Stream logs as CSV every 10 seconds
(
    DataGenerator(spec)
    .size(500)
    .writeStream
    .format("csv")
    .mode("overwrite")
    .trigger(10)
    .option("timeout", 600)  # 10 minutes
    .option("index", False)
    .start("/var/log/stream")
)
```

### Example 3: Financial Transactions Stream (Parquet)
```python
spec = {
    "transaction_id": {"method": "int_zfilled", "kwargs": {"length": 12}},
    "customer_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "amount": {"method": "floats_normal", "kwargs": {"mean": 200.0, "std": 100.0, "decimals": 2}},
    "currency": {"method": "distincts", "kwargs": {"distincts": ["USD", "EUR", "GBP"]}}
}

# Generate Parquet files every 30 seconds
(
    DataGenerator(spec)
    .size(1_000)
    .writeStream
    .format("parquet")
    .mode("overwrite")
    .trigger(30)
    .option("timeout", 1800)  # 30 minutes
    .option("compression", "snappy")
    .start("/data/transactions_stream")
)
```

---

## 🔧 Technical Details

### File Naming Convention
- **Batch (single file):** `{filename}.{extension}`
- **Batch (multiple files):** `{filename}/part_{uuid}.{extension}`
- **Streaming:** `{directory}/part-{uuid}.{extension}`

### Directory Creation
- Directories are **automatically created** if they don't exist
- No need to pre-create output paths

### Overwrite Mode Behavior
- **Batch:** Deletes existing file(s) before writing
- **Streaming:** Clears directory before starting stream

### Append Mode Behavior
- **Batch:** Adds data to existing file
- **Streaming:** Not recommended (files accumulate indefinitely)

### Internal Implementation
- Uses pandas `.to_csv()`, `.to_json()`, `.to_parquet()` under the hood
- Abstracts complexity of multiple file handling
- Handles UUIDs for unique file names

---

## ⚠️ Important Notes

### 1. SparkGenerator Does NOT Support File Writing
```python
# ❌ WRONG - No .write or .writeStream in SparkGenerator
from rand_engine.main.spark_generator import SparkGenerator

df = SparkGenerator(spark, F, spec).size(1_000_000).get_df()
# df.write ???  # Doesn't exist

# ✅ CORRECT - Use Spark's native API
df.write.format("parquet").mode("overwrite").save("/path/to/output")
```

### 2. Streaming Timeout is Required
Without `timeout`, streaming runs indefinitely (default 20 seconds):

```python
# Runs for 20 seconds (default)
.writeStream.trigger(5).start("/data")

# Runs for 300 seconds
.writeStream.trigger(5).option("timeout", 300).start("/data")
```

### 3. Size in Streaming is Per-File
```python
# Generates 100 rows per file, NOT total
DataGenerator(spec).size(100).writeStream...
```

### 4. Compression Auto-Detection
File extension is automatically adjusted for compression:

```python
.option("compression", "gzip").save("/data/output.csv")
# Creates: /data/output.csv.gz (not output.csv)
```

---

## 📊 Comparison: Batch vs Streaming

| Feature | Batch (`write`) | Streaming (`writeStream`) |
|---------|-----------------|---------------------------|
| **Output** | Single file or N files at once | Continuous file generation |
| **Execution** | Returns immediately | Blocks until timeout |
| **Use Case** | One-time exports | Continuous data simulation |
| **Trigger** | N/A | Time-based (seconds) |
| **Timeout** | N/A | Required (default 20s) |
| **File Count** | Fixed (1 or N via numFiles) | Grows over time |

---

## 🧪 Complete Examples

### Example: Generate and Write Multiple Formats
```python
from rand_engine.main.data_generator import DataGenerator

spec = {
    "user_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "name": {"method": "distincts", "kwargs": {"distincts": ["Alice", "Bob", "Charlie"]}},
    "age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}
}

generator = DataGenerator(spec, seed=42).size(10_000)

# Write to CSV
generator.write.format("csv").mode("overwrite").save("/data/users.csv")

# Write to JSON
generator.write.format("json").mode("overwrite").save("/data/users.json")

# Write to Parquet
generator.write.format("parquet").mode("overwrite").save("/data/users.parquet")
```

### Example: Batch with Multiple Files and Transformers
```python
def add_timestamp(df):
    from datetime import datetime
    df["created_at"] = datetime.now()
    return df

(
    DataGenerator(spec)
    .size(50_000)
    .transformers([add_timestamp])  # Add timestamp before writing
    .write
    .format("parquet")
    .mode("overwrite")
    .option("numFiles", 10)  # 10 files, ~5000 rows each
    .option("compression", "snappy")
    .save("/data/users_partitioned")
)
```

---

## 📚 Related Documentation
- **[1_DATA_GENERATOR.md](1_DATA_GENERATOR.md)** - DataGenerator methods and RandSpecs
- **[2_SPARK_GENERATOR.md](2_SPARK_GENERATOR.md)** - SparkGenerator (use Spark's .write)
- **[4_CONSTRAINTS.md](4_CONSTRAINTS.md)** - Constraints and checkpoints
