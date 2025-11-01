# CI/CD Pipeline Documentation

## Overview

Fully automated CI/CD pipeline with 5 workflows managing testing, security, versioning, and PyPI publishing via Trusted Publishing.

---

## Workflows

### 1. `test_on_push.yml` - Feature Branch Testing

**Trigger:** Push to any branch except `master` and `development`

**Purpose:** Validate changes early without duplicating PR tests

**Flow:**
1. **Check PR Existence** - Uses GitHub CLI to detect open PRs
   - If PR exists → Skip (tests run in PR workflow)
   - If no PR → Execute full test matrix

2. **Test Matrix** (9 combinations)
   - OS: Ubuntu, Windows, macOS
   - Python: 3.10, 3.11, 3.12
   - Note: Spark tests auto-skip on Windows + Python 3.12

3. **Summary** - Markdown report in GitHub Actions UI
   - Test results table
   - Next steps (create PR or continue development)

**Key Features:**
- Smart PR detection prevents duplicate runs
- Cross-platform testing ensures compatibility
- Cached Poetry dependencies for speed

---

### 2. `pr_to_development.yml` - Pre-Release Validation

**Trigger:** PR opened/updated targeting `development`

**Purpose:** Comprehensive validation before merging to development branch

**Jobs:**

#### 2.1 Validate Source
- **Check:** PR source is NOT from `master`
- **Why:** Prevents reverse merges

#### 2.2 Security - SAST (Static Analysis)
- **Bandit:** Python security linter (medium+ severity)
- **Semgrep:** Pattern-based security scanner (error severity)
- **Output:** JSON reports uploaded as artifacts (30-day retention)
- **Behavior:** Continue on error (warnings, not blockers)

#### 2.3 Security - Dependency Scanning
- **Safety:** Checks known CVEs in dependencies
- **Trivy:** Comprehensive vulnerability scanner
- **Output:** SARIF uploaded to GitHub Security tab
- **Behavior:** Continue on error (warnings, not blockers)

#### 2.4 Security - CodeQL
- **Analysis:** Advanced semantic code analysis
- **Queries:** `security-extended` + `security-and-quality`
- **Output:** Results in GitHub Security tab

#### 2.5 Test Matrix
- **Full Matrix:** 3 OS × 3 Python = 9 combinations
- **Coverage:** Minimum 60% enforced with `--cov-fail-under=60`
- **Upload:** Coverage XML sent to Codecov (Python 3.12 only)

#### 2.6 Test Package Build & Installation
- **Build:** `poetry build` creates wheel + sdist
- **Validate:** `twine check` verifies metadata
- **Install Test:** Installs wheel and imports `DataGenerator`
- **Functionality Test:** Generates 10 rows with integer and float columns

#### 2.7 Summary
- **Report:** Status table for all jobs
- **Critical:** Source validation, tests, and build must pass
- **Warnings:** Security findings don't block merge

**Branch Protection:** All critical jobs must pass to merge

---

### 3. `pr_to_master.yml` - Production Validation

**Trigger:** PR opened/updated targeting `master`

**Purpose:** Final validation before production release

**Jobs:**

#### 3.1 Validate Source
- **Check:** PR source IS `development`
- **Why:** Enforces release flow (feature → development → master)

#### 3.2 Test Matrix
- **Full Matrix:** 3 OS × 3 Python = 9 combinations
- **Coverage:** Measured but not enforced (already validated in development)
- **Upload:** Coverage to Codecov

#### 3.3 Summary
- **Report:** Pass/fail for validation and tests
- **Requirement:** Both must pass to merge

**Branch Protection:** Validation and tests must pass

---

### 4. `auto_tag_publish_development.yml` - RC Release

**Trigger:** PR merged to `development`

**Purpose:** Automated RC (Release Candidate) tagging and PyPI publishing

**Jobs:**

#### 4.1 Prepare Release
- **Extract Version:** Parse `pyproject.toml` (e.g., `0.5.5`)
- **Find Existing RCs:** `git tag -l "0.5.5rc*"`
- **Determine Next RC:**
  - If no RCs exist → `0.5.5rc1`
  - If `0.5.5rc2` exists → `0.5.5rc3`
- **Output:** `version`, `rc_tag`, `rc_number`

**Logic:**
```bash
# Get existing RCs matching X.Y.Zrc[0-9]+
git tag -l "0.5.5rc*" | grep -E "^0.5.5rc[0-9]+$" | sort -V | tail -1
# Extract number and increment
```

