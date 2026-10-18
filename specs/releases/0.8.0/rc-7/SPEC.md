# SPEC — Release: 0.8.0, candidate 7 (final maintenance)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-18
**Origin:** operator-demand

- The operator's handoff named these remaining rand-engine items: the CLI
  `exists()` then write race, a missing `poetry-core` lower bound, the unpinned
  Poetry installer, and the set-based reference-duplicate check. It also named
  the intended exclusive `xb` creation for the CLI.
- The later operator demand is to adapt only rand-engine and its child worktrees,
  leave dadaia-workspace unchanged, complete all open rand-engine work and finish
  with no active backlog, release or release candidate.
- Read-only inspection found the four items still present at the rc-6 head. It
  found the old runpy warning and duplicate-import observations no longer
  reproducible, and the three Faker declarations intentional for their separate
  packaging roles. Those observations create no work here.

## Bug window review

Rc-6 resolved no bug-ledger record. This candidate does include one confirmed
bug that has not yet been registered: a creator can place the target after the
CLI's `exists()` check and `write_bytes()` then overwrites it. The product-memory
contract says an existing target is left unchanged with exit 1. A temporary-path
reproduction on `6f87fa5` returned exit 0 and
`competitor_preserved=False`. Before its RED test or source change, the product
engineer registers `get-started-race-overwrites-existing-target`; the fix closes
that same record.

The relevant persisted fixes were inspected:

- `get-started-scaffold-shadows-package` (`16e8fc1`) is **KEEP**. The
  `<slug>-example.py` name and all five runnable scaffolds remain unchanged. The
  original `J6.T2` target-creation seam now carries a second bug, so the as-is
  review must REBUILD only that seam as one exclusive-create path, retaining its
  tests and messages.
- `reference-test-self-referential` (`adc66be`) is **KEEP**. The expected objects
  still come from `rand_engine.__all__`; only the lossy set comparison is
  tightened so multiplicity is checked too.
- `workflow-actions-mutable-refs` (`948bfe8`) and
  `workflow-missing-top-level-permissions` (`b150df5`) are **KEEP**. Action
  references, permission blocks and privilege widening remain unchanged while
  the Poetry bootstrap command is replaced.

No prior fix is deleted, loosened or given a second implementation path.

## 1. Problem

Four bounded maintenance gaps remain before the release can be promoted.

First, `rand-engine get-started` checks whether its target exists and later writes
it with ordinary truncating semantics. A competing creator between those calls
is overwritten even though the command promises never to overwrite an existing
target.

Second, `[build-system]` names bare `poetry-core` even though the published wheel
must preserve the static PEP 621 metadata and `License-Expression: MIT`. An
isolated exact-version build proved that `poetry-core` 2.0.0 through 2.1.3 emit
legacy `License: MIT`; 2.2.0 is the first tested version that emits Metadata 2.4
with `License-Expression: MIT`.

Third, fourteen installation sites in seven GitHub Actions workflows execute an
unpinned remote Poetry bootstrap script and then add its user-script directory to
`PATH`. The release CI has already run successfully with Poetry 2.5.1, whose
Python range includes every tested 3.10–3.13 interpreter.

Finally, the main-reference contract derives expected objects from
`rand_engine.__all__` but compares directive names as sets. Missing or extra
distinct names fail, while a repeated directive is silently accepted.

## 2. Measurable goals

- The CLI creates a scaffold through one exclusive file-creation operation. A
  target introduced at the former check/write boundary is preserved byte for
  byte, produces the existing error text on stderr and exits 1.
- The build backend declares `poetry-core>=2.2.0`; an exact-floor package build
  retains the static project metadata, console entry point and
  `License-Expression: MIT`.
- Every current workflow Poetry installation uses exactly Poetry 2.5.1 through
  the Python selected by the workflow. No remote installer pipe or installer-only
  `PATH` workaround remains.
- The reference test checks one canonical directive per public export without
  imposing a documentation-order contract; deleting, changing or duplicating a
  directive fails it.
- One maintenance job carries the four items and pays one independent review and
  one unchanged repository `verify:` gate.

**Wave ranking:** one maintenance wave, ordered by product-contract risk: the CLI
bug, build and CI reproducibility, then reference-gate hardening. Their production
and test write sets are disjoint; only bug registration precedes the CLI RED test,
and bug resolution follows the reviewed fix.

## 3. Non-goals

- Any change to dadaia-workspace, its evolved worktree behavior, hooks, skills,
  projected law or another repository.
- New CLI commands, slugs, filenames, messages, exit codes, public imports,
  runtime dependencies, supported Python/Spark versions or generated scaffold
  bytes.
- A new CI workflow, action, matrix leg, test command, threshold, permission, gate,
  publishing relationship, caching policy, plugin or `pipx` layer.
- A workflow-source mirror test, documentation-order requirement, new docs-test
  home or removal, skip, weakening or unrelated rewrite of an existing assertion.
- Changes to `poetry.lock`, the intentional Faker declarations, the currently
  passing runpy test, duplicate local imports that do not exist, or historical
  dadaia governance observations.
- Outreach execution or disposition. It remains separate post-stable work and is
  not relabelled as maintenance delivery.

## 4. Requirements

### FR1 — Preserve a competing CLI target

- AC1.1 (unit): a new race-partition case in `tests/test_9_cli.py` injects a
  competing file after the former absence decision but before output creation.
  `get-started` exits 1, leaves the competitor's literal bytes unchanged, prints
  nothing on stdout and emits the same
  `error: <target> already exists, not overwriting` stderr contract.
