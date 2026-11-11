---
slug: agent-eval
title: Agent eval
tldr: "A CI gate on whether rand-engine's shipped docs let a headless agent use each feature: ten offline usage tasks, a sandbox canary, k trials per leg."
summary: "evals/run.py runs each task under evals/tasks/ k times, each trial in a fresh temporary directory and venv, with headless claude -p isolated from host settings, skills and MCP servers, then the task's check. A usage check fails at one of three layers: artifact, provenance, documented use. evals/gate.py passes a usage task on at least k // 2 + 1 wheel passes, never fewer than the PyPI leg's, and fails on a red canary, a harness error, a missing file or a task without its task.toml token ceiling. The Agent eval gate job of eval.yml exits with that verdict and also fails on a red no-agent self-check; discovery never gates."
tags: [eval, agents, ci, quality]
sources:
  - evals/**
  - .github/workflows/eval.yml
---

## Rounds

Each task sets its round in `task.toml` (`[task] round`); `run.py` maps the round to its tools and flags.

- `usage` (gates): offline. Web tools are disallowed, the sandbox allows no network domain and denies reading the home directory outside the trial directory.
- `canary` (gates): the same sandbox. The agent runs three probes, and the check prints `probe:import`, `probe:pip` and `probe:network` for each one shown: `rand_engine` imports, `pip` runs, the network is blocked.
- `discovery` (never gates): online, with `WebSearch` and `WebFetch`, on the PyPI leg only, with no rand-engine installed. The agent gets a real data-generation need with no library named; the check records whether it adopted rand-engine, the surface it reached first and any legacy name, and `passed` is `null`.

## Usage tasks

One task per user-facing feature; each runs on the `pypi` and `wheel` legs.

| task | the agent is asked to |
|---|---|
| `data-generator` | build a seeded Parquet dataset from a declarative spec, with nulls and a derived column ([[data-generator]]) |
| `public-api` | write a seeded 100-row Parquet sample through the top-level public API only, and the version to `version.txt` ([[public-api]]) |
| `templates-and-examples` | produce seeded customer and order tables from the ready-made templates and a Faker city pool ([[templates-and-examples]]) |
| `generation-methods` | produce a skewed-popularity column from a pandas-only method with its kwargs ([[generation-methods]]) |
| `pk-fk-constraints` | produce related customers and orders tables whose keys the library enforces ([[pk-fk-constraints]]) |
| `documentation` | find the page documenting a named topic using only what the installed package ships ([[documentation]]) |
| `get-started-cli` | find and use the package CLI to scaffold the data-lake starter into a named directory ([[get-started-cli]]) |
| `writers-and-streaming` | write a gzip CSV batch file and a file stream through the library's writers ([[writers-and-streaming]]) |
| `spark-generator` | build a seeded Spark DataFrame from a spec on `local[1]` and save it as Parquet; the trial installs `pyspark>=4` ([[spark-generator]]) |
| `rand-spec-grammar` | repair a wrong spec from the library's construction error, then build and save a frame from it ([[rand-spec-grammar]]) |

- A task is a folder under `evals/tasks/`: `instruction.md`, `task.toml` (round, legs, agent and verifier timeouts, `[limits] ceiling_tokens` for a usage task, optional `[environment]` `install_rand_engine` and `requirements`), an optional `environment/` copied into the agent's directory, and `tests/check.py`, whose exit 0 means passed. A usage task also carries a reference `tests/solution/solve.py` and a decoy `tests/decoy/solve.py`, which writes numpy-built data beside a decorative `DataGenerator` call; a variant may carry its recorded `transcript.jsonl`.

## Check layers

A usage check runs three layers in order. A failure prints one line starting with its layer; every check ends with one `RESULT` line carrying `layer` (the failing layer, or `pass`) and the documentation surfaces the agent's tool calls touched. Files the agent wrote are read ignoring undecodable bytes.

1. **Artifact**: the output exists with the asked rows, columns, nulls and values.
2. **Provenance**: `evals/_check.py` reads and hashes every delivered artifact, then re-runs the agent's script in a scratch copy without the artifacts, under a recording shim. The shim keeps one record per distinct generation — its entry point (`get_df`, `stream_dict`, `save`, `start`), its evaluated spec and whether code under the scratch copy called it — and hashes the output of each `get_df`, `stream_dict` and file `save`. Every artifact column must match an output the agent's own code called for, so numpy-built data beside a decorative `DataGenerator` call fails. A column hashes as a multiset of its values as text: row order does not count, and `None`, `NaN` and `NaT` hash alike. An undelivered artifact, one that resolves outside the work directory, a re-run that fails or records no generation from the agent's code fails here too. `documentation` instead checks its URL is a link of the installed `llms.txt`; `get-started-cli` checks its scaffold is byte-equal to the packaged starter and that its required transcript shows a Bash call of the package CLI's `get-started lake` — `rand-engine` by basename, `python -m rand_engine`, or `python -c` code calling its `main`.
3. **Documented use**: a spec the agent's code generated with uses the documented method and kwargs, and the agent's files use no legacy name; on every usage task, the trial's tokens stay within the task's `ceiling_tokens` and no web tool was used.

## Gate

- `evals/gate.py --results <dir> --tasks evals/tasks --k <n>` prints `FAIL` lines, then a table `task | wheel | pypi | tokens | cost_usd | layer | surface`, then one line per discovery leg, `discovery <leg>: adopted <n> of <k>, leading surface <s>`, plus `, missing <file>` for each absent trial file, and exits 1 on any `FAIL`; the discovery line never fails the gate. A discovery trial with no surface counts as `other`; a usage task whose passing trials recorded no token total shows `tokens unknown`.
- A usage task needs at least `k // 2 + 1` passing wheel trials (2 of 3 at the default k), and no fewer wheel passes than PyPI passes.
- The canary needs every trial file on each leg, no harness error, and each probe shown in at least one trial; a leg missing a probe is void and its usage passes count as 0.
- A usage task without `ceiling_tokens` fails. `--calibrate` writes `ceilings.json` with `ceil(2 × median)` of each task's passing token totals and exits 0; the gate reads only `task.toml`, so a calibrated value is copied there by hand.

## Self-check

- `evals/selfcheck.py --rand-engine <wheel>` uses no agent: for each usage task the reference must pass its check and the decoy, numpy-built data beside a decorative `DataGenerator` call, must fail at layer 2; a variant's recorded transcript, when present, is handed to its check. Any other outcome, a missing file, or no usage task at all exits 1.

## Runner

- `python evals/run.py --task <names> --leg pypi|wheel --k 3 --rand-engine <requirement or wheel> --model <full model id> --out <dir>` uses the standard library only; `--out` must lie outside the repo.
- Each trial installs the rand-engine under test unless the task opts out, and runs `claude -p` with `--setting-sources ""` (no host settings file), no MCP servers, slash commands or skills; the usage and canary rounds pass their sandbox and permission denies inline with `--settings`. The init event must list exactly the round's tools.
- The OAuth token reaches only the `claude -p` call, which runs with `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` so the agent's subprocesses do not inherit it. A failed isolation, auth, API, rate or usage limit, or a stream with no init event (named by the result event's errors or startup failure reason), is a harness error: the trial records `error` and `passed: false`, and the run exits 1. A `passed: false` trial without `error` is a result.
- Each trial writes `{task}-{leg}-{n}.json` as UTF-8 (task, trial, leg, k, round, passed, agent exit, model, the agent's final message, input tokens with cache reads and writes, output tokens, cost, duration, the check's output, its first failure line and its `RESULT` keys) and its stream-json transcript.

## CI

- `.github/workflows/eval.yml` runs on push to `feature/**` or an rc `wt-rc` branch touching `evals/**` or the workflow, on every pull request to `development` or `master`, and on manual dispatch with `model` and `k` inputs. It pins the model id and the agent CLI version; one concurrency group per ref cancels the run in progress, and a trial job fails when `k` is above 3, the most its timeout fits.
- Every job's checkout sets `persist-credentials: false`, so no git token stays in the workspace.
- The `Eval self-check` job runs `selfcheck.py` on the wheel built from the checkout.
- One trial job per task and leg: the canary and every usage task on both legs, discovery on PyPI. Each refreshes the package index and installs bubblewrap and socat, lifting the runner's unprivileged user-namespace restriction where that setting exists, for the agent's subprocess sandbox; scans its results for the token, deleting them and failing on a hit; and uploads them as an artifact.
- The `Agent eval gate` job needs the self-check and every trial job and always runs: it downloads every result, writes the calibrated ceilings to the job summary and an artifact, prints the gate table, exits with `gate.py`'s code, and fails when the self-check is red. Whether it is a required check is a GitHub branch-protection setting, not repo code.
- The eval runs outside pytest: no file under `evals/` is one pytest collects, and the wheel ships none of it ([[public-api]]).
