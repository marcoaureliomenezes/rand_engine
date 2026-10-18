# Job 10 — FR6 the Agent Skill

**Wave:** 5 · **Waits on:** Job 6, Job 8

- `skills/rand-engine/SKILL.md` stays outside the wheel (AC3.2 test of Job 4 plus AC6.2). Its `python` blocks run through the same fence extractor as the docs, so it cannot drift from `METHOD_CATALOG` (the authority for RandSpec method grammar).
- Evidence before merge: no site build in `verify:`; the task states a strict build in a scratch copy outside the repo tree (`cp -r <tree> $SCRATCH/site-check && cd $SCRATCH/site-check && cp README.md docs/index.md && zensical build --strict`), exit 0 handed to the reviewer; `docs.yml` repeats it on push to `feature/**`.
- The README and site links to it are asserted in Job 11.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J10.T1 | sr | AC6.1 | `tests/test_docs.py` | RED: SKILL.md front matter has `name: rand-engine` and `description`; its python blocks execute in order under the AC5.4 contract. Owner: tests/test_docs.py |
| J10.T2 | sr | AC6.1 | `skills/rand-engine/SKILL.md`, `tests/test_docs.py` | skill: RandSpec grammar, choosing a method, `pk`/`fk`, sinks, `rand-engine get-started`; blocks synthetic and <= 10^4 rows. Owner: tests/test_docs.py |
