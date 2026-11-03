# Job 9 — the ceilings from the calibration run (wave 5)

Waits on the calibration run (PLAN §3: run 1, pushed by the main thread after Job 8). The dispatch brief carries the run id and the `eval-ceilings` artifact's values, read with `gh run download`; no agent reads the network.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J9.T1 | jr | AC15.3 | `evals/tasks/data-generator/task.toml`, `evals/tasks/public-api/task.toml`, `evals/tasks/templates-and-examples/task.toml`, `evals/tasks/generation-methods/task.toml`, `evals/tasks/pk-fk-constraints/task.toml`, `evals/tasks/documentation/task.toml`, `evals/tasks/get-started-cli/task.toml`, `evals/tasks/writers-and-streaming/task.toml`, `evals/tasks/spark-generator/task.toml`, `evals/tasks/rand-spec-grammar/task.toml` | add `[limits] ceiling_tokens = <value>` to each task that has a ceiling in run 1, the run id in the commit body; a task with 0 passing trials gets none (it is a feature-doc bug first, PLAN §3). No other line changes. Owner test: `tests/integrations/test_eval_gate.py` (a task without a ceiling fails) and the next run |

Done when: `verify:`; each `task.toml` parses.
