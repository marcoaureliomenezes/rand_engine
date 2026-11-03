# Job 8 — the coverage guard and the eval README (wave 4)

Waits on Jobs 5 to 7 (the ten folders exist). The two tasks are disjoint and run together. The calibration run (PLAN §3) is pushed after this job merges, so run 1 sees the final eval tree.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J8.T1 | sr | AC12.2 | `tests/integrations/test_eval_tasks.py` | green on arrival, revert-checked: reads `specs/memory/product/catalog.json` and every `evals/tasks/*/task.toml`; the folders whose `[task] round` is `usage` equal, as a set of literals, the slugs whose `area` is not `quality`; the failure message names the missing and the extra slug. The reviewer deletes a folder and sees it red |
| J8.T2 | jr | AC18.1 | `evals/README.md` | text only: describe the gate. Replace `:3,9,11,19` (the "non-blocking" workflow, the per-leg JSON, the last-line `check_output`) from the final diff: the three rounds, the three layers, `gate.py` and its 2-of-3 and no-regression rule, the ceilings and `--calibrate`, the canary, the self-check job (CI only), the result layout of PLAN D4, `--leg`. No other file |

Done when: `verify:`; `tests/integrations/test_eval_tasks.py` passes.
