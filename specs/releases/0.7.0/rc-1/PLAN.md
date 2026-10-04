# PLAN — Release: 0.7.0, candidate 1 (relations core + visibility)

**Status:** In review
**Release ID:** 0.7.0
**Owner:** dd-software-engineer
**SPEC:** `specs/releases/0.7.0/rc-1/SPEC.md`; ADR 0002 accepted.
**Approval:** operator, 2026-10-03, verbatim: "Approve trio + 4 fills (Recommended)" — PLAN and TASKS approved with the four fills: the fk seed mixes the fk kwargs; every `docs/*.md` executed; pk defaults `sequence`/`start` 0/`step` 1/`key` 0; T-070-10/11 checked by build + `twine check` evidence.
**Re-approval:** operator, 2026-10-03, verbatim: "Re-approve all three (Recommended)" — SPEC, PLAN and TASKS as amended per the definition review (5fc0fd8, bb0cbb8).
**Re-approval (light tests):** operator, 2026-10-04, verbatim: "Re-approve (Recommended)" — SPEC 84fae68, ADR repair 85f0a46, PLAN/TASKS 66734c1.
**Re-approval (AC1.7 step 0):** operator, 2026-10-04, verbatim: "Re-approve (Recommended)" — SPEC 815ac0e, PLAN/TASKS 32d8fc7.
**Amended (speed program):** SPEC 24007e5 FR11–FR14 → As-is rows, authorities, §2–§5 and T-070-13..17 (2026-10-04), pending re-approval.
**Amended:** SPEC AC1.7 (815ac0e, T-070-1 review MEDIUM); §5 step 1 and T-070-12 wording (definition review L3–L5, review LOW-3).

## 1. As-is review

