# Keys — related tables with `pk` and `fk`

Relations are two column methods. A `pk` value is a pure function of its kwargs and the row index;
an `fk` value is a function of its parent's `pk` definition, the generator seed and the row index.
Nothing is stored between generators: the child rebuilds parent keys from the parent's spec.

```python
from rand_engine import DataGenerator

customer_id = {"method": "pk", "kwargs": {"start": 1}}

customers = DataGenerator({
    "customer_id": customer_id,
    "city": {"method": "distincts", "kwargs": {"distincts": ["Rio", "Recife"]}},
}, seed=1).size(1_000).get_df()

orders = DataGenerator({
    "order_id": {"method": "pk", "kwargs": {"start": 1}},
    "customer_id": {"method": "fk", "kwargs": {"parent": customer_id, "parent_size": 1_000}},
}, seed=2).size(2_000).get_df()

assert customers["customer_id"].is_unique
assert orders["customer_id"].isin(customers["customer_id"]).all()
```

## `pk`

| kwarg | Default | Meaning |
|---|---|---|
| `style` | `"sequence"` | `"sequence"`: `start + i * step`; `"permuted"`: `start` + a bijection of `i` over `[0, domain)` |
| `start` | `0` | first value / offset |
| `step` | `1` | `sequence` only; never `0` |
| `domain` | — | `permuted` only, required, in `[1, 2**62]`; row indices must stay below it |
| `key` | `0` | `permuted` only; another `key` gives another order |
| `format` | — | renders each value with `str.format`; exactly one integer field, e.g. `"C-{:06d}"` |

`i` is the row index. Both styles are unique by construction, and neither depends on the seed.

```python
spec = {
    "seq": {"method": "pk", "kwargs": {"start": 100, "step": 10}},
    "shuffled": {"method": "pk", "kwargs": {"style": "permuted", "domain": 1_000, "key": 7}},
    "code": {"method": "pk", "kwargs": {"start": 1, "format": "C-{:06d}"}},
}
df = DataGenerator(spec, seed=1).size(1_000).get_df()
assert df["seq"].tolist()[:3] == [100, 110, 120]
assert sorted(df["shuffled"]) == list(range(1_000))
assert df["code"].iloc[0] == "C-000001"
assert DataGenerator(spec, seed=99).size(1_000).get_df().equals(df)
```

## `fk`

| kwarg | Meaning |
|---|---|
| `parent` | the parent's `pk` column spec, exactly as the parent declares it |
| `parent_size` | number of parent rows to pick from (row indices `0 … parent_size-1`); at most a permuted parent's `domain` |
| `skew` | `0` (default): uniform; `> 0`: Zipf with exponent `skew`, the hot parents scattered rather than the first rows |

The child must use the parent's exact `pk` kwargs (`format` included) and a `parent_size` no larger
than the rows the parent generated, or its keys point at rows that do not exist.

```python
parent = {"method": "pk", "kwargs": {"style": "permuted", "domain": 10_000, "format": "P{:05d}"}}
products = DataGenerator({"product_id": parent}, seed=1).size(200).get_df()

sales = DataGenerator({
    "product_id": {"method": "fk", "kwargs": {"parent": parent, "parent_size": 200, "skew": 1.2}},
}, seed=5).size(4_000).get_df()

assert sales["product_id"].isin(products["product_id"]).all()
top_share = sales["product_id"].value_counts().iloc[0] / len(sales)
assert top_share > 1 / 200 * 10  # a few parents take most of the rows
```

## Streams and multi-file writes continue the row index

Each microbatch of `stream_dict`, `writeStream`, and each part of `write` with `numFiles` starts at
the row index where the previous one ended, so `pk` values never repeat across batches.

```python
from itertools import islice

stream = DataGenerator({"event_id": {"method": "pk", "kwargs": {"start": 1}}}, seed=1).size(10)
records = list(islice(stream.stream_dict(min_throughput=500, max_throughput=1000), 25))
assert [r["event_id"] for r in records] == list(range(1, 26))
```

## Spark

`SparkGenerator` refuses `pk` and `fk` with a `SpecValidationError`: keys run on the NumPy engine only.
Generate the keyed tables with `DataGenerator` and hand them to Spark with `spark.createDataFrame`.
