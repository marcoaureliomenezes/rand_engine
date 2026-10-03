# PLAN — Release: 0.7.0, candidate 1 (relations core + visibility)

**Status:** Approved
**Release ID:** 0.7.0
**Owner:** dd-software-engineer
**SPEC:** `specs/releases/0.7.0/rc-1/SPEC.md` (Approved); ADR 0002 accepted.
**Approval:** operator, 2026-10-03, verbatim: "Approve trio + 4 fills (Recommended)" — PLAN and TASKS approved with the four fills: the fk seed mixes the fk kwargs; every `docs/*.md` executed; pk defaults `sequence`/`start` 0/`step` 1/`key` 0; T-070-10/11 checked by build + `twine check` evidence.

## 1. As-is review

Bug ledger: Arm B records D5/D7/D8 (fixed on `wt/0.7.0b-bug`, pending merge) and D9–D20 (registered, fix pending). Fix history = `git log --follow` commit counts (total/`fix`). Evidence: audit 0.6.4, `probes/`, `proto/` under `.dadaia/reports/rand-engine/20261003-revival/`.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `main/_constraints_handler.py` `ConstraintsHandler` | PK rows into a checkpoint DB with `creation_time`; FK sampled from rows inside a wall-clock watermark | D1, D2, D16, D19 (3/1) | DELETE | contract contradicts the SPEC (stateless keys); deletion test: complexity vanishes, replaced by arithmetic |
| `integrations/_sqlite_handler.py`, `_duckdb_handler.py`, `_base_handler.py`, `__init__.py` | class-level connection pool; int64 stored as BLOB; ABC with two adapters used only by the checkpoint | D1, D3, D18, D19 (7/1) | DELETE | no caller after the handler goes; the shared `:memory:` pool is hidden global state; `duckdb` leaves |
| `main/data_generator.py` `DataGenerator` | `np.random.seed(seed)` global; `del spec["constraints"]`; `db_checkpoint`; `option("reset_checkpoint")` | D3, D4, D13 (31/6, the most-fixed unit) | REBUILD (seams only) | ≥ 2 bugs; keep the fluent surface (`size`, `transformers`, `get_df`, `stream_dict`, `write`, `writeStream`); delete `db_checkpoint`, `option`, the `del`; holds one `SeedSequence`, one `rng`, a row counter per stream |
| `main/_rand_generator.py` `RandGenerator` | one dispatch dict; unused `DuckDBHandler` import; dead `validate` param | D11 (16/1) | UPDATE | `map_methods(rng, offset, key_seed)` binds the per-call inputs with `functools.partial`; the column loop is unchanged; dead import/param leave |
| `core/_np_core.py` `NPCore` | operator-written vectorised core over global `np.random` | D12, D13, D14, D15, D20 (9/1) | UPDATE | `rng` keyword per function, `np.random.x` → `rng.x`; bodies otherwise kept; D12/D14/D15/D20 are Arm B |
| `core/_py_core.py` `PyCore` | Python-loop correlated methods; `gen_distincts_untyped` serves `gen_distincts_map` | D13, D18 (9/0) | UPDATE | `rng` keyword; `gen_distincts_untyped` KEEPs (caller `gen_distincts_map`); the DuckDB import is D18 (Arm B) |
| `core/_spark_core.py`, `main/spark_generator.py` | native Spark exprs; no seed | D13, D15 (13/0) | KEEP | D3: Spark rejects keys in the validator; D15 is Arm B |
| — `core/_keys.py` `Keys` | — | — | ADD | no unit can carry a pure `pk(i)` / `fk(j)`: sequence, Feistel cycle-walk permutation, uniform and Zipf parent index; port of `proto/core.py` (`xxh64_long`, `cell_hash`, `zipf_index`) + `proto/feistel.py`, NumPy only, ~70 LOC |
| `validators/advanced_validator.py` | `validate_constraints` (PK/FK/watermark); `METHOD_SPECS` | D9, D11 (3/1) | UPDATE | `pk`/`fk` entries + their rules (AC1.7, AC2.6); `validate_constraints` becomes the AC5.1 refusal naming `pk` and `fk` |
| `validators/common_validator.py` `_validate_spark_column` | Spark spec rules | D9, D10, D20 (3/1) | UPDATE | one refusal for `pk`/`fk` (AC6.1) |
| `utils/update.py` `Changer` | `np.random.seed(None)` reseed; imported by `templates/web_server_logs.py`, never called | D13 | DELETE | global-state writer with no call site |
| `main/_cdc_generator.py` | unimportable | D17 | DELETE (Arm B) | not a task here |
| `README.md` | `unique_ids`/`references`/`get_dfs`/`splitable` examples; six dead links; stale timing | D6 | REBUILD | every `python` block executed by the suite |
| `docs/4_CONSTRAINTS.md`; `docs/1..3_*.md` | drifted API; checkpoint guide | D6 | REBUILD (4), UPDATE (1–3) | keys guide; blocks executed |
| `docs/5_RECIPES.md`, `llms.txt`, `LICENSE` | — | — | ADD | AC8.2, AC8.4, AC9.1: nothing carries them |
| `pyproject.toml`, `poetry.lock`, `requirements.txt`, `CHANGELOG.md` | v2 summary, no licence, one URL, `duckdb`; changelog stops at 0.6.0 | D18 | UPDATE | AC5.4, AC9.2–AC9.4 |
| `AGENTS.md` (repo), `tests/AGENTS.md`, `specs_bkp/` | checkpoint stop condition and key paths; uncalibrated test law; tracked backup | — | UPDATE, UPDATE, DELETE | AC10.1, AC10.2, AC10.4 |
| `tests/integrations/test_sqlite.py`, `test_duckdb.py`, `test_constraints_cleanup.py`, `tests/fixtures/f4_database_handlers.py` | test the deleted adapters | — | DELETE | feature removed |
| `tests/test_8_consistency.py` + `tests/fixtures/f3_data_generator_constraints.py` | VARCHAR-only FK, commented subset asserts | — | REBUILD | the relations contract file (AC10.3); fixture deleted |
| `tests/test_0_*_core.py`, `test_1_*_validator.py`, `test_2_data_generator.py`, `test_5_files_write_*.py` | run checks | — | UPDATE | each owns its RED; no new file except `tests/test_docs.py` (no file owns docs) |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| what is row i's primary key | `Keys.gen_pk` | `RandGenerator.map_methods` | `ConstraintsHandler.handle_primary_keys`, `*Handler.insert_df` |
| which parent does child row j reference | `Keys.gen_fk` (index sampler → `Keys.gen_pk`) | `RandGenerator.map_methods` | `ConstraintsHandler.handle_foreign_keys` |
| is a key spec admissible | `AdvancedValidator` `pk`/`fk` rules | `DataGenerator.__init__` | `validate_constraints` watermark rules |
| does Spark accept a key | `CommonValidator._validate_spark_column` | `SparkGenerator.__init__` | — |
| where randomness comes from | `DataGenerator` (`SeedSequence` → `rng`, `key_seed`) | `NPCore`, `PyCore`, `Keys` | `np.random.seed(seed)`, `Changer` reseed |
| which row index a batch starts at | `DataGenerator` row counter per stream | `RandGenerator.map_methods` | — |
| is a doc example true | `tests/test_docs.py` | `README.md`, `llms.txt`, `docs/*.md` | hand-written test counts and timings |
| licence | `LICENSE` | `pyproject.toml` `license` | — |

