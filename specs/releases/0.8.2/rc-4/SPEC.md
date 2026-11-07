# SPEC — Release: 0.8.2, candidate 4 (the refined backlog, compatible changes only)

**Status:** Draft
**Release ID:** 0.8.2
**Owner:** dd-product-engineer
**Opened:** 2026-11-06
**Origin:** backlog:spark-java17-options-dead,test-docstring-hygiene,text-perf-follow-ups,shared-verify-venv,eval-harness-hygiene,eval-task-checks,error-text-accuracy,validator-leftovers,spark-callable-size

- Invariant 12, operator verbatim, 2026-11-05: "Aprovo gen_uuid4 (Recommended)". The operator approves by name `NPCore.gen_uuid4` (`rand_engine/core/_np_core.py:132-140`): its hex step moves from `bytes.hex().encode()` to `binascii.hexlify`, in the operator's style (2-space indentation, one-line guards, terse NumPy). No other `gen_*` body changes.
- Sources: the grill handoff `2026-11-06T004854Z-main-thread-grill-0-8-2-rc4`; the as-is review `2026-11-05T130306Z-dd-sw-engineer-sr-rc4-as-is-review`; the backlog-lane review `2026-11-05T130507Z` (APPROVED). Every `path:line` is a `99821e9` anchor; the PLAN re-greps it.
- FR numbers continue the release: rc-4 owns FR19–FR29. Not an ADR: every change is reversible and keeps compatibility.

### Grill rulings, operator verbatim

| ruling | answer | meaning |
|---|---|---|
| Scope | "devemos fazer tudo absolutamente todo trabbalho que ja definimos e refinamos agora" | rc-4 takes every item defined and refined before 2026-11-05 that keeps compatibility |
| Release vehicle | "Nada publica até a 1.0 (Recommended)" | 0.8.2 merges to `master` with no PyPI publish and no tag, since one live release (`specs/releases/AGENTS.md` §1) must close before 0.9.0 opens; the operator publishes at 1.0 |
| Invariant 12 | "Aprovo gen_uuid4 (Recommended)" | FR26 |
| Summary and test deletion | "Confirmo, apagar os 2 (Recommended)" | the two deletions of AC21.6 and AC23.5; each `test(` commit quotes this order |

### Answered by inspection (main thread)

- Eval shim REBUILD: no library source edit; net lines of `evals/_check.py` ≤ 0; where the record is taken is the PLAN's.
- Spark eval task: `pyspark>=4`, since `docs/compatibility.md:19-20` pairs Spark 4.x with Python 3.12, which `eval.yml` runs. Only the task's `setuptools` pin goes. The library pin (`pyproject.toml:52`) stays: it closes `setuptools-ghsa-xmj3-open-on-master` at the `master` merge.
- PR to `master`: a concurrency group only. A `paths` filter stays forbidden (rc-3 FR16): a skipped workflow leaves a required check pending.
- N5 is true: one docstring line at `rand_engine/validators/method_specs.py:213-214`. N13 folds by parametrizing the inference option; both partitions stay and no assert is removed.
- `shared-verify-venv` is measured before the operator rules, since the `verify:` line is a gate (root map §1).
- Corrections from the backlog-lane review: `error-text-accuracy` item (1) is already done (`rand_engine/validators/exceptions.py:16-18`, `f95c678`, `e2aeead`); item (6) cites `docs/errors.md:16`.

### What the operator must see

- The `verify:` lines change only after the operator rules on FR19's measured costs.
- Two tests are deleted on the operator's order (AC21.6, AC23.5).
- The `master` merge starts `auto_tag_publish_master.yml`. 0.8.2 has no tag, and `check_tag` skips only when the tag exists, so `publish_pypi` waits on the `production` environment. Per "Nada publica até a 1.0 (Recommended)", the operator rejects that deployment. No tag is created, since `create_tag` needs the publish.

## Bug window review

Prior candidate: rc-3, with two resolved bugs. One bug is open: `setuptools-ghsa-xmj3-open-on-master` (CRITICAL), fixed on the work branch, which closes at the 0.8.2 `master` merge. Each fix was read with `git show --stat --patch` (as-is review §2).

