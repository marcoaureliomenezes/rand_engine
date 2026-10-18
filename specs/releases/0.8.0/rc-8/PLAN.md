# PLAN — Release: 0.8.0, candidate 8 (sustainable adoption for humans and agents)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-sw-engineer-sr
**SPEC:** `specs/releases/0.8.0/rc-8/SPEC.md`

## 1. As-is review

Evidence is the pre-SPEC review
`2026-10-18T035517Z-dd-sw-engineer-sr-adoption-sustainable-as-is.handoff.json`
and the operator grill named in the SPEC. This is Arm A: it adds an opt-in
onboarding path and truthful documentation routes. No open bug, workspace
feature, workflow, dependency, benchmark, or public generation behavior is in
scope. The existing `stream_dict` performance failure remains a separate
release-level gate.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `rand_engine/cli.py` `CASES` and `main` | one dictionary supplies five descriptions, while resource and `<slug>-example.py` names are derived in separate expressions | two retained target-creation fixes: `get-started-scaffold-shadows-package`, `get-started-race-overwrites-existing-target` | REBUILD | a sixth Markdown starter needs resource, target and kind to agree; one small descriptor is the only authority and retains one `xb` writer. |
| `rand_engine/cases/` | five packaged Python resources, each an executable Databricks-format source | 0 open | ADD | the portable project-use context has no source home; one Markdown resource is needed and is not executable. |
| `tests/test_9_cli.py` and `tests/integrations/test_public_api.py` | assert five Python starters, their output names and wheel bytes | target-creation coverage retained | UPDATE | the CLI contract home must prove the Agent partition and the wheel must prove its declared resource without weakening five-starter assertions. |
| `tests/test_docs.py` | derives tutorials, case links and landing references from the five-slug CLI mapping | 0 open | UPDATE | it currently treats every case as a Python tutorial; it must derive five runnable starters and one agent resource from the same descriptor, without prose snapshots. |
| `docs/`, `README.md`, `llms.txt`, `skills/rand-engine/SKILL.md`, `mkdocs.yml` | accurate tutorials and skill exist, but compatibility facts are scattered and no portable starter, contribution, support or security authorities exist | 0 open | UPDATE | one canonical compatibility path and linked trust routes improve adoption using the existing rendered-docs system. |
| `CONTRIBUTING.md` and `SECURITY.md` | absent | 0 open | ADD | repository-relative contribution, support and verified private-reporting guidance have no canonical file. |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| each starter's description, resource, target and kind | `rand_engine/cli.py` one Case descriptor | CLI parser, packaged resources, tests and docs inventories | separate description map, derived uniform `.py.txt` resource and uniform `-example.py` target assumptions |
| whether scaffold creation overwrites a target | `rand_engine/cli.py` `main` through one `Path.open("xb")` | `tests/test_9_cli.py` output contracts | none; the exclusive writer remains the prior fix |
| which starters are runnable tutorials | descriptor kind in `rand_engine/cli.py` | `docs/getting-started.md`, `tests/test_docs.py` | the assumption that every CLI slug maps to a Python tutorial |
| compatibility and migration guidance | `docs/compatibility.md` | `pyproject.toml`, Spark guide, test/workflow facts and CHANGELOG | scattered, non-canonical compatibility directions |
| contribution, support and security routes | `CONTRIBUTING.md` and `SECURITY.md` | enabled GitHub Issues and verified private vulnerability reporting | implicit repository discovery and any unsupported contact claim |

## 2. Decisions and measured gate cost

- Job 1 serializes its RED and GREEN tasks. It replaces only the descriptor and
  resource/target selection; its GREEN task also writes the minimal Agent links
  needed by the RED documentation inventory. The existing one-path exclusive
  writer, five Python resources, output names, bytes and execution assertions
  remain.
- Job 2 waits for Job 1 because it extends those rendered authorities with the
  compatibility and trust routes. It changes no tests or prose mirrors; the
  existing documentation harness and strict site build remain its evidence.
- No dependency, workflow, benchmark, threshold, test command, permanent score
  artifact or gate is introduced. The unchanged repository `verify:` is the
  candidate merge gate. A built-wheel adoption sample and field-by-field score
  report are closure evidence, not a new CI obligation.
- The main thread enables and verifies GitHub native private vulnerability
  reporting before Job 2 merges security guidance. Documentation may link only
  that verified route; it must not add an email, credential, SLA or bounty.

## DAG

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `rand_engine/cli.py`, `rand_engine/cases/agent.md.txt`, `README.md`, `docs/getting-started.md`, `mkdocs.yml`, `llms.txt`, `skills/rand-engine/SKILL.md`, `tests/test_9_cli.py`, `tests/test_docs.py`, `tests/integrations/test_public_api.py` |
| Job 2 | Job 1 | 2 | `README.md`, `docs/getting-started.md`, `docs/compatibility.md`, `mkdocs.yml`, `llms.txt`, `skills/rand-engine/SKILL.md`, `CONTRIBUTING.md`, `SECURITY.md` |

## 3. Reconciliation (after Job 2)

**W:** `CHANGELOG.md`, `specs/memory/ARCHITECTURE.md`, `specs/memory/QUALITY.md`, `specs/memory/product/onboarding/get-started-cli.md`, `specs/memory/product/onboarding/documentation.md`, `specs/memory/product/api/public-api.md`, `specs/memory/product/content/templates-and-examples.md`, `specs/memory/product/catalog.json`, `specs/memory/product/index.md`, `llms.txt`, `specs/releases/0.8.0/_RELEASE.json`.

The product engineer records the agent starter and adoption authorities in the
CHANGELOG and reconciles the named atoms against the final diff. It records
unchanged atoms as reviewed where the source work did not change their truth,
regenerates catalog/index and refreshes only markers affected by those atoms.
It records a field-by-field evidence score that keeps candidate readiness,
public availability and retrieval observations separate. It leaves `outreach`
active and does not represent rc-8 or its closure as stable publication.
