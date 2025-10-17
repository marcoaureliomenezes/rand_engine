#!/bin/bash

# Script para testar localmente a lógica de tagging do workflow
# Uso: ./test_tag_logic.sh

set -e

echo "🧪 Teste da Lógica de Tagging do Workflow"
echo "=========================================="
echo ""

# Extrair versão do pyproject.toml
echo "1️⃣  Extraindo versão do pyproject.toml..."
VERSION=$(grep -E '^version = "[0-9]+\.[0-9]+\.[0-9]+"' pyproject.toml | sed -E 's/version = "(.*)"/\1/')

if [ -z "$VERSION" ]; then
    echo "❌ Falha ao extrair versão!"
    exit 1
fi

echo "✅ Versão extraída: $VERSION"
echo ""

# Obter tags existentes
echo "2️⃣  Verificando tags existentes para versão $VERSION..."
EXISTING_TAGS=$(git tag -l "${VERSION}*" || echo "")

if [ -n "$EXISTING_TAGS" ]; then
    echo "📋 Tags encontradas:"
    echo "$EXISTING_TAGS"
else
    echo "📋 Nenhuma tag encontrada para versão $VERSION"
fi
echo ""

# Determinar próxima tag
echo "3️⃣  Determinando próxima tag RC (Release Candidate)..."

# Get all RC tags for this version (format: X.Y.Zrc[0-9]+)
RC_TAGS=$(git tag -l "${VERSION}rc*" | grep -E "^${VERSION}rc[0-9]+$" || echo "")

if [ -n "$RC_TAGS" ]; then
    echo "📋 RC tags encontradas:"
    echo "$RC_TAGS"
    
    # Get latest RC number
    LATEST_RC=$(echo "$RC_TAGS" | sort -V | tail -1)
    RC_NUM=$(echo "$LATEST_RC" | sed -E "s/^${VERSION}rc([0-9]+)$/\1/")
    NEXT_RC=$((RC_NUM + 1))
    TAG="${VERSION}rc${NEXT_RC}"
    echo "📈 Incrementando: $LATEST_RC → $TAG"
else
    echo "📋 Nenhuma RC tag encontrada, começando com rc1"
    TAG="${VERSION}rc1"
fi

PRERELEASE_TYPE="rc"

if [ -z "$TAG" ]; then
    echo "❌ Falha ao determinar TAG!"
    exit 1
fi

echo "✅ Próxima tag: $TAG"
echo "✅ Tipo: $PRERELEASE_TYPE"
echo ""

# Verificar se tag já existe
echo "4️⃣  Verificando se tag $TAG já existe..."
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "⚠️  Tag $TAG já existe!"
    echo "   Para testar novamente, remova a tag: git tag -d $TAG"
else
    echo "✅ Tag $TAG não existe ainda"
    echo ""
    echo "🎯 Resultado Final:"
    echo "=================="
    echo "Versão: $VERSION"
    echo "Nova Tag: $TAG"
    echo "Tipo: $PRERELEASE_TYPE"
    echo ""
    echo "📝 Para criar a tag manualmente:"
    echo "   git tag -a \"$TAG\" -m \"Pre-release $TAG\""
    echo "   git push origin \"$TAG\""
fi