Bug surface: net reduction — ~370 LOC (handler + three adapters) and `Changer` leave against ~70 LOC of `Keys`; `duckdb` leaves; the global pool and the global seed close.

## 2. Strategy

- Core problem: a key must be a pure function of its column definition, a seed and the row index; nothing else may be read.
- Tracer first (T-070-1): `pk` sequence + `fk` uniform through `DataGenerator.get_df`, contract FK ⊂ PK in `tests/test_8_consistency.py`; every later task widens that path.
- DELETE before ADD where expand–contract allows: the checkpoint leaves (T-070-2) once `pk`/`fk` exist, before the key surface grows (T-070-4, T-070-5).
- Seam: `RandGenerator.map_methods(rng, offset, key_seed)` binds per-call inputs with `functools.partial` — `rng` for every core method, `offset`/`key_seed` for the two key methods. The column loop gains no branch.
- Operator-written core: tasks change signatures (`rng` keyword) and `np.random.x` → `rng.x`; no body rewrite, naming and style kept. Every task's diff holds or shrinks the touched unit; `Keys` is the only ADD.

## 3. Design

- `DataGenerator.__init__`: `ss = np.random.SeedSequence(seed)`; `self._rng = np.random.default_rng(ss)`; `self._key_seed = int(ss.generate_state(1)[0])` — `seed=None` draws fresh entropy, never the global state (AC4.1). The tracer lands `_key_seed`; T-070-3 adds `_rng`.
- `pk` kwargs and defaults: `style="sequence"`, `start=0`, `step=1`; `permuted` requires `domain`, `key=0`; `format=None`. Row i = `start + i*step`, or `start + feistel(i, domain, key)`.
- `feistel`: balanced Feistel over `2·half` bits (`half = ceil(bits/2)`), 4 rounds of `cell_hash(key + r, ·)` on `uint64`, cycle-walk until `< domain`. Overflow: the prototype's affine `i*a % n` wraps silently in int64 (measured) — not ported; Feistel halves are ≤ 31 bits for `domain < 2^62`, `uint64` hashing wraps by design under `np.errstate(over="ignore")`; the validator refuses `start + domain` or `start + size*step` past int64 (AC1.3). Expected walks < 4 (domain ≥ ¼ of the bit range).
- Row index ≥ `domain` → `RandEngineError` naming column and domain (AC1.6); the loop's `ColumnGenerationError` already names the column.
- `format` renders after the integer is computed (`np.char.mod` is not `str.format`; use `[fmt.format(v) for v in ...]`, the existing PyCore style) (AC1.4).
- `fk` row j: `h = cell_hash(fk_seed, offset + j)`; uniform `p = h mod parent_size`; `skew > 0`: `rank = zipf_index(h, parent_size, skew)`, `p = feistel(rank, parent_size, key=fk_seed)` so hot parents scatter (AC2.5); value = `gen_pk` of the parent spec at indices `p`. `fk_seed = crc32(key_seed, canonical JSON of the fk kwargs)` — keys never read `rng` (AC3.1).
- Row index: `get_df` and `write` use offset 0 every call (AC3.3); `stream_dict` and `writeStream` keep a counter `c_k` in the closure that advances by `n_k` (AC3.1, AC3.2).
- Spec immutability: the spec is evaluated per call and never mutated (AC5.2); the `del` leaves with T-070-2.

