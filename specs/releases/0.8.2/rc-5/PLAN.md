# PLAN — Release: 0.8.2, candidate 5

**Status:** Draft
**Release ID:** 0.8.2
**Owner:** dd-sw-engineer-sr
**SPEC:** `rc-5/SPEC.md` (14e0362)

Sources: as-is review `.dadaia/reports/rand-engine/2026-11-11T135627Z-dd-sw-engineer-sr-rc5-as-is-review.md`; the grill record `2026-11-11T150000Z-main-thread-rc5-grill.md`; the SPEC's operator rulings. Tree `worktrees/rand-engine/0.8.2/rc-5/wt-rc`. Every `path:line` was re-read at `162fa1d` (the define commits touch only `specs/`). Open bugs: `setuptools-ghsa-xmj3-open-on-master` only; it closes at the `master` merge and no rc-5 file touches its pin. The bug window review is the SPEC's.

## 1. As-is review

Bug history = the ledger (`BUGS.jsonl` and `_archive/bugs_histo.jsonl`) plus `git log -E --grep '^(fix|refactor)\(bugs\): ' -- <file>`. Entry 4 is narrowed: no code edit on rows 27, 40, 80; item 5 (row 81) already holds and is dropped.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `tests/test_9_cli.py:156-205` starter cases (entry 1) | one test with a slug-branching `notebook` label, its own `ARROW_CONF` copy and tombstone asserts | none on the file | UPDATE | one rewrite into `(slug, expectation)` rows; tombstones KEEP until after the ship |
| library tests, 11 sites (entry 2) | ids in docstrings, loose matches, standalone tests | owners' bugs only, none on these asserts | UPDATE | each fix tightens an owner test; only `test_0_np_core.py:419-428` adds an assert |
| `tests/integrations/test_eval_tasks.py` and its neighbours (entry 3) | 13 reference trials, env built 3 times, a mock at `test_public_api.py:853` | `test_public_api.py` 4 bugs, none on these lines | UPDATE | one trial per slug is the only cost item; one case added carries its own deletion (`:52-55`) |
| `evals/_check.py`, `run.py`, `gate.py`, `eval.yml`, `README.md` (entry 4) | 272-line helper: SHIM source, `read_artifact`, `value_hash`, `provenance` | `_check.py` 7 bugs in the rc-4 window; `run.py` 2; `gate.py` 1 | UPDATE, narrowed | text, names and messages only on `_check.py`; the copy failure message, the one path spelling and `run.py`, `gate.py`, `eval.yml` items stay |
| `evals/_check.py:133,137` `read_artifact` content-order sort | sorts parts by `astype(str).values.tolist()` | `eval-parts-dir-provenance-order-random` (made it), `eval-spark-multipart-dir-fails-provenance` (its child) | DELETE | inert under the multiset `value_hash`; only its own pin goes red |
| `evals/_check.py:160,184,187` `provenance` path resolution | `realpath` and `.resolve()` side by side after 162fa1d | `eval-provenance-refuses-absolute-in-workdir-link` | UPDATE | one spelling; the link and loop tests stay green |
| `evals/tasks/get-started-cli/tests/check.py` (entry 5) | 8 rewrites of the matcher, 4 accepted ceilings | none in the ledger | UPDATE | docstring, one accept case, one indent; no ninth rewrite |
| `evals/tasks/pk-fk-constraints/tests/check.py:16,51,55` | reads private `Keys._pk_at` | none | UPDATE | if no public source exists, J7.T1 returns to the main thread |
| `rand_engine/file_handlers/file_handler.py:125/387, 211/397, 293/407` (entry 6) | each format decides its accepted options twice | `json-indent-writes-multiline-records`, `writestream-bare-name-targets-filesystem-root`, `writestream-drive-relative-targets-drive-root` | REBUILD | a duplicated decider, and no test goes red if one copy drifts: 4e1cdf1 edited both by hand. Repro: drop `indent`'s peer key from `:211` only and no test fails |
| docstrings of entry 7 | `_writer_batch.py:364`, `_writer_stream.py:82`, `_rand_generator.py:37`, `exceptions.py:53-58`, `docs/1_DATA_GENERATOR.md:91`, `CHANGELOG.md:34` | none | UPDATE | text, net ≤ 0; `CHANGELOG.md` has no closure shape, so a task carries it |
| `benchmarks/speed.py:309-311` and `tests/test_benchmarks.py:172-199` (entry 11) | head and base both min-of-three; `Fake` answers base 1.0 | `speed-gate-fails-on-runner-noise` | KEEP the estimator, ADD the partition | no test goes red when `:311` returns to `median`; ADD carries it as a test only |
| `docs/benchmarks.json`, `docs/BENCHMARKS.md` | records d577ed0 | none | UPDATE | the committed artifact of the last measured head (AC30.3) |
| `AGENTS.md` `verify:`, default date format literals (entries 8, 9) | — | — | not touched | rejected by the grill |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| an eval artifact's frame and column hash | `evals/_check.py` `value_hash` (multiset) | `read_artifact`, the shim, `provenance` | the sort in `read_artifact` |
| a path inside the scratch copy | one `realpath` spelling in `provenance` | the link and loop tests | the `.resolve()` spelling |
| which run owns the shim's record | the process that loaded the shim (`_check.py:37`) | `dump` | none |
| a writer format's accepted options | one tuple per format in `file_handler.py` | batch and stream constructors, `to_csv`, `to_json`, `to_parquet` | the second list at `:387`, `:397`, `:407` |
| "passed and no error" of a trial | one test in `gate.py` | the two uses at `:80`, `:86` | the second test |
| the speed gate's estimator | `min` of three (`speed.py:309,311`) | `tests/test_benchmarks.py` | none |

