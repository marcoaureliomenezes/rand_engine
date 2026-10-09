# Job 8 — final public surfaces and performance evidence

**Status:** Approved

Job 8 is a normal implementation job after Jobs 4 and 5 and the zero-open bug batch. Before it opens, the main thread verifies the merged feature, publishes that exact production-source SHA from `feature/0.7.0`, and retains the real CI run artifacts. Job 8 moves the still-unopened executable-documentation, public-boundary and terminal-performance evidence out of reconciliation. New RED assertions are recorded in separate test-only commits and are not hidden under strict xfail markers.

| task | AC | `W:` | outcome |
|---|---|---|---|
| J8.T1 | AC9.2, AC9.4 | `tests/test_docs.py` `tests/integrations/test_public_api.py` | Executable docs and public-boundary RED; owner `tests/test_docs.py`. Assertion-first RED exercises approved spellings/defaults, kwargs migration, batching and helper examples at light sizes. Preserve passing public controls for unsupported Spark refusal and the unchanged import/dependency boundary. No strict xfail. |
| J8.T2 | AC9.2, AC9.4 | `README.md` `llms.txt` `docs/1_DATA_GENERATOR.md` `docs/2_SPARK_GENERATOR.md` `docs/3_WRITING_FILES.md` `docs/5_RECIPES.md` `CHANGELOG.md` | Rebuild executable docs and migration surfaces; owner `tests/test_docs.py`. Source/documentation-only implementation uses synthetic data and current public names; both J8.T1 files must be green. |
| J8.T3 | AC2.4, AC4.4 | `tests/test_benchmarks.py` | Terminal benchmark artifact RED; owner `tests/test_benchmarks.py`. Assertion-first RED, without xfail, requires the artifact to name the final feature/base commits and retain the distribution 1.5x and modifier 1.25x thresholds. |
| J8.T4 | AC2.4, AC4.4 | `docs/benchmarks.json` `docs/BENCHMARKS.md` | Record terminal performance proof; owner `tests/test_benchmarks.py`. Consume the authorized CI artifact with exact run, base and measured production-source SHA. Prove later Job 8 commits contain no measured production/benchmark-code diff; do not claim the artifact measured its own later evidence commit. A failed threshold reopens its owning implementation; it never edits the threshold. |
| J8.T5 | AC2.4, AC4.4, AC9.2, AC9.4 | `specs/releases/0.7.0/rc-2/tasks/job8-final-surfaces.md` | Close final-surfaces job; owner `tests/test_docs.py`. After both owner suites and final package/build checks are green, write terminal `done` exactly once. |

Ordering: after Jobs 4/5 merge and the bug batch reaches zero open records, publish only the verified feature's exact production-source SHA and retain its CI artifacts; then open Job 8 and run J8.T1 → J8.T2 and J8.T3 → J8.T4, followed by J8.T5. No Job 8 or task-worktree branch is pushed. Job 6 opens after Job 8 is merged.
