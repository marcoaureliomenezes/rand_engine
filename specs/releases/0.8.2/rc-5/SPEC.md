# SPEC — Release: 0.8.2, candidate 5 (the rc-4 intake drain, compatible changes only)

**Status:** Approved
**Release ID:** 0.8.2
**Owner:** dd-product-engineer
**Opened:** 2026-11-11
**Origin:** backlog:cli-starter-test-names,library-test-hygiene,eval-test-hygiene,eval-harness-hygiene-2,get-started-cli-check-ceilings,writer-options-one-decider,docstring-accuracy-follow-ups,speed-gate-noise-floor

- Sources: the grill record `2026-11-11T150000Z-main-thread-rc5-grill`; the as-is review `2026-11-11T135627Z-dd-sw-engineer-sr-rc5-as-is-review`; the intake `0.8.2-rc4-intake.md`, rows 1-162. Every `path:line` is a `162fa1d` anchor; since f33fc38 only `evals/_check.py` and `tests/integrations/test_eval_check.py` moved. The PLAN re-greps each one.
- FR numbers continue the release: rc-5 owns FR30–FR38. Not an ADR: every change is reversible and keeps compatibility.

### Grill rulings, operator verbatim

| ruling | answer | meaning |
|---|---|---|
| The drain | "Ratify as proposed (Recommended)" | the eight Origin entries are rc-5's whole scope |
| Row 88 | "Replace :52-55, keep rest (Recommended)" | AC37.8 |
| Row 96 | "Delete sort + pin (Recommended)" | AC32.8 |

### Decided by the main thread (agent default, unruled)

- Entry 4's narrowing drops only the `evals/_check.py` code rows 27, 40 and 80. The `run.py`, `gate.py` and `eval.yml` items stay. Item 5 (row 81) already holds (`_check.py:9`) and is dropped.
- The speed gate keeps min-of-three and gains the noisy-base partition. The residual false-fail floor (1 of 160 row reps, row 145) is accepted.
- The gate's calibrate crash on missing results (row 160) is AC32.6; the one path-resolution spelling (row 162) is AC32.9.
- Closure work (rows 150, 154, 161) is FR38.

### What the operator must see

- Three test removals wait for the operator's order (AC31.3, AC37.4, AC37.9), and AC32.10's line bound predates the abs-link REBUILD (§6).

## Bug window review

Prior candidate: rc-4, with 12 resolved bugs: the as-is review §2's 11 plus `eval-provenance-refuses-absolute-in-workdir-link`, resolved after it. One bug is open: `setuptools-ghsa-xmj3-open-on-master` (CRITICAL), which closes at the 0.8.2 `master` merge. Each fix was read with `git show --stat --patch`.

| bug | fix | pattern hit | verdict | why |
|---|---|---|---|---|
| `eval-shim-sqlite-save-crashes-rerun` | ef4defb (+2 −1), after 7e2f777 | `wrap_save` re-tests `write_format == "sqlite"` (`_check.py:85`), which `save` also decides | KEEP | one condition; the first attempt was replaced, not stacked |
| `json-indent-writes-multiline-records` | 4e1cdf1 (+4 −3) | none; it edited both option lists by hand | KEEP | the fix shrank the feature; the two lists it exposed are FR31's REBUILD |
| `eval-parts-dir-provenance-order-random` | 005c093 (+2 −2) | its premise was refuted; a child bug followed 3 h later | KEEP until AC32.8 | `value_hash` is a multiset (2c390aa), so the sort is inert; its deletion is the row 96 order, not a bug |
| `eval-rerun-overwrites-delivered-artifact` | efa19c9 (+12 −12) | none: a reorder | KEEP | net 0; no later bug names it |
| `eval-spark-multipart-dir-fails-provenance` | 2c390aa (+2 −2) | none | KEEP | one decider of column equality |
| `validator-accepts-aware-date-bounds` | 37e6b25 (+4 −1) | a branch in `_date_bounds`, which both callers share | KEEP | one path; a child of REBUILD 7244f63 |
| `eval-provenance-crashes-on-stray-link` | 4639a44 (+1 −1) | a callable `ignore` | KEEP (superseded) | 85ad011's `symlinks=True` replaced it |
| `eval-shim-record-overwritten-by-child-process` | 06121c3 (+4 −1) | the forked-child bug followed on the same lines | KEEP (corrected by 0e8a9c4) | the env pop alone missed the fork |
| `eval-provenance-copy-loops-on-directory-links` | 85ad011 (J4.T4), pin 09ab567 | none | KEEP | the rc-4 REBUILD; the record's 1f47ff8 and 240a98f are pre-sync shas (row 149) |
| `eval-shim-record-overwritten-by-forked-child` | 0e8a9c4 (+2 −2) | none | KEEP | `_check.py:37,116` is the one owner decider |
| `speed-gate-fails-on-runner-noise` | cd775e9 (+5 −3), pin ecb5f00 | none; the pin covers the head half only | KEEP | one statistic, `min`, on both sides (`benchmarks/speed.py:309,311`); RUNS, LIMIT and the interleaving unchanged; AC30.1 adds the base partition |
| `eval-provenance-refuses-absolute-in-workdir-link` | 162fa1d (+2 −2) over b9b3aee (+8 −5); RED 6b368a1, e1f04ff, 4269659 | a retarget loop in the scratch copy (`_check.py:183-186`), +4 lines, after two rejected deciders: f65d886 judged containment on the work dir (the re-run wrote into the original), b9b3aee compared raw link text (an alias escaped it) | KEEP | one cause, a link in the copy must keep its meaning, and one `realpath` decider; no assert loosened (4269659 parametrizes the spelling); outside links stay refused (CWE-59). Its second spelling, `:187`'s `.resolve()`, is AC32.9 |

