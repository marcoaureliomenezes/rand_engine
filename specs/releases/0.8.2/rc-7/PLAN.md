# PLAN — Release: 0.8.2, candidate 7

**Status:** Draft
**Release ID:** 0.8.2
**Owner:** dd-sw-engineer-sr
**SPEC:** `rc-7/SPEC.md` (cfeed38)

Sources: as-is review `.dadaia/reports/rand-engine/2026-11-13T014103Z-dd-sw-engineer-sr-rc7-as-is-review.md`; the grill record `2026-11-14T000000Z-main-thread-rc7-grill.md` with its amendment; the SPEC's rulings. Tree `worktrees/rand-engine/0.8.2/rc-7/wt-rc`. Every `path:line` was re-read at `cfeed38` (the define commits touch only `specs/`; code equals `22fa076`): the §2 sweep prints 43 hits and `tests/test_docs.py` holds bare match asserts at `:88`, `:340` and `:888`. Open bug: `setuptools-ghsa-xmj3-open-on-master` only; it closes at the promote and no rc-7 file touches its pin. The bug window review is the SPEC's.

## 1. As-is review

Bug history = the ledger (`BUGS.jsonl` and `_archive/bugs_histo.jsonl`) plus `git log -E --grep '^(fix|refactor)\(bugs\): ' -- <file>`; none open on a unit below.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `rand_engine/file_handlers/file_handler.py` `_ACCEPTED`, `open_*`, `to_*`, `_to_file` (`:50,378-411`) | the format spelled in `_ACCEPTED`, three openers, three `to_*`, a `getattr` | 3 (`json-indent-writes-multiline-records`, `csv-tz-aware-fails-on-windows`, `writer-options-consumed-by-use`); REBUILDs 2a48173 and a46645f each followed by another drain on the same key | REBUILD | no owner of the key set; the third drain on the unit; net -31 production lines |
| `rand_engine/file_handlers/writer.py:30,33-40` `__map_methods`, `writer_method` | a third dict, name-mangled call | none | DELETE | the key set is `_SESSIONS` |
| `rand_engine/file_handlers/_writer_batch.py:291-311` `_open_session`, `:394` | a fourth dict and a dead refusal | `writer-options-consumed-by-use`, `writer-numfiles-rows-per-file` (resolved, KEEP) | REBUILD | the method shrinks to one call |
| `rand_engine/file_handlers/_writer_stream.py:63` | indexes `writer_method` | 3 writestream path bugs (resolved, KEEP) | UPDATE | one call |
| `tests/test_5_files_write_batch.py` 16 sites, `tests/test_docs.py:597` | call the deleted names | none | UPDATE | call shape only, asserts byte-identical (grill 3) |
| `tests/test_5_files_write_batch.py`, `tests/test_5_files_write_stream.py` | no unsupported-format case | none | ADD (RED) | one new contract: the refusal is reachable |
| `tests/test_docs.py:88,340,888` | bare match asserts | 4 test_docs bugs (KEEP) | UPDATE | a message each |
| `tests/integrations/test_public_api.py:905-921` | name, no ids, a conditional | `k-guard-test-runs-wsl-bash-on-windows` (KEEP) | UPDATE | items 1-3 |
| `tests/test_0_np_core.py:642,658`, `test_1_common_validator.py:749`, `test_2_data_generator.py:151,165,182` | one-row parametrize | none | UPDATE | plain cases |
| `tests/test_8_consistency.py:335,342` | docstrings cite absent units | none | UPDATE | text |
| `tests/integrations/test_eval_tasks.py:17-20,99,104,147,151,234` | module globals, shadowing locals, an overstated name | none | UPDATE (the load: REBUILD to a function) | items 7, 8 |
| `tests/integrations/test_eval_check.py:196-200` | a glob assert red only on a cold tree | rc-6 `run_script` fix (KEEP) | UPDATE (a deletion on the operator's order) | item 9 |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| which session class and options a write format has | `file_handler.py` `_SESSIONS` + class `ACCEPTED`, via `_session` | `FileHandler.open_session`, `FileHandler.to_file`, both writers, `test_docs.py` | `_ACCEPTED`, `open_*`, `to_*`, `_to_file`, `__map_methods`, `writer_method`, `_open_session`'s dict |
| the unsupported-format refusal | `_session` | both writers through `to_file` and `open_session` | `_writer_batch.py:305` |

## DAG

Waves are schedule waves; jobs of one wave write disjoint files. Tasks inside a job run in numeric order.

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `tests/integrations/test_public_api.py` |
| Job 2 | — | 1 | `tests/test_0_np_core.py`, `tests/test_1_common_validator.py`, `tests/test_2_data_generator.py`, `tests/test_8_consistency.py` |
| Job 3 | — | 1 | `tests/test_docs.py` |
| Job 4 | — | 1 | `tests/integrations/test_eval_tasks.py`, `tests/integrations/test_eval_check.py` |
| Job 5 | Job 3 | 2 | `rand_engine/file_handlers/file_handler.py`, `rand_engine/file_handlers/writer.py`, `rand_engine/file_handlers/_writer_batch.py`, `rand_engine/file_handlers/_writer_stream.py`, `tests/test_5_files_write_batch.py`, `tests/test_5_files_write_stream.py`, `tests/test_docs.py` |
| Reconciliation | Job 1 to Job 5 | 3 | `specs/memory/product/output/writers-and-streaming.md`, `specs/memory/product/catalog.json`, `CHANGELOG.md` |

Edge reason: `tests/test_docs.py` is in Job 3 (AC47.3) and Job 5 (AC45.5, the `:597` call shape); Job 5 branches after Job 3 merges.

### Schedule and sizing

- 8 tasks: Job 1 one (jr); Job 2 two (jr); Job 3 one (jr); Job 4 two (jr); Job 5 two (sr). 2 sr, 6 jr. Job 5 carries the one new behaviour, so its RED (J5.T1) precedes the REBUILD (J5.T2); the others are test hygiene with their asserts unchanged or a deletion the operator ordered.
- Net lines: J5.T2 deletes more `rand_engine/` lines than it adds (AC45.4); Job 1 adds one `ids=` line and one case; Job 4 nets 0..+2. A task that cannot hold its bound returns to the main thread.

## 2. Gates

The job gate is the repo's `verify:` line (`python scripts/ci.py job`), unchanged; no preflight, matrix or local gate is added. Each job's Done-when is `verify:` plus the test directories its change reaches (Job 5: with Java, for the three Spark rows of `tests/test_docs.py`). 8 task merges, 5 job merges and one `wt-rc` merge run the existing line.

## Acceptance map

| AC | owner task | implementation task |
|---|---|---|
| AC45.1 | J5.T1 | J5.T2 |
| AC45.2 | the existing `FileHandler`, batch and stream cases, asserts unchanged | J5.T2 |
| AC45.3, AC45.4 | no test; read on the diff | J5.T2 |
| AC45.5 | `test_docs.py::test_writing_doc_inventory_matches_the_accepted_writer_options`, unchanged | J5.T2 |
| AC46.1, AC46.2, AC46.3 | the K-guard cases | J1.T1 |
| AC47.1 | the six cases, asserts unchanged | J2.T1 |
| AC47.2 | no test; docstring text | J2.T2 |
| AC47.3 | the docs cases | J3.T1 |
| AC48.1, AC48.2 | the eval-task cases, asserts unchanged | J4.T1 |
| AC48.3 | the deletion, on the operator's order | J4.T2 |
| AC49.1, AC49.2, AC49.3 | no test | Reconciliation |

### Reconciliation (the rc's last commits, `RC-FLOW.md` step 4)

Order, `dd-product-engineer`: (1) `release.py phase CLOSURE`; (2) the memory pass from the final diff (AC49.1), then `catalog generate`; (3) the `CHANGELOG.md` bullet (AC49.2, SPEC open question 2); (4) the closure summary quoting the net lines of `rand_engine/` (AC49.3).
