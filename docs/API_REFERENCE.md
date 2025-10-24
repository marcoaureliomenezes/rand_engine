# API Reference

Complete reference documentation for all public APIs in `rand-engine` v0.6.1.

---

## Table of Contents

- [Core Classes](#core-classes)
  - [DataGenerator](#datagenerator)
  - [RandSpecs](#randspecs)
- [Generation Methods](#generation-methods)
  - [Numeric Methods](#numeric-methods)
  - [Identifier Methods](#identifier-methods)
  - [Selection Methods](#selection-methods)
  - [Temporal Methods](#temporal-methods)
  - [Advanced Methods](#advanced-methods)
- [Constraints & Referential Integrity](#constraints--referential-integrity) ⭐ **NEW**
  - [Constraint Types](#constraint-types)
  - [Checkpoint Management](#checkpoint-management)
  - [Watermarks](#watermarks)
- [File Writers](#file-writers)
  - [Batch Writer](#batch-writer)
  - [Stream Writer](#stream-writer)
- [Database Handlers](#database-handlers)
  - [DuckDB Handler](#duckdb-handler)
  - [SQLite Handler](#sqlite-handler)
- [Validation](#validation)
- [Logging](#logging)

---

## Core Classes

### DataGenerator

Main class for data generation orchestration.

#### Constructor

```python
DataGenerator(
    spec: Dict[str, Any],
    seed: Optional[Union[int, bool]] = None,
    validate: bool = False
)
```

**Parameters:**

- `spec` (dict): Specification dictionary defining columns and generation methods
- `seed` (int | bool, optional): Random seed for reproducibility. If `True`, uses default seed
- `validate` (bool): Enable spec validation with helpful error messages. Default: `False`

**Returns:** `DataGenerator` instance

**Example:**

```python
from rand_engine import DataGenerator

spec = {
    "id": {"method": "unique_ids", "kwargs": {"strategy": "zint"}},
    "value": {"method": "floats", "kwargs": {"min": 0.0, "max": 100.0}}
}

generator = DataGenerator(spec, seed=42, validate=True)
```

---

#### Methods

##### `size(n: int) -> DataGenerator`

Set the number of rows to generate.

**Parameters:**
- `n` (int): Number of rows

**Returns:** Self (for method chaining)

**Example:**

```python
generator.size(1000)
```

---

##### `checkpoint(database: str) -> DataGenerator` ⭐ **NEW**

Set checkpoint database for constraints (PK/FK).

**Parameters:**
- `database` (str): Database path or `":memory:"` for in-memory database

**Returns:** Self (for method chaining)

**Notes:**
- Required when using constraints in spec
- Use same database path across related specs for referential integrity
- `:memory:` creates temporary in-memory database (useful for testing)
- File paths create persistent DuckDB databases

**Example:**

```python
# In-memory database (testing)
generator.checkpoint(":memory:")

# Persistent database (production)
generator.checkpoint("data/checkpoints.duckdb")

# Same checkpoint across multiple generators
db_path = "shared.duckdb"
gen_categories = DataGenerator(spec_cat).checkpoint(db_path).size(10).get_df()
gen_products = DataGenerator(spec_prod).checkpoint(db_path).size(100).get_df()
```

---

##### `get_df() -> pd.DataFrame`

Generate and return a pandas DataFrame.

**Returns:** `pd.DataFrame`

**Example:**

```python
df = generator.size(1000).get_df()
```

---

##### `get_dict() -> Dict[str, Any]`

Generate a single record as a dictionary.

**Returns:** `Dict[str, Any]`

**Example:**

```python
record = generator.get_dict()
# {"id": "00000001", "value": 42.5}
```

---

##### `transformers(funcs: List[Callable]) -> DataGenerator`

Apply DataFrame-level transformations after generation.

**Parameters:**
- `funcs` (list): List of functions that take a DataFrame and return a DataFrame

**Returns:** Self (for method chaining)

**Example:**

```python
def add_year(df):
    df['year'] = 2024
    return df

def uppercase_names(df):
    df['name'] = df['name'].str.upper()
    return df

df = generator.transformers([add_year, uppercase_names]).size(100).get_df()
```

---

##### `stream_dict(min_throughput: int = 1, max_throughput: int = 10) -> Generator`

Generate continuous stream of records as dictionaries.

**Parameters:**
- `min_throughput` (int): Minimum records per second. Default: 1
- `max_throughput` (int): Maximum records per second. Default: 10

**Returns:** Generator yielding dictionaries

**Notes:**
- Each record automatically includes `timestamp_created` field
- Actual throughput varies randomly between min and max
- Runs indefinitely until stopped

**Example:**

```python
stream = generator.stream_dict(min_throughput=5, max_throughput=15)

for record in stream:
    print(record)
    # Send to Kafka, API, etc.
```

---

##### `write -> BatchWriter`

Access batch file writer interface.

**Returns:** `BatchWriter` instance

**Example:**

```python
generator.write.size(1000).format("parquet").save("output.parquet")
```

---

##### `writeStream -> StreamWriter`

Access streaming file writer interface.

**Returns:** `StreamWriter` instance

**Example:**

```python
generator.writeStream \
    .throughput(min=10, max=50) \
    .format("json") \
    .save("stream/")
```

---

### RandSpecs

Static class providing pre-built specification templates.

All methods are `@classmethod` - no instantiation required.

#### Methods

##### `customers() -> Dict[str, Any]`

Customer profile specification.

**Fields:**
- `customer_id`: Unique customer identifier (e.g., "C00000001")
- `name`: Customer name
- `age`: Age (18-70)
- `email`: Email address
- `is_active`: Active status (boolean)
- `account_balance`: Account balance (0-50000)

**Example:**

```python
from rand_engine import DataGenerator, RandSpecs

df = DataGenerator(RandSpecs.customers()).size(1000).get_df()
```

---

##### `products() -> Dict[str, Any]`

Product catalog specification.

**Fields:**
- `sku`: Stock Keeping Unit (e.g., "SKU000001")
- `product_name`: Product name
- `category`: Product category (weighted distribution)
- `price`: Product price (9.99-999.99)
- `stock`: Stock quantity (0-1000)
- `rating`: Product rating (1.0-5.0)

---

##### `orders() -> Dict[str, Any]`

E-commerce order specification with correlated fields.

**Fields:**
- `order_id`: Unique order identifier (e.g., "ORD0000001")
- `order_date`: Order timestamp
- `amount`: Order amount (10.0-5000.0)
- `status`: Order status (weighted: pending, shipped, delivered, cancelled)
- `payment_method`: Payment method
- `currency`: Currency code (USD, EUR, GBP) - correlated with country
- `country`: Country code (US, DE, GB) - correlated with currency

**Note:** Uses `distincts_map` for currency-country correlation

---

##### `transactions() -> Dict[str, Any]`

Financial transaction specification.

**Fields:**
- `transaction_id`: Unique transaction ID
- `timestamp`: Transaction timestamp
- `amount`: Transaction amount (1.0-10000.0)
- `type`: Transaction type (deposit, withdrawal, transfer, payment)
- `currency`: Currency code
- `description`: Transaction description

---

##### `employees() -> Dict[str, Any]`

Employee record specification with hierarchical splits.

**Fields:**
- `employee_id`: Unique employee ID (e.g., "EMP000001")
- `hire_date`: Hire date timestamp
- `salary`: Annual salary (30000-150000)
- `department`: Department name - split from combined field
- `level`: Job level (junior, mid, senior) - split from combined field
- `role`: Job role - split from combined field
- `is_remote`: Remote work status
- `bonus`: Annual bonus (0-20000)

**Note:** Uses `distincts_multi_map` for department-level-role correlation

---

##### `devices() -> Dict[str, Any]`

IoT device telemetry specification.

**Fields:**
- `device_id`: Unique device identifier (e.g., "DEV000001")
- `device_type`: Device type (sensor, camera, controller, gateway)
- `status`: Device status - split from combined field
- `priority`: Alert priority - split from combined field
- `temperature`: Temperature reading (-20 to 60°C)
- `battery`: Battery level (0-100%)
- `last_ping`: Last communication timestamp

---

##### `users() -> Dict[str, Any]`

Application user specification with transformer example.

**Fields:**
- `user_id`: Unique user ID (e.g., "U00000001")
- `username`: Username
- `plan`: Subscription plan (FREE, STANDARD, PREMIUM) - **uppercase transformer**
- `signup_date`: Signup timestamp
- `login_count`: Number of logins (0-1000)
- `is_verified`: Email verification status

**Note:** Demonstrates column-level transformers (uppercase)

---

##### `invoices() -> Dict[str, Any]`

Invoice record specification.

**Fields:**
- `invoice_number`: Unique invoice number (e.g., "INV000001")
- `issue_date`: Issue date timestamp
- `due_date`: Due date timestamp
- `amount`: Invoice amount (100-10000)
- `status`: Payment status (pending, paid, overdue, cancelled)
- `tax_rate`: Tax rate percentage (0-25%)

---

##### `shipments() -> Dict[str, Any]`

Shipping record specification with carrier-destination correlation.

**Fields:**
- `tracking_number`: Unique tracking number (e.g., "TRK000001")
- `carrier`: Shipping carrier - split from combined field
- `destination`: Destination country - split from combined field
- `weight`: Package weight (0.1-50.0 kg)
- `status`: Shipment status (processing, in_transit, delivered, returned)
- `ship_date`: Ship date timestamp
- `estimated_delivery`: Estimated delivery timestamp

---

##### `events() -> Dict[str, Any]`

Event log specification.

**Fields:**
- `event_id`: Unique event ID (e.g., "EVT000001")
- `timestamp`: Event timestamp
- `event_type`: Event type (info, warning, error, critical)
- `severity`: Severity level (1-5)
- `source`: Event source
- `message`: Event message

---

## Generation Methods

All generation methods are specified in the `spec` dictionary format:

```python
{
    "column_name": {
        "method": "method_name",
        "kwargs": {
            "param1": value1,
            "param2": value2
        }
    }
}
```

### Numeric Methods

#### `integers`

Generate random integers within a range.

**Parameters:**
- `min` (int, required): Minimum value (inclusive)
- `max` (int, required): Maximum value (inclusive)

**Example:**

```python
{
    "age": {
        "method": "integers",
        "kwargs": {"min": 18, "max": 65}
    }
}
```

---

#### `floats`

Generate random floating-point numbers.

**Parameters:**
- `min` (float, required): Minimum value
- `max` (float, required): Maximum value
- `round` (int, optional): Decimal places. Default: 2

**Example:**

```python
{
    "price": {
        "method": "floats",
        "kwargs": {"min": 9.99, "max": 999.99, "round": 2}
    }
}
```

---

#### `floats_normal`

Generate floats from normal (Gaussian) distribution.

**Parameters:**
- `mean` (float, required): Distribution mean
- `std` (float, required): Standard deviation
- `round` (int, optional): Decimal places. Default: 2

**Example:**

```python
{
    "height_cm": {
        "method": "floats_normal",
        "kwargs": {"mean": 170.0, "std": 10.0, "round": 1}
    }
}
```

---

#### `booleans`

Generate boolean values with probability control.

**Parameters:**
- `true_prob` (float, optional): Probability of True (0.0-1.0). Default: 0.5

**Example:**

```python
{
    "is_active": {
        "method": "booleans",
        "kwargs": {"true_prob": 0.8}  # 80% True
    }
}
```

---

### Identifier Methods

#### `unique_ids`

Generate unique identifiers.

**Parameters:**
- `strategy` (str, required): ID generation strategy
  - `"zint"`: Zero-padded integers (e.g., "00000001")
  - `"uuid4"`: UUID4 strings
  - `"numeric"`: Sequential numbers
- `length` (int, optional): Length for zint strategy. Default: 8
- `prefix` (str, optional): Prefix for IDs. Default: ""

**Examples:**

```python
# Zero-padded integers with prefix
{
    "customer_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint", "prefix": "CUST", "length": 10}
    }
}
# Output: CUST0000000001, CUST0000000002, ...

# UUID4
{
    "session_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "uuid4"}
    }
}
# Output: "a3f8b2c1-...", "7d9e4f21-...", ...
```

---

### Selection Methods

#### `distincts`

Random selection from a list of values (uniform distribution).

**Parameters:**
- `distincts` (list, required): List of values to choose from

**Example:**

```python
{
    "status": {
        "method": "distincts",
        "kwargs": {
            "distincts": ["pending", "active", "completed", "cancelled"]
        }
    }
}
```

---

#### `distincts_prop`

Weighted random selection from values.

**Parameters:**
- `distincts` (dict, required): Dictionary with values as keys and weights as values

**Example:**

```python
{
    "product_category": {
        "method": "distincts_prop",
        "kwargs": {
            "distincts": {
                "Electronics": 40,  # 40% of records
                "Clothing": 30,     # 30%
                "Food": 20,         # 20%
                "Books": 10         # 10%
            }
        }
    }
}
```

**Note:** Weights don't need to sum to 100 - they're relative proportions

---

#### `distincts_map`

Generate two correlated columns (1:N mapping).

**Parameters:**
- `distincts` (dict, required): Mapping of key → list of values
- `cols` (list, required): Two-element list of column names `[key_col, value_col]`

**Example:**

```python
{
    "device_os": {
        "method": "distincts_map",
        "cols": ["device_type", "os"],
        "kwargs": {
            "distincts": {
                "smartphone": ["Android", "iOS"],
                "desktop": ["Windows", "macOS", "Linux"],
                "tablet": ["Android", "iOS", "Windows"]
            }
        }
    }
}
# Result: 2 columns (device_type, os) with valid combinations
```

---

#### `distincts_map_prop`

Correlated columns with weighted values.

**Parameters:**
- `distincts` (dict, required): Mapping of key → list of (value, weight) tuples
- `cols` (list, required): Two-element list of column names

**Example:**

```python
{
    "product_status": {
        "method": "distincts_map_prop",
        "cols": ["product_type", "status"],
        "kwargs": {
            "distincts": {
                "laptop": [
                    ("new", 90),        # 90% of laptops are new
                    ("refurbished", 10) # 10% refurbished
                ],
                "phone": [
                    ("new", 70),
                    ("refurbished", 25),
                    ("used", 5)
                ]
            }
        }
    }
}
```

---

#### `distincts_multi_map`

Generate N correlated columns (Cartesian product with weights).

**Parameters:**
- `distincts` (dict, required): Complex nested structure for N-way correlations
- `cols` (list, required): List of N column names

**Example:**

```python
{
    "company_info": {
        "method": "distincts_multi_map",
        "cols": ["sector", "sub_sector", "size", "region"],
        "kwargs": {
            "distincts": {
                "tech": [
                    ["software", "hardware"],  # sub_sectors
                    [0.6, 0.3, 0.1],          # size weights (large, medium, small)
                    ["north_america", "europe", "asia"],
                    ["usa", "canada"]          # regions for north_america
                ],
                "finance": [
                    ["banking", "insurance"],
                    [0.5, 0.4, 0.1],
                    ["north_america", "europe"],
                    ["usa", "uk", "germany"]
                ]
            }
        }
    }
}
```

**Note:** Most complex method - see `employees()` spec for real example

---

### Temporal Methods

#### `unix_timestamps`

Generate Unix timestamps within a date range.

**Parameters:**
- `start` (str, required): Start date
- `end` (str, required): End date
- `format` (str, optional): Date format string. Default: `"%d-%m-%Y"`

**Example:**

```python
{
    "created_at": {
        "method": "unix_timestamps",
        "kwargs": {
            "start": "01-01-2024",
            "end": "31-12-2024",
            "format": "%d-%m-%Y"
        }
    }
}
# Output: 1704067200, 1704153600, ... (Unix timestamps)
```

**Common Format Codes:**
- `%d`: Day (01-31)
- `%m`: Month (01-12)
- `%Y`: Year (4 digits)
- `%H`: Hour (00-23)
- `%M`: Minute (00-59)
- `%S`: Second (00-59)

---

### Advanced Methods

#### `complex_distincts`

Generate complex patterns by template replacement.

**Parameters:**
- `pattern` (str, required): Template pattern with placeholders
- `replacement` (str, required): Placeholder character to replace
- `templates` (list, required): List of generation specs for each placeholder

**Example - IP Addresses:**

```python
{
    "ip_address": {
        "method": "complex_distincts",
        "kwargs": {
            "pattern": "x.x.x.x",
            "replacement": "x",
            "templates": [
                {
                    "method": "distincts",
                    "kwargs": {"distincts": ["192", "10", "172"]}
                },
                {
                    "method": "integers",
                    "kwargs": {"min": 0, "max": 255}
                },
                {
                    "method": "integers",
                    "kwargs": {"min": 0, "max": 255}
                },
                {
                    "method": "integers",
                    "kwargs": {"min": 1, "max": 254}
                }
            ]
        }
    }
}
# Output: "192.168.1.45", "10.0.52.231", ...
```

**Example - URLs:**

```python
{
    "url": {
        "method": "complex_distincts",
        "kwargs": {
            "pattern": "https://x.example.com/x",
            "replacement": "x",
            "templates": [
                {"method": "distincts", "kwargs": {"distincts": ["api", "web", "cdn"]}},
                {"method": "distincts", "kwargs": {"distincts": ["users", "products", "orders"]}}
            ]
        }
    }
}
# Output: "https://api.example.com/users", "https://web.example.com/products", ...
```

---

## Constraints & Referential Integrity

⭐ **NEW in v0.6.1** - Create realistic datasets with proper Primary Key/Foreign Key relationships.

### Constraint Types

#### Primary Key (PK)

Creates a checkpoint table with generated records for reference by other specs.

**Structure:**

```python
"constraints": {
    "constraint_name": {
        "name": "checkpoint_table_name",
        "tipo": "PK",
        "fields": ["field1 TYPE1", "field2 TYPE2", ...]
    }
}
```

**Parameters:**
- `name` (str): Checkpoint table name (must be unique)
- `tipo` (str): Must be `"PK"`
- `fields` (list): Column names with SQL types (e.g., `"user_id VARCHAR(10)"`)

**Example:**

```python
spec_users = {
    "user_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 8}},
    "username": {"method": "distincts", "kwargs": {"distincts": ["alice", "bob", "charlie"]}},
    "constraints": {
        "users_pk": {
            "name": "users_pk",
            "tipo": "PK",
            "fields": ["user_id VARCHAR(8)"]
        }
    }
}

# Creates checkpoint_users_pk table in database
df = DataGenerator(spec_users).checkpoint("data.duckdb").size(100).get_df()
```

---

#### Foreign Key (FK)

References values from a PK checkpoint table, ensuring referential integrity.

**Structure:**

```python
"constraints": {
    "constraint_name": {
        "name": "referenced_pk_table_name",
        "tipo": "FK",
        "fields": ["field1", "field2", ...],
        "watermark": 60  # Optional: seconds
    }
}
```

**Parameters:**
- `name` (str): Name of referenced PK checkpoint table
- `tipo` (str): Must be `"FK"`
- `fields` (list): Column names (without types)
- `watermark` (int, optional): Temporal window in seconds. Default: None (all records)

**Example:**

```python
spec_posts = {
    "post_id": {"method": "unique_ids", "kwargs": {"strategy": "uuid4"}},
    "title": {"method": "distincts", "kwargs": {"distincts": ["Post A", "Post B"]}},
    "constraints": {
        "user_fk": {
            "name": "users_pk",
            "tipo": "FK",
            "fields": ["user_id"],
            "watermark": 3600  # Reference users created in last hour
        }
    }
}

# References checkpoint_users_pk table
df = DataGenerator(spec_posts).checkpoint("data.duckdb").size(1000).get_df()

# Verify integrity
assert set(df['user_id']).issubset(set(df_users['user_id']))  # True
```

---

### Composite Keys

Multi-column primary and foreign keys.

**Primary Key Example:**

```python
spec_clients = {
    "client_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 8}},
    "client_type": {"method": "distincts", "kwargs": {"distincts": ["PF", "PJ"]}},
    "name": {"method": "distincts", "kwargs": {"distincts": ["Client A", "Client B"]}},
    "constraints": {
        "clients_pk": {
            "name": "clients_pk",
            "tipo": "PK",
            "fields": ["client_id VARCHAR(8)", "client_type VARCHAR(2)"]
        }
    }
}

df_clients = DataGenerator(spec_clients).checkpoint("data.duckdb").size(100).get_df()
```

**Foreign Key Example:**

```python
spec_transactions = {
    "transaction_id": {"method": "unique_ids", "kwargs": {"strategy": "uuid4"}},
    "amount": {"method": "floats", "kwargs": {"min": 10.0, "max": 5000.0, "round": 2}},
    "constraints": {
        "client_fk": {
            "name": "clients_pk",
            "tipo": "FK",
            "fields": ["client_id", "client_type"],
            "watermark": 3600
        }
    }
}

df_transactions = DataGenerator(spec_transactions).checkpoint("data.duckdb").size(5000).get_df()

# Verify composite key integrity
client_keys = set(zip(df_clients['client_id'], df_clients['client_type']))
transaction_keys = set(zip(df_transactions['client_id'], df_transactions['client_type']))
assert transaction_keys.issubset(client_keys)  # True
```

---

### Checkpoint Management

#### Database Types

- **In-Memory** (`:memory:`): Temporary, lost after program ends. Fast, ideal for testing.
- **Persistent** (file path): Saved to disk, reusable across runs. Required for production.

**Example:**

```python
# Testing: in-memory
gen = DataGenerator(spec).checkpoint(":memory:")

# Production: persistent file
gen = DataGenerator(spec).checkpoint("checkpoints/production.duckdb")
```

---

#### Shared Checkpoints

Use the same database path across multiple generators for referential integrity:

```python
db_path = "ecommerce.duckdb"

# Level 1: Categories
df_cat = DataGenerator(spec_categories).checkpoint(db_path).size(10).get_df()

# Level 2: Products (references categories)
df_prod = DataGenerator(spec_products).checkpoint(db_path).size(100).get_df()

# Level 3: Orders (references products)
df_orders = DataGenerator(spec_orders).checkpoint(db_path).size(1000).get_df()

# Result: 3-level referential integrity
```

---

### Watermarks

**Purpose:** Limit FK references to recent records (temporal window).

**When to Use:**
- Streaming data scenarios
- Time-based relationships (e.g., orders reference recent products)
- Large datasets where you don't want to load entire PK table

**How It Works:**

1. PK records include `created_at` timestamp
2. FK queries: `WHERE created_at >= (NOW() - watermark_seconds)`
3. Only recent records are referenced

**Example:**

```python
# Products PK created at 10:00:00
spec_products = {
    "product_id": {"method": "unique_ids", "kwargs": {"strategy": "zint"}},
    "constraints": {
        "product_pk": {"tipo": "PK", "fields": ["product_id VARCHAR(8)"]}
    }
}
df_prod = DataGenerator(spec_products).checkpoint("data.db").size(100).get_df()
# Checkpoint has products with created_at = 10:00:00

# Orders FK with 60-second watermark (generated at 10:01:30)
spec_orders = {
    "order_id": {"method": "unique_ids", "kwargs": {"strategy": "uuid4"}},
    "constraints": {
        "product_fk": {
            "tipo": "FK",
            "fields": ["product_id"],
            "watermark": 60  # Only products created after 10:00:30
        }
    }
}
df_orders = DataGenerator(spec_orders).checkpoint("data.db").size(1000).get_df()
# Orders only reference products from last 60 seconds
```

**Best Practices:**
- **Short-lived data:** 60-300 seconds
- **Medium-lived:** 600-3600 seconds
- **Long-lived:** 3600+ seconds or no watermark
- **Testing:** No watermark (reference all records)

---

### Complete Example - E-commerce (3 Levels)

```python
from rand_engine import DataGenerator

db = "ecommerce.duckdb"

# Level 1: Categories (PK)
spec_categories = {
    "category_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 4}},
    "name": {"method": "distincts", "kwargs": {"distincts": ["Electronics", "Books"]}},
    "constraints": {
        "category_pk": {"name": "category_pk", "tipo": "PK", "fields": ["category_id VARCHAR(4)"]}
    }
}
df_cat = DataGenerator(spec_categories).checkpoint(db).size(10).get_df()

# Level 2: Products (PK + FK → categories)
spec_products = {
    "product_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 8}},
    "name": {"method": "distincts", "kwargs": {"distincts": [f"Product {i}" for i in range(100)]}},
    "price": {"method": "floats", "kwargs": {"min": 10.0, "max": 1000.0, "round": 2}},
    "constraints": {
        "product_pk": {"name": "product_pk", "tipo": "PK", "fields": ["product_id VARCHAR(8)"]},
        "category_fk": {"name": "category_pk", "tipo": "FK", "fields": ["category_id"], "watermark": 60}
    }
}
df_prod = DataGenerator(spec_products).checkpoint(db).size(100).get_df()

# Level 3: Orders (FK → products)
spec_orders = {
    "order_id": {"method": "unique_ids", "kwargs": {"strategy": "uuid4"}},
    "quantity": {"method": "integers", "kwargs": {"min": 1, "max": 10}},
    "total": {"method": "floats", "kwargs": {"min": 10.0, "max": 5000.0, "round": 2}},
    "constraints": {
        "product_fk": {"name": "product_pk", "tipo": "FK", "fields": ["product_id"], "watermark": 120}
    }
}
df_orders = DataGenerator(spec_orders).checkpoint(db).size(1000).get_df()

# Verify 3-level integrity
print(f"Categories → Products: {set(df_prod['category_id']).issubset(set(df_cat['category_id']))}")
print(f"Products → Orders: {set(df_orders['product_id']).issubset(set(df_prod['product_id']))}")
# Both: True ✅
```

📖 **Complete guide with more examples:** [CONSTRAINTS.md](./CONSTRAINTS.md)

---

## File Writers

### Batch Writer

Write generated data to files in batch mode.

#### Methods

##### `size(n: int) -> BatchWriter`

Set number of rows to generate.

**Parameters:**
- `n` (int): Number of rows

---

##### `format(fmt: str) -> BatchWriter`

Set output format.

**Parameters:**
- `fmt` (str): Format name. Options: `"csv"`, `"json"`, `"parquet"`

---

##### `option(key: str, value: Any) -> BatchWriter`

Set format-specific options.

**Parameters:**
- `key` (str): Option name
- `value`: Option value

**Common Options:**

**CSV:**
- `compression`: `"gzip"`, `"zip"`, `"bz2"`, `None`
- `sep`: Column separator. Default: `","`
- `index`: Include index. Default: `False`

**JSON:**
- `compression`: `"gzip"`, `"zip"`, `"bz2"`, `None`
- `orient`: JSON structure. Default: `"records"`
- `indent`: Pretty print indentation

**Parquet:**
- `compression`: `"snappy"`, `"gzip"`, `"brotli"`, `None`
- `engine`: `"pyarrow"` or `"fastparquet"`. Default: `"fastparquet"`

---

##### `num_files(n: int) -> BatchWriter`

Split output into multiple files.

**Parameters:**
- `n` (int): Number of files

---

##### `save(path: str) -> None`

Write data to file(s).

**Parameters:**
- `path` (str): Output path (file or directory)

---

#### Examples

```python
from rand_engine import DataGenerator, RandSpecs

generator = DataGenerator(RandSpecs.customers())

# Single CSV with gzip
generator.write \
    .size(10000) \
    .format("csv") \
    .option("compression", "gzip") \
    .save("customers.csv.gz")

# Parquet with snappy
generator.write \
    .size(1000000) \
    .format("parquet") \
    .option("compression", "snappy") \
    .save("customers.parquet")

# Multiple JSON files
generator.write \
    .size(100000) \
    .num_files(10) \
    .format("json") \
    .save("customers/")
```

---

### Stream Writer

Write generated data in streaming mode.

#### Methods

##### `throughput(min: int, max: int) -> StreamWriter`

Set throughput range (records/second).

**Parameters:**
- `min` (int): Minimum throughput
- `max` (int): Maximum throughput

---

##### `format(fmt: str) -> StreamWriter`

Set output format (same as BatchWriter).

---

##### `option(key: str, value: Any) -> StreamWriter`

Set format options (same as BatchWriter).

---

##### `save(path: str) -> None`

Start streaming to directory.

**Parameters:**
- `path` (str): Output directory path

---

#### Example

```python
from rand_engine import DataGenerator, RandSpecs

# Stream events to JSON files
DataGenerator(RandSpecs.events()).writeStream \
    .throughput(min=10, max=50) \
    .format("json") \
    .option("indent", 2) \
    .save("stream/events/")
```

---

## Database Handlers

### DuckDB Handler

Interface for DuckDB database operations (used internally by constraints).

#### Constructor

```python
from rand_engine.integrations._duckdb_handler import DuckDBHandler

db = DuckDBHandler(database: str = ":memory:")
```

**Parameters:**
- `database` (str): Database path or `":memory:"` for in-memory. Default: `":memory:"`

---

#### Methods

##### `create_table(table_name: str, schema: str) -> None`

Create a table.

**Parameters:**
- `table_name` (str): Table name
- `schema` (str): SQL column definitions

**Example:**

```python
db.create_table("users", "user_id VARCHAR(10) PRIMARY KEY, name VARCHAR(100)")
```

---

##### `insert_df(table_name: str, df: pd.DataFrame, pk_cols: List[str] = None) -> None`

Insert DataFrame into table.

**Parameters:**
- `table_name` (str): Table name
- `df` (pd.DataFrame): Data to insert
- `pk_cols` (list, optional): Primary key columns for conflict handling

**Example:**

```python
df = DataGenerator(RandSpecs.customers()).size(10000).get_df()
db.insert_df("customers", df, pk_cols=["customer_id"])
```

---

##### `select_all(table_name: str, columns: List[str] = None) -> pd.DataFrame`

Query table and return DataFrame.

**Parameters:**
- `table_name` (str): Table name
- `columns` (list, optional): Columns to select. Default: all

**Returns:** `pd.DataFrame`

**Example:**

```python
result = db.select_all("customers", columns=["customer_id", "name", "age"])
```

---

##### `close() -> None`

Close database connection.

**Example:**

```python
db.close()
```

---

#### Complete Example

```python
from rand_engine import DataGenerator, RandSpecs
from rand_engine.integrations._duckdb_handler import DuckDBHandler

# Create database
db = DuckDBHandler("analytics.duckdb")

# Create table
db.create_table("customers", "customer_id VARCHAR(10) PRIMARY KEY")

# Generate and insert data
df = DataGenerator(RandSpecs.customers()).size(10000).get_df()
db.insert_df("customers", df, pk_cols=["customer_id"])

# Query
result = db.select_all("customers")
print(f"Inserted {len(result)} customers")

# Cleanup
db.close()
```

---

### SQLite Handler

Interface for SQLite database operations (same API as DuckDB).

#### Constructor

```python
from rand_engine.integrations._sqlite_handler import SQLiteHandler

db = SQLiteHandler(database: str)
```

**Parameters:**
- `database` (str): Database file path (e.g., `"test.db"`)

---

#### Methods

Same methods as DuckDBHandler:
- `create_table()`
- `insert_df()`
- `select_all()`
- `close()`

#### Example

```python
from rand_engine.integrations._sqlite_handler import SQLiteHandler

db = SQLiteHandler("test.db")
db.create_table("orders", "order_id VARCHAR(10) PRIMARY KEY")

df = DataGenerator(RandSpecs.orders()).size(1000).get_df()
db.insert_df("orders", df, pk_cols=["order_id"])

db.close()
```

---

## Validation

### Spec Validation

Enable validation to get helpful error messages.

#### Usage

```python
from rand_engine import DataGenerator

spec = {
    "age": {
        "method": "integers"  # Missing required params
    }
}

try:
    generator = DataGenerator(spec, validate=True)
except Exception as e:
    print(e)
```

#### Error Message Example

```
❌ Column 'age': Missing required parameter 'min'

Correct example:
{
    "age": {
        "method": "integers",
        "kwargs": {"min": 18, "max": 65}
    }
}

Available methods: integers, floats, floats_normal, booleans,
distincts, distincts_prop, distincts_map, distincts_map_prop,
distincts_multi_map, complex_distincts, unix_timestamps, unique_ids
```

---

### Constraint Validation ⭐ **NEW**

Validates constraints structure automatically when `validate=True`.

**Validates:**
- Required fields: `name`, `tipo`, `fields`
- `tipo` must be `"PK"` or `"FK"`
- `fields` must be non-empty list
- PK fields must include SQL types (e.g., `"id VARCHAR(8)"`)
- FK fields must not include types
- `watermark` must be positive number (FK only)

**Example:**

```python
invalid_spec = {
    "user_id": {"method": "unique_ids", "kwargs": {"strategy": "zint"}},
    "constraints": {
        "users_pk": {
            "tipo": "PK",  # Missing 'name'
            "fields": []    # Empty fields
        }
    }
}

try:
    gen = DataGenerator(invalid_spec, validate=True)
except Exception as e:
    print(e)
    # ❌ Constraint 'users_pk': Missing required field 'name'
    # ❌ Constraint 'users_pk': 'fields' cannot be empty
```

---

## Logging

### Enable Logging

Configure logging to see internal operations (constraints, database handlers).

```python
import logging
from rand_engine.utils.logger import RandEngineLogger

# Enable INFO level logging
RandEngineLogger.setup_logging(level=logging.INFO)

# Now operations will log messages
from rand_engine import DataGenerator
spec = {...}
gen = DataGenerator(spec).checkpoint("data.duckdb")
# Output: [INFO] rand_engine.integrations._duckdb_handler - Created new connection to DuckDB database: data.duckdb

df = gen.size(1000).get_df()
# Output: [INFO] rand_engine.integrations._duckdb_handler - Inserted 1000 rows into checkpoint_table_name
```

### Disable Logging

```python
from rand_engine.utils.logger import RandEngineLogger

RandEngineLogger.disable_logging()
```

### Logged Operations

**DuckDB/SQLite Handlers:**
- Connection creation/reuse
- Table creation
- Data insertion
- Query execution
- Connection closure

📖 **Complete logging guide:** [LOGGING.md](./LOGGING.md)

---

## Type Hints

All public APIs include comprehensive type hints:

```python
from typing import Dict, Any, Optional, Union, List, Callable, Generator
import pandas as pd
import logging

def DataGenerator(
    spec: Dict[str, Any],
    seed: Optional[Union[int, bool]] = None,
    validate: bool = False
) -> DataGenerator: ...

def checkpoint(self, database: str) -> DataGenerator: ...
def size(self, n: int) -> DataGenerator: ...
def get_df(self) -> pd.DataFrame: ...
def get_dict(self) -> Dict[str, Any]: ...
def transformers(self, funcs: List[Callable[[pd.DataFrame], pd.DataFrame]]) -> DataGenerator: ...
def stream_dict(self, min_throughput: int = 1, max_throughput: int = 10) -> Generator[Dict[str, Any], None, None]: ...
```

---

## Version Information

**Current Version:** 0.6.1

**Python Compatibility:** >= 3.10

**Core Dependencies:**
- `numpy ^2.1.1`
- `pandas ^2.2.2`

**Optional Dependencies:**
- `faker ^28.4.1` (for realistic names/addresses in tests)
- `duckdb ^1.1.0` (for constraints with DuckDB)

---

## Additional Resources

- **[README.md](../README.md)** - Getting started guide with quickstart examples
- **[EXAMPLES.md](../EXAMPLES.md)** - 50+ comprehensive examples (1,600+ lines)
- **[CONSTRAINTS.md](./CONSTRAINTS.md)** - Complete guide to PK/FK system (900+ lines)
- **[LOGGING.md](./LOGGING.md)** - Logging configuration guide (450+ lines)
- **[CHANGELOG.md](../CHANGELOG.md)** - Version history and release notes
- **[GitHub Issues](https://github.com/marcoaureliomenezes/rand_engine/issues)** - Bug reports and feature requests
- **[GitHub Discussions](https://github.com/marcoaureliomenezes/rand_engine/discussions)** - Community Q&A

---

**Last Updated:** October 21, 2025 (v0.6.1)
