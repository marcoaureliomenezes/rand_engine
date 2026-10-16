# Recipes

Short, runnable patterns. Every `python` block runs in CI, in order, in one namespace.

## Faker pools

<!-- derived-from: generation-methods sha256:4ee6c20c444a -->
<!-- derived-from: templates-and-examples sha256:fa66c7f7252b -->

Faker is slow per value; `RandSpecs.faker_pool` draws a pool once and returns a `distincts` spec
(needs the optional `rand-engine[faker]`). `seed` fixes the pool.

```python
from rand_engine import DataGenerator, RandSpecs

name_spec = RandSpecs.faker_pool("name", locale="pt_BR", pool_size=500, seed=0)
people = DataGenerator({
    "name": name_spec,
    "email": RandSpecs.faker_pool("email", pool_size=500, seed=0),
}, seed=1).size(2_000).get_df()
assert people["name"].isin(name_spec["kwargs"]["distincts"]).all()
```

## Spec from an Arrow schema

<!-- derived-from: templates-and-examples sha256:fa66c7f7252b -->

`RandSpecs.from_schema` maps each field's Arrow type to a method and validates the result;
`overrides` replaces or tunes a field (a `method` key replaces it, other keys merge into it).

```python
import pyarrow as pa

schema = pa.schema([("id", pa.int64()), ("score", pa.float64()), ("active", pa.bool_())])
spec = RandSpecs.from_schema(schema, overrides={"score": {"kwargs": {"min": 0, "max": 10}}})
df = DataGenerator(spec, seed=1).size(500).get_df()
assert list(df.columns) == ["id", "score", "active"] and df["score"].between(0, 10).all()
```

## Kafka or any queue

<!-- derived-from: data-generator sha256:8af2e4c55309 -->

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

<!-- derived-from: writers-and-streaming sha256:554e6476d19d -->

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

<!-- derived-from: pk-fk-constraints sha256:afdf58f551d1 -->

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
