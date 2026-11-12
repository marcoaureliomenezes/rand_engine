# PLAN — Release: 0.8.2, candidate 6

**Status:** Approved
**Release ID:** 0.8.2
**Owner:** dd-sw-engineer-sr
**SPEC:** `rc-6/SPEC.md` (0a72a09)

Sources: as-is review `.dadaia/reports/rand-engine/2026-11-12T110331Z-dd-sw-engineer-sr-rc6-as-is-review.md`; the grill record `2026-11-12T111500Z-main-thread-rc6-grill.md` with its amendment; the SPEC's rulings. Tree `worktrees/rand-engine/0.8.2/rc-6/wt-rc`. Every `path:line` was re-read at `0a72a09` (the define commits touch only `specs/`; code equals `8758c72`). Open bug: `setuptools-ghsa-xmj3-open-on-master` only; it closes at the `master` merge and no rc-6 file touches its pin. The bug window review is the SPEC's.

## 1. As-is review

Bug history = the ledger (`BUGS.jsonl` and `_archive/bugs_histo.jsonl`) plus `git log -E --grep '^(fix|refactor)\(bugs\): ' -- <file>`; 95 ledger rows read, none open on a unit below.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `rand_engine/file_handlers/file_handler.py:378` `_to_file` | takes `format` and `opener`; the three `to_*` pass `FileHandler.open_<fmt>` (`:403,407,411`) | `json-indent-writes-multiline-records` (4e1cdf1, KEEP); 2a48173 REBUILD of accepted options; no child bug after | REBUILD | the opener follows from `format`; signature changes, net lines negative |
| `tests/test_5_files_write_batch.py:252-263,284-290` | 4 rows all save `f.json`, so a csv refusal writes `f.json.csv` and `not path.exists()` misses it; a one-row parametrize | none | UPDATE | `f.{format_type}` per row; plain case |
| `tests/test_benchmarks.py:194`, `tests/test_9_cli.py:167-171`, `tests/test_3_spark_generator.py:703-705`, `tests/AGENTS.md:8` | a name that omits the base sample; two generator fixtures with no teardown; "FR11" in a law line | none | UPDATE | rename; `return`; "the speed benchmark script" |
| `tests/test_docs.py:165,579,870,1010,1011,1036` | `re.search(...).group()` | 4 test_docs bugs, all KEEP | UPDATE | a named assert before each; `:1044-1046` is the model |
| `tests/test_8_consistency.py:335,418`, `tests/test_1_common_validator.py:772` | `proto/` cited (absent); "100 rows per file" unasserted; no reason on the test | none | UPDATE | ruled literals (SPEC grill 3, 5) |
| `evals/run.py:79-80,154,156` | seed copy inside `prepare_trial`; `check.returncode == 0` twice | `eval-token-reaches-agent-shell` (f29b3e8 REBUILD, KEEP) | UPDATE | `passed` read once; `seed_cwd(task_dir, cwd)` extracted, net zero lines |
| `evals/gate.py:6-7`, `evals/README.md:18,50` | Exit omits exit 1; an unparsable sentence; `gate.py:101` is now `:105` | `e5502a0` adoption-rate print (KEEP) | UPDATE | one clause, one sentence, then the cite last |
| `evals/_check.py:198` | walrus on `data` | 9 provenance bugs (REBUILD in rc-5), none on this line | UPDATE | `data = ...` then `generations = data["records"]`; five other walruses stay |
| `evals/tasks/*/tests/check.py` (7), `get-started-cli/tests/check.py:43-45` | local `record` (14 lines); four ceilings, a fifth reproduced | 8 matcher rewrites (row 119), none on these lines | UPDATE | rename to `generations`; docstring only |
| `.github/workflows/eval.yml:145` | first `[` prints "integer expression expected"; message names one bound | `k-guard-test-runs-wsl-bash-on-windows` (fae1efa, KEEP) | UPDATE | one `2>/dev/null`, the ruled message, the `if [ "$K"` prefix stays |
| `tests/integrations/test_public_api.py:858,905-919` | name overstates; guard pin; K rows 3,4,abc,"",2.5 | the k-guard bug above | UPDATE + RED | rows "0","-1", stderr literal; pin moves with the guard (ruling 2) |
| `tests/integrations/test_eval_check.py:62-64,195-197` and its 26 `record` hits | `run_script` inherits the env minus the flag after the `delenv`; 7 `__pycache__` under `rand_engine/` in a lone run | none on this file | UPDATE + RED | `run_script` passes the flag; rename to `generations` |
| `tests/integrations/test_eval_tasks.py:15-16,93,107-125,147` | `sys.path` insert; duplicate trial row; `reference_trial` restates the seed copy; name covers 7 of 11 rows | 3 hygiene commits (5b7d0c6, d3e14bb), no bug | UPDATE | `importlib`; delete `:93`; `run.seed_cwd`; rename |
| the same file, bare `{"method": "pk"}` parent | no row; the check accepts it today | none | ADD | one parametrize row, green at birth (grill 4) |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| format to opener | `FileHandler.open_<fmt>` via `getattr` in `_to_file` | the three `to_*` | the `opener` parameter and its three passes |
| did the check pass | `check.returncode`, read once in `evals/run.py` | `first_failure`, `passed` | the second read |
| which K is valid | the guard line in `eval.yml` | both K tests | the unsilenced `[` stderr |
| a trial's seed environment | `run.seed_cwd` | `prepare_trial`, `reference_trial` | `reference_trial`'s own copy |
| bytecode off for the agent run | the test env, passed by `run_script` | `provenance` | the `delenv` leak into `run_script` |