## 1. Problem

- The writers decide each format's accepted options twice (`rand_engine/file_handlers/file_handler.py:125/:387`, `:211/:397`, `:293/:407`). No test goes red if one copy drifts, so 4e1cdf1 had to edit both by hand.
- The speed gate's base half has no partition: `Fake` answers base 1.0 on every sample (`tests/test_benchmarks.py:172-175`), so `statistics.median` back at `benchmarks/speed.py:311` still passes. `docs/benchmarks.json:2` still records d577ed0.
- Eval harness lines hide their cause:
  - a copy failure reads "the script could not re-run: Error" (`evals/_check.py:194`);
  - `gate.py --calibrate` crashes with `FileNotFoundError` when results are missing (`evals/gate.py:117`, Agent Eval 43036600243);
  - a non-integer K passes the K guard (`.github/workflows/eval.yml:145`);
  - `run.py` reports "no init event: None" (`evals/run.py:134`).
- Eval docstrings and names say less than the code; `read_artifact` keeps an inert sort (`_check.py:137`).
- Tests claim what they do not assert (`tests/test_9_cli.py:177`), carry AC, FR and bug ids, match loosely, mock the module's own function (`tests/integrations/test_public_api.py:853`), and run 13 reference trials where one per slug does.
- Docstrings, one docs sentence and one CHANGELOG bullet say more or less than the code.

## 2. Measurable goals

- Each writer format's accepted options live in one tuple, and a test goes red when one path drifts.
- Putting `speed.py:311` back to `statistics.median` turns `tests/test_benchmarks.py` red.
- No eval harness failure surfaces as a traceback or an unnamed cause.
- `tests/integrations/test_eval_tasks.py` runs one reference trial per slug, timed against today's 31-102 s.
- Every Origin item lands, or Non-goals names it.

### Wave ranking

| wave | scope | FRs |
|---|---|---|
| 1 — law, skills and dev loop | the speed gate's base partition | FR30 (AC30.1, AC30.2) |
| 2 — shared foundation | one accepted-options decider per writer format | FR31 |
| 3 — features and bugs | eval harness, the get-started-cli check, docstrings | FR32, FR33, FR34 |
| 4 — promote-facing | test hygiene, the benchmark record, closure | FR35, FR36, FR37, AC30.3, FR38 |

AC30.3 waits for FR31's merge, since FR31 touches a measured path.

## 3. Non-goals

