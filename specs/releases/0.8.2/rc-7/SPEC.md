# SPEC — Release: 0.8.2, candidate 7 (the rc-6 closure drain: one writer-format decider, test hygiene 3)

**Status:** Draft
**Release ID:** 0.8.2
**Owner:** dd-product-engineer
**Opened:** 2026-11-14
**Origin:** backlog:test-hygiene-3,writer-format-opener-one-decider

- The operator ratified both entries as rc-7's whole scope: "Ratify both (Recommended)" (2026-11-13, `0.8.2-rc4-intake.md`, section "Operator ruling, 2026-11-13 (AskUserQuestion) — rc-7 drain").
- One behaviour changes: an unsupported write format, for example `format("xml")`, raises `RandEngineError: unsupported write format 'xml'` on `save` and on `start`, where today a `KeyError: 'xml'` leaks. The operator's approval of this SPEC covers that change (grill ruling 2).
- The open CRITICAL `setuptools-ghsa-xmj3-open-on-master` closes at the 0.8.2 promote (the `master` merge), outside rc-7 (grill ruling 11).
- Sources: the grill record `2026-11-14T000000Z-main-thread-rc7-grill`; the as-is review `2026-11-13T014103Z-dd-sw-engineer-sr-rc7-as-is-review`; the intake `0.8.2-rc4-intake.md`, rows 189, 191-193, 195-200 and 202. Every `path:line` is a `22fa076` anchor (code equal to `7c73d13`). The PLAN re-greps each one.
- FR numbers continue the release: rc-7 owns FR45–FR49. Not an ADR: every change is reversible, and `FileHandler` is private (absent from `rand_engine/__init__.py`, the docs and the README).

### Rulings, verbatim

| ruling | answer | meaning |
|---|---|---|
| The drain (operator) | "Ratify both (Recommended)" | the two Origin entries are rc-7's whole scope |
| Q3, intake row 200 (operator, 2026-11-14) | "Delete the glob assert (Recommended)" | AC48.3 |
| Grill 1 (main thread) | "one table `_SESSIONS`, one lookup `_session(format)` holding the only refusal; `FileHandler.open_session` and `FileHandler.to_file` replace `_ACCEPTED`, `open_*`, `to_*`, `_to_file`, `__map_methods`, `writer_method` and `_open_session`'s dict and refusal" | FR45 |
| Grill 2, Q1 (main thread) | "an unsupported format raises `RandEngineError: unsupported write format 'xml'` on save and start instead of the leaked `KeyError`" … "RED test first" | AC45.1 |
| Grill 3, Q2 (main thread) | "J5.T2 rewrites the 16 call sites of `tests/test_5_files_write_batch.py` and `tests/test_docs.py:597` to the new call shape; asserts stay byte-identical; the `refactor` commit body names this ruling" | AC45.2 |
| Grill 5, Q4 (main thread) | "`tests/test_docs.py:597` imports the private `_SESSIONS`; no public registry is added" | AC45.5 |
| Grill 6, Q5 (main thread) | "the refusal rows keep the `k=` f-string; the accept row (`k=\"3\"`) is its own case pinning stderr `\"\"`; no conditional in the expectation" | AC46.3 |
| Grill 7, Q6 (main thread) | "`_load_eval_run()` returns the module, bound as `eval_run`; the four shadowing locals become `result`; item 8 is a rename to what all 11 rows hold, no new case" | AC48.1, AC48.2 |
| Grill 8, row 202 (main thread) | "the bare-match sweep covers `tests/test_docs.py:88`, `:340` and `:888`; each gets a message naming the page and what was not found (model `:884`). The nine non-match `is not None` asserts stay." | AC47.3 |
| Grill 9 (main thread) | "Item 2: `ids=` list (one added line, 7 ids). Item 4: the six one-row decorators are deleted, the value bound in the body." | AC46.2, AC47.1; Open question 1 |
| Grill 10 (main thread) | "Jobs 1-4 in wave 1 (disjoint test files), Job 5 in wave 2 waiting on Job 3 (`tests/test_docs.py` in both write sets). J4.T2 (item 9) is a jr task now that the order is given." | §5 |
| Grill 11 (main thread) | "stays a promote-time close, stated in the SPEC Origin" | the Origin bullet above |

## Bug window review

Prior candidate: rc-6. Its window review judged rc-5's one resolved bug, `k-guard-test-runs-wsl-bash-on-windows` (KEEP). No bug was resolved since: `git log 0a72a09..22fa076 -- specs/bugs` prints nothing. One bug is open: `setuptools-ghsa-xmj3-open-on-master` (CRITICAL), outside rc-7. No open or resolved bug sits on a unit rc-7 touches (as-is §0).

