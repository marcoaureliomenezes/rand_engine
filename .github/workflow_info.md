# CI/CD Pipeline Documentation# CI/CD Pipeline Documentation# 🚀 CI/CD Workflows - Rand Engine



## Overview



Automated CI/CD pipeline with GitHub Actions for testing, security scanning, versioning, and PyPI publishing using Trusted Publishing (no tokens required).## Overview> Documentação completa do sistema de CI/CD com versionamento RC, segurança e visual summaries



**Key Features:** RC versioning for `development`, stable versioning for `master`, multi-platform testing (Ubuntu/Windows/macOS), Python 3.10-3.12, security scanning (SAST/CodeQL), optimized execution.



---This repository uses a fully automated CI/CD pipeline with GitHub Actions for testing, security scanning, versioning, and publishing to PyPI.## 📋 Índice



## Branch Strategy & Versioning



| Branch | Tag Format | PyPI Release | Source |### Key Features- [Visão Geral](#-visão-geral)

|--------|-----------|--------------|--------|

| `development` | `X.Y.Zrc[N]` (e.g., `0.5.5rc1`) | Pre-release | Auto-increments on each merge |- ✅ Automated RC (Release Candidate) versioning for `development` branch- [Estratégia de Versionamento](#-estratégia-de-versionamento)

| `master` | `X.Y.Z` (e.g., `0.5.5`) | Stable | From `pyproject.toml` |

- ✅ Automated stable versioning for `master` branch  - [Workflows Implementados](#-workflows-implementados)

**Version Source:** `pyproject.toml` - always use clean version without suffixes.

- ✅ Multi-platform testing (Ubuntu, Windows, macOS)- [Segurança e Otimizações](#-segurança-e-otimizações)

**Flow Example:**

```- ✅ Multi-version Python support (3.10, 3.11, 3.12)- [Visual Summaries](#-visual-summaries)

pyproject.toml: version = "0.5.5"

  ↓- ✅ Security scanning (SAST, dependency check, CodeQL)- [Fluxo Completo](#-fluxo-completo)

development merges → 0.5.5rc1, 0.5.5rc2, 0.5.5rc3...

  ↓- ✅ PyPI Trusted Publishing (no tokens needed)- [Configuração Necessária](#-configuração-necessária)

master merge → 0.5.5 (stable)

```- ✅ Optimized test execution (no duplicate runs)- [Como Usar](#-como-usar)



**To Bump Version:** Edit `pyproject.toml`, commit, and merge to `development`.- [Troubleshooting](#-troubleshooting)



------- [Melhores Práticas](#-melhores-práticas)



## Workflows



### `test_on_push.yml`## Branch Strategy---

- **Trigger:** Push to feature branches (not `master`/`development`)

- **Action:** Runs tests (3 OS × 3 Python = 9 jobs) if NO open PR exists

- **Purpose:** Prevents duplicate test runs

### Protected Branches## 🎯 Visão Geral

### `pr_to_development.yml`

- **Trigger:** PR to `development`

- **Validates:** Source is NOT `master`

- **Runs:** Security (SAST/Semgrep/CodeQL), dependency scan, tests (3 OS × 3 Python), coverage (60% min), build validation| Branch | Purpose | Versioning | PyPI Release |Este projeto utiliza **CI/CD totalmente automatizado** com os seguintes princípios:

- **Required:** Must pass to merge

|--------|---------|------------|--------------|

### `pr_to_master.yml`

- **Trigger:** PR to `master`| `master` | Production stable releases | `X.Y.Z` (e.g., `0.5.5`) | Stable release |- ✅ **Tags automáticas** - Sem criação manual

- **Validates:** Source IS `development`

- **Runs:** Tests (3 OS × 3 Python), coverage (60% min)| `development` | Pre-release testing | `X.Y.Zrc[N]` (e.g., `0.5.5rc1`) | Pre-release |- ✅ **Apenas RC** para pre-release (sem alpha/beta)

- **Required:** Must pass to merge

- ✅ **Multi-job workflows** - Modularidade e clareza

### `auto_tag_publish_development.yml`

- **Trigger:** Merge to `development`### Working Branches- ✅ **PyPI Trusted Publishing** - Sem tokens ou senhas

- **Actions:** 

  1. Determine next RC number (e.g., `0.5.5rc3`)Any other branch (feature branches, bugfix branches, etc.) - these are NOT protected.- ✅ **Segurança em camadas** - SAST, dependency scanning, CodeQL

  2. Test (Python 3.10-3.12, Ubuntu only)

  3. Build package- ✅ **Testes otimizados** - Sem duplicação (~66% economia)

  4. Create git tag

  5. Publish to PyPI as pre-release---- ✅ **Coverage enforcement** - Mínimo 60% obrigatório

  6. Create GitHub Release

- ✅ **Melhores práticas** - Validação, testes, instalação

### `auto_tag_publish_master.yml`

- **Trigger:** Merge to `master`## Versioning System- ✅ **Observabilidade** - Logs detalhados e sumários visuais

- **Actions:**

  1. Extract version from `pyproject.toml`

  2. Test (Python 3.10-3.12, Ubuntu only)

  3. Build package### Version Source of Truth### Estrutura de Branches

  4. Create git tag

  5. Publish to PyPI as stable release```toml

  6. Create GitHub Release

# pyproject.toml**Branches Protegidas:**

---

version = "0.5.5"  # Always clean version WITHOUT suffixes- `master` - Versões estáveis em produção

## Developer Guide

```- `development` - Versões RC (Release Candidate)

### Feature Development

```bash

git checkout -b feature/xyz

git commit -am "feat: description"### How Versioning Works**Branches Desprotegidas:**

git push -u origin feature/xyz

gh pr create --base development- Qualquer outra branch (features, bugfixes, etc.)

# After merge → auto-tagged as X.Y.Zrc[N] and published

```**Development Branch (RC - Release Candidate):**



### Production Release- First merge to `development` → creates tag `0.5.5rc1`---

```bash

gh pr create --base master --head development --title "release: X.Y.Z"- Second merge to `development` → creates tag `0.5.5rc2`  

# After merge → tagged as X.Y.Z and published

```- Third merge to `development` → creates tag `0.5.5rc3`## 📦 Estratégia de Versionamento



### Version Bump- And so on...

```bash

# Edit pyproject.toml: version = "0.6.0"### Fonte Única de Verdade

git commit -am "chore: bump version to 0.6.0"

# PR to development → creates 0.6.0rc1 on merge**Master Branch (Stable):**```toml

```

- Merge from `development` to `master` → creates tag `0.5.5`# pyproject.toml

---

version = "0.5.5"  # Sempre versão limpa, SEM sufixos

## Security & Testing

### How to Change Version```

### Security Tools

- **SAST:** Bandit (Python security), Semgrep (patterns)

- **Dependencies:** Safety, pip-audit

- **Code Analysis:** CodeQL1. Edit `pyproject.toml`:### Versionamento Semântico

- **Publishing:** PyPI Trusted Publishing (OIDC-based)

   ```toml

### Test Matrix

- **PR workflows:** Ubuntu/Windows/macOS × Python 3.10/3.11/3.12   version = "0.6.0"  # Update to new version| Ambiente | Formato | Exemplo | Uso |

- **Publish workflows:** Ubuntu only × Python 3.10/3.11/3.12

- **Coverage:** 60% minimum (enforced on Python 3.12 + Ubuntu)   ```|----------|---------|---------|-----|



---| **Development** | `X.Y.Zrc[N]` | `0.5.5rc1`, `0.5.5rc2` | Pre-releases no PyPI |



## Configuration2. Commit and create PR:| **Master** | `X.Y.Z` | `0.5.5` | Versão estável no PyPI |



### Branch Protection   ```bash

**`development`:** Require PR + passing checks (validation, tests, security, build)  

**`master`:** Require PR + passing checks (validation from `development`, tests)   git add pyproject.toml### Fluxo de Versões



### PyPI Trusted Publishing   git commit -m "chore: bump version to 0.6.0"

Configure at PyPI project settings → Publishing → Add publisher:

- **Project:** `rand-engine`   git push```

- **Owner:** `marcoaureliomenezes`

- **Repo:** `rand_engine`   ```pyproject.toml: version = "0.5.5"

- **Workflows:** `auto_tag_publish_development.yml`, `auto_tag_publish_master.yml`

         ↓

---

3. After PR is merged to `development`:    DEVELOPMENT

## Troubleshooting

   - Tag `0.6.0rc1` is automatically created         ↓

| Issue | Solution |

|-------|----------|   - Package is published to PyPI as pre-release   PR Merged #1 → 0.5.5rc1 (PyPI pre-release)

| PyPI upload fails | Verify Trusted Publishing config matches repo owner/name/workflow exactly |

| PySpark tests crash on Windows | Expected - auto-skipped on Windows + Python 3.12 |   PR Merged #2 → 0.5.5rc2 (PyPI pre-release)

| RC number doesn't increment | Check tags were created/pushed: `git push --tags` |

| Coverage fails | Add tests or adjust threshold (not recommended) |---   PR Merged #3 → 0.5.5rc3 (PyPI pre-release)



---         ↓



## Best Practices## Workflows    PR → MASTER



**DO:** Create PRs, write tests, keep `pyproject.toml` clean (no suffixes), use semantic commits           ↓

**DON'T:** Create tags manually, push to protected branches, add version suffixes, merge `master` → `development`

### 1. `test_on_push.yml` - Tests on Feature Branches   PR Merged → 0.5.5 (PyPI stable)

---

**Trigger:** Push to any branch EXCEPT `master` and `development````

## Monitoring



```bash

gh run list --limit 10           # Check workflow runs**What it does:**### Mudança de Versão

gh release list                   # View releases

pip index versions rand-engine    # Check PyPI versions- Checks if an open PR exists for the branch

```

- If NO PR: Runs full test suite (3 OS × 3 Python versions = 9 jobs)Para mudar a versão, edite **apenas** `pyproject.toml`:

- If PR exists: Skips (tests will run in PR workflow)

```bash

**Why:** Prevents duplicate test runs when you push to a branch with an open PR.# Editar pyproject.toml

version = "0.5.6"

### 2. `pr_to_development.yml` - PR Validation for Development

**Trigger:** PR opened/updated targeting `development` branch# Commit e PR → development

git add pyproject.toml

**What it does:**git commit -m "chore: bump version to 0.5.6"

1. **Validation**: Ensures PR is NOT from `master` branch# Após merge: 0.5.6rc1 será criada automaticamente

2. **Security Scans**:```

   - SAST (Static Application Security Testing) with Bandit + Semgrep

   - Dependency vulnerability scanning with Safety + pip-audit---

   - CodeQL analysis for code security issues

3. **Tests**: Full test suite (3 OS × 3 Python versions)## �️ Segurança e Otimizações

4. **Coverage**: Enforces minimum 60% code coverage

5. **Quality Checks**: Validates package building and installation### ✅ Problema Resolvido: Testes Duplicados



**Branch Protection:** This workflow MUST pass before merging to `development`.**Antes:**

```

### 3. `pr_to_master.yml` - PR Validation for MasterPush em feature → test_on_push.yml executa

**Trigger:** PR opened/updated targeting `master` branchAbrir PR → pr_to_development.yml executa (DUPLICADO)

Push no PR → pr_to_development.yml executa (TRIPLICADO)

**What it does:**```

1. **Validation**: Ensures PR comes ONLY from `development` branch

2. **Tests**: Full test suite (3 OS × 3 Python versions)**Depois:**

3. **Coverage**: Enforces minimum 60% code coverage```

Push em feature (sem PR) → test_on_push.yml executa

**Branch Protection:** This workflow MUST pass before merging to `master`.Push em feature (com PR aberto) → test_on_push.yml SKIP ⏭️

Abrir PR → pr_to_development.yml executa (ÚNICA VEZ)

### 4. `auto_tag_publish_development.yml` - Deploy to DevelopmentPush no PR → pr_to_development.yml executa (ATUALIZAÇÃO)

**Trigger:** PR merged to `development` branch```



**What it does:****Economia:** ~66% menos execuções de testes!

1. **Prepare**: Extracts version from `pyproject.toml` and determines next RC number

2. **Test**: Runs tests on Python 3.10, 3.11, 3.12 (Ubuntu only)### 🔒 Camadas de Segurança Implementadas

3. **Build**: Creates wheel and source distribution

4. **Validate**: Tests package installation and basic imports#### 1. SAST - Static Application Security Testing

5. **Tag**: Creates git tag (e.g., `0.5.5rc1`)

6. **Publish**: Uploads to PyPI as pre-release using Trusted Publishing**Bandit (Python Security Scanner)**

7. **Release**: Creates GitHub Release with changelog- Detecta vulnerabilidades comuns no código Python

- Exemplos: `eval()`, `exec()`, SQL injection, hardcoded passwords, weak cryptography

**Example Flow:**- Configuração: `.bandit` suprime falsos positivos (B101, B311, B324)

```- Status: ⚠️ Warning (não bloqueia PR)

pyproject.toml: version = "0.5.5"

  ↓**Semgrep (Advanced Static Analysis)**

Merge PR #1 → Tag: 0.5.5rc1 → PyPI: rand-engine==0.5.5rc1- Análise semântica avançada

Merge PR #2 → Tag: 0.5.5rc2 → PyPI: rand-engine==0.5.5rc2- Exemplos: Code injection, insecure deserialization, path traversal, XSS

Merge PR #3 → Tag: 0.5.5rc3 → PyPI: rand-engine==0.5.5rc3- Status: ⚠️ Warning (não bloqueia PR)

```

#### 2. Dependency Scanning

### 5. `auto_tag_publish_master.yml` - Deploy to Production

**Trigger:** PR merged to `master` branch**Safety (Python Package Vulnerabilities)**

- Verifica vulnerabilidades conhecidas em dependências

**What it does:**- Database: CVE (Common Vulnerabilities and Exposures)

1. **Prepare**: Extracts version and checks if tag already exists- Status: ⚠️ Warning (não bloqueia PR)

2. **Test**: Runs tests on Python 3.10, 3.11, 3.12 (Ubuntu only)

3. **Build**: Creates wheel and source distribution**Trivy (Comprehensive Scanner)**

4. **Validate**: Tests package installation and basic imports  - Scanner multi-propósito: vulnerabilidades, misconfigurações, secrets, licenses

5. **Tag**: Creates git tag (e.g., `0.5.5`)- Upload SARIF para GitHub Security tab

6. **Publish**: Uploads to PyPI as stable release using Trusted Publishing- Status: ⚠️ Warning (não bloqueia PR)

7. **Release**: Creates GitHub Release with changelog

#### 3. CodeQL (GitHub Advanced Security)

**Example Flow:**

```- Análise semântica profunda (gratuito para repos públicos)

pyproject.toml: version = "0.5.5"- Queries: security-extended + security-and-quality

  ↓- Taint analysis, data flow analysis, control flow analysis, CWE detection

Merge PR from development → Tag: 0.5.5 → PyPI: rand-engine==0.5.5 (stable)- Status: ⚠️ Warning (não bloqueia PR)

```

#### 4. Coverage Enforcement

---

- **Mínimo:** 60% de cobertura de testes

## Developer Workflows- **Bloqueio:** PR não pode ser mergeado se coverage < 60%

- **Status:** ❌ Blocker (falha CI se não atender)

### Working on a Feature

### 🚨 Política de Segurança

```bash

# 1. Create feature branch**❌ Blockers (PR não pode ser mergeado):**

git checkout -b feature/my-feature1. Testes falhando

2. Coverage < 60%

# 2. Make changes and commit3. Validação de source branch falhar

git add .

git commit -m "feat: add new feature"**⚠️ Warnings (Review necessário, mas não bloqueia):**

1. Vulnerabilidades detectadas pelo Bandit

# 3. Push to remote2. Issues encontrados pelo Semgrep

git push -u origin feature/my-feature3. Vulnerabilidades em dependências (Safety/Trivy)

# ✅ test_on_push.yml runs automatically4. Findings do CodeQL



# 4. Create PR to development**Razão:** Nem todo "finding" é um problema real. Falsos positivos são comuns, especialmente em bibliotecas de geração de dados de teste.

gh pr create --base development --title "feat: add new feature"

# ✅ pr_to_development.yml runs (includes security scans)### 🔧 Fix: Poetry Export Error



# 5. After PR approval and merge**Problema:** `The requested command export does not exist.`

# ✅ auto_tag_publish_development.yml runs

# ✅ Creates tag like 0.5.5rc1**Solução:** Desde Poetry 1.2+, o comando `export` foi movido para plugin separado.

# ✅ Publishes to PyPI as pre-release

``````yaml

- name: Install Poetry Export Plugin

### Releasing to Production  run: poetry self add poetry-plugin-export



```bash- name: Export requirements

# 1. Create PR from development to master  run: poetry export -f requirements.txt --output requirements.txt --without-hashes

gh pr create --base master --head development --title "release: version 0.5.5"```

# ✅ pr_to_master.yml runs

### 🛡️ SQL Injection Protection

# 2. After PR approval and merge

# ✅ auto_tag_publish_master.yml runsImplementado validação de input em handlers de banco de dados:

# ✅ Creates tag 0.5.5

# ✅ Publishes to PyPI as stable release```python

```# Valida table names (apenas alphanumeric + underscore)

if not table_name.replace('_', '').isalnum():

### Bumping Version    raise ValueError(f"Invalid table name: {table_name}")

```

```bash

# 1. Edit pyproject.tomlArquivos protegidos:

version = "0.6.0"- `rand_engine/integrations/duckdb_handler.py`

- `rand_engine/integrations/sqlite_handler.py`

# 2. Commit and create PR

git add pyproject.toml### 📊 Arquitetura de Segurança

git commit -m "chore: bump version to 0.6.0"

git push```

┌─────────────────────────────────────────────────────────┐

# 3. Create PR to development│               PR para Development Branch                 │

gh pr create --base development└─────────────────────────────────────────────────────────┘

                         │

# 4. After merge        ┌────────────────┼────────────────┬──────────────┐

# ✅ First merge creates: 0.6.0rc1        ↓                ↓                ↓              ↓

# ✅ Second merge creates: 0.6.0rc2┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────┐

# etc...│   SAST       │  │ Dependency   │  │ CodeQL   │  │  Tests   │

```│  Analysis    │  │   Scanning   │  │ Analysis │  │ + Cov    │

│              │  │              │  │          │  │  ≥60%    │

---│ • Bandit     │  │ • Safety     │  │ • Taint  │  │          │

│ • Semgrep    │  │ • Trivy      │  │ • Data   │  │ • Pytest │

## Security Features│              │  │              │  │   Flow   │  │ • Cov    │

│ Status: ⚠️   │  │ Status: ⚠️   │  │ Status:⚠️│  │Status: ❌│

### 1. SAST (Static Application Security Testing)│ (Warning)    │  │ (Warning)    │  │(Warning) │  │(Blocker) │

- **Bandit**: Python security linter - finds common security issues└──────────────┘  └──────────────┘  └──────────┘  └──────────┘

- **Semgrep**: Multi-language static analysis - detects security patterns        │                │                │              │

        └────────────────┴────────────────┴──────────────┘

### 2. Dependency Scanning                           │

- **Safety**: Checks for known vulnerabilities in Python dependencies                         ↓

- **pip-audit**: Audits Python packages for security vulnerabilities              ✅ READY TO MERGE (if tests pass)

              ⚠️  REVIEW SECURITY FINDINGS

### 3. CodeQL Analysis```

- Advanced semantic code analysis

- Detects security vulnerabilities and coding errors### 🔧 Ferramentas e Custos

- Runs on every PR to `development`

| Ferramenta | Tipo | Custo | Onde Executa |

### 4. PyPI Trusted Publishing|------------|------|-------|--------------|

- No API tokens or passwords stored| **Bandit** | SAST Python | Grátis | GitHub Actions |

- Uses OpenID Connect (OIDC) for authentication| **Semgrep** | SAST Universal | Grátis (Community) | GitHub Actions |

- More secure than traditional token-based publishing| **Safety** | Dependency | Grátis (DB básico) | GitHub Actions |

| **Trivy** | Multi-scanner | Grátis (Open Source) | GitHub Actions |

---| **CodeQL** | Advanced SAST | Grátis (repos públicos) | GitHub Actions |

| **pytest-cov** | Coverage | Grátis | GitHub Actions |

## Testing Strategy| **Codecov** | Coverage Viz | Grátis (repos públicos) | Cloud |



### Test Matrix**Total:** R$ 0,00 para repositórios públicos! 🎉

| OS | Python Versions | When |

|----|----------------|------|---

| Ubuntu | 3.10, 3.11, 3.12 | All workflows |

| Windows | 3.10, 3.11, 3.12 | PR workflows only |## 📊 Visual Summaries

| macOS | 3.10, 3.11, 3.12 | PR workflows only |

### Todos os Workflows têm Summaries Visuais

### Coverage Requirements

- Minimum: 60%#### 1. `test_on_push.yml` - 3 Cenários

- Measured on Python 3.12 + Ubuntu

- Enforced in PR workflows**Cenário A: Tests Executados com Sucesso ✅**

```markdown

### Optimizations# 🧪 Test Results - Feature Branch

- **No duplicate runs**: If PR exists, `test_on_push.yml` skips- Branch info table

- **OS optimization**: Publish workflows only test on Ubuntu- Test execution status (all ✅)

- **Caching**: Poetry dependencies are cached for faster runs- Next steps: Create PR commands and links

```

---

**Cenário B: Tests Executados com Falha ❌**

## Configuration Requirements```markdown

# 🧪 Test Results - Feature Branch

### GitHub Settings- Branch info table

- Test execution status (with ❌)

#### 1. Branch Protection Rules- Debugging steps and local test commands

```

**For `development` branch:**

- Require a pull request before merging**Cenário C: Tests Pulados (PR existe) ⏭️**

- Require status checks to pass:```markdown

  - `Validate PR Source`# 🧪 Test Results - Feature Branch

  - `Run Tests (all matrix combinations)`- Branch info table

  - `Security - SAST`- Explanation: Tests run on PR workflow

  - `Security - Dependency Scanning`- Link to PR checks

  - `Security - CodeQL````

  - `Build and Validate Package`

#### 2. `pr_to_development.yml` - Security + Tests

**For `master` branch:**

- Require a pull request before merging```markdown

- Require status checks to pass:# 🔍 Security & Test Validation

  - `Validate PR from Development`- Security analysis results (4 tools)

  - `Run Tests (all matrix combinations)`- Test results matrix (Python 3.10, 3.11, 3.12)

- Coverage status

#### 2. PyPI Trusted Publishing- Links to artifacts

```

Go to PyPI project settings:

1. Navigate to: Publishing → Add a new publisher#### 3. `auto_tag_publish_development.yml` - RC Deployment

2. Configure:

   - **PyPI Project Name**: `rand-engine````markdown

   - **Owner**: `marcoaureliomenezes`# 📦 RC Deployment Complete

   - **Repository**: `rand_engine`- Version info (e.g., 0.5.5rc1)

   - **Workflow name**: `auto_tag_publish_development.yml`- Pipeline status table (all 7 jobs)

   - **Environment name**: leave blank- PyPI pre-release link

- GitHub Pre-Release link

3. Repeat for `auto_tag_publish_master.yml`- Installation commands

- Testing instructions

### Repository Secrets```



No secrets are needed! PyPI Trusted Publishing uses OIDC.#### 4. `auto_tag_publish_master.yml` - Production Deployment



---**Success Scenario:**

```markdown

## Troubleshooting# 🎉 Production Deployment Complete!

- Version info with RC promotion details

### Build Fails on PyPI Upload- Pipeline status table (all 6 jobs)

- Direct links to PyPI and GitHub Release

**Problem:** `Error: Invalid or non-existent authentication information`- Installation: pip install rand-engine==X.Y.Z

- Testing instructions

**Solution:** - Next steps suggestions

1. Check PyPI Trusted Publishing is configured correctly```

2. Verify repository owner and name match exactly

3. Ensure workflow name is spelled correctly**Skip Scenario (tag exists):**

```markdown

### Tests Fail Only on Windows# ⏭️ Deployment Skipped

- Tag already exists explanation

**Problem:** PySpark tests crash on Windows + Python 3.12- Links to existing release

- Guidance on creating new version

**Solution:** ```

This is expected. Tests automatically skip PySpark on Windows + Python 3.12.

See `tests/fixtures/f5_spark_fixtures.py` for the skip logic.### 🎨 Benefícios dos Summaries



### RC Number Doesn't Increment1. **Visibilidade Total**: Status de cada job em formato tabela

2. **Documentação Automática**: Comandos prontos para copiar

**Problem:** Multiple merges create the same RC tag3. **Debugging Facilitado**: Mensagens claras sobre o que fazer

4. **Profissionalismo**: UX consistente e visual atraente

**Solution:**5. **Orientação Clara**: Próximos passos baseados no contexto

1. Check that previous tags were created successfully

2. Verify git tags are pushed to remote: `git push --tags`---

3. The workflow uses `git tag -l` to find existing RCs



### Coverage Below 60%## 🔄 Workflows Implementados



**Problem:** PR fails due to low coverage### 1. `test_on_push.yml` - Testes em Feature Branches



**Solution:****Trigger:** Push em qualquer branch **exceto** `master` e `development`

1. Add tests for new code

2. Or adjust the threshold in workflow files (not recommended)**Jobs:**

1. **check_pr**: Detecta se PR existe (usando GitHub CLI)

---2. **test**: Testes Python 3.10, 3.11, 3.12 (apenas se não houver PR)

3. **summary**: Visual report com 3 cenários (success/failure/skip)

## Best Practices

**Função:**

### DO ✅- Testes automáticos antes de criar PRs

- Always create PRs for changes (even small ones)- Skip inteligente se PR já existe (evita duplicação)

- Write tests for new features- Cobertura de testes

- Keep version in `pyproject.toml` clean (no `-rc` suffixes)- Orientação sobre próximos passos

- Test RC versions before promoting to master

- Use semantic commit messages (`feat:`, `fix:`, `chore:`)**Uso:** Desenvolvimento local em feature branches



### DON'T ❌---

- Don't create tags manually

- Don't push directly to `master` or `development`### 2. `pr_to_development.yml` - Validação de PR + Security

- Don't add version suffixes to `pyproject.toml`

- Don't merge `master` back into `development`**Trigger:** Pull Request para `development`

- Don't skip security scan failures without investigation

**Jobs:**

---1. **validate_source**: Source branch ≠ master

2. **security_sast**: Bandit + Semgrep (⚠️ warning)

## Monitoring3. **security_dependencies**: Safety + Trivy (⚠️ warning)

4. **security_codeql**: GitHub Advanced Security (⚠️ warning)

### Check Workflow Status5. **test**: Python 3.10, 3.11, 3.12 + Coverage ≥60% (❌ blocker)

```bash6. **summary**: Status de todos os checks

gh run list --limit 10

gh run view <run-id>**Validações:**

```- ✅ Análise de segurança em 5 ferramentas

- ✅ Coverage enforcement (mínimo 60%)

### View Recent Releases- ✅ Poetry export plugin instalado automaticamente

```bash- ✅ Upload SARIF para GitHub Security tab

gh release list

```**Uso:** Validação antes de merge em `development`



### Check PyPI Versions---

```bash

pip index versions rand-engine### 3. `pr_to_master.yml` - Validação Strict

```

**Trigger:** Pull Request para `master`

---

**Validações:**

## Additional Resources- ✅ Source branch **deve** ser `development` (apenas!)

- ✅ Testes completos em Python 3.10, 3.11, 3.12

- [GitHub Actions Documentation](https://docs.github.com/en/actions)- ✅ Coverage upload para Codecov

- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)

- [Semantic Versioning](https://semver.org/)**Uso:** Validação antes de release estável

- [PEP 440 - Version Identification](https://peps.python.org/pep-0440/)

---

### 4. `auto_tag_publish_development.yml` - RC Deployment

**Trigger:** Pull Request **merged** em `development`

**Arquitetura:** 7 jobs modulares

#### Job 1: Prepare
- Extrai versão do `pyproject.toml`
- Determina próxima RC tag (rc1, rc2, rc3, ...)
- Valida formato da versão

#### Job 2: Test
- Testes em Python 3.10, 3.11, 3.12 (matriz)
- Upload de coverage para Codecov
- Cache de dependências Poetry

#### Job 3: Build
- Atualiza versão para RC usando `poetry version $RC_TAG`
- Build do pacote (wheel + source distribution)
- Validação de metadata com `twine check`
- Teste de instalação do pacote

#### Job 4: Create Tag
- Cria tag RC anotada automaticamente
- Push da tag para o repositório
- Mensagem detalhada com metadata

#### Job 5: Publish PyPI
- Publica no PyPI usando OIDC (Trusted Publishing)
- Environment: `development`
- Versão como pre-release

#### Job 6: Create GitHub Release
- Cria GitHub Pre-Release
- Changelog automático desde último RC
- Artifacts do build anexados
- Instruções de instalação

#### Job 7: Summary
- Sumário visual do deployment
- Links para PyPI e GitHub Release
- Status de cada job
- Próximos passos sugeridos

**Outputs:**
```yaml
version: "0.5.5"           # Base version
rc_tag: "0.5.5rc1"         # Full RC tag
rc_number: "1"             # RC number
```

---

### 5. `auto_tag_publish_master.yml` - Production Deployment

**Trigger:** Pull Request **merged** em `master`

**Arquitetura:** 6 jobs principais + skip notification

#### Job 1: Prepare
- Extrai versão do `pyproject.toml`
- Verifica se tag já existe (evita republicação)
- Valida que versão **não tem sufixo RC**
- Encontra último RC tag (para changelog)

#### Job 2: Test
- Testes em Python 3.10, 3.11, 3.12
- Executa apenas se tag não existir

#### Job 3: Build
- Build do pacote (versão limpa, sem RC)
- Validação de metadata
- Teste de instalação

#### Job 4: Create Tag
- Cria tag de produção (sem sufixo)
- Mensagem com promoção de RC (se existir)

#### Job 5: Publish PyPI
- Publica no PyPI como versão estável
- Environment: `production`

#### Job 6: Create GitHub Release
- Cria GitHub Release (não pre-release)
- Changelog desde último RC ou stable
- Mostra qual RC foi promovido
- Artifacts anexados

#### Job 7: Summary
- Sumário visual do deployment
- Informações de versão e RC promovido
- Status de cada job (✅/❌)
- Links para PyPI e GitHub Release
- Comandos de instalação e testes
- Próximos passos sugeridos
- Determina sucesso/falha com exit codes

#### Job 8: Skip Notification
- Executa quando tag já existe
- Explica por que deployment foi pulado
- Links para release existente
- Orientação sobre como criar nova versão

**Outputs:**
```yaml
version: "0.5.5"           # Production version
tag_exists: "false"        # Se já existe
latest_rc: "0.5.5rc3"      # Último RC (se existir)
```

---

## 🔧 Troubleshooting

### Poetry Export Error

**Sintoma:** `The requested command export does not exist.`

**Causa:** Plugin poetry-plugin-export não instalado (obrigatório desde Poetry 1.2+)

**Solução:** Já implementada nos workflows - instala automaticamente:
```yaml
- name: Install Poetry Export Plugin
  run: poetry self add poetry-plugin-export
```

### Bandit False Positives

**Sintoma:** Bandit reporta issues em código de teste/mock data

**Causa:** Biblioteca gera dados aleatórios para testes (uso legítimo de `random`, `assert`, `hashlib`)

**Solução:** Configuração `.bandit` já criada:
```ini
[bandit]
skips = B101,B311,B324  # assert, random, hashlib
```

### Trivy Upload Error

**Sintoma:** `Error: Unable to upload SARIF file`

**Causa:** Trivy pode não gerar SARIF em algumas situações

**Solução:** Já implementada - `continue-on-error: true` nos jobs de segurança

### Coverage Failure

**Sintoma:** `Error: coverage is less than 60%`

**Causa:** Código novo sem testes adequados

**Solução:** Adicionar testes para cobrir pelo menos 60% do código
```bash
# Rodar localmente para ver coverage
poetry run pytest tests/ --cov=rand_engine --cov-report=html
# Abrir htmlcov/index.html para ver detalhes
```

### Tag Already Exists

**Sintoma:** Deployment skip notification

**Causa:** Versão já foi publicada anteriormente

**Solução:** Atualizar versão no `pyproject.toml`:
```toml
[tool.poetry]
version = "0.5.6"  # Incrementar versão
```

### PyPI Publishing Error

**Sintoma:** `invalid-publisher: valid token, but no corresponding publisher`

**Causa:** PyPI Trusted Publishing não configurado corretamente

**Solução:** Verificar configuração no PyPI:
- Workflow name deve ser exato: `auto_tag_publish_development.yml` ou `auto_tag_publish_master.yml`
- Owner e repo devem corresponder exatamente
- Ver seção [Configuração PyPI](#-configuração-necessária)

---

## 🎯 Fluxo Completo

### Diagrama ASCII

```
┌─────────────────────────────────────────────────────────────────┐
│                      FEATURE BRANCH                              │
│                   (feature/nova-feature)                         │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ git push
                           ↓
              ┌────────────────────────┐
              │   test_on_push.yml     │
              │  Python 3.10-3.12      │
              └────────────────────────┘
                           │
                           │ Criar PR → development
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                       PULL REQUEST                               │
│                      → development                               │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ↓
              ┌────────────────────────┐
              │ pr_to_development.yml  │
              │  ✓ Source ≠ master     │
              │  ✓ Tests + Coverage    │
              └────────────────────────┘
                           │
                           │ ✅ MERGE PR
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                   DEVELOPMENT BRANCH                             │
│                      (protected)                                 │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ↓
    ┌──────────────────────────────────────────────┐
    │ auto_tag_publish_development.yml (7 jobs)    │
    │  1. Prepare    → Determina RC tag            │
    │  2. Test       → Python 3.10, 3.11, 3.12     │
    │  3. Build      → poetry version $RC_TAG      │
    │  4. Create Tag → 0.5.5rc1, 0.5.5rc2, ...     │
    │  5. Publish    → PyPI (pre-release)          │
    │  6. Release    → GitHub Pre-Release          │
    │  7. Summary    → Visual deployment report     │
    └──────────────────────────────────────────────┘
                           │
                           │ Validação e testes
                           │ Criar PR → master
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                       PULL REQUEST                               │
│                        → master                                  │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ↓
              ┌────────────────────────┐
              │   pr_to_master.yml     │
              │  ✓ Source = development│
              │  ✓ Tests + Coverage    │
              └────────────────────────┘
                           │
                           │ ✅ MERGE PR
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                      MASTER BRANCH                               │
│                      (protected)                                 │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ↓
    ┌──────────────────────────────────────────────┐
    │   auto_tag_publish_master.yml (6 jobs)       │
    │  1. Prepare    → Extrai versão, valida       │
    │  2. Test       → Python 3.10, 3.11, 3.12     │
    │  3. Build      → Versão limpa (sem RC)       │
    │  4. Create Tag → 0.5.5                       │
    │  5. Publish    → PyPI (stable)               │
    │  6. Release    → GitHub Release              │
    └──────────────────────────────────────────────┘
                           │
                           ↓
                   ✅ PRODUCTION READY
```

### Exemplos Práticos

#### Cenário 1: Nova Feature
```bash
# 1. Criar feature branch
git checkout -b feature/minha-feature

# 2. Desenvolver
# ... editar código ...

# 3. Commit e push
git add .
git commit -m "feat: adiciona nova feature"
git push origin feature/minha-feature
# → test_on_push.yml executa automaticamente

# 4. Criar PR para development (GitHub UI)
# → pr_to_development.yml valida

# 5. Merge PR
# → auto_tag_publish_development.yml
# → Tag 0.5.5rc1 criada
# → PyPI: 0.5.5rc1 (pre-release)
# → GitHub: Pre-Release 0.5.5rc1
```

#### Cenário 2: Múltiplas RCs
```bash
# PR 1 mergeado → 0.5.5rc1
# PR 2 mergeado → 0.5.5rc2
# PR 3 mergeado → 0.5.5rc3
# ... até estar pronto
```

#### Cenário 3: Release Estável
```bash
# 1. Criar PR: development → master (GitHub UI)
# → pr_to_master.yml valida (strict: source deve ser development)

# 2. Merge PR
# → auto_tag_publish_master.yml
# → Tag 0.5.5 criada
# → PyPI: 0.5.5 (stable)
# → GitHub: Release 0.5.5 (promovido de 0.5.5rc3)
```

#### Cenário 4: Bump de Versão
```bash
# 1. Editar pyproject.toml
version = "0.5.6"

# 2. Commit
git add pyproject.toml
git commit -m "chore: bump version to 0.5.6"

# 3. Push e criar PR → development

# 4. Após merge:
# → Tag 0.5.6rc1 criada automaticamente
```

---

## 🔐 Configuração Necessária

### PyPI Trusted Publishing (OIDC)

**⚠️ CRÍTICO:** Configure no PyPI antes de usar os workflows

#### URL de Configuração
https://pypi.org/manage/project/rand-engine/settings/publishing/

#### Publisher 1: Development (Pre-Release)

| Campo | Valor |
|-------|-------|
| **PyPI Project Name** | `rand-engine` |
| **Owner** | `marcoaureliomenezes` |
| **Repository name** | `rand_engine` |
| **Workflow name** | `auto_tag_publish_development.yml` |
| **Environment name** | `development` *(opcional)* |

#### Publisher 2: Master (Stable Release)

| Campo | Valor |
|-------|-------|
| **PyPI Project Name** | `rand-engine` |
| **Owner** | `marcoaureliomenezes` |
| **Repository name** | `rand_engine` |
| **Workflow name** | `auto_tag_publish_master.yml` |
| **Environment name** | `production` *(opcional)* |

#### Vantagens do Trusted Publishing
- ✅ Sem API tokens ou senhas
- ✅ Segurança baseada em OIDC (OpenID Connect)
- ✅ Configuração por workflow específico
- ✅ Audit trail completo no GitHub
- ✅ Zero secrets para gerenciar

#### Troubleshooting

**Erro:** `invalid-publisher: valid token, but no corresponding publisher`

**Causa:** Workflow name no PyPI não bate com o arquivo real

**Solução:** Verifique que o workflow name está **exatamente**:
- ✅ `auto_tag_publish_development.yml` (para development)
- ✅ `auto_tag_publish_master.yml` (para master)
- ❌ Não use nomes antigos ou variações

---

### GitHub Secrets

#### CODECOV_TOKEN
- **Onde:** Repository Settings → Secrets → Actions
- **Uso:** Upload de cobertura de testes
- **Como obter:** https://codecov.io

---

### GitHub Environments (Opcional)

Se usar environments, configure em: Settings → Environments

#### Environment: development
- Sem proteções especiais (deploy automático)
- Ou com revisor opcional

#### Environment: production
- Revisores obrigatórios recomendado
- Delay opcional (ex: 5 minutos)
- Proteção de branch: apenas master

---

## 💡 Como Usar

### Desenvolvimento Diário

```bash
# 1. Feature branch
git checkout -b feature/nome-da-feature

# 2. Desenvolver, testar localmente
poetry run pytest tests/ -v

# 3. Commit
git add .
git commit -m "feat: descrição"

# 4. Push
git push origin feature/nome-da-feature

# 5. Criar PR → development
# 6. Aguardar validação e merge
# 7. Tag RC criada automaticamente!
```

### Testes Locais

#### Testar lógica de RC tagging
```bash
./.github/test_tag_logic.sh
```

#### Verificar configuração PyPI
```bash
./.github/check_pypi_config.sh
```

#### Rodar testes completos
```bash
poetry run pytest tests/ -v --cov=rand_engine
```

---

## 📦 Melhores Práticas Implementadas

### ✅ Build e Packaging
- [x] Build com Poetry 2.0.1
- [x] Validação de metadata com `twine check`
- [x] Teste de instalação antes de publicar
- [x] Artifacts salvos (30 dias dev, 90 dias prod)
- [x] Wheel (.whl) e Source Distribution (.tar.gz)

### ✅ Testing
- [x] Testes em Python 3.10, 3.11, 3.12 (matriz)
- [x] Coverage tracking com Codecov
- [x] Cache de dependências Poetry
- [x] Fail-fast desabilitado (vê todos os erros)

### ✅ Versioning
- [x] SemVer compliance (X.Y.Zrc[N])
- [x] RC incremento automático (rc1, rc2, rc3, ...)
- [x] Tags anotadas com metadata detalhada
- [x] Changelog automático entre versões

### ✅ Security
- [x] PyPI Trusted Publishing (OIDC)
- [x] Environments com proteção opcional
- [x] Permissões mínimas necessárias
- [x] Secrets management com GitHub Secrets

### ✅ Deployment
- [x] Deploy apenas após merge de PR
- [x] Validação de tag existente (evita duplicação)
- [x] Rollback prevention
- [x] Verificação pós-publicação

### ✅ Observabilidade
- [x] GitHub Actions Summary visual
- [x] Logs detalhados com emojis
- [x] Status de cada job
- [x] Links para PyPI e GitHub Release
- [x] Próximos passos sugeridos

---

## 🔍 Diferenças entre Workflows

| Feature | Development (RC) | Master (Production) |
|---------|-----------------|---------------------|
| **Trigger** | PR merged → development | PR merged → master |
| **Tag Format** | `X.Y.Zrc[N]` | `X.Y.Z` |
| **Incremento** | Automático (rc1, rc2, rc3) | Sem incremento |
| **PyPI** | Pre-release | Stable |
| **GitHub** | Pre-Release | Release (latest) |
| **Environment** | development (opcional) | production (opcional) |
| **Validação Versão** | Aceita RC format | Rejeita se tiver RC |
| **Changelog** | Desde último RC | Desde último RC ou stable |
| **Jobs** | 7 jobs | 6 jobs + skip |
| **Artifact Retention** | 30 dias | 90 dias |

---

## 🎉 Benefícios da Nova Arquitetura

### Antes (Sistema Antigo)
- ❌ Tags alpha/beta/rc misturadas
- ❌ Lógica complexa de evolução
- ❌ Formato inconsistente
- ❌ Difícil de entender sequência
- ❌ Jobs monolíticos
- ❌ Pouca visibilidade

### Depois (Sistema Atual)
- ✅ **Apenas RC** para pre-release
- ✅ **Incremento simples** (rc1, rc2, rc3)
- ✅ **Formato consistente** sempre
- ✅ **Claro e previsível**
- ✅ **Produção limpa** (sem sufixos)
- ✅ **7 jobs modulares** com validações
- ✅ **Melhores práticas** Python packaging
- ✅ **Observabilidade completa**

---

## 📚 Referências

### Documentação Oficial
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Semantic Versioning](https://semver.org/)

### Ferramentas de Segurança
- [Bandit](https://bandit.readthedocs.io/) - Python security scanner
- [Semgrep](https://semgrep.dev/docs/) - Advanced static analysis
- [Safety](https://pyup.io/safety/) - Dependency vulnerability scanner
- [Trivy](https://aquasecurity.github.io/trivy/) - Comprehensive security scanner
- [CodeQL](https://codeql.github.com/) - GitHub Advanced Security

### Security Standards
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Guidelines](https://nvd.nist.gov/)

### Scripts de Utilidade
- `.github/test_tag_logic.sh` - Testa lógica de RC localmente
- `.github/check_pypi_config.sh` - Diagnóstico de configuração

### Workflows
- `.github/workflows/test_on_push.yml` - Testes em feature branches
- `.github/workflows/pr_to_development.yml` - Validação de PR + Security
- `.github/workflows/pr_to_master.yml` - Validação strict de PR
- `.github/workflows/auto_tag_publish_development.yml` - RC deployment
- `.github/workflows/auto_tag_publish_master.yml` - Production deployment

### Configurações
- `.bandit` - Configuração do Bandit security scanner
- `pyproject.toml` - Poetry configuration e versão do projeto


---

## 📝 Checklist de Setup Inicial

- [ ] Branches `master` e `development` criadas e protegidas
- [ ] Configurei PyPI Trusted Publishing para `auto_tag_publish_development.yml`
- [ ] Configurei PyPI Trusted Publishing para `auto_tag_publish_master.yml`
- [ ] Adicionei `CODECOV_TOKEN` nos GitHub Secrets
- [ ] (Opcional) Configurei GitHub Environments: `development` e `production`
- [ ] Testei `.github/test_tag_logic.sh` localmente
- [ ] Li e entendi o fluxo completo
- [ ] Fiz primeiro merge em development para testar RC deployment
- [ ] Verifiquei tag RC criada no GitHub
- [ ] Verifiquei pacote RC no PyPI
- [ ] Instalei e testei: `pip install rand-engine==0.5.5rc1`

---

## 🚀 Status Atual

**✅ Sistema Implementado e Pronto para Uso**

- **Workflows:** 5 workflows funcionais com visual summaries
- **Segurança:** 5 ferramentas de análise (Bandit, Semgrep, Safety, Trivy, CodeQL)
- **Testes:** Cobertura em 3 versões Python (3.10, 3.11, 3.12)
- **Coverage:** Enforcement de mínimo 60%
- **Otimização:** Testes sem duplicação (~66% economia)
- **Publishing:** PyPI Trusted Publishing (OIDC) configurável
- **Observabilidade:** Logs detalhados e sumários visuais em todos os workflows
- **Documentação:** Completa e atualizada

**🎯 Próximos Passos:**
1. Configurar PyPI Trusted Publishing (development + production)
2. Adicionar `CODECOV_TOKEN` nos GitHub Secrets
3. Testar com merge em development (RC deployment)
4. Validar segurança e coverage
5. Testar promoção para production

---

**Documentação atualizada:** 2025-10-17  
**Versão do sistema:** RC-only com segurança e visual summaries  
**Arquivos consolidados:** README.md, POETRY_EXPORT_FIX.md, MASTER_SUMMARY_ENHANCEMENT.md, TEST_ON_PUSH_SUMMARY.md, SECURITY_IMPROVEMENTS.md

