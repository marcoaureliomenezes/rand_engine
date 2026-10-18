# PLAN — Release: 0.8.0, candidate 7 (final maintenance)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-sw-engineer-sr
**SPEC:** `specs/releases/0.8.0/rc-7/SPEC.md`

## 1. As-is review

Evidence is the pre-SPEC review
`2026-10-18T014824Z-dd-sw-engineer-sr-known-maintenance-as-is.handoff.json`
at `9104df1`. The four named maintenance items are one bounded job. The CLI
contract break is Arm B: the operator named it and its reproduction establishes
that a competing creator is overwritten. The other three items are Arm A
maintenance. No workspace or other-repository unit is a candidate for change.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `rand_engine/cli.py` `main` target creation | checks `target.exists()` and later calls truncating `write_bytes()` | new `get-started-race-overwrites-existing-target`, caused by `J6.T2`; prior filename fix `get-started-scaffold-shadows-package` | REBUILD | this one seam now carries two fixes and contradicts the no-overwrite contract under a concurrent creator. Rebuild only target creation as one exclusive open; retain slugs, names, data bytes, output and errors. |
| `tests/test_9_cli.py` get-started tests | proves a target existing before invocation is retained, but has no check/write-boundary partition | `get-started-scaffold-shadows-package` coverage retained | UPDATE | the existing CLI contract home needs one real-I/O race partition; all current partitions stay. |
| `pyproject.toml` `[build-system]` | names unbounded `poetry-core` although the current static metadata needs the measured PEP 639-capable floor | 0 open | UPDATE | `poetry-core>=2.2.0` is the first isolated floor that preserves `License-Expression: MIT`; backend and dependency policy remain intact. |
| seven `.github/workflows/*.yml` Poetry setup steps | fourteen sites pipe a mutable remote installer and add its installer path | 0 open; action pins and permission fixes remain | UPDATE | each existing selected-Python setup is its workflow's owner; replacing just the bootstrap with exact `python -m pip install poetry==2.5.1` makes the tool reproducible without changing CI topology. |
| `tests/test_docs.py` `test_reference_directive_names_the_canonical_documented_object` | derives from `__all__`, then compares directive names as sets | `reference-test-self-referential` (`adc66be`) KEEP | UPDATE | its single existing assertion loses multiplicity. Sorted lists preserve the live `__all__` authority while remaining insensitive to page order. |
| `specs/bugs/BUGS.jsonl` | has no record for the reproduced CLI break | new Arm B record | UPDATE | the ledger is the exclusive registration and terminal-resolution authority; registration and resolution are parent-`wt-main` metadata exceptions, never source writes. |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| whether a scaffold target can be created | `rand_engine/cli.py` `main` through one `Path.open("xb")` | packaged case bytes and `tests/test_9_cli.py` output contracts | preliminary `Path.exists()` decision and truncating `write_bytes()` creation |
| lowest backend version that preserves published license metadata | `pyproject.toml` `[build-system].requires` | isolated `poetry-core` floor evidence and PEP 639 support evidence | bare `poetry-core` requirement |
| Poetry executable used by each current CI job | the existing installer step in each of the seven named workflows | selected `actions/setup-python`, lock generator and CI run 39081652038 | remote installer pipes and installer-only path mutations |
| documented-object multiset | `test_reference_directive_names_the_canonical_documented_object` derived from live `rand_engine.__all__` | `docs/reference.md` directives and existing public-docstring check | lossy `set` comparison |
| lifecycle of the race bug | `bugs.py` over `specs/bugs/BUGS.jsonl` | reproduction, RED/GREEN evidence and the reviewed task fix | no alternate issue record or manual ledger edit |

## 2. Decisions and measured gate cost

- Job 1 is the sole maintenance job. It has one reviewer verdict and one unchanged
  repository `verify:` gate; no workflow, test command, matrix, dependency or
  runtime gate is added. The existing GitHub matrix and package workflow remain
  the cross-platform and PEP 517 evidence.
- The CLI RED case wraps only the target's real `Path.open` write attempt. On its
  first `"wb"` or `"xb"` call it creates the competing file with real I/O and then
  delegates to the original open. It patches neither `exists()` nor an outcome:
  old `write_bytes()` truncates the competitor, while the exclusive replacement
  raises `FileExistsError` at the same stable boundary.
- Metadata and workflow edits are a single bounded task because their shared
  build-tool authority is declared by the same project and all fourteen existing
  installer sites must change together. The docs assertion remains its own task.
- The bug's registration and resolution deliberately write the same ledger in
  serial parent-`wt-main` tasks under the explicit bug-flow exception. They do
  not open a source task tree or overlap production writes.

## DAG

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `specs/bugs/BUGS.jsonl`, `tests/test_9_cli.py`, `rand_engine/cli.py`, `pyproject.toml`, `.github/workflows/auto_tag_publish_development.yml`, `.github/workflows/auto_tag_publish_master.yml`, `.github/workflows/benchmarks.yml`, `.github/workflows/docs.yml`, `.github/workflows/pr_to_development.yml`, `.github/workflows/pr_to_master.yml`, `.github/workflows/test_on_push.yml`, `tests/test_docs.py` |

## 3. Reconciliation (after Job 1)

**W:** `CHANGELOG.md`, `specs/memory/ARCHITECTURE.md`, `specs/memory/QUALITY.md`, `specs/memory/product/onboarding/get-started-cli.md`, `specs/memory/product/api/public-api.md`, `specs/memory/product/onboarding/documentation.md`, `specs/memory/product/catalog.json`, `specs/memory/product/index.md`, `llms.txt`, `specs/releases/0.8.0/_RELEASE.json`, `specs/bugs/BUGS.jsonl`, `specs/bugs/_archive/bugs_histo.jsonl`.

The product engineer records the `Fixed` changelog entries for the atomic
no-overwrite repair and reproducible build tooling; updates the Architecture
Tech Stack with the exact `poetry-core>=2.2.0` floor and Poetry 2.5.1 CI tool;
and reviews the named onboarding/public API/documentation atoms and QUALITY
against the final code. It regenerates the catalog and index and refreshes only
the exact derived `llms.txt` marker(s) whose reviewed source hash changed. It
resolves then archives the named CLI bug through its verbs and appends closure
state through `release.py`; it does not use wildcards or modify unrelated docs.
