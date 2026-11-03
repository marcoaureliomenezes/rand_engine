Use the rand-engine Python library to build a small synthetic people sample.

- 100 rows with two columns: `id` (an integer from 1 to 100000) and `score` (a float between 0 and 1, rounded to 3 decimals).
- Save the sample as `people.parquet` in the current directory.
- Write the code as a re-runnable script `solve.py` in the current directory, with a fixed seed, so running it again gives the same file.
- Import rand-engine only from its top-level package, never from its submodules.
- Make `solve.py` print the installed rand-engine version (`rand_engine.__version__`) when it runs.

Use only what the installed rand-engine package ships (docstrings, `help()`, `rand_engine/llms.txt`, the `rand-engine` CLI, its examples). You have no web access.
