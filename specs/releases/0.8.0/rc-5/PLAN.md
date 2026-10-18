# PLAN — Release: 0.8.0, candidate 5 (platform integration)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-sw-engineer-sr
**SPEC:** `specs/releases/0.8.0/rc-5/SPEC.md`

## 1. As-is review

Evidence is the pre-SPEC review
`2026-10-18T001427Z-dd-sw-engineer-sr-rc5-platform-as-is.handoff.json` and
the corrected fixture identification recorded by the product engineer. The bug
ledger has no open record; this candidate restores the declared CI environment
and closes two test-owned setup resources without changing a product contract.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `.github/workflows/{test_on_push,pr_to_development,pr_to_master,auto_tag_publish_development,auto_tag_publish_master}.yml` full-suite `test` jobs | select Python but inherit the hosted runner JVM; `test_on_push.yml` also re-echoes the Windows ambient `JAVA_HOME` after dependency installation | 0 open; PR #47 macOS Spark failure is CI integration evidence | UPDATE | the five existing full-suite jobs are the sole owners of their test runtime. Pinning Temurin 17 there restores the supported Spark 3.5.8 runtime without changing a matrix, command, trigger, gate or publishing job. |
| `tests/test_5_files_write_batch.py` SQLite overwrite fixtures | each named fixture uses a transaction context that commits but leaves the connection object alive through the writer call | 0 open; PR #47 Windows Python 3.12–3.13 failure is fixture-lifetime evidence | UPDATE | this is the existing owner of SQLite overwrite contracts. A closing context around the transaction releases the platform file handle while retaining every existing setup row, call and assertion. |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| JVM used by each full-suite CI job | the `test` job steps in each of the five named workflow files | Spark 3.5.8 compatibility evidence and existing workflow action-pinning convention | ambient hosted-runner JVM selection; the Windows no-op `JAVA_HOME` echo in `test_on_push.yml` |
| lifetime of SQLite setup connections in the named tests | the two setup blocks in `tests/test_5_files_write_batch.py` | Python `sqlite3` context-manager semantics and existing writer assertions | transaction-context-only fixture lifetime |

## 2. Decisions and measured gate cost

- Existing failing CI checks are the RED evidence. The candidate adds no test case,
  assertion, skip, xfail, workflow, matrix leg, dependency, test command or gate.
- Both tasks have disjoint exact write sets and may be implemented in parallel.
  The job merge runs the unchanged repository `verify:` once; the existing GitHub
  full-suite matrix supplies the cross-platform E2E evidence. No task repeats it.
- Java setup is inserted in each existing `test` job after checkout/Python setup
  and before dependency installation and test execution. It uses exactly
  `actions/setup-java@cf277c60eb25467037889841efdb72551f06f6c3` (`v4`),
  `distribution: temurin`, and `java-version: '17'`.

## DAG

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `tests/test_5_files_write_batch.py`, `.github/workflows/test_on_push.yml`, `.github/workflows/pr_to_development.yml`, `.github/workflows/pr_to_master.yml`, `.github/workflows/auto_tag_publish_development.yml`, `.github/workflows/auto_tag_publish_master.yml` |

## 3. Reconciliation (after Job 1)

**W:** `specs/releases/0.8.0/_RELEASE.json`.

The product engineer performs the standard closure record after the reviewed job
lands: record the candidate's integration evidence and closure summary through
the release ledger's verbs. No memory, backlog, bug ledger or documentation
claim changes because the runtime selection and fixture ownership do not alter a
released product contract.