Bug ledger: B1 (`wt/0.7.0b-bug`) holds `writer-options-consumed-by-use` and `writer-size-not-from-generator`, pending re-review; operator-confirmed, not yet registered: D9–D12, D14, D15, D17, D18, D20, `writer-state-shared-across-chains`, `writer-numfiles-rows-per-file`, `memory-atom-ignored-by-output-glob`. Fix history = `git log --follow` commit counts (total/`fix`). Evidence: audit 0.6.4, `probes/`, `proto/` under `.dadaia/reports/rand-engine/20261003-revival/`.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `main/_constraints_handler.py` `ConstraintsHandler` | PK rows into a checkpoint DB with `creation_time`; FK sampled from rows inside a wall-clock watermark | D1, D2, D16, D19 (3/1) | DELETE | contract contradicts the SPEC (stateless keys); deletion test: complexity vanishes, replaced by arithmetic |
| `integrations/_sqlite_handler.py`, `_duckdb_handler.py`, `_base_handler.py`, `__init__.py` | class-level connection pool; int64 stored as BLOB; ABC with two adapters used only by the checkpoint | D1, D3, D18, D19 (7/1) | DELETE | no caller after the handler goes; the shared `:memory:` pool is hidden global state; `duckdb` leaves |
| `main/data_generator.py` `DataGenerator` | `np.random.seed(seed)` global; `del spec["constraints"]`; `db_checkpoint`; `option("reset_checkpoint")` | D3, D4, D13 (31/6, the most-fixed unit) | REBUILD | seams only; ≥ 2 bugs; keep the fluent surface (`size`, `transformers`, `get_df`, `stream_dict`, `write`, `writeStream`); delete `db_checkpoint`, `option`, the `del`; holds one `SeedSequence`, one `rng`, a row counter per stream |
| `main/_rand_generator.py` `RandGenerator` | one dispatch dict; unused `DuckDBHandler` import; dead `validate` param | D11 (16/1) | UPDATE | `map_methods(rng, offset, key_seed)` binds the per-call inputs with `functools.partial`; the column loop is unchanged; dead import/param leave |
| `core/_np_core.py` `NPCore` | operator-written vectorised core over global `np.random` | D12, D13, D14, D15, D20 (9/1) | UPDATE | `rng` keyword per function, `np.random.x` → `rng.x`; bodies otherwise kept; D12/D14/D15/D20 are Arm B |
| `core/_py_core.py` `PyCore` | Python-loop correlated methods; `gen_distincts_untyped` serves `gen_distincts_map` | D13, D18 (9/0) | UPDATE | `rng` keyword; `gen_distincts_untyped` KEEPs (caller `gen_distincts_map`); the DuckDB import is D18 (Arm B) |
| `core/_spark_core.py`, `main/spark_generator.py` | native Spark exprs; no seed | D13, D15 (13/0) | KEEP | D3: Spark rejects keys in the validator; D15 is Arm B |
| — `core/_keys.py` `Keys` | — | — | ADD | no unit can carry a pure `pk(i)` / `fk(j)`: sequence, Feistel cycle-walk permutation, uniform and Zipf parent index; port of `proto/core.py` (`xxh64_long`, `cell_hash`, `zipf_index`) + `proto/feistel.py`, NumPy only, ~70 LOC |
| `validators/advanced_validator.py` | `validate_constraints` (PK/FK/watermark); `METHOD_SPECS` | D9, D11 (3/1) | UPDATE | `pk`/`fk` entries + their rules (AC1.7, AC2.6); `validate_constraints` becomes the AC5.1 refusal naming `pk` and `fk` |
| `validators/common_validator.py` `_validate_spark_column` | Spark spec rules | D9, D10, D20 (3/1) | UPDATE | one refusal for `pk`/`fk` (AC6.1) |
| `file_handlers/writer.py` `FileWriter.size` | a second row count beside the generator's | D5 | DELETE | delivered by B1 (8a28805, operator ruling "Delete `.write.size()`"); no task |
| `file_handlers/_writer_batch.py`, `_writer_stream.py` | one `save`/microbatch over `numFiles` files | `writer-numfiles-rows-per-file` | UPDATE | after that bug splits `size` across files, each file call carries its row offset `c_f` (AC3.5) |
| `utils/update.py` `Changer` | `np.random.seed(None)` reseed; imported by `templates/web_server_logs.py`, never called | D13 | DELETE | global-state writer with no call site |
| `main/_cdc_generator.py` | unimportable | D17 | DELETE | Arm B D17, not a task here |
| `README.md` | `unique_ids`/`references`/`get_dfs`/`splitable` examples; six dead links; stale timing | D6 | REBUILD | every `python` block executed by the suite |
| `docs/4_CONSTRAINTS.md` | checkpoint guide | D6 | REBUILD | keys guide; blocks executed |
| `docs/1..3_*.md` | drifted API | D6 | UPDATE | blocks executed |
| `docs/5_RECIPES.md`, `llms.txt`, `LICENSE` | — | — | ADD | AC8.2, AC8.4, AC9.1: nothing carries them |
| `pyproject.toml`, `poetry.lock`, `requirements.txt`, `CHANGELOG.md` | v2 summary, no licence, one URL, `duckdb`; changelog stops at 0.6.0 | D18 | UPDATE | AC5.4, AC9.2–AC9.4 |
| `AGENTS.md` (repo), `tests/AGENTS.md` | checkpoint stop condition and key paths; uncalibrated test law | — | UPDATE | AC10.1, AC10.4 |
| `specs_bkp/` | tracked backup | — | DELETE | AC10.2 |
| `tests/integrations/test_sqlite.py`, `test_duckdb.py`, `test_constraints_cleanup.py`, `tests/fixtures/f4_database_handlers.py` | test the deleted adapters | — | DELETE | feature removed |
| `tests/integrations/test_public_api.py`, `validators/__init__.py` | assert/describe the checkpoint surface ("constraints validation") | — | UPDATE | drop the deleted names (AC5.3, AC10.3) |
| `tests/test_8_consistency.py` + `tests/fixtures/f3_data_generator_constraints.py` | VARCHAR-only FK, commented subset asserts | — | REBUILD | the relations contract file (AC10.3); fixture deleted |
| `core/_np_core.py` `gen_uuid4` | per-row `str(uuid.uuid4())` from the OS, ~0.14 rows/µs at 10^5 (research 6d7755b5) | (10/2 on the file) | UPDATE | T-070-3's rng-bytes body (§2); FR12 gates it ≤ 1.3× baseline |
| `core/_np_core.py` `gen_dates`, `gen_unix_timestamps` | `dt.strptime(...).timestamp()` and per-row `dt.fromtimestamp(ts).strftime` in local time, ~0.22 rows/µs | `timestamps-depend-on-local-timezone` (open, HIGH), `floats-bounds-truncated`/`int-type-overflow-silent` on the file (10/2) | UPDATE | the bug fixes the timezone per row (Arm B, B8); T-070-15 then replaces the loop with `datetime64[s]` + vectorised formatting, strings unchanged (AC14.1) |
| `file_handlers/file_handler.py` `FileHandler.to_csv`, `to_parquet` | `write_options` forwarded as pandas kwargs (4/1) | `writer-options-consumed-by-use` (resolved, B1) | UPDATE | the two lambdas become `pyarrow.csv.write_csv` / `pyarrow.parquet.write_table` over `Table.from_pandas(df, preserve_index=False)`; option map §3; `to_json` KEEP (AC14.2) |
| `file_handlers/_writer_batch.py`, `_writer_stream.py`, `writer.py` | call `FileHandler` per file (13/5, 9/5, 6/3) | B1, B5, B6 (resolved) | KEEP | the format seam is `FileHandler`; no writer changes for AC14.2 |
| `main/data_generator.py` `DataGenerator.stream_dict` | `StreamHandler.convert_dt_to_str` then `to_dict('records')` per microbatch (36/9, the most-fixed unit) | `writer-size-not-from-generator` (resolved, B1) | UPDATE | `pa.Table.from_pandas(df, preserve_index=False).to_pylist()` replaces `to_dict`; the loop, the lazy spec and `timestamp_created` kept (AC14.3) |
| `utils/stream_handler.py` `StreamHandler.convert_dt_to_str` | datetime64 columns → `str` (2/0) | — | KEEP | the Arrow path needs the same strings for `==` with today's records |
| `.github/workflows/test_on_push.yml` `stress` job | `pytest -m stress` on push only (8/4) | — | DELETE | workflow triggers are per file: this file runs on `push`, FR11 needs `pull_request` + `workflow_dispatch`; the job moves whole into `benchmarks.yml` |
| — `.github/workflows/benchmarks.yml` | — | — | ADD | no workflow carries AC11.1's triggers without re-running its other jobs (`pr_to_development.yml` already runs the matrix on PRs); one job: `pytest -m stress` then the FR11 script (AC10.5 "one dedicated job") |
| — `benchmarks/speed.py` | — | `method-registry-has-five-owners` (open, HIGH): the script reads the one dispatch, `map_methods` | ADD | no unit measures methods: the 10^7 `stress` benchmark in `tests/test_0_np_core.py` (T-070-12) times `NPCore` only, inside pytest (AC10.5 forbids the matrix there); it is deleted for this script; stdlib `time`/`statistics`/`tracemalloc`/`json` + NumPy |
| — `docs/benchmarks.json`, `docs/BENCHMARKS.md` | — | — | ADD | the baseline the gate reads and its rendering (AC11.2, G1); derived: written only from the CI artifact |
| `tests/test_0_*_core.py`, `test_1_*_validator.py`, `test_2_data_generator.py`, `test_5_files_write_*.py` | run checks | — | UPDATE | each owns its RED; no new file except `tests/test_docs.py` (no file owns docs) |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| what is row i's primary key | `Keys.gen_pk` | `RandGenerator.map_methods` | `ConstraintsHandler.handle_primary_keys`, `*Handler.insert_df` |
| which parent does child row j reference | `Keys.gen_fk` (index sampler → `Keys.gen_pk`) | `RandGenerator.map_methods` | `ConstraintsHandler.handle_foreign_keys` |
| is a key spec admissible | `AdvancedValidator` `pk`/`fk` rules | `DataGenerator.__init__` | `validate_constraints` watermark rules |
| does Spark accept a key | `CommonValidator._validate_spark_column` | `SparkGenerator.__init__` | — |
| where randomness comes from | `DataGenerator` (`SeedSequence` → `rng`, `key_seed`) | `NPCore`, `PyCore`, `Keys` | `np.random.seed(seed)`, `Changer` reseed |
| which row index a batch starts at | `DataGenerator` row counter per stream; the batch writer's file offset `c_f` | `RandGenerator.map_methods` | — |
| how many rows one call writes | `DataGenerator._resolve_size` (B1) | `FileBatchWriter`, `FileStreamWriter` | `FileWriter.size` |
| is a doc example true | `tests/test_docs.py` | `README.md`, `llms.txt`, `docs/*.md` | hand-written test counts and timings |
| how fast each method is | `benchmarks/speed.py` (CI job `benchmarks`) | the agent committing `docs/benchmarks.json` | `tests/test_0_np_core.py` 10^7 `stress` benchmark |
| does a change pass the speed gate | `benchmarks/speed.py` `compare` (1.3× of `docs/benchmarks.json`) | `benchmarks.yml` | — |
| what a seed yields per method | the goldens in `tests/test_2_data_generator.py` (T-070-14) | every later task | — |
| how a csv/parquet file is written | `FileHandler.to_csv`/`to_parquet` over pyarrow | `FileBatchWriter`, `FileStreamWriter` | pandas `to_csv`/`to_parquet` kwargs |
| what a streamed record is | `DataGenerator.stream_dict` (`to_pylist`) | `StreamHandler.convert_dt_to_str` | `to_dict('records')` |
| licence | `LICENSE` | `pyproject.toml` `license` | — |