#### 4.2 Test
- **Matrix:** Python 3.10, 3.11, 3.12 (Ubuntu only)
- **Coverage:** Generated but not enforced (validated in PR)

#### 4.3 Build Package
- **Update Version:** `poetry version 0.5.5rc3` (modifies pyproject.toml)
- **Build:** Creates wheel + sdist
- **Validate:** `twine check dist/*`
- **Install Test:** Imports `DataGenerator` from wheel
- **Upload:** Artifacts stored for 30 days

#### 4.4 Create RC Tag
- **Check:** Tag doesn't already exist
- **Create:** Annotated tag with metadata (PR number, commit SHA)
- **Push:** To origin

#### 4.5 Publish to PyPI
- **Method:** PyPI Trusted Publishing (OIDC)
- **Environment:** `development`
- **Artifacts:** Download from build job
- **Publish:** Pre-release flag set automatically by `rc` suffix

#### 4.6 Create GitHub Release
- **Type:** Pre-release
- **Assets:** Wheel + sdist attached
- **Notes:** Changelog from commits

**Result:** Package available as `pip install rand-engine==0.5.5rc3`

---

### 5. `auto_tag_publish_master.yml` - Production Release

**Trigger:** PR merged to `master`

**Purpose:** Automated stable version tagging and PyPI publishing

**Jobs:**

#### 5.1 Prepare Production Release
- **Extract Version:** Parse `pyproject.toml` (e.g., `0.5.5`)
- **Check Tag Exists:** Skip if `0.5.5` already exists
- **Find Latest RC:** For release notes (e.g., `0.5.5rc3`)

#### 5.2 Test
- **Matrix:** Python 3.10, 3.11, 3.12 (Ubuntu only)
- **Skip:** If tag exists

#### 5.3 Build Production Package
- **Verify:** No `rc` suffix in version
- **Build:** `poetry build`
- **Upload:** Artifacts

#### 5.4 Create Production Tag
- **Create:** Annotated tag `0.5.5`
- **Push:** To origin

#### 5.5 Publish to PyPI
- **Method:** Trusted Publishing
- **Environment:** `production`
- **Type:** Stable release (no pre-release flag)

#### 5.6 Create GitHub Release
- **Type:** Latest release
- **Assets:** Wheel + sdist
- **Notes:** Mentions promoted RC if exists

#### 5.7 Deployment Summary
- **Report:** Complete pipeline status
- **Links:** PyPI package, GitHub release
- **Command:** `pip install rand-engine==0.5.5`

**Result:** Package available as stable version on PyPI

---

## Versioning Strategy

### Source of Truth
```toml
# pyproject.toml
version = "0.5.5"  # Clean version, NO suffixes
```

### Version Flow

```
┌─────────────────────────────────────────────┐
│  pyproject.toml: version = "0.5.5"          │
└─────────────────────────────────────────────┘
                    ↓
        ┌───────────────────────┐
        │   development branch  │
        └───────────────────────┘
                    ↓
    ┌──────────────┴──────────────┐
    │  PR #1 merged               │
    │  → Tag: 0.5.5rc1            │
    │  → PyPI: Pre-release        │
    └──────────────┬──────────────┘
                   ↓
    ┌──────────────┴──────────────┐
    │  PR #2 merged               │
    │  → Tag: 0.5.5rc2            │
    │  → PyPI: Pre-release        │
    └──────────────┬──────────────┘
                   ↓
    ┌──────────────┴──────────────┐
    │  PR #3 merged               │
    │  → Tag: 0.5.5rc3            │
    │  → PyPI: Pre-release        │
    └──────────────┬──────────────┘
                   ↓
        ┌───────────────────────┐
        │    master branch      │
        └───────────────────────┘
                   ↓
    ┌──────────────┴──────────────┐
    │  PR merged from development │
    │  → Tag: 0.5.5               │
    │  → PyPI: Stable             │
    └─────────────────────────────┘
```

### Version Bump Process

**To bump from 0.5.5 to 0.6.0:**

1. Edit `pyproject.toml`:
   ```toml
   version = "0.6.0"
   ```

2. Commit and create PR to `development`:
   ```bash
   git add pyproject.toml
   git commit -m "chore: bump version to 0.6.0"
   gh pr create --base development
   ```

3. After merge → `0.6.0rc1` auto-created

