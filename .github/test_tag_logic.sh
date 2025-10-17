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
echo "3️⃣  Determinando próxima tag de pre-release..."

# Get all existing tags for this version with valid pre-release format
# Valid formats: X.Y.Za[0-9]+, X.Y.Zb[0-9]+, X.Y.Zrc[0-9]+
ALL_TAGS=$(git tag -l "${VERSION}*" || echo "")

# Filter only valid pre-release tags
ALPHA_TAGS=$(echo "$ALL_TAGS" | grep -E "^${VERSION}a[0-9]+$" || echo "")
BETA_TAGS=$(echo "$ALL_TAGS" | grep -E "^${VERSION}b[0-9]+$" || echo "")
RC_TAGS=$(echo "$ALL_TAGS" | grep -E "^${VERSION}rc[0-9]+$" || echo "")

echo "📋 Valid pre-release tags found:"
[ -n "$ALPHA_TAGS" ] && echo "  Alpha: $(echo $ALPHA_TAGS | tr '\n' ' ')"
[ -n "$BETA_TAGS" ] && echo "  Beta: $(echo $BETA_TAGS | tr '\n' ' ')"
[ -n "$RC_TAGS" ] && echo "  RC: $(echo $RC_TAGS | tr '\n' ' ')"
[ -z "$ALPHA_TAGS" ] && [ -z "$BETA_TAGS" ] && [ -z "$RC_TAGS" ] && echo "  (none)"

# Determine next pre-release type and number
# Priority: alpha (a) -> beta (b) -> release candidate (rc)

if [ -n "$RC_TAGS" ]; then
    # If rc exists, increment rc
    LATEST_RC=$(echo "$RC_TAGS" | sort -V | tail -1)
    RC_NUM=$(echo "$LATEST_RC" | sed -E "s/^${VERSION}rc([0-9]+)$/\1/")
    NEXT_RC=$((RC_NUM + 1))
    TAG="${VERSION}rc${NEXT_RC}"
    PRERELEASE_TYPE="rc"
elif [ -n "$BETA_TAGS" ]; then
    # If beta exists but no rc, increment beta
    LATEST_BETA=$(echo "$BETA_TAGS" | sort -V | tail -1)
    BETA_NUM=$(echo "$LATEST_BETA" | sed -E "s/^${VERSION}b([0-9]+)$/\1/")
    NEXT_BETA=$((BETA_NUM + 1))
    TAG="${VERSION}b${NEXT_BETA}"
    PRERELEASE_TYPE="beta"
elif [ -n "$ALPHA_TAGS" ]; then
    # If alpha exists, increment alpha
    LATEST_ALPHA=$(echo "$ALPHA_TAGS" | sort -V | tail -1)
    ALPHA_NUM=$(echo "$LATEST_ALPHA" | sed -E "s/^${VERSION}a([0-9]+)$/\1/")
    NEXT_ALPHA=$((ALPHA_NUM + 1))
    TAG="${VERSION}a${NEXT_ALPHA}"
    PRERELEASE_TYPE="alpha"
else
    # No pre-release tags, start with alpha 1
    TAG="${VERSION}a1"
    PRERELEASE_TYPE="alpha"
fi

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