Bug surface: net reduction — ~370 LOC (handler + three adapters) and `Changer` leave against ~70 LOC of `Keys`; `duckdb` leaves; the global pool and the global seed close. Speed program: one script + one workflow ADD against the `stress` benchmark and job DELETE; FR14 replaces two loops and two pandas calls in place, no second path.

## 2. Strategy

- Core problem: a key must be a pure function of its column definition, a seed and the row index; nothing else may be read.
- Tracer first (T-070-1): `pk` sequence + `fk` uniform through `DataGenerator.get_df`, contract FK ⊂ PK in `tests/test_8_consistency.py`; every later task widens that path.
- DELETE before ADD where expand–contract allows: the checkpoint leaves (T-070-2) once `pk`/`fk` exist, before the key surface grows (T-070-4, T-070-5).
- Seam: `RandGenerator.map_methods(rng, offset, key_seed, column)` binds per-call inputs with `functools.partial` — `rng` for every core method, `offset`/`key_seed`/`column` for the two key methods; the loop builds the table once per column (it already knows `k`) and gains no branch.
- `rng` mapping in the core (T-070-3), the only non-literal renames: `np.random.randint(a, b, n, dtype=d)` → `rng.integers(a, b, n, dtype=d)` (high stays exclusive); `np.random.choice` → `rng.choice`; `np.random.normal` → `rng.normal`. `NPCore.gen_uuid4` body changes (operator "Build from rng bytes"): `b = np.frombuffer(rng.bytes(16*size), np.uint8).reshape(size, 16)`; `b[:,6] = b[:,6] & 0x0F | 0x40`; `b[:,8] = b[:,8] & 0x3F | 0x80` (vectorised); render `str(uuid.UUID(bytes=row.tobytes()))` per row; signature and format kept (AC4.2, AC4.5). Arm B D20 (kwargs, `length`) touches the same function and merges first.
- Operator-written core: tasks change signatures (`rng` keyword) and `np.random.x` → `rng.x`; no body rewrite, naming and style kept. Every task's diff holds or shrinks the touched unit; `Keys` is the only ADD.

