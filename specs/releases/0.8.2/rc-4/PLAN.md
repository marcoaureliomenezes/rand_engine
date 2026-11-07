# PLAN — Release: 0.8.2, candidate 4

**Status:** Draft
**Release ID:** 0.8.2
**Owner:** dd-sw-engineer-sr
**SPEC:** `rc-4/SPEC.md` (0f4819c)

Sources: as-is review `.dadaia/reports/rand-engine/2026-11-05T130306Z-dd-sw-engineer-sr-rc4-as-is-review.html` (base `99821e9`); the pre-mortem rulings `.dadaia/reports/rand-engine/2026-11-07T134824Z-main-thread-rc4-premortem-rulings.md`; the SPEC's operator rulings. Tree `worktrees/rand-engine/0.8.2/rc-4/wt-rc`. Every `path:line` was re-read at `0f4819c` (the define commits touch only `specs/`). Open bugs: `setuptools-ghsa-xmj3-open-on-master` only; it closes at the `master` merge and no rc-4 file touches its pin.

## 1. As-is review

Bug history = the ledger plus `git log -p` of each unit. Un-ledgered rework: the eval shim took five fix commits in rc-3 J4.T2 on a file born one rc earlier. The validator and Spark-pool rows took their REBUILDs (`1c3ddc2`, `89d1156`) and are only edited at the edges.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `evals/_check.py` SHIM + `provenance` (`:27-104,145-194`) | four wraps each re-derive the spec, two `size_def.__self__` reach-ins, out-params `specs`/`calls`, any frame counts | rc-3 J4.T2 reworks `b3cb8ef`, `dd45e0c`, `26c01a4`, `17d9571`, `cd24fd7` | REBUILD | evidence is collected per surface, without the caller's identity; a fix needs a layer (SLOP S5) |
| `evals/_check.py` `result_text` (`:260-263`) | `startswith(layer)` branch | none | UPDATE | dead: `grep -rnE '(fail\|result_text)\("[123]", *f?"[123]:' evals` has 0 hits |
| `evals/_check.py` other helpers | stable, tested | none | KEEP | `:186` text and append-mode `save` are pinned by tests, not source |
| `evals/run.py` `run_trial` | errored trial keeps `passed: true`; no final message; bare `StopIteration` (`:131`); `write_text` without encoding (`:182`) | `eval-token-reaches-agent-shell` REBUILD `f29b3e8` | UPDATE | the token env at `:113-117` stays |
| `evals/gate.py` `main` | `None` surface prints "None" (`:109`); unknown tokens print `-` (`:83-85`) | `discovery-adoption-never-reported` | UPDATE | same lines, no fourth walk |
| `.github/workflows/eval.yml` | no concurrency group, no `k` guard, no `apt-get update` | `eval-checkout-persists-token` | UPDATE | no `paths` filter (rc-3 FR16) |
| `evals/tasks/*/tests/check.py` (11) | three pass-line shapes, five `fail()` copies, strict reads | none | UPDATE | harmonised in place; nothing moves into `_check.py` (its net is ≤ 0) |
| `evals/tasks/get-started-cli/tests/check.py` | substring command match, transcript skip | none | REBUILD | one command decider rewritten |
| `evals/tasks/spark-generator/task.toml:17` | `pyspark>=3.5,<4`, `setuptools` pin | CRITICAL open (library pin only) | UPDATE | `pyspark>=4`, no `setuptools` |
| `CommonValidator._raise` (`common_validator.py:276`) | private, reached from `data_generator.py:116`, `spark_generator.py:68`, `advanced_validator.py:453` | `validated-specs-fail-in-generation` (`4cbdd5f`) | REBUILD | one public raiser; 0 hits for `\b_raise\b` in `tests/` |
| `method_specs.py` `_date_bounds` (`:284,290`), aware/naive (`:291-292`), docstring `:213-214` | restated default, raw `TypeError`, stale prose | `date-bound-parse-diverges-numpy-spark`, `date-format-required-but-docs-omit-it` | UPDATE | import the engine default; message instead of raise |
| `advanced_validator.py:260-263` | early return hides template errors | `distincts-map-empty-pool-validates` family | UPDATE | append and continue |
| `AGENTS.md:51-53` | `verify:` plus two dead copies | `shared-verify-venv` backlog | DELETE `:52-53`; `:51` UPDATE only after the ruling | gate law; nothing reads the copies (`_worktree_end.py:216-221`) |
| `tests/fixtures/f2_spark_generator_specs_right.py:35-51`, `databricks.py.txt:39`, `databricks.md:35` | dead Java 17 options and netty sentence | `spark-java17-options-dead` | DELETE | the Arrow conf at `databricks.py.txt:44` stays (user advice) |
| `tests/test_9_cli.py:165-176` | databricks starter leaves the Arrow conf on the shared session; slug branch | none | UPDATE | the test restores the conf; parametrize |
| `rand_engine/core/_np_core.py:137` `gen_uuid4` | `bytes.hex().encode()` | none | UPDATE | `binascii.hexlify`, byte-identical; approved by name (invariant 12) |
| zero-row `uuid4`/`int_zfilled` tests | no size-0 partition | none | UPDATE (tests) | added in the owning contract test |
| `tests/test_2_data_generator.py:713-719` + `_fails.py:179-182` + `test_5_files_write_batch.py:188-194` | repeated unset-size checks, `.size(n)` match | none | UPDATE / DELETE | tighten first, then delete two cases (operator order) |
| `tests/integrations/test_public_api.py:854-861` | unpinned line, duplicate socat test | `workflow-scan-test-reads-locale-encoding` | UPDATE / DELETE | tighten, then delete (operator order) |
| `tests/test_docs.py:4,968-972,1033-1035,1050-1051` | dead helper, shifted lines, `AttributeError` | none | DELETE / UPDATE | zero callers of `_docs_site_module` |
| docstrings (`exceptions.py`, `data_generator.py:269,307`, `spark_generator.py`), `CHANGELOG.md:28,39` | say more or less than the code | none | UPDATE | text |
| `tests/test_3_spark_generator.py` (`:234-237,739,780-784`) | `seconds()` branches; two twin cases; callable-size fk untested | `spark-text-pool-none-written-as-nan` REBUILD `89d1156` | UPDATE (tests) | the pool decider is KEEP |
| `text-perf-follow-ups` (1) dates with time directives | per-row loops | none | not touched | 0.9.0 |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| which rand_engine call produced the graded data (spec, entry point, whose frame) | the `_file_seam` hook in the `evals/_check.py` SHIM, plus the `SparkGenerator.get_df` wrap | `provenance`, 8 `check.py`, `test_eval_check.py` | `record_spec` x4, both `size_def.__self__` reach-ins, out-params `specs`/`calls`, `wrap_start` |
| layer prefix of a failure line | `result_text` | all `check.py` | the `startswith(layer)` branch |
| pass line and `fail` signature of a task | each `check.py`'s one `fail(layer, message)` and `RESULT` line | `test_eval_tasks.py` | the three pass shapes, the `surfaces=` parameter |
| how a validation error is raised | `CommonValidator.raise_validation(errors, engine)` | `validate_spark_and_raise`, `validate_and_raise`, `data_generator.py:116`, `spark_generator.py:68` | `_raise` |
| "size unset" wording | `resolve_size` (`data_generator.py:33-36`) | the Raises text of `get_df`, `stream_dict`, `SparkGenerator.get_df` | the "was not set" copies |
| default `date_format` | the engine signature (`_np_core.py:231,239`) | `method_specs.py:284,290` | the restated literals |
| `verify:` | `AGENTS.md:51` | the worktree merge (`_worktree_end.py:216-221`) | `verify-stage:`, `verify-task:` |

