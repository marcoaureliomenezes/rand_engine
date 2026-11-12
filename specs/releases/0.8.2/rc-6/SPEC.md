# SPEC — Release: 0.8.2, candidate 6 (the rc-5 closure drain, compatible changes only)

**Status:** Approved
**Release ID:** 0.8.2
**Owner:** dd-product-engineer
**Opened:** 2026-11-12
**Origin:** backlog:to-file-opener-from-format,library-test-hygiene-2,eval-harness-hygiene-3,eval-test-hygiene-2

- The open CRITICAL `setuptools-ghsa-xmj3-open-on-master` closes at the 0.8.2 promote (the `master` merge), outside rc-6 (grill ruling 7).
- Sources: the grill record `2026-11-12T111500Z-main-thread-rc6-grill`; the as-is review `2026-11-12T110331Z-dd-sw-engineer-sr-rc6-as-is-review`; the intake `0.8.2-rc4-intake.md`, rows 163-189. Every `path:line` is a `0a0ecd8` anchor (code equal to `8758c72`). The PLAN re-greps each one.
- FR numbers continue the release: rc-6 owns FR39–FR44. Not an ADR: every change is reversible and keeps compatibility.

### Rulings, verbatim

| ruling | answer | meaning |
|---|---|---|
| The drain (operator) | "Ratify all 4 (Recommended)" | the four Origin entries are rc-6's whole scope |
| Intake row 181 (operator) | "Delete :93 duplicate (Recommended)" | AC43.5 |
| Intake row 171 (operator) | "Confirm the skip (Recommended)" | the POSIX `skipif` at `tests/integrations/test_public_api.py:912` stands (AC42.3) |
| Grill 1 (main thread) | "extract only `run.seed_cwd`, net-zero lines; the transcript rule stays restated with a one-line docstring note. Job 6 does not wait on Job 5." | AC43.2 |
| Grill 2 (main thread) | "the guard literal pin and behaviour test change with the guard; the RED `test(...)` commit names this ruling. Message: `k=$K: k must be an integer from 1 to 3 (the job timeout fits k up to 3)`; one `2>/dev/null`; the `if [ "$K"` prefix stays." | FR42 |
| Grill 3 (main thread) | "restore the one-line docstring \"max - min is inf in float64\"" | AC40.7 |
| Grill 4 (main thread) | "one parametrize row, green at birth; the reviewer proves it by mutating `pk_identity` and seeing it go red" | AC43.6 |
| Grill 5 (main thread) | "writeStream into 10 files carries ids 1..1000 and the parent_id of one 1000-row get_df" | AC40.7 |
| Grill 6 (main thread) | "rename the 14 provenance-result lines in 7 checks and the 26 hits in test_eval_check.py to `generations`; the shim's `RAND_EVAL_RECORD` and `"records"` key stay; `discovery/tests/check.py:1` prose stays" | AC41.5 |
| Grill 7 (main thread) | "stays a promote-time close, stated in the SPEC Origin" | the Origin bullet above |

## Bug window review

Prior candidate: rc-5. Its window review judged rc-4's 12 resolved bugs; one bug was resolved since: `k-guard-test-runs-wsl-bash-on-windows`. One bug is open: `setuptools-ghsa-xmj3-open-on-master` (CRITICAL), outside rc-6. The fix was read with `git show fae1efa --stat --patch`.

| bug | fix | pattern hit | verdict | why |
|---|---|---|---|---|
| `k-guard-test-runs-wsl-bash-on-windows` | fae1efa (+1 −0), `refactor(bugs)` REBUILD; caused by 113031b (rc-5 J6.T3) | a newly skipped test: `skipif(os.name != "posix")` on the guard's `bash -c` case | KEEP | the trials job runs on ubuntu only, so the case is judged where its shell is; the text pin still runs on every OS; the operator confirmed the skip ("Confirm the skip (Recommended)", row 171); no child bug through 0a0ecd8 |

## 1. Problem

- `_to_file` (`rand_engine/file_handlers/file_handler.py:378`) takes an `opener` beside the `format` it follows from; each `to_csv`, `to_json`, `to_parquet` passes both (`:403,407,411`).
- Library tests say more or less than they assert:
  - `tests/test_benchmarks.py:194` names only the head sample, while its rows pin the quickest base and head samples;
  - `spark_guard` (`tests/test_9_cli.py:167-171`) and `arrow_conf` (`tests/test_3_spark_generator.py:703-705`) are generator fixtures with no teardown of their own;
  - every row of the refusal case at `tests/test_5_files_write_batch.py:258-263` saves to `f.json`, so a failed csv or parquet refusal writes a file `not path.exists()` never sees; `:284-287` is a one-row parametrize;
  - six `re.search(...).group()` calls in `tests/test_docs.py` (`:165,579,870,1010,1011,1036`) raise `AttributeError` on a docs drift instead of naming the page;
  - docstrings cite an absent `proto/` (`tests/test_8_consistency.py:335`) and claim 100 rows per file that no assert checks (`:418`); `tests/test_1_common_validator.py:772` lost its reason (7b0472e); `tests/AGENTS.md:8` carries the id "FR11".