Noted for intake, out of scope: the format-to-opener decider also lives in `_writer_batch.py:299-306` and `writer.py:35-39`; the three agree for csv, json and parquet.

## DAG

Waves are schedule waves; jobs of one wave write disjoint files. Each shared file belongs to one job: `evals/run.py` to Job 5 only (grill amendment), `test_public_api.py` to Job 4, `test_eval_check.py` and `test_eval_tasks.py` to Job 6, `test_5_files_write_batch.py` to Job 2 (FR39's owner tests are its existing cases, asserts unchanged). Tasks inside a job run in numeric order.

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `rand_engine/file_handlers/file_handler.py` |
| Job 2 | — | 1 | `tests/test_5_files_write_batch.py`, `tests/test_benchmarks.py`, `tests/test_9_cli.py`, `tests/test_3_spark_generator.py`, `tests/AGENTS.md` |
| Job 3 | — | 1 | `tests/test_docs.py`, `tests/test_8_consistency.py`, `tests/test_1_common_validator.py` |
| Job 4 | — | 1 | `.github/workflows/eval.yml`, `tests/integrations/test_public_api.py` |
| Job 5 | — | 1 | `evals/run.py`, `evals/gate.py`, `evals/_check.py`, `evals/README.md`, `evals/tasks/data-generator/tests/check.py`, `evals/tasks/generation-methods/tests/check.py`, `evals/tasks/get-started-cli/tests/check.py`, `evals/tasks/pk-fk-constraints/tests/check.py`, `evals/tasks/rand-spec-grammar/tests/check.py`, `evals/tasks/spark-generator/tests/check.py`, `evals/tasks/templates-and-examples/tests/check.py`, `evals/tasks/writers-and-streaming/tests/check.py` |
| Job 6 | Job 5 (J6.T8 only) | 2 | `tests/integrations/test_eval_check.py`, `tests/integrations/test_eval_tasks.py` |
| Reconciliation | Job 1 to Job 6 | 3 | `specs/memory/product/quality/agent-eval.md`, `specs/memory/product/output/writers-and-streaming.md`, `specs/memory/product/onboarding/get-started-cli.md`, `specs/memory/product/catalog.json` |

Edge reason: J6.T8 calls `run.seed_cwd`, which J5.T2 creates; every other Job 6 task is independent of Job 5, so Job 6 is in wave 2 only because a job merges whole, and J6.T8 is its last task. Atoms the memory pass touches are those that name the writer's opener, the K guard, the get-started-cli ceilings or the eval tests' bytecode.

### Schedule and sizing

- 23 tasks: Job 1 one (jr); Job 2 three (jr); Job 3 two (jr); Job 4 three (1 sr, 2 jr); Job 5 six (1 sr, 5 jr); Job 6 eight (3 sr, 5 jr). 5 sr, 18 jr. A RED task precedes its implementation where behaviour is new (J4.T1, J6.T1); the others are test hygiene or text with their owner test already in the repo.
- Net lines: Job 1 shrinks `file_handler.py` (AC39.2); J5.T2 nets zero in `evals/run.py` (AC43.2); J5.T1 shrinks it. Job 4 adds two rows and J6.T7 one row, each ratified in the SPEC. A task that cannot hold its bound returns to the main thread.

## 2. Gates

The job gate is the repo's `verify:` line (`python scripts/ci.py job`), unchanged; no preflight, matrix or local gate is added, and no task's Done-when is the full CI line. Each job's Done-when is `verify:` plus the test directories its change reaches. Eval changes run on the existing push trigger once, at the `wt-rc` push.

## Measured cost

- Gate law: no task adds a step to `verify:` or the merge. 23 task merges, 6 job merges and one `wt-rc` merge run the existing line.
- AC39.2 quotes the net lines of `file_handler.py`; AC43.2 those of `evals/run.py` (closure summary, AC44.3).

## Acceptance map

| AC | owner task | implementation task |
|---|---|---|
| AC39.1 | the existing `FileHandler.to_*` cases, asserts unchanged | J1.T1 |
| AC39.2 | no test; read on the diff | J1.T1 |
| AC40.1 | `tests/test_benchmarks.py` rows, unchanged | J2.T2 |
| AC40.2 | the tests that use the fixtures | J2.T2 |
| AC40.3, AC40.4 | J2.T1 | J2.T1 (green on arrival; revert-check: drop the csv refusal, the csv row goes red) |
| AC40.5 | J3.T1 | J3.T1 |
| AC40.6, AC40.7 | no test; docstring text | J3.T2 |
| AC40.8 | no test; law text | J2.T3 |
| AC40.9 | the three sweeps, run at the `wt-rc` after Jobs 2 and 3 merge | J3.T2 (its files); J2.T3 (`tests/AGENTS.md`) |
| AC41.1 | the `run.py` contract tests, unchanged | J5.T1 |
| AC41.2, AC41.3, AC41.4 | no test; text | J5.T3 |
| AC41.5 | the reference and decoy trials, the `test_eval_check.py` cases | J5.T5 (the 7 checks), J6.T3 (the test file) |
| AC41.6 | the `test_eval_check.py` provenance cases | J5.T4 |
| AC41.7 | no test; docstring text | J5.T6 |
| AC42.1, AC42.2, AC42.3 | J4.T1 | J4.T2 |
| AC43.1 | J6.T1 | J6.T2 |
| AC43.2 | the reference trials, unchanged | J5.T2 (`run.seed_cwd`), J6.T8 (`reference_trial`) |
| AC43.3 | the reference trials | J6.T5 |
| AC43.4 | no test; name | J6.T6 |
| AC43.5 | J6.T4 (the deletion, on the operator's order) | J6.T4 |
| AC43.6 | J6.T7 (green at birth; the reviewer mutates `pk_identity`) | J6.T7 |
| AC43.7 | no test; name | J4.T3 |
| AC44.1, AC44.2, AC44.3 | no test | Reconciliation |

### Reconciliation (the rc's last commits, `RC-FLOW.md` step 4)

Order, `dd-product-engineer`: (1) `release.py phase CLOSURE`; (2) the memory pass from the final diff (AC44.1), then `catalog generate`; (3) the closure summary quoting AC39.2 and AC43.2's net lines (AC44.3); `CHANGELOG.md` gains no entry (AC44.2).
