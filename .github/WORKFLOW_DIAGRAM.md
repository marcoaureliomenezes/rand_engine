# 🔄 Fluxo Completo de CI/CD - Rand Engine

## 📊 Diagrama do Fluxo

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FEATURE BRANCH                               │
│                     (feature/nova-feature)                          │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ git push
                                 ↓
                    ┌────────────────────────┐
                    │   test_on_push.yml     │
                    │  Testes automáticos    │
                    │  Python 3.10-3.12      │
                    └────────────────────────┘
                                 │
                                 │ Criar PR para development
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                              PULL REQUEST                            │
│                         → development                                │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ↓
                    ┌────────────────────────┐
                    │ pr_to_development.yml  │
                    │  ✓ Source ≠ master     │
                    │  ✓ Testes completos    │
                    │  ✓ Coverage Codecov    │
                    └────────────────────────┘
                                 │
                                 │ ✅ MERGE PR
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        DEVELOPMENT BRANCH                            │
│                          (protected)                                 │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ PR merged (automatic trigger)
                                 ↓
              ┌──────────────────────────────────────┐
              │ auto_tag_publish_development.yml     │
              │  1. Extrai versão (pyproject.toml)  │
              │  2. Determina próxima tag            │
              │     - 0.5.5a1, 0.5.5a2, ...         │
              │     - 0.5.5b1, 0.5.5b2, ...         │
              │     - 0.5.5rc1, 0.5.5rc2, ...       │
              │  3. Cria tag automaticamente         │
              │  4. Build com Poetry                 │
              │  5. Publica PyPI (pre-release)      │
              │  6. GitHub Pre-Release               │
              └──────────────────────────────────────┘
                                 │
                                 │ Quando pronto para stable
                                 │ Criar PR para master
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                              PULL REQUEST                            │
│                            → master                                  │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ↓
                    ┌────────────────────────┐
                    │   pr_to_master.yml     │
                    │  ✓ Source = development│
                    │  ✓ Testes completos    │
                    │  ✓ Coverage Codecov    │
                    └────────────────────────┘
                                 │
                                 │ ✅ MERGE PR
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                          MASTER BRANCH                               │
│                          (protected)                                 │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ PR merged (automatic trigger)
                                 ↓
              ┌──────────────────────────────────────┐
              │   auto_tag_publish_master.yml        │
              │  1. Extrai versão (pyproject.toml)  │
              │  2. Verifica se tag existe           │
              │  3. Cria tag estável (0.5.5)        │
              │  4. Build com Poetry                 │
              │  5. Publica PyPI (stable)           │
              │  6. GitHub Release                   │
              │  7. Changelog automático             │
              └──────────────────────────────────────┘
                                 │
                                 ↓
                         ✅ PRODUCTION READY
```

## 🎯 Pontos-Chave

### ✅ Automação Completa
- **Nenhuma tag manual** - Todas criadas automaticamente
- **Trigger por merge** - Não em todo push
- **Incremento inteligente** - a1→a2, b1→b2, rc1→rc2
- **Validação de formato** - Apenas tags válidas são consideradas

### 🔐 Segurança
- **Branches protegidas** - master e development
- **PRs obrigatórios** - Não há push direto
- **Validação de origem** - development→master, qualquer→development
- **Testes automáticos** - Em todas as etapas

### 📦 Versionamento
- **pyproject.toml** - Fonte única de verdade
- **Semver compliance** - X.Y.Z[{a|b|rc}N]
- **Tags válidas** - Regex estrito
- **Tags inválidas** - Ignoradas automaticamente

### 🚀 Deploy
- **PyPI Trusted Publishing** - Sem tokens ou senhas
- **Pre-release** - Automático após merge em development
- **Stable** - Automático após merge em master
- **GitHub Releases** - Criados automaticamente

## 📝 Workflow Passo a Passo

### Fase 1: Desenvolvimento
```bash
# 1. Criar feature branch
git checkout -b feature/nova-funcionalidade