## 3. Design

- `DataGenerator.__init__`: `ss = np.random.SeedSequence(seed)`; `self._rng = np.random.default_rng(ss)`; `self._key_seed = int(ss.generate_state(1)[0])` — `seed=None` draws fresh entropy, never the global state (AC4.1). The tracer lands `_key_seed`; T-070-3 adds `_rng`.
- `pk` kwargs and defaults: `style="sequence"`, `start=0`, `step=1`; `permuted` requires `domain`, `key=0`; `format=None`. Row i = `start + i*step`, or `start + feistel(i, domain, key)`.
- `feistel`: balanced Feistel over `2·half` bits (`half = ceil(bits/2)`), 4 rounds of `cell_hash(key + r, ·)` on `uint64`, cycle-walk until `< domain`. Overflow: the prototype's affine `i*a % n` wraps silently in int64 (measured) — not ported; Feistel halves are ≤ 31 bits for `domain < 2^62`, `uint64` hashing wraps by design under `np.errstate(over="ignore")`; the validator refuses `start + domain` past int64 (static); a `sequence` whose `start + (offset+size-1)*step` leaves int64 raises `RandEngineError` in `Keys.gen_pk` at generation time, like AC1.6 (size is unknown to the validator) (AC1.3). Expected walks < 4 (domain ≥ ¼ of the bit range).
- Row index ≥ `domain` → `RandEngineError` naming column and domain (AC1.6); the loop's `ColumnGenerationError` already names the column.
- `format` renders after the integer is computed (`np.char.mod` is not `str.format`; use `[fmt.format(v) for v in ...]`, the existing PyCore style) (AC1.4).
- `fk` row j: `h = cell_hash(fk_seed, offset + j)`; uniform `p = h mod parent_size`; `skew > 0`: `rank = zipf_index(h, parent_size, skew)`, `p = feistel(rank, parent_size, key=fk_seed)` so hot parents scatter (AC2.5); value = `gen_pk` of the parent spec at indices `p`. `fk_seed = crc32(key_seed, spec column name, canonical JSON of the fk kwargs)` (AC2.8) — keys never read `rng` (AC3.1).
- Row index: `get_df` and `write` use offset 0 every call (AC3.3); a `save` over `numFiles` files calls the microbatch with `(n_f, offset=c_f)`, and a stream microbatch split across files adds `c_f` to `c_k` (AC3.5); `stream_dict` and `writeStream` keep a counter `c_k` in the closure that advances by `n_k` (AC3.1, AC3.2).
- Spec immutability: the spec is evaluated per call and never mutated (AC5.2); the `del` leaves with T-070-2.

