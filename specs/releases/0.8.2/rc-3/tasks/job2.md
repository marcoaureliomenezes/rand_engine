# Job 2 — `evals/gate.py`: 2 of 3, no regression, calibration (wave 1)

Runs beside Job 1 (disjoint `W:`). The trial JSON keys are PLAN D2 and D4, the canary rule D9, calibration D10; the test's fixtures are literal JSON, so neither job waits on the other.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | sr | AC14.2, AC15.1, AC15.2, AC15.3, AC11.3 | `tests/integrations/test_eval_gate.py` | RED: loads `gate.py` by path; fixture task folders and trial JSONs in `tmp_path`, k = 3; one case per partition, each exit code and message a literal. Exit 0: all green. Non-zero naming the cause: usage 1 of 3 on the wheel; wheel 2 of 3 against PyPI 3 of 3; a red canary (the sandbox message, text distinct from the others); a usage harness error; a missing file; a usage task without a ceiling. Exit 0: a failed or errored discovery trial with everything else green. `--calibrate`: `ceilings.json` equals `ceil(2 × median)` of input plus output tokens over the passing usage trials of both legs; the table lists task, wheel and PyPI passes, tokens, cost, layer, surface. The 2-of-3 and no-regression assertions are the diff a weakening PR shows. Red today: `gate.py` does not exist |
| J2.T2 | jr | AC14.2, AC15.1, AC15.2, AC15.3, AC11.3 | `evals/gate.py` | stdlib-only decider per PLAN D9, D10: expected set from `task.toml` `[task]` and `--k`; canary probes unioned from the leg's `probe:` lines; discovery exempt; table to stdout for the job summary; `--calibrate` as D10. Owner test: `tests/integrations/test_eval_gate.py` |

Done when: `verify:`; `tests/integrations/test_eval_gate.py` passes.