4. Subsequent merges → `0.6.0rc2`, `0.6.0rc3`, etc.

5. When ready, PR `development` → `master` → `0.6.0` stable

---

## Security Architecture

### Multi-Layer Defense

| Layer | Tools | Scope | Blocking |
|-------|-------|-------|----------|
| SAST | Bandit, Semgrep | Source code patterns | No (warnings) |
| Dependencies | Safety, Trivy | Known CVEs | No (warnings) |
| CodeQL | GitHub Advanced Security | Semantic analysis | No (warnings) |
| Tests | pytest + coverage | Functionality | Yes (60% min) |

### Why Security Doesn't Block

Security scans are **warnings** to enable fast iteration while maintaining visibility. Critical issues should be addressed before production but don't block development flow.

---

## Testing Strategy

### Test Execution Matrix

| Workflow | OS | Python | Total Jobs |
|----------|-------|--------|-----------|
| `test_on_push.yml` | Ubuntu, Windows, macOS | 3.10, 3.11, 3.12 | 9 |
| `pr_to_development.yml` | Ubuntu, Windows, macOS | 3.10, 3.11, 3.12 | 9 |
| `pr_to_master.yml` | Ubuntu, Windows, macOS | 3.10, 3.11, 3.12 | 9 |
| `auto_tag_publish_development.yml` | Ubuntu | 3.10, 3.11, 3.12 | 3 |
| `auto_tag_publish_master.yml` | Ubuntu | 3.10, 3.11, 3.12 | 3 |

### Coverage Requirements

- **Minimum:** 60% enforced in PR workflows
- **Measured:** Python 3.12 on Ubuntu
- **Uploaded:** To Codecov for trend tracking

### Optimizations

1. **Smart PR Detection:** Skip `test_on_push.yml` if PR exists
2. **Publish OS Optimization:** Only Ubuntu (already validated cross-platform)
3. **Dependency Caching:** Poetry cache based on `poetry.lock` hash
4. **Fail-Fast Disabled:** All matrix combinations complete for visibility

---

## PyPI Trusted Publishing

### Configuration

**At PyPI (per workflow):**
1. Project: `rand-engine`
2. Owner: `marcoaureliomenezes`
3. Repository: `rand_engine`
4. Workflow: `auto_tag_publish_development.yml` or `auto_tag_publish_master.yml`
5. Environment: `development` or `production`

**At GitHub:**
- **No secrets needed** - uses OIDC (OpenID Connect)
- Workflow gets temporary token from PyPI during publish
- Token scoped to specific project + workflow

### Security Benefits

- ✅ No long-lived credentials
- ✅ No token rotation needed
- ✅ Audit trail via OIDC
- ✅ Scoped to specific workflows

---

## Developer Workflows

### Working on Features

```bash
# 1. Create feature branch
git checkout -b feature/new-capability

# 2. Make changes, commit
git commit -am "feat: add new capability"
git push

# Workflow: test_on_push.yml runs (9 jobs)

# 3. Create PR when ready
gh pr create --base development --title "feat: add new capability"

# Workflows: pr_to_development.yml runs
# - Security scans (3 jobs)
# - Tests (9 jobs)
# - Build validation (1 job)

# 4. After approval and merge
# Workflow: auto_tag_publish_development.yml runs
# - Determines RC number (e.g., 0.5.5rc4)
# - Tests (3 jobs)
# - Builds package
# - Creates git tag
# - Publishes to PyPI as pre-release
# - Creates GitHub release

# Result: pip install rand-engine==0.5.5rc4
```

### Releasing to Production

```bash
# 1. Create PR from development to master
gh pr create --base master --head development --title "release: version 0.5.5"

# Workflow: pr_to_master.yml runs
# - Validates source is development
# - Tests (9 jobs)

# 2. After approval and merge
# Workflow: auto_tag_publish_master.yml runs
# - Extracts version 0.5.5
# - Tests (3 jobs)
# - Builds package
# - Creates git tag
# - Publishes to PyPI as stable
# - Creates GitHub release

# Result: pip install rand-engine==0.5.5
```

---

## Branch Protection Rules

### `development` Branch

**Require PR before merging:** Yes

**Required status checks:**
- `Validate PR Source`
- `Security - SAST (Bandit + Semgrep)`
- `Security - Dependency Scanning`
- `Security - CodeQL Analysis`
- `Run Tests (Python X.X on OS)` - all 9 combinations
- `Test Package Build & Installation`

