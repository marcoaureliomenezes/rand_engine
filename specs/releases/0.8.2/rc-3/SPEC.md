# SPEC — Release: 0.8.2, candidate 3 (the agent eval becomes the deploy gate)

**Status:** Draft
**Release ID:** 0.8.2
**Owner:** dd-product-engineer
**Opened:** 2026-11-02
**Origin:** operator-demand

- Demand, operator verbatim, 2026-11-02: "eles medem como um agente saberia usar nossa documentação publica, digas, docstrings para usar com excelencia o rand-engine?? ... o publico do rand-engine será humanos e agentes e para agentes esses evals avaliarão com rigorosos requisitos se a lib rand-engne possui documentações e outras features bem documentadas, disponiveis e otimizadas para acelerar adoção e uso do rand-engine ... São gates?? pois deveriam. É um gate para deploy de qualquer versão do rand-engine validar completamente o rand-engine usando agentes para entender se temos tudo no lugar."
- Sources: the grill `.dadaia/handoff/rand-engine/2026-11-02T233916Z-main-thread-grill-0.8.2-rc3.handoff.json` and the as-is review `2026-11-02T235200Z-dd-sw-engineer-sr-asis-0.8.2-rc3`, both anchored at `feature/0.8.2` `02d6ffe`. Every `path:line` below is a `02d6ffe` anchor; the PLAN re-greps each one before its task.
- FR numbers continue the release (rc-1 and rc-2 end at FR10): rc-3 owns FR11–FR18.
- Not an ADR: a workflow and a required check are reversible (grill, by inspection of the ADR threshold).

### Grill rulings, operator verbatim

| ruling | question | answer | meaning |
|---|---|---|---|
| Placement | Where does the eval redesign go? | "rc-3 da 0.8.2 (Recommended)" | the 0.8.2 promote and PyPI publish wait until the new gate passes |
| Surfaces | Which documentation does each eval measure? | "Descoberta online, uso offline (Recommended)" | discovery runs with web tools; usage tasks run without web and see only the installed package |
| Coverage | What counts as "validate completely"? | "Uma tarefa por feature (Recommended)" | one usage task per user-facing feature of `catalog.json`; a repo test fails on a feature without a task |
| Criteria | What makes a trial pass? | "3 camadas determinísticas (Recommended)" | correct artifact; produced by rand-engine through the documented API; the right feature, no old syntax, within a token ceiling; no LLM judge |
| Gate | Where does the gate block? | "Check obrigatório no promote (Recommended)" | a required check on the promote PR to `master`; runs on `feature/**` and on PRs to `development` stay a non-blocking signal |
| Threshold | What is the pass rule for usage tasks? | "2 de 3 e sem regressão (Recommended)" | every usage task passes at least 2 of 3 trials on the build, and no task scores fewer passes than the previous PyPI release in the same run |
| Discovery | Does discovery also block the deploy? | "Medir e reportar, sem travar (Recommended)" | adoption rate and the leading surface are reported; the gate covers usage tasks only |
| Agents | Which agents run the gate? | "Claude Code, um modelo (Recommended)" | Claude Code with `claude-sonnet-5-5` pinned, on the existing secret |
| Summary | Is this the shared understanding? | "Confirmo (Recommended)" | the eight rulings, the in-scope fixes and the three agent defaults below |

### Agent defaults of the grill

- **Agent default, unruled:** the per-task token ceiling is 2× the median tokens of the passing trials in the first rc-3 run, stored in `task.toml`. Reason: the ceiling needs a measured anchor before the gate binds.
- **Agent default, unruled:** a failed gated task follows the red-CI loop as a bug against the feature that failed. Reason: the gate encodes a documented contract, that every feature is usable by an agent from its shipped docs.
- **Agent default, unruled:** about 1.7 USD per gated run (36 trials × 0.048 USD), an estimate to be replaced by the first run's measurement. §5 Costs re-counts the trials the rulings imply.

### What the operator must see

