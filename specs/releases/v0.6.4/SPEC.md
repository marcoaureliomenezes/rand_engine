# SPEC: v0.6.4 - Dependabot vulnerability zero-tolerance hotfix

**Status:** Aprovado
**Release ID:** v0.6.4
**Owner:** product-engineer
**Created:** 2026-06-05

## 1. Objective

Eliminate all open Dependabot vulnerabilities reported on the default branch and
publish a new stable package release.

## 2. Evidence

GitHub Dependabot reports four open alerts:

- `poetry` in `requirements.txt`: `GHSA-2599-h6xx-hpxp` / `CVE-2026-34591`,
  high severity, fixed in Poetry `2.3.3`.
- `poetry` in `requirements.txt`: `GHSA-73h3-mf4w-8647` /
  `CVE-2026-41140`, low severity, fixed in Poetry `2.3.4`.
- `pytest` in `requirements.txt`: `GHSA-6w46-j5rx-g56g` /
  `CVE-2025-71176`, medium severity, fixed in pytest `9.0.3`.
- `pytest` in `poetry.lock`: same pytest advisory, fixed in pytest `9.0.3`.

The operator decision for this release is zero tolerance for Dependabot
vulnerabilities.

## 3. Scope

In scope:

- Upgrade vulnerable dependency declarations and lock entries so Dependabot has
  no open alerts for the default branch.
- Keep dependency changes minimal: Poetry `>=2.3.4`, pytest `>=9.0.3`, and any
  lockfile metadata required by the resolver.
- Run dependency/security and test validation.
- Publish a new stable release after QA, code review, and security review
  approve the implementation commit.

Out of scope:

- DuckDB correlation work.
- Public API changes.
- README/marketing rewrite except release metadata strictly required by the
  release automation.

## 4. Acceptance Criteria

- `requirements.txt`, `pyproject.toml`, and `poetry.lock` no longer reference
  vulnerable Poetry or pytest versions.
- Dependabot open alerts for the default branch are zero or only remain pending
  GitHub rescans after fixed manifests are pushed.
- Full pytest suite passes.
- Package build/check passes.
- Security review approves the dependency state.
- New stable release is published as `0.6.4`.
