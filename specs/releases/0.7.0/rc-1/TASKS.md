# TASKS — Release: 0.7.0, candidate 1 (relations core + visibility)

**Status:** In review
**Release ID:** 0.7.0
**Owner:** dd-software-engineer

Every commit touching `.py` carries `test-audit:` and `mutation:` lines (PLAN §4): before staging, new or changed tests pass the test-audit gate (`~/.claude/plugins/cache/claude-settings/test-audit/1.0.0/skills/test-audit/SKILL.md`) and `mutation-diff` (`~/.claude/skills/mutation-diff/SKILL.md`) runs on the worktree; survivors strengthened or named equivalent. Local runs ≤ 10^4 rows, never `-m stress` or the benchmark script locally. Bug-merge waits: PLAN §5. Default tests ≤ 10^4 rows; `Stress:` variants carry `@pytest.mark.stress` (AC10.5, PLAN §4).

- [x] T-070-1 — Tracer: `pk` sequence + `fk` uniform through `get_df` (FR1, FR2 slice). `W:` `rand_engine/core/_keys.py`, `rand_engine/main/_rand_generator.py`, `rand_engine/main/data_generator.py`, `rand_engine/validators/advanced_validator.py`, `tests/test_8_consistency.py`, `tests/fixtures/f3_data_generator_constraints.py`
  blocked by: none. delivers: the operator generates a parent and a child frame whose integer FK values all sit in the parent PK set.
  `Keys.gen_pk` (sequence), `Keys.gen_fk` (uniform, `cell_hash` port); `map_methods(offset, key_seed)` binds them by `partial`; `DataGenerator._key_seed` from `SeedSequence`; the loop builds `map_methods` per column; `pk`/`fk` in `METHOD_SPECS`. `test_8` rebuilt (old cases and the f3 fixture deleted: their target leaves in T-070-2).
  RED: `tests/test_8_consistency.py` — AC1.1, AC2.1 (sequence parent), AC3.3 at light sizes; the 10^6 variants under `stress`; asserts on the output read back (AC10.3). Merges after T-070-12 (marker registered).
- [x] T-070-12 — Light default suite + CI stress/benchmark job (AC10.5). `W:` `pyproject.toml`, `.github/workflows/test_on_push.yml`, `tests/fixtures/f3_integrations.py`, `tests/test_0_spark_core.py`, `tests/test_0_np_core.py`, `tests/fixtures/f0_benchmarks.py`
  blocked by: none. delivers: the operator runs the default suite on this machine in seconds, with stress and benchmarks only in CI.
  Register `stress` in `markers`, `addopts = "-m 'not stress'"`; one `stress` job in `test_on_push.yml` (ubuntu-latest, Python 3.12, `pytest -m stress`; no `${{ }}` of untrusted input inside `run:`). Shrink `f3_integrations` sizes 10^5 → ≤ 10^4; `test_large_dataset_performance` (range 100000) shrunk to 10^4, not moved under `stress` (shipped departure, review LOW-3: its row-count assert holds at any size). `f0_benchmarks.py` imports the long-gone `rand_engine.bulk` and never runs: deleted, rebuilt as one `stress` benchmark over `NPCore` at 10^7 in `test_0_np_core.py`.
  RED: evidence, not a test (definition review L3); `tests/test_0_np_core.py` holds the `stress` benchmark — the default run deselects `stress` (`pytest --collect-only -q` lists no `stress` test); no default test builds > 10^4 rows (`grep -rnE` evidence in the commit body).
