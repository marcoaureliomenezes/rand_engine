# Faker

For anyone who needs realistic names, emails or cities at volume. It teaches `RandSpecs.faker_pool`: Faker draws a small pool once, and NumPy samples it into many rows.

## Prerequisite and run

Install the extra first:

```bash
pip install "rand-engine[faker]"
rand-engine get-started faker
python faker-example.py
```

The command writes `faker-example.py` to the current directory. `--out DIR` writes it to `DIR`
instead, created when missing. An existing file is never overwritten. Running it prints the first
rows of a 10,000-row DataFrame and the distinct-name count from the configured pool.

```python no-run
--8<-- "rand_engine/cases/faker.py.txt"
```

## What it shows

- **Install**: the file needs the `faker` extra; the install line is at the top of the file.
- **Pools**: `name` uses the `pt_BR` locale, and `email` and `city` use the default locale. Each pool has a size and a seed.
- **Sample**: 10 000 rows drawn from the pools and the native columns, then the head, and the number of distinct names against the pool size.

## Next steps

- [Recipes](../5_RECIPES.md): `faker_pool` beside `from_schema`, and the other recipes.
- [Reference](../reference.md): the `RandSpecs` API.