- `shared-verify-venv-platform` (rejected: +1.06 s per verify run; rows 16-19 stand as ceilings). The `verify:` line does not change.
- `date-format-one-source` (rejected: no route leaves the frozen `gen_*` bodies untouched).
- `dates-time-directives-perf`: 0.9.0's.
- Any `gen_*` body (invariant 12); any `rand_engine/` edit made for the eval alone.
- The `_check.py` code rows 27, 40 and 80, and entry 4 item 5 (row 81, already holds).
- A ninth rewrite of the `get-started-cli` matcher (ruling 119).
- A minimum duration per benchmark sample.
- Retiring the AC20 tombstones (`tests/test_9_cli.py:156,204-205`): after 0.8.2 ships.
- `test_eval_tasks.py:59-62` and `:70-73` stay (row 88).
- Any change that breaks compatibility (grammar, seed, error format, default, exported name): 0.9.0's.
- A PyPI publish or a tag of 0.8.2 ("Nada publica até a 1.0 (Recommended)"); closed-candidate text stays history.

## 4. Requirements

### FR30 — The speed gate's base partition and the benchmark record (`speed-gate-noise-floor`)

- AC30.1 (unit, `tests/test_benchmarks.py`): `Fake` takes a `bases=` tuple like `heads=`. The parametrize at `:188-192` gains the row `bases=(1.0, 3.0, 3.0)`, `heads=(1.4, 1.5, 1.6)`, expecting `"over 1.3x base: [('integers', 10)]"`. With `speed.py:311` back to `statistics.median`, that row fails.
- AC30.2 (no test; read on the diff): `speed.py:309-311` keep min-of-three on both sides; RUNS, LIMIT and the interleaving are unchanged. A CI red from the gate is registered as its own bug.
- AC30.3 (integration, the committed-artifact tests `tests/test_benchmarks.py:337-351`): `docs/benchmarks.json` and `docs/BENCHMARKS.md` hold, byte for byte, the CI artifact of the Benchmarks run on rc-5's last head that touches a measured path (`benchmarks.md:44`). FR31 touches `rand_engine/file_handlers/`, so this supersedes run 43036665165 (`feature/0.8.2` at df1b8d7, success). The record commit adds only `docs/` and `tests/`.

### FR31 — Each writer format decides its accepted options once (`writer-options-one-decider`, REBUILD)

