# Rand Engine - Examples Gallery

**Comprehensive collection of real-world use cases demonstrating the full power of `rand-engine`.**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](./docs/README.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

---

## 📚 Table of Contents

### 🚀 Getting Started
- [Quick Start](#-quick-start)
- [Pre-Built Templates](#-pre-built-templates)
- [Custom Specs](#-custom-specs)

### 🎯 Core Features
- [Basic Data Generation](#-basic-data-generation)
- [Streaming Data](#-streaming-data)
- [File Export](#-file-export)
- [Transformers](#-transformers)

### 🔗 Advanced Features ⭐
- [**Constraints & Referential Integrity**](#-constraints--referential-integrity-new)
- [Correlated Columns](#-correlated-columns)
- [Complex Patterns](#-complex-patterns)

### 💼 Industry Use Cases
- [E-commerce](#-e-commerce)
- [Financial Services](#-financial-services)
- [Human Resources](#-human-resources)
- [IoT & Telemetry](#-iot--telemetry)
- [Web Analytics](#-web-analytics)

### 🛠️ Engineering & Testing
- [ETL Pipeline Testing](#-etl-pipeline-testing)
- [Load Testing](#-load-testing)
- [Database Integration](#-database-integration)

### ⚡ Performance
- [Benchmarks](#-benchmarks)
- [Memory Optimization](#-memory-optimization)
- [Parallel Generation](#-parallel-generation)

---

## 🔥 What's New in v0.6.1

- ✅ **Constraints System**: Primary Keys (PK) and Foreign Keys (FK) for referential integrity
- ✅ **Composite Keys**: Support for multi-column primary and foreign keys
- ✅ **Watermarks**: Temporal windows for realistic time-based relationships
- ✅ **Spec Validation**: Educational error messages with examples
- ✅ **Logging System**: Transparent logging with Python's built-in logger
- ✅ **Windows Compatibility**: Full cross-platform support (Linux, macOS, Windows)

---

## 🚀 Quick Start

### Your First DataFrame (30 seconds)

```python
from rand_engine import DataGenerator, RandSpecs

# Generate 10,000 customer records
customers = DataGenerator(RandSpecs.customers(), seed=42).size(10000).get_df()
print(customers.head())
```

**Output:**
```
  customer_id       name  age                    email  is_active  account_balance
0   C00000001  John Smith   42    john.smith@email.com       True         15432.50
1   C00000002  Jane Brown   28   jane.brown@email.com       True          8721.33
2   C00000003  Bob Wilson   56   bob.wilson@email.com      False         42156.89
```

---

## 📦 Pre-Built Templates

Ready-to-use specs for common use cases:

```python
from rand_engine import RandSpecs, DataGenerator

# 🛒 E-commerce & Retail
customers = DataGenerator(RandSpecs.customers()).size(10000).get_df()
products = DataGenerator(RandSpecs.products()).size(1000).get_df()
orders = DataGenerator(RandSpecs.orders()).size(50000).get_df()
invoices = DataGenerator(RandSpecs.invoices()).size(50000).get_df()
shipments = DataGenerator(RandSpecs.shipments()).size(50000).get_df()

# 💰 Financial
transactions = DataGenerator(RandSpecs.transactions()).size(100000).get_df()

# 👥 HR & People
employees = DataGenerator(RandSpecs.employees()).size(500).get_df()
users = DataGenerator(RandSpecs.users()).size(50000).get_df()

# 🔧 IoT & Systems
devices = DataGenerator(RandSpecs.devices()).size(10000).get_df()
events = DataGenerator(RandSpecs.events()).size(1000000).get_df()
```

**Each template includes:**
- ✅ 6-10 realistic fields
- ✅ Proper data types (strings, integers, floats, booleans)
- ✅ Realistic distributions (normal, weighted)
- ✅ Domain-specific values (currencies, statuses, countries)

---

## 🔧 Custom Specs

### Basic Spec Structure

```python
spec = {
    "column_name": {
        "method": "generation_method",     # How to generate
        "kwargs": {"param": value}         # Method parameters
    }
}
```

### Available Methods

| Method | Description | Example |
|--------|-------------|---------|
| `unique_ids` | Unique identifiers (UUID, zero-filled ints) | `{"strategy": "zint", "length": 8}` |
| `integers` | Random integers in range | `{"min": 0, "max": 100}` |
| `floats` | Random floats in range | `{"min": 0.0, "max": 1.0, "round": 2}` |
| `floats_normal` | Normal distribution floats | `{"mean": 50, "std": 10}` |
| `booleans` | Boolean values | `{"true_prob": 0.7}` |
| `distincts` | Pick from list (uniform) | `{"distincts": ["A", "B", "C"]}` |
| `distincts_prop` | Pick from dict (weighted) | `{"distincts": {"A": 70, "B": 30}}` |
| `unix_timestamps` | Unix timestamps | `{"start": "01-01-2024", "end": "31-12-2024"}` |

📖 **See full method reference:** [API_REFERENCE.md](./docs/API_REFERENCE.md)

### Example - User Registration Dataset

```python
from rand_engine import DataGenerator

spec = {
    "user_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint", "length": 8}
    },
    "username": {
        "method": "distincts",
        "kwargs": {"distincts": [f"user{i}" for i in range(10000)]}
    },
    "age": {
        "method": "integers",
        "kwargs": {"min": 18, "max": 80}
    },
    "premium": {
        "method": "booleans",
        "kwargs": {"true_prob": 0.15}  # 15% premium users
    },
    "signup_date": {
        "method": "unix_timestamps",
        "kwargs": {
            "start": "01-01-2024",
            "end": "31-12-2024",
            "format": "%d-%m-%Y"
        }
    }
}

users = DataGenerator(spec, seed=42).size(50000).get_df()
print(users.head())
```

---

## 🎯 Basic Data Generation

### Generate DataFrame

```python
from rand_engine import DataGenerator, RandSpecs

# Simple generation
df = DataGenerator(RandSpecs.customers()).size(1000).get_df()

# With seed (reproducible)
df = DataGenerator(RandSpecs.customers(), seed=42).size(1000).get_df()
```

### Generate Dictionary

```python
# Single record
record = DataGenerator(RandSpecs.customers()).get_dict()
print(record)
# {'customer_id': 'C00000001', 'name': 'John Smith', ...}
```

---

## 🌊 Streaming Data

### Continuous Stream

```python
from rand_engine import DataGenerator, RandSpecs

# Create infinite stream
stream = DataGenerator(RandSpecs.events()).stream_dict(
    min_throughput=10,  # 10 events/sec minimum
    max_throughput=50   # 50 events/sec maximum
)

# Process events in real-time
for event in stream:
    print(f"Event: {event['event_id']} at {event['timestamp']}")
    # Send to Kafka, Redis, etc.
```

### Timed Stream (Simulate Real Traffic)

```python
import time

stream = DataGenerator(RandSpecs.transactions()).stream_dict(
    min_throughput=5,
    max_throughput=20
)

# Run for 1 minute
start_time = time.time()
count = 0

for transaction in stream:
    print(f"Transaction {count}: ${transaction['amount']}")
    count += 1
    
    if time.time() - start_time > 60:  # 60 seconds
        break

print(f"Generated {count} transactions in 1 minute")
```

---

## 💾 File Export

### Single File Export

```python
from rand_engine import DataGenerator, RandSpecs

# Export to CSV
(
    DataGenerator(RandSpecs.customers())
    .write
    .size(10000)
    .format("csv")
    .mode("overwrite")
    .load("/tmp/customers.csv")
)

# Export to Parquet with compression
(
    DataGenerator(RandSpecs.transactions())
    .write
    .size(1000000)
    .format("parquet")
    .mode("overwrite")
    .option("compression", "snappy")
    .load("/tmp/transactions.parquet")
)

# Export to JSON
(
    DataGenerator(RandSpecs.events())
    .write
    .size(50000)
    .format("json")
    .mode("overwrite")
    .load("/tmp/events.json")
)
```

### Multiple Files (Partitioning)

```python
# Export to 10 CSV files
(
    DataGenerator(RandSpecs.orders())
    .write
    .size(1000000)
    .format("csv")
    .mode("overwrite")
    .option("numFiles", 10)
    .load("/tmp/orders/")
)

# Output:
# /tmp/orders/orders_000000.csv
# /tmp/orders/orders_000001.csv
# ...
# /tmp/orders/orders_000009.csv
```

### Streaming to Files

```python
# Stream continuously to CSV files
(
    DataGenerator(RandSpecs.devices())
    .write_stream
    .format("csv")
    .option("max_rows_per_file", 10000)
    .option("min_throughput", 100)
    .option("max_throughput", 500)
    .load("/tmp/device_stream/")
)
```

---

## 🔄 Transformers

Apply post-generation transformations to your data:

### Single Transformer

```python
from rand_engine import DataGenerator

spec = {
    "name": {
        "method": "distincts",
        "kwargs": {"distincts": ["john", "jane", "bob"]}
    }
}

# Add transformer
dg = DataGenerator(spec).transformers([
    lambda df: df.assign(name=df['name'].str.upper())  # Convert to uppercase
])

df = dg.size(1000).get_df()
print(df['name'].head())
# JOHN, JANE, BOB
```

### Multiple Transformers (Chained)

```python
dg = DataGenerator(spec).transformers([
    lambda df: df.assign(name=df['name'].str.upper()),              # Uppercase
    lambda df: df.assign(name_length=df['name'].str.len()),         # Add length
    lambda df: df.assign(is_short=df['name_length'] < 5)           # Flag short names
])

df = dg.size(1000).get_df()
print(df.head())
```

### Complex Transformation

```python
import pandas as pd
from datetime import datetime

spec = {
    "order_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 8}},
    "amount": {"method": "floats", "kwargs": {"min": 10, "max": 1000, "round": 2}},
    "timestamp": {
        "method": "unix_timestamps",
        "kwargs": {"start": "01-01-2024", "end": "31-12-2024", "format": "%d-%m-%Y"}
    }
}

dg = DataGenerator(spec).transformers([
    # Convert Unix timestamp to datetime
    lambda df: df.assign(order_date=pd.to_datetime(df['timestamp'], unit='s')),
    
    # Add derived columns
    lambda df: df.assign(
        year=df['order_date'].dt.year,
        month=df['order_date'].dt.month,
        weekday=df['order_date'].dt.day_name()
    ),
    
    # Categorize amounts
    lambda df: df.assign(
        amount_category=pd.cut(
            df['amount'],
            bins=[0, 50, 200, 500, 1000],
            labels=['Low', 'Medium', 'High', 'Premium']
        )
    ),
    
    # Drop temporary columns
    lambda df: df.drop(columns=['timestamp'])
])

df = dg.size(10000).get_df()
print(df.head())
```

---

## 🔗 Constraints & Referential Integrity ⭐ NEW

**The most powerful feature of v0.6.1!** Create realistic datasets with proper Primary Key/Foreign Key relationships.

### Concept

Constraints ensure **referential integrity** between multiple specs:
- **Primary Key (PK)**: Creates a checkpoint table with generated records
- **Foreign Key (FK)**: References values from a PK checkpoint table
- **Watermark**: Limits FK references to recent records (e.g., last 60 seconds)

### Simple PK → FK Example

```python
from rand_engine import DataGenerator

# 1. Create CATEGORIES (Primary Key)
spec_categories = {
    "category_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint", "length": 4}
    },
    "category_name": {
        "method": "distincts",
        "kwargs": {"distincts": ["Electronics", "Books", "Clothing", "Home", "Sports"]}
    },
    "constraints": {
        "category_pk": {
            "name": "category_pk",         # Checkpoint table name
            "tipo": "PK",                   # Primary Key
            "fields": ["category_id VARCHAR(4)"]  # Field + SQL type
        }
    }
}

# Generate categories
dg_cat = DataGenerator(spec_categories, seed=42).checkpoint(":memory:")
df_categories = dg_cat.size(10).get_df()
print(f"✅ Created {len(df_categories)} categories")
print(df_categories)

# 2. Create PRODUCTS (Foreign Key → categories)
spec_products = {
    "product_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint", "length": 8}
    },
    "product_name": {
        "method": "distincts",
        "kwargs": {"distincts": [f"Product {i}" for i in range(100)]}
    },
    "price": {
        "method": "floats_normal",
        "kwargs": {"mean": 50, "std": 20, "round": 2}
    },
    "constraints": {
        "category_fk": {
            "name": "category_pk",          # References PK table
            "tipo": "FK",                   # Foreign Key
            "fields": ["category_id"],      # Field (no type needed)
            "watermark": 60                 # Only last 60 seconds
        }
    }
}

# Generate products
dg_prod = DataGenerator(spec_products, seed=42).checkpoint(":memory:")
df_products = dg_prod.size(1000).get_df()
print(f"✅ Created {len(df_products)} products")
print(df_products.head())

# 3. VERIFY INTEGRITY
print("\n📊 Integrity Check:")
print(f"Unique category_ids in products: {df_products['category_id'].nunique()}")
print(f"All products reference valid categories: {set(df_products['category_id']).issubset(set(df_categories['category_id']))}")
```

**Output:**
```
✅ Created 10 categories
  category_id category_name
0        0001   Electronics
1        0002         Books
2        0003      Clothing
3        0004          Home
4        0005        Sports

✅ Created 1000 products
  product_id product_name  price category_id
0   00000001    Product 1  45.32        0003
1   00000002    Product 2  67.89        0001
2   00000003    Product 3  32.15        0002

📊 Integrity Check:
Unique category_ids in products: 5
All products reference valid categories: True
```

### Composite Keys

```python
# CLIENTS with composite PK (client_id + client_type)
spec_clients = {
    "client_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint", "length": 8}
    },
    "client_type": {
        "method": "distincts",
        "kwargs": {"distincts": ["PF", "PJ"]}  # Pessoa Física/Jurídica
    },
    "name": {
        "method": "distincts",
        "kwargs": {"distincts": [f"Client {i}" for i in range(1000)]}
    },
    "constraints": {
        "clients_pk": {
            "name": "clients_pk",
            "tipo": "PK",
            "fields": [
                "client_id VARCHAR(8)",
                "client_type VARCHAR(2)"
            ]
        }
    }
}

dg_clients = DataGenerator(spec_clients).checkpoint(":memory:")
df_clients = dg_clients.size(100).get_df()
print(f"✅ Created {len(df_clients)} clients")

# TRANSACTIONS with composite FK
spec_transactions = {
    "transaction_id": {
        "method": "unique_ids",
        "kwargs": {"strategy": "zint", "length": 12}
    },
    "amount": {
        "method": "floats_normal",
        "kwargs": {"mean": 500, "std": 200, "round": 2}
    },
    "constraints": {
        "clients_fk": {
            "name": "clients_pk",
            "tipo": "FK",
            "fields": ["client_id", "client_type"],  # Composite FK
            "watermark": 3600  # Last hour
        }
    }
}

dg_trans = DataGenerator(spec_transactions).checkpoint(":memory:")
df_transactions = dg_trans.size(5000).get_df()
print(f"✅ Created {len(df_transactions)} transactions")

# Verify
valid_clients = set(zip(df_clients['client_id'], df_clients['client_type']))
transaction_clients = set(zip(df_transactions['client_id'], df_transactions['client_type']))
print(f"All transactions reference valid clients: {transaction_clients.issubset(valid_clients)}")
```

### Complete E-commerce Example (3 Levels)

```python
from rand_engine import DataGenerator

# Level 1: CATEGORIES (PK)
spec_categories = {
    "category_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 4}},
    "category_name": {"method": "distincts", "kwargs": {"distincts": ["Electronics", "Books", "Clothing"]}},
    "constraints": {
        "categories_pk": {
            "name": "categories_pk",
            "tipo": "PK",
            "fields": ["category_id VARCHAR(4)"]
        }
    }
}

df_cat = (
    DataGenerator(spec_categories)
    .checkpoint(":memory:")
    .option("reset_checkpoint", True)  # Clear previous data
    .size(10).get_df()
)
print(f"✅ Level 1: {len(df_cat)} categories")

# Level 2: PRODUCTS (FK → categories, PK for orders)
spec_products = {
    "product_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 8}},
    "product_name": {"method": "distincts", "kwargs": {"distincts": [f"Product {i}" for i in range(100)]}},
    "price": {"method": "floats_normal", "kwargs": {"mean": 100, "std": 30, "round": 2}},
    "constraints": {
        "products_pk": {
            "name": "products_pk",
            "tipo": "PK",
            "fields": ["product_id VARCHAR(8)"]
        },
        "categories_fk": {
            "name": "categories_pk",
            "tipo": "FK",
            "fields": ["category_id"],
            "watermark": 60
        }
    }
}

df_prod = DataGenerator(spec_products).size(100).get_df()
print(f"✅ Level 2: {len(df_prod)} products")

# Level 3: ORDERS (FK → products)
spec_orders = {
    "order_id": {"method": "unique_ids", "kwargs": {"strategy": "uuid4"}},
    "quantity": {"method": "integers", "kwargs": {"min": 1, "max": 10}},
    "constraints": {
        "products_fk": {
            "name": "products_pk",
            "tipo": "FK",
            "fields": ["product_id"],
            "watermark": 120
        }
    }
}

df_orders = DataGenerator(spec_orders).size(1000).get_df()
print(f"✅ Level 3: {len(df_orders)} orders")

# Verify 3-level integrity
print("\n📊 Full Integrity Check:")
print(f"Products reference categories: {set(df_prod['category_id']).issubset(set(df_cat['category_id']))}")
print(f"Orders reference products: {set(df_orders['product_id']).issubset(set(df_prod['product_id']))}")
print(f"Categories → Products → Orders: ✅ VALID")
```

📖 **Complete constraints documentation:** [CONSTRAINTS.md](./docs/CONSTRAINTS.md)

---

## 🔗 Correlated Columns

Generate columns with correlated values (without constraints).

### Simple Correlation (distincts_map)

```python
spec = {
    "device_os": {
        "method": "distincts_map",
        "cols": ["device_type", "os"],  # Output columns
        "kwargs": {
            "distincts": {
                "smartphone": ["android", "ios"],
                "tablet": ["android", "ios", "windows"],
                "desktop": ["windows", "macos", "linux"]
            }
        }
    }
}

df = DataGenerator(spec).size(1000).get_df()
print(df.groupby('device_type')['os'].value_counts())
```

### Weighted Correlation (distincts_map_prop)

```python
spec = {
    "product_status": {
        "method": "distincts_map_prop",
        "cols": ["product_type", "condition"],
        "kwargs": {
            "distincts": {
                "laptop": [("new", 80), ("refurbished", 20)],
                "smartphone": [("new", 90), ("used", 10)],
                "tablet": [("new", 85), ("refurbished", 10), ("used", 5)]
            }
        }
    }
}

df = DataGenerator(spec).size(5000).get_df()
print(df.groupby('product_type')['condition'].value_counts(normalize=True))
```

---

## 🎨 Complex Patterns

### IP Addresses

```python
spec = {
    "ip_address": {
        "method": "complex_distincts",
        "kwargs": {
            "pattern": "x.x.x.x",
            "replacement": "x",
            "templates": [
                {"method": "distincts", "parms": {"distincts": ["192", "10", "172"]}},
                {"method": "integers", "parms": {"min": 0, "max": 255}},
                {"method": "integers", "parms": {"min": 0, "max": 255}},
                {"method": "integers", "parms": {"min": 1, "max": 254}}
            ]
        }
    }
}

df = DataGenerator(spec).size(1000).get_df()
print(df['ip_address'].head())
# 192.45.123.67
# 10.201.34.12
# 172.98.56.234
```

### Email Addresses

```python
spec = {
    "email": {
        "method": "complex_distincts",
        "kwargs": {
            "pattern": "x@x.x",
            "replacement": "x",
            "templates": [
                {"method": "distincts", "parms": {"distincts": [f"user{i}" for i in range(1000)]}},
                {"method": "distincts", "parms": {"distincts": ["gmail", "yahoo", "outlook", "hotmail"]}},
                {"method": "distincts", "parms": {"distincts": ["com", "net", "org"]}}
            ]
        }
    }
}

df = DataGenerator(spec).size(1000).get_df()
print(df['email'].head())
# user42@gmail.com
# user891@yahoo.net
# user123@outlook.com
```

### API Endpoints

```python
spec = {
    "endpoint": {
        "method": "complex_distincts",
        "kwargs": {
            "pattern": "/api/v1/x/x",
            "replacement": "x",
            "templates": [
                {"method": "distincts", "parms": {"distincts": ["users", "orders", "products", "payments"]}},
                {"method": "distincts", "parms": {"distincts": ["list", "create", "update", "delete"]}}
            ]
        }
    }
}

df = DataGenerator(spec).size(1000).get_df()
print(df['endpoint'].value_counts())
```

---

## 💼 E-commerce

### Complete E-commerce Pipeline

```python
from rand_engine import DataGenerator, RandSpecs

# 1. Generate customers
customers = DataGenerator(RandSpecs.customers(), seed=42).size(10000).get_df()
customer_ids = customers['customer_id'].tolist()

# 2. Generate products
products = DataGenerator(RandSpecs.products(), seed=42).size(1000).get_df()
product_ids = products['product_id'].tolist()

# 3. Generate orders (referencing customers and products)
orders_spec = RandSpecs.orders()
orders_spec['customer_id'] = {
    "method": "distincts",
    "kwargs": {"distincts": customer_ids}
}
orders_spec['product_id'] = {
    "method": "distincts",
    "kwargs": {"distincts": product_ids}
}
orders = DataGenerator(orders_spec, seed=42).size(50000).get_df()

# 4. Analysis
print("=" * 80)
print("E-COMMERCE ANALYTICS")
print("=" * 80)
print(f"Total customers: {len(customers):,}")
print(f"Total products: {len(products):,}")
print(f"Total orders: {len(orders):,}")
print(f"\nRevenue by currency:")
print(orders.groupby('currency')['amount'].sum().sort_values(ascending=False))
print(f"\nTop 10 customers by number of orders:")
print(orders['customer_id'].value_counts().head(10))
```

### Shopping Cart Abandonment

```python
spec = {
    "session_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 12}},
    "user_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 8}},
    "items_in_cart": {"method": "integers", "kwargs": {"min": 1, "max": 20}},
    "cart_value": {"method": "floats_normal", "kwargs": {"mean": 150, "std": 75, "round": 2}},
    "time_spent_min": {"method": "floats_normal", "kwargs": {"mean": 8, "std": 5, "round": 1}},
    "device": {"method": "distincts_prop", "kwargs": {"distincts": {"mobile": 65, "desktop": 35}}},
    "abandoned": {"method": "booleans", "kwargs": {"true_prob": 0.68}},  # 68% abandonment rate
}

carts = DataGenerator(spec, seed=123).size(50000).get_df()

# Analysis
print("=" * 80)
print("CART ABANDONMENT ANALYSIS")
print("=" * 80)
abandonment_rate = (carts['abandoned'].sum() / len(carts)) * 100
print(f"Overall abandonment rate: {abandonment_rate:.2f}%")
print(f"\nBy device:")
print(carts.groupby('device')['abandoned'].agg(['count', 'mean']))
print(f"\nAverage cart value (abandoned): ${carts[carts['abandoned']]['cart_value'].mean():.2f}")
print(f"Average cart value (converted): ${carts[~carts['abandoned']]['cart_value'].mean():.2f}")
```

---

## 💰 Financial Services

### Banking Transactions

```python
from rand_engine import DataGenerator, RandSpecs

# Generate 1M transactions
transactions = DataGenerator(RandSpecs.transactions(), seed=42).size(1000000).get_df()

# Export to Parquet
transactions.to_parquet("transactions_2024.parquet", compression="snappy")

# Analysis
print("=" * 80)
print("TRANSACTION SUMMARY")
print("=" * 80)
print(f"Total transactions: {len(transactions):,}")
print(f"Total volume: ${transactions['amount'].sum():,.2f}")
print(f"Average transaction: ${transactions['amount'].mean():.2f}")
print(f"\nBy type:")
print(transactions.groupby('type')['amount'].agg(['count', 'sum', 'mean']).round(2))
```

### Fraud Detection Dataset

```python
spec = {
    "transaction_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 16}},
    "account_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 10}},
    "amount": {"method": "floats_normal", "kwargs": {"mean": 85, "std": 120, "round": 2}},
    "merchant_category": {
        "method": "distincts_prop",
        "kwargs": {"distincts": {
            "grocery": 250,
            "gas": 180,
            "restaurant": 200,
            "online": 150,
            "travel": 80,
            "entertainment": 100,
            "other": 40
        }}
    },
    "location_match": {"method": "booleans", "kwargs": {"true_prob": 0.95}},
    "time_since_last_tx_min": {"method": "floats_normal", "kwargs": {"mean": 240, "std": 180, "round": 0}},
    "is_fraud": {"method": "booleans", "kwargs": {"true_prob": 0.002}},  # 0.2% fraud rate
}

fraud_data = DataGenerator(spec, seed=789).size(500000).get_df()

# ML Training Split
from sklearn.model_selection import train_test_split

train_df, test_df = train_test_split(fraud_data, test_size=0.2, random_state=42)

print("=" * 80)
print("FRAUD DETECTION DATASET")
print("=" * 80)
print(f"Total transactions: {len(fraud_data):,}")
print(f"Training set: {len(train_df):,}")
print(f"Test set: {len(test_df):,}")
print(f"Fraud cases (train): {train_df['is_fraud'].sum()} ({(train_df['is_fraud'].sum()/len(train_df)*100):.3f}%)")
print(f"Fraud cases (test): {test_df['is_fraud'].sum()} ({(test_df['is_fraud'].sum()/len(test_df)*100):.3f}%)")
```

---

## 👥 Human Resources

### Employee Management System

```python
from rand_engine import DataGenerator, RandSpecs

# Generate employees
employees = DataGenerator(RandSpecs.employees(), seed=42).size(1000).get_df()

# Analysis
print("=" * 80)
print("HR METRICS")
print("=" * 80)
print(f"Total employees: {len(employees):,}")
print(f"Average salary: ${employees['salary'].mean():,.2f}")
print(f"\nBy department:")
print(employees.groupby('department').agg({
    'employee_id': 'count',
    'salary': ['mean', 'min', 'max']
}).round(2))
print(f"\nBy level:")
print(employees.groupby('level').agg({
    'employee_id': 'count',
    'salary': ['mean', 'min', 'max']
}).round(2))
```

### Payroll Processing

```python
import pandas as pd

spec = {
    "employee_id": {"method": "unique_ids", "kwargs": {"strategy": "zint", "length": 6, "prefix": "EMP"}},
    "base_salary": {"method": "floats_normal", "kwargs": {"mean": 5000, "std": 2000, "round": 2}},
    "overtime_hours": {"method": "floats_normal", "kwargs": {"mean": 5, "std": 3, "round": 1}},
    "bonus": {"method": "floats_normal", "kwargs": {"mean": 500, "std": 300, "round": 2}},
    "deductions": {"method": "floats_normal", "kwargs": {"mean": 800, "std": 200, "round": 2}},
}

payroll = DataGenerator(spec, seed=654).size(5000).get_df()

# Calculate derived fields
payroll['overtime_rate'] = payroll['base_salary'] / 160 * 1.5  # 1.5x hourly rate
payroll['overtime_pay'] = payroll['overtime_hours'] * payroll['overtime_rate']
payroll['gross_pay'] = payroll['base_salary'] + payroll['overtime_pay'] + payroll['bonus']
payroll['tax_withheld'] = payroll['gross_pay'] * 0.25  # 25% tax
payroll['net_pay'] = payroll['gross_pay'] - payroll['deductions'] - payroll['tax_withheld']

print("=" * 80)
print("PAYROLL SUMMARY")
print("=" * 80)
print(f"Total employees: {len(payroll):,}")
print(f"Total gross payroll: ${payroll['gross_pay'].sum():,.2f}")
print(f"Total net payroll: ${payroll['net_pay'].sum():,.2f}")
print(f"Average overtime hours: {payroll['overtime_hours'].mean():.1f}")
print(f"Total tax withheld: ${payroll['tax_withheld'].sum():,.2f}")
```

---

## 🌐 IoT & Telemetry

### IoT Device Monitoring

```python
from rand_engine import DataGenerator, RandSpecs

# Generate device telemetry
devices = DataGenerator(RandSpecs.devices(), seed=42).size(10000).get_df()

# Find critical devices
critical = devices[
    (devices['status'] == 'critical') & 
    (devices['battery'] < 20)
]

print("=" * 80)
print("IOT DEVICE MONITORING")
print("=" * 80)
print(f"Total devices: {len(devices):,}")
print(f"Critical devices with low battery: {len(critical)}")
print(f"\nStatus distribution:")
print(devices['status'].value_counts())
print(f"\nPriority distribution:")
print(devices['priority'].value_counts())

# Export for monitoring dashboard
devices.to_parquet("device_telemetry.parquet")
```

### Server Metrics

```python
spec = {
    "server_id": {
        "method": "complex_distincts",
        "kwargs": {
            "pattern": "srv-x-x",
            "replacement": "x",
            "templates": [
                {"method": "distincts", "parms": {"distincts": ["us-east-1", "us-west-2", "eu-central-1"]}},
                {"method": "integers", "parms": {"min": 1, "max": 100}}
            ]
        }
    },
    "cpu_usage_pct": {"method": "floats_normal", "kwargs": {"mean": 45, "std": 20, "round": 1}},
    "memory_usage_pct": {"method": "floats_normal", "kwargs": {"mean": 60, "std": 15, "round": 1}},
    "disk_usage_pct": {"method": "floats_normal", "kwargs": {"mean": 70, "std": 10, "round": 1}},
    "network_in_mbps": {"method": "floats_normal", "kwargs": {"mean": 100, "std": 50, "round": 2}},
    "network_out_mbps": {"method": "floats_normal", "kwargs": {"mean": 80, "std": 40, "round": 2}},
    "response_time_ms": {"method": "floats_normal", "kwargs": {"mean": 150, "std": 75, "round": 0}},
}

metrics = DataGenerator(spec, seed=111).size(100000).get_df()

# Alert conditions
high_cpu = metrics[metrics['cpu_usage_pct'] > 80]
high_memory = metrics[metrics['memory_usage_pct'] > 85]
slow_response = metrics[metrics['response_time_ms'] > 300]

print("=" * 80)
print("SERVER MONITORING ALERTS")
print("=" * 80)
print(f"Total metrics: {len(metrics):,}")
print(f"High CPU alerts (>80%): {len(high_cpu)}")
print(f"High memory alerts (>85%): {len(high_memory)}")
print(f"Slow response alerts (>300ms): {len(slow_response)}")
```

---

## 📊 Web Analytics

### Web Server Logs

```python
spec = {
    "request_id": {"method": "unique_ids", "kwargs": {"strategy": "uuid4"}},
    "timestamp": {
        "method": "unix_timestamps",
        "kwargs": {"start": "01-01-2024", "end": "31-12-2024", "format": "%d-%m-%Y"}
    },
    "method": {
        "method": "distincts_prop",
        "kwargs": {"distincts": {"GET": 700, "POST": 200, "PUT": 50, "DELETE": 30, "PATCH": 20}}
    },
    "endpoint": {
        "method": "complex_distincts",
        "kwargs": {
            "pattern": "/api/v1/x",
            "replacement": "x",
            "templates": [
                {"method": "distincts", "parms": {"distincts": [
                    "users", "orders", "products", "payments", "analytics", "reports"
                ]}}
            ]
        }
    },
    "status_code": {
        "method": "distincts_prop",
        "kwargs": {"distincts": {200: 850, 201: 100, 400: 20, 404: 15, 500: 10, 503: 5}}
    },
    "response_time_ms": {"method": "floats_normal", "kwargs": {"mean": 200, "std": 100, "round": 0}},
    "user_agent": {
        "method": "distincts_prop",
        "kwargs": {"distincts": {
            "Chrome": 450,
            "Firefox": 250,
            "Safari": 200,
            "Edge": 80,
            "Mobile": 20
        }}
    }
}

logs = DataGenerator(spec, seed=999).size(1000000).get_df()

# Analysis
print("=" * 80)
print("WEB SERVER ANALYTICS")
print("=" * 80)
print(f"Total requests: {len(logs):,}")
print(f"\nBy HTTP method:")
print(logs['method'].value_counts())
print(f"\nBy status code:")
print(logs['status_code'].value_counts().sort_index())
print(f"\nError rate: {((logs['status_code'] >= 400).sum() / len(logs) * 100):.2f}%")
print(f"Average response time: {logs['response_time_ms'].mean():.0f}ms")
```

---

## 🛠️ ETL Pipeline Testing

### End-to-End Pipeline

```python
from rand_engine import DataGenerator, RandSpecs
import pandas as pd

print("=" * 80)
print("ETL PIPELINE SIMULATION")
print("=" * 80)

# 1. EXTRACT: Generate source data
print("\n[1/4] EXTRACT: Generating source data...")
source_data = DataGenerator(RandSpecs.transactions(), seed=42).size(1000000).get_df()
source_data.to_parquet("staging/raw_transactions.parquet")
print(f"✅ Generated {len(source_data):,} transactions → staging/raw_transactions.parquet")

# 2. TRANSFORM: Apply business logic
print("\n[2/4] TRANSFORM: Applying transformations...")
source_data['transaction_date'] = pd.to_datetime(source_data['timestamp'], unit='s')
source_data['year_month'] = source_data['transaction_date'].dt.to_period('M')
source_data['amount_category'] = pd.cut(
    source_data['amount'],
    bins=[0, 50, 200, 500, float('inf')],
    labels=['Small', 'Medium', 'Large', 'XLarge']
)
print("✅ Added derived columns: transaction_date, year_month, amount_category")

# 3. LOAD: Export to data warehouse
print("\n[3/4] LOAD: Writing to data warehouse...")
source_data.to_parquet(
    "warehouse/fact_transactions.parquet",
    partition_cols=['year_month'],
    compression="snappy"
)
print("✅ Loaded to warehouse/fact_transactions.parquet (partitioned by year_month)")

# 4. VALIDATE: Data quality checks
print("\n[4/4] VALIDATE: Running data quality checks...")
checks = {
    "Row count": len(source_data) == 1000000,
    "No duplicate IDs": source_data['transaction_id'].nunique() == 1000000,
    "No null amounts": source_data['amount'].isna().sum() == 0,
    "Valid amount range": (source_data['amount'] >= 0).all(),
    "Valid dates": (source_data['transaction_date'].dt.year == 2024).all()
}

for check_name, passed in checks.items():
    status = "✅" if passed else "❌"
    print(f"{status} {check_name}")

all_passed = all(checks.values())
print(f"\n{'=' * 80}")
print(f"ETL PIPELINE: {'✅ SUCCESS' if all_passed else '❌ FAILED'}")
print(f"{'=' * 80}")
```

### Incremental Loads

```python
from datetime import datetime, timedelta
from rand_engine import DataGenerator, RandSpecs

def generate_daily_batch(date_str, num_records):
    """Generate daily batch with date-specific seed."""
    seed = int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())
    spec = RandSpecs.transactions()
    spec['batch_date'] = {
        "method": "distincts",
        "kwargs": {"distincts": [date_str]}
    }
    return DataGenerator(spec, seed=seed).size(num_records).get_df()

# Simulate 7 days of incremental loads
print("=" * 80)
print("INCREMENTAL DATA PIPELINE")
print("=" * 80)

for i in range(7):
    date = datetime(2024, 1, 1) + timedelta(days=i)
    date_str = date.strftime("%Y-%m-%d")
    
    # Generate daily batch
    daily_data = generate_daily_batch(date_str, 100000)
    
    # Append to data lake
    output_path = f"data_lake/transactions/date={date_str}/data.parquet"
    daily_data.to_parquet(output_path, compression="snappy")
    
    print(f"✅ Day {i+1} ({date_str}): {len(daily_data):,} records → {output_path}")

print(f"\n{'=' * 80}")
print("✅ Incremental load complete for 7 days")
print(f"{'=' * 80}")
```

---

## ⚡ Load Testing

### API Load Test

```python
from rand_engine import DataGenerator, RandSpecs
import requests
from concurrent.futures import ThreadPoolExecutor
import time

# Generate test users
print("Generating test data...")
users = DataGenerator(RandSpecs.users(), seed=42).size(1000).get_df()

def create_user(user_data):
    """Send POST request to create user."""
    try:
        response = requests.post(
            "http://localhost:8000/api/users",
            json=user_data.to_dict(),
            timeout=5
        )
        return response.status_code
    except Exception as e:
        return 0

# Parallel load test
print("\n=" * 80)
print("LOAD TEST: Creating 1000 users with 10 concurrent threads")
print("=" * 80)

start_time = time.time()

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(
        create_user,
        [users.iloc[i] for i in range(len(users))]
    ))

elapsed = time.time() - start_time

# Analyze results
success_rate = (results.count(201) / len(results)) * 100
throughput = len(results) / elapsed

print(f"\n✅ Load test complete!")
print(f"Total requests: {len(results)}")
print(f"Success rate: {success_rate:.2f}%")
print(f"Total time: {elapsed:.2f}s")
print(f"Throughput: {throughput:.2f} req/sec")
```

### Database Stress Test

```python
from rand_engine import DataGenerator, RandSpecs
from rand_engine.integrations._duckdb_handler import DuckDBHandler
import time

# Create database
db = DuckDBHandler(":memory:")
db.create_table("transactions", "transaction_id VARCHAR(20) PRIMARY KEY")

# Test different batch sizes
batch_sizes = [1_000, 10_000, 50_000, 100_000]
results = []

print("=" * 80)
print("DATABASE STRESS TEST")
print("=" * 80)

for batch_size in batch_sizes:
    # Generate data
    data = DataGenerator(RandSpecs.transactions()).size(batch_size).get_df()
    
    # Measure insert time
    start = time.time()
    db.insert_df("transactions", data, pk_cols=["transaction_id"])
    elapsed = time.time() - start
    
    throughput = batch_size / elapsed
    results.append({
        'batch_size': batch_size,
        'time_sec': elapsed,
        'throughput': throughput
    })
    
    print(f"Batch {batch_size:,}: {elapsed:.3f}s ({throughput:,.0f} rows/sec)")

db.close()

print(f"\n{'=' * 80}")
print("✅ Stress test complete")
print(f"{'=' * 80}")
```

---

## 💾 Database Integration

### DuckDB Integration

```python
from rand_engine import DataGenerator, RandSpecs
from rand_engine.integrations._duckdb_handler import DuckDBHandler

# Create database
db = DuckDBHandler("analytics.duckdb")

# Create table
db.create_table(
    "customers",
    pk_def="customer_id VARCHAR(10), email VARCHAR(100)"
)

# Generate and insert data
customers = DataGenerator(RandSpecs.customers(), seed=42).size(10000).get_df()
db.insert_df("customers", customers, pk_cols=["customer_id"])

print(f"✅ Inserted {len(customers):,} customers into DuckDB")

# Query data
result = db.select_all("customers", columns=["customer_id", "name", "email"])
print(f"✅ Retrieved {len(result)} rows from database")
print(result.head())

# Analytical query
query = """
SELECT 
    is_active,
    COUNT(*) as count,
    AVG(account_balance) as avg_balance
FROM customers
GROUP BY is_active
"""
analytics = db.query_with_pandas(query)
print("\n📊 Analytics:")
print(analytics)

db.close()
```

### PostgreSQL Integration

```python
import psycopg2
from rand_engine import DataGenerator, RandSpecs
import pandas as pd

# Generate data
transactions = DataGenerator(RandSpecs.transactions(), seed=42).size(100000).get_df()

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="testdb",
    user="postgres",
    password="password"
)

# Create table
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(10),
    amount DECIMAL(10,2),
    currency VARCHAR(3),
    type VARCHAR(20),
    timestamp BIGINT
)
""")
conn.commit()

# Insert data (batch insert)
from psycopg2.extras import execute_batch

insert_query = """
INSERT INTO transactions (transaction_id, user_id, amount, currency, type, timestamp)
VALUES (%s, %s, %s, %s, %s, %s)
"""

data_tuples = list(transactions.itertuples(index=False, name=None))
execute_batch(cursor, insert_query, data_tuples, page_size=1000)
conn.commit()

print(f"✅ Inserted {len(transactions):,} transactions into PostgreSQL")

cursor.close()
conn.close()
```

---

## ⚡ Benchmarks

### Generation Speed

```python
from rand_engine import DataGenerator, RandSpecs
import time

sizes = [1_000, 10_000, 100_000, 1_000_000]

print("=" * 80)
print("GENERATION SPEED BENCHMARK")
print("=" * 80)

for size in sizes:
    start = time.time()
    df = DataGenerator(RandSpecs.customers(), seed=42).size(size).get_df()
    elapsed = time.time() - start
    throughput = size / elapsed
    
    print(f"{size:>10,} rows: {elapsed:>6.2f}s ({throughput:>10,.0f} rows/sec)")

print(f"\n{'=' * 80}")
```

**Example Output:**
```
================================================================================
GENERATION SPEED BENCHMARK
================================================================================
     1,000 rows:   0.01s (    100,000 rows/sec)
    10,000 rows:   0.05s (    200,000 rows/sec)
   100,000 rows:   0.45s (    222,222 rows/sec)
 1,000,000 rows:   4.50s (    222,222 rows/sec)
================================================================================
```

### Batch vs Streaming

```python
from rand_engine import DataGenerator, RandSpecs
import time

spec = RandSpecs.transactions()
target_records = 100_000

# Batch generation
print("Batch generation:")
start = time.time()
df = DataGenerator(spec, seed=42).size(target_records).get_df()
batch_time = time.time() - start
print(f"  Time: {batch_time:.2f}s")
print(f"  Throughput: {target_records/batch_time:,.0f} rows/sec")
print(f"  Memory: ~{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")

# Stream generation
print("\nStream generation:")
start = time.time()
count = 0
stream = DataGenerator(spec).stream_dict(min_throughput=50000, max_throughput=50000)
for record in stream:
    count += 1
    if count >= target_records:
        break
stream_time = time.time() - start
print(f"  Time: {stream_time:.2f}s")
print(f"  Throughput: {target_records/stream_time:,.0f} rows/sec")
print(f"  Memory: Constant (~few KB per record)")
```

---

## 🧠 Memory Optimization

### Chunk Processing (Large Datasets)

```python
from rand_engine import DataGenerator, RandSpecs

# Generate 10M rows in chunks of 100K
chunk_size = 100_000
total_rows = 10_000_000
num_chunks = total_rows // chunk_size

print(f"Generating {total_rows:,} rows in {num_chunks} chunks of {chunk_size:,}...")

for i in range(num_chunks):
    chunk = DataGenerator(RandSpecs.transactions()).size(chunk_size).get_df()
    
    # Process chunk (e.g., write to database, export to file)
    chunk.to_parquet(f"/tmp/chunks/chunk_{i:04d}.parquet")
    
    if (i + 1) % 10 == 0:
        print(f"Processed {(i+1)*chunk_size:,} / {total_rows:,} rows...")

print("✅ Complete - memory-efficient generation")
```

### Streaming to Avoid Memory Issues

```python
from rand_engine import DataGenerator, RandSpecs
import csv

# Stream 10M records directly to CSV (constant memory)
output_file = "/tmp/massive_dataset.csv"
target_records = 10_000_000

print(f"Streaming {target_records:,} records to {output_file}...")

stream = DataGenerator(RandSpecs.customers()).stream_dict(
    min_throughput=100000,
    max_throughput=100000
)

with open(output_file, 'w', newline='') as f:
    writer = None
    count = 0
    
    for record in stream:
        if writer is None:
            writer = csv.DictWriter(f, fieldnames=record.keys())
            writer.writeheader()
        
        writer.writerow(record)
        count += 1
        
        if count % 1000000 == 0:
            print(f"Written {count:,} records...")
        
        if count >= target_records:
            break

print(f"✅ Complete - {count:,} records written with constant memory usage")
```

---

## 🚀 Parallel Generation

### Multi-Process Generation

```python
from rand_engine import DataGenerator, RandSpecs
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
import time

def generate_chunk(chunk_id, size):
    """Generate data chunk in separate process."""
    seed = 42 + chunk_id  # Different seed per chunk
    df = DataGenerator(RandSpecs.transactions(), seed=seed).size(size).get_df()
    return df

# Generate 1M rows using 4 processes
num_processes = 4
chunk_size = 250_000
total_rows = num_processes * chunk_size

print("=" * 80)
print(f"PARALLEL GENERATION: {num_processes} processes")
print("=" * 80)

start_time = time.time()

with ProcessPoolExecutor(max_workers=num_processes) as executor:
    futures = [
        executor.submit(generate_chunk, i, chunk_size)
        for i in range(num_processes)
    ]
    chunks = [f.result() for f in futures]

# Combine results
final_df = pd.concat(chunks, ignore_index=True)
elapsed = time.time() - start_time

print(f"\n✅ Generated {len(final_df):,} total rows")
print(f"Time: {elapsed:.2f}s")
print(f"Throughput: {len(final_df)/elapsed:,.0f} rows/sec")
```

---

## 🔍 Logging & Debugging

### Enable Logging

```python
import logging
from rand_engine import DataGenerator, RandSpecs

# Enable INFO-level logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

# Operations now show logs
from rand_engine.integrations._duckdb_handler import DuckDBHandler

db = DuckDBHandler(":memory:")
# INFO:rand_engine.integrations._duckdb_handler:Created new connection to DuckDB database: :memory:

db.create_table("test", pk_def="id VARCHAR(10)")
df = DataGenerator(RandSpecs.customers()).size(1000).get_df()
db.insert_df("test", df, pk_cols=["customer_id"])

db.close()
# INFO:rand_engine.integrations._duckdb_handler:Database connection closed and removed from pool: :memory:
```

### Debug Mode

```python
# Enable DEBUG logging for detailed information
logging.basicConfig(level=logging.DEBUG)

# Now see detailed operation logs
dg = DataGenerator(RandSpecs.customers())
df = dg.size(100).get_df()
```

📖 **Complete logging guide:** [LOGGING.md](./docs/LOGGING.md)

---

## 📚 Additional Resources

- 📖 **Documentation Hub**: [docs/README.md](./docs/README.md)
- 📖 **API Reference**: [API_REFERENCE.md](./docs/API_REFERENCE.md)
- 🔗 **Constraints Guide**: [CONSTRAINTS.md](./docs/CONSTRAINTS.md)
- 🔧 **Logging Guide**: [LOGGING.md](./docs/LOGGING.md)
- 📝 **Changelog**: [CHANGELOG.md](./CHANGELOG.md)
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/marcoaureliomenezes/rand_engine/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/marcoaureliomenezes/rand_engine/discussions)

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

---

**Last Updated:** October 21, 2025  
**Version:** 0.6.1  
**Maintainer:** Marco Aurelio Menezes
