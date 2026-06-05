# TASKS: v0.6.4 - Dependabot vulnerability zero-tolerance hotfix

**Status:** Aprovado
**Release ID:** v0.6.4
**Owner:** product-engineer
**Created:** 2026-06-05

Marks: `[ ]` OPEN, `[-]` IN PROGRESS, `[x]` DONE.

## Group G1 - Security Dependency Hotfix

### T-SEC-01 - Upgrade vulnerable Poetry and pytest dependency surfaces

- **Status:** [-]
- **Owner:** Codex
- **Write set:**
  - `requirements.txt`
  - `pyproject.toml`
  - `poetry.lock`
  - release automation metadata only if required for stable `0.6.4`
- **Acceptance:**
  - Poetry is pinned or constrained to a patched version `>=2.3.4` wherever
    Dependabot reads it.
  - pytest is pinned or constrained to a patched version `>=9.0.3` wherever
    Dependabot reads it.
  - Lockfile is regenerated/updated consistently.
  - Full test suite passes with cache disabled or redirected outside the repo.
  - Security review reports zero tolerated Dependabot vulnerabilities.
  - QA, code review, and security review approve before marking this task done.
