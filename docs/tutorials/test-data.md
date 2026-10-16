# Test data

For pipeline tests that need a DataFrame with nulls and extreme values. It teaches `null_rate` and `anomaly_rate` on a column.

Get the file:

```bash
rand-engine get-started test-data
```

It writes the file to the current directory. `--out DIR` writes it to `DIR` instead, created when missing. An existing file is never overwritten.

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
