# Job 8 — library test hygiene (wave 2)

Waits on Job 2 (`test_5_files_write_*.py`). Runs beside Jobs 6, 7 and 9. Test files only; asserts move or tighten, none is removed. `tests/AGENTS.md:8`'s "FR11" is a law line, not a test: T4's sweep excludes it and reports it to the main thread. Order: T1 then T5 (`test_docs.py`); T2 then T4 (`test_5_files_write_*.py`).

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J8.T1 | jr | AC36.1 | `tests/test_docs.py` | the page with front matter but no `description:` line (`:1044`) fails naming the page, not with `AttributeError` |
| J8.T2 | jr | AC36.2 | `tests/test_5_files_write_stream.py` | the unset-size test (`:136`) pins "No size set: call .size(n) with an int or a callable returning one." in full |
| J8.T3 | jr | AC36.4 | `tests/test_0_np_core.py` | the zero-size `uuid4` and `int_zfilled` partition (`:419-428`) moves into the owner contract tests (`:192-212`, `:398-413`) with ids naming the method; one assert goes red when `_np_core.py:103` is deleted (reviewer check) |
| J8.T4 | jr | AC36.3 | `tests/test_0_np_core.py`, `tests/test_1_advanced_validator.py`, `tests/test_1_common_validator.py`, `tests/test_2_data_generator.py`, `tests/test_2_data_generator_fails.py`, `tests/test_5_files_write_batch.py`, `tests/test_6_stream_objects.py`, `tests/test_8_consistency.py` | each docstring or comment that holds an AC, FR or bug id states the contract instead (`:180` of `_fails`, `:1` of `_batch` included). Sweep: `git grep -nE '[AF][CR][0-9]+' -- tests/ ':!tests/AGENTS.md'` prints nothing |
| J8.T5 | jr | AC36.5 | `tests/test_1_common_validator.py`, `tests/test_docs.py` | the aware-bound case (`:864-865`) builds its spec with `_date_spec` (`:284`), sits with the date-bound tests, named for its asserts; the dead `"indent"` literal (`test_docs.py:592`) goes |

Done when: `verify:`; the touched test files pass; the sweep prints nothing.
