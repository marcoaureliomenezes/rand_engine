# Agent evals

On-demand eval of how an agent uses rand-engine. Outside pytest, the `verify:` line and CI.

```bash
python evals/run.py --task e3-fix-by-error --k 3 \
  --rand-engine rand-engine==0.8.1 --model <full model id> --out ~/eval-results
```

- `--out` must be outside this repo; the runner refuses a path inside it. One JSON per trial: task, trial, passed, input and output tokens (input counts cache reads and writes), cost, duration, model id.
- `--rand-engine` is a pip requirement or a wheel path, installed into a fresh venv per trial; `--task` takes folder names under `evals/tasks/`.
- Trial Bash runs in Claude Code's native sandbox: writes confined to the trial temp directory, network only to PyPI, no unsandboxed fallback (the run fails if the sandbox cannot start); WebSearch and WebFetch stay on, as in a stock session.
- Each trial runs headless `claude -p` in a fresh temp directory with no settings sources, no MCP servers, no skills; the stream's init event is asserted and a leak fails the trial. Auth is whatever the caller's environment already holds; the runner never reads or stores it.

## Task contract

`evals/tasks/<name>/` holds `instruction.md` (the prompt), `task.toml`, an optional `environment/` and `tests/check.py`.

- `task.toml`: `[agent] timeout_sec`, `[verifier] timeout_sec`, and optionally `[environment] install_rand_engine` (default `true`; `false` leaves the trial venv without rand-engine, for cold discovery).
- Trial layout: `<tmp>/venv` is the venv, `<tmp>/work` is the agent's cwd with `environment/` copied in; the venv is never inside `work`. The agent runs with `PATH=<tmp>/venv/bin:$PATH` and `VIRTUAL_ENV=<tmp>/venv`.
- The check runs as `<tmp>/venv/bin/python <task>/tests/check.py` with cwd `<tmp>/work`; exit 0 means passed. Its last stdout line is stored as `check_output` in every result.