## DAG

Waves are schedule waves; jobs of one wave write disjoint files. Job 1 first. Entries 3, 4 and 5 share `test_eval_tasks.py` and `test_eval_check.py`, so their tasks run in order inside Jobs 3, 6 and 7, never as parallel tasks. The three ACs awaiting the operator's order are one task each: J2.T3 (AC31.3), J6.T9 (AC37.4), J3.T7 (AC37.9); a "no" cancels that task alone, with its reason.

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `tests/test_benchmarks.py` |
| Job 2 | — | 1 | `rand_engine/file_handlers/file_handler.py`, `tests/test_5_files_write_batch.py`, `tests/test_5_files_write_stream.py` |
| Job 3 | — | 1 | `evals/_check.py`, `evals/README.md`, `tests/integrations/test_eval_check.py`, `evals/tasks/templates-and-examples/tests/check.py`, `evals/tasks/pk-fk-constraints/tests/check.py`, `evals/tasks/generation-methods/tests/check.py`, `evals/tasks/rand-spec-grammar/tests/check.py`, `evals/tasks/spark-generator/tests/check.py`, `evals/tasks/data-generator/tests/check.py`, `evals/tasks/writers-and-streaming/tests/check.py` |
| Job 4 | — | 1 | `rand_engine/file_handlers/_writer_batch.py`, `rand_engine/file_handlers/_writer_stream.py`, `rand_engine/main/_rand_generator.py`, `rand_engine/validators/exceptions.py`, `docs/1_DATA_GENERATOR.md`, `CHANGELOG.md` |
| Job 5 | — | 1 | `tests/test_9_cli.py`, `tests/test_3_spark_generator.py`, `tests/conftest.py` |
| Job 6 | — | 2 | `evals/run.py`, `evals/gate.py`, `.github/workflows/eval.yml`, `tests/integrations/test_public_api.py`, `tests/integrations/test_eval_gate.py` |
| Job 7 | Job 3 | 2 | `evals/tasks/pk-fk-constraints/tests/check.py`, `evals/tasks/get-started-cli/tests/check.py`, `tests/integrations/test_eval_tasks.py` |
| Job 8 | Job 2 | 2 | `tests/test_docs.py`, `tests/test_0_np_core.py`, `tests/test_1_advanced_validator.py`, `tests/test_1_common_validator.py`, `tests/test_2_data_generator.py`, `tests/test_2_data_generator_fails.py`, `tests/test_5_files_write_batch.py`, `tests/test_5_files_write_stream.py`, `tests/test_6_stream_objects.py`, `tests/test_8_consistency.py` |
| Job 9 | Job 2, Job 4 | 2 | `docs/benchmarks.json`, `docs/BENCHMARKS.md` |
| Reconciliation | Job 1 to Job 9 | 3 | `specs/memory/product/quality/agent-eval.md`, `specs/memory/product/quality/benchmarks.md`, `specs/memory/product/output/writers-and-streaming.md`, `specs/memory/product/onboarding/get-started-cli.md`, `specs/memory/product/relations/pk-fk-constraints.md`, `specs/memory/product/catalog.json` |

Edge reasons: Job 7 needs Job 3's rename in `pk-fk-constraints/tests/check.py`; Job 8 shares both `test_5_files_write_*.py` with Job 2; Job 9 needs the last measured-path merge (Jobs 2 and 4 touch `rand_engine/file_handlers/`). Job 6 is disjoint from Job 3 and waits on nothing; it sits in wave 2 to hold each wave to five jobs. Job 8's AC36.3 sweep excludes `tests/AGENTS.md:8` ("FR11", a law line).

