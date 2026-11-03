Use the Python library rand-engine (already installed) to generate synthetic data for two related tables, with a fixed seed: 1,000 customers and 5,000 orders, where every order's `customer_id` references an existing customer.

Write them to `customers.parquet` and `orders.parquet` in the current directory (`customers.parquet` has exactly the column `customer_id`; `orders.parquet` has exactly `order_id` and `customer_id`; both keys are unique). Save the re-runnable script that builds them as `solve.py` in the current directory.

Use only what the installed rand-engine package ships (docstrings, `help()`, `rand_engine/llms.txt`, the `rand-engine` CLI, its examples). You have no web access.