- AC31.1 (unit, `tests/test_5_files_write_batch.py`, `tests/test_5_files_write_stream.py`): for csv, json and parquet, an undocumented option is refused with the full literal `<format> option '<key>' is not documented; accepted: <list>` on the batch path (`write…save`) and the stream path (`writeStream…start`). The test goes red when one format's list changes on one path only.
- AC31.2 (no test; read on the diff): `file_handler.py` holds one accepted-options tuple per format. The constructors (`:125`, `:211`, `:293`) and `FileHandler.to_csv`, `to_json`, `to_parquet` (`:387`, `:397`, `:407`) both read it; the `to_*` functions add only the writer's own keys. Every message, exception class and accepted list is unchanged, and the file's net lines are ≤ 0.
- AC31.3 (unit; pending the operator's order in the approval question): the two json `indent` tests (`test_5_files_write_batch.py:271-281`) fold into AC31.1's json rows with the option `indent`, keeping their full literals and their `not path.exists()` asserts. Without the order they stay.

### FR32 — Eval harness hygiene 2 (`eval-harness-hygiene-2`)

- AC32.1 (integration, `tests/integrations/test_eval_check.py:393`): a copy failure prints one `provenance` line naming the copy step and the unreadable file, pinned as the full literal (`_check.py:194`).
- AC32.2 (no test; docstring text): `origin()` (`_check.py:39-40`) says it reads any frame local named `tag`; the `provenance` docstring (`:154-159`) names the outside-the-work-dir refusal.
- AC32.3 (integration, the existing `test_eval_check.py` and `test_eval_tasks.py` cases, asserts unchanged): `agent()` (`:148`), `hashed()` (`:56`) and `record` are renamed for what they hold or do. Consumers: `_check.py:3,199,201`; `_check.agent` in the checks of `templates-and-examples:54`, `pk-fk-constraints:44`, `generation-methods:35`, `rand-spec-grammar:32`, `spark-generator:40`, `data-generator:37` and `writers-and-streaming:29`; `evals/README.md`.
- AC32.4 (no test; doc text): `evals/README.md:18` says an artifact column must match output of the agent's own code; `:50` lists `final_message`, `first_failure` and the `tokens unknown` cell; `:61-65` names the per-variant transcript fixture.
- AC32.5 (integration, the `run.py` contract tests in `test_public_api.py`): a failing check that also prints a malformed `RESULT` line keeps `first_failure` (`run.py:152-154`). A stream with no result event raises naming the missing result event, never "no init event: None" (`:134`).
- AC32.6 (integration, `tests/integrations/test_eval_gate.py` and the workflow-text tests):
  - `gate.py` decides "passed and no error" once (`:80`, `:86`);
  - `gate.py --calibrate` with a missing results directory names the missing results and exits non-zero, never with a `FileNotFoundError` traceback (`:117`);
  - the K guard (`eval.yml:145`) fails closed on a non-integer K.
- AC32.7 (integration, the `pk-fk-constraints` reference and decoy trials in `test_eval_tasks.py`): `pk-fk-constraints/tests/check.py` reads no private `Keys._pk_at` (`:16,51,55`), and its pass and fail cases are unchanged.
- AC32.8 (integration, `test_eval_check.py`; a deletion on the operator's order "Delete sort + pin (Recommended)"): the content-order sort in `read_artifact` (`_check.py:137`) and its docstring clause (`:133`) are deleted with their pin `test_parts_directory_frame_does_not_depend_on_part_names` (`:127-133`). `test_spark_parts_directory_skips_hidden_files` (`:117`) stays green.
- AC32.9 (integration, the link and loop tests of `test_eval_check.py:265-357`): `provenance` resolves paths with one spelling (`_check.py:160,184,187`), and every link and loop test stays green.
- AC32.10 (no test; read on the diff): no `rand_engine/` file changes; rows 27, 40 and 80 get no code edit; `evals/_check.py` ends at most 266 lines, one under adba94f's 267 (row 143; §6).

### FR33 — The get-started-cli check's ceilings (`get-started-cli-check-ceilings`)

- AC33.1 (no test; docstring text): the `Ceilings:` sentence (`evals/tasks/get-started-cli/tests/check.py:43`) lists the four ruled ceilings of intake rows 115-116, one clause each.
- AC33.2 (unit, the matcher's accept cases, `test_eval_tasks.py:176-202`): `rand-engine get-started --out=starter lake` is accepted, and dropping the `--out=VALUE` handling at `check.py:54` turns it red.
- AC33.3 (no test; read on the diff): the `any(...)` continuation (`:70-71`) is indented under its opening. Every other accept and refuse case is unchanged.

### FR34 — Docstring and doc accuracy (`docstring-accuracy-follow-ups`)

- AC34.1 (no test; docstring text, under the `ruff D` check and the doctests):
  - the Raises sections at `rand_engine/file_handlers/_writer_batch.py:364` and `_writer_stream.py:82` use the `resolve_size` wording (`data_generator.py:36`);
  - `rand_engine/main/_rand_generator.py:37` reads "an empty unicode ndarray";
  - the `ColumnGenerationError` docstring (`rand_engine/validators/exceptions.py:53-58`) states its three steps once.
- AC34.2 (no test; doc text read against the directive check): the timezone sentence (`docs/1_DATA_GENERATOR.md:91`) leaves the `dates` paragraph, since `%z` with `dates` fails the directive check.
- AC34.3 (integration, the dated-header test in `tests/test_docs.py`): `CHANGELOG.md:34`'s size bullet names that `SparkGenerator` now takes a callable size, where 0.8.1 raised a raw `TypeError`. It lands in a task, since no closure shape covers `CHANGELOG.md`.

### FR35 — The CLI starter tests say what they assert (`cli-starter-test-names`)

- AC35.1 (unit, `tests/test_9_cli.py`): the starter test (`:166-200`) is named for what it asserts. Its rows are `(slug, expectation)` with each starter's true notebook expectation: `lake`, `kafka`, `faker` and `databricks` start with `# Databricks notebook source` (`get-started-cli.md:34`). The ids come from the rows, not by position (`:175`).
- AC35.2 (unit, same file): the Spark fixture is driven by its own parameter, not the notebook label; the body branches on no slug (5 `if` and a `try/finally` today, `:178-200`). No assert is removed.
- AC35.3 (unit, same file): the Arrow conf assert runs after the starter and before any restore, so it pins the starter (AC20.1), not the test's own restore (`:197-200`). `ARROW_CONF` and its save and restore have one home, shared with `tests/test_3_spark_generator.py:696-706`.

### FR36 — Library test hygiene (`library-test-hygiene`)

- AC36.1 (unit, `tests/test_docs.py:1044`): a page with front matter but no `description:` line fails naming the page, not with `AttributeError`.
- AC36.2 (unit, `tests/test_5_files_write_stream.py:136`): the `writeStream` unset-size test pins the full literal "No size set: call .size(n) with an int or a callable returning one.".
- AC36.3 (no test; a sweep): `git grep -nE '\b(AC|FR)[0-9]+' -- tests/` prints nothing (25 hits at 162fa1d), and no bug id names a test's contract (`tests/test_2_data_generator_fails.py:180`, `tests/test_5_files_write_batch.py:1`). Each test states its contract in place of the id.
- AC36.4 (unit, `tests/test_0_np_core.py`): the zero-size `uuid4` and `int_zfilled` partition (`:419-428`) moves into the owner contract tests (`:192-212`, `:398-413`) with ids that name the method. One assert goes red when `_np_core.py:103` is deleted. No assert is removed.
- AC36.5 (unit; names and helpers, asserts unchanged):
  - the aware-bound case (`tests/test_1_common_validator.py:864-865`) builds its spec with `_date_spec` (`:284`), sits with the date-bound tests and is named for its asserts;
  - `test_spark_zero_callable_size_skips_the_eligibility_check` (`tests/test_3_spark_generator.py:680`) is named for its asserts, an empty frame that keeps the fk column;
  - the dead `"indent"` literal at `tests/test_docs.py:592` goes.

### FR37 — Eval test hygiene (`eval-test-hygiene`)

- AC37.1 (no test; text): `test_eval_check.py:16` says eight legacy items, as `LEGACY` holds (`_check.py:230-239`).
- AC37.2 (integration, `test_eval_check.py:168-179`): the repeated-call case asserts the record list, so a duplicate record fails; today it compares a set.
- AC37.3 (integration, `test_public_api.py`):
  - the test at `:853` replaces a boundary, not `run.run_trial`;
  - `:912` accepts only the guard form `eval.yml` ships;
  - `:848` expects one literal per case, with no conditional;
  - the concurrency test (`:954`) pins `cancel-in-progress`.
- AC37.4 (integration; pending the operator's order in the approval question): the malformed-result test (`:823`) asserts `passed` is false, and its repeat at `:830` folds into it. Without the order both stay.
- AC37.5 (no test; names): the tests at `test_public_api.py:948` and `test_eval_gate.py:222` are named for their asserts.
- AC37.6 (integration, `test_eval_check.py`): a case pins the full "exited N on re-run" line (`_check.py:196`), and the file's net lines for this item are ≤ 0.
- AC37.7 (integration, `test_eval_tasks.py`; timed): one reference trial per slug, its file wall time quoted against today's 31-102 s. The child env is built once (`:85-86`, `:107-108`, `:227-228`), the unused runner goes (`:114`, `:125`), `:144` takes its expected literal from the case, not the slug, and the get-started fixture stops exec-ing the whole `check.py` (`:166-169`).
- AC37.8 (integration, same file; a deletion on the operator's order "Replace :52-55, keep rest (Recommended)"): first, a case per usage slug asserts that its reference trial ends in a `RESULT` line that `evals/run.py` `check_result` (`:86`) reads as layer `pass` with its `surfaces`. Then `test_usage_check_prints_one_pass_line_with_layer_and_surfaces` (`:52-55`) is deleted, its `test(` commit quoting the order.
- AC37.9 (integration; pending the operator's order in the approval question): `test_absent_artifact_fails` (`test_eval_check.py:359-361`) folds into `test_absent_artifact_message_is_pinned` (`:376-377`), which keeps the full literal. Without the order both stay.

### FR38 — Closure: memory, the record and CHANGELOG

- AC38.1 (closure memory pass, `pe`, from the final diff):
  - `agent-eval.md:41` says what the code reads: artifacts strictly as UTF-8 (`_check.py:143,145`), and only the task checks' reads of agent-written files ignore undecodable bytes (row 154);
  - the `agent-eval` atom states the scratch copy's link rule and records a Windows junction, copied by value, as a ceiling (row 162);
  - an atom that names a writer's accepted options, a renamed `_check.py` name or the speed gate's estimator matches the code;
  - `catalog.json` is regenerated by `catalog generate`.
- AC38.2 (no test; rc-5's closure summary, since the log is append-only):
  - `eval-provenance-copy-loops-on-directory-links` was fixed by 85ad011 (J4.T4), pinned by 09ab567; 8ca6930 is its resolve commit (row 150);
  - fea0101's and 674cb8d's bodies are rebase leftovers of the J7.T3 stop (row 131), and b9603bd's move is ordered by the rulings file `2026-11-07T231500Z`, "J9.T2, the AC21.5 fold" (row 137);
  - `eval-provenance-refuses-absolute-in-workdir-link`'s true solution is 162fa1d's one `realpath` decider, not the text comparison its write-once `solution` names (row 161).
- AC38.3 (integration, the dated-header test in `tests/test_docs.py`): `## [0.8.2]` gains an entry only for a user-visible change rc-5 lands. FR31 keeps every message, so AC34.3's bullet is the only CHANGELOG edit.
- AC38.4 (no test): the closure summary quotes AC30.3's run id, AC37.7's wall times and `evals/_check.py`'s line count against AC32.10.

## Replaces

- The second accepted-options list per format (`file_handler.py:387,397,407` against `:125,211,293`) → AC31.2. Consumers: the batch writer (`_writer_batch.py:300-302`), the shared writer map (`writer.py:36-38`) and `test_5_files_write_batch.py:253-260,271-281`; the message is unchanged.
- `read_artifact`'s content-order sort (`_check.py:133,137`) and its pin (`test_eval_check.py:127-133`) → AC32.8. No consumer of its frame reads row order (as-is review §4).
- The copy failure's "the script could not re-run: Error" → AC32.1. Consumers: `test_eval_check.py:393`, `run.py`'s `first_failure`.
- The names `agent()`, `hashed()` and `record` → AC32.3; consumers there.
- `gate.py`'s two "passed and no error" tests and its calibrate crash, and the K guard that passes a non-integer → AC32.6. "no init event: None" → AC32.5.
- The pk-fk check's reach into `Keys._pk_at` → AC32.7. The second path-resolution spelling in `provenance` → AC32.9.
- `test_usage_check_prints_one_pass_line_with_layer_and_surfaces` (`test_eval_tasks.py:52-55`) → AC37.8; the three env builds, the unused runner, the whole-check exec and the reference trials beyond one per slug → AC37.7.
- `test_9_cli.py`'s slug branches, positional ids and second `ARROW_CONF` → AC35.1-AC35.3; the standalone zero-size test (`test_0_np_core.py:419-428`) → AC36.4.
- Only on the operator's order: the json `indent` tests → AC31.3; `test_public_api.py:830` → AC37.4; `test_absent_artifact_fails` → AC37.9.

## 5. Constraints and risks

| risk | control |
|---|---|
| No public surface exposes the pk defaults that AC32.7 needs | the job returns to the main thread; no `rand_engine/` edit |
| `evals/_check.py` carries 8 of the rc-4 window's 12 bugs | entry 4 is narrowed to text, names and messages; any other code change returns to the main thread |
| Shared files: `test_eval_tasks.py` (FR32, FR33, FR37), `test_eval_check.py` (FR32, FR37), `test_public_api.py` (FR32, FR37), `test_5_files_write_batch.py` (FR31, FR36), `test_docs.py` (FR34, FR36) | the PLAN gives each file to one job, or orders the jobs |
| AC30.3 needs a Benchmarks run on rc-5's last measured head | dispatched on the `wt-rc` after FR31 merges; a red is its own bug |

- The open CRITICAL `setuptools-ghsa-xmj3-open-on-master` closes at the 0.8.2 `master` merge, not in rc-5.

## 6. Open questions

For the main thread; none blocks the PLAN.

1. **Test removals.** Row 152 (AC37.9) is in the grill's approval question. Rows 23 (AC31.3) and 52 (AC37.4) also remove a test function, and the grill record does not list them. They are written as pending the same order.
2. **AC32.10's bound.** The entry asks for one line under adba94f (267 lines, so ≤ 266). The abs-link REBUILD then added 4 lines (162fa1d), and HEAD holds 272. Text-only items must now remove 6 lines. If that is out of reach, the alternative bound is net ≤ 0 against 162fa1d. The main thread rules; the SPEC carries the entry's bound.
