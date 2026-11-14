# SPEC — Release: 0.8.2, candidate 8 (the rc-7 closure drain: test hygiene 4, the writer Raises sections)

**Status:** Approved
**Release ID:** 0.8.2
**Owner:** dd-product-engineer
**Opened:** 2026-11-14
**Origin:** backlog:test-hygiene-4,writer-raises-docstrings

- The operator ratified both entries as rc-8's whole scope: "Ratificar as duas (Recommended)" (2026-11-14, `0.8.2-rc4-intake.md`, section "Operator ruling, 2026-11-14 (AskUserQuestion) — rc-8 drain"), intake rows 204, 205, 206, 208, 209, 211, 213, 214 and 215; the drain-lane review added rows 219 (the second `prototype` name) and 220 (the other refusals the Raises sections omit).
- Grill ruling 3 widens row 213 from `tests/test_docs.py:594` to the 13 plain dead imports the F401 sweep finds: `tests/test_docs.py:594`, `tests/test_1_advanced_validator.py:17`, `tests/test_2_data_generator.py:6`, `tests/test_5_files_write_batch.py:10,11`, `tests/test_5_files_write_stream.py:8`, `tests/fixtures/f1_right_specs.py:2,3`, `tests/fixtures/f2_templates.py:1`, `tests/fixtures/f2_spark_generator_specs_right.py:118,133,154` and `benchmarks/comparison.py:12`.
- No behaviour of `rand_engine` changes: rc-8 touches tests, test names, two docstrings of `rand_engine` and one benchmark import. No CHANGELOG bullet; the closure needs a memory pass record and a summary only.
- The open CRITICAL `setuptools-ghsa-xmj3-open-on-master` closes at the 0.8.2 promote (the `master` merge), outside rc-8 (grill ruling 10).
- Sources: the grill record `2026-11-14T122500Z-main-thread-rc8-grill`; the as-is review `2026-11-14T122244Z-dd-sw-engineer-sr-rc8-as-is-review`. Every `path:line` is a `dea4f23` anchor; the PLAN re-greps each one.
- FR numbers continue the release: rc-8 owns FR50–FR54. Not an ADR: every change is reversible and no public name changes.

### Rulings, verbatim

| ruling | answer | meaning |
|---|---|---|
| The drain (operator) | "Ratificar as duas (Recommended)" | the two Origin entries are rc-8's whole scope |
| Grill 1 (main thread) | "the three renames as the as-is gives them — `test_pk_permuted_heads_are_pinned_by_domain_and_key`, `test_fk_heads_are_pinned_by_seed_and_skew`, `test_json_undocumented_option_raises_before_writing`. Rows, bodies and asserts unchanged." | AC50.1 |
| Grill 2 (main thread) | "the as-is's exact text for `tests/test_8_consistency.py:335` and `:342`" | AC50.2 |
| Grill 3, Q2 (main thread) | "the sweep rule extends row 213 to the full set of 13 plain dead imports (12 under `tests/`, `benchmarks/comparison.py:12`); the SPEC Origin and ACs name them" | AC51.1 |
| Grill 4, Q3 (main thread) | "the 54 `tests.fixtures.*` F401 hits stay … Record only; no `noqa`, no ruff rule is added" | AC51.2, Non-goals |
| Grill 5, Q4 (main thread) | "one `load_by_path(name, path)` in the existing `tests/conftest.py` replaces the four load-by-path blocks (measured +21/-25); no new file" | AC52.1 |
| Grill 6, row 205 (main thread) | "the refusal parametrize on one line, the as-is's exact text" | AC52.2 |
| Grill 7, Q5 (main thread) | "the `save` and `start` Raises sections name every writer-owned `RandEngineError` refusal the as-is traced, in call order; `OSError`-family, `TypeError` and generation-stage errors stay unnamed, as `get_df` does. Docstring text only, a `docs(...)` commit, checked by the repo's own `ruff check --select D`." | FR53 |
| Grill 8, row 206 (main thread) | "close the row as a record, net 0 … the operator decides at the SPEC approval; the SPEC is written without the split" | Non-goals; Open question 1 |
| Grill 9 (main thread) | "three jobs, one wave, disjoint write sets; J1.T4 exists only if the operator orders the split" | §5 |
| Grill 10 (main thread) | "stays a promote-time close, stated in the SPEC Origin" | the Origin bullet above |

## Bug window review