- [x] T-070-2 — DELETE the checkpoint (FR5, AC10.4). `W:` `rand_engine/main/_constraints_handler.py`, `rand_engine/integrations/__init__.py`, `rand_engine/integrations/_base_handler.py`, `rand_engine/integrations/_sqlite_handler.py`, `rand_engine/integrations/_duckdb_handler.py`, `rand_engine/main/data_generator.py`, `rand_engine/main/_rand_generator.py`, `rand_engine/validators/advanced_validator.py`, `pyproject.toml`, `poetry.lock`, `requirements.txt`, `AGENTS.md`, `tests/integrations/test_sqlite.py`, `tests/integrations/test_duckdb.py`, `tests/integrations/test_constraints_cleanup.py`, `tests/fixtures/f4_database_handlers.py`, `tests/integrations/test_public_api.py`, `rand_engine/validators/__init__.py`, `tests/test_1_advanced_validator.py`, `tests/test_2_data_generator.py`
  blocked by: T-070-1. delivers: the operator installs rand-engine without `duckdb`, and an old `constraints` spec fails with a message naming `pk` and `fk`.
  Deletes `db_checkpoint`, `option`, the `del spec["constraints"]`, the handler, the adapters and their tests; `validate_constraints` becomes the AC5.1 refusal; repo `AGENTS.md` loses the checkpoint stop condition and key paths; `test_public_api.py` and the `validators` docstring drop the deleted names; no test imports a deleted module (AC10.3).
  RED: `tests/test_1_advanced_validator.py` — AC5.1; `tests/test_2_data_generator.py` — AC5.3; AC5.4 grep in the commit body.
- [ ] T-070-3 — One rng per generator, under the speed gate (FR4, FR12). `W:` `rand_engine/main/data_generator.py`, `rand_engine/main/_rand_generator.py`, `rand_engine/core/_np_core.py`, `rand_engine/core/_py_core.py`, `rand_engine/utils/update.py`, `rand_engine/templates/web_server_logs.py`, `tests/test_0_np_core.py`, `tests/test_0_py_core.py`, `tests/test_2_data_generator.py`, `docs/benchmarks.json`, `docs/BENCHMARKS.md`
  blocked by: T-070-1, T-070-13. delivers: the operator's NumPy state survives a generator, two same-seed generators agree, and no method got slower than 1.3× baseline.
  `rng` keyword on every `NPCore`/`PyCore` method, bodies kept: `np.random.randint` → `rng.integers` (exclusive high, `dtype` kept), `choice`/`normal` → `rng.choice`/`rng.normal`; `gen_uuid4` builds RFC 4122 v4 from `rng.bytes` (version/variant bits set vectorised, PLAN §3); `map_methods` binds `rng`; `np.random.seed` and `Changer` deleted.
  Gate (AC12.1): its CI `benchmarks` rows vs the baseline, before/after shown to the operator; a method > 1.3× → `SFC64` bit generator and FR4's ACs re-run; still over → revert. Adds the lazy-spec guard (PLAN §3).
  RED: `tests/test_2_data_generator.py` — AC4.1, AC4.2 (`uuid4` included), AC4.3, a callable spec evaluated once per `get_df` and per `stream_dict` microbatch; `tests/test_0_np_core.py` — AC4.5; AC4.4 grep and the FR11 rows in the commit body.
- [ ] T-070-4 — PK complete: `permuted`, `format`, domain guard (FR1). `W:` `rand_engine/core/_keys.py`, `rand_engine/validators/advanced_validator.py`, `tests/test_8_consistency.py`, `tests/test_1_advanced_validator.py`
  blocked by: T-070-1. delivers: the operator generates random-looking unique ids, as integers or formatted strings.
  Feistel cycle-walk port (`proto/feistel.py`), never the affine form (int64 wrap, PLAN §3). AC1.3's row 10^15−1 is reached through the internal seam `Keys.gen_pk(..., offset=10**15-1)`, not a 10^15-row frame. A `sequence` leaving int64 raises `RandEngineError` in `Keys.gen_pk` at generation time.
  RED: `tests/test_8_consistency.py` — AC1.2–AC1.6, read back (AC10.3); `tests/test_1_advanced_validator.py` — AC1.7.