### 1.2 Design seams closed

**D1 — where the provenance record is taken (pre-mortem Row 1).** `DataGenerator._resolve_size` receives a size and never a frame, so it is not the hook. The hook is `DataGenerator._file_seam`, replaced from the shim by a wrapper that returns the same pair with its own `batch`. Proof, read at `0f4819c` and run in scratch (a copy of the shim idea, 6 calls, repo untouched):

- Every DataGenerator generation passes `_file_seam`: `get_df` (`:278`) and `stream_dict` (`:318`) reach it through `wrapped_df_generator` (`:171`); `write` passes it as `file_def` to the batch writer (`_writer_batch.py:224,329`, sqlite included); `writeStream` reaches it through `wrapped_df_generator` as `microbatch_def` (`_writer_stream.py:101,117`). `writer.save` binds `self._file_seam` at property access (`:354`), so a patch of the class attribute made before use is seen.
- Walking `sys._getframe` from the wrapper up through frames whose file lies in the `rand_engine` package, the outermost one names the entry point (`get_df`, `stream_dict`, `save`, `start`; sqlite and the multi-file path give `save`; a direct `wrapped_df_generator(n)()` gives `<lambda>`), and the next frame's file is the caller: equal to the re-run script, it is the agent's. Run result: `get_df`, `stream_dict`, `save` (csv), `save` (sqlite), `start` each report their name and `agent=True`.
- The evaluated spec is the sole argument of the first returned element, a `functools.partial(self._catalog_schema, evaluated_spec)` (`:132`): `seam[0].args[0]`. It needs no `hasattr`/`getattr` pair and no second evaluation of a lazy spec.
- `stream_dict` and `start` call the seam once per microbatch (3 calls for 12 rows in the run), so equal consecutive records collapse: the record is a set of distinct `(entry, spec, agent)`.
- `SparkGenerator.get_df` does not touch the seam (it builds from `spark.range` and `self.metadata`, `:72`); it keeps its existing wrap, which now takes the same record through the same helper. No `rand_engine/` edit.

