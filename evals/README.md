# Agent evals

The agent eval measures whether rand-engine's shipped docs let an agent adopt and use each feature. The docs are the docstrings, `help()`, `llms.txt`, the CLI and the examples. Every release must pass the gate. The gate job of `.github/workflows/eval.yml` exits 1 on any `FAIL` line, and it also fails when the `selfcheck` job is red.

## Rounds

Each task sets its round in `task.toml` (`[task] round`). `run.py` maps each round to its tools and flags (`ROUNDS`).

- `usage`: offline. One task per feature. Web tools are disallowed and the sandbox allows no network domain. Gates.
- `canary`: sandbox probes. It shows that the sandbox lets the agent import `rand_engine` and run `pip`, and blocks the network. Gates.
- `discovery`: online. `WebSearch` and `WebFetch` are allowed, and the trial venv has no rand-engine (`install_rand_engine = false`). It records whether the agent adopted rand-engine and which surface it reached first. Its `passed` is `null`. It never gates.

## Check layers

A usage check names the layer of its failure: the failure line starts with `1`, `2` or `3`, and a `RESULT` line carries `"layer"` (`_check.result_text`). The layers run in order.

1. **Artifact.** The output exists, with the asked rows, columns, nulls and values.
2. **Provenance.** `_check.provenance` re-runs the agent's script in a scratch copy, under a recording shim. The shim records each frame rand_engine generates, by row count and per-column hash. Every column of the artifact must match a recorded column. A re-run that records no agent-tagged generation (one called by code under the scratch copy) fails here: a script that does not call rand_engine's generating API, or whose generation is called from library code only. The re-run times out after 300 s. Two usage tasks are exceptions and have no shim re-run. `documentation`: its answer is a URL, and layer 2 checks that the URL is a link of the installed `llms.txt`. `get-started-cli`: its scaffold is byte-equal to the packaged `cases/lake.py.txt`, and the transcript shows a Bash call of the package CLI's `get-started lake`; a missing transcript fails.
3. **Documented use.** The recorded spec uses the documented method and kwargs, and the agent's files use no legacy name (`LEGACY`, 8 patterns). Only the tasks that record a spec get these two checks: every usage task except `documentation` and `get-started-cli`. Every usage task: when the trial recorded tokens, the total is within `ceiling_tokens`, and no web tool was used.

## Gate (`gate.py`)

`gate.py --results <dir> --tasks evals/tasks --k <n>` reads the trial files and prints `FAIL` lines, then a table with the header `task | wheel | pypi | tokens | cost_usd | layer | surface`. It exits 1 when any `FAIL` line exists.

- **Usage.** A leg passes a trial when `passed` is true and `error` is absent. Each task needs at least `k // 2 + 1` wheel passes (2 of 3 at the default `k` of 3). The wheel passes must also be no fewer than the PyPI passes.
- **Canary.** Each leg needs every trial file, no `error`, and each probe (`import`, `pip`, `network`) shown in at least one trial. A leg that misses a probe is void: its usage passes count as 0.
- **Ceilings.** Each usage task needs `ceiling_tokens` under `[limits]` in its `task.toml`. Without it the gate fails.
- **`--calibrate`.** Writes `<results>/ceilings.json` with `ceil(2 × median)` of each usage task's passing token counts, and prints a `ceiling <task> <n>` line for each. It exits 0 once written, whatever the verdict. The gate reads `task.toml`, not `ceilings.json`, so a calibrated value is copied there by hand.

## Self-check job

The `selfcheck` job of `eval.yml` runs `python evals/selfcheck.py --rand-engine <wheel>`. It runs in CI only and uses no agent. For each usage task, the reference (`tests/solution/solve.py`) must pass the check, and the decoy (`tests/decoy/solve.py`) must fail at layer `2`. Any other outcome, and a missing file, is a harness error that names the task. The job also fails when no usage task exists.

## Running a trial

```bash
python evals/run.py --task data-generator --leg wheel --k 3 --rand-engine <requirement or wheel> --model <full model id> --out <dir>
```

- `--task` takes one or more folder names under `evals/tasks/`. `--leg` is required, `pypi` or `wheel`.
- `--out` must be outside this repo. The runner refuses a path inside it. The workflow uses `$RUNNER_TEMP`.
- `--rand-engine` is a pip requirement or a wheel path. Each trial gets a fresh venv.
- Each trial runs headless `claude -p` with no settings sources, no MCP servers and no skills. The init event must list exactly the round's tools. A failed isolation is an error.
- `CLAUDE_CODE_OAUTH_TOKEN` reaches only the `claude -p` call.

## Trial layout

For each trial, `run.py` writes two files under `--out`:

- `{task}-{leg}-{n}.json`: the result. It holds `task`, `trial`, `leg`, `k`, `round`, `passed`, `agent_exit`, `model`, `input_tokens`, `output_tokens`, `cost_usd`, `duration_s` and `check_output`, the check's full stdout. It also holds `error` when the trial failed, and the keys of the check's `RESULT` line.
- `{task}-{leg}-{n}/transcript.jsonl`: the agent's stream-json output.

Input tokens include cache reads and writes. An agent timeout is recorded in `agent_exit`. It is an error only when the stream holds no init event. A `passed: false` trial is a result, not an error. Any trial with `error` makes `run.py` exit 1.

## Adding a task

A task is a folder `evals/tasks/<name>/` with five files:

1. `instruction.md`: the prompt.
2. `task.toml`: `[task] round` and `legs`; `[agent] timeout_sec`; `[verifier] timeout_sec`. A usage task also needs `[limits] ceiling_tokens`. `[environment]` is optional: `install_rand_engine` (default `true`) and `requirements`.
3. `tests/check.py`: run with the trial venv's Python, with the trial's `work/` as cwd. Exit 0 means passed. Layer failures go through `_check.result_text`.
4. `tests/solution/solve.py`: the reference. It produces the right answer with rand_engine.
5. `tests/decoy/solve.py`: the decoy. It produces a plausible wrong answer without the generating API, usually from numpy or pandas alone. The self-check requires it to fail at layer 2.

An optional `environment/` folder is copied into the agent's cwd. A usage task needs both the reference and the decoy. A canary or discovery task needs only the first three files.
