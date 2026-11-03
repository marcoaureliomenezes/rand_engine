# Job 10 — the ceilings of the fixed tasks (wave 6)

Waits on Job 9, on every feature-doc bug lane merged and synced, and on run 2 (the push of Job 9 with the fixes, PLAN §3). Conditional: if run 1 had no 0-pass task, this task is **cancelled** with that reason and its row kept.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J10.T1 | jr | AC15.3 | `evals/tasks/data-generator/task.toml`, `evals/tasks/public-api/task.toml`, `evals/tasks/templates-and-examples/task.toml`, `evals/tasks/generation-methods/task.toml`, `evals/tasks/pk-fk-constraints/task.toml`, `evals/tasks/documentation/task.toml`, `evals/tasks/get-started-cli/task.toml`, `evals/tasks/writers-and-streaming/task.toml`, `evals/tasks/spark-generator/task.toml`, `evals/tasks/rand-spec-grammar/task.toml` | add `[limits] ceiling_tokens` to each task Job 9 left without one, from run 2's `eval-ceilings`, run id in the body. A task still at 0 passes after its fix is a new bug or the operator's call; no ceiling is ever invented. Owner test: the next run (run 3, the first fully gated one) |

Done when: `verify:`; each `task.toml` parses.
