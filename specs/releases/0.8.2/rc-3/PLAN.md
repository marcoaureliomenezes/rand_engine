# PLAN — Release: 0.8.2, candidate 3

**Status:** Draft
**Release ID:** 0.8.2
**Owner:** dd-sw-engineer-sr
**SPEC:** `rc-3/SPEC.md` (ae5dedf)

Sources: as-is review `.dadaia/handoff/rand-engine/2026-11-02T235200Z-dd-sw-engineer-sr-asis-0.8.2-rc3` (HEAD `02d6ffe`), the grill `2026-11-02T233916Z-main-thread-grill-0.8.2-rc3`, the pre-mortem and its rulings (SPEC header). Tree `worktrees/rand-engine/0.8.2/rc-3/wt-rc`. Every `path:line` was re-grepped at `ae5dedf` (the define commits touch only `specs/`, so `evals/`, `eval.yml` and the tests read as at `02d6ffe`; `run.py` anchors: `FLAGS` `:15-18`, scrub `:62`, `check_output` `:91`, `{task}-{n}.json` `:118`). Open bugs: none; `bugs.py status` reads 0 open at `ae5dedf`.

Main-thread rulings on the SPEC's new defaults, taken as given: 69 trials per gated run; `check_output` keeps stdout only; the ceiling write-back is a committed job task; the canary is green only when each of the 3 probes shows its expected result in at least one trial.

## 1. As-is review

