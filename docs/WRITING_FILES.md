# 📝 Writing Files with rand_engine

> **Version:** 0.6.1  
> **Complete Guide:** File writing modes, formats, and compression options

---

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Comparison: Batch vs Stream](#quick-comparison-batch-vs-stream)
- [Batch Mode](#batch-mode)
  - [Single File](#single-file)
  - [Multiple Files](#multiple-files)
  - [Overwrite vs Append](#overwrite-vs-append)
- [Streaming Mode](#streaming-mode)
  - [Continuous Generation](#continuous-generation)
  - [Timeout and Trigger](#timeout-and-trigger)
  - [Streaming Append](#streaming-append)
- [Supported Formats](#supported-formats)
  - [CSV](#csv)
  - [JSON](#json)
  - [Parquet](#parquet)
- [Compression Options](#compression-options)
  - [CSV/JSON Compression](#csvjson-compression)
  - [Parquet Compression](#parquet-compression)
  - [File Extensions](#file-extensions)
- [File Naming Patterns](#file-naming-patterns)
- [Complete API Reference](#complete-api-reference)
- [Practical Examples](#practical-examples)
- [Performance Considerations](#performance-considerations)
- [Troubleshooting](#troubleshooting)

---

## Overview

`rand_engine` provides **two distinct writing modes** for generating and exporting data:

1. **Batch Mode** (`.write`): Generate all data at once and write to one or multiple files
2. **Streaming Mode** (`.writeStream`): Continuously generate data over time with configurable frequency

Both modes support:
- ✅ **3 formats**: CSV, JSON, Parquet
- ✅ **Multiple compression types** per format
- ✅ **Overwrite or append modes**
- ✅ **Fluent API** for easy configuration

---

## Quick Comparison: Batch vs Stream

| Feature | Batch Mode (`.write`) | Streaming Mode (`.writeStream`) |
|---------|----------------------|----------------------------------|
| **Use Case** | Single data dump, one-time export | Continuous data generation, time-series simulation |
| **Generation** | All records at once | Records generated over time |
| **File Count** | 1 or N files (via `numFiles`) | Multiple files based on timeout/trigger |
| **Timing** | Immediate | Controlled by `timeout` + `trigger(frequency)` |
| **API Method** | `.save(path)` | `.start(path)` |
| **Mode Support** | `overwrite`, `append` | `overwrite`, `append` |

**When to use Batch:**
- One-time data exports
- Testing with fixed datasets
- ETL pipeline inputs
- Database loading

**When to use Streaming:**
- Simulating real-time data sources
- Time-series data generation
- Load testing over time
- Event stream simulation

---

## Batch Mode

Batch mode generates all data at once and writes to one or more files.

### Single File

Generate a single file with all records:

```python
from rand_engine import DataGenerator

spec = {
    "id": {"method": "gen_incremental"},
    "name": {"method": "gen_name"},
    "age": {"method": "gen_ints", "parms": {"min": 18, "max": 65}}
}

# Single CSV file
DataGenerator(spec).write \
    .size(10000) \
    .format("csv") \
    .mode("overwrite") \
    .save("output/users.csv")
```

**Output:**
```
output/
└── users.csv  (10,000 records)
```

### Multiple Files

Use `option("numFiles", N)` to split data across multiple files:

```python
# Generate 5 Parquet files
DataGenerator(spec).write \
    .size(100000) \
    .format("parquet") \
    .option("numFiles", 5) \
    .option("compression", "snappy") \
    .mode("overwrite") \
    .save("output/users.parquet")
```

**Output:**
```
output/
└── users/
    ├── part_a1b2c3d4e5f6g7h8.parquet  (~20,000 records)
    ├── part_b2c3d4e5f6g7h8i9.parquet  (~20,000 records)
    ├── part_c3d4e5f6g7h8i9j0.parquet  (~20,000 records)
    ├── part_d4e5f6g7h8i9j0k1.parquet  (~20,000 records)
    └── part_e5f6g7h8i9j0k1l2.parquet  (~20,000 records)
```

**Key Points:**
- Each file gets a unique UUID prefix (`part_{uuid}`)
- Records are distributed across files
- Total size (100,000) ÷ number of files (5) = ~20,000 per file
- Creates a directory structure automatically

### Overwrite vs Append

**Overwrite Mode** (default): Replaces existing files

```python
# First write: Creates 2 files
DataGenerator(spec).write \
    .size(1000) \
    .option("numFiles", 2) \
    .mode("overwrite") \
    .save("output/data.parquet")

# Second write: REPLACES the 2 files with new 2 files
DataGenerator(spec).write \
    .size(1000) \
    .option("numFiles", 2) \
    .mode("overwrite") \
    .save("output/data.parquet")
```

**Result:** 2 files (second write replaced first write)

**Append Mode**: Adds more files to existing directory

```python
# First write: Creates 2 files
DataGenerator(spec).write \
    .size(1000) \
    .option("numFiles", 2) \
    .mode("overwrite") \
    .save("output/data.parquet")

# Second write: ADDS 2 more files (4 total)
DataGenerator(spec).write \
    .size(1000) \
    .option("numFiles", 2) \
    .mode("append") \
    .save("output/data.parquet")
```

**Result:** 4 files (first 2 + second 2)

---

## Streaming Mode

Streaming mode continuously generates data over a specified time period.

### Continuous Generation

Generate files continuously until timeout is reached:

```python
from rand_engine import DataGenerator

spec = {
    "timestamp": {"method": "gen_now"},
    "event": {"method": "gen_str_choice", "parms": {"options": ["click", "view", "purchase"]}},
    "user_id": {"method": "gen_ints", "parms": {"min": 1000, "max": 9999}}
}

# Stream for 60 seconds, new file every 5 seconds
DataGenerator(spec).writeStream \
    .size(100) \
    .format("json") \
    .option("timeout", 60) \
    .trigger(frequency=5) \
    .mode("overwrite") \
    .start("output/events")
```

**Output:**
```
output/
└── events/
    ├── part-uuid1.json  (generated at t=0s)
    ├── part-uuid2.json  (generated at t=5s)
    ├── part-uuid3.json  (generated at t=10s)
    ├── ...
    └── part-uuid12.json (generated at t=55s)
```

**Result:** 12 files (60 seconds ÷ 5 seconds per file = 12 files)

### Timeout and Trigger

Two key parameters control streaming:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `timeout` | Total duration (seconds) for streaming | `option("timeout", 3600)` = 1 hour |
| `trigger(frequency)` | Interval (seconds) between file generations | `trigger(frequency=60)` = 1 file per minute |

**Calculation:**
```
Number of files = timeout ÷ frequency
```

**Examples:**

```python
# Example 1: 1 hour of data, 1 file per minute
.option("timeout", 3600) \
.trigger(frequency=60)
# Result: 60 files

# Example 2: 10 minutes, 1 file every 30 seconds
.option("timeout", 600) \
.trigger(frequency=30)
# Result: 20 files

# Example 3: 24 hours, 1 file per hour
.option("timeout", 86400) \
.trigger(frequency=3600)
# Result: 24 files
```

### Streaming Append

Append mode continues adding files to the same directory:

```python
# First stream: 10 minutes, 1 file per minute
DataGenerator(spec).writeStream \
    .size(50) \
    .format("csv") \
    .option("timeout", 600) \
    .trigger(frequency=60) \
    .mode("overwrite") \
    .start("output/metrics")
# Creates 10 files

# Second stream: Additional 5 minutes (append mode)
DataGenerator(spec).writeStream \
    .size(50) \
    .option("timeout", 300) \
    .trigger(frequency=60) \
    .mode("append") \
    .start("output/metrics")
# Adds 5 more files (15 total)
```

**Result:** 15 files (10 from first stream + 5 from second stream)

---

## Supported Formats

### CSV

Comma-separated values format (RFC 4180).

**Basic Usage:**

```python
DataGenerator(spec).write \
    .size(1000) \
    .format("csv") \
    .save("output/data.csv")
```

**Options:**

```python
DataGenerator(spec).write \
    .size(1000) \
    .format("csv") \
    .option("sep", ";")           # Delimiter (default: ",")
    .option("decimal", ",")       # Decimal separator (default: ".")
    .option("encoding", "utf-8")  # File encoding
    .option("index", False)       # Include pandas index
    .option("compression", "gzip") # See compression section
    .save("output/data.csv.gz")
```

**Characteristics:**
- ✅ Human-readable
- ✅ Widely supported
- ✅ Small file size with compression
- ❌ No schema enforcement
- ❌ Slower parsing than Parquet

### JSON

JavaScript Object Notation format.

**Basic Usage:**

```python
DataGenerator(spec).write \
    .size(1000) \
    .format("json") \
    .save("output/data.json")
```

**Options:**

```python
DataGenerator(spec).write \
    .size(1000) \
    .format("json") \
    .option("orient", "records")    # JSON structure (default)
    .option("lines", True)          # One JSON object per line (JSONL)
    .option("force_ascii", False)   # Allow Unicode characters
    .option("indent", 2)            # Pretty-print with indentation
    .option("compression", "gzip")  # See compression section
    .save("output/data.json.gz")
```

**JSON Orientations:**

```python
# records (default): [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
.option("orient", "records")

# split: {"columns": ["a", "b"], "data": [[1, 2], [3, 4]]}
.option("orient", "split")

# index: {"0": {"a": 1, "b": 2}, "1": {"a": 3, "b": 4}}
.option("orient", "index")
```

**Characteristics:**
- ✅ Human-readable
- ✅ Flexible structure
- ✅ Web API compatible
- ❌ Larger file size than Parquet
- ❌ No schema enforcement

### Parquet

Apache Parquet columnar storage format.

**Basic Usage:**

```python
DataGenerator(spec).write \
    .size(1000) \
    .format("parquet") \
    .save("output/data.parquet")
```

**Options:**

```python
DataGenerator(spec).write \
    .size(1000) \
    .format("parquet") \
    .option("compression", "snappy")  # See compression section
    .option("engine", "pyarrow")      # Parquet engine (pyarrow/fastparquet)
    .option("index", False)           # Include pandas index
    .save("output/data.parquet")
```

**Characteristics:**
- ✅ Columnar storage (efficient queries)
- ✅ Built-in compression
- ✅ Schema enforcement
- ✅ Fast read/write performance
- ✅ Small file size
- ❌ Not human-readable (binary format)

---

## Compression Options

### CSV/JSON Compression

CSV and JSON support **external compression** (file is compressed as a whole).

**Supported Codecs:**

| Codec | Extension | Compression Ratio | Speed | Use Case |
|-------|-----------|-------------------|-------|----------|
| `gzip` | `.csv.gz`, `.json.gz` | High | Medium | General purpose, widely supported |
| `bz2` | `.csv.bz2`, `.json.bz2` | Very High | Slow | Maximum compression |
| `zip` | `.csv.zip`, `.json.zip` | High | Fast | Windows compatibility |
| `xz` | `.csv.xz`, `.json.xz` | Very High | Slow | Long-term archival |
| None | `.csv`, `.json` | None | Fastest | No compression needed |

**Examples:**

```python
# CSV with gzip (recommended)
DataGenerator(spec).write \
    .size(10000) \
    .format("csv") \
    .option("compression", "gzip") \
    .save("output/data.csv.gz")

# JSON with bz2 (maximum compression)
DataGenerator(spec).write \
    .size(10000) \
    .format("json") \
    .option("compression", "bz2") \
    .save("output/data.json.bz2")

# No compression
DataGenerator(spec).write \
    .size(10000) \
    .format("csv") \
    .save("output/data.csv")
```

### Parquet Compression

Parquet uses **internal compression** (each column is compressed separately).

**Supported Codecs:**

| Codec | Speed | Compression Ratio | CPU Usage | Use Case |
|-------|-------|-------------------|-----------|----------|
| `snappy` (default) | Very Fast | Medium | Low | General purpose, balanced |
| `gzip` | Medium | High | Medium | Good compression, slower writes |
| `zstd` | Fast | Very High | Medium | Best compression, modern |
| `lz4` | Very Fast | Low-Medium | Low | Speed over compression |
| `brotli` | Slow | Very High | High | Maximum compression |
| None | Fastest | None | Lowest | No compression needed |

**Examples:**

```python
# Snappy (default, recommended)
DataGenerator(spec).write \
    .size(100000) \
    .format("parquet") \
    .option("compression", "snappy") \
    .save("output/data.parquet")

# Zstd (best compression)
DataGenerator(spec).write \
    .size(100000) \
    .format("parquet") \
    .option("compression", "zstd") \
    .save("output/data.parquet")

# No compression
DataGenerator(spec).write \
    .size(100000) \
    .format("parquet") \
    .option("compression", None) \
    .save("output/data.parquet")
```

**Parquet Compression Benchmark** (1M records):

```
Codec    | File Size | Write Time | Read Time | CPU
---------|-----------|------------|-----------|-----
None     | 45.2 MB   | 1.2s       | 0.8s      | Low
snappy   | 12.8 MB   | 1.5s       | 1.0s      | Low
gzip     | 8.4 MB    | 2.8s       | 1.4s      | Med
zstd     | 7.2 MB    | 2.0s       | 1.2s      | Med
lz4      | 14.5 MB   | 1.3s       | 0.9s      | Low
brotli   | 6.8 MB    | 5.2s       | 1.8s      | High
```

### File Extensions

**CSV/JSON (External Compression):**
```
Format  | Compression | Extension
--------|-------------|------------------
CSV     | None        | .csv
CSV     | gzip        | .csv.gz
CSV     | bz2         | .csv.bz2
CSV     | zip         | .csv.zip
CSV     | xz          | .csv.xz
JSON    | None        | .json
JSON    | gzip        | .json.gz
JSON    | bz2         | .json.bz2
JSON    | zip         | .json.zip
JSON    | xz          | .json.xz
```

**Parquet (Internal Compression):**
```
Format  | Compression    | Extension
--------|----------------|------------------
Parquet | All codecs     | .parquet
```

**Important:** Parquet compression is internal to the file format. The extension is always `.parquet` regardless of the compression codec used.

---

## File Naming Patterns

### Single File (Batch Mode)

```python
DataGenerator(spec).write \
    .save("output/data.csv")
```

**Result:**
```
output/
└── data.csv
```

### Multiple Files (Batch Mode)

```python
DataGenerator(spec).write \
    .option("numFiles", 3) \
    .save("output/data.csv")
```

**Result:**
```
output/
└── data/
    ├── part_a1b2c3d4e5f6g7h8.csv
    ├── part_b2c3d4e5f6g7h8i9.csv
    └── part_c3d4e5f6g7h8i9j0.csv
```

**Pattern:** `part_{uuid}.{ext}`

### Streaming Mode

```python
DataGenerator(spec).writeStream \
    .option("timeout", 10) \
    .trigger(frequency=2) \
    .start("output/stream")
```

**Result:**
```
output/
└── stream/
    ├── part-uuid1.json
    ├── part-uuid2.json
    ├── part-uuid3.json
    ├── part-uuid4.json
    └── part-uuid5.json
```

**Pattern:** `part-{uuid}.{ext}`

**Note:** UUIDs are unique identifiers (18 characters for batch, full UUID for streaming).

---

## Complete API Reference

### Batch Mode

```python
DataGenerator(spec).write \
    .size(int)                    # Number of records
    .format(str)                  # "csv", "json", "parquet"
    .mode(str)                    # "overwrite" (default), "append"
    .option(key, value)           # Format-specific options
    .save(path: str)              # Write to file(s)
```

**Options:**

| Option | Formats | Description | Example |
|--------|---------|-------------|---------|
| `numFiles` | All | Number of files to create | `option("numFiles", 5)` |
| `compression` | All | Compression codec | `option("compression", "gzip")` |
| `sep` | CSV | Field delimiter | `option("sep", ";")` |
| `decimal` | CSV | Decimal separator | `option("decimal", ",")` |
| `encoding` | CSV, JSON | File encoding | `option("encoding", "utf-8")` |
| `index` | All | Include pandas index | `option("index", False)` |
| `orient` | JSON | JSON structure | `option("orient", "records")` |
| `lines` | JSON | JSONL format | `option("lines", True)` |
| `indent` | JSON | Pretty-print indentation | `option("indent", 2)` |
| `engine` | Parquet | Parquet engine | `option("engine", "pyarrow")` |

### Streaming Mode

```python
DataGenerator(spec).writeStream \
    .size(int)                    # Records per file
    .format(str)                  # "csv", "json", "parquet"
    .mode(str)                    # "overwrite" (default), "append"
    .option("timeout", int)       # Total duration (seconds)
    .trigger(frequency=int)       # Interval between files (seconds)
    .option(key, value)           # Format-specific options
    .start(path: str)             # Start streaming
```

**Required Options:**

| Option | Description | Example |
|--------|-------------|---------|
| `timeout` | Total streaming duration (seconds) | `option("timeout", 3600)` |
| `frequency` | File generation interval (seconds) | `trigger(frequency=60)` |

---

## Practical Examples

### Example 1: E-commerce Orders (Single CSV)

```python
from rand_engine import DataGenerator

spec = {
    "order_id": {"method": "gen_incremental"},
    "customer_id": {"method": "gen_ints", "parms": {"min": 1000, "max": 9999}},
    "product": {"method": "gen_str_choice", "parms": {"options": ["Laptop", "Phone", "Tablet"]}},
    "price": {"method": "gen_floats", "parms": {"min": 100, "max": 2000, "round": 2}},
    "order_date": {"method": "gen_dates", "parms": {"date_min": "2024-01-01", "date_max": "2024-12-31"}}
}

# Single compressed CSV file
DataGenerator(spec).write \
    .size(50000) \
    .format("csv") \
    .option("compression", "gzip") \
    .mode("overwrite") \
    .save("output/orders_2024.csv.gz")
```

### Example 2: User Data (Multiple Parquet Files)

```python
spec = {
    "user_id": {"method": "gen_incremental"},
    "name": {"method": "gen_name"},
    "email": {"method": "gen_email"},
    "age": {"method": "gen_ints", "parms": {"min": 18, "max": 80}},
    "country": {"method": "gen_str_choice", "parms": {"options": ["USA", "UK", "Brazil", "Germany"]}}
}

# Split into 10 Parquet files for parallel processing
DataGenerator(spec).write \
    .size(1000000) \
    .format("parquet") \
    .option("numFiles", 10) \
    .option("compression", "zstd") \
    .mode("overwrite") \
    .save("output/users.parquet")
```

### Example 3: Real-Time Events (Streaming JSON)

```python
spec = {
    "event_id": {"method": "gen_uuid"},
    "timestamp": {"method": "gen_now"},
    "event_type": {"method": "gen_str_choice", "parms": {"options": ["click", "view", "purchase", "search"]}},
    "user_id": {"method": "gen_ints", "parms": {"min": 1, "max": 10000}},
    "page": {"method": "gen_str_choice", "parms": {"options": ["/home", "/products", "/cart", "/checkout"]}}
}

# Stream for 1 hour, new file every minute
DataGenerator(spec).writeStream \
    .size(500) \
    .format("json") \
    .option("compression", "gzip") \
    .option("timeout", 3600) \
    .trigger(frequency=60) \
    .mode("overwrite") \
    .start("output/events")
```

### Example 4: IoT Sensor Data (Streaming CSV)

```python
spec = {
    "sensor_id": {"method": "gen_str_choice", "parms": {"options": ["S001", "S002", "S003", "S004", "S005"]}},
    "timestamp": {"method": "gen_now"},
    "temperature": {"method": "gen_floats", "parms": {"min": -10, "max": 45, "round": 1}},
    "humidity": {"method": "gen_floats", "parms": {"min": 20, "max": 90, "round": 1}},
    "pressure": {"method": "gen_floats", "parms": {"min": 980, "max": 1040, "round": 2}}
}

# Stream for 24 hours, new file every hour
DataGenerator(spec).writeStream \
    .size(3600) \
    .format("csv") \
    .option("compression", "gzip") \
    .option("timeout", 86400) \
    .trigger(frequency=3600) \
    .mode("overwrite") \
    .start("output/sensors")
```

### Example 5: Append Mode (Incremental Data)

```python
spec = {
    "transaction_id": {"method": "gen_incremental"},
    "amount": {"method": "gen_floats", "parms": {"min": 10, "max": 500, "round": 2}},
    "timestamp": {"method": "gen_now"}
}

# Day 1: Initial load
DataGenerator(spec).write \
    .size(10000) \
    .format("parquet") \
    .option("numFiles", 2) \
    .mode("overwrite") \
    .save("output/transactions.parquet")

# Day 2: Add more data (append mode)
DataGenerator(spec).write \
    .size(5000) \
    .option("numFiles", 1) \
    .mode("append") \
    .save("output/transactions.parquet")

# Result: 3 files (2 from day 1 + 1 from day 2)
```

---

## Performance Considerations

### File Size Recommendations

| Records | Format | Files | Recommendation |
|---------|--------|-------|----------------|
| < 10K | CSV/JSON | 1 | Single file, gzip compression |
| 10K - 100K | CSV/JSON | 1 | Single file, gzip compression |
| 100K - 1M | Parquet | 1-5 | Single or few files, snappy compression |
| 1M - 10M | Parquet | 5-20 | Multiple files, zstd compression |
| 10M+ | Parquet | 20-100 | Many files, zstd compression |

### Compression Trade-offs

**Speed Priority (Fast writes/reads):**
```python
# CSV/JSON: No compression or gzip
.format("csv")

# Parquet: snappy or lz4
.format("parquet").option("compression", "snappy")
```

**Size Priority (Minimum disk usage):**
```python
# CSV/JSON: bz2 or xz
.format("csv").option("compression", "bz2")

# Parquet: zstd or brotli
.format("parquet").option("compression", "zstd")
```

**Balanced (Recommended):**
```python
# CSV/JSON: gzip
.format("csv").option("compression", "gzip")

# Parquet: snappy or zstd
.format("parquet").option("compression", "snappy")
```

### Parallel Processing

**Multiple Files for Parallel Reads:**

```python
# Create 10 files for 10 parallel workers
DataGenerator(spec).write \
    .size(1000000) \
    .option("numFiles", 10) \
    .save("output/data.parquet")

# Each worker reads one file
import pandas as pd
from glob import glob

files = glob("output/data/part_*.parquet")
for file in files:
    df = pd.read_parquet(file)
    process(df)  # Process in parallel
```

### Memory Management

**Large Datasets (Streaming Approach):**

```python
# Instead of generating 100M records at once (high memory):
DataGenerator(spec).write.size(100000000).save("output/data.parquet")

# Generate in chunks with streaming:
DataGenerator(spec).writeStream \
    .size(1000000) \
    .option("timeout", 100) \
    .trigger(frequency=1) \
    .start("output/data")
# Creates 100 files × 1M records = 100M total (low memory)
```

---

## Troubleshooting

### Common Issues

#### Issue 1: "Permission Denied" Error

**Problem:** Cannot write to file or directory

**Solutions:**
```bash
# Check permissions
ls -la output/

# Fix permissions
chmod 755 output/

# Or write to a different location
DataGenerator(spec).write.save("/tmp/data.csv")
```

#### Issue 2: Files Not Created in Streaming Mode

**Problem:** `start()` returns but no files created

**Cause:** `timeout` is too short or `frequency` is too long

**Solution:**
```python
# Ensure timeout > frequency
DataGenerator(spec).writeStream \
    .option("timeout", 10)    # At least 10 seconds
    .trigger(frequency=1)      # File every 1 second
    .start("output/stream")
# Creates ~10 files
```

#### Issue 3: Append Mode Not Working

**Problem:** Append mode replaces files instead of adding

**Cause:** Using single file path instead of directory

**Solution:**
```python
# ❌ Wrong: Single file path
.save("output/data.csv")

# ✅ Correct: Use numFiles to create directory
.option("numFiles", 2)
.save("output/data.csv")

# Then append works:
.option("numFiles", 2)
.mode("append")
.save("output/data.csv")
```

#### Issue 4: Compression Not Applied

**Problem:** File extension doesn't match compression

**Cause:** Manual extension conflicts with auto-detection

**Solution:**
```python
# ❌ Wrong: Manual extension with compression option
.option("compression", "gzip")
.save("output/data.csv")  # Creates data.csv (not .csv.gz)

# ✅ Correct: Include extension in path
.option("compression", "gzip")
.save("output/data.csv.gz")  # Creates data.csv.gz

# Or let rand_engine handle it:
.option("compression", "gzip")
.save("output/data")  # Creates data.csv.gz automatically
```

#### Issue 5: Parquet Compression Not Recognized

**Problem:** Parquet file not compressed

**Cause:** Invalid codec name

**Solution:**
```python
# ✅ Valid codecs
"snappy", "gzip", "zstd", "lz4", "brotli", None

# ❌ Invalid
"zip", "bz2", "xz"  # These are CSV/JSON codecs only
```

### Debugging Tips

**1. Check File Creation:**
```python
import os
from glob import glob

# List files in output directory
files = glob("output/**/*", recursive=True)
print(f"Created {len(files)} files:")
for f in files:
    size = os.path.getsize(f) / 1024  # KB
    print(f"  {f}: {size:.2f} KB")
```

**2. Verify Compression:**
```python
import os

# Check file size with/without compression
DataGenerator(spec).write.size(10000).save("output/data.csv")
uncompressed_size = os.path.getsize("output/data.csv")

DataGenerator(spec).write.size(10000).option("compression", "gzip").save("output/data.csv.gz")
compressed_size = os.path.getsize("output/data.csv.gz")

ratio = uncompressed_size / compressed_size
print(f"Compression ratio: {ratio:.2f}x")
```

**3. Test Streaming Timing:**
```python
import time

start = time.time()
DataGenerator(spec).writeStream \
    .size(100) \
    .option("timeout", 5) \
    .trigger(frequency=1) \
    .start("output/test")
elapsed = time.time() - start

print(f"Elapsed: {elapsed:.2f}s (expected ~5s)")
files = len(glob("output/test/part-*.json"))
print(f"Files created: {files} (expected ~5)")
```

---

## Related Documentation

- **[API Reference](./API_REFERENCE.md)** - Complete API documentation
- **[Examples](../EXAMPLES.md)** - Comprehensive examples gallery
- **[Constraints Guide](./CONSTRAINTS.md)** - Primary/Foreign key relationships
- **[Logging Guide](./LOGGING.md)** - Logging configuration

---

**Questions or Issues?** Check the [main README](../README.md) or open an issue on GitHub.