- 0.8.2 ships only after this gate passes (ruling Placement). No promote or PyPI publish comes first.
- Offline, the agent cannot reach the method reference: `docs/*.md` is not in the wheel (`tests/integrations/test_public_api.py:558-561`), and `rand_engine/llms.txt` holds 28 `https://` lines and no pointer to an installed file, `help()` or the CLI. The as-is review predicts that some usage tasks fail on that surface (Q2), `generation-methods` first.
- A gate failure on a shipped doc surface is a feature-doc bug. rc-3 fixes it itself, because no rc closes with an open bug. **rc-3's scope can grow by those fixes.** A fix that needs a grammar, seed, error-format or default change belongs to 0.9.0 (version ruling, rc-1 SPEC); such a fix goes to the operator, since 0.8.2 cannot ship without it.

## Bug window review

Prior candidate: 0.8.2 rc-2: its two fixed bugs, plus two resolved on `feature/0.8.2` after its closure; `bugs.py status` reports 0 open. Each fix was read with `git show --stat --patch`. This review only judges.

| bug | fix chain | pattern hit | verdict | why |
|---|---|---|---|---|
| `spark-pool-types-fail-or-corrupt` (HIGH) | REBUILDs `b5a2c91`, `c62d00f`, `4532e8e`, `c37b4fe`, `38bf367`, `a690336` of `_spark_pool_problem` (`rand_engine/validators/method_specs.py`) | repetition: six REBUILDs of one decider in one window | KEEP | each REBUILD replaced the one before; the last is +1 −1 (infer over `column.tolist()`). The decider stays a watch item: its next child bug makes a REBUILD due (`LINEAGE.md` §The filter) |
| `spark-text-pool-none-written-as-nan` (HIGH) | `61fcea7` reverted by `7ea4f1a`, then REBUILD `89d1156` | a branch on `pd.StringDtype` inside the new builder; `gen_distincts` edited under the operator's by-name approval ("Approve gen_distincts edit (Recommended)") | KEEP | it collapses two column builds, in the decider and in `gen_distincts`, into one `spark_pool_column`; the branch is pandas 3's string dtype, the root cause; no child bug |
| `none-name-test-expects-pandas2-label` (HIGH) | REBUILD `23f5ecc` | an assert the fix changed: the expected frame is now `pd.DataFrame(expected).to_dict("list")` | KEEP | the contract is the frame pandas builds from the declared names. A literal cannot hold on both pandas 2 and 3 (`None` against `nan`), and a per-version literal would add a branch. The expected values stay literals |
| `workflow-scan-test-reads-locale-encoding` (HIGH) | REBUILD `4ff596b` | none: `encoding="utf-8"` on five reads, net 0 | KEEP | `evals/run.py:47`, `:60` are rebuilt by FR11, and the rebuild keeps UTF-8 reads |

## 1. Problem

- The eval does not measure whether an agent can use rand-engine from its docs. The baseline run 41486371952 (artifacts and run timings, as-is Q1) holds 15 trials, 4 of them passed, at 0.7183 USD, from 16:56:40Z to 16:59:37Z (2 min 57 s), a mean of 0.048 USD per trial.
  - Its 4 passes measure nothing. `e1-cold-discovery`'s check always exits 0, so its 3 passes are vacuous (`passed: true` with `installed: false`). The fourth pass is one of 6 `e3` trials. `e2` passed 0 of 6.
  - `e2`'s check passes a pure numpy or pandas solution (`evals/tasks/e2-named-related-tables/tests/check.py:12-17`).
  - `evals/run.py:98-99` keeps only the check's last stdout line and drops the agent stream (`:76-77` reads it; `:112-113` writes only the result JSON). So no failure can name the doc surface that failed.
  - 8 of the 10 user-facing features have no task.
  - `FLAGS` grants `WebSearch` and `WebFetch` to every task (`run.py:15-16`), so no task measures the installed docs alone.
- **Proven locally** (as-is Q1, the CI's CLI pin and `run.py`'s flags):
  - With `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` (`run.py:77-79`), the CLI forces `permissionMode: default` over the `dontAsk` flag and runs Bash under bubblewrap. On a host with `kernel.apparmor_restrict_unprivileged_userns = 1`, every Bash call returned `bwrap: setting up uid map: Permission denied`.
  - Without the scrub, on the same host, the agent ran `rand-engine get-started lake` and found the `lake` case. `e2`'s check printed `customers=1000 orders=5000 PASS`.
