Use the Python library `rand-engine` (already installed) to generate fake customer data: an `age` column (whole numbers from 18 to 80), a `country` column (one of BR, US, DE) and an `amount` column (decimals from 1 to 500).

1. Write 1,000 rows as a gzip-compressed CSV file at `customers.csv.gz` in the current directory.
2. Write a short file stream of the same columns (10 rows per file, for about 1 second) into the directory `stream_out` in the current directory.

Both files must be written by rand-engine's own file writers (its batch file writer and its file-stream writer), not by pandas I/O.

Save one re-runnable Python script with a fixed seed in the current directory, `solve.py`, that produces both.
