# Recipes

Short, runnable patterns. Every `python` block runs in CI, in order, in one namespace.

## Faker pools

<!-- derived-from: generation-methods sha256:1552dc309621 -->
<!-- derived-from: templates-and-examples sha256:fa66c7f7252b -->

Faker is slow per value; `RandSpecs.faker_pool` draws a pool once and returns a `distincts` spec.
Install the optional extra first: `pip install "rand-engine[faker]"`. It accepts a Faker provider
such as `name` or `email`, a locale (default `en_US`), a positive `pool_size` (default 100), and
an optional seed. The seed fixes the materialized pool, then NumPy samples that pool for every row.
Invalid pool sizes, unavailable Faker, unsupported locales/providers, provider failures and
non-scalar provider values raise `RandEngineError`.

```python
from rand_engine import DataGenerator, RandSpecs

name_spec = RandSpecs.faker_pool("name", locale="pt_BR", pool_size=500, seed=0)
people = DataGenerator({
    "name": name_spec,
    "email": RandSpecs.faker_pool("email", pool_size=500, seed=0),
}, seed=1).size(2_000).get_df()
assert people["name"].isin(name_spec["kwargs"]["distincts"]).all()

from rand_engine.validators.exceptions import RandEngineError

try:
    RandSpecs.faker_pool("name", pool_size=0)
except RandEngineError:
    pass
else:
    raise AssertionError("expected positive pool_size")
```

## Spec from an Arrow schema

<!-- derived-from: templates-and-examples sha256:fa66c7f7252b -->

`RandSpecs.from_schema` maps Arrow metadata to a validated RandSpec. Boolean fields become
`booleans(true_prob=0.5)`; integer fields become `integers(min=0, max=min(100, type maximum),
int_type=<Arrow type>)`; floating fields become `floats(0..1, decimals=2)`; string and large-string
fields become `uuid4`; date fields become `dates(2000-01-01..2030-12-31)`; timezone-naive timestamps
become second-resolution `dates`; string, large-string, date and timestamp fields generate `string[pyarrow]` columns; and null fields
become `constant(None)`, an `object` column. Nullable fields retain
the same recipe: Arrow nullability does not add a RandSpec modifier.

For an override, `kwargs` merge into the default recipe. An override containing `method` replaces
the whole field recipe. The builder refuses non-schemas, unknown fields, duplicate schema names,
non-dict overrides, unsupported Arrow families without a complete `method` replacement, and any
resulting invalid RandSpec with `SpecValidationError`.

```python
import pyarrow as pa
from rand_engine.validators.exceptions import SpecValidationError

schema = pa.schema([
    ("active", pa.bool_()), ("id", pa.int64()), ("score", pa.float64()),
    ("label", pa.string()), ("note", pa.large_string()), ("day", pa.date32()),
    ("at", pa.timestamp("s")), ("missing", pa.null()),
])
spec = RandSpecs.from_schema(schema, overrides={
    "score": {"kwargs": {"min": 0, "max": 10}},
    "label": {"method": "distincts", "kwargs": {"distincts": ["trial", "paid"]}},
})
df = DataGenerator(spec, seed=1).size(500).get_df()
assert list(spec) == list(schema.names) and df["score"].between(0, 10).all()
assert spec["label"] == {"method": "distincts", "kwargs": {"distincts": ["trial", "paid"]}}

try:
    RandSpecs.from_schema(pa.schema([("amount", pa.decimal128(10, 2))]))
except SpecValidationError:
    pass
else:
    raise AssertionError("expected unsupported Arrow type")

try:
    RandSpecs.from_schema(pa.schema([("id", pa.int32())]), overrides={"missing": {}})
except SpecValidationError:
    pass
else:
    raise AssertionError("expected unknown override")

```

## Ready-made specifications

`RandSpecs` is the top-level alias for `CommonRandSpecs`: its ten factories work with both
`DataGenerator` and `SparkGenerator`. `AdvancedRandSpecs` has ten factories for `DataGenerator`
only; they demonstrate correlated and template methods. Use the factory pages as a compact inventory,
then run a returned spec with the generator that family supports.

::: rand_engine.examples.common_rand_specs.CommonRandSpecs

::: rand_engine.examples.advanced_rand_specs.AdvancedRandSpecs

## Kafka or any queue

<!-- derived-from: data-generator sha256:511ff7f3a370 -->

`stream_dict` yields Python record dicts at a bounded rate; send them with your client.
After normalization, every microbatch uses pandas records so its public Python representation is
retained.

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

<!-- derived-from: writers-and-streaming sha256:194abd1a89af -->

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

<!-- derived-from: pk-fk-constraints sha256:324d5cb88eec -->

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
