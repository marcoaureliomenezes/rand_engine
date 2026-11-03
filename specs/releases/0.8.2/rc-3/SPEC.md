# SPEC — Release: 0.8.2, candidate 3 (the agent eval becomes the deploy gate)

**Status:** Approved
**Release ID:** 0.8.2
**Owner:** dd-product-engineer
**Opened:** 2026-11-02
**Origin:** operator-demand

- Demand, operator verbatim, 2026-11-02: "eles medem como um agente saberia usar nossa documentação publica, digas, docstrings para usar com excelencia o rand-engine?? ... o publico do rand-engine será humanos e agentes e para agentes esses evals avaliarão com rigorosos requisitos se a lib rand-engne possui documentações e outras features bem documentadas, disponiveis e otimizadas para acelerar adoção e uso do rand-engine ... São gates?? pois deveriam. É um gate para deploy de qualquer versão do rand-engine validar completamente o rand-engine usando agentes para entender se temos tudo no lugar."
- Sources:
  - the grill `.dadaia/handoff/rand-engine/2026-11-02T233916Z-main-thread-grill-0.8.2-rc3.handoff.json`;
  - the as-is review `2026-11-02T235200Z-dd-sw-engineer-sr-asis-0.8.2-rc3`;
  - the `dd-researcher` consumer pre-mortem of `54894ca` (`.dadaia/tmp/main/20261102/premortem-0.8.2-rc3.md`), whose findings H1–H7, M1–M10 and L1–L14 the main thread ruled. Each ruling is tagged "main-thread ruling (pre-mortem)".

  Every `path:line` is a `02d6ffe` anchor; the PLAN re-greps it.
- FR numbers continue the release: rc-3 owns FR11–FR18. Not an ADR: the change is reversible.
- L5, main-thread ruling (pre-mortem): an operator-demand origin satisfies the slop law's "a candidate exists only with scope that changes behavior".

### Grill rulings, operator verbatim

| ruling | answer | meaning |
|---|---|---|
| Placement | "rc-3 da 0.8.2 (Recommended)" | the 0.8.2 promote and PyPI publish wait for the new gate |
| Surfaces | "Descoberta online, uso offline (Recommended)" | discovery runs with web tools; usage tasks see only the installed package |
| Coverage | "Uma tarefa por feature (Recommended)" | one usage task per user-facing `catalog.json` feature; a repo test fails on a feature without one |
| Criteria | "3 camadas determinísticas (Recommended)" | correct artifact; made by rand-engine through the documented API; the right feature, no old syntax, within a token ceiling; no LLM judge |
| Gate | "Check obrigatório no promote (Recommended)" | a required check on the promote PR to `master`; `feature/**` and PRs to `development` are a signal |
| Threshold | "2 de 3 e sem regressão (Recommended)" | each usage task passes ≥ 2 of 3 on the build, and none scores below the PyPI release in the same run |
| Discovery | "Medir e reportar, sem travar (Recommended)" | adoption and the leading surface are reported; never gated |
| Agents | "Claude Code, um modelo (Recommended)" | Claude Code, `claude-sonnet-5-5` pinned, on the existing secret |
| Summary | "Confirmo (Recommended)" | rulings, fixes, three defaults |

### Agent defaults of the grill

- **Agent default, unruled:** the per-task token ceiling is 2× the median tokens of the passing trials in the first rc-3 run, stored in `task.toml`. M5 sets its mechanics (AC15.3).
- **Agent default, unruled:** a failed gated task follows the red-CI loop as a bug against the failing feature. L13, main-thread ruling (pre-mortem): a bug-law note, no AC.
- **Agent default, unruled:** about 1.7 USD per gated run (36 trials × 0.048 USD); §5 re-counts it.

### What the operator must see

- 0.8.2 ships only after this gate passes (Placement).
- Offline, the method reference is unreachable. `docs/*.md` is not in the wheel (`tests/integrations/test_public_api.py:558-561`). `rand_engine/llms.txt` holds 28 `https://` lines and no pointer to an installed file, `help()` or the CLI. The as-is review predicts failures there, `generation-methods` first.
- A gate failure on a shipped doc surface is a feature-doc bug that rc-3 fixes itself, since no rc closes with an open bug. **The scope can grow by those fixes.**
  - A fix that needs a grammar, seed, error-format or default change is 0.9.0's (version ruling) and goes to the operator.
  - L7, main-thread ruling (pre-mortem): a fix to a `gen_*` docstring needs the operator's by-name approval (invariant 12).