- **Still a hypothesis:**
  - that bubblewrap fails on the GitHub runner. The sysctl lift ran there (all 5 legs printed `= 0`), and the CI token counts only match the local dead-Bash signature;
  - Bash network reach and `pip` under the scrub;
  - every flag of the offline usage round (as-is Q4: this host cannot run the sandbox).

## 2. Measurable goals

- On the promote PR to `master`, a required check passes only when every user-facing feature's usage task passes ≥ 2 of 3 trials on the build and no task scores below the PyPI release in the same run.
- Every failing trial names the layer that failed and, where the transcript shows it, the doc surface. Every trial keeps its transcript and every check output line.
- A solution that builds the artifact without rand-engine fails every usage check.
- Every run's summary reports discovery's adoption rate and leading surface.
- The first rc-3 run measures cost and duration per run, replacing every estimate in §5.

### Wave ranking

| wave | scope | FRs |
|---|---|---|
| 1 — law, skills and dev loop | the harness, the gate script and the aggregate job: the gate itself | FR11, FR15, FR16 |
| 2 — shared foundation | the one provenance helper every check imports (layers 2 and 3) | FR13 |
| 3 — features and bugs | one usage task per feature, discovery, and every feature-doc bug the gate finds | FR12, FR14 |
| 4 — promote-facing | the operator's required-check setting, closure memory and CHANGELOG | FR17, FR18 |

## 3. Non-goals

- An LLM judge. Every layer is deterministic (ruling Criteria).
- Codex or any other harness, and a second model (ruling Agents).
- Gating on discovery (ruling Discovery).
- Any change to the repo `verify:` line or to `pr_to_master.yml`. The required check lives in `eval.yml`.
- Any GitHub setting changed by an agent (FR17).
- A library change made for the eval alone, such as a marker column (as-is Q3). Library changes enter only as feature-doc bug fixes (§What the operator must see).

## 4. Requirements

### FR11 — Harness truth

The eval's own failure must never read as a docs failure. The scrub stays (rc-1 ruling "Scrub child env (Recommended)"); the canary decides whether it works on the runner.