## 4. Tests and the test stack

- `tests/test_8_consistency.py` is the relations contract file: every FR1–FR3 and AC5.2 assert reads the output back (frame, Parquet, stream records), never the run alone (AC10.3). Cross-process cases (AC1.5, AC2.3) run a child `python -c` via `subprocess` writing into `tmp_path`.
- Docs (AC7.2, AC8.3): `tests/test_docs.py` extracts the fenced `python` blocks of `docs/*.md` (T-070-8; a superset of the linked docs) and of `README.md` (T-070-9), runs each file's blocks in order in one namespace with `monkeypatch.chdir(tmp_path)`, skips only `python no-run`, and asserts every link of `README.md` and `llms.txt` resolves (AC7.4, AC8.4); docs land before the README so its links resolve on arrival. Stdlib `re` + `exec`; no new dependency.
- AC9.2: evidence `poetry build && pipx run twine check dist/*` (tool run, not a dependency) plus `importlib.metadata` read of the built wheel in the reviewer's evidence.
- Every task commit touching `.py` carries `test-audit: …` and `mutation: K/N killed; kept survivors: …` lines (`~/.claude/rules/private-test-stack.md`); `mutation-diff` runs on the task worktree before commit.
- Language gate per task: `ruff check` and the full `pytest -q -p no:cacheprovider` green.

## 5. Parallel schedule

Arm B bug worktrees run one at a time beside the tasks; a task opens only after the bug owning a shared file merged. Order: B1 D5/D7/D8 (`file_handlers/*`, `main/data_generator.py`; fixed, pending merge) → B3 D9/D10/D11/D20 (both validators, `core/_np_core.py` `gen_uuid4`) → B4 D17/D18 (`main/_cdc_generator.py`, `pyproject.toml`, `poetry.lock`, `requirements.txt`, `core/_py_core.py`) → B2 D12/D14/D15 (`core/_np_core.py`, `core/_spark_core.py`).

| step | tasks open together | width | how |
|---|---|---|---|
| 1 | T-070-1, T-070-7 | 2 | one impl worktree each; after B1 and B3 merged; B4 runs |
| 2 | T-070-2 | 1 | impl worktree; after B4 merged; B2 runs |
| 3 | T-070-3, T-070-4 | 2 | one impl worktree each; T-070-3 after B2 merged |
| 4 | T-070-5 | 1 | impl worktree |
| 5 | T-070-6 | 1 | impl worktree |
| 6 | T-070-8, T-070-10 | 2 | one impl worktree each |
| 7 | T-070-9 | 1 | impl worktree |
| 8 | T-070-11 | 1 | impl worktree; the version bump, last |

- Critical path: B1 → B3 → T-070-1 → T-070-2 → T-070-4 → T-070-5 → T-070-6 → T-070-8 → T-070-9 → T-070-11 = 8 task steps after two bug merges.
- File-sharing order (not `blocked by:` edges): T-070-2 after T-070-1 (`data_generator.py`, `advanced_validator.py`); T-070-4 after T-070-2 (`advanced_validator.py`); T-070-5, T-070-6 serial on `tests/test_8_consistency.py`; T-070-11 after T-070-10 (`pyproject.toml`).
- Overlap check: disjoint within each step except `TASKS.md` and the `*.jsonl` ledgers.