- M10, main-thread ruling (pre-mortem), for approval: layer 3 carries two checks beyond the grill's wording:
  - the documented method and kwargs, as "the right feature" (Criteria);
  - no web `tool_use` in the usage round, which enforces "uso offline" (Surfaces).

## Bug window review

Prior candidate: rc-2: its two fixed bugs plus two resolved after its closure; 0 open. Each fix was read with `git show --stat --patch`.

| bug | fix chain | pattern hit | verdict | why |
|---|---|---|---|---|
| `spark-pool-types-fail-or-corrupt` (HIGH) | REBUILDs `b5a2c91`, `c62d00f`, `4532e8e`, `c37b4fe`, `38bf367`, `a690336` of `_spark_pool_problem` | repetition: six REBUILDs of one decider | KEEP | each replaced the last (the last is +1 −1); a watch item: its next child bug makes a REBUILD due |
| `spark-text-pool-none-written-as-nan` (HIGH) | `61fcea7`, reverted `7ea4f1a`; REBUILD `89d1156` | a `pd.StringDtype` branch; `gen_distincts` edited with "Approve gen_distincts edit (Recommended)" | KEEP | two column builds collapse into one `spark_pool_column`; the branch is the root cause; no child bug |
| `none-name-test-expects-pandas2-label` (HIGH) | REBUILD `23f5ecc` | a changed assert: the expected value is `pd.DataFrame(expected).to_dict("list")` | KEEP | no literal holds on pandas 2 and 3; a per-version literal adds a branch |
| `workflow-scan-test-reads-locale-encoding` (HIGH) | REBUILD `4ff596b` | none; net 0 | KEEP | FR11 rebuilds `evals/run.py:47,60` and keeps their UTF-8 reads |

## 1. Problem

- Baseline run 41486371952 (artifacts and run timings): 15 trials, 4 passed, 0.7183 USD, 16:56:40Z–16:59:37Z (2 min 57 s), a mean of 0.048 USD per trial. It measures nothing about the docs:
  - `e1`'s check always exits 0 (3 vacuous passes); `e2` passed 0 of 6, `e3` 1 of 6;
  - `e2`'s check passes a pure numpy or pandas solution (`evals/tasks/e2-named-related-tables/tests/check.py:12-17`);
  - `evals/run.py:91` keeps the check's last stdout line. The stream lives only in memory (`:66-74`), and `:118` writes only the result JSON, so no failure names a doc surface;
  - 8 of the 10 user-facing features have no task;
  - `FLAGS` (`run.py:15-18`) grants `WebSearch` and `WebFetch` to every task (`:18`).
- **Proven locally** (as-is Q1, CI flags):
  - With the scrub on (`run.py:62-63`), the CLI forces `permissionMode: default` over `dontAsk` and runs Bash under bubblewrap. With unprivileged user namespaces restricted, every Bash call failed (`bwrap: setting up uid map: Permission denied`).
  - Without it, the agent found `get-started lake` and `e2` passed.
- **Still a hypothesis:** bubblewrap failing on the runner, where the sysctl lift ran (only the CI token counts match the dead-Bash signature); Bash network and `pip` under the scrub; every offline-round flag.

## 2. Measurable goals

- On the promote PR to `master`, a required check passes only under the Threshold ruling, for every user-facing feature.
- Every failing trial names its layer and, where the transcript shows it, the doc surface. Every trial keeps its transcript and the check's full output.
- A solution made without rand-engine fails every usage check.
- Every run's summary reports discovery's adoption and leading surface; the calibration run replaces every §5 estimate.

### Wave ranking

M7, main-thread ruling (pre-mortem): AC11.5 sits in wave 3, with the solutions it runs.

| wave | scope | FRs |
|---|---|---|
| 1 — law, skills and dev loop | the harness, `gate.py`, the aggregate job | FR11 (except AC11.5), FR15, FR16 |
| 2 — shared foundation | the provenance helper `evals/_check.py` | FR13 |
| 3 — features and bugs | the usage tasks, discovery, the self-check job, and feature-doc bugs | FR12, FR14, AC11.5 |
| 4 — promote-facing | the required-check setting, closure | FR17, FR18 |