- AC1.2 (unit): target creation in `rand_engine/cli.py` uses one exclusive binary
  create-and-write path. `FileExistsError` maps to the existing exit-1 behavior;
  unrelated I/O errors retain their existing propagation behavior. No preliminary
  target-existence decision or fallback write path remains.
- AC1.3 (unit): the existing pre-existing-target, missing-directory, exact-byte,
  five-slug, console-script and `python -m rand_engine` tests remain unchanged and
  pass.
- AC1.4 (integration): before AC1.1 or AC1.2 is implemented, the confirmed bug is
  registered with its documented contract and reproduction. The resolution names
  `J6.T2` as the introducing task, records RED/GREEN evidence and closes the record
  without rewriting its immutable fields.

### FR2 — Declare the metadata-preserving build floor

- AC2.1 (integration): `[build-system].requires` is exactly
  `poetry-core>=2.2.0` and keeps `poetry.core.masonry.api` as its backend. No
  runtime, optional or test dependency changes.
- AC2.2 (integration): a PEP 517 wheel build using exactly `poetry-core==2.2.0`
  succeeds and its metadata retains package name `rand-engine`, version `0.8.0`,
  `Requires-Python: >=3.10`, `License-Expression: MIT` and the `rand-engine`
  console entry point. The normal Poetry 2.5.1 check and package build also pass.
- AC2.3 (no new test): the exact-floor build is direct package evidence and the
  existing wheel/public-API contracts cover its installed result; no source-text
  or duplicate packaging test is added.

### FR3 — Pin Poetry installation in every workflow

- AC3.1 (integration): all fourteen current installation sites in
  `.github/workflows/auto_tag_publish_development.yml`,
  `auto_tag_publish_master.yml`, `benchmarks.yml`, `docs.yml`,
  `pr_to_development.yml`, `pr_to_master.yml` and `test_on_push.yml` install
  exactly `poetry==2.5.1` with `python -m pip` after `actions/setup-python`.
- AC3.2 (integration): the seven workflows contain no
  `install.python-poetry.org` invocation and no `GITHUB_PATH`, `$HOME/.local/bin`
  or `%APPDATA%` mutation that existed only to expose that installer. Existing OS
  conditions and shells remain valid.
- AC3.3 (E2E): triggers, matrices, setup actions, permissions, caches, Poetry
  commands, test commands, thresholds, summaries, artifacts, job dependencies,
  releases and publishing steps remain unchanged; the existing GitHub checks run
  successfully and report Poetry 2.5.1.

### FR4 — Make the public-reference comparison multiplicity-safe

- AC4.1 (unit): the existing assertion in `tests/test_docs.py` compares the live
  directive list with the defining paths derived from `rand_engine.__all__` using
  multiplicity-preserving, order-insensitive values.
- AC4.2 (unit): adding a duplicate valid `:::` directive makes the existing test
  fail; restoring the page makes it pass. Deletion and wrong-target failures from
  `reference-test-self-referential` remain covered.
- AC4.3 (unit): the same test retains its live `__all__` authority and public
  docstring assertion. No new test or required directive order is introduced.

### FR5 — Reconcile and record the maintenance result

- AC5.1 (integration): the 0.8.0 changelog records the atomic CLI no-overwrite fix
  and the reproducible build-tool floor and pin without claiming a new product
  feature.
- AC5.2 (integration): closure updates `ARCHITECTURE.md` Tech Stack to the exact
  `poetry-core>=2.2.0` backend floor and Poetry 2.5.1 CI tool, as constitution
  invariant 11 requires. It reviews `get-started-cli`, `public-api`,
  `documentation` and `QUALITY.md` against the final diff, regenerates the memory
  catalog/index and refreshes only derived markers whose source truth changed.
- AC5.3 (integration): the bug, backlog, release and memory ledgers validate; the
  registered CLI bug is resolved; the unchanged repository `verify:` gate passes;
  no maintenance-created backlog item or open bug remains.

## 5. Replaces

- The separate target-existence check plus truncating write is replaced by one
  exclusive target creation operation.
- The unbounded build-backend declaration is replaced by the first verified floor
  that preserves the release's license-expression metadata.
- Fourteen unpinned remote Poetry bootstraps and their path workarounds are
  replaced by exact Poetry 2.5.1 installation through the selected Python.
- Set equality in the main-reference directive assertion is replaced by an
  order-insensitive comparison that preserves multiplicity.
- No public name, output shape, release gate or supported platform is replaced.

## 6. Constraints and risks

- One job owns the complete source write set: `specs/bugs/BUGS.jsonl`,
  `tests/test_9_cli.py`, `rand_engine/cli.py`, `pyproject.toml`, the seven named
  workflow files and `tests/test_docs.py`. Registration, RED, implementation and
  resolution are separate commits/tasks where the bug flow requires them.
- Closure owns `CHANGELOG.md`, `specs/memory/ARCHITECTURE.md`, the reviewed memory
  atoms/canonical quality file, generated catalog/index, any actually affected
  derived markers and `specs/releases/0.8.0/_RELEASE.json`; the PLAN must declare
  the exact final set rather than assuming release-ledger-only reconciliation.
- The exclusive create must not introduce a temporary file, retry, second write
  path or broad exception catch. The installer replacement must not change a
  workflow's execution graph or dependency environment beyond pinning Poetry.
- Package-build artifacts, caches and virtual environments stay outside the repo.
  Existing repo-local cache prohibitions and the complete test gate remain in
  force.

## 7. Open questions

None. The operator already named the four maintenance items and the CLI remedy;
the isolated build evidence resolved the backend floor, and the existing
successful CI run resolved the Poetry version.