Prior candidate: rc-7. Its window review found no fix in rc-6's window. No bug was resolved or registered since: `git log 22fa076..dea4f23 -- specs/bugs` prints nothing. One bug is open: `setuptools-ghsa-xmj3-open-on-master` (CRITICAL), outside rc-8. No open or resolved bug sits on a unit rc-8 touches (as-is §3).

| bug | fix | pattern hit | verdict | why |
|---|---|---|---|---|
| none | — | — | — | no fix landed in rc-7's window |

## 1. Problem

- Three test names cite a unit the tree no longer holds:
  - `tests/test_8_consistency.py:63` `test_pk_permuted_matches_the_prototype_feistel` and `:334` `test_fk_matches_the_prototype_parent_index` name a prototype (row 204, row 219);
  - `tests/test_5_files_write_batch.py:304` `test_to_json_undocumented_option_raises_before_writing` names `FileHandler.to_json`, which rc-7 deleted (row 214).
- Two docstrings in `tests/test_8_consistency.py` claim more than the body runs:
  - `:335` says the case pins "the feistel permutation", while the skew=0 row (`:333`) never reaches `_feistel` (`rand_engine/core/_keys.py:122-125`) (row 208);
  - `:342` gives a reason, "n unclamped would hang the Feistel cycle-walk", that the body (only `_zipf_rank`) does not run (row 209).
- 13 imports are dead (F401, each name used 0 times in its file): the Origin list (row 213, grill ruling 3). `ruff check --select F401 --no-cache --isolated tests evals benchmarks scripts` prints 67 hits at dea4f23: those 13 and 54 `tests.fixtures.*` fixture registrations.
- Four test files load an `evals/` script by path, each with its own copy of the `spec_from_file_location` / `module_from_spec` / `exec_module` block: `tests/integrations/test_eval_tasks.py:19-23`, `test_public_api.py:686-692`, `test_eval_check.py:42-46`, `test_eval_gate.py:16-20` (row 211).
- The K-guard refusal parametrize, `tests/integrations/test_public_api.py:920-922`, spans three lines (row 205).
- The `save` (`rand_engine/file_handlers/_writer_batch.py:355-358`) and `start` (`rand_engine/file_handlers/_writer_stream.py:79-82`) Raises sections name only the size refusals; both methods also raise `RandEngineError` for an unsupported format, an undocumented option and a refused option value, `save` for the SQLite and append refusals, and `start` for `sqlite` (rows 215, 220; as-is §1.2).

## 2. Measurable goals

- `git grep -nIE 'prototype|to_json_undocumented|[Ff]eistel|cycle-walk' -- tests` prints nothing (5 hits at dea4f23).
- `ruff check --select F401 --no-cache --isolated tests evals benchmarks scripts` prints 54 hits, every one a `tests.fixtures.*` import (67 at dea4f23).
- `git grep -nE 'spec_from_file_location|module_from_spec' -- tests` prints hits in `tests/conftest.py` only (8 hits in four files at dea4f23).
- `python -m pytest -q -p no:cacheprovider --collect-only tests/` prints the count it prints at dea4f23 in the same environment (`1817/1825 tests collected (8 deselected)` in the shared venv, measured 2026-11-14): no case is added or removed.
- `git diff dea4f23 -- rand_engine` changes only lines inside the `Raises` sections of `save` and `start`.
- Every Origin item lands, or Non-goals names it.

### Wave ranking

| wave | scope | FRs |
|---|---|---|
| 1 — law, skills and dev loop | none | — |
| 2 — shared foundation | none | — |
| 3 — features and bugs | test names and docstrings, dead imports, the one loader, the writer Raises sections | FR50, FR51, FR52, FR53 |
| 4 — promote-facing | closure | FR54 |

## 3. Non-goals

- Any behaviour of `rand_engine`: no code line outside the two Raises sections changes.
- The 54 `tests.fixtures.*` F401 hits: pytest resolves a fixture by name from the test module, and three `create_output_dir` imports feed `base_path_files_test` (`tests/fixtures/f3_integrations.py:27`); no `noqa`, no ruff rule, F401 is not added to the `verify:` line (grill ruling 4).
- Row 206, `tests/test_benchmarks.py:326` (`-9 if os.name != "nt" else 1`): the conditional encodes a platform fact (POSIX SIGKILL is -9; Windows `Popen.kill` is `TerminateProcess(1)`), closed as a record (grill ruling 8). Open question 1.
- The other platform conditionals the as-is judged (`test_public_api.py:919,929` POSIX `skipif`, the `hasattr` feature checks, the Spark environment setup, the simulated `ntpath`): KEEP.
- Naming the not-`RandEngineError` errors in the Raises sections (`OSError` family, `TypeError` for a non-numeric `timeout` or trigger frequency) and the generation-stage errors (grill ruling 7); the defensive `indeterminate` and `append did not create its destination` refusals the as-is could not reach.
- A non-numeric `timeout` or trigger frequency raising `TypeError` in the stream writer: intake (row 221), outside rc-8.
- Docstrings for `FileHandler.open_session`, `to_file` and `handle_path`: internal helpers outside the `verify:` line's `ruff --select D` list.
- Records with no work: rows 207, 210, 212, 216, 217; row 218 is library intake.
- A CHANGELOG bullet, a PyPI publish or a tag of 0.8.2; closed-candidate text stays history.

