# Test Rules — rand-engine

These rules govern everything under `tests/`; slop: `dd-code-review` SLOP.md and `specs/memory/QUALITY.md`.

## Layout

- One pytest suite: numbered files `test_<n>_<area>.py`, by layer — 0 core methods, 1 validators, 2 `DataGenerator`, 3 Spark and advanced specs, 4 example specs, 5 batch and stream writers, 6 `stream_dict`, 7 templates, 8 the `pk`/`fk` relations contract.
- `tests/integrations/test_public_api.py` owns the public import surface; `test_benchmarks.py` the FR11 script; `test_docs.py` the docs contract (fenced blocks executed, README and `llms.txt` links resolve).
- Specs under test live in `tests/fixtures/f<n>_*.py` (`fixtures_templates.py` is the exception: an orphan no test imports, and it cannot be imported); Spark tests skip when PySpark is absent or on Windows with Python 3.12+.
- A new test goes into the file that owns its area; a new file only when no file owns it.

## Law

- A test asserts behaviour on literal expected values, never values computed by the code under test, never text or counts of the source.
- Relations are asserted on the output read back (frame, file, stream records), never on the run alone.
- A default test generates at most 10^4 rows; a larger one carries `@pytest.mark.stress`, deselected by default and run only in the CI `benchmarks` job.
- No benchmark or timing assert in the default suite; speed is measured only by `benchmarks/speed.py` in CI.
- Golden seeded outputs (`test_2_data_generator.py`) change only deliberately: the commit that changes generation output rewrites the golden in the same commit, its body stating why.
- A fix adds a new case; it never rewrites an old assert.
- Mock only boundaries; writer tests write under `tmp_path`.

## Run

```bash
PYTHONDONTWRITEBYTECODE=1 poetry run pytest tests/ -q -p no:cacheprovider
```