# 2. Desenvolver código
# ... editar arquivos ...

# 3. Commit e push
git add .
git commit -m "feat: adiciona nova funcionalidade"
git push origin feature/nova-funcionalidade

# → Resultado: test_on_push.yml executa automaticamente
```

### Fase 2: PR para Development
```bash
# 4. Criar PR no GitHub: feature/nova-funcionalidade → development

# → Resultado: pr_to_development.yml valida PR
#   - Verifica que source ≠ master
#   - Executa testes Python 3.10, 3.11, 3.12
#   - Upload de coverage para Codecov

# 5. Revisar PR e aprovar

# 6. MERGE PR (no GitHub)

# → Resultado: auto_tag_publish_development.yml
#   - Tag 0.5.5a1 criada automaticamente
#   - Publicado no PyPI como pre-release
#   - GitHub Pre-Release criado
```

### Fase 3: Release Estável
```bash
# 7. Quando pronto para produção, criar PR: development → master

# → Resultado: pr_to_master.yml valida PR
#   - Verifica que source = development (APENAS)
#   - Executa testes completos
#   - Upload de coverage

# 8. Revisar PR e aprovar

# 9. MERGE PR (no GitHub)

# → Resultado: auto_tag_publish_master.yml
#   - Tag 0.5.5 criada automaticamente
#   - Publicado no PyPI como stable
#   - GitHub Release criado com changelog
```

## 🛠️ Gerenciamento de Versões

### Como Incrementar Versão

```bash
# 1. Editar pyproject.toml
version = "0.5.6"  # Nova versão

# 2. Commit
git add pyproject.toml
git commit -m "chore: bump version to 0.5.6"

# 3. Push e criar PR
git push origin feature/bump-version
# Criar PR → development

# 4. Após merge, workflow cria automaticamente:
# - 0.5.6a1 (primeiro alpha)
```

### Evolução de Pre-Releases

```
Versão no pyproject.toml: 0.5.6

Sequência automática de tags:
- PR 1 mergeado → 0.5.6a1
- PR 2 mergeado → 0.5.6a2
- PR 3 mergeado → 0.5.6a3
- (evoluir manualmente para beta se necessário)
- PR N mergeado → 0.5.6b1
- PR N+1 mergeado → 0.5.6b2
- (evoluir para RC)
- PR M mergeado → 0.5.6rc1
- PR M+1 mergeado → 0.5.6rc2
- (merge em master)
- PR final → 0.5.6 (stable)
```

**⚠️ Nota:** A evolução alpha→beta→rc não é automática. Você controla isso decidindo quando fazer o próximo merge.

## 🔍 Troubleshooting

### Tags não sendo criadas
**Problema:** Workflow executa mas tag não é criada

**Soluções:**
1. Verificar se PR foi **mergeado** (não apenas fechado)
2. Verificar logs do workflow para erros
3. Executar `.github/test_tag_logic.sh` localmente

### Publicação PyPI falhando
**Problema:** `invalid-publisher` error

**Solução:** Configurar Trusted Publishing no PyPI
- Ver: `.github/PYPI_TRUSTED_PUBLISHING_SETUP.md`

### Tags com formato inválido
**Problema:** Tags antigas com formato errado (ex: 0.5.5rc1a1)

**Solução:** Tags inválidas são **ignoradas automaticamente**
- Formato válido: `X.Y.Za[0-9]+`, `X.Y.Zb[0-9]+`, `X.Y.Zrc[0-9]+`
- Formato inválido: qualquer outro formato

## 📚 Referências Rápidas

- **Workflows:** `.github/workflows/`
- **Documentação:** `.github/workflows/README.md`
- **Setup PyPI:** `.github/PYPI_TRUSTED_PUBLISHING_SETUP.md`
- **Teste local:** `.github/test_tag_logic.sh`
- **Diagnóstico:** `.github/check_pypi_config.sh`

---

**🎯 Resumo: PRs mergeados → Tags automáticas → Publicação automática → Zero intervenção manual!**
