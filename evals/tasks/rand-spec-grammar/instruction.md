`spec.py` in the current directory defines `spec`, a `rand-engine` spec that does not build. Use the installed rand-engine, and the error it reports, to fix `spec.py`; keep its four columns `id`, `name`, `amount` and `status`.

Then write `make.py`, a re-runnable script with a fixed seed that builds a 1,000-row frame from `spec` with rand-engine and saves it as `out.parquet` in the current directory. Run it once so `out.parquet` exists.
