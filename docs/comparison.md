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