**D2 — the save read-back stays (SPEC AC22.2 condition met).** In-memory frames cannot replace the read-back of what `save` wrote. Run result on `RandSpecs.customers()`: a csv artifact reads `['false', 'false', 'false']` where the generated frame holds `[False, False, False]` (bool), so their per-column hashes differ; with `maxRowsPerBatch=20`, 50 rows pass the batch closure as 3 batches while the artifact is one 50-row column. J4.T2 pins both as tests (a csv bool column written by `save` passes provenance), so deleting the read-back turns them red. The read-back, the `get_df` return hash and the `stream_dict` rows hash remain the three output hashes; each takes the agent tag from the same helper. If J4.T3 cannot hold `evals/_check.py` at net ≤ 0 with this, it stops and returns to the main thread (SPEC §5 first risk).

**D3 — the record's shape.** `provenance(...)` returns `(message | None, record)`; `record` is a list of `{"entry", "spec", "agent"}`. `calls` is `{r["entry"] for r in record if r["agent"]}` (deduplicated; sqlite and parts are `save`); specs for layer 3 are the specs of agent records. The agent filter is written once, in `_check.py`. No out-param remains.

**D4 — who is the agent (main-thread ruling).** A frame is the agent's when its file lies under the root of the trial's scratch copy: the script and any module the agent wrote there. Library frames stay non-agent, since `rand_engine` lives outside that root. The tag only filters records; a decorative call still fails because the graded artifact must match the output of a record (AC22.1, AC22.3).

**D5 — `raise_validation` (pre-mortem Row 3).** Neither external caller matches an existing `*_and_raise` wrapper: `data_generator.py:116` raises the error list of a per-column generation probe (`__refuse_ungeneratable`), and `spark_generator.py:68` raises the merge of `validate_spark_spec` on ordinary columns and `AdvancedValidator.validate` on key columns; the wrappers take a spec and validate it. So `_raise` is renamed to the public `raise_validation(errors, engine)` in `common_validator.py`; both wrappers and both callers use it; message and `SpecValidationError` class are unchanged; `rand_engine.__all__` stays three names. Net lines 0.