| bug | fix | pattern hit | verdict | why |
|---|---|---|---|---|
| `discovery-adoption-never-reported` (HIGH) | `e5502a0`, `evals/gate.py` +11 −1; RED `b737e12` first | a third walk over the trial records in `main` | KEEP | the RED test (`tests/integrations/test_eval_gate.py:249,261`) is literal; no assert changed, no test value special-cased, nothing deleted, no reach-in. Its `None` surface (`gate.py:109`) is AC23.3, an UPDATE of the same lines |
| `eval-checkout-persists-token` (LOW) | `c6c9fa8`, `eval.yml` +6; RED `95ba249` first | none | KEEP | `tests/integrations/test_public_api.py:972` asserts every checkout step, not a count. The other workflows run no unsandboxed agent, outside the bug's component |

## 1. Problem

- The eval provenance shim (`evals/_check.py:27-104,145-194`) took five unledgered reworks in rc-3 J4.T2 (`b3cb8ef`, `dd45e0c`, `26c01a4`, `17d9571`, `cd24fd7`). It collects evidence per entry point:
  - four wraps each record the spec;
  - two reach into `size_def.__self__` (`:61,70`);
  - two out-params carry the result (`:145`);
  - any frame counts, so a decorative `DataGenerator` call beside numpy-written data passes (`generation-methods` check `:36-37`, `data-generator` `:38`).
- An errored eval trial keeps `passed: true` (`evals/run.py:149,155`), and its record has no final message. The task checks print the pass line three ways.
- The `verify:` line (`AGENTS.md:51`) builds a ~0.66 GB virtualenv per worktree path; `verify-stage:` and `verify-task:` (`:52-53`) copy it, read by nothing. On 2026-10-20, 70 orphans (43 GB) filled the disk. The local stack (pandas 2.2.3, pyspark 3.5.8) differs from most CI legs (pandas 3.1.0, pyspark 4.3.0).
- The validators restate the date default, leak a raw `TypeError`, hide template errors behind an early return, and are reached through a private `_raise`.
- The test Spark session carries Java 17 options that no Java 17 run needs, and the databricks starter leaves an Arrow conf on the shared session, so Spark tests depend on order.
- Docstrings, CHANGELOG lines and test names say more or less than the code.
- `gen_uuid4` builds ~640 MB of temporaries at 10M rows.

## 2. Measurable goals

- A decorative call beside numpy-written data fails layer 2. `evals/_check.py` records each generation once, with net lines ≤ 0.
- No eval trial that raised reads `passed: true`.
- The operator rules on the `verify:` line from 3 cold and 3 warm runs of each line.
- `gen_uuid4` returns identical bytes for every seed.
- Every Origin item lands, or Non-goals names it.

### Wave ranking

| wave | scope | FRs |
|---|---|---|
| 1 — law, skills and dev loop | the `verify:` measurement, the Java 17 options, test and docstring hygiene | FR19, FR20, FR21 |
| 2 — shared foundation | the eval provenance REBUILD | FR22 |
| 3 — features and bugs | eval records and workflow, eval task checks, validators, `gen_uuid4` | FR23, FR24, FR25, FR26 |
| 4 — promote-facing | error texts, the Spark callable size, closure | FR27, FR28, FR29 |

FR23 and FR24 consume FR22's record, so wave 3 waits for FR22's merge.

## 3. Non-goals

- `text-perf-follow-ups` item (1), dates with time directives: 0.9.0's. It is re-judged after `native-datetime-output`, and `gen_dates` has no by-name approval.
- `error-text-accuracy` item (1): already done.
- Closed-candidate text stays history (`specs/releases/AGENTS.md` §2, a closed candidate is never amended): `rc-1/tasks/job1.md:9`, rc-1 SPEC `:9,:169`, rc-3 SPEC AC11.4 and `rc-3/tasks/job6.md:7-9`, which the rc-3 reconcile missed.
- Any change that breaks compatibility (grammar, seed, error format, default): 0.9.0's.
- A PyPI publish or a tag of 0.8.2 ("Nada publica até a 1.0 (Recommended)").
- The library's `setuptools` pin; a `paths` filter on the PR to `master`; a `verify:` line heavier than today's; `persist-credentials` on workflows that run no agent.
- Any `gen_*` body but `gen_uuid4`; any `rand_engine/` edit made for the eval alone.
- `echo rand-engine …` passing AC24.2 as a launcher prefix (LOW): RULED, accepted, by the pre-mortem J7 ruling.