- Speed program (FR11–FR14), order G16: baseline (T-070-13) → T-070-3 under the gate → goldens (T-070-14) → hot paths (T-070-15..17).
- `benchmarks/speed.py`: one fixed kwargs set per `map_methods` key (`pk`/`fk` included, a sequence parent), one-column spec, sizes 10^6 and 10^7; per run `core_s` (the bound method alone), `get_df_s`, `peak_mib` (`tracemalloc`, which tracks NumPy buffers); times = median of 3, `rows_per_us` = rows ÷ mean `get_df` µs (G1, G3). `compare(current, baseline, limit=1.3) -> (failed, unbaselined)` is the one gate function; `python benchmarks/speed.py --baseline docs/benchmarks.json --out docs/` exits 1 on any failure, renders `BENCHMARKS.md` from the JSON. Outside pytest collection (no `test_*` name). Plain stdlib + NumPy, the core's style.
- `benchmarks.yml`: `on: pull_request: [master]`, `pull_request: [development]`, `workflow_dispatch`; `permissions: contents: read`; ubuntu-latest, Python 3.12; steps: `pytest -m stress`, then the script, then `actions/upload-artifact` of `docs/benchmarks.json` + `docs/BENCHMARKS.md` (`if: always()`); no `${{ }}` of untrusted input in `run:`. The agent downloads the artifact (`gh run download`) and commits it on the work branch with the measured change (AC11.3).
- Baseline bootstrap: `workflow_dispatch` is offered only for a workflow present on the default branch (`master`), and `benchmarks.yml` reaches `master` only at promote. The first baseline comes from the job's first `pull_request` run — a draft PR from the work branch to `development`, opened for measurement and never merged before closure — or the main thread rules otherwise (TASKS T-070-13). The first run has no baseline: every method is recorded, none fails (AC11.3).
- FR12 on T-070-3: the T-070-3 PR run's rows vs the baseline; any method > 1.3× → `np.random.Generator(np.random.SFC64(ss))` in `DataGenerator.__init__` and FR4's ACs re-run; still over → revert T-070-3. Same-seed values are not compared across bit generators (AC4.2 is per generator).
- `dates` (T-070-15): one path, `pd.to_datetime(ts, unit="s").strftime(date_format)` (Cython `format_array_from_datetime`, no per-row Python call), naive UTC; equals per-row `datetime.fromtimestamp(ts, timezone.utc).strftime(fmt)` (B8's form); FR11 rows decide whether it lands (FR12).
- pyarrow option map (T-070-16), from `docs/3_WRITING_FILES.md` and `tests/test_5_files_write_*.py`: csv `index=False` → no-op (Arrow writes no index); csv `sep` → `pyarrow.csv.WriteOptions(delimiter=sep)`; csv `compression` `gzip` → `pa.CompressedOutputStream(path, "gzip")` (also `bz2`, which the tests use); parquet `compression` `snappy`/`gzip`/`zstd`/`brotli`/`lz4` → `pq.write_table(compression=…)` (unchanged backend: pandas already used `engine="pyarrow"`). Cannot map: csv `zip` and `xz` (tested today; Arrow has no zip/xz codec), parquet `engine="fastparquet"` (documented; `fastparquet` already left with D18). An unmapped option raises `RandEngineError` naming it — no pandas fallback (a second path); the CHANGELOG lists the break. Pending main-thread ruling (contradiction with AC14.2 "every option").
- `stream_dict` (T-070-17), checked with pandas 2.3.3 / pyarrow 19 at 3 rows (lock: pandas 2.2.2, pyarrow 23.0.1; same code path, `maybe_box_native`): `to_dict('records')` already yields native `int`/`float`/`bool`/`str`, and `Table.from_pandas(df, preserve_index=False).to_pylist()` yields the same types and `==` records (int32/float64/bool/object/int64 columns; datetimes are `str` after `convert_dt_to_str`). One divergence: a float `NaN` becomes `None` under Arrow (`from_pandas` maps NaN to null); no method emits NaN today — the AC14.3 test pins it.
- Lazy spec: a callable spec is evaluated once per `get_df` and per microbatch (`data_generator.py:45`, `wrapped_lazy_dataframe`). No test guards it today: `test_create_df_simple_with_lazy_spec` passes the called dict, not the callable. T-070-3 adds the guard (a counting callable) in `tests/test_2_data_generator.py`; T-070-17 keeps it green.

## 4. Tests and the test stack

- `tests/test_8_consistency.py` is the relations contract file: every FR1–FR3 and AC5.2 assert reads the output back (frame, Parquet, stream records), never the run alone (AC10.3). Cross-process cases (AC1.5, AC2.3) run a child `python -c` via `subprocess` writing into `tmp_path`.
- Docs (AC7.2, AC8.3): `tests/test_docs.py` extracts the fenced `python` blocks of `docs/*.md` (T-070-8; a superset of the linked docs) and of `README.md` (T-070-9), runs each file's blocks in order in one namespace with `monkeypatch.chdir(tmp_path)`, skips only `python no-run`, and asserts every link of `README.md` and `llms.txt` resolves (AC7.4, AC8.4); docs land before the README so its links resolve on arrival. Stdlib `re` + `exec`; no new dependency.
- AC9.2: evidence `poetry build && pipx run twine check dist/*` (tool run, not a dependency) plus `importlib.metadata` read of the built wheel in the reviewer's evidence.
- Every task commit touching `.py` carries `test-audit: …` and `mutation: K/N killed; kept survivors: …` lines (`~/.claude/rules/private-test-stack.md`); `mutation-diff` runs on the task worktree before commit.
- FR11 (AC11.4): `tests/test_benchmarks.py` — `compare` on literal fake numbers: 1.29× passes, 1.31× fails, an unbaselined method passes and is reported; no file owns benchmarks, so a new one. The script itself runs only in CI.
- FR13: goldens in `tests/test_2_data_generator.py`, one seeded `get_df` at 10^3 rows per NumPy-engine method, literal values or a literal `hashlib.sha256` of `df.to_csv()`; taken from the CI (UTC) run, after B8.
- FR14: each task's equivalence test compares against the old path computed inline in the test at ≤ 10^4 rows (per-row `strftime` in UTC; the pandas-written file; `to_dict('records')`); the old path never stays in `rand_engine/`.
- Every task adding tests or Python source (T-070-13..17 included) runs the `test-audit` authoring gate (`~/.claude/plugins/cache/claude-settings/test-audit/1.0.0/skills/test-audit/SKILL.md`) and `mutation-diff` (`~/.claude/skills/mutation-diff/SKILL.md`) before its commit.
- Light by default (AC10.5): a default test generates ≤ 10^4 rows; each AC's `Stress:` variant carries `@pytest.mark.stress`, deselected by `addopts = "-m 'not stress'"` in `pyproject.toml`, and runs only in the one CI job `benchmarks` (ubuntu-latest, Python 3.12) with the FR11 script (T-070-12, moved by T-070-13).
- Test-run discipline, every task: iterate on the owning test file only; run the full default suite once before the commit; never run `-m stress` locally; at most 2 test-running agents at once on this machine.
- Language gate per task: `ruff check` and the full default `pytest -q -p no:cacheprovider` green.

## 5. Parallel schedule

Done: T-070-1, T-070-2, T-070-7, T-070-12; bugs B1, B3, B4, B5, B6 resolved. Arm B worktrees run one at a time beside the tasks; a task opens only after the bug owning a shared file merged. Open waits: B2 `floats-bounds-truncated`, `int-type-overflow-silent`, `spark-integers-max-exclusive` (`core/_np_core.py`, `core/_spark_core.py`) before T-070-3; B8 `timestamps-depend-on-local-timezone` (`core/_np_core.py`, `tests/test_0_np_core.py`) after T-070-3 merges, before T-070-14; B7 `memory-atom-ignored-by-output-glob` (`.gitignore`) any slot. At most 2 test-running agents at once (this machine): every step is ≤ 2 wide.

| step | tasks open together | width | how |
|---|---|---|---|
| 1 | T-070-13, T-070-4 | 2 | one impl worktree each; T-070-13's baseline run on CI; B2 runs |
| 2 | T-070-3, T-070-5 | 2 | one impl worktree each; T-070-3 after T-070-13's baseline committed and B2 merged; then B8 |
| 3 | T-070-14, T-070-6 | 2 | one impl worktree each; T-070-14 after B8 merged |
| 4 | T-070-15, T-070-16 | 2 | one impl worktree each |
| 5 | T-070-8, T-070-10 | 2 | one impl worktree each |
| 6 | T-070-9, T-070-17 | 2 | one impl worktree each |
| 7 | T-070-11 | 1 | impl worktree; the version bump, last |

- Critical path: T-070-13 (baseline) → B2 → T-070-3 → B8 → T-070-14 → T-070-16 → T-070-8 → T-070-9 → T-070-11 = 7 task steps and two bug merges; T-070-17 sits in step 6 only for the 2-agent cap.
- File-sharing order (not `blocked by:` edges): T-070-3 after T-070-13 (`tests/test_0_np_core.py`); T-070-5 after T-070-4 (`_keys.py`, `advanced_validator.py`, `test_8`); T-070-6 after T-070-3 (`data_generator.py`) and T-070-5 (`test_8`); T-070-14 after T-070-3 (`tests/test_2_data_generator.py`); T-070-15 after B8 (`_np_core.py`); T-070-17 after T-070-6 (`data_generator.py`); T-070-9 after T-070-8 (`tests/test_docs.py`); T-070-11 after T-070-10 (`pyproject.toml`); `.github/workflows/*` are T-070-13's alone.
- Overlap check: disjoint within each step except `TASKS.md`, the `*.jsonl` ledgers and the derived `docs/benchmarks.json` and derived `docs/BENCHMARKS.md` (written only from the CI artifact).
