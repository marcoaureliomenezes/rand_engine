---
slug: agent-eval
title: Agent eval
tldr: "A CI-only, non-blocking eval measures how a headless agent discovers and uses rand-engine: three tasks, k trials each, one JSON result per trial."
summary: "evals/run.py runs each task under evals/tasks/ k times, each trial in a fresh temporary directory and venv holding the rand-engine under test, with headless claude -p isolated from host settings, skills and MCP servers, then the task's deterministic check. The eval workflow runs it outside pytest and every gating check; a failed trial is a result, only a harness error fails the job."
tags: [eval, agents, ci, quality]
sources:
  - evals/**
  - .github/workflows/eval.yml
---

## Tasks

| task | the agent is asked to | passes when |
|---|---|---|
| `e1-cold-discovery` | produce related `customers` and `orders` Parquet tables, no library named, with rand-engine not installed | never judged: the check records whether rand-engine was installed and imported, and which spec syntax the agent's files use |
| `e2-named-related-tables` | generate 1,000 customers and 5,000 orders with a valid foreign key using the installed rand-engine | both row counts hold, `customer_id` is unique in customers and every order's `customer_id` is in it |
| `e3-fix-by-error` | repair a `spec.py` that does not build, from the library's error alone | the fixed spec generates 1,000 rows with columns `id`, `name`, `amount`, `status` |

- A task is a folder under `evals/tasks/`: `instruction.md` (the prompt), `task.toml` (agent and verifier timeouts, and whether rand-engine is installed), an optional `environment/` copied into the agent's directory, and `tests/check.py`, whose exit 0 means passed ([[pk-fk-constraints]], [[rand-spec-grammar]]).

## Runner

- `python evals/run.py --task <names> --k 3 --rand-engine <requirement or wheel> --model <full model id> --out <dir>` uses the standard library only. `--out` must lie outside the repo.
- Each trial creates a temporary directory with a venv and a separate work directory, installs the rand-engine under test unless the task opts out, and runs headless `claude -p` with no settings sources, MCP servers, slash commands or skills; the init event is asserted to list none.
- The OAuth token reaches only the `claude -p` call, which runs with `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`, so the agent's own shell and tool subprocesses do not inherit it; the scrub needs bubblewrap. A failed isolation, auth, API, rate or usage limit is a harness error: the trial records `error` and the run exits 1. A trial with `passed: false` is a result.
- One JSON per trial records the task, trial, passed, the check's last output line, the model id, input tokens (cache reads and writes included), output tokens, cost and duration.

## CI

- `.github/workflows/eval.yml` runs on push to `feature/**` touching `evals/**` or the workflow, on pull requests to `development`, and on manual dispatch with `model` and `k` inputs. It pins the model id and the agent CLI version, and installs bubblewrap with the runner's unprivileged user-namespace restriction lifted, for the scrub.
- Its matrix runs E1 on the PyPI release, and E2 and E3 on both the PyPI release and the wheel built from the checkout, k = 3 by default. Each leg writes a job-summary table and uploads its trial results as an artifact.
- The eval runs outside pytest and is never a required check; `pytest` collects no `evals/` path and the wheel ships none of it ([[public-api]]).
