# Scope comparison

rand-engine, [Faker](https://faker.readthedocs.io/en/stable/), and
[dbldatagen](https://github.com/databrickslabs/dbldatagen) overlap in synthetic-data work while
using different execution and deployment models. The table records only capabilities described by
the linked primary sources; it is not a ranking.

| Tool | Execution and output | Required input or optional source | Repeatability and relationships | Deployment |
|---|---|---|---|---|
| rand-engine | A declarative RandSpec runs through Python/NumPy/pandas `DataGenerator`, or a caller-supplied Spark session; it returns pandas frames, record streams, files, or Spark DataFrames. | A RandSpec is required; generation does not read a database. | A seed reconstructs stateless PK/FK values from definitions and row indexes. In Spark, an explicit seed controls keys only; ordinary Spark values remain unseeded. | Python with NumPy and pandas; Spark is optional. [Project source](https://github.com/marcoaureliomenezes/rand_engine/blob/master/README.md) |
| Faker | Calls a Python provider generator and can print repeated provider output through its CLI. | Typical examples create `Faker()`; dynamic providers can supply external elements. | `seed` and `seed_instance` repeat provider calls when methods and Faker version match. This page makes no multi-table relationship comparison for Faker. | Python package and CLI. [Faker documentation](https://faker.readthedocs.io/en/stable/) |
| dbldatagen | A code-defined specification builds a Spark SQL DataFrame and can use the Structured Streaming Rate source. | Ad-hoc specifications can run without an input dataset; its experimental analyzer can use a schema or source DataFrame. | Its documentation covers repeatable multi-table, CDC, merge and join scenarios with PK/FK consistency. | PySpark-compatible Spark/Databricks workflows, including notebooks and Delta Live Tables. [README](https://github.com/databrickslabs/dbldatagen) · [API reference](https://databrickslabs.github.io/dbldatagen/public_docs/reference/api/dbldatagen.data_generator.html) |

Use Faker for provider-oriented values, dbldatagen for its Spark/Databricks-oriented generation
workflows, and rand-engine where its RandSpec, stateless relations, pandas outputs, or optional
Spark facade fit the application. These descriptions identify overlap, not equivalent feature sets.

## rand-engine regression evidence

The [recorded results](BENCHMARKS.md) and [same-runner methodology](https://github.com/marcoaureliomenezes/rand_engine/blob/master/benchmarks/speed.py)
measure rand-engine base and head revisions under one runner. These are rand-engine regression
measurements, not a Faker or dbldatagen speed comparison.

## Bounded CI observations

The following observations come from one successful, validated [GitHub Actions
run](https://github.com/marcoaureliomenezes/rand_engine/actions/runs/39153239357)
at harness commit `bff8526cc6a5d76cb2cb8a454b69971cbf0876a5`. Its retained
[artifact](https://github.com/marcoaureliomenezes/rand_engine/actions/runs/39153239357/artifacts/12146450195)
contains the machine-readable record and derived summary. The artifact was 74,765 bytes, had
SHA-256 `6cd6cd39239839fc38b8d021c9bc19ea33b451d5f5db21f820ba55c0c3e90a0f`,
and is scheduled to expire on 2027-01-16T18:14:24Z; the raw values are retained here so the
observations do not depend on artifact access.

This was one GitHub-hosted Ubuntu/Linux x64 run (`GitHub Actions 1000038864`) on Python 3.12.15,
Java (version components: 17, 0, 20, 1), and Spark 3.5.8 in `local[8]`. It installed the public, non-editable
`rand-engine` 0.8.0 wheel (SHA-256
`db4422a43a20605babb369ac223d526e5607f6539f5056c5d277ead22ad173ba`) in an isolated
environment. The direct comparison pins were Faker 28.4.1, dbldatagen 0.4.0.post1, PySpark
3.5.8, NumPy 2.1.1, pandas 2.2.3, PyArrow 23.0.1, setuptools 83.0.0, jmespath 1.0.1, and
pyparsing 3.2.5.

Each side had one warm-up, then three timed samples in AB/BA/AB order. Setup, warm-up, and
output validation were outside the timed generation samples. For the Python workload,
`DataGenerator` and Faker were seeded with 42. For Spark, rand-engine's seed 42 controls its
key generation only; dbldatagen used `randomSeed=42` and `hash_fieldname`. The Spark payload
values are not claimed to repeat exactly across the two implementations.

The shared Python contract was exactly 100,000 dictionaries with `value: int` in 0..999999,
`tier: str` in `bronze`, `silver`, or `gold`, and `active: bool`. The timed rand-engine call was
`DataGenerator(...).get_df().to_dict("records")` followed by scalar normalization; Faker used
direct providers for the same fields. Validation of all 100,000 outputs was outside the clock.
`stream_dict` was not used.

The Spark contract built and fully evaluated 1,000,000 rows at eight partitions. Each timed call
built its frame, selected `xxhash64(ordinal, value, tier)`, then aggregated `count(*)` and the
hash sum with `collect()`. Both observed schemas were `ordinal: bigint` (not nullable),
`value: int` (nullable), and `tier: string` (nullable); the observed null counts were zero.
Validation also recorded ordinal range 0..999999, one million distinct ordinals, and the common
value and tier domains. The recorded physical plans show the hash consumes all three payload
columns, rather than only counting rows.

The immutable [runner](https://github.com/marcoaureliomenezes/rand_engine/blob/bff8526cc6a5d76cb2cb8a454b69971cbf0876a5/benchmarks/comparison.py),
[pinned requirements](https://github.com/marcoaureliomenezes/rand_engine/blob/bff8526cc6a5d76cb2cb8a454b69971cbf0876a5/benchmarks/comparison-requirements.txt),
and [workflow](https://github.com/marcoaureliomenezes/rand_engine/blob/bff8526cc6a5d76cb2cb8a454b69971cbf0876a5/.github/workflows/comparison.yml)
at that harness commit provide the exact invocation. The workflow installs the public wheel in an
isolated environment and runs the harness from outside the checkout with that environment's
interpreter.

| Workload | Contract and validation | Timed samples in seconds | Median in seconds |
|---|---|---|---|
| Python: rand-engine | 100,000 materialized dictionaries with `value`, `tier`, and `active`; validation passed | 0.16667477599999359, 0.15877993899999865, 0.15641291299999693 | 0.15877993899999865 |
| Python: Faker | 100,000 materialized dictionaries with `value`, `tier`, and `active`; validation passed | 0.7647746930000068, 0.7687502190000117, 0.7753420730000045 | 0.7687502190000117 |
| Spark: rand-engine | 1,000,000 fully evaluated rows with `ordinal`, `value`, and `tier` at eight partitions; validation passed | 1.831968039000003, 1.340617297999998, 1.2995347960000032 | 1.340617297999998 |
| Spark: dbldatagen | 1,000,000 fully evaluated rows with `ordinal`, `value`, and `tier` at eight partitions; validation passed | 0.9171129059999998, 0.3948988709999952, 0.5162802759999892 | 0.5162802759999892 |

| Separate observed cost | Seconds |
|---|---:|
| Workflow environment creation | 3.162337567 |
| Isolated harness installation | 32.132155979 |
| Workflow bounded-observation step | 59.837671308 |
| Whole Actions job | 103 |
| Python workload setup / validation | 0.38064580299999307 / 0.3279378719999926 |
| Spark workload setup / validation | 3.1340523949999977 / 32.52120048800002 |

These observations apply only to these two contracts, pins, runner, and three-repetition run.
They are not production-throughput measurements or claims of universal speed, adoption, causal
architecture, or statistical ranking. No winner is inferred.
