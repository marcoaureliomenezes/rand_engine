# CI/CD Workflows - Rand Engine

Este diretório contém os workflows do GitHub Actions para automação completa de CI/CD do projeto rand-engine.

## 📋 Estrutura de Branches

### Branches Protegidas
- **`master`**: Versões estáveis (releases oficiais)
- **`development`**: Versões em desenvolvimento (pre-releases)

### Branches Desprotegidas
- Qualquer outra branch (features, bugfixes, etc.)

## 🔄 Workflows Implementados

### 1. `test_on_push.yml` - Testes em Pushes
**Trigger:** Push em qualquer branch **exceto** `master` e `development`

**Função:**
- Executa testes automaticamente em branches de desenvolvimento
- Valida código antes de criar PRs
- Testa em Python 3.10, 3.11, 3.12

**Quando usar:**
- Desenvolvimento local em feature branches
- Antes de abrir PRs

---

### 2. `pr_to_development.yml` - Validação de PR para Development
**Trigger:** Pull Request para `development`

**Validações:**
- ✅ Branch de origem **não** pode ser `master`
- ✅ Testes completos em Python 3.10, 3.11, 3.12
- ✅ Cobertura de código (upload para Codecov)

**Quando usar:**
- Ao criar PR de qualquer branch (feature, bugfix) para `development`

---

### 3. `pr_to_master.yml` - Validação de PR para Master
**Trigger:** Pull Request para `master`

**Validações:**
- ✅ Branch de origem **deve** ser `development` (apenas!)
- ✅ Testes completos em Python 3.10, 3.11, 3.12
- ✅ Cobertura de código (upload para Codecov)

**Quando usar:**
- Ao promover versão de `development` para `master`

---

### 4. `auto_tag_publish_development.yml` - Auto Tag e Publish (Pre-Release)
**Trigger:** Push/Merge em `development`

**Fluxo:**
1. **Extrai versão** do `pyproject.toml` (ex: `0.4.6`)
2. **Determina tipo de pre-release:**
   - Se não existem tags: cria `0.4.6a1` (alpha 1)
   - Se existe `0.4.6a1`: cria `0.4.6a2` (alpha 2)
   - Se existe alpha: pode evoluir para `0.4.6b1` (beta 1)
   - Se existe beta: pode evoluir para `0.4.6rc1` (release candidate 1)
3. **Cria e pusha tag automaticamente**
4. **Builda pacote** com Poetry
5. **Publica no PyPI** como pre-release
6. **Cria GitHub Pre-Release** com informações detalhadas

**Exemplo de sequência de tags:**
```
0.4.6a1 → 0.4.6a2 → 0.4.6a3 → 0.4.6b1 → 0.4.6b2 → 0.4.6rc1 → 0.4.6rc2
```

**Quando usar:**
- Automaticamente após merge de PRs em `development`

---

### 5. `auto_tag_publish_master.yml` - Auto Tag e Publish (Stable)
**Trigger:** Push/Merge em `master`

**Fluxo:**
1. **Extrai versão** do `pyproject.toml` (ex: `0.4.6`)
2. **Verifica se tag já existe** (evita republicação)
3. **Cria e pusha tag estável** (sem sufixos: `0.4.6`)
4. **Builda pacote** com Poetry
5. **Publica no PyPI** como versão estável
6. **Cria GitHub Release** com changelog desde último pre-release

**Quando usar:**
- Automaticamente após merge de `development` em `master`

---

## 🎯 Fluxo de Trabalho Completo

### Cenário 1: Nova Feature
```bash
# 1. Criar branch de feature
git checkout -b feature/minha-feature

# 2. Desenvolver e fazer commit
git add .
git commit -m "feat: adiciona nova feature"
git push origin feature/minha-feature
# → Trigger: test_on_push.yml (testes automáticos)

# 3. Criar PR para development
# → Trigger: pr_to_development.yml (validação completa)

# 4. Merge do PR em development
# → Trigger: auto_tag_publish_development.yml
# → Resultado: Tag 0.4.6a1 criada, publicada no PyPI
```

### Cenário 2: Release Estável
```bash
# 1. Criar PR de development para master
# → Trigger: pr_to_master.yml (validação strict)

# 2. Merge do PR em master
# → Trigger: auto_tag_publish_master.yml
# → Resultado: Tag 0.4.6 criada, publicada no PyPI como stable
```

### Cenário 3: Múltiplas Pre-Releases
```bash
# Merge 1 em development → 0.4.6a1
# Merge 2 em development → 0.4.6a2
# Merge 3 em development → 0.4.6a3
# ... até estar pronto para release estável
# Merge em master → 0.4.6
```

---

## 🔐 Secrets Necessários

### CODECOV_TOKEN
- **Onde:** Repository Secrets
- **Uso:** Upload de cobertura de testes
- **Como obter:** https://codecov.io

### PyPI Trusted Publishing (OIDC)
- **Configuração:** https://pypi.org/manage/account/publishing/
- **Publisher:** `github.com/<owner>/<repo>`
- **Workflow:** `auto_tag_publish_development.yml` e `auto_tag_publish_master.yml`
- **Environment:** (opcional, usar se configurado)

---

## 📊 Versionamento Semântico

### Formato
```
X.Y.Z[{a|b|rc}N]
```

- **X**: Major version (breaking changes)
- **Y**: Minor version (new features)
- **Z**: Patch version (bugfixes)
- **a**: Alpha (early testing)
- **b**: Beta (feature complete, testing)
- **rc**: Release Candidate (production ready, final testing)
- **N**: Incremental number (1, 2, 3...)

### Exemplos
```
0.4.6      → Stable release
0.4.6a1    → Alpha 1
0.4.6a2    → Alpha 2
0.4.6b1    → Beta 1
0.4.6rc1   → Release Candidate 1
```

---

## 🛠️ Gerenciamento de Versões

### Como Incrementar Versão

1. **Editar `pyproject.toml`:**
```toml
[tool.poetry]
version = "0.4.7"  # Nova versão
```

2. **Commit e push:**
```bash
git add pyproject.toml
git commit -m "chore: bump version to 0.4.7"
git push
```

3. **Workflow automaticamente:**
   - Em `development`: Cria tags `0.4.7a1`, `0.4.7a2`, etc.
   - Em `master`: Cria tag `0.4.7` estável

### ⚠️ IMPORTANTE
- **NUNCA** crie tags manualmente
- **SEMPRE** atualize versão no `pyproject.toml`
- **WORKFLOWS** gerenciam tags automaticamente

---

## 🧪 Testando Workflows Localmente

### Usando `act` (GitHub Actions local)
```bash
# Instalar act
brew install act  # macOS
# ou
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Testar workflow de testes
act push -W .github/workflows/test_on_push.yml

# Testar PR validation
act pull_request -W .github/workflows/pr_to_development.yml
```

---

## 📚 Referências

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [Semantic Versioning](https://semver.org/)
- [Codecov Documentation](https://docs.codecov.com/)

---

## 🗂️ Workflows Antigos

Workflows anteriores foram movidos para `/old_workflows/` para referência histórica.
