# SPEC — Release: 0.8.0, candidate 5 (platform integration)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-18
**Origin:** operator-demand

- Operator demand: adapt only rand-engine and its child worktrees to the evolved
  dadaia-workspace, finish every open rand-engine release candidate and leave no
  active release or backlog item; do not change dadaia-workspace.
- PR #47 supplied the RED evidence after rc-4 had closed: the macOS matrix ran
  Spark 3.5.8 with the runner's Java 21 and failed its Arrow Python exchange, while
  Windows Python 3.12 and 3.13 retained two SQLite fixture connections across the
  writer's atomic replace.
- Inspection resolved both choices without a new product decision: the already
  supported Java 17 runtime passes the full local suite, and the SQLite tests need
  to close their setup connection after committing and before invoking the writer.

## Bug window review

Rc-4 introduced no bug-ledger resolution. `BUGS.jsonl` reports zero open records,
and no new persisted `fix_sha` exists after the fixes already judged by rc-4. The
failed PR checks expose integration-environment and test-fixture lifetime defects,
not a new product behavior or a change to a registered bug fix. There is therefore
no fix to classify KEEP or REBUILD in this candidate.

## 1. Problem

The rc-4 implementation passes the complete repository gate on the supported
Java 17 runtime, but the GitHub-hosted macOS runner currently supplies Java 21.
Spark 3.5.8 then raises `UnsupportedOperationException` in Arrow's
`mapInPandas` exchange, failing five Spark key tests before their product
assertions run.

On Windows Python 3.12 and 3.13, two SQLite tests commit fixture setup through a
connection transaction context but retain the connection handle. Windows keeps
the database file locked, so the output sink cannot atomically replace it. The
same tests pass on platforms that permit replacement of an open file.

These failures prevent the already approved product from passing its declared
platform matrix. They require no production-code, public-API, dependency, matrix,
gate or release-policy change.

## 2. Measurable goals

- Every full-suite GitHub Actions workflow selects Temurin Java 17 before running
  its existing tests, and keeps its current OS/Python matrix and test command.
- The two affected SQLite tests finish and close fixture setup connections before
  the writer performs its atomic replacement, while retaining every current
  assertion and test case.
- The unchanged complete suite passes on the declared GitHub Actions matrix,
  including Spark on macOS and SQLite on Windows Python 3.12 and 3.13.

**Wave ranking:** one platform-restoration wave. The workflow runtime and the two
test fixtures are independent edits in one job because their only shared outcome
is restoring the existing candidate gate; no product behavior follows from
either change.

## 3. Non-goals

- Any change to `rand_engine/**`, public behavior, RandSpec grammar, SQLite writer
  semantics, Spark key semantics, dependencies, supported Python/Spark matrix,
  benchmark code or documentation.
- Supporting Spark 3.5.8 on Java 21, changing the developer machine's default JVM,
  adding a fallback path, skipping a test or narrowing an assertion.
- Adding a test case, gate, workflow, matrix leg, release, backlog item or bug
  record; changing dadaia-workspace, its hooks or its worktree model.
- Reworking unrelated workflow jobs or SQLite test helpers.

## 4. Requirements

### FR1 — Select the supported JVM in full-suite workflows

- AC1.1 (integration): the full-suite jobs in exactly
  `.github/workflows/test_on_push.yml`,
  `.github/workflows/pr_to_development.yml`,
  `.github/workflows/pr_to_master.yml`,
  `.github/workflows/auto_tag_publish_development.yml` and
  `.github/workflows/auto_tag_publish_master.yml` select Temurin Java 17 before
  dependency installation and test execution. The Java setup action is pinned to
  an immutable commit, following the existing workflow security convention.
- AC1.2 (integration): every existing OS/Python matrix entry, pytest command,
  coverage threshold, trigger, permission, publishing step and job relationship
  in those workflows remains unchanged.
- AC1.3 (E2E): the existing full-suite checks pass on their declared runners; in
  particular, the five rc-4 Spark Arrow tests reach and pass their product
  assertions on macOS rather than failing in the Java 21 Arrow runtime.

### FR2 — End SQLite fixture ownership before atomic replacement

- AC2.1 (unit): in
  `tests/test_5_files_write_batch.py`, the fixture setup of
  `test_sqlite_quotes_hostile_names_binds_values_and_round_trips_supported_types`
  and
  `test_sqlite_overwrite_replaces_only_selected_table_and_preserves_unrelated_tables`
  uses a closing resource context around a transaction context. Each transaction
  commits and each connection closes before the tested writer is called.
- AC2.2 (unit): both tests keep their existing setup rows, writer calls and
  assertions byte-for-byte; no assertion, parametrization or test case is removed,
  skipped, weakened or added.
- AC2.3 (E2E): the existing tests pass on Windows Python 3.12 and 3.13 and continue
  to prove hostile identifier quoting, value binding and supported-type
  round-trips as well as selected-table replacement and unrelated-table
  preservation.

## 5. Replaces

- Implicit use of each hosted runner's JVM in the five workflows is replaced by
  explicit Temurin Java 17 selection for full-suite jobs.
- Transaction-context-only setup in the two named SQLite tests is replaced by a
  transaction nested inside an explicit connection-closing lifetime.
- No product behavior is replaced.

## 6. Constraints and risks

- The candidate may touch only the five named workflow files, the one named test
  file and its own release-definition artifacts.
- Existing CI failures are the RED proof. No duplicate test or extra verification
  gate is created.
- Workflow YAML indentation and placement must make Java 17 effective in each
  full-suite job without affecting build-only, security, benchmark or deploy jobs.
- The repository `verify:` command and all existing merge checks remain exactly as
  configured.

## 7. Open questions

None. Repository and CI inspection resolved the runtime and resource-lifetime
choices; the concrete SPEC and PLAN still require the operator's approval before
the candidate enters `IMPLEMENTATION`.
