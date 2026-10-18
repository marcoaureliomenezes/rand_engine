# Compatibility, migration and recovery

## Choose an environment

`rand-engine` requires Python 3.10 or newer. Continuous integration currently tests Python
3.10 through 3.13; later Python releases may work, but are not part of that tested set.

```bash
pip install rand-engine
pip install "rand-engine[faker]"  # only for RandSpecs.faker_pool
```

The core install includes Python, NumPy and pandas generation. PySpark is deliberately a
caller-supplied dependency: use `SparkGenerator` only when your application already has a
Spark session and `pyspark.sql.functions`. Spark CI runs on Linux and macOS with Python
3.10–3.13 and on Windows with Python 3.10–3.11. It uses Java 17. On Windows with Python
3.12 or newer, use the pandas generator or a supported Spark/Python partition instead.

## Pick the generator

Use `DataGenerator` for seeded pandas DataFrames, record streams and files. The same spec,
seed and size reproduce its NumPy-generated frame; generated values still depend on the
installed NumPy version, RandSpec and requested batch/row bounds. Use `SparkGenerator` for
ordinary columns in an existing Spark job. Its seed controls only `pk` and `fk` key columns;
ordinary Spark columns remain unseeded.

`SparkGenerator` accepts ordinary methods, stateless keys, and `int_zfilled` lengths through
15. It refuses `uint64`, inclusive integer domains wider than `2**53`, NumPy-only
distributions such as `poisson`, and modifiers such as `null_rate`. The four correlated
methods `distincts_map`, `distincts_map_prop`, `distincts_multi_map`, and `complex_distincts`
are a special case: Spark warns and returns a NULL string column. They do not raise. See the
[Spark method table](2_SPARK_GENERATOR.md#methods) for the supported surface rather than
copying an exhaustive grammar into a job.

`int_zfilled` accepts an integer `length` from 1 through 18 in `DataGenerator`; invalid
lengths fail validation before generation. SQLite is one batch output table through
`write.format("sqlite")`; it is not a database lookup or a production database integration.
See [Writing files](3_WRITING_FILES.md#sqlite-table-sink) for its table, append and overwrite
semantics.

## Move from 0.7 to 0.8

Keep the supported imports:

```python
from rand_engine import DataGenerator, RandSpecs, SparkGenerator
```

Then run your existing RandSpecs through construction before a production job. Version 0.8
makes several invalid inputs fail earlier, including `int_zfilled` lengths outside 1..18.
Use the [errors guide](errors.md) to correct a complete validation report rather than retrying
one message at a time.

For new work, use the CLI starters and rendered reference: `rand-engine list` shows six
starters, of which five are runnable Python tutorials; `rand-engine get-started agent --out
PROJECT` writes an opt-in project context in 0.8.0. Spark `pk` and `fk` definitions now work
through the shared stateless key path. SQLite output is available through the batch writer,
and stream records retain their public Python values across the Arrow/pandas conversion choice.
Read the [changelog](https://github.com/marcoaureliomenezes/rand_engine/blob/master/CHANGELOG.md)
for the complete version history, including the distinct 0.7 migration changes.

## Recover from common symptoms

| Symptom | Cause | Recovery |
| --- | --- | --- |
| `faker` cannot be imported | Faker is optional. | Install `pip install "rand-engine[faker]"`, then rebuild the pool with `RandSpecs.faker_pool`. |
| Spark cannot start or Java is missing | Spark and its JDK are supplied by the caller. | Install/configure PySpark and a compatible Java runtime; use Java 17 for the tested setup, or use `DataGenerator` for a pandas path. |
| A Spark spec raises `SpecValidationError` | The method or boundary is unsupported by Spark. | Use the [Spark table](2_SPARK_GENERATOR.md#methods); generate the unsupported portion with `DataGenerator` and create a Spark DataFrame when that suits the workload. |
| A correlated Spark column is NULL | One of the four correlated methods is a warned placeholder in Spark. | Use `DataGenerator` for correlated values, or change the Spark spec to supported ordinary/key columns. |
| A RandSpec is invalid | Construction validates the whole spec. | Read every reported item and its corrected example, fix the spec, then construct a new generator. |
| A starter target already exists | Starters create files exclusively to protect project work. | Keep the existing file, choose a different `--out` directory, or review and merge the starter manually. |