### Schedule and sizing

- 41 tasks: Job 1 one (jr); Job 2 three (2 sr, 1 jr); Job 3 seven (3 sr, 4 jr); Job 4 three (jr); Job 5 three (1 sr, 2 jr); Job 6 nine (4 sr, 5 jr); Job 7 six (3 sr, 3 jr); Job 8 five (jr); Job 9 one (jr). 13 sr, 28 jr. A RED task precedes its implementation where behaviour is new (J2, J3.T1/T3, J6); the others are test hygiene or text, each with its owner test already in the repo.
- J3 holds `evals/_check.py` at net ≤ 0 against 162fa1d (272 lines, the main thread's ruling); J2.T2 holds `file_handler.py` at net ≤ 0. A task that cannot returns to the main thread.

## 2. Gates

The job gate is the repo's `verify:` line, unchanged (`AGENTS.md`); no preflight, matrix or local gate is added, and no task's Done-when is the full CI line. Each job's Done-when is `verify:` plus the test directories its change reaches. Eval changes run on the existing push trigger once, at the `wt-rc` push.

## Measured cost

- Gate law: no task adds a step to `verify:` or the merge. 41 task merges, 9 job merges and one `wt-rc` merge run the existing line.
- J7.T4 reduces `tests/integrations/test_eval_tasks.py` from 13 reference trials to one per slug; its hand-back quotes the wall time against today's 31-102 s (**measured by the task**, source the run it reports).
- AC30.3 quotes the Benchmarks run id; AC38.4 the line count of `evals/_check.py`.

## Acceptance map

| AC | owner task | implementation task |
|---|---|---|
| AC30.1 | J1.T1 | J1.T1 (green on arrival) |
| AC30.2 | no test; read on the diff | none, `speed.py` unchanged |
| AC30.3 | `tests/test_benchmarks.py:337-351` | J9.T1 |
| AC31.1 | J2.T1 | J2.T1 (green on arrival), J2.T2 |
| AC31.2 | J2.T1 | J2.T2 |
| AC31.3 | J2.T3, pending the order | J2.T3 |
| AC32.1 | J3.T1 | J3.T3 |
| AC32.2, AC32.9, AC32.10 | no test / the link and loop tests / read on the diff | J3.T3 |
| AC32.3 | existing `test_eval_check.py`, `test_eval_tasks.py` | J3.T4, J3.T5 |
| AC32.4 | no test | J3.T5 |
| AC32.5 | J6.T1 | J6.T4 |
| AC32.6 | J6.T2, J6.T3 | J6.T5, J6.T6 |
| AC32.7 | the pk-fk reference and decoy trials | J7.T1 |
| AC32.8 | J3.T2 (the deletion) | J3.T3 |
| AC33.1, AC33.3 | no test; read on the diff | J7.T3 |
| AC33.2 | J7.T2 | J7.T3 (green on arrival) |
| AC34.1 | `ruff D` and doctests in `verify:` | J4.T1 |
| AC34.2 | no test | J4.T2 |
| AC34.3, AC38.3 | the dated-header test in `tests/test_docs.py` | J4.T3 |
| AC35.1, AC35.2 | J5.T1 | J5.T1 |
| AC35.3 | J5.T2 | J5.T2 |
| AC36.1 | J8.T1 | J8.T1 |
| AC36.2 | J8.T2 | J8.T2 |
| AC36.3 | a sweep | J8.T4 |
| AC36.4 | J8.T3 | J8.T3 |
| AC36.5 | J5.T3, J8.T5 | J5.T3, J8.T5 |
| AC37.1, AC37.2, AC37.6 | J3.T6 | J3.T6 |
| AC37.3, AC37.5 | J6.T7, J6.T8 | J6.T7, J6.T8 |
| AC37.4 | J6.T9, pending the order | J6.T9 |
| AC37.7 | J7.T4 | J7.T4 |
| AC37.8 | J7.T5 | J7.T5, J7.T6 |
| AC37.9 | J3.T7, pending the order | J3.T7 |
| AC38.1, AC38.2, AC38.4 | no test | Reconciliation |

### Reconciliation (the rc's last commits, `RC-FLOW.md` step 4)

Order, `dd-product-engineer`: (1) `release.py phase CLOSURE`; (2) the memory pass from the final diff (AC38.1: `agent-eval.md:41`, the scratch copy's link rule and the Windows junction ceiling, the writer options, renamed `_check.py` names, the speed gate's estimator), then `catalog generate`; (3) the closure summary quoting AC30.3's run id, AC37.7's wall times, `evals/_check.py`'s line count against 272, and the AC38.2 corrections.
