Use the rand-engine Python library to generate synthetic tables from its ready-made customer and order templates, and a list of cities.

- `customers.parquet`: 200 customer rows.
- `orders.parquet`: 1000 order rows.
- `cities.parquet`: 500 rows with one column `city`, each value drawn from a pool of 50 realistic fake US city names built with the Faker library (locale en_US, seed 7).
- Write the code as a re-runnable script `solve.py` in the current directory, with a fixed seed, so running it again gives the same files.
- Save all three files in the current directory.

Use only what the installed rand-engine package ships (docstrings, `help()`, `rand_engine/llms.txt`, the `rand-engine` CLI, its examples). You have no web access.
