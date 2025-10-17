# 🔐 Configuração PyPI Trusted Publishing

Este guia explica como configurar o **PyPI Trusted Publishing (OIDC)** para os novos workflows de CI/CD.

## ❌ Erro Atual

```
`invalid-publisher`: valid token, but no corresponding publisher 
(Publisher with matching claims was not found)
```

**Causa:** O PyPI está configurado para o workflow antigo, mas agora os nomes mudaram.

---

## ✅ Solução: Atualizar Trusted Publishers no PyPI

### 1. Acessar PyPI Publishing Settings

1. Acesse: https://pypi.org/manage/project/rand-engine/settings/publishing/
2. Faça login com sua conta que tem permissões de maintainer

---

### 2. Remover Publishers Antigos (se existirem)

Se houver publishers configurados com os workflows antigos, remova-os:
- `test_and_publish_development.yml`
- `test_and_publish_production.yml`

---

### 3. Adicionar Publisher para Development (Pre-Release)

Clique em **"Add a new publisher"** e configure:

| Campo | Valor |
|-------|-------|
| **PyPI Project Name** | `rand-engine` |
| **Owner** | `marcoaureliomenezes` |
| **Repository name** | `rand_engine` |
| **Workflow name** | `auto_tag_publish_development.yml` |
| **Environment name** | *(deixe em branco)* |

**⚠️ IMPORTANTE:** O campo que importa é o **Workflow name**.

---

### 4. Adicionar Publisher para Master (Stable Release)

Clique novamente em **"Add a new publisher"** e configure:

| Campo | Valor |
|-------|-------|
| **PyPI Project Name** | `rand-engine` |
| **Owner** | `marcoaureliomenezes` |
| **Repository name** | `rand_engine` |
| **Workflow name** | `auto_tag_publish_master.yml` |
| **Environment name** | *(deixe em branco)* |

---

## 📋 Resumo das Configurações

Você deve ter **2 trusted publishers** configurados:

### Publisher 1: Development (Pre-Release)
```
Owner: marcoaureliomenezes
Repository: rand_engine
Workflow: auto_tag_publish_development.yml
Environment: (empty)
```

### Publisher 2: Master (Stable)
```
Owner: marcoaureliomenezes
Repository: rand_engine
Workflow: auto_tag_publish_master.yml
Environment: (empty)
```

---

## 🧪 Testar a Configuração

Após configurar, teste fazendo um merge em `development`:

```bash
# 1. Certifique-se de estar na branch development
git checkout development

# 2. Faça um push (se houver mudanças)
git push origin development

# 3. O workflow será disparado automaticamente
```

O workflow irá:
1. Extrair versão do `pyproject.toml`
2. Criar tag automaticamente (ex: `0.4.6a1`)
3. Buildar o pacote
4. Publicar no PyPI usando OIDC (sem senha!)
5. Criar GitHub Pre-Release

---

## 🔍 Verificar Claims do OIDC

Se ainda houver erro, verifique os claims no log do workflow:

```yaml
* `repository`: `marcoaureliomenezes/rand_engine`
* `workflow_ref`: `marcoaureliomenezes/rand_engine/.github/workflows/auto_tag_publish_development.yml@refs/heads/development`
```

O **workflow_ref** deve bater **exatamente** com o que está configurado no PyPI.

---

## 🆘 Troubleshooting

### Erro: "valid token, but no corresponding publisher"
**Solução:** Verifique se o **workflow name** no PyPI está correto:
- ✅ `auto_tag_publish_development.yml`
- ❌ `test_and_publish_development.yml` (antigo)

### Erro: "environment mismatch"
**Solução:** Se você configurou um **environment** no PyPI (ex: "development"), adicione no workflow:

```yaml
publish_pypi:
  environment:
    name: development  # Adicione esta seção
```

Mas **recomendo não usar environments** para simplificar.

---

## 📚 Referências

- [PyPI Trusted Publishing Guide](https://docs.pypi.org/trusted-publishers/)
- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [PyPA gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)

---

## ✨ Vantagens do Trusted Publishing

- ✅ Sem necessidade de API tokens ou senhas
- ✅ Segurança baseada em OIDC (OpenID Connect)
- ✅ Configuração por workflow específico
- ✅ Audit trail completo no GitHub
- ✅ Zero secrets para gerenciar

---

## 📝 Checklist

- [ ] Acessei https://pypi.org/manage/project/rand-engine/settings/publishing/
- [ ] Removi publishers antigos (se existentes)
- [ ] Adicionei publisher para `auto_tag_publish_development.yml`
- [ ] Adicionei publisher para `auto_tag_publish_master.yml`
- [ ] Testei fazendo push em `development`
- [ ] Verifiquei publicação no PyPI
- [ ] Testei instalação: `pip install rand-engine==0.4.6a1`

---

**🎯 Após seguir este guia, seus workflows devem funcionar automaticamente!**
