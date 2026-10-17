# Test data

For pipeline tests that need a DataFrame with nulls and extreme values. It teaches `null_rate` and `anomaly_rate` on a column.

## Prerequisite and run

Install `rand-engine`, then scaffold and run the file from the directory where it was written:

Get the file:

```bash
pip install rand-engine
rand-engine get-started test-data
python test-data-example.py
```

It writes `test-data-example.py` to the current directory. `--out DIR` writes it to `DIR` instead,
created when missing. An existing file is never overwritten. Running it prints a 1,000-row sample,
the null count for `amount`, and rows carrying the configured anomaly values.

```python no-run
--8<-- "rand_engine/cases/test-data.py.txt"
```

## What it shows

- **Describe**: `amount` carries `null_rate` and `anomaly_rate`, and `anomaly_values` lists the extreme values drawn in place of some rows.
- **Generate**: `DataGenerator` with a seed builds 1 000 rows into `df`; the same seed gives the same rows on every run.
- **Look**: the first rows, the count of nulls in `amount`, and the anomalous rows.

## Next steps

- [Data generator](../1_DATA_GENERATOR.md): every method, and the null and anomaly rates.
- [Reference](../reference.md): the `DataGenerator` API.