## 3. Non-goals

- An LLM judge (Criteria). Codex or any other harness, and a second model (Agents). Gating on discovery (Discovery).
- Any change to the repo `verify:` line or to `pr_to_master.yml`. Any GitHub setting changed by an agent.
- A library change for the eval alone (a marker column); library changes enter only as feature-doc bug fixes.

## 4. Requirements

### FR11 — Harness truth

The eval's own failure never reads as a docs failure. The scrub stays ("Scrub child env (Recommended)"), and the canary proves whether it works.

- AC11.1 (unit, the eval contract tests, `tests/integrations/test_public_api.py:676-711`; E2E, the first run's artifact). H4, H6, M1, M8, main-thread rulings (pre-mortem):
  - `run.py` writes the agent stream to `<trial>/transcript.jsonl`. It runs `check.py` with `RAND_EVAL_TRANSCRIPT=<path>` and `PYTHONPATH=<repo>/evals` in its env, so `from _check import …` resolves.
  - The trial JSON adds `leg` (`pypi` or `wheel`), `round` (`usage`, `discovery` or `canary`), `k`, the failed `layer` and `surfaces`. `check_output` keeps its name and holds the check's full stdout. Discovery records `passed: null`.
  - Files are named `{task}-{leg}-{n}.json`; the artifact also holds each transcript.
  - Before upload, a step fails the leg as a harness error and deletes the artifact when any artifact file contains the OAuth token's value. The token is never printed.
- AC11.2 (unit, the same tests). H1, main-thread ruling (pre-mortem): `assert_isolated` also raises unless:
  - the init `permissionMode` equals the mode the CLI reports for the round's flags, `default` under the scrub;
  - the init `tools` list holds exactly the round's allowed tools.

  A mismatch is a harness error.
- AC11.3 (E2E, the first run; unit via AC15.2). M4, L14, main-thread rulings (pre-mortem): a `canary` task runs on each leg with k = 3. Through the agent's Bash it runs:
  - `python -c "import rand_engine"` and `pip --version`, in the trial venv;
  - a network probe, which must fail in the usage round.

  The canary is green when at least one trial's transcript holds each probe's Bash `tool_result` with the expected output. It is red only when none does. A red canary is a harness error whose message names the sandbox, distinct from every other harness error's message, and `gate.py` counts no usage trial of that leg.
- AC11.4 (integration, the flag-set test; E2E, the first run's transcripts). H7, M8, main-thread rulings (pre-mortem): each `task.toml` names its round, and `run.py` maps each round to one flag set.
  - The usage round passes `--settings <json>`, carrying a sandbox block:
    - `enabled`, `failIfUnavailable` and `allowUnsandboxedCommands: false`;
    - network with no allowed domains;
    - Read denied outside the trial directory, the runner home included.
  - It also passes `--disallowedTools WebSearch,WebFetch`. The discovery round keeps the web tools.
  - `--setting-sources ""` stays, so no user or project settings load. Whether a CLI `--settings` still applies under it is a PLAN verification item; the canary and AC11.2 prove it in CI.
  - E2E: no usage transcript holds a `WebSearch` or `WebFetch` `tool_use`.
- AC11.5 (E2E, CI only). H3, L6, M7, main-thread rulings (pre-mortem): every usage task ships, under its `tests/` and never copied to the agent, a reference solution and a decoy that makes the artifact without rand-engine.
  - A no-agent self-check job runs each check on both, writing under the runner's temp dir. The reference must pass and the decoy must fail at layer 2; anything else is a harness error.
  - It never runs in local pytest.

### FR12 — One usage task per user-facing feature

- AC12.1 (no test; a tree that AC11.5 and the gated run exercise): `evals/tasks/<slug>/` exists, round `usage`, for each catalog feature whose area is not `quality`: `public-api`, `templates-and-examples`, `data-generator`, `generation-methods`, `spark-generator`, `documentation`, `get-started-cli`, `writers-and-streaming`, `pk-fk-constraints`, `rand-spec-grammar`.
  - Each folder holds `instruction.md`, `task.toml` (round, legs, timeouts, ceiling), an optional `environment/` and `tests/check.py`. Each task exercises the documented API of the as-is Q2 table.
  - M2, main-thread ruling (pre-mortem): every instruction asks for a re-runnable script with a fixed seed.
  - `e2-named-related-tables` becomes `pk-fk-constraints`.
  - H5, main-thread ruling (pre-mortem): `e3-fix-by-error` becomes `rand-spec-grammar`, with a changed instruction:
    - the agent fixes `spec.py`, then writes a re-runnable, seeded `make.py` that builds the frame from `spec` and saves `out.parquet`;
    - layer 1 checks `out.parquet` (1,000 rows, columns `id`, `name`, `amount`, `status`), and layer 2 re-runs `make.py`;
    - both legs get the new instruction, so the same-run comparison holds.
  - L9, main-thread ruling (pre-mortem): `writers-and-streaming` writes to local file sinks in the trial directory. The `spark-generator` leg installs pyspark and Java before the agent starts (a PLAN item); pyspark is not a runtime dependency.
- AC12.2 (unit, beside the eval contract tests). L2, main-thread ruling (pre-mortem): one test reads `specs/memory/product/catalog.json`. The folders whose `task.toml` round is `usage` equal the slugs whose `area` is not `quality`. A missing task fails it, and so does an extra one.

### FR13 — Three deterministic check layers

A usage trial passes only when all three layers hold; no LLM judges any of them. The checks share `evals/_check.py`.

- AC13.1 (E2E via AC11.5; the checks are the tests), layer 1: the requested artifact exists and is correct (row counts, keys, columns).
- AC13.2 (same level), layer 2, provenance. M2, main-thread ruling (pre-mortem): the helper re-runs the agent's script, `make.py` included, with the trial venv's python under a recording shim. The shim wraps `DataGenerator.get_df`, the writers' `save`, `stream_dict` and `SparkGenerator.get_df`.
  - Layer 2 passes only when each artifact column's name, row count and value hash equal those of a frame or record rand-engine returned in that re-run. The fixed seed keeps the re-run deterministic.
  - A numpy-made file fails, even beside a decorative `DataGenerator` call.
  - A script that cannot re-run fails as `provenance`, never as a harness error. A static check (a `rand_engine` import and a call of the documented API) runs first and supplies the message.
- AC13.3 (same level), layer 3. M3, M10, L10, main-thread rulings (pre-mortem):
  - the recorded calls use the task's documented method and kwargs (Criteria);
  - no legacy name or syntax appears in the agent's files. Legacy means only what `CHANGELOG.md` marks removed or renamed:
    - `ExampleSpecs` (`:251`);
    - the top-level `constraints` key (`:117`);
    - `db_checkpoint()` and `option()` (`:118`);
    - `uuid4`'s `length` (`:124`);
    - the positional `args` key (`:125`);
    - the `splitable` and `sep` keys (`:126`);
    - `validate_with_warnings` and `validate_spark_with_warnings` (`:46`);
  - the trial's input plus output tokens stay within the `task.toml` ceiling;
  - no web `tool_use` appears in the usage round (Surfaces).
- AC13.4 (E2E, the first run): every failing check line names its layer. Surface attribution is reported, never gated. It matches each `tool_use` against these surface tokens: `llms.txt`, `help(`, `get-started`, `cases/`, `examples/`, `method_specs`, and the `SpecValidationError` text.

### FR14 — Discovery online: measured and reported, never gating

- AC14.1 (E2E, the first run). L1, L12, M1, M3, main-thread rulings (pre-mortem): `e1-cold-discovery` is renamed `discovery`, and its `instruction.md` stays byte-identical. It names no library, keeps the web tools and starts without rand-engine, k = 3, once per run.
  - The agent can install only from PyPI, so the adoption figure describes the latest PyPI release, never the build.
  - The trial JSON records `passed: null`, `adopted` (the transcript shows rand-engine installed and then imported by the agent's code) and the leading surface (README, PyPI, docs site, search or other). The leading surface is the first `tool_use` that names rand-engine.
  - The era field's legacy regex follows AC13.3's list.
  - The adoption rate and the leading surfaces go to each run's summary.
- AC14.2 (unit, AC15.2). H2, main-thread ruling (pre-mortem): a discovery trial's failure or error is reported and never changes `gate.py`'s exit.

### FR15 — `evals/gate.py`: 2 of 3, no regression against PyPI

- AC15.1 (unit). H2, H4, main-thread rulings (pre-mortem): `evals/gate.py`, stdlib only, derives the expected trial set from `evals/tasks/*/task.toml` (round, legs) and `k`. A missing file counts as a failed trial. It exits 0 only when:
  - each leg's canary is green, and no canary or usage trial is a harness error. Discovery is exempt;
  - every usage task passes ≥ 2 of 3 on the `wheel` leg;
  - no usage task's `wheel` passes fall below its `pypi` passes. The `pypi` leg installs the latest PyPI release, 0.8.1 at 0.8.2's promote;
  - every usage task's `task.toml` carries a ceiling.

  It prints one table for the job summary: task, wheel and PyPI passes, tokens, cost, the failed layer and the surface. It replaces the per-leg summary at `eval.yml:82-94`.
- AC15.2 (unit, fixture JSONs in `tmp_path`). L4, main-thread ruling (pre-mortem): one case per partition.
  - All green exits 0.
  - Each of these exits non-zero and names its cause: 1 of 3; wheel 2 of 3 against PyPI 3 of 3; a red canary; a usage harness error; a missing file; a missing ceiling.
  - A failed or errored discovery trial, with everything else green, exits 0.

  The test pins the 2-of-3 and no-regression rule, so a PR that weakens it shows in its diff. The promote PR's review is the guard.
- AC15.3 (unit, the same file). M5, main-thread ruling (pre-mortem): the first CI run is the calibration run. `gate.py --calibrate` writes each usage task's ceiling to the run's output, and never passes the gate. The ceiling is 2× the median input plus output tokens of its passing trials, and a job task commits it to the task's `task.toml`.
  - A task with 0 passes in calibration is a feature-doc bug, fixed in rc-3 before it gets a ceiling.
  - Outside `--calibrate`, a task without a ceiling fails.

### FR16 — The `Agent eval gate` job

- AC16.1 (integration: the workflow-text tests, hardened and never loosened; E2E: the first run on a PR to `master`). H3, L3, main-thread rulings (pre-mortem): `.github/workflows/eval.yml`:
  - keeps its push (`feature/**`, `paths`), PR-to-`development` and dispatch triggers;
  - adds `pull_request` to `master` with **no** `paths` filter, since a skipped workflow leaves a required check pending;
  - runs the canary, the usage tasks on both legs (k = 3) and discovery, each job uploading its results;
  - ends with a job declared `name: Agent eval gate`. It `needs` the self-check job and every trial job, runs with `if: always()`, downloads every artifact, runs `gate.py`, writes the table to the summary and exits with its code;
- AC16.2 (integration, the same tests):
  - the five-leg `include` matrix (`eval.yml:37-43`) and its per-leg summary step are gone;
  - the timeout comment (`:33`) states the new trial set;
  - the CLI pin, bubblewrap and sysctl asserts stay.

### FR17 — The operator sets the required check (a GitHub setting, never repo code)

- Measured (as-is Q5, `gh api`): `master`'s branch protection requires 1 approval and no status check. Ruleset 8964291 targets `master` **and** `development`, with no status-check rule and admin bypass `always`.
- AC17.1 (no test; operator act, read back with `gh api`): after `Agent eval gate` has run once on the 0.8.2 promote PR, and before that PR merges, the operator adds the check to `master`'s branch protection. Adding it to ruleset 8964291 would also gate `development`, against the Gate ruling. No agent changes the setting.
- AC17.2 (no test): the promote PR merges only with `Agent eval gate` green. `validate_source` keeps the head on `development`, so the run has `CLAUDE_CODE_OAUTH_TOKEN`.

### FR18 — Closure: memory, CHANGELOG, eval docs

- AC18.1 (no test; a job task): `evals/README.md` describes the gate.
- AC18.2 (closure memory pass, `pe`, from the final diff): these lines change:
  - the `agent-eval` atom (`tldr`, `summary`, tasks, Runner, CI, `:33`);
  - `QUALITY.md:5,26`, plus a `## Gates` line for the PR to `master`;
  - `ARCHITECTURE.md:30,65-66`;
  - `index.md:70`;
  - `catalog.json`, by `catalog generate`.

  The `wt-rc` reconcile carries them (shape 9; main thread confirmed).
- AC18.3 (integration, the dated-header test in `tests/test_docs.py`): `## [0.8.2]` gains an entry for each shipped fix rc-3 lands. The eval ships nothing in the wheel, so it gets none (the rc-1 FR8 precedent).
- AC18.4 (no test): the closure summary quotes the calibration run and the first gated run (passes per task, cost, duration) and the ceilings.

## Replaces

M1 and M6, main-thread rulings (pre-mortem), add the consumers.

- rc-1 AC8.3: E1 "never a pass target" with its vacuous `passed=True`, E2's count-only check, and E3's check with no layer 3. FR12–FR14 replace them.
- rc-1 AC8.6: "passed=false never fails the job", "never a required check", and the five-leg matrix with its per-leg summary. FR15–FR17 replace them.
- The last-line `check_output` (`run.py:91`), the in-memory stream (`:66-74`) and `{task}-{n}.json` (`:118`) become AC11.1. The `check_output` consumers are `run.py:91`, `evals/README.md:19` and `agent-eval.md:27`.
- The web tools on every task (`run.py:18`) become the round flag sets (AC11.4).
- `e1-cold-discovery`, `e2-named-related-tables` and `e3-fix-by-error` become `discovery`, `pk-fk-constraints` and `rand-spec-grammar`, and e3's instruction changes (H5). Consumers: `eval.yml:39-43`, `evals/README.md:6`, `agent-eval.md:16-18`.
- The eval contract tests are hardened, never loosened (AC11.1, AC11.2, AC16.1):
  - `test_public_api.py:680-682` loads `run.py` by path;
  - `:693-694` picks the first task folder and passes `SimpleNamespace` args, which must carry every `args.<x>` that `run_trial` reads;
  - `:704-711` checks substring order, which must not pass vacuously against the rebuilt workflow.
- `eval.yml:33`, the `3 × 2100 s` timeout comment.
- The "non-blocking" text is rewritten from the final diff:
  - `evals/README.md:3,9,11,19`;
  - `agent-eval.md:4,20,25,33` (`:25`'s "no settings sources" is restated with H7's `--settings`);
  - `QUALITY.md:5,26`, `ARCHITECTURE.md:30`, `index.md:70`, `catalog.json:240`.

## 5. Constraints and risks

### Costs

M9, main-thread ruling (pre-mortem): the operator's Gate ruling is the authority that lets this gate cost more than one `verify:` run.

| item | value | source |
|---|---|---|
| baseline run, 15 trials | 0.7183 USD, 2 min 57 s, 0.048 USD per trial | measured, run 41486371952 |
| local `e2` trial, Bash working / dead | 0.0700 USD / 0.0425 USD | measured, as-is Q1 |
| gated run, cost | 10 × 3 × 2 legs + 3 discovery + 2 legs × 3 canary = 69 trials: **3.3–4.8 USD** at 0.048–0.070 USD per trial. The ruled 3.1–4.6 USD counted 65 trials, before M4 gave the canary k = 3 | **estimate**, from the two rows above; measured by the calibration run |
| gated run, duration | about **3 min per job of up to 3 trials**, with jobs in parallel | **estimate**: the baseline's 2 min 57 s for a 5-leg matrix of up to 3 trials (dead-Bash trials: likely low); measured by the calibration run |

- The cost recurs only on PRs to `development` (signal) and `master` (gate), and on `feature/**` pushes touching `evals/**` (signal).

### Risks

| risk | control |
|---|---|
| bubblewrap fails on the runner (the hypothesis) | the red canary names the sandbox (AC11.3). Fixing the runner keeps the scrub; dropping it is the operator's call (§6) |
| four env revisions of the agent's shell in four days (`be65f43`, `66ca54f`, `9ece9d6`, `f29b3e8`) | the canary and the kept stream end the loop, not a fifth tweak |

- At promote, the operator still approves the PyPI publish in the `production` environment (invariant 13).

## 6. Open questions

- None blocks approval.
  - Conditional: if the canary proves that bubblewrap cannot run on the runner and the runner cannot be fixed, does the scrub go, for a token-less design? That reverses "Scrub child env (Recommended)".
  - For awareness: the ruleset's admin bypass is `always`, so an admin can merge past the check. Binding admins is the operator's setting; this SPEC changes nothing there.
