# Job 1 — README and agent entry point

**Status:** Approved
**done:** true

## Stage J1.S1 — RED

- Contract: exit tests execute every README Python block and resolve every README/`llms.txt` link; envelope `tests/test_docs.py`; ACs AC7.2–AC7.5, AC8.4
- J1.S1.T1 — AC7.2–AC7.5, AC8.4 · `W:` `tests/test_docs.py` · owner `tests/test_docs.py` · add strict-xfail README execution and link cases; retain the existing docs assertions
  Superseded: the existing `tests/test_docs.py` already executes README blocks and resolves README/`llms.txt` links. Legacy T-070-9 supplied its RED evidence and implementation in `f713abb`, integrated through `9769777`; this stage added no tests or xfail markers.

## Stage J1.S2 — rebuild

- Contract: exit J1.S1 green and the DataFrame, Faker-pool, file, stream and related-table examples execute from a temporary directory; envelope `README.md`, `llms.txt`, `tests/test_docs.py`; ACs AC7.2–AC7.5, AC8.4
- [x] J1.S2.T1 — AC7.2–AC7.5, AC8.4 · `W:` `README.md`, `llms.txt`, `tests/test_docs.py` (RED marker lines only) · owner `tests/test_docs.py` · REBUILD the stale README and add the compact agent index; no hand-written timing or test count
  Done: legacy T-070-9 delivered the README and agent index; `c51ed75` completed the optional Faker installation instruction, reduced the example to 10,000 rows, and asserted 1,000 Parquet rows read back. Only `README.md` changed in J1.S2.T1.

## Stage J1.S3 — close

- Contract: exit documentation tests green and links resolved; envelope this file; ACs AC7.2–AC7.5, AC8.4
- [x] J1.S3.T1 — AC7.2–AC7.5, AC8.4 · `W:` this file (`done`) · owner `tests/test_docs.py`
  Done: this closure records the inherited implementation and superseded RED stage without claiming new acceptance tests.

## Evidence

- README execution at `c51ed75`: `tests/test_docs.py::test_readme_python_blocks_execute_in_order` — 1 passed in 0.62s, including Parquet read-back, with output in a temporary directory.
- J1.S2 stage gate at `c51ed75`, reported by the main thread: the full default suite — 686 passed, 8 deselected; existing documentation execution and link checks green.