| bug | fix | pattern hit | verdict | why |
|---|---|---|---|---|
| none | — | — | — | no fix landed in rc-6's window |

## 1. Problem

- Nothing owns the question "which code writes format F" (as-is §2). The key set `{csv, json, parquet}` is spelled in six places:
  - `_ACCEPTED` (`rand_engine/file_handlers/file_handler.py:50`), `FileHandler.open_csv/json/parquet` and `to_csv/json/parquet` (`:390-411`), and the `getattr(FileHandler, f"open_{format}")` in `_to_file` (`:380`);
  - `_open_session`'s dict (`_writer_batch.py:299-303`) and `__map_methods` (`writer.py:33-39`), which `writer_method` (`writer.py:30`) exposes and both writers index (`_writer_batch.py:394`, `_writer_stream.py:63`).
- Two drains (rc-5 2a48173, rc-6 a46645f) each removed one copy inside `file_handler.py`, and a new drain followed each one on the same key.
- The unsupported-format refusal has two homes, and the reachable one leaks: `DataGenerator(spec).size(2).write.format("xml").save(p)` and `.writeStream.format("xml").start(p)` raise `KeyError: 'xml'`, because `writer_method[...]` runs first. `_writer_batch.py:305` (`unsupported write format`) is unreachable; `git grep -n "unsupported write format" -- tests` prints nothing.
- The K-guard tests (`tests/integrations/test_public_api.py`):
  - `:905`'s name states only K above three, while its guard pins both bounds (`:907`);
  - the parametrize at `:913` has no ids, so the `""` row is hard to tell from the `"-1"` row in a report;
  - `:921` picks the expected stderr by a conditional on the exit code.
- Library tests:
  - six parametrizes hold one row each: `tests/test_0_np_core.py:642,658`, `tests/test_1_common_validator.py:749`, `tests/test_2_data_generator.py:151,165,182`;
  - the docstrings at `tests/test_8_consistency.py:335` and `:342` cite `zipf_index` and `proto`, which the repo does not hold (`git grep -nw zipf_index -- rand_engine` and `git ls-files 'proto*'` print nothing);
  - `tests/test_docs.py:88`, `:340` and `:888` assert a match `is not None` with no message, so a docs drift fails without naming the page.
- Eval tests:
  - `tests/integrations/test_eval_tasks.py:17-20` leaves `spec` and `run` (`evals/run.py`) as module globals, and locals named `run` (`:99,104,151,234`) shadow the module;
  - `:147`'s name claims an undecodable byte for all 11 rows, while 4 rows (`:144-145`) write no file;
  - `tests/integrations/test_eval_check.py:198,200`: the `.pyc`-set assert goes red only on a tree that holds no `rand_engine` bytecode; the child-side `assert sys.dont_write_bytecode` (`:199`) carries the pin.

## 2. Measurable goals

- An unsupported write format raises `RandEngineError` with the message `unsupported write format 'xml'` on `save` and on `start`, and no `KeyError` leaks.
- `git grep -nE 'writer_method|__map_methods|_to_file\b|_ACCEPTED\b|getattr\(FileHandler|FileHandler\.(open|to)_(csv|json|parquet)\b|def (open|to)_(csv|json|parquet)\b' -- . ':!specs'` prints nothing (43 hits at 22fa076).
- `git grep -n "unsupported write format" -- rand_engine` prints one line, in `file_handler.py`.
- `rand_engine/` shrinks: `git diff --numstat -- rand_engine` deletes more lines than it adds (the as-is prototype measured +27 / −58).
- `git grep -nE 'assert \w+ is not None\s*$' -- tests/test_docs.py` (3 hits) and `git grep -nwE 'zipf_index|proto' -- tests/test_8_consistency.py` (2 hits) print nothing.
- Every Origin item lands, or Non-goals names it.

### Wave ranking

| wave | scope | FRs |
|---|---|---|
| 1 — law, skills and dev loop | none | — |
| 2 — shared foundation | none | — |
| 3 — features and bugs | the writer-format decider, the K-guard tests, library tests, eval tests | FR45, FR46, FR47, FR48 |
| 4 — promote-facing | closure | FR49 |

## 3. Non-goals

