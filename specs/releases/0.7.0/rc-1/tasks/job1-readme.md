# Job 1 — README and agent entry point

**Status:** Approved

## Stage J1.S1 — RED

- Contract: exit tests execute every README Python block and resolve every README/`llms.txt` link; envelope `tests/test_docs.py`; ACs AC7.2–AC7.5, AC8.4
- J1.S1.T1 — AC7.2–AC7.5, AC8.4 · `W:` `tests/test_docs.py` · owner `tests/test_docs.py` · add strict-xfail README execution and link cases; retain the existing docs assertions

## Stage J1.S2 — rebuild

- Contract: exit J1.S1 green and the DataFrame, Faker-pool, file, stream and related-table examples execute from a temporary directory; envelope `README.md`, `llms.txt`, `tests/test_docs.py`; ACs AC7.2–AC7.5, AC8.4
- J1.S2.T1 — AC7.2–AC7.5, AC8.4 · `W:` `README.md`, `llms.txt`, `tests/test_docs.py` (RED marker lines only) · owner `tests/test_docs.py` · REBUILD the stale README and add the compact agent index; no hand-written timing or test count

## Stage J1.S3 — close

- Contract: exit documentation tests green and links resolved; envelope this file; ACs AC7.2–AC7.5, AC8.4
- J1.S3.T1 — AC7.2–AC7.5, AC8.4 · `W:` this file (`done`) · owner `tests/test_docs.py`
