# Lake

For data engineers who need related tables. It teaches `pk` and `fk`: orders point at customers, and a join proves every order finds its customer.

Get the file:

```bash
rand-engine get-started lake
```

It writes the file to the current directory. `--out DIR` writes it to `DIR` instead, created when missing. An existing file is never overwritten.

```python no-run
--8<-- "rand_engine/cases/lake.py.txt"
```

## What it shows

- **Describe**: the customers own a `pk`; the orders carry an `fk` that points at it.
- **Write**: each table lands as one Parquet file under `lake/`, in the directory the file runs in, and the relation is recorded.
- **Read back**: both tables are read from the lake and joined on the `fk`, then the counts are printed.

## Next steps

- [Writing files](../3_WRITING_FILES.md): the writer contract, batch and stream.
- [Data generator](../1_DATA_GENERATOR.md): `pk` and `fk` among the methods.
- [Reference](../reference.md): the `DataGenerator` API.