- [ ] T-070-5 — FK complete: string and permuted parents, `skew`, cross-process (FR2). `W:` `rand_engine/core/_keys.py`, `rand_engine/validators/advanced_validator.py`, `tests/test_8_consistency.py`, `tests/test_1_advanced_validator.py`
  blocked by: T-070-4. delivers: the operator skews children toward scattered hot parents and joins tables generated by separate processes.
  The parent-index hash mixes the spec column name, the key seed and the fk kwargs (AC2.8).
  RED: `tests/test_8_consistency.py` — AC2.1 (permuted), AC2.2–AC2.5, AC2.7, AC2.8, read back (AC10.3); `tests/test_1_advanced_validator.py` — AC2.6.
- [ ] T-070-6 — Row index across batches, streams and files (FR3, AC5.2). `W:` `rand_engine/main/data_generator.py`, `rand_engine/file_handlers/_writer_batch.py`, `rand_engine/file_handlers/_writer_stream.py`, `tests/test_8_consistency.py`
  blocked by: T-070-1. delivers: the operator streams a child whose keys match a single batch of the same rows.
  Row counter per `stream_dict` / `writeStream` closure; `get_df` and `write` at offset 0; each file of a `numFiles` save gets offset `c_f`. Waits for bug `writer-numfiles-rows-per-file` (PLAN §5).
  RED: `tests/test_8_consistency.py` — AC3.1, AC3.2, AC3.4, AC3.5, AC5.2, read back (AC10.3).
- [x] T-070-7 — Spark refuses keys (FR6). `W:` `rand_engine/validators/common_validator.py`, `tests/test_1_common_validator.py`
  blocked by: none. delivers: the operator gets "NumPy engine only in 0.7.0" naming `DataGenerator` for a Spark spec with keys.
  RED: `tests/test_1_common_validator.py` — AC6.1, AC6.2.
- [ ] T-070-8 — Docs rebuilt and executed (FR8 docs). `W:` `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`, `docs/3_WRITING_FILES.md`, `docs/4_CONSTRAINTS.md`, `docs/5_RECIPES.md`, `tests/test_docs.py`
  blocked by: T-070-2, T-070-3, T-070-5, T-070-6, T-070-7, T-070-16. delivers: the operator follows any guide and every example runs.
  `docs/3_WRITING_FILES.md` lists only the writer options T-070-16 maps.
  RED: `tests/test_docs.py` — AC8.1, AC8.2, AC8.3 over `docs/*.md`.
- [ ] T-070-9 — README and `llms.txt` (FR7, AC8.4). `W:` `README.md`, `llms.txt`, `tests/test_docs.py`
  blocked by: T-070-8, T-070-10. delivers: a newcomer, human or agent, reaches a working related-tables example from PyPI in one read.
  RED: `tests/test_docs.py` — AC7.2–AC7.5, AC8.4 (README blocks executed; README and `llms.txt` links resolve).
- [ ] T-070-10 — Licence, metadata, changelog, test law, backup (FR9 less AC9.4, AC10.1, AC10.2). `W:` `LICENSE`, `pyproject.toml`, `CHANGELOG.md`, `tests/AGENTS.md`, `specs_bkp/**`
  blocked by: T-070-2, T-070-3, T-070-7. delivers: the operator sees MIT, the identity summary and the 0.7.0 break list on PyPI.
  RED: none statable as a pytest — evidence `poetry build && pipx run twine check dist/*` and `git ls-files specs_bkp` empty, in the commit body.
- [ ] T-070-11 — Version 0.7.0 (AC9.4). `W:` `pyproject.toml`
  blocked by: T-070-1, T-070-2, T-070-3, T-070-4, T-070-5, T-070-6, T-070-7, T-070-8, T-070-9, T-070-10, T-070-13, T-070-14, T-070-15, T-070-16, T-070-17. delivers: the pipeline tags and publishes 0.7.0 at promote.
  RED: none — `grep '^version = "0.7.0"' pyproject.toml` in the commit body.
