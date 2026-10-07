# Recipes

Short, runnable patterns. Every `python` block runs in CI, in order, in one namespace.

## Faker pools

<!-- derived-from: generation-methods sha256:b3bed2e747eb -->

Faker is slow per value; draw a pool once and sample it with `distincts`.

```python
from faker import Faker
from rand_engine import DataGenerator

fake = Faker("pt_BR")
Faker.seed(0)
names = [fake.name() for _ in range(500)]
emails = [fake.email() for _ in range(500)]

people = DataGenerator({
    "name": {"method": "distincts", "kwargs": {"distincts": names}},
    "email": {"method": "distincts", "kwargs": {"distincts": emails}},
}, seed=1).size(2_000).get_df()
assert people["name"].isin(names).all()
```

## Kafka or any queue

<!-- derived-from: data-generator sha256:2a69edeee8a2 -->

`stream_dict` yields JSON-ready dicts at a bounded rate; send them with your client.

```python
import json
from itertools import islice

events = DataGenerator({
    "event_id": {"method": "pk", "kwargs": {"start": 1}},
    "kind": {"method": "distincts", "kwargs": {"distincts": ["click", "view"]}},
}, seed=1).size(100)

records = [json.dumps(r).encode() for r in islice(events.stream_dict(min_throughput=500, max_throughput=1000), 20)]
assert json.loads(records[0])["event_id"] == 1
```

With `kafka-python` (not a test dependency, so this block is not executed):

```python no-run
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers="localhost:9092")
for record in events.stream_dict(min_throughput=10, max_throughput=50):
    producer.send("events", json.dumps(record).encode())
```

## Parquet lake

<!-- derived-from: writers-and-streaming sha256:6b17969e7cb2 -->

One folder per partition value, several files each.

```python
import pandas as pd

for day in ["2024-01-01", "2024-01-02"]:
    sales = DataGenerator({
        "sale_id": {"method": "pk", "kwargs": {"start": 1, "format": day.replace("-", "") + "{:06d}"}},
        "amount": {"method": "floats", "kwargs": {"min": 1, "max": 500}},
    }, seed=int(day[-2:])).size(1_000)
    sales.write.format("parquet").options(numFiles=2, compression="zstd").save(f"lake/sales/day={day}")

lake = pd.read_parquet("lake/sales")
assert len(lake) == 2_000 and lake["sale_id"].is_unique
```

## Related tables

<!-- derived-from: pk-fk-constraints sha256:3cc5aee7e657 -->

Share the parent's `pk` spec with the child's `fk`; see [4_CONSTRAINTS.md](4_CONSTRAINTS.md).

```python
customer_pk = {"method": "pk", "kwargs": {"start": 1, "format": "C{:05d}"}}
order_pk = {"method": "pk", "kwargs": {"start": 1}}

customers = DataGenerator({"customer_id": customer_pk}, seed=1).size(500).get_df()
orders = DataGenerator({
    "order_id": order_pk,
    "customer_id": {"method": "fk", "kwargs": {"parent": customer_pk, "parent_size": 500, "skew": 1.0}},
}, seed=2).size(2_000).get_df()
items = DataGenerator({
    "order_id": {"method": "fk", "kwargs": {"parent": order_pk, "parent_size": 2_000}},
    "qty": {"method": "integers", "kwargs": {"min": 1, "max": 5}},
}, seed=3).size(3_000).get_df()

assert orders.merge(customers, on="customer_id").shape[0] == 2_000
assert items.merge(orders, on="order_id").shape[0] == 3_000
```
