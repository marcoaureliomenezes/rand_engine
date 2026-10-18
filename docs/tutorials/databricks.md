# Databricks

For Spark and Databricks users. It teaches `SparkGenerator`, which builds a users table natively in Spark.

## Prerequisite and run

Use a Databricks runtime, or a machine with PySpark and Java available. `rand-engine` itself does
not install PySpark. Scaffold the file, then import it into Databricks or run it where that Spark
environment is already available:

Get the file:

```bash
pip install rand-engine
rand-engine get-started databricks
python databricks-example.py
```

It writes `databricks-example.py` to the current directory. `--out DIR` writes it to `DIR` instead,
created when missing. An existing file is never overwritten. The native path builds a 1,000-row
Spark DataFrame, then shows its first rows and schema; the final cell also shows the 100-row
pandas-to-Spark route.

```python no-run
--8<-- "rand_engine/cases/databricks.py.txt"
```

The file is in Databricks notebook source format: its first line is `# Databricks notebook source`, and its cells are separated by `# COMMAND ----------`. Import it into a Databricks workspace as a notebook, or run it with `python` where PySpark and Java are available.

## DataGenerator-only features

`SparkGenerator` accepts stateless `pk` and `fk` through the same key definitions as `DataGenerator`; an explicit seed applies to those key columns only. It still refuses the distributions (`exponential`, `lognormal`, `poisson`, `zipf`), `constant`, `null_rate` and `anomaly_rate`. For those, or for a small volume, generate with `DataGenerator` and wrap the pandas frame with `spark.createDataFrame`. The file's last cell does that for 100 rows.

## What it shows

- **Session**: the Spark session, the one the notebook already runs or the one created where there is none.
- **Describe**: the users spec, with supported methods only.
- **Generate**: 1 000 rows built natively into `df`, then shown with `show` and `printSchema`.
- **Small volume**: the `DataGenerator` path and `spark.createDataFrame`, beside the native `df`.

## Next steps

- [Spark generator](../2_SPARK_GENERATOR.md): the methods `SparkGenerator` supports and the refusals it raises.
- [Reference](../reference.md): the `SparkGenerator` API.