- The eval harness:
  - `evals/run.py:154,156` reads `check.returncode == 0` twice;
  - the K guard (`.github/workflows/eval.yml:145`) prints bash's "integer expression expected" on a non-integer K, and its message names only the upper bound;
  - `evals/gate.py:6-7`'s Exit omits the exit 1 on a missing results directory (`:29-31`);
  - `evals/README.md:18` does not parse, and `:50` cites `gate.py:101` where the `tokens unknown` cell is `:105`;
  - seven task checks and `test_eval_check.py` call the provenance result `record`; `_check.py:198` binds it through a walrus;
  - the get-started-cli `Ceilings:` (`evals/tasks/get-started-cli/tests/check.py:43-45`) omits a reproduced fifth ceiling: `rand-engine get-started \` continued onto a next line holding `lake` is refused.
- Eval tests:
  - `test_rerun_writes_no_bytecode` (`tests/integrations/test_eval_check.py:195-197`) deletes `PYTHONDONTWRITEBYTECODE`, and `run_script` (`:62-64`) then delivers the artifacts with that env: a lone run of the case leaves 7 `__pycache__` dirs under `rand_engine/` (as-is §1, reproduced with the flag set);
  - `reference_trial` (`test_eval_tasks.py:107-125`) restates the harness's seed copy (`evals/run.py:79-80`); `:15-16` imports `run` by a `sys.path` insert; `:147`'s name covers 7 of its 11 rows; `:93` repeats the pk-fk reference trial that `:142` runs; no case pins a bare `{"method": "pk"}` parent;
  - the K-guard case (`test_public_api.py:912-919`) has no K below 1, and `:858`'s name says it names the result event while it asserts the error carries the reason.

## 2. Measurable goals

- `_to_file` takes one parameter fewer, `file_handler.py` shrinks, and every writer's output is unchanged.
- `git grep -nE 're\.(search|match)\(.*\)\.group' -- tests evals`, `git grep -n 'proto/' -- tests/` and `git grep -nE '\b(AC|FR)[0-9]+' -- tests/` print nothing.
- A K outside the integers 1 to 3 fails with one line naming both bounds and no shell noise.
- Under the `verify:` line's env, a run of `tests/integrations/test_eval_check.py` leaves the `.pyc` files under `rand_engine/` as it found them.
- Every Origin item lands, or Non-goals names it.

### Wave ranking

| wave | scope | FRs |
|---|---|---|
| 1 — law, skills and dev loop | none | — |
| 2 — shared foundation | none | — |
| 3 — features and bugs | the writer's opener, library tests, eval harness, the K guard, eval tests | FR39, FR40, FR41, FR42, FR43 |
| 4 — promote-facing | closure | FR44 |

## 3. Non-goals

- The other format-to-opener deciders, `_writer_batch.py:299-306` and `writer.py:35-39` (intake row 189); the three agree for csv, json and parquet.
- `benchmarks/speed.py:1`'s "FR11" docstring; the five other walruses in `evals/_check.py` (`:63,99,183,186,202`).
- The shim's `RAND_EVAL_RECORD`, `record.json` and `"records"` key: a private shim-to-provenance format; `discovery/tests/check.py:1`'s "Discovery record" prose.
- A rewrite of the get-started-cli matcher (ruling row 119): the fifth ceiling is documented, not lifted.
- Extracting the transcript rule (`evals/selfcheck.py:29-30`): it is conditional on a file there (grill 1).
- Running the K-guard case on Windows (the skip stands, row 171).
- A change for `test_eval_tasks.py`'s bytecode: it leaves none today (as-is §1, Spark rows deselected).
- Any `gen_*` body; any change that breaks compatibility (grammar, seed, error format, default, exported name): 0.9.0's.
- A PyPI publish or a tag of 0.8.2; closed-candidate text stays history.

## 4. Requirements

### FR39 — The file writer derives its opener from the format (`to-file-opener-from-format`, REBUILD)

- AC39.1 (unit, the `FileHandler.to_*` cases of `tests/test_5_files_write_batch.py`, asserts unchanged): `_to_file` takes the format and no opener; `to_csv`, `to_json` and `to_parquet` pass only their format. Every written file, accepted option list and refusal message is unchanged.
- AC39.2 (no test; read on the diff): `git diff --numstat` of `file_handler.py` deletes more lines than it adds; no other file under `rand_engine/` changes.

### FR40 — Library test hygiene 2 (`library-test-hygiene-2`)

- AC40.1 (unit, `tests/test_benchmarks.py:194`): the name states that a row is judged by its quickest base and quickest head samples; rows and asserts unchanged.
- AC40.2 (unit, `tests/test_9_cli.py`, `tests/test_3_spark_generator.py`): `spark_guard` and `arrow_conf` return their value with no `yield`; `arrow_conf_restored` keeps the restore, and every test that uses them stays green.
- AC40.3 (unit, `tests/test_5_files_write_batch.py:252-263`): each row asserts that no file exists where its own format's save would write. Dropping the refusal on the csv path turns the csv row red; the json rows keep `f.json`.
- AC40.4 (unit, same file, `:284-290`): the one-row parametrize becomes a plain case keeping the full literal `^json option 'indent' is not documented; accepted: orient, force_ascii, compression$` and its `not path.exists()` assert.
- AC40.5 (unit, `tests/test_docs.py`): each of the six `.group()` sites asserts its match first, with a message naming its page or section, as `:1044-1046` does; a drift fails with that message, never `AttributeError`.
- AC40.6 (no test; docstring text): `tests/test_8_consistency.py:335` states its pins without a `proto/` path.
- AC40.7 (no test; docstring text, ruled literals): the docstring at `tests/test_8_consistency.py:418` reads "writeStream into 10 files carries ids 1..1000 and the parent_id of one 1000-row get_df"; `test_spark_float_span_overflowing_float64_is_refused` (`tests/test_1_common_validator.py:772`) carries "max - min is inf in float64".
- AC40.8 (no test; law text): `tests/AGENTS.md:8` names `test_benchmarks.py` as owning the speed benchmark script, with no requirement id.
- AC40.9 (no test; the sweeps): the three greps of §2 print nothing (6, 1 and 1 hits at 0a0ecd8).

### FR41 — Eval harness hygiene 3 (`eval-harness-hygiene-3`, items 1 and 3-8)

- AC41.1 (integration, the `run.py` contract tests in `test_public_api.py`, asserts unchanged): `evals/run.py` reads the check's exit code once; `passed` and `first_failure` hold today's values in every case.
- AC41.2 (no test; docstring text): `evals/gate.py`'s Exit clause names the exit 1 on a missing results directory.
- AC41.3 (no test; doc text): `evals/README.md:18` states, in a sentence that parses, the rule `_check.py:201-202` enforces: every artifact column equals, by name, row count and value hash, a column of a frame the agent's own code generated.
- AC41.4 (no test; doc text, written after AC41.2): `evals/README.md:50` cites the `gate.py` line that holds the `tokens unknown` cell.
- AC41.5 (integration, the task checks' reference and decoy trials in `test_eval_tasks.py` and the `test_eval_check.py` cases, asserts unchanged): the provenance result is named `generations` in the seven checks (14 lines) and in `test_eval_check.py` (26 hits). `git grep -nw record -- 'evals/tasks/*/tests/check.py' tests/integrations/test_eval_check.py` prints only `evals/tasks/discovery/tests/check.py:1`.
- AC41.6 (integration, the `test_eval_check.py` provenance cases, asserts unchanged): `_check.py:198` binds the parsed record file without a walrus; `provenance` returns the same message and generations in every case.
- AC41.7 (no test; docstring text): the get-started-cli `Ceilings:` sentence lists a fifth ceiling: a `get-started` call continued by a backslash onto the next line before `lake` is refused. The diff of that `check.py` touches only its docstring.

### FR42 — The K guard names both bounds (`eval-harness-hygiene-3` item 2, `eval-test-hygiene-2` item 7)

- AC42.1 (integration, the K-guard case in `test_public_api.py`, RED first): rows `"0"` and `"-1"` join `"3"`, `"4"`, `"abc"`, `""` and `"2.5"`. A row outside the integers 1 to 3 exits 1 and its stderr is exactly `k=<K>: k must be an integer from 1 to 3 (the job timeout fits k up to 3)` and a newline; `"3"` exits 0 with an empty stderr. At 0a0ecd8 every failing row is red on stderr only: `"0"` and `"-1"` already exit 1, and `"abc"`, `""`, `"2.5"` also print "integer expression expected".
- AC42.2 (integration, the guard text pin `test_public_api.py:905-909`): the guard line keeps the `if [ "$K"` prefix, carries one added `2>/dev/null`, and precedes `python evals/run.py`. The pin moves with the guard under grill ruling 2, which the RED `test(...)` commit names.
- AC42.3 (no test; read on the diff): the case keeps its POSIX `skipif` ("Confirm the skip (Recommended)"), and its name states the bounds 1 to 3.

### FR43 — Eval test hygiene 2 (`eval-test-hygiene-2`, items 1-6 and 8)

- AC43.1 (integration, `test_eval_check.py::test_rerun_writes_no_bytecode`, RED first): under `PYTHONDONTWRITEBYTECODE=1`, the case leaves the set of `.pyc` files under `rand_engine/` equal before and after; red at 0a0ecd8. The artifact delivery (`run_script`) runs with the flag set, and the case still asserts the re-run's own `sys.dont_write_bytecode`.
- AC43.2 (integration, the reference trials in `test_eval_tasks.py`, asserts unchanged): `reference_trial` copies a task's seed environment through `run.seed_cwd`, the same function `prepare_trial` calls; the extraction nets zero lines in `evals/run.py`. The transcript rule stays in `reference_trial`, with a one-line docstring note naming `evals/selfcheck.py` as its source.
- AC43.3 (integration, same file): `run` is loaded by `importlib.util.spec_from_file_location`, as `test_eval_check.py:43`, `test_eval_gate.py:17` and `test_public_api.py:689` load their modules; `git grep -n 'sys.path' -- tests/integrations/test_eval_tasks.py` prints nothing.
- AC43.4 (no test; name): `:147`'s name covers all 11 rows: each reference trial passes its check, and an undecodable byte in an agent-written file does not crash it.
- AC43.5 (integration; a deletion on the operator's order "Delete :93 duplicate (Recommended)"): the `CUSTOMER_PK` row (`:93`) of `test_pk_fk_check_accepts_a_parent_equal_to_the_pk_after_its_defaults` is deleted, its `test(` commit quoting the order. The pk-fk-constraints row at `:142` and the constant `CUSTOMER_PK` stay.
- AC43.6 (integration, same parametrize; green at birth, grill 4): a bare `'{"method": "pk"}'` parent row expects exit 0 and `"layer": "pass"`. No RED is possible, since the check accepts it at 0a0ecd8; the reviewer mutates `pk_identity` (`evals/tasks/pk-fk-constraints/tests/check.py:50-57`) and sees the row go red.
- AC43.7 (no test; name): `test_public_api.py:858`'s name states its asserts: the error carries the result event's reason and no `StopIteration`.

### FR44 — Closure: memory and the record

- AC44.1 (closure memory pass, `pe`, from the final diff): an atom that names the writer's opener, the K guard, the get-started-cli ceilings or the eval tests' bytecode matches the code; `catalog.json` is regenerated by `catalog generate`.
- AC44.2 (no test): `CHANGELOG.md` gains no entry: FR39 keeps every writer's output, and FR40-FR43 touch tests, evals and CI only.
- AC44.3 (no test; rc-6's closure summary): it quotes the net lines of `file_handler.py` (AC39.2) and `evals/run.py` (AC43.2).

## Replaces

- `_to_file`'s `opener` parameter and the three `FileHandler.open_<fmt>` arguments (`file_handler.py:378,403,407,411`) → AC39.1. Consumers: only those three `to_*` (`git grep -n '_to_file\b'`: four hits, all in `file_handler.py`); `_to_file` is private.
- The second read of the check's exit code (`run.py:156`) → AC41.1; the walrus at `_check.py:198` → AC41.6; the local name `record` → AC41.5.
- The K guard's bash stderr and its one-bound message (`eval.yml:145`) → FR42. Consumers: `test_public_api.py:905-909` and `:912-919`; the eval job's log.
- `reference_trial`'s own seed copy (`test_eval_tasks.py:118-119`) → AC43.2; the `sys.path` insert (`:15-16`) → AC43.3; the `CUSTOMER_PK` row (`:93`) → AC43.5, on the operator's order.
- The generator fixtures' `yield` → AC40.2; the one-row parametrize → AC40.4.

## 5. Constraints and risks

| risk | control |
|---|---|
| Shared files: `evals/run.py` (AC41.1, AC43.2), `test_eval_check.py` (AC41.5, AC43.1), `test_public_api.py` (FR42, AC43.7), `test_5_files_write_batch.py` (FR39 owner tests, AC40.3, AC40.4) | the PLAN gives each file to one job, or orders the jobs |
| AC41.4's line cite moves with AC41.2's edit | the same task, AC41.2 first |
| AC43.1's measure needs the flag in the parent; without it pytest itself writes bytecode | the RED runs under the `verify:` line's env |
| The Spark row of `test_eval_tasks.py` needs Java and pyspark | a scratch run deselects it; CI runs it |

## 6. Open questions

For the main thread; none blocks the PLAN.

1. **`evals/run.py` in two jobs.** Grill 1 says "Job 6 does not wait on Job 5", while the as-is DAG gives `evals/run.py` to Job 5 and AC43.2 edits it. That holds only if the PLAN puts `run.seed_cwd` and AC41.1 in one job's `W:`, or orders the two.