- A public format registry; `FileHandler` stays private (grill rulings 1 and 5).
- Any change to a writer's output, accepted options or option refusal messages; `sqlite` keeps its own path.
- The nine `is not None` asserts that test no regex match (`test_public_api.py:32,103,288`, `test_0_np_core.py:550`, `test_4_common_rand_specs.py:259,270,326,336`, `test_5_files_write_batch.py:572`): they stay (grill ruling 8).
- A new case for the four eval rows that write no file (grill ruling 7).
- The K guard itself (`.github/workflows/eval.yml`) and the K-guard case's POSIX `skipif` (row 171).
- Any `gen_*` body; any other change that breaks compatibility (grammar, seed, default, exported name): 0.9.0's.
- A PyPI publish or a tag of 0.8.2; closed-candidate text stays history.

## 4. Requirements

### FR45 — One decider maps a write format to its file session (`writer-format-opener-one-decider`, REBUILD)

- AC45.1 (unit, RED first, `tests/test_5_files_write_batch.py` and `tests/test_5_files_write_stream.py`): `DataGenerator(spec).size(2).write.format("xml").save(path)`, `DataGenerator(spec).writeStream.format("xml").start(path)`, `FileHandler.open_session("xml", …)` and `FileHandler.to_file("xml", …)` each raise `RandEngineError` whose message matches `^unsupported write format 'xml'$`. Red at 22fa076: `save` and `start` raise `KeyError: 'xml'`, and the two `FileHandler` names do not exist.
- AC45.2 (unit, the `FileHandler`, batch and stream cases of `tests/test_5_files_write_batch.py` and `tests/test_5_files_write_stream.py`, asserts byte-identical): every file written as csv, json or parquet, every accepted option list and every option refusal message is unchanged. The 16 call sites move to the new call shape (`FileHandler.to_x(` becomes `FileHandler.to_file("x", `; the `getattr(FileHandler, f"open_{format_type}")` row becomes `FileHandler.open_session(format_type, …)`); the `refactor` commit body names grill ruling 3.
- AC45.3 (no test; read on the diff): `file_handler.py` holds one table `_SESSIONS = {"csv": _CsvFile, "json": _JsonFile, "parquet": _ParquetFile}` and one lookup `_session(format)`, the only home of the unsupported-format refusal. Each session class carries its own `ACCEPTED`. `FileHandler.open_session(format, path, options, *, append_from, expected_schema)` and `FileHandler.to_file(format, dataframe, full_path, write_options, writer_keys=())` both resolve the format through `_session`; the batch and stream writers call them with `self.write_format`. The §2 sweeps print what they state.
- AC45.4 (no test; read on the diff): `git diff --numstat -- rand_engine` deletes more lines than it adds, and only `file_handler.py`, `writer.py`, `_writer_batch.py` and `_writer_stream.py` change under `rand_engine/`.
- AC45.5 (unit, `tests/test_docs.py::test_writing_doc_inventory_matches_the_accepted_writer_options`, asserts unchanged): the writer guide's format inventory is checked against the keys of `_SESSIONS` (grill ruling 5).

### FR46 — The K-guard tests state their rows and pin one stderr each (`test-hygiene-3` items 1-3)

- AC46.1 (integration, `tests/integrations/test_public_api.py:905`; name only): the guard-pin case's name states that the trials step refuses a K outside 1 to 3 before the eval; its guard literal and asserts are unchanged.
- AC46.2 (integration, the K-guard parametrize at `:913`): each row carries an id, given as one `ids=` list; the `""` row's id differs from the `"-1"` row's.
- AC46.3 (integration, `:912-921`; grill ruling 6): each refusal row (`"4"`, `"0"`, `"-1"`, `"abc"`, `""`, `"2.5"`) asserts exit 1 and stderr exactly `f"k={k}: k must be an integer from 1 to 3 (the job timeout fits k up to 3)\n"`. `K="3"` is its own case: exit 0 and stderr `""`. No expectation is chosen by a conditional. Both cases keep the POSIX `skipif`, since both run `bash`.

### FR47 — Library test hygiene 3 (`test-hygiene-3` items 4-6, row 202)

- AC47.1 (unit, the six cases at `tests/test_0_np_core.py:642,658`, `tests/test_1_common_validator.py:749`, `tests/test_2_data_generator.py:151,165,182`, asserts unchanged): each one-row `parametrize` decorator is deleted and its value is bound in the case's body.
- AC47.2 (no test; docstring text): `tests/test_8_consistency.py:335` states that the case pins `gen_fk` heads by seed, and `:342` states that it pins the top-of-domain rank literal; neither names `zipf_index` or `proto`.
- AC47.3 (unit, `tests/test_docs.py:88,340,888`): each bare match assert carries a message naming the page and what was not found, as `:884` does; a docs drift fails with that message.