**D6 — the starter keeps the Arrow conf (Row 4).** Only the netty sentence, its prose copy and the fixture options go. The leak is closed by the test that runs the starter (`test_9_cli.py`), which restores the conf; J2.T1 picks restore or an isolated session.

**D7 — test and law edits.** A `tests/*` path is never in an implementation task (`tests:` glob). Test-only hygiene is `test(<id>)`; a source or doc path is its own task. The two deletions are `test(J3.T3)` and `test(J5.T4)` and quote the operator order "Confirmo, apagar os 2 (Recommended)"; each is preceded in the same job by the task that tightens the surviving assert, so no precision is lost. The one rewritten call shape of `provenance` in `test_eval_check.py` (`:146-149`, the `calls=`/`specs=` helpers) is a main-thread ruling named in `test(J4.T1)`: this PLAN's approval, Row 1 "callers move in the same job". If `WT merge` reads `evals/tasks/*/tests/check.py` as the `tests:` glob, the main thread splits those paths into a `test(...)` tree at dispatch (rc-3 PLAN precedent).

### 1.3 Pre-mortem hits

| hit | answer | task |
|---|---|---|
| Row 1 `_resolve_size` cannot be the hook | D1: `_file_seam` plus `SparkGenerator.get_df`, proven above; no library edit | J4.T3 |
| Row 1 save read-back | D2: kept, with two tests that go red without it | J4.T2 |
| Row 1 `calls` | a deduplicated set of entry points, sqlite is `save` (D1, D3) | J4.T1, J4.T3 |
| Row 1 callers move in the same job | the 8 `check.py` call sites, `evals/README.md:18`, the `test_eval_check.py` helpers move in J4.T1 and J4.T3; the `agent-eval.md:44` atom line moves in the reconcile (a memory atom is the closure's, `pe`); between the merge and the reconcile it reads the old shape for one rc | J4.T1, J4.T3, Reconciliation |
| Row 1 `result_text` | branch deleted, prefix always written; 0 callers repeat it | J4.T4 |
| Row 2 get-started-cli forms | one decider: quote-aware split, basename `rand-engine` behind `uvx`, `uv run`, `poetry run`, `pipx run`, `timeout N`; `python -m rand_engine`; `python -c` calling the CLI `main`; slug = first positional after `get-started`; the matcher gets a unit test over every form; the `echo` LOW is RULED, no change (SPEC §3) | J6.T2, J6.T5 |
| Row 3 `_raise` | D5 | J7.T1, J7.T2 |
| Row 4 starter | D6 | J2.T1-T3 |
| Row 5 `gen_uuid4` | pins `tests/test_0_np_core.py:412` and `tests/test_2_data_generator.py:596` run green on the old body first; the 1M/10M row is the CI speed benchmark (`benchmarks/speed.py:38` holds `uuid4`), quoted at closure | J8.T1, J8.T3 |
| Row 6 `AGENTS.md:52-53` | deleted, not a gate change; `:51` waits for the ruling | J1.T2, J1.T3 |
| Row 7 spark task | `["pyspark>=4"]`, no `setuptools`; the selfcheck runs on pyspark 4 in the eval workflow at the `wt-rc` push, no extra local gate | J6.T8 |

## DAG

Waves are schedule waves, one per overlap of `W:`; jobs of one wave write disjoint files. The SPEC's ranking (FR19-FR21; FR22; FR23-FR26; FR27-FR29) is the order of merit; Jobs 7 and 8 sit beside Jobs 5 and 6 because their files are disjoint.

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `.dadaia/reports/rand-engine/`, `AGENTS.md` |
| Job 2 | — | 1 | `tests/test_9_cli.py`, `tests/fixtures/f2_spark_generator_specs_right.py`, `rand_engine/cases/databricks.py.txt`, `docs/tutorials/databricks.md` |
| Job 3 | — | 1 | `tests/test_docs.py`, `tests/test_2_data_generator.py`, `tests/test_2_data_generator_fails.py`, `tests/test_5_files_write_batch.py`, `rand_engine/main/_rand_generator.py`, `.github/workflows/benchmarks.yml` |
| Job 4 | — | 1 | `evals/_check.py`, `evals/README.md`, `tests/integrations/test_eval_check.py`, `evals/tasks/writers-and-streaming/tests/check.py`, `evals/tasks/generation-methods/tests/check.py`, `evals/tasks/templates-and-examples/tests/check.py`, `evals/tasks/pk-fk-constraints/tests/check.py`, `evals/tasks/public-api/tests/check.py`, `evals/tasks/data-generator/tests/check.py`, `evals/tasks/rand-spec-grammar/tests/check.py`, `evals/tasks/spark-generator/tests/check.py` |
| Job 5 | Job 4 | 2 | `evals/run.py`, `evals/gate.py`, `.github/workflows/eval.yml`, `tests/integrations/test_eval_gate.py`, `tests/integrations/test_public_api.py` |
| Job 6 | Job 4 | 2 | `evals/tasks/data-generator/tests/check.py`, `evals/tasks/generation-methods/tests/check.py`, `evals/tasks/public-api/tests/check.py`, `evals/tasks/templates-and-examples/tests/check.py`, `evals/tasks/get-started-cli/tests/check.py`, `evals/tasks/pk-fk-constraints/tests/check.py`, `evals/tasks/documentation/tests/check.py`, `evals/tasks/canary/tests/check.py`, `evals/tasks/spark-generator/tests/check.py`, `evals/tasks/spark-generator/task.toml`, `evals/tasks/generation-methods/tests/decoy/solve.py`, `evals/tasks/data-generator/tests/decoy/solve.py`, `tests/integrations/test_eval_tasks.py` |
| Job 7 | — | 2 | `rand_engine/validators/common_validator.py`, `rand_engine/validators/advanced_validator.py`, `rand_engine/validators/method_specs.py`, `rand_engine/main/data_generator.py`, `rand_engine/main/spark_generator.py`, `tests/test_1_common_validator.py`, `tests/test_1_advanced_validator.py` |
| Job 8 | — | 2 | `rand_engine/core/_np_core.py`, `tests/test_0_np_core.py` |
| Job 9 | Job 7 | 3 | `rand_engine/main/data_generator.py`, `rand_engine/main/spark_generator.py`, `rand_engine/validators/exceptions.py`, `CHANGELOG.md`, `tests/test_3_spark_generator.py` |
| Reconciliation | Job 1, Job 5, Job 6, Job 8, Job 9 | 4 | `specs/memory/product/generation/spark-generator.md`, `specs/memory/product/quality/agent-eval.md`, `specs/memory/QUALITY.md`, `specs/memory/product/catalog.json` |

Edge reasons: Jobs 5 and 6 consume Job 4's record and `result_text` (SPEC §2). Job 9 edits the two generator files after Job 7. Job 1's `J1.T3` waits on the operator's ruling, not on a job; the Reconciliation does not wait for it (if no ruling, the line stays and the cancelled row keeps its reason). Wave 1 is four jobs, wave 2 four; Job 6 is the widest sequence (its tasks share `check.py` files).

### Schedule and sizing

- 42 tasks: Job 1 three (1 sr, 2 jr), Job 2 four (1, 3), Job 3 five (0, 5), Job 4 four (3, 1), Job 5 seven (3, 4), Job 6 nine (5, 4), Job 7 three (2, 1), Job 8 three (1, 2), Job 9 four (1, 3). 17 sr, 25 jr. A behaviour is a RED task then its implementation; test-only hygiene and behaviour-preserving edits (J3, J8.T3, J9) are single `jr` tasks whose owner test already exists or is the file itself.
- Tasks of one job run in the order of their `W:` overlap; each job file names it.
- J4.T3 is the only REBUILD of size and risk (net of `evals/_check.py` ≤ 0); it merges before Jobs 5 and 6 open.

## 2. Gates

The job gate is the repo's `verify:` line, unchanged, as `release.py` and the worktree merge read it (`AGENTS.md:51`). No preflight, matrix or local gate is added. Job 1 measures the line to let the operator rule; nothing in this PLAN makes a requirement apply to every task. Eval changes run on the existing push trigger (`eval.yml`, rc-3 D11) once, at the `wt-rc` push, including the pyspark 4 selfcheck.

## Measured cost

- Gate law: no task adds a step to `verify:` or the merge. 42 task merges, 9 job merges and one `wt-rc` merge run the existing line. Per-run time is not re-measured here; the figure J1.T1 produces (3 cold, 3 warm, both lines) is the only new measurement, and it is the operator's input to FR19.
- Added tests are fixture-only: **estimate** a few seconds per run, source: the same file sizes as rc-3's `test_eval_check.py` (10-row scripts through the pytest interpreter).
- `AC26.2` quotes the CI speed benchmark's `uuid4` row at 1M and 10M, base against head, from the run of the `wt-rc` push.

## Acceptance map

| AC | owner task | implementation task |
|---|---|---|
| AC19.1 | no test; J1.T1's report | J1.T1 |
| AC19.2, AC19.3 | no test; the operator's ruling | J1.T3 |
| AC19.4 | no test; read on the diff | J1.T2 |
| AC20.1, AC20.3 | J2.T1 | J2.T1 (restore), J2.T2 |
| AC20.2 | the Spark suite on CI's Java 17 | J2.T3 |
| AC21.1 | the renamed tests | J3.T4 |
| AC21.2 | `tests/test_docs.py` | J3.T1 |
| AC21.3 | no test | J3.T5, J4.T1, J7.T3, J8.T2 |
| AC21.4 | J2.T4, J5.T2 | J2.T4, J5.T2 |
| AC21.5 | J9.T2 | J9.T2 |
| AC21.6 | J3.T2, J3.T3 | J3.T3 |
| AC22.1, AC22.2, AC22.3 | J4.T1 | J4.T3 |
| AC22.4, AC22.5 | J4.T2 | J4.T3, J4.T4 |
| AC22.6 | no test; read on the diff | J4.T3 |
| AC23.1, AC23.2 | J5.T1 | J5.T5 |
| AC23.3 | J5.T2 | J5.T6 |
| AC23.4 | J5.T3 | J5.T7 |
| AC23.5 | J5.T4 | J5.T4 |
| AC24.1, AC24.6 | J6.T1 | J6.T4, J6.T6, J6.T8 |
| AC24.2 | J6.T2 | J6.T5 |
| AC24.3, AC24.4 | J6.T3 | J6.T6, J6.T7 |
| AC24.5 | the no-agent selfcheck job | J6.T9 |
| AC25.1 | no test; a sweep | J7.T3 |
| AC25.2, AC25.3, AC25.4 | J7.T1 | J7.T2, J7.T3 |
| AC26.1 | the golden at `test_0_np_core.py:412` | J8.T3 |
| AC26.2 | the CI benchmark run | closure summary |
| AC26.3 | J8.T1 | J8.T1 (green on arrival: size 0 already returns an empty array) |
| AC27.1, AC27.2, AC28.2 | no test; `ruff D` and the doctests in `verify:` | J9.T3 |
| AC27.3, AC29.2 | `tests/test_docs.py` dated-header test | J9.T4 |
| AC28.1 | J9.T1 (green on arrival: the pin) | none, no source change |
| AC28.3 | J9.T2 | J9.T2 |
| AC29.1, AC29.3 | no test | Reconciliation |

### Reconciliation (the rc's last commits, `RC-FLOW.md` step 4)

Order, `dd-product-engineer`: (1) `release.py phase CLOSURE`; (2) the memory pass from the final diff: `spark-generator.md:17` (callable size), the `QUALITY.md` Spark-session line and verify line (per the ruling), the `agent-eval` atom (the one record, `agent-eval.md:44`, the trial record fields, `pyspark>=4`), `catalog generate`; (3) the closure summary quoting FR19's numbers and ruling, the AC26.2 run and the net lines of `evals/_check.py`.