## 4. Requirements

### FR50 — Test names and docstrings state what the case pins (`test-hygiene-4` items 1, 2, 5, 6; rows 204, 219, 214, 208, 209)

- AC50.1 (no test; a rename, asserts unchanged; grill ruling 1): `tests/test_8_consistency.py:63` is `test_pk_permuted_heads_are_pinned_by_domain_and_key`, `:334` is `test_fk_heads_are_pinned_by_seed_and_skew`, and `tests/test_5_files_write_batch.py:304` is `test_json_undocumented_option_raises_before_writing`; their parametrize rows, bodies and asserts are byte-identical. `git grep -nwE 'test_pk_permuted_heads_are_pinned_by_domain_and_key|test_fk_heads_are_pinned_by_seed_and_skew|test_json_undocumented_option_raises_before_writing' -- tests` prints 3 lines, one per definition.
- AC50.2 (no test; docstring text; grill ruling 2): the docstring at `tests/test_8_consistency.py:335` is `"""Pins the gen_fk heads by seed and skew: the parent index and the seed crc32(key_seed/column/canonical kwargs)."""`, and the one at `:342` is `"""Pins the top-of-domain rank literal: at u = 1 - 2**-53 the rank stays inside [0, n)."""`.
- AC50.3 (no test; a sweep on the diff): `git grep -nIE 'prototype|to_json_undocumented|[Ff]eistel|cycle-walk' -- tests` prints nothing. The word "prototyping" in `tests/integrations/test_public_api.py:99` is spec prose under test and does not match.

### FR51 — No dead import in tests or benchmarks (`test-hygiene-4` item 8, row 213; grill rulings 3 and 4)

- AC51.1 (no test; deletions only; the reach is run): the 13 imports of the Origin list are deleted, each line whole, except `tests/fixtures/f1_right_specs.py:3`, which keeps `datetime as dt` and drops `timedelta`; the blank line `tests/test_docs.py:595` goes with its import. `ruff check --select F401 --no-cache --isolated tests evals benchmarks scripts` prints 54 hits, every one naming a `tests.fixtures.` module. The files that import from the touched fixture modules pass unchanged, the Spark cases of `tests/test_3_spark_generator.py` with Java.
- AC51.2 (no test; read on the diff): no `noqa` comment is added, and `pyproject.toml` and the `verify:` line are unchanged.

### FR52 — One loader for scripts loaded by path; the one-line K-guard parametrize (`test-hygiene-4` items 3, 7; rows 211, 205)

- AC52.1 (integration, `tests/integrations` passes with every assert unchanged; grill ruling 5): `tests/conftest.py` holds one `load_by_path(name, path)` that loads the file at `path` as module `name` and returns it; the four blocks of §1 call it, through `from tests.conftest import load_by_path`, and keep their own wrapper names (`_load_eval_run`, `_load_run`, the `check` fixture, `load_gate`). `git grep -nE 'spec_from_file_location|module_from_spec' -- tests` prints hits in `tests/conftest.py` only, and `git grep -n 'importlib.util' -- tests/integrations` prints nothing. No file is added. `git diff --numstat dea4f23 -- tests/conftest.py tests/integrations` deletes more lines than it adds (as-is prototype: +22/−28 with AC52.2).
- AC52.2 (integration; one line; grill ruling 6): `tests/integrations/test_public_api.py:920-922` becomes the one line `@pytest.mark.parametrize("k", ["4", "0", "-1", "abc", "", "2.5"], ids=["k4", "k0", "k-1", "kabc", "kempty", "k2.5"])`; the POSIX `skipif` above it and the case body are unchanged.

### FR53 — The `save` and `start` Raises sections name every writer-owned refusal (`writer-raises-docstrings`, rows 215, 220; grill ruling 7)

