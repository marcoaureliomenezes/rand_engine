# Agent evals

Agent eval of how an agent uses rand-engine. It runs in its own non-blocking workflow, `.github/workflows/eval.yml`, outside pytest and the required checks: on push to `feature/**` touching `evals/**` or the workflow, on pull requests to `development`, and on `workflow_dispatch` (inputs `model`, `k`). The repository secret `CLAUDE_CODE_OAUTH_TOKEN` authenticates the agent; the runner only inherits it from the environment.

```bash
python evals/run.py --task e3-fix-by-error --k 3 --rand-engine <requirement or wheel> --model <full model id> --out <dir>
```

- `--out` must be outside this repo; the runner refuses a path inside it (the workflow uses `$RUNNER_TEMP`). One JSON per trial: task, trial, passed, input and output tokens (input counts cache reads and writes), cost, duration, model id.
- `--rand-engine` is a pip requirement or a wheel path, installed into a fresh venv per trial; `--task` takes folder names under `evals/tasks/`.
- Each trial runs headless `claude -p` with no settings sources, no MCP servers, no skills; the init event is asserted. A failed isolation or auth is a harness error: the trial records `error` and the run exits 1. A trial with `passed: false` is a result, not an error.

## Task contract

`evals/tasks/<name>/` holds `instruction.md` (the prompt), `task.toml`, an optional `environment/` and `tests/check.py`.

- `task.toml`: `[agent] timeout_sec`, `[verifier] timeout_sec`, and optionally `[environment] install_rand_engine` (default `true`; `false` leaves the trial venv without rand-engine, for cold discovery).
- Trial layout: `<tmp>/venv` is the venv, `<tmp>/work` is the agent's cwd with `environment/` copied in; the venv is never inside `work`. The agent runs with `PATH=<tmp>/venv/bin:$PATH` and `VIRTUAL_ENV=<tmp>/venv`.
- The check runs as `<tmp>/venv/bin/python <task>/tests/check.py` with cwd `<tmp>/work`; exit 0 means passed. Its last stdout line is stored as `check_output` in every result.