Bug history = `git log -E --grep '^(fix|refactor)\(bugs\): ' -- <unit>` plus the ledger. `bugs.py stats` prints no `rebuild-due` line; the REBUILDs below are demand-driven (the demand changes the unit's fundamental behaviour, or contradicts its contract).

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `evals/run.py` (125 lines) | per trial: venv, pip install, headless `claude -p`, `check.py`; keeps the check's last stdout line (`:91`), drops the agent stream (read at `:75-77`, only the result JSON written at `:118`); `FLAGS` grants the web tools to every task (`:18`); no leg, round or layer in the result | 2 id lines: `eval-token-reaches-agent-shell` (REBUILD `f29b3e8`, `caused_by J1.T2`, added the scrub), `workflow-scan-test-reads-locale-encoding` (`4ff596b`, UTF-8 reads, unrelated) | REBUILD | the demand changes its behaviour (round flag sets, transcript kept, three layers, canary, surfaces). `f29b3e8` is the commit after which every measured e2 trial failed: the unit is not mature. Four env revisions in four days (`be65f43`, `66ca54f`, `9ece9d6`, `f29b3e8`) on one question: the rebuild ends the loop with the canary and the kept stream, never a fifth tweak |
| `evals/tasks/e1-cold-discovery/` | no library named, `install_rand_engine=false`; `check.py` always exits 0, so `passed=True` is vacuous (3 of 3 `passed:true` with `installed:false`) | 0 | REBUILD | its contract (never fails) contradicts a gated suite; becomes `discovery`, `instruction.md` byte-identical (AC14.1) |
| `evals/tasks/e2-named-related-tables/` | its check passes any parquet with the right counts and fk subset, so pure numpy passes (`tests/check.py:12-17`) | 0 | REBUILD | layer 2 is absent; becomes `pk-fk-constraints` |
| `evals/tasks/e3-fix-by-error/` | repair a broken spec from the library error; the check runs the fixed `spec.py` through `DataGenerator` | 0 | REBUILD | the instruction changes (H5: fix `spec.py`, then a seeded `make.py` saving `out.parquet`), so layers 1 and 2 have a target; becomes `rand-spec-grammar` |
| `evals/tasks/<7 features>`, `canary` | none | 0 | ADD | 7 user-facing features have no task; the canary proves Bash runs python and the sandbox holds before any usage trial counts. No unit carries either |
| `evals/_check.py`, `evals/gate.py`, `evals/selfcheck.py` | none (e1's regex is in its own `check.py:19`) | 0 | ADD | no unit can carry the shared layers, the gate decider or the no-agent self-check; each is stdlib-only except `_check.py`, which imports the library under test |
| `.github/workflows/eval.yml` (101 lines) | triggers push `feature/**` + `paths`, PR to `development`, dispatch; 5-leg matrix with a per-leg summary (`:73-94`); no job aggregates legs; no PR-to-`master` trigger; timeout comment `:33` | 1 id line (`f29b3e8`) | REBUILD | one required check cannot be a matrix of independent legs; the matrix, the per-leg summary and the `3 × 2100 s` comment go |
| `tests/integrations/test_public_api.py:676-711` (`_agent_env`, scrub env test, workflow pin test) | assert the env dict and workflow text only; `:680-682` loads `run.py` by path; `:693-694` picks the first task folder with `SimpleNamespace` args; `:704-711` checks substring order across the whole file | 0 | UPDATE | the green gate diverges from real behaviour (Q1: the scrub puts Bash under bubblewrap). Hardened, loosen nothing: its own fixture task dir (`run.HERE` patched), every `args.<x>` `run_trial` reads, order checked inside one job block |
| `tests/integrations/test_public_api.py:564-577` (`names_the_evals_folder`, `holds_no_file_pytest_collects`) | keep eval out of the other workflows and out of pytest collection | 1 (`4ff596b`, encoding) | KEEP | contract unchanged. Note: the three new test files stay under `tests/integrations/`, not under `evals/` |
| new guard: a catalog user-facing feature without a task fails | none | 0 | ADD | AC12.2; no unit carries it. One test file beside the others |
| `tests/test_docs.py:965` (`excludeFolders` holds `evals`) | the docs build excludes `evals` | 0 | KEEP | unchanged |
| `evals/README.md` | documents the non-blocking workflow | 0 | UPDATE | lying text after the gate ruling (`:3,9,11,19`) |
| `specs/memory/product/quality/agent-eval.md`, `QUALITY.md:5,26`, `ARCHITECTURE.md:30,65-66`, `product/index.md:70`, `catalog.json:240` | the old design, "never a required check" | 0 | UPDATE (closure) | the reconcile's memory pass; `W:` refuses `specs/memory` |
| rc-1 SPEC FR8, AC8.1-AC8.6 | closed history | 0 | KEEP | a closed candidate is never edited; the SPEC `Replaces` names AC8.3 and AC8.6 |
| `rand_engine/llms.txt` (52 lines), public docstrings, `rand_engine/cli.py`, `rand_engine/cases/*`, `rand_engine/examples/**`, `README.md` | the offline doc surfaces: 28 `https://` lines and no pointer to an installed file, `help()` or the CLI | `get-started-scaffold-shadows-package` (`16e8fc1`), `advanced-rand-specs-fail-validation`, `distincts-map-column-order-reversed` (REBUILD `009d443`); no child bug after any | KEEP | the gate finds which gaps hurt; a gate failure becomes a bug against the surface. Predicted first failure: `documentation`, `generation-methods` (no installed method reference: `docs/*.md` is not in the wheel, `test_public_api.py:558-561`) |
| `.github/workflows/pr_to_master.yml` | source must be `development`; test matrix; `summary` job; Temurin 17 step at `:57-61` | 0 | KEEP | the precedent for an `if: always()` aggregate job and the Java step. FR17's setting is not repo code |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| did a trial pass | the task's `tests/check.py` (layer 1) plus `evals/_check.py` (layers 2, 3): one pass bit per trial | `run.py` reads the check's exit code; `gate.py` reads `passed` | e1's vacuous `passed=True`; e1's regex as a pass signal |
| the legacy names and the transcript reader | `evals/_check.py` (`LEGACY`, `tool_events`) | the discovery check (`era`), the canary check, the usage checks | `evals/tasks/e1-cold-discovery/tests/check.py:19` |
| tokens of a trial | `run.py` (the formula of `:80-85`) | the check gets it as `RAND_EVAL_TOKENS`; `gate.py` reads the JSON | none: the check never re-parses the usage |
| does the gate hold | `evals/gate.py` | the aggregate job runs it | the per-leg summary step `eval.yml:82-94` |
| the expected trial set | `task.toml` (`round`, `legs`) and `--k`, read by `gate.py` | `eval.yml`'s matrix is the runner's list; a task the matrix omits is a missing file, a failed trial | none |
| the agent's tools, network and files per round | `ROUNDS` in `run.py` (one mapping, one flag set per round) | `assert_isolated` compares the init event with it | the web tools of `FLAGS` in the usage round |
| the canary verdict | the canary's `check.py` prints one `probe:<name>` line per probe seen in its trial; `gate.py` unions them over the leg's trials | the aggregate job | none |
| which features need a task | `catalog.json`, area not `quality` | `tests/integrations/test_eval_tasks.py` | none |
| a task's token ceiling | `task.toml` `[limits] ceiling_tokens` | `gate.py` (presence), the usage check (value) | none |
| the required check on the promote PR | branch protection on `master` (an operator setting) | `eval.yml`'s job name | none |

### 1.2 Design seams closed

- **D1 `task.toml`.** Keeps `[metadata]`, `[agent] timeout_sec`, `[verifier] timeout_sec`, `[environment] install_rand_engine`. Adds `[task] round` (`usage`, `discovery` or `canary`) and `legs` (`["pypi","wheel"]`; discovery `["pypi"]`); `[environment] requirements` (extra pip requirements, installed before the agent starts and outside its sandbox); `[limits] ceiling_tokens` (usage only).
- **D2 the check's result line.** A check's stdout is stored whole as `check_output`. Its last line starting `RESULT ` holds a JSON object that `run.py` merges into the trial JSON: `layer` and `surfaces` on a failure; `adopted` and `surface` for discovery. Canary probes ride `check_output` as `probe:<name>` lines. One mechanism, no per-round code in `run.py`.
- **D3 the check's env.** `RAND_EVAL_TRANSCRIPT` (path), `RAND_EVAL_TOKENS` (input plus output tokens), `PYTHONPATH=<repo>/evals`. With none of the first two (the no-agent self-check), the transcript-based layer-3 checks (ceiling, web `tool_use`, the surface report) are skipped; layers 1, 2 and the file checks still run.
- **D4 trial layout.** `<out>/{task}-{leg}-{n}.json` and `<out>/{task}-{leg}-{n}/transcript.jsonl`. New JSON keys: `leg`, `round`, `k` (the run's K; `trial` stays n), `layer`, `surfaces`. `run.py` gains `--leg`, kept beside `--rand-engine`. Discovery records `passed: null`. `run.py` exposes `prepare_trial` (venv, pip, requirements, `environment/` copy), which `selfcheck.py` reuses.
- **D5 round flag sets** (`ROUNDS`). `usage`: `--allowedTools Bash,Read,Write,Edit,Glob,Grep`, `--disallowedTools WebSearch,WebFetch`, and `--settings` with the SPEC's sandbox block (§1.3). `discovery`: today's tool list with the web tools, no `--settings`. `canary`: the usage set. `--setting-sources ""` stays in all three.
- **D6 `assert_isolated`** also receives the round's expected `permissionMode` (`default`, the CLI's value under the scrub) and tool list, and raises on any difference (AC11.2).
- **D7 value hash** (AC13.2). Each value becomes `str(v)`, any null-like (`None`, NaN, NaT) becomes the empty string; the column hash is the SHA-256 of the list. Compare name, row count and hash. A writers artifact compares decompressed contents, since gzip headers carry an mtime.
- **D8 layer 2 outside the generators.** `documentation` (the answer's URL is a member of the installed `llms.txt` link set) and `get-started-cli` (the scaffold is byte-equal to the packaged `cases/*.py.txt`) cannot use the recording shim; each names its own source of truth in its check. The other eight use the shim.
- **D9 the canary.** Instruction: run, through Bash, `python -c "import rand_engine; print('IMPORT_OK')"`, `pip --version`, and a `urllib` fetch of a public URL printing `NET_OK` or `NET_FAIL`. A probe is seen when its Bash `tool_result` holds `IMPORT_OK`, a line starting `pip `, or `NET_FAIL` without `NET_OK`. `gate.py` reads the `probe:` lines of the leg's three canary trials; any missing probe is a red canary whose message names the sandbox (distinct text), and the leg's usage trials count for nothing.
- **D10 `--calibrate`.** `gate.py --calibrate --results DIR` writes `ceilings.json` (task to `ceil(2 × median)` of input plus output tokens over the passing usage trials of both legs) and prints it. It runs in its own step before the verdict step and exits 0 once written; the aggregate job's exit code is the plain run's, so calibration never passes the gate.
- **D11 the first-run trigger.** `eval.yml` pushes run for `feature/**`, and the plan adds the one branch shape `wt/*/rc-*/wt-rc` (additive; it keeps the SPEC's triggers). The `wt-rc` is a pushable branch of the contract and its name matches no `feature/**` filter; the work branch moves only by a closed rc. This is the decision I need the operator to approve with the PLAN. Fallback if refused: a draft PR from the pushed `wt-rc` to `development` (the `pull_request` trigger has no `paths`), closed unmerged; it also starts `pr_to_development.yml`.

### 1.3 H7 — does `--settings` apply under `--setting-sources ""` (documentation only, no `claude` run)

- Read: the Claude Code CLI reference's flag table (`https://code.claude.com/docs/en/cli-reference`): `--setting-sources` takes a comma-separated list of sources to load, the values being `user`, `project` and `local`; `--settings` takes a path to a settings JSON file or a JSON string "to load additional settings from". The settings page (`https://code.claude.com/docs/en/settings`) lists command-line arguments as their own precedence tier above local, project and user settings, and the sandbox page (`https://code.claude.com/docs/en/sandboxing`, "Strict allowlist") says the proxy refuses hosts outside `allowedDomains` in every permission mode.
- Verdict: the docs name `--settings` a separate tier, not one of the three sources, and say nothing that lets `--setting-sources ""` cancel it. No page states the combination in a sentence, so "applies" is documented by omission, not guaranteed. I did not re-fetch the pages in this session (no web tool); J1.T2's implementer re-reads the two pages and quotes the lines in the commit body.
- Proof in CI: the canary's network probe is `NET_FAIL` only when the sandbox block is in force, and AC11.2 compares the init `permissionMode` and `tools`. If the block is inert, the network probe prints `NET_OK`, the canary is red and names the sandbox.
- Fallback if it does not apply: `run.py` writes the same JSON as `<trial>/work/.claude/settings.json` and passes `--setting-sources project` instead of `""`. The trial directory is the only project the CLI sees, so no user or project setting of the host loads; AC11.2 still asserts no skill, command, MCP server or plugin. This changes D5 only.

### 1.4 Pre-mortem hits

| hit | answer | task |
|---|---|---|
| H1 init `permissionMode` | D6, the round's expected value | J1.T1, J1.T2 |
| H2 discovery vs gate exit | discovery exempt in `gate.py`; canary and usage errors still exit non-zero | J2.T1, J2.T2 |
| H3 the self-check is not a gate input | the aggregate job `needs` the self-check job and the trials job | J3.T1, J3.T2 |
| H4 leg collision, expected set | D4 file names, D1 keys, `--k` | J1.T3, J2.T2 |
| H5 e3's instruction | `rand-spec-grammar` instruction, both legs | J7.T5 |
| H6 transcript to the check | D3 | J1.T1, J1.T3 |
| H7 sandbox carrier | D5, §1.3 | J1.T2 |
| M1, M6 consumers of `check_output`, the test and README lines | the Replaces list is executed: `run.py:91` (J1.T3), `evals/README.md:19` (J8.T2), `agent-eval.md:27` (reconcile); the hardened tests (J1.T1, J3.T1) | as named |
| M2 value equality | D7 | J4.T1, J4.T2 |
| M3, L10 legacy list | `LEGACY` holds the seven CHANGELOG items only | J4.T1, J4.T3 |
| M4, L14 canary | D9, k = 3 | J5.T1, J2.T2 |
| M5 ceiling bootstrap | D10, the calibration run (§3), J9, J10 | J2.T2, J9.T1, J10.T1 |
| M7 AC11.5 in wave 3 | `selfcheck.py` in Job 5 with the solutions of Jobs 6 and 7 | J5.T3 |
| M8 secrets | the pre-upload scan step; Read denied outside the trial dir | J3.T2, J1.T2 |
| M10 two extra layer-3 checks | in `_check.py` | J4.T3 |
| L2 | the guard filters `round = usage` | J8.T1 |
| L3 | `name: Agent eval gate` | J3.T2 |
| L9 | writers use local sinks; the Spark leg (§4) | J7.T3, J7.T4 |

## DAG

The SPEC's four waves are the ranking; the waves below are schedule waves, one per overlap of `W:`. Jobs of one wave write disjoint files.

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `tests/integrations/test_public_api.py`, `evals/run.py` |
| Job 2 | — | 1 | `tests/integrations/test_eval_gate.py`, `evals/gate.py` |
| Job 3 | Job 1, Job 2 | 2 | `tests/integrations/test_public_api.py`, `.github/workflows/eval.yml` |
| Job 4 | Job 1 | 2 | `tests/integrations/test_eval_check.py`, `evals/_check.py` |
| Job 5 | Job 3, Job 4 | 3 | `evals/tasks/canary/instruction.md`, `evals/tasks/canary/task.toml`, `evals/tasks/canary/tests/check.py`, `evals/tasks/discovery/instruction.md`, `evals/tasks/discovery/task.toml`, `evals/tasks/discovery/tests/check.py`, `evals/tasks/e1-cold-discovery/instruction.md`, `evals/tasks/e1-cold-discovery/task.toml`, `evals/tasks/e1-cold-discovery/tests/check.py`, `evals/selfcheck.py` |
| Job 6 | Job 3, Job 4 | 3 | `evals/tasks/data-generator/instruction.md`, `evals/tasks/data-generator/task.toml`, `evals/tasks/data-generator/tests/check.py`, `evals/tasks/data-generator/tests/solution/solve.py`, `evals/tasks/data-generator/tests/decoy/solve.py`, `evals/tasks/public-api/instruction.md`, `evals/tasks/public-api/task.toml`, `evals/tasks/public-api/tests/check.py`, `evals/tasks/public-api/tests/solution/solve.py`, `evals/tasks/public-api/tests/decoy/solve.py`, `evals/tasks/templates-and-examples/instruction.md`, `evals/tasks/templates-and-examples/task.toml`, `evals/tasks/templates-and-examples/tests/check.py`, `evals/tasks/templates-and-examples/tests/solution/solve.py`, `evals/tasks/templates-and-examples/tests/decoy/solve.py`, `evals/tasks/generation-methods/instruction.md`, `evals/tasks/generation-methods/task.toml`, `evals/tasks/generation-methods/tests/check.py`, `evals/tasks/generation-methods/tests/solution/solve.py`, `evals/tasks/generation-methods/tests/decoy/solve.py`, `evals/tasks/pk-fk-constraints/instruction.md`, `evals/tasks/pk-fk-constraints/task.toml`, `evals/tasks/pk-fk-constraints/tests/check.py`, `evals/tasks/pk-fk-constraints/tests/solution/solve.py`, `evals/tasks/pk-fk-constraints/tests/decoy/solve.py`, `evals/tasks/e2-named-related-tables/instruction.md`, `evals/tasks/e2-named-related-tables/task.toml`, `evals/tasks/e2-named-related-tables/tests/check.py` |
| Job 7 | Job 3, Job 4 | 3 | `evals/tasks/documentation/instruction.md`, `evals/tasks/documentation/task.toml`, `evals/tasks/documentation/tests/check.py`, `evals/tasks/documentation/tests/solution/solve.py`, `evals/tasks/documentation/tests/decoy/solve.py`, `evals/tasks/get-started-cli/instruction.md`, `evals/tasks/get-started-cli/task.toml`, `evals/tasks/get-started-cli/tests/check.py`, `evals/tasks/get-started-cli/tests/solution/solve.py`, `evals/tasks/get-started-cli/tests/decoy/solve.py`, `evals/tasks/writers-and-streaming/instruction.md`, `evals/tasks/writers-and-streaming/task.toml`, `evals/tasks/writers-and-streaming/tests/check.py`, `evals/tasks/writers-and-streaming/tests/solution/solve.py`, `evals/tasks/writers-and-streaming/tests/decoy/solve.py`, `evals/tasks/spark-generator/instruction.md`, `evals/tasks/spark-generator/task.toml`, `evals/tasks/spark-generator/tests/check.py`, `evals/tasks/spark-generator/tests/solution/solve.py`, `evals/tasks/spark-generator/tests/decoy/solve.py`, `evals/tasks/rand-spec-grammar/instruction.md`, `evals/tasks/rand-spec-grammar/task.toml`, `evals/tasks/rand-spec-grammar/tests/check.py`, `evals/tasks/rand-spec-grammar/tests/solution/solve.py`, `evals/tasks/rand-spec-grammar/tests/decoy/solve.py`, `evals/tasks/e3-fix-by-error/instruction.md`, `evals/tasks/e3-fix-by-error/task.toml`, `evals/tasks/e3-fix-by-error/environment/spec.py`, `evals/tasks/e3-fix-by-error/tests/check.py` |
| Job 8 | Job 5, Job 6, Job 7 | 4 | `tests/integrations/test_eval_tasks.py`, `evals/README.md` |
| Job 9 | Job 8 | 5 | `evals/tasks/data-generator/task.toml`, `evals/tasks/public-api/task.toml`, `evals/tasks/templates-and-examples/task.toml`, `evals/tasks/generation-methods/task.toml`, `evals/tasks/pk-fk-constraints/task.toml`, `evals/tasks/documentation/task.toml`, `evals/tasks/get-started-cli/task.toml`, `evals/tasks/writers-and-streaming/task.toml`, `evals/tasks/spark-generator/task.toml`, `evals/tasks/rand-spec-grammar/task.toml` |
| Job 10 | Job 9 | 6 | `evals/tasks/data-generator/task.toml`, `evals/tasks/public-api/task.toml`, `evals/tasks/templates-and-examples/task.toml`, `evals/tasks/generation-methods/task.toml`, `evals/tasks/pk-fk-constraints/task.toml`, `evals/tasks/documentation/task.toml`, `evals/tasks/get-started-cli/task.toml`, `evals/tasks/writers-and-streaming/task.toml`, `evals/tasks/spark-generator/task.toml`, `evals/tasks/rand-spec-grammar/task.toml` |
| Job 11 | Job 8 | 6 | `CHANGELOG.md` |
| Reconciliation | Job 10, Job 11 | 7 | `specs/memory/product/quality/agent-eval.md`, `specs/memory/QUALITY.md`, `specs/memory/ARCHITECTURE.md`, `specs/memory/product/index.md`, `specs/memory/product/catalog.json` |

External steps, not jobs (the DAG table holds jobs only): the **calibration run** (wave 4, after Job 8: the main thread pushes the `wt-rc`, §3) and the **feature-doc bug lanes** (wave 5, after the calibration run: one `wt-hotfix-<bug-id>` each, by bug law). Job 9 also waits on the calibration run; Job 10 on every merged bug lane and on run 2; Job 11 on the bug lanes.

Edge reasons: Job 3 after Job 1 (`test_public_api.py`) and Job 2 (the gate's CLI the workflow calls). Job 4 after Job 1 (the D2 and D3 contract is pinned in its tests). Jobs 5 to 7 after Job 3 (the matrix runs their tasks) and Job 4 (`_check.py`). Job 8's guard needs the ten folders. Job 10 rewrites the ceilings Job 9 wrote (the same ten files, a later wave). Jobs 1 and 2 run together, Jobs 3 and 4, and Jobs 5 to 7.

### Schedule and sizing

- 28 tasks: Job 1 three (2 sr, 1 jr), Job 2 two (1, 1), Job 3 two (2, 0), Job 4 three (2, 1), Job 5 three (3, 0), Job 6 five (3, 2), Job 7 five (5, 0), Job 8 two (1, 1), Jobs 9, 10, 11 one each (jr). 19 sr, 9 jr. Each behaviour is a RED task then an implementation task. The usage tasks are one task each: their check, reference solution and decoy are the tests (AC12.1 states no test), proven by `selfcheck.py` in CI. J8.T1 is green on arrival (the folders exist), as rc-2's J4.T1 was.
- Concurrency: tasks of one job with disjoint `W:` run together. The peak is Job 7's five tasks. In Job 6 the two jr tasks open after `data-generator` (T1) merges: they copy its check pattern.
- An implementation commit may not touch the `tests:` glob (`tests/*`, `WT merge` refuses it), so the new test files are `test(...)` tasks. The task folders hold `tests/check.py` beneath `evals/`; if `WT merge` reads that as the glob, the task is split by path into a `test(J<n>.T<k>)` tree (check, solution, decoy) and its instruction tree, same `W:` halves, and the main thread rules the split at dispatch.
- Net lines: `run.py` is a REBUILD held near its 125 lines plus the new behaviour; the e1, e2, e3 folders move by `git mv`, so each task states its net lines.
- Test rulings reserved, each in a `test(...)` commit naming it: the hardening of `test_public_api.py:676-711` (J1.T1, J3.T1). No assert is loosened or removed; `_agent_env`'s task pick and `SimpleNamespace` change to a fixture dir and the full arg set.
- Fix commits of an Origin bug: none (Origin is `operator-demand`). The feature-doc bugs the gate finds are fixed in `wt-hotfix` lanes (`specs/bugs/AGENTS.md` §2), RED first, and each ships its CHANGELOG line in Job 11.

## 2. Gates

The job gate is the repo's `verify:` line, unchanged. No preflight, matrix or local gate is added. Local tests stay light: `test_eval_gate.py` reads fixture JSONs in `tmp_path`; `test_eval_check.py` runs three scripts of at most 10 rows through the pytest interpreter (no Spark, no network, no agent); `test_eval_tasks.py` reads `catalog.json` and the folder names. AC11.5 (`selfcheck.py`, the references and decoys) runs only in CI.

## 3. The calibration run and the bug loop

1. After Job 8 merges, the main thread pushes the `wt-rc` (D11). The push touches `evals/**`, so `eval.yml` runs. This is run 1: `gate.py --calibrate` writes `ceilings.json` to the job summary and the artifact `eval-ceilings`; the plain gate step fails for lack of ceilings, as designed.
2. Job 9 (jr) copies each usage task's ceiling from run 1 into its `task.toml`, the run id in the commit body. A task with 0 passing trials has no ceiling to copy: it is registered as a feature-doc bug (`dd-bug-registration`, operator-confirmed under the standing rule), fixed in a `wt-hotfix` lane, RED first. The failing transcript names the surface; the first check is whether the trial's transcript shows a dead sandbox or a Spark port error (a harness cause, not a docs bug) before registering anything. A fix that needs a grammar, seed, error-format or default change goes to the operator (SPEC), and one to a `gen_*` docstring needs the operator's by-name approval (L7).
3. Re-run trigger: every push of the `wt-rc` that carries a commit touching `evals/**` or `eval.yml`. Job 9's commit always does, so the push that brings the lane fixes (after `worktree sync`) and Job 9 is run 2: it gates the tasks that have ceilings and re-calibrates the fixed ones. A library-only push does not trigger the workflow, so the fixes never go alone.
4. Job 10 (jr) writes the remaining ceilings from run 2; its push is run 3. If run 1 had no 0-pass task, Job 10 is cancelled with that reason and run 2 is the first gated run. The loop ends when a run's `Agent eval gate` exits 0 on the `wheel` leg; AC18.4 quotes that run and the calibration run.
5. The `wt-rc`'s merge into `feature/0.8.2` and its push run the eval once more (a signal); the PR to `development` and the promote PR to `master` run it again.

## 4. The Spark task's leg

`spark-generator` needs pyspark and Java, and neither is a runtime dependency (`pyproject.toml:41-51`). The trial matrix entry adds `actions/setup-java` Temurin 17 for that task only, pinned like `pr_to_master.yml:57-61`, and the task's `task.toml` carries `requirements = ["pyspark>=3.5,<4"]`, which `prepare_trial` installs into the trial venv before the agent starts, outside the sandbox. Cost: no measurement exists for the eval's install; estimate, from the repo's own test matrix that installs the same pin on every push (`test_on_push.yml:45-50`), tens of seconds for Java setup and the pyspark wheel per trial; the calibration run's per-job duration replaces it. Risk: Spark local mode binds loopback ports and the sandbox allows no domains; a 0-pass `spark-generator` is read first as a harness cause (§3 step 2), and a sandbox block that cannot allow loopback is the operator's call (§6 of the SPEC), never a silent drop.

## 5. The writers task

`writers-and-streaming` writes to local file sinks in the trial directory (a batch `csv` with `compression` and a `writeStream` file sink), never a broker or a cloud path. Its layer 2 compares decompressed contents (D7).

## 6. The operator act (FR17)

Not repo code, not a task. After `Agent eval gate` has run once on a PR to `master`, and before that PR merges, the operator adds it to `master`'s branch protection (never ruleset 8964291, which would gate `development`), then reads it back with `gh api`. The check name exists only after one run, so the act sits after the promote PR opens. No agent changes the setting.

## Measured cost

- Gate law: no task adds a step to `verify:`, `verify-task` or the merge. The count is 40 runs of the job gate: 28 task merges, 11 job merges, one `wt-rc` merge. Per-run time is not re-measured for this PLAN; rc-2's PLAN carried rc-1's reading of 55.74-66.58 s of pytest per run at its head, and that figure is not rc-3's. The added tests are fixture-only: **estimate**, a few seconds per run, source the three file descriptions in §2; the first job gate on each new file measures it.
- Eval cost (SPEC §5, the Gate ruling is the authority to exceed one `verify:` run): a gated run is 69 trials, **estimate** 3.3-4.8 USD (0.048 to 0.070 USD per trial, measured baseline run 41486371952 and as-is Q1), and about 3 minutes per job of up to 3 trials, jobs in parallel (**estimate** from the baseline's 2 min 57 s). The plan expects up to three runs on the `wt-rc` (calibration, the gated re-run, the last ceilings), one on the work-branch push, one on the PR to `development`, one on the PR to `master`: up to six runs, **estimate** 20-29 USD, replaced by the measured figures at closure (AC18.4). Concurrency: 23 trial jobs plus the self-check and the gate job exceed GitHub's free-plan cap of 20 concurrent jobs (usage limits page of GitHub Actions, not re-read here); the excess queues, so duration may stretch.
- Product cost: none; no code path of `rand_engine/` changes except the feature-doc fixes the gate finds.

## Acceptance map

| AC | owner task | implementation task |
|---|---|---|
| AC11.1 | J1.T1 (unit), the first run (E2E) | J1.T3; the token scan J3.T2 |
| AC11.2 | J1.T1 | J1.T2 |
| AC11.3 | J2.T1 (the red canary); the first run | J5.T1, J2.T2 |
| AC11.4 | J1.T1 (flag set), the first run | J1.T2 |
| AC11.5 | none locally (CI only) | J5.T3, with the solutions and decoys of J6, J7 |
| AC12.1 | no test; AC11.5 and the gated run | J6.T1-T5, J7.T1-T5 |
| AC12.2 | J8.T1 | none (green on arrival) |
| AC13.1-AC13.3 | J4.T1; AC11.5 | J4.T2, J4.T3 |
| AC13.4 | J4.T1; the first run | J4.T3 |
| AC14.1 | the first run | J5.T2 |
| AC14.2 | J2.T1 | J2.T2 |
| AC15.1, AC15.2, AC15.3 | J2.T1 | J2.T2, J9.T1, J10.T1 |
| AC16.1, AC16.2 | J3.T1 | J3.T2 |
| AC17.1, AC17.2 | no test; operator act (§6) | none |
| AC18.1 | no test | J8.T2 |
| AC18.2 | Reconciliation | — |
| AC18.3 | the existing dated-header test in `tests/test_docs.py` | J11.T1 |
| AC18.4 | the closure summary | — |

### Reconciliation (the rc's last commits, `RC-FLOW.md` step 4)

Order, `dd-product-engineer`: (1) `release.py phase CLOSURE` first (RC-FLOW step 4); (2) the closure memory pass of `MEMORY-UPDATE.md`: the `agent-eval` atom (tldr, summary, tasks, Runner, CI), `QUALITY.md:5,26` and a `## Gates` line for the PR to `master`, `ARCHITECTURE.md:30,65-66`, `index.md:70`, `catalog.json` by `catalog generate` (shape 9; the main thread confirmed the reconcile carries them). `agent-eval.md:25`'s "no settings sources" is restated with `--settings`.
