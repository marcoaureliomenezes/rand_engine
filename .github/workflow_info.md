# 🚀 CI/CD Workflows - Rand Engine

> Documentação completa do sistema de CI/CD com versionamento RC, segurança e visual summaries

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Estratégia de Versionamento](#-estratégia-de-versionamento)
- [Workflows Implementados](#-workflows-implementados)
- [Segurança e Otimizações](#-segurança-e-otimizações)
- [Visual Summaries](#-visual-summaries)
- [Fluxo Completo](#-fluxo-completo)
- [Configuração Necessária](#-configuração-necessária)
- [Como Usar](#-como-usar)
- [Troubleshooting](#-troubleshooting)
- [Melhores Práticas](#-melhores-práticas)

---

## 🎯 Visão Geral

Este projeto utiliza **CI/CD totalmente automatizado** com os seguintes princípios:

- ✅ **Tags automáticas** - Sem criação manual
- ✅ **Apenas RC** para pre-release (sem alpha/beta)
- ✅ **Multi-job workflows** - Modularidade e clareza
- ✅ **PyPI Trusted Publishing** - Sem tokens ou senhas
- ✅ **Segurança em camadas** - SAST, dependency scanning, CodeQL
- ✅ **Testes otimizados** - Sem duplicação (~66% economia)
- ✅ **Coverage enforcement** - Mínimo 60% obrigatório
- ✅ **Melhores práticas** - Validação, testes, instalação
- ✅ **Observabilidade** - Logs detalhados e sumários visuais

### Estrutura de Branches

**Branches Protegidas:**
- `master` - Versões estáveis em produção
- `development` - Versões RC (Release Candidate)

**Branches Desprotegidas:**
- Qualquer outra branch (features, bugfixes, etc.)

---

## 📦 Estratégia de Versionamento

### Fonte Única de Verdade
```toml
# pyproject.toml
version = "0.5.5"  # Sempre versão limpa, SEM sufixos
```

### Versionamento Semântico

| Ambiente | Formato | Exemplo | Uso |
|----------|---------|---------|-----|
| **Development** | `X.Y.Zrc[N]` | `0.5.5rc1`, `0.5.5rc2` | Pre-releases no PyPI |
| **Master** | `X.Y.Z` | `0.5.5` | Versão estável no PyPI |

### Fluxo de Versões

```
pyproject.toml: version = "0.5.5"
         ↓
    DEVELOPMENT
         ↓
   PR Merged #1 → 0.5.5rc1 (PyPI pre-release)
   PR Merged #2 → 0.5.5rc2 (PyPI pre-release)
   PR Merged #3 → 0.5.5rc3 (PyPI pre-release)
         ↓
    PR → MASTER
         ↓
   PR Merged → 0.5.5 (PyPI stable)
```

### Mudança de Versão

Para mudar a versão, edite **apenas** `pyproject.toml`:

```bash
# Editar pyproject.toml
version = "0.5.6"

# Commit e PR → development
git add pyproject.toml
git commit -m "chore: bump version to 0.5.6"
# Após merge: 0.5.6rc1 será criada automaticamente
```

---

## �️ Segurança e Otimizações

### ✅ Problema Resolvido: Testes Duplicados

**Antes:**
```
Push em feature → test_on_push.yml executa
Abrir PR → pr_to_development.yml executa (DUPLICADO)
Push no PR → pr_to_development.yml executa (TRIPLICADO)
```

**Depois:**
```
Push em feature (sem PR) → test_on_push.yml executa
Push em feature (com PR aberto) → test_on_push.yml SKIP ⏭️
Abrir PR → pr_to_development.yml executa (ÚNICA VEZ)
Push no PR → pr_to_development.yml executa (ATUALIZAÇÃO)
```

**Economia:** ~66% menos execuções de testes!

### 🔒 Camadas de Segurança Implementadas

#### 1. SAST - Static Application Security Testing

**Bandit (Python Security Scanner)**
- Detecta vulnerabilidades comuns no código Python
- Exemplos: `eval()`, `exec()`, SQL injection, hardcoded passwords, weak cryptography
- Configuração: `.bandit` suprime falsos positivos (B101, B311, B324)
- Status: ⚠️ Warning (não bloqueia PR)

**Semgrep (Advanced Static Analysis)**
- Análise semântica avançada
- Exemplos: Code injection, insecure deserialization, path traversal, XSS
- Status: ⚠️ Warning (não bloqueia PR)

#### 2. Dependency Scanning

**Safety (Python Package Vulnerabilities)**
- Verifica vulnerabilidades conhecidas em dependências
- Database: CVE (Common Vulnerabilities and Exposures)
- Status: ⚠️ Warning (não bloqueia PR)

**Trivy (Comprehensive Scanner)**
- Scanner multi-propósito: vulnerabilidades, misconfigurações, secrets, licenses
- Upload SARIF para GitHub Security tab
- Status: ⚠️ Warning (não bloqueia PR)

#### 3. CodeQL (GitHub Advanced Security)

- Análise semântica profunda (gratuito para repos públicos)
- Queries: security-extended + security-and-quality
- Taint analysis, data flow analysis, control flow analysis, CWE detection
- Status: ⚠️ Warning (não bloqueia PR)

#### 4. Coverage Enforcement

- **Mínimo:** 60% de cobertura de testes
- **Bloqueio:** PR não pode ser mergeado se coverage < 60%
- **Status:** ❌ Blocker (falha CI se não atender)

### 🚨 Política de Segurança

**❌ Blockers (PR não pode ser mergeado):**
1. Testes falhando
2. Coverage < 60%
3. Validação de source branch falhar

**⚠️ Warnings (Review necessário, mas não bloqueia):**
1. Vulnerabilidades detectadas pelo Bandit
2. Issues encontrados pelo Semgrep
3. Vulnerabilidades em dependências (Safety/Trivy)
4. Findings do CodeQL

**Razão:** Nem todo "finding" é um problema real. Falsos positivos são comuns, especialmente em bibliotecas de geração de dados de teste.

### 🔧 Fix: Poetry Export Error

**Problema:** `The requested command export does not exist.`

**Solução:** Desde Poetry 1.2+, o comando `export` foi movido para plugin separado.

```yaml
- name: Install Poetry Export Plugin
  run: poetry self add poetry-plugin-export

- name: Export requirements
  run: poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### 🛡️ SQL Injection Protection

Implementado validação de input em handlers de banco de dados:

```python
# Valida table names (apenas alphanumeric + underscore)
if not table_name.replace('_', '').isalnum():
    raise ValueError(f"Invalid table name: {table_name}")
```

Arquivos protegidos:
- `rand_engine/integrations/duckdb_handler.py`
- `rand_engine/integrations/sqlite_handler.py`

### 📊 Arquitetura de Segurança

```
┌─────────────────────────────────────────────────────────┐
│               PR para Development Branch                 │
└─────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┬──────────────┐
        ↓                ↓                ↓              ↓
┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────┐
│   SAST       │  │ Dependency   │  │ CodeQL   │  │  Tests   │
│  Analysis    │  │   Scanning   │  │ Analysis │  │ + Cov    │
│              │  │              │  │          │  │  ≥60%    │
│ • Bandit     │  │ • Safety     │  │ • Taint  │  │          │
│ • Semgrep    │  │ • Trivy      │  │ • Data   │  │ • Pytest │
│              │  │              │  │   Flow   │  │ • Cov    │
│ Status: ⚠️   │  │ Status: ⚠️   │  │ Status:⚠️│  │Status: ❌│
│ (Warning)    │  │ (Warning)    │  │(Warning) │  │(Blocker) │
└──────────────┘  └──────────────┘  └──────────┘  └──────────┘
        │                │                │              │
        └────────────────┴────────────────┴──────────────┘
                         │
                         ↓
              ✅ READY TO MERGE (if tests pass)
              ⚠️  REVIEW SECURITY FINDINGS
```

### 🔧 Ferramentas e Custos

| Ferramenta | Tipo | Custo | Onde Executa |
|------------|------|-------|--------------|
| **Bandit** | SAST Python | Grátis | GitHub Actions |
| **Semgrep** | SAST Universal | Grátis (Community) | GitHub Actions |
| **Safety** | Dependency | Grátis (DB básico) | GitHub Actions |
| **Trivy** | Multi-scanner | Grátis (Open Source) | GitHub Actions |
| **CodeQL** | Advanced SAST | Grátis (repos públicos) | GitHub Actions |
| **pytest-cov** | Coverage | Grátis | GitHub Actions |
| **Codecov** | Coverage Viz | Grátis (repos públicos) | Cloud |

**Total:** R$ 0,00 para repositórios públicos! 🎉

---

## 📊 Visual Summaries

### Todos os Workflows têm Summaries Visuais

#### 1. `test_on_push.yml` - 3 Cenários

**Cenário A: Tests Executados com Sucesso ✅**
```markdown
# 🧪 Test Results - Feature Branch
- Branch info table
- Test execution status (all ✅)
- Next steps: Create PR commands and links
```

**Cenário B: Tests Executados com Falha ❌**
```markdown
# 🧪 Test Results - Feature Branch
- Branch info table
- Test execution status (with ❌)
- Debugging steps and local test commands
```

**Cenário C: Tests Pulados (PR existe) ⏭️**
```markdown
# 🧪 Test Results - Feature Branch
- Branch info table
- Explanation: Tests run on PR workflow
- Link to PR checks
```

#### 2. `pr_to_development.yml` - Security + Tests

```markdown
# 🔍 Security & Test Validation
- Security analysis results (4 tools)
- Test results matrix (Python 3.10, 3.11, 3.12)
- Coverage status
- Links to artifacts
```

#### 3. `auto_tag_publish_development.yml` - RC Deployment

```markdown
# 📦 RC Deployment Complete
- Version info (e.g., 0.5.5rc1)
- Pipeline status table (all 7 jobs)
- PyPI pre-release link
- GitHub Pre-Release link
- Installation commands
- Testing instructions
```

#### 4. `auto_tag_publish_master.yml` - Production Deployment

**Success Scenario:**
```markdown
# 🎉 Production Deployment Complete!
- Version info with RC promotion details
- Pipeline status table (all 6 jobs)
- Direct links to PyPI and GitHub Release
- Installation: pip install rand-engine==X.Y.Z
- Testing instructions
- Next steps suggestions
```

**Skip Scenario (tag exists):**
```markdown
# ⏭️ Deployment Skipped
- Tag already exists explanation
- Links to existing release
- Guidance on creating new version
```

### 🎨 Benefícios dos Summaries

1. **Visibilidade Total**: Status de cada job em formato tabela
2. **Documentação Automática**: Comandos prontos para copiar
3. **Debugging Facilitado**: Mensagens claras sobre o que fazer
4. **Profissionalismo**: UX consistente e visual atraente
5. **Orientação Clara**: Próximos passos baseados no contexto

---


## 🔄 Workflows Implementados

### 1. `test_on_push.yml` - Testes em Feature Branches

**Trigger:** Push em qualquer branch **exceto** `master` e `development`

**Jobs:**
1. **check_pr**: Detecta se PR existe (usando GitHub CLI)
2. **test**: Testes Python 3.10, 3.11, 3.12 (apenas se não houver PR)
3. **summary**: Visual report com 3 cenários (success/failure/skip)

**Função:**
- Testes automáticos antes de criar PRs
- Skip inteligente se PR já existe (evita duplicação)
- Cobertura de testes
- Orientação sobre próximos passos

**Uso:** Desenvolvimento local em feature branches

---

### 2. `pr_to_development.yml` - Validação de PR + Security

**Trigger:** Pull Request para `development`

**Jobs:**
1. **validate_source**: Source branch ≠ master
2. **security_sast**: Bandit + Semgrep (⚠️ warning)
3. **security_dependencies**: Safety + Trivy (⚠️ warning)
4. **security_codeql**: GitHub Advanced Security (⚠️ warning)
5. **test**: Python 3.10, 3.11, 3.12 + Coverage ≥60% (❌ blocker)
6. **summary**: Status de todos os checks

**Validações:**
- ✅ Análise de segurança em 5 ferramentas
- ✅ Coverage enforcement (mínimo 60%)
- ✅ Poetry export plugin instalado automaticamente
- ✅ Upload SARIF para GitHub Security tab

**Uso:** Validação antes de merge em `development`

---

### 3. `pr_to_master.yml` - Validação Strict

**Trigger:** Pull Request para `master`

**Validações:**
- ✅ Source branch **deve** ser `development` (apenas!)
- ✅ Testes completos em Python 3.10, 3.11, 3.12
- ✅ Coverage upload para Codecov

**Uso:** Validação antes de release estável

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

