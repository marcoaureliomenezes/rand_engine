# Job 1 — the direction rulings in the constitution (wave 1)

Law text, no code. The SPEC (AC6.1) holds the section verbatim.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | pe | AC6.1, AC6.2 | `specs/constitution.md` | insert the `## Direction` section of AC6.1 verbatim between `## Purpose` and `## Invariants`; no other line changes; `QUALITY.md` and `ARCHITECTURE.md` `## Principles` gain nothing; no test (law text); commit `docs(specs): …` or `feat(specs): …` per `dd-gitflow-default` §3a; `dadaia doctor` stays clean |

Done when: `git diff` of the task shows only the inserted section; the repo `verify:` line passes.
