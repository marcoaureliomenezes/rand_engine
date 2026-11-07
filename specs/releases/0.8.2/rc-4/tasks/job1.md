# Job 1 — the `verify:` line: measure, delete the dead copies, change only on the ruling (wave 1)

Runs beside Jobs 2, 3 and 4 (disjoint `W:`). T2 and T3 both write `AGENTS.md`: T2 first. T3 opens only after the operator rules on T1's numbers; without a ruling it is cancelled with that reason and `verify:` stays.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC19.1 | `.dadaia/reports/rand-engine/` | measure 3 cold and 3 warm wall-clock runs of the current `verify:` line (`AGENTS.md:51`) and of a shared-environment line (one virtualenv not keyed by the worktree path, under `.dadaia/tmp/poetry-cache`). Cold = no environment exists; warm = it exists. Each run: start and end from one clock (`date +%s.%N`), exit code, the command, the machine load read just before. The report names the pandas and pyspark pairing the shared environment pins against the CI legs (local pandas 2.2.3 / pyspark 3.5.8; CI pandas 3.1.0 / pyspark 4.3.0, each read from its lock or run log with the source cited) and the disk each line leaves behind. No repo file is written; the numbers go to the operator for the ruling |
| J1.T2 | jr | AC19.4 | `AGENTS.md` | delete the `verify-stage:` and `verify-task:` lines (`:52-53`). Nothing reads them (`_worktree_end.py:216-221` reads `verify:` only); commit `chore(J1.T2): …`. Sweep: `git grep -n -e verify-stage -e verify-task -- . ':!specs'` prints nothing |
| J1.T3 | jr | AC19.2, AC19.3 | `AGENTS.md` | after the ruling only: replace `AGENTS.md:51` with the line the operator ruled, no heavier than today's, cold against cold and warm against warm. Read back (AC19.3): `verify:` run in a second worktree creates no new virtualenv (the listing of the poetry cache before and after, in the hand-back). Owner: none (no test) |

Done when: `verify:` runs the changed line green in one tree; `release.py check` exits 0. The commit body of J1.T3 quotes the ruling and J1.T1's report path.