- [ ] T-070-13 — Speed benchmark CI job and baseline (FR11). `W:` `benchmarks/speed.py`, `tests/test_benchmarks.py`, `.github/workflows/benchmarks.yml`, `.github/workflows/test_on_push.yml`, `tests/test_0_np_core.py`, `docs/benchmarks.json`, `docs/BENCHMARKS.md`
  blocked by: none. delivers: the operator reads every method's rows/µs at 10^6 and 10^7 in `docs/BENCHMARKS.md`, and a PR slower than 1.3× baseline goes red.
  The script and `benchmarks.yml` per PLAN §3; the `stress` job leaves `test_on_push.yml` whole into `benchmarks.yml` (AC10.5 one job); the 10^7 `stress` benchmark in `tests/test_0_np_core.py` is deleted (the matrix runs only here). Baseline: the job's first run on today's code (draft PR work → `development`; `workflow_dispatch` needs the file on `master` — PLAN §3), artifact downloaded and committed.
  RED: `tests/test_benchmarks.py` — AC11.4 (1.29 passes, 1.31 fails, unbaselined reported); AC11.1–AC11.3 evidence: the run URL and the committed JSON in the commit body.
- [ ] T-070-14 — Golden seeded output (FR13). `W:` `tests/test_2_data_generator.py`
  blocked by: T-070-3. delivers: the operator changes generation code and learns at once whether any seeded output moved.
  One seeded `get_df` at 10^3 rows per NumPy-engine method (`map_methods` keys, `pk`/`fk` included); literal values or a literal sha256; expected literals from a UTC run after B8 (`timestamps-depend-on-local-timezone`) merged (PLAN §5).
  RED: `tests/test_2_data_generator.py` — AC13.1; AC13.2 is the standing rule, stated in `tests/AGENTS.md` by T-070-10.
- [ ] T-070-15 — `dates` vectorised in UTC (AC14.1, AC14.4). `W:` `rand_engine/core/_np_core.py`, `tests/test_0_np_core.py`, `docs/benchmarks.json`, `docs/BENCHMARKS.md`
  blocked by: T-070-14, bug `timestamps-depend-on-local-timezone`. delivers: the operator generates `dates` columns at NumPy speed, identical on every machine.
  `gen_dates` per PLAN §3; FR11 `dates` rows before/after in the commit body and to the operator; lands only ≤ 1.3× baseline (FR12) — expected far below.
  RED: `tests/test_0_np_core.py` — AC14.1 equality with per-row UTC `strftime` over each documented `date_format`; T-070-14's goldens unchanged.
- [ ] T-070-16 — csv and parquet through pyarrow (AC14.2, AC14.4). `W:` `rand_engine/file_handlers/file_handler.py`, `tests/test_5_files_write_batch.py`, `tests/test_5_files_write_stream.py`, `docs/benchmarks.json`, `docs/BENCHMARKS.md`
  blocked by: T-070-14. delivers: the operator writes csv and parquet files faster, each reading back equal to the pandas-written file.
  Option map and the unmappable set (csv `zip`/`xz`, parquet `engine`) per PLAN §3 — pending the main-thread ruling; JSON stays on pandas. Before/after evidence pending the AC14.4 ruling (FR11 times `get_df`, not writers).
  RED: `tests/test_5_files_write_batch.py` — AC14.2 per mapped option and compression, read back vs the pandas-written file; an unmapped option raises; `tests/test_5_files_write_stream.py` — the stream csv/parquet path.
- [ ] T-070-17 — `stream_dict` records through Arrow (AC14.3, AC14.4). `W:` `rand_engine/main/data_generator.py`, `tests/test_6_stream_objects.py`, `docs/benchmarks.json`, `docs/BENCHMARKS.md`
  blocked by: T-070-14. delivers: the operator streams records faster, each equal to today's.
  `to_dict('records')` → `Table.from_pandas(df, preserve_index=False).to_pylist()`; `convert_dt_to_str`, `timestamp_created` and the per-microbatch lazy spec kept (T-070-3's guard stays green). Before/after evidence pending the AC14.4 ruling.
  RED: `tests/test_6_stream_objects.py` — AC14.3 record `==` and type equality vs `to_dict('records')` over every method's column.