- AC53.1 (no test; docstring text, checked by `ruff check --select D` and read on the diff): `FileBatchWriter.save`'s `Raises` section (`_writer_batch.py:355-358`) keeps its size sentence and names, in call order, each `RandEngineError` it raises: an unsupported format (not `csv`, `json`, `parquet` or `sqlite`); an option not documented for the format; a refused option value (csv `index`, `sep` or `compression`; json `orient` or `compression`; parquet `compression`); for SQLite a missing or invalid `table`, any other option, a mode other than `overwrite` or `append`, an append schema mismatch, a failed write; a csv or parquet column that mixes types; and on append a parquet schema mismatch, a `numFiles` destination that is not a directory, a zip output not holding exactly one file.
- AC53.2 (no test; as AC53.1): `FileStreamWriter.start`'s `Raises` section (`_writer_stream.py:79-82`) keeps its size sentence and names: `sqlite` (batch only); an unsupported format (not `csv`, `json` or `parquet`); an undocumented option (`numFiles` and `maxRowsPerBatch` are batch options); a refused option value (the same list as AC53.1); a csv or parquet column that mixes types.
- AC53.3 (no test; the gate and a diff read): `ruff check --select D rand_engine/file_handlers/_writer_batch.py rand_engine/file_handlers/_writer_stream.py` prints `All checks passed!`; `git diff dea4f23 -- rand_engine` adds lines only inside the two `Raises` sections, removes none, and changes no other file. The as-is's proposed text (+3 lines `save`, +2 `start`) is the reference; the commit is a `docs(...)` commit. `tests/test_docs.py` passes unchanged.

### FR54 — Closure: the memory pass record and the summary

- AC54.1 (closure memory pass, `pe`, from the final diff): `release.py memory` records the pass over rc-8's diff. No behaviour changes, so an atom changes only if it misstates a refusal the Raises sections now name (`specs/memory/product/output/writers-and-streaming.md` is read against AC53.1-AC53.2); `catalog.json` is regenerated only when an atom changes.
- AC54.2 (no test): no `CHANGELOG.md` edit.
- AC54.3 (no test; rc-8's closure summary): it quotes the net lines of the candidate (`git diff --numstat dea4f23..HEAD -- . ':!specs'`) and the collected-test count of §2.

## Replaces

- The three test names of AC50.1 → their new names. Consumers: none outside `specs/backlog/BACKLOG.json` (as-is §1.1: `git grep -nE "matches_the_prototype|to_json_undocumented"`).
- The two overclaiming docstring clauses → AC50.2.
- The 13 dead imports → deleted (AC51.1).
- The four inline load-by-path blocks → `tests/conftest.py` `load_by_path` (AC52.1).
- The three-line K-guard parametrize → one line (AC52.2).
- No product behaviour is replaced: the Raises sections grow by text only (FR53).

## 5. Constraints and risks

| risk | control |
|---|---|
| A deleted fixture-module import was a side-effect registration | AC51.1 deletes only names used 0 times (`git grep -nw` per file), the 54 `tests.fixtures.*` hits stay, and the job's gate runs the touched files' importers, the Spark ones with Java |
| `tests/integrations` imports `tests.conftest` | five test files already import from it (`natural_datetime_unit`, `ARROW_CONF`); AC52.1 adds no file |
| The `verify:` line runs `ruff check --select D` on both writers | AC53.3 runs it on both files |
| The Spark trial of `tests/integrations` fails on `py4j` without Java (as-is §1.5) | the loader job's gate runs it with `JAVA_HOME` set |
| A path under `tests/` lands only in a `test(...)` commit (`tests: tests/*`) | the fixture files and `tests/conftest.py` ride `test(...)` commits; `benchmarks/comparison.py` and the writer docstrings do not |

Jobs (grill ruling 9): three jobs in one wave, disjoint write sets — names, docstrings and dead imports under `tests/` (FR50, FR51 but `benchmarks/comparison.py`); the loader and the parametrize (FR52); the writer Raises sections and `benchmarks/comparison.py:12` (FR53, AC51.1's last line).

## 6. Open questions

For the main thread and the operator; none blocks the PLAN.

1. **Row 206, `tests/test_benchmarks.py:326`.** The operator decides at approval whether to order the two-row split with `skipif` (`pytest.param(-9, marks=skipif(os.name == "nt", …))` and `pytest.param(1, marks=skipif(os.name != "nt", …))`, net +3 lines). Main-thread position: no split; the row is a record (grill ruling 8). If ordered, J1.T4 exists, the split's `test(` commit quotes the order, and §2's collected count rises by one (two rows replace one case, one skipped per platform).
