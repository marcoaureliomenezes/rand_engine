# PLAN — Release: 0.8.2, candidate 8

**Status:** Draft
**Release ID:** 0.8.2
**Owner:** dd-sw-engineer-sr
**SPEC:** `rc-8/SPEC.md` (95c1de1)

Sources: as-is review `.dadaia/reports/rand-engine/2026-11-14T122244Z-dd-sw-engineer-sr-rc8-as-is-review.md`; the grill record `2026-11-14T122500Z-main-thread-rc8-grill.md`; the SPEC's rulings. Tree `worktrees/rand-engine/0.8.2/rc-8/wt-rc`. Every `path:line` is a `dea4f23` anchor; the define commits touch only `specs/`. Open bug: `setuptools-ghsa-xmj3-open-on-master` only; it closes at the promote and no rc-8 file touches its pin. The bug window review is the SPEC's. Row 206 is out (SPEC open question 1): there is no J1.T4; if the operator orders the split at approval, the main thread amends this PLAN.

## 1. As-is review

Bug history = the ledger (`BUGS.jsonl` and `_archive/bugs_histo.jsonl`) plus `git log -E --grep '^(fix|refactor)\(bugs\): ' -- <file>`; none open on a unit below.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `tests/test_8_consistency.py:63,334,335,342` | two names cite `prototype`, two docstrings overclaim | none | UPDATE | names and clauses state what is pinned |
| `tests/test_5_files_write_batch.py:304`, `:10-11` | name cites the deleted `to_json`; `time`, `threading` unused | none | UPDATE / DELETE | one name, two dead imports |
| `tests/test_docs.py:594`, `tests/test_1_advanced_validator.py:17`, `tests/test_2_data_generator.py:6`, `tests/test_5_files_write_stream.py:8`, `tests/fixtures/f1_right_specs.py:2-3`, `tests/fixtures/f2_templates.py:1`, `tests/fixtures/f2_spark_generator_specs_right.py:118,133,154` | dead imports (F401, 0 uses) | none | DELETE | 12 lines |
| `benchmarks/comparison.py:12` | `import sys` unused | none | DELETE | 1 line |
| the 54 `tests.fixtures.*` F401 hits | fixture registrations by import | none | KEEP | pytest resolves a fixture by name; three feed `base_path_files_test` (grill 4) |
| `tests/test_benchmarks.py:326` | platform conditional expectation | none | KEEP | a real platform fact; a record (grill 8) |
| `tests/integrations/test_eval_tasks.py:19-26`, `test_public_api.py:686-692,920-922`, `test_eval_check.py:42-46`, `test_eval_gate.py:16-20` | four load-by-path blocks; a 3-line parametrize | `k-guard-test-runs-wsl-bash-on-windows` (resolved, KEEP) | REBUILD (loader) / UPDATE | one decider for loading a script |
| `tests/conftest.py` | hooks, fixtures, two helpers | none | ADD `load_by_path` | the one existing home, five test files already import from it; nothing else can carry it |
| `rand_engine/file_handlers/_writer_batch.py:355-358`, `_writer_stream.py:79-82` | Raises name only the size refusal | 7 resolved writer bugs, none on docstrings (KEEP) | UPDATE | docstring text only |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| how a test loads a script by path | `tests/conftest.py` `load_by_path` | the four integration test files | four inline blocks |
| which refusals `save` and `start` raise | the code; the Raises sections mirror it | the docs reference render | none |

## DAG

Waves are schedule waves; jobs of one wave write disjoint files. Tasks inside a job run in numeric order (Job 1: T2 waits on T1, both write `tests/test_5_files_write_batch.py`).

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `tests/test_8_consistency.py`, `tests/test_5_files_write_batch.py`, `tests/test_5_files_write_stream.py`, `tests/test_docs.py`, `tests/test_1_advanced_validator.py`, `tests/test_2_data_generator.py`, `tests/fixtures/f1_right_specs.py`, `tests/fixtures/f2_templates.py`, `tests/fixtures/f2_spark_generator_specs_right.py` |
| Job 2 | — | 1 | `tests/conftest.py`, `tests/integrations/test_eval_tasks.py`, `tests/integrations/test_public_api.py`, `tests/integrations/test_eval_check.py`, `tests/integrations/test_eval_gate.py` |
| Job 3 | — | 1 | `rand_engine/file_handlers/_writer_batch.py`, `rand_engine/file_handlers/_writer_stream.py`, `benchmarks/comparison.py` |
| Reconciliation | Job 1 to Job 3 | 2 | `specs/memory/product/output/writers-and-streaming.md`, `specs/memory/product/catalog.json` |

### Schedule and sizing

| job | task | who | net lines (def, return, blank counted) | shape |
|---|---|---|---|---|
| 1 | J1.T1 | jr | 0 (4 replaced lines in `test_8_consistency.py`, 1 in the batch file) | `test(J1.T1)` |
| 1 | J1.T2 | jr | -12 (docs -2, validator -1, data_generator -1, batch -2, stream -1, f1_right -1, f2_templates -1, f2_spark -3) | `test(J1.T2)` |
| 2 | J2.T1 | jr | -6 (+22/-28: conftest +9, four files +12/-25, parametrize +1/-3) | `test(J2.T1)` |
| 3 | J3.T1 | jr | +5 (+3 `save`, +2 `start`; 0 `def`, `return` or blank) | `docs(J3.T1)` |
| 3 | J3.T2 | jr | -1 | `chore(J3.T2)` |

- 5 tasks, all jr: every outcome is fully stated by its AC and `W:`; no behaviour changes, so no RED test exists (asserts unchanged, as rc-7 Jobs 1-4). rc net -14 lines, all under the ~100-line bound.
- A path under `tests/` goes only in a `test(...)` commit; `benchmarks/` and `rand_engine/` do not.

## 2. Gates

The job gate is the repo's `verify:` line (`python scripts/ci.py job`), unchanged; no preflight, matrix or local gate is added. Each job's Done-when is `verify:` plus the test directories its change reaches (Job 1 and Job 2: with `JAVA_HOME` set, for the Spark cases). 5 task merges, 3 job merges and one `wt-rc` merge run the existing line.

## Acceptance map

| AC | owner task | note |
|---|---|---|
| AC50.1, AC50.2, AC50.3 | J1.T1 | no test; names and docstrings, asserts byte-identical |
| AC51.1 | J1.T2 | the 12 imports under `tests/`; its last line, `benchmarks/comparison.py:12`, is J3.T2's |
| AC51.2 | J1.T2 | read on the diff |
| AC52.1, AC52.2 | J2.T1 | `tests/integrations` passes, every assert unchanged |
| AC53.1, AC53.2, AC53.3 | J3.T1 | no test; `ruff check --select D` and a diff read |
| AC54.1, AC54.2, AC54.3 | Reconciliation | |

### Reconciliation (the rc's last commits, `RC-FLOW.md` step 4)

Order, `dd-product-engineer`: (1) `release.py phase CLOSURE`; (2) the memory pass from the final diff (AC54.1), then `catalog generate` only if an atom changed; (3) the closure summary quoting the net lines and the collected-test count (AC54.3); no `CHANGELOG.md` edit (AC54.2).