### FR48 — Eval test hygiene 3 (`test-hygiene-3` items 7-9)

- AC48.1 (integration, `tests/integrations/test_eval_tasks.py`, asserts unchanged): a function `_load_eval_run()` loads `evals/run.py` and returns the module, bound at module level as `eval_run`; `spec` is local to the function; the locals at `:99,104,151,234` are named `result`. `git grep -nE '^(spec|run) =|^\s+run =' -- tests/integrations/test_eval_tasks.py` prints nothing (6 hits at 22fa076).
- AC48.2 (integration; name only, grill ruling 7): `:147`'s name states what all 11 rows hold: each reference trial passes its check, and an undecodable byte in an agent-written file, where the row writes one, does not crash it. Its rows are unchanged, and no case is added.
- AC48.3 (integration; a deletion on the operator's order "Delete the glob assert (Recommended)", 2026-11-14): `test_rerun_writes_no_bytecode` (`tests/integrations/test_eval_check.py:196-200`) loses the `before` snapshot (`:198`) and the glob assert (`:200`); `monkeypatch.delenv` and the child-side `assert sys.dont_write_bytecode` stay. Its `test(` commit quotes the order.

### FR49 — Closure: memory and the record

- AC49.1 (closure memory pass, `pe`, from the final diff): `specs/memory/product/output/writers-and-streaming.md` states that an unsupported write format raises `RandEngineError` on `save` and `start`; an atom that names the writer-format mapping matches the code; `catalog.json` is regenerated by `catalog generate`.
- AC49.2 (no test): `CHANGELOG.md`'s `## [0.8.2]` `### Fixed` gains one bullet: an unsupported write format raises `RandEngineError` (`unsupported write format '<format>'`) on `save` and `start`, instead of a `KeyError`. Open question 2.
- AC49.3 (no test; rc-7's closure summary): it quotes the net lines of `rand_engine/` (AC45.4).

## Replaces

- The `KeyError: '<format>'` raised by `save` and `start` on an unsupported format → AC45.1. Consumers: none pins it (as-is §2: `git grep` over tests, docs, README, skills and `specs/memory` prints no hit).
- `_ACCEPTED`, `FileHandler.open_csv/json/parquet`, `FileHandler.to_csv/json/parquet`, `_to_file`, `__map_methods`, `writer_method`, `_open_session`'s dict and its refusal (`_writer_batch.py:299-306`) → AC45.3. Consumers: the 16 call sites in `tests/test_5_files_write_batch.py` and `tests/test_docs.py:597` (AC45.2, AC45.5); `writer_method` is an undocumented attribute of the object `.write` returns (docs, README, skills: 0 hits).
- The conditional stderr expectation (`test_public_api.py:921`) → AC46.3; the six one-row decorators → AC47.1.
- The module globals `spec` and `run` (`test_eval_tasks.py:17-20`) → AC48.1.
- The `before` snapshot and the glob assert (`test_eval_check.py:198,200`) → AC48.3, on the operator's order.

## 5. Constraints and risks

| risk | control |
|---|---|
| `tests/test_docs.py` is in both the row-202 job (AC47.3) and the decider job (AC45.5) | the decider job waits on the other's merge (grill ruling 10) |
| A caller that catches `KeyError` on an unsupported format stops catching it | no doc or test pins the `KeyError` (as-is §2); the Origin states the change, and the operator's SPEC approval covers it (grill ruling 2) |
| The `verify:` line runs `ruff check --select D` on `writer.py`, `_writer_batch.py` and `_writer_stream.py` | a public def added there carries a docstring |
| The three Spark rows of `tests/test_docs.py` need Java; without it they fail on `py4j` (as-is §2) | the decider job's gate runs them with Java |

## 6. Open questions

For the main thread; none blocks the PLAN.

1. **The K-guard ids count.** Grill ruling 9 says "7 ids", which counts the parametrize before ruling 6 moves `K="3"` into its own case. Position: the refusal parametrize keeps 6 rows, so its `ids=` list holds 6 ids (AC46.2 says one id per row).
2. **The CHANGELOG bullet.** No ruling covers it. Position: AC49.2's one `### Fixed` bullet, since the error class a user sees changes; rc-5 (b47d10b) added a 0.8.2 bullet the same way. If the main thread rules no CHANGELOG edit, AC49.2 says so.
