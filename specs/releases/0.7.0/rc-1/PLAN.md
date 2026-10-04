# PLAN — Release: 0.7.0, candidate 1 (relations core + visibility)

**Status:** In review
**Release ID:** 0.7.0
**Owner:** dd-software-engineer
**SPEC:** `specs/releases/0.7.0/rc-1/SPEC.md` (In review: amended per the definition review, commits bb0cbb8..19600df); ADR 0002 accepted.
**Approval:** operator, 2026-10-03, verbatim: "Approve trio + 4 fills (Recommended)" — PLAN and TASKS approved with the four fills: the fk seed mixes the fk kwargs; every `docs/*.md` executed; pk defaults `sequence`/`start` 0/`step` 1/`key` 0; T-070-10/11 checked by build + `twine check` evidence.
**Re-approval:** operator, 2026-10-03, verbatim: "Re-approve all three (Recommended)" — SPEC, PLAN and TASKS as amended per the definition review (5fc0fd8, bb0cbb8).
**Amended:** per the dd-code-reviewer definition REJECT at 464e5f7 (F1–F18) and the operator's rulings recorded in the SPEC; awaiting re-review and re-approval.

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
| licence | `LICENSE` | `pyproject.toml` `license` | — |

Bug surface: net reduction — ~370 LOC (handler + three adapters) and `Changer` leave against ~70 LOC of `Keys`; `duckdb` leaves; the global pool and the global seed close.

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

## 4. Tests and the test stack

- `tests/test_8_consistency.py` is the relations contract file: every FR1–FR3 and AC5.2 assert reads the output back (frame, Parquet, stream records), never the run alone (AC10.3). Cross-process cases (AC1.5, AC2.3) run a child `python -c` via `subprocess` writing into `tmp_path`.
- Docs (AC7.2, AC8.3): `tests/test_docs.py` extracts the fenced `python` blocks of `docs/*.md` (T-070-8; a superset of the linked docs) and of `README.md` (T-070-9), runs each file's blocks in order in one namespace with `monkeypatch.chdir(tmp_path)`, skips only `python no-run`, and asserts every link of `README.md` and `llms.txt` resolves (AC7.4, AC8.4); docs land before the README so its links resolve on arrival. Stdlib `re` + `exec`; no new dependency.
- AC9.2: evidence `poetry build && pipx run twine check dist/*` (tool run, not a dependency) plus `importlib.metadata` read of the built wheel in the reviewer's evidence.
- Every task commit touching `.py` carries `test-audit: …` and `mutation: K/N killed; kept survivors: …` lines (`~/.claude/rules/private-test-stack.md`); `mutation-diff` runs on the task worktree before commit.
- Light by default (AC10.5): a default test generates ≤ 10^4 rows; each AC's `Stress:` variant carries `@pytest.mark.stress`, deselected by `addopts = "-m 'not stress'"` in `pyproject.toml`, and runs only in the one CI job `stress` (ubuntu-latest, Python 3.12) with the benchmarks (T-070-12).
- Test-run discipline, every task: iterate on the owning test file only; run the full default suite once before the commit; never run `-m stress` locally; at most 2 test-running agents at once on this machine.
- Language gate per task: `ruff check` and the full default `pytest -q -p no:cacheprovider` green.

## 5. Parallel schedule

Arm B bug worktrees run one at a time beside the tasks; a task opens only after the bug owning a shared file merged. Order: B1 writers `writer-options-consumed-by-use`, `writer-size-not-from-generator` (`file_handlers/*`, `main/data_generator.py`; pending re-review) → B5 `writer-state-shared-across-chains` (`file_handlers/*`, `main/data_generator.py`) → B6 `writer-numfiles-rows-per-file` (`file_handlers/_writer_batch.py`, `_writer_stream.py`) → B3 validators D9/D10/D11/D20 (both validators, `core/_np_core.py` `gen_uuid4`) → B4 dead code D17/D18 (`main/_cdc_generator.py`, `pyproject.toml`, `poetry.lock`, `requirements.txt`, `core/_py_core.py`) → B2 values D12/D14/D15 (`core/_np_core.py`, `core/_spark_core.py`) → B7 `memory-atom-ignored-by-output-glob` (`.gitignore`; any slot, disjoint from every task).

| step | tasks open together | width | how |
|---|---|---|---|
| 1 | T-070-12, T-070-1 | 2 | one impl worktree each; T-070-1 already open (`0.7.0a-impl`) and merges after T-070-12 (its `Stress:` variants need the registered marker); T-070-7 done (5197718); B4 runs |
| 2 | T-070-2 | 1 | impl worktree; after B4 merged; B2 runs |
| 3 | T-070-3, T-070-4 | 2 | one impl worktree each; T-070-3 after B2 (and D20 in B3) merged |
| 4 | T-070-5 | 1 | impl worktree |
| 5 | T-070-6 | 1 | impl worktree |
| 6 | T-070-8, T-070-10 | 2 | one impl worktree each |
| 7 | T-070-9 | 1 | impl worktree; after T-070-10 (the README links `LICENSE`) |
| 8 | T-070-11 | 1 | impl worktree; the version bump, last |

- Critical path: B1 → B5 → B6 → B3 → T-070-12 → T-070-1 (merge) → T-070-2 → T-070-4 → T-070-5 → T-070-6 → T-070-8 → T-070-9 → T-070-11 = 8 task steps after four bug merges; T-070-12 sits inside step 1, so it adds no step.
- File-sharing order (not `blocked by:` edges): T-070-1 merges after T-070-12 (marker registration; W disjoint); T-070-2, T-070-10, T-070-11 after T-070-12 (`pyproject.toml`); T-070-3 after T-070-12 (`tests/test_0_np_core.py`); T-070-2 after T-070-1 (`data_generator.py`, `_rand_generator.py`, `advanced_validator.py`); T-070-3 after T-070-2 (`data_generator.py`, `_rand_generator.py`, `tests/test_2_data_generator.py`); T-070-4 after T-070-2 (`advanced_validator.py`, `tests/test_1_advanced_validator.py`); T-070-5 after T-070-4 (`_keys.py`, `advanced_validator.py`, `test_8`); T-070-6 after T-070-3 (`data_generator.py`) and T-070-5 (`test_8`); T-070-9 after T-070-8 (`tests/test_docs.py`); T-070-11 after T-070-10 (`pyproject.toml`); `.github/workflows/test_on_push.yml` is T-070-12's alone. Bug waits: T-070-6 after B6 (`_writer_batch.py`, `_writer_stream.py`); T-070-3 after D20 and B2 (`_np_core.py`) and B4 (`_py_core.py`); T-070-2 after B4 (`pyproject.toml`, `poetry.lock`, `requirements.txt`); T-070-12 after B4 if B4 is in flight (`pyproject.toml`).
- Overlap check: disjoint within each step except `TASKS.md` and the `*.jsonl` ledgers.
