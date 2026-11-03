Use the rand-engine Python library to build a synthetic users dataset.

- 500 rows with the columns `age` (an integer from 18 to 80), `salary` (a float between 30000 and 120000) and `salary_k` (the salary in thousands).
- About 10% of the `age` values must be missing (null).
- Save the dataset as `users.parquet` in the current directory.
- Write the code as a re-runnable script `solve.py` in the current directory, with a fixed seed, so running it again gives the same file.

Use only what the installed rand-engine package ships (docstrings, `help()`, `rand_engine/llms.txt`, the `rand-engine` CLI, its examples). You have no web access.