- AC11.1 (E2E, the first CI run's artifact): per trial, the artifact holds the agent's stream-json transcript and the check's full stdout and stderr. The trial JSON keeps today's fields and adds the failed `layer` and the `surfaces` the transcript shows. Repo text reads stay `encoding="utf-8"`.
- AC11.2 (unit, the eval contract tests beside `tests/integrations/test_public_api.py:676-711`): `assert_isolated` also raises when the init event's `permissionMode` or tool list differs from what the round asked. A mismatch is a harness error.
- AC11.3 (E2E, the first CI run; unit for `gate.py`, AC15.2): a `canary` task runs first on each install leg. Through the agent's own Bash, it runs `python -c "import rand_engine"` and `pip --version` in the trial venv, plus a network probe that must fail in the usage round. Its check reads those tool results from the transcript. A red canary makes the leg a harness error, and `gate.py` counts no usage trial of that leg. The failure line names the cause it read, `bwrap` included.
- AC11.4 (integration, the flag-set test; E2E, the first run's transcripts): each task's `task.toml` names its round: `usage`, `discovery` or `canary`. `run.py` maps each round to one flag set. The usage round:
  - disallows `WebSearch` and `WebFetch`;
  - refuses Bash network through the sandbox's strict allowlist, with `failIfUnavailable`, so a broken sandbox fails loud instead of running unsandboxed;
  - scopes `Read` away from the repo checkout.

  The discovery round keeps today's web tools. E2E proof: zero `WebSearch`/`WebFetch` `tool_use` events in any usage transcript, and the canary's network probe fails.
- AC11.5 (E2E, a no-agent step in `eval.yml` that also runs locally): every usage task ships, under its `tests/` and never copied into the agent's directory, a reference solution and a decoy that builds the artifact without rand-engine. Before any agent trial, the job runs each check on both. The reference must pass, and the decoy must fail at layer 2; otherwise it is a harness error.

### FR12 — One usage task per user-facing feature

- AC12.1 (no test; a tree, exercised by AC11.5 and the gated run): `evals/tasks/<slug>/` exists for each of the 10 catalog features whose area is not `quality`: `public-api`, `templates-and-examples`, `data-generator`, `generation-methods`, `spark-generator`, `documentation`, `get-started-cli`, `writers-and-streaming`, `pk-fk-constraints`, `rand-spec-grammar`. Each folder holds `instruction.md`, `task.toml` (round `usage`, timeouts, token ceiling), an optional `environment/` and `tests/check.py`.
  - Each task exercises the documented API in the as-is Q2 table. `e2-named-related-tables` becomes `pk-fk-constraints`, and `e3-fix-by-error` becomes `rand-spec-grammar`, which keeps its instruction, environment and check and adds layer 3.
  - Each instruction asks for a re-runnable script, which layer 2 re-runs.
  - The `spark-generator` trial venv gets `pyspark` and Java from the harness, before the agent starts and outside the agent's network limits. pyspark is not a runtime dependency (`pyproject.toml:41-51`).
- AC12.2 (unit, beside the eval contract tests): one test reads `specs/memory/product/catalog.json`. The set of usage-task folders equals the set of slugs whose `area` is not `quality`. A feature with no task fails it, and so does a usage task whose folder names no catalog feature.

### FR13 — Three deterministic check layers

Each usage check passes a trial only when all three layers hold. No LLM judges any of them.

- AC13.1 (E2E via AC11.5; the checks are the tests), layer 1, the artifact: the task's requested output exists and is correct, for example row counts, key integrity and columns.
- AC13.2 (same level), layer 2, provenance: one shared helper re-runs the agent's script with the trial venv's python under a recording shim on rand-engine's documented entry points (`DataGenerator.get_df`, the writers' `save`, `stream_dict`, `SparkGenerator.get_df`). Layer 2 passes only when the shim recorded at least one call and every artifact column equals a column rand-engine produced. So:
  - a numpy- or pandas-made file fails, even beside a decorative `DataGenerator` call;
  - a script that cannot re-run fails as `provenance`, never as a harness error.

  A static check (an import of `rand_engine` and a call of the documented API) runs first and gives the failure message when no re-run is possible. Known limit: literal values the hook never saw escape it.
- AC13.3 (same level), layer 3, the right feature with excellence:
  - the recorded calls use the task's documented method names and kwargs shape;
  - no legacy name (`RandGenerator`, `rand_engine.main.`, `rand_engine.core.`) appears in the agent's files, and the re-run raises no `DeprecationWarning`;
  - the trial's tokens stay within the `task.toml` ceiling;
  - in the usage round, the transcript holds no web `tool_use`.
- AC13.4 (E2E, the first run): every failing check line names its layer. Surface attribution matches each `tool_use` against surface tokens (`llms.txt`, `help(`, `get-started`, `cases/`, `examples/`, `method_specs`, the `SpecValidationError` text). It is reported in the trial JSON and the summary, and it never gates.

### FR14 — Discovery online: measured and reported, never gating

- AC14.1 (E2E, the first run): one `discovery` task (today's `e1-cold-discovery`, renamed) names no library, keeps web tools and runs with rand-engine not installed, k = 3 once per run. Its trial JSON records:
  - `adopted`: the transcript shows rand-engine installed and imported by the agent's own code;
  - the leading surface: README, PyPI, docs site, search or other, read from the first `tool_use` that names rand-engine.

  The vacuous `passed` goes; the old-syntax regex stays as a report field. The adoption rate and the leading surfaces go to each run's summary.
- AC14.2 (unit, AC15.2's partition): a failed or errored discovery trial never changes `gate.py`'s exit.

### FR15 — `evals/gate.py`: 2 of 3, no regression against PyPI

- AC15.1 (unit): `evals/gate.py`, stdlib only, reads one run's trial JSONs and exits 0 only when:
  - each install leg's canary is green, and no trial is a harness error;
  - every usage task passes at least 2 of 3 trials on the build. A missing trial result counts as a failure;
  - no usage task's build passes fall below its PyPI passes in the same run. The PyPI leg installs the latest PyPI release, 0.8.1 at 0.8.2's promote;
  - every usage task's `task.toml` carries a token ceiling. So the first run, which sets the ceilings, cannot pass.

  It prints one table to stdout for the job summary: task, build passes, PyPI passes, tokens, cost, the failed layer and surface. It replaces the per-leg inline summary at `eval.yml:82-94`.
- AC15.2 (unit, fixture JSONs in `tmp_path`): one case per partition. All green exits 0. Each of these exits non-zero and names its cause: a usage task at 1 of 3; a build at 2 of 3 against PyPI at 3 of 3; a red canary; a harness error; a missing trial; a missing ceiling. A failed discovery trial with everything else green exits 0.

### FR16 — The `Agent eval gate` job

- AC16.1 (integration, the workflow-text test at `tests/integrations/test_public_api.py:704-711`, hardened and never loosened; E2E, the first run on a PR to `master`): `.github/workflows/eval.yml`:
  - keeps its push (`feature/**`, its `paths`), `pull_request` to `development` and `workflow_dispatch` triggers;
  - adds `pull_request` to `master` with **no** `paths` filter, because a skipped workflow leaves a required check pending forever;
  - runs the canary, the usage tasks on both installs (k = 3) and discovery in its trial jobs, each uploading its results;
  - adds a final job named exactly `Agent eval gate`, with `needs` on the trial jobs and `if: always()`. It downloads every artifact, runs `evals/gate.py`, writes its table to the job summary and exits with its code.
  - Discovery results reach the summary but never the exit.
- AC16.2 (integration, the same test): the five-leg `include` matrix (`eval.yml:37-43`) and its per-leg summary step are gone. The CLI pin, bubblewrap install and sysctl lift asserts stay.
- AC16.3 (no test; the run is the check): on `feature/**` pushes and PRs to `development`, the gate job runs and reports; nothing requires it there.

### FR17 — The operator sets the required check (a GitHub setting, never repo code)

- Measured (as-is Q5, `gh api`): `master`'s branch protection has 1 required approval and no `required_status_checks`. Ruleset `master-only-on-PR` (id 8964291) targets `master` **and** `development` and holds no status-check rule; its admin bypass is `always`.
- AC17.1 (no test; operator act, read back by the main thread with `gh api`): after the `Agent eval gate` job has run once on the 0.8.2 promote PR, and before that PR merges, the operator adds `Agent eval gate` to `master`'s required status checks in its branch protection. Adding it to ruleset 8964291 would also gate PRs to `development`, against ruling Gate. No agent changes this setting.
- AC17.2 (no test): the promote PR merges only with `Agent eval gate` green. `pr_to_master.yml`'s `validate_source` keeps the head on `development`, so the run has the `CLAUDE_CODE_OAUTH_TOKEN` secret.

### FR18 — Closure: memory, CHANGELOG, eval docs

- AC18.1 (no test; a job task): `evals/README.md` describes the gate: rounds, layers, `gate.py`, the required check.
- AC18.2 (closure memory pass, `pe`), from the final diff:
  - the `agent-eval` atom: its `tldr`, `summary`, task table, Runner and CI sections, and `:33` ("never a required check");
  - `QUALITY.md:5` and `:26` ("non-blocking workflow"), plus a `## Gates` line for the PR to `master`;
  - `ARCHITECTURE.md:30` ("a non-blocking agent eval") and `:65-66` (the `evals/` tree gains `gate.py` and the task folders);
  - `index.md:70` and the `catalog.json` digest by `catalog generate`.

  These are Gates and layout lines, not Principles, so the wt-rc reconcile carries them (shape 9).
- AC18.3 (integration, `tests/test_docs.py`'s dated-header test): `CHANGELOG.md` `## [0.8.2]` gains an entry for each shipped fix rc-3 lands, a feature-doc bug fix included. The eval ships nothing in the wheel, so it gets no entry (rc-1 FR8 precedent).
- AC18.4 (no test): the closure summary quotes the first gated run's measured trials, passes per task, cost and duration, and the ceilings it set.

## Replaces

- rc-1 AC8.3: E1 "never a pass target", the vacuous `passed=True` included; E2's count-only check, which a numpy solution passes; and E3's check without layer 3. FR12–FR14 replace all three.
- rc-1 AC8.6: "A trial with passed=false never fails the job" and "It is never a required check" become FR15–FR17. The five-leg matrix (E1 once on PyPI; E2 and E3 on PyPI and on the wheel) and its per-leg job summary become FR16's trial jobs and aggregate job.
- `run.py`'s last-line `check_output` and the dropped stream (`:98-99`, `:112-113`) become AC11.1.
- `FLAGS`'s web tools on every task (`run.py:15-16`) become the per-round flag sets (AC11.4).
- Task folders `e1-cold-discovery`, `e2-named-related-tables`, `e3-fix-by-error` are renamed `discovery`, `pk-fk-constraints`, `rand-spec-grammar`. Consumers: `eval.yml:39-43`, `evals/README.md:6`, the atom `agent-eval.md:16-18` (closure), and `_agent_env`'s first-task pick (`test_public_api.py:693`).
- The lines that say "non-blocking": `evals/README.md:3`, `QUALITY.md:5,26`, `ARCHITECTURE.md:30`, `agent-eval.md:4,33`, `index.md:70`, `catalog.json:240`. Each is rewritten from the final diff (AC18.1, AC18.2).
- Unchanged: closed rc-1 and rc-2 text; `test_public_api.py:564-577` (evals stay out of other workflows and of pytest collection); `tests/test_docs.py:965`.

## 5. Constraints and risks

### Costs

| item | value | source |
|---|---|---|
| baseline run, 15 trials | 0.7183 USD, 2 min 57 s, 0.048 USD per trial | measured, run 41486371952 (artifact sum, run timings) |
| one local `e2` trial, Bash working | 0.0700 USD, 5 turns, 130k input tokens | measured, as-is Q1 |
| one local `e2` trial, Bash dead | 0.0425 USD, 4 turns | measured, as-is Q1 |
| gated run, grill's count | about 1.7 USD (36 trials × 0.048) | estimate, grill agent default |
| gated run, the rulings' count | 10 usage tasks × 3 trials × 2 installs + 3 discovery + 2 canary = 65 trials: about 3.1 USD at 0.048, about 4.6 USD at 0.070 | estimate (this SPEC's count; per-trial costs above) |
| gated run duration | not estimated; each trial job's timeout stays within 120 minutes | the PLAN sets the matrix fan-out |
| `spark-generator` trial: pyspark and Java install | PLAN item | — |

- The baseline mean comes from trials whose Bash is suspected dead, so it understates a working trial. The first rc-3 run measures the real cost before the operator sets the required check (FR17), and AC18.4 records it.
- The cost recurs on each `feature/**` push touching `evals/**` and each PR to `development` or `master`.

### Risks

| risk | control |
|---|---|
| bubblewrap fails on the runner, so the agent's Bash is dead (the hypothesis) | the canary runs first and fails as a harness error naming `bwrap` (AC11.3). Fixing user namespaces on the runner keeps the scrub ruling. Dropping the scrub reverses an operator ruling, so it goes to the operator (§6) |
| the offline sandbox silently falls back to unsandboxed Bash, reopening the network | `failIfUnavailable` plus the canary's network probe (AC11.4) |
| a check passes a decoy, or fails its reference solution | AC11.5 runs both before any trial |
| four revisions of the agent shell's env in four days (`be65f43`, `66ca54f`, `9ece9d6`, `f29b3e8`; as-is) | this candidate ends the loop with the canary and the kept stream, not a fifth env tweak |

- At promote, the operator still approves the PyPI publish in the GitHub environment `production` (invariant 13).

## 6. Open questions

- None blocks approval.
  - Conditional: if the canary proves that bubblewrap cannot run on the runner and the runner cannot be fixed: drop the scrub for a token-less design? That would reverse "Scrub child env (Recommended)".
  - For the operator's awareness: the ruleset's admin bypass is `always`, so an admin can merge past the required check. Whether the check binds admins is the operator's own setting; this SPEC changes nothing there.