## 4. Requirements

### FR19 — One shared verify environment, measured before the ruling (`shared-verify-venv`)

- AC19.1 (no test; a measurement report with its sources): 3 cold and 3 warm wall-clock runs of the current `verify:` line and of the shared-environment line. Cold means no environment exists; warm means it exists. The report names the pandas and pyspark pairing the shared environment pins, against the CI legs.
- AC19.2 (no test; the operator's ruling): the `verify:` line (`AGENTS.md:51`) changes only after the operator rules on AC19.1's numbers, and never to a line heavier per run than today's, cold against cold and warm against warm. Without the ruling it stays.
- AC19.3 (no test; read back): after the change, a `verify:` run in a second worktree creates no new virtualenv.
- AC19.4 (no test; a text deletion no program reads): the dead `verify-stage:` and `verify-task:` lines (`AGENTS.md:52-53`) are deleted. Only `verify:` is read, so this is not a gate change.

### FR20 — Dead Java 17 options and the leaked Arrow conf (`spark-java17-options-dead`)

- AC20.1 (unit, `tests/test_9_cli.py`): after the databricks starter runs on the shared test session, `spark.sql.execution.arrow.pyspark.enabled` holds the value it had before.
- AC20.2 (unit, the Spark suite on CI's Java 17): the test session builder (`tests/fixtures/f2_spark_generator_specs_right.py:35-51`) sets no netty reflection flag and no `--add-opens`, and the three Arrow tests pass. This amends the 0.8.1 AC2.8 contract by a test change.
- AC20.3 (unit, the scaffold tests): `rand_engine/cases/databricks.py.txt:39` and `docs/tutorials/databricks.md:35` carry no netty sentence.

### FR21 — Test and docstring hygiene (`test-docstring-hygiene`)

- AC21.1 (unit, the renamed tests): the tests at `tests/test_2_data_generator.py:424,628` are named for what they assert (`pd.NA`, Arrow text); their asserts are unchanged.
- AC21.2 (unit, `tests/test_docs.py`):
  - `_docs_site_module` and its `importlib.util` import (`:968-972,4`) are gone; they have no caller;
  - a message after fence stripping keeps the page's line numbers (`:1033-1035`);
  - a page without front matter fails naming the page, not with `AttributeError` (`:1050-1051`).
- AC21.3 (no test; text that no program reads):
  - `RandGenerator._column` (`rand_engine/main/_rand_generator.py:37`) drops "never empty" and says the Arrow branch wraps any Arrow type;
  - `tests/test_0_np_core.py:399` states its contract instead of "AC4.5", and the "Pinned from 0.8.0" comment moves to the `_draw` test it describes (`:126`);
  - the stale comment at `.github/workflows/benchmarks.yml:37` is corrected;
  - `tests/integrations/test_eval_check.py:8` states its contract instead of "F6";
  - `method_specs.py:213-214` says only object columns reach the inference path (N5).
- AC21.4 (unit): `tests/test_9_cli.py:172-176` parametrizes (slug, expectation) with no slug branch. The fixture writes at `tests/integrations/test_eval_gate.py:28,37` use UTF-8.
- AC21.5 (unit, `tests/test_3_spark_generator.py`): N13. The text-with-none case (`:739`) and its `future.infer_string` twin (`:780-784`) become one test parametrized over the option. Both partitions run; no assert is removed.
- AC21.6 (unit; a deletion on the operator's order "Confirmo, apagar os 2 (Recommended)"): first, the unset-size asserts at `tests/test_2_data_generator_fails.py:179-182` (`get_df`) and `tests/test_5_files_write_batch.py:188-194` (`save`) are tightened from `.size(n)` to the full message literal. Then `tests/test_2_data_generator.py:713-719` keeps only its `stream_dict` case, which still asserts the full literal. The message has one source, `resolve_size`.

### FR22 — Eval provenance: one record per generation (`eval-harness-hygiene` items 10-20)

- AC22.1 (integration, `tests/integrations/test_eval_check.py`): a numpy-written artifact beside a decorative `DataGenerator` call fails layer 2 (`provenance`). The same artifact written by the agent script's own rand-engine call passes.
- AC22.2 (integration, same file): one provenance record per generation, with no out-params. Every `DataGenerator` path records once (`get_df`, `stream_dict`, `write…save` sqlite included, `writeStream…start`), and so does `SparkGenerator.get_df`. The record holds the spec, the entry point and whether the calling frame is the agent script's. `calls`:
  - the entry points form a deduplicated set;
  - sqlite maps to `save`;
  - the `save` read-back stays only if a test shows that written text differs from the generated frame.
- AC22.3 (integration, same file): layer 2 matches the graded artifact only to output that an entry point called by the agent script returned or wrote, and the record names that entry point. A writer that ran on other data does not make a numpy-written file pass.
- AC22.4 (integration, same file):
  - an append-mode `write.save` artifact passes;
  - the "was not delivered" message is pinned by its exact text (`_check.py:186`);
  - a variable outside `RERUN_ENV` is absent from the re-run's environment;
  - a symlink in the work directory is copied as a link, and a copy failure reports as `provenance`, not as a harness error.
- AC22.5 (integration, same file): every failure line starts with its layer, once, with no caller repeating it.
- AC22.6 (no test; read on the diff):
  - no `rand_engine/` file changes;
  - `evals/_check.py` has net lines ≤ 0 and no `size_def.__self__` reach-in;
  - the spec is recorded in one place;
  - there is no `hasattr`/`getattr` pair (`:39`) and no conditional expression used as a statement (`:163`).

### FR23 — Honest trial records and workflow guards (`eval-harness-hygiene` items 1-9, 21)

- AC23.1 (integration, the `run.py` contract tests):
  - a trial whose run raises records `passed: false`;
  - the trial JSON holds the agent's final message and the check's first failure line;
  - the file is written as UTF-8 (`run.py:182`).
- AC23.2 (integration, same tests): a stream with no init event raises an error that names the result event's `errors` or `startup_failure_reason`, never a bare `StopIteration` (`run.py:131`).
- AC23.3 (integration, `tests/integrations/test_eval_gate.py`): a discovery trial with no surface counts as `other`, never `None`. A passing usage trial with unknown tokens prints `tokens unknown`, never `-`.
- AC23.4 (integration, the workflow-text tests, hardened and never loosened): `eval.yml`'s `pull_request` trigger has a concurrency group and still no `paths` filter. The trials step fails when `k` is above 3. `apt-get update` runs before `apt-get install`, and the sysctl lift runs only where its key exists.
- AC23.5 (integration; a deletion on the operator's order "Confirmo, apagar os 2 (Recommended)"): the pin at `tests/integrations/test_public_api.py:854` asserts the `apt-get install -y bubblewrap socat` line and its place before `python evals/run.py`. The separate socat test (`:859-861`) is deleted; its assert lives on in the tightened pin.

### FR24 — Eval task checks (`eval-task-checks`)

- AC24.1 (integration, `tests/integrations/test_eval_tasks.py`): every usage `check.py` prints one pass-line shape carrying `layer` and `surfaces`, and fails through one `fail(layer, message)` signature.
- AC24.2 (unit, over each form below; integration, same file): `get-started-cli` splits each command quote-aware and accepts only:
  - the console-script basename `rand-engine`, with or without a launcher prefix;
  - `python -m rand_engine`;
  - `python -c` code calling the CLI `main`.

  The slug is the first positional after `get-started`. A missing transcript fails.
- AC24.3 (integration, same file): `pk-fk-constraints` compares the pk parent after filling the pk defaults (`rand_engine/core/_keys.py:61`), not as text.
- AC24.4 (integration, same file): the eight checks of the backlog item (7) read agent-written files ignoring undecodable bytes. Files the harness writes stay strict.
- AC24.5 (E2E, the no-agent self-check job): a decoy that writes numpy data beside a decorative `DataGenerator` call fails at layer 2.
- AC24.6 (integration, same file; E2E, the eval run): `spark-generator/task.toml` requires `pyspark>=4` and no `setuptools`. The unused pandas import of `spark-generator/tests/check.py:13` is gone. The spark selfcheck runs on pyspark 4 in the eval workflow on the rc's `wt-rc` push, before the rc merges.

### FR25 — Validator leftovers (`validator-leftovers`)

- AC25.1 (no test; a sweep): `method_specs.py:284,290` take the engine's default `date_format` (`_np_core.py:231,239`). In `method_specs.py`, `'%Y-%m-%d'` remains only in the doc examples (`:465,:479`).
- AC25.2 (unit, `tests/test_1_*`): a `start` and `end` where one is timezone-aware and the other naive return a validation message naming the column, never a `TypeError`.
- AC25.3 (unit, same files): a spec with a bad replacement and template errors reports all of them in one validation result (`advanced_validator.py:260-263`).
- AC25.4 (unit, same files; a sweep): `CommonValidator` exposes one public raiser. `DataGenerator` and `SparkGenerator` call it, nothing outside the validators calls `_raise`, and every message and exception class is unchanged. No exported name is added: `rand_engine.__all__` stays three names.

### FR26 — `gen_uuid4` and the zero-row partition (`text-perf-follow-ups` items 2-3)

- AC26.1 (unit, the seeded golden `tests/test_0_np_core.py:412`, run green on the old body first): `NPCore.gen_uuid4` returns identical bytes for each seed, its hex step is `binascii.hexlify`, and its body keeps the operator's style. The authority is "Aprovo gen_uuid4 (Recommended)".
- AC26.2 (no test; the CI speed benchmark): the `uuid4` row at 1M and 10M rows, base against head, is quoted with its run id, time and peak memory. Head stays within the benchmark's own limit.
- AC26.3 (unit, the owning contract tests `tests/test_0_np_core.py:192-212,398-413`): `uuid4` and `int_zfilled` with size 0 return an empty Arrow column.

### FR27 — Error texts say what the code does (`error-text-accuracy` items 2-6)

- AC27.1 (no test; docstring text, under the `ruff D` check and the doctests): the Raises sections at `data_generator.py:269,307` use the `resolve_size` wording (`data_generator.py:33-36`).
- AC27.2 (no test; docstring text): in `rand_engine/validators/exceptions.py`, the anomaly-dtype clause (`:12-14`) reads "the column's transformers (embedded or global)". The `ColumnGenerationError` docstring (`:52-57`) names the method call, the conversion and the multi-column unpack, as `docs/errors.md:16` does.
- AC27.3 (no test; text read against the measured source): `CHANGELOG.md:28`'s int64 clause reads "in a numeric pool"; `:39` names 0.8.0 as the measured version.

### FR28 — SparkGenerator's callable size (`spark-callable-size` items 1-4)

- AC28.1 (unit, `tests/test_3_spark_generator.py`): with a callable size, an fk whose first row has no eligible parent raises `RandEngineError` naming the column. A callable returning 0 yields an empty frame (`spark_generator.py:190-207`).
- AC28.2 (no test; docstring text): `SparkGenerator.size` (`:118`) documents an int or a callable returning one. The `get_df` Raises section (`:149-150`) uses the `resolve_size` wording.
- AC28.3 (unit, same file): the `seconds()` helper (`:234-237`) converts one way with no branch on the method; its asserts are unchanged.

### FR29 — Closure: memory and CHANGELOG

- AC29.1 (closure memory pass, `pe`, from the final diff):
  - `spark-generator.md:17` names the callable size (`spark-callable-size` item 5);
  - the `QUALITY.md` Spark-session line drops the Java 17 options, and the verify line follows FR19's ruling;
  - the `agent-eval` atom states the one provenance record, the trial record fields and the Spark task's `pyspark>=4`;
  - `catalog.json` is regenerated by `catalog generate`.
- AC29.2 (integration, the dated-header test in `tests/test_docs.py`): `## [0.8.2]` gains an entry for each user-visible change rc-4 lands (AC25.2, AC25.3). Eval, test and docstring changes get none.
- AC29.3 (no test): the closure summary quotes FR19's measurements and ruling, the AC26.2 run, and `evals/_check.py`'s net lines.

## Replaces

- The eval shim's four entry-point wraps (`get_df`, `save`, `start`, `stream_dict`; `_check.py:47-83`), each recording the spec, and the two `size_def.__self__` reach-ins (`:61,70`) → AC22.2.
- `provenance`'s two out-params, `specs` and `calls` (`:145,150-151,181-182`), and the SHIM comment that omits `calls` (`:27`) → one returned record (AC22.2). Consumers:
  - `tests/integrations/test_eval_check.py:147-149`;
  - the `check.py` of `writers-and-streaming:27`, `generation-methods:33`, `templates-and-examples:52`, `pk-fk-constraints:38`, `public-api:39`, `data-generator:34`, `rand-spec-grammar:30` and `spark-generator:40`;
  - `evals/README.md:18`.
- The frame-agnostic match that passes a decorative call (`_check.py:237-240`) → AC22.1, AC22.3.
- `result_text`'s `startswith(layer)` branch (`_check.py:262`) → AC22.5. Consumers: `run.py`'s `check_result`, `gate.py:83-85`, `test_eval_check.py`, `test_eval_tasks.py`, `evals/README.md`.
- The three pass-line shapes and five `fail()` copies of the task checks → AC24.1. No consumer reads the `PASS` word.
- `get-started-cli`'s substring command match and its transcript skip (`check.py:18-32,44`) → AC24.2. Consumers: `test_eval_tasks.py`, `evals/selfcheck.py`.
- The spark eval task pin `pyspark>=3.5,<4` and `setuptools>=84.1.0` (`spark-generator/task.toml:17`) → AC24.6.
- An errored trial's `passed: true` (`run.py:149,155`) → AC23.1.
- The private `CommonValidator._raise` reach-in (`data_generator.py:14,116`, `spark_generator.py:68`) → AC25.4; the PLAN greps the tests for `_raise`.
- The early return at `advanced_validator.py:260-263` → AC25.3; the raw aware/naive `TypeError` (`method_specs.py:291-292`) → AC25.2; the restated `'%Y-%m-%d'` (`:284,290`) → AC25.1.
- The test session's Java 17 options and the 0.8.1 AC2.8 test contract that requires them → AC20.2. The netty sentence → AC20.3; consumers: the `get-started databricks` scaffold bytes and `test_9_cli.py:172-176`.
- The Arrow conf the databricks starter leaves on the shared session → AC20.1.
- `gen_uuid4`'s `bytes.hex().encode()` temporaries (`_np_core.py:137`) → AC26.1.
- `_docs_site_module` and its import (`test_docs.py:968-972,4`) → AC21.2.
- The separate socat test (`test_public_api.py:859-861`) → AC23.5.
- The `get_df` and `save` cases of `test_2_data_generator.py:713-719` → AC21.6.
- The per-path virtualenv of the `verify:` line, only if the operator rules for the change → FR19. The dead `verify-stage:` and `verify-task:` lines → AC19.4.

## 5. Constraints and risks

| risk | control |
|---|---|
| The Spark generation cannot be recorded at `SparkGenerator.get_df` without a library edit | FR22's job stops and returns to the main thread; no `rand_engine/` edit for the eval (AC22.6) |
| Shared files across jobs: `test_0_np_core.py` (FR21, FR26), `data_generator.py`/`spark_generator.py` (FR25, FR27, FR28), `test_3_spark_generator.py` (FR21, FR28) | the PLAN gives each file to one job, or orders the jobs |
| AC20.3 changes the `get-started databricks` scaffold bytes | `test_9_cli.py` pins them; the PLAN answers the consumer list above |
| A local green differs from CI (version skew) | AC19.1 names the pinned pairing; CI on push stays the net |

- The open CRITICAL `setuptools-ghsa-xmj3-open-on-master` closes at the 0.8.2 `master` merge, not in rc-4.

## 6. Open questions

- None blocks approval.
  - FR19's ruling is due before its change merges, not before this approval.
  - AC21.6 tightens the `get_df` and `save` unset-size asserts to the full literal before the deletion, so no precision is lost.
