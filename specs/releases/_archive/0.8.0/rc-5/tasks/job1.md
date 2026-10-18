# Job 1 — Restore supported platform integration

**Wave:** 1
**Waits on:** —
**W:** `tests/test_5_files_write_batch.py`, `.github/workflows/test_on_push.yml`, `.github/workflows/pr_to_development.yml`, `.github/workflows/pr_to_master.yml`, `.github/workflows/auto_tag_publish_development.yml`, `.github/workflows/auto_tag_publish_master.yml`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC2.1–AC2.3 | `tests/test_5_files_write_batch.py` | In the two named SQLite setup blocks only, nest the existing transaction context inside an explicit closing connection context. Keep all setup rows, writer calls, assertions, parametrization, cases and skips byte-for-byte. The existing Windows failure is the RED evidence; the unchanged existing tests are the GREEN evidence. |
| J1.T2 | jr | AC1.1–AC1.3 | `.github/workflows/test_on_push.yml`, `.github/workflows/pr_to_development.yml`, `.github/workflows/pr_to_master.yml`, `.github/workflows/auto_tag_publish_development.yml`, `.github/workflows/auto_tag_publish_master.yml` | In each existing full-suite `test` job, add the pinned Temurin Java 17 setup before dependency installation and tests: `actions/setup-java@cf277c60eb25467037889841efdb72551f06f6c3` (`v4`), `distribution: temurin`, `java-version: '17'`. Remove only the Windows ambient-`JAVA_HOME` echo block from `test_on_push.yml`; retain every matrix, command, trigger, permission, job relation and non-test job unchanged. |

The two tasks share no file and can run in parallel. The unchanged job merge
`verify:` and the existing CI matrix provide the required complete-suite and
cross-platform evidence.