### `master` Branch

**Require PR before merging:** Yes

**Required status checks:**
- `Validate PR from Development`
- `Run Tests (Python X.X on OS)` - all 9 combinations

---

## Monitoring & Troubleshooting

### Check Pipeline Status

```bash
# List recent workflow runs
gh run list --limit 10

# View specific run
gh run view <run-id> --log

# Check releases
gh release list

# View PyPI versions
pip index versions rand-engine
```

### Common Issues

**Issue:** RC number doesn't increment  
**Cause:** Tags not pushed or workflow failed at tag creation  
**Fix:** Check `git tag -l "X.Y.Zrc*"` and re-run workflow

**Issue:** PyPI upload fails with authentication error  
**Cause:** Trusted Publishing misconfigured  
**Fix:** Verify owner/repo/workflow names match exactly

**Issue:** PySpark tests crash on Windows  
**Cause:** Known issue with Python 3.12 + Windows  
**Fix:** Tests auto-skip this combination (see `f5_spark_fixtures.py`)

**Issue:** Coverage below 60%  
**Cause:** New code not covered by tests  
**Fix:** Add tests or adjust threshold (not recommended)

**Issue:** Security scan warnings  
**Cause:** Potential vulnerabilities detected  
**Fix:** Review findings, update dependencies, or accept risk

---

## Best Practices

### DO ✅
- Create PRs for all changes (even small fixes)
- Write tests for new features (maintain 60%+ coverage)
- Keep `pyproject.toml` version clean (no `-rc` suffixes)
- Test RC versions before promoting to master
- Use semantic commit messages (`feat:`, `fix:`, `chore:`)
- Review security findings even if they don't block

### DON'T ❌
- Create or push tags manually (automated by workflows)
- Push directly to `master` or `development` (use PRs)
- Add version suffixes to `pyproject.toml` (handled by workflows)
- Merge `master` back into `development` (one-way flow)
- Skip security warnings without investigation
- Bypass coverage requirements without discussion

---

## Architecture Decisions

### Why RC Versioning?
- **PEP 440 Compliant:** `X.Y.Zrc[N]` is standard pre-release format
- **PyPI Native:** No special handling needed
- **Semantic:** Clear distinction between RC and stable
- **Incremental:** Easy to track multiple pre-releases

### Why Trusted Publishing?
- **Security:** No credentials in GitHub
- **Simplicity:** No token rotation
- **Audit Trail:** OIDC provides full traceability

### Why Continue-on-Error for Security?
- **Developer Velocity:** Don't block on false positives
- **Visibility:** Still see findings in reports
- **Flexibility:** Review and fix on timeline
- **Graduation:** Can promote to blockers later

### Why Multi-Platform Testing?
- **Real-World:** Users run on different OS
- **Early Detection:** OS-specific bugs caught early
- **Confidence:** Know it works everywhere

### Why Skip Tests When PR Exists?
- **Efficiency:** No duplicate runs
- **Resources:** Save GitHub Actions minutes
- **UX:** Single source of truth (PR checks)

---

## Workflow Dependencies

```
Feature Branch Push → test_on_push.yml
                              ↓
                    [Create PR to development]
                              ↓
                   pr_to_development.yml
                              ↓
                      [Merge to development]
                              ↓
              auto_tag_publish_development.yml
                              ↓
                      [Create PR to master]
                              ↓
                      pr_to_master.yml
                              ↓
                        [Merge to master]
                              ↓
                auto_tag_publish_master.yml
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Create feature PR | `gh pr create --base development` |
| Create release PR | `gh pr create --base master --head development` |
| Check workflow status | `gh run list --limit 10` |
| View workflow logs | `gh run view <id> --log` |
| List releases | `gh release list` |
| Check PyPI versions | `pip index versions rand-engine` |
| Install RC | `pip install rand-engine==X.Y.Zrc[N]` |
| Install stable | `pip install rand-engine==X.Y.Z` |
| Run tests locally | `poetry run pytest tests/ -v --cov=rand_engine` |
| Build locally | `poetry build` |
| Validate build | `twine check dist/*` |

---

**Last Updated:** 2025-10-31  
**Pipeline Version:** 2.0  
**Workflows:** 5 (test_on_push, pr_to_development, pr_to_master, auto_tag_publish_development, auto_tag_publish_master)
