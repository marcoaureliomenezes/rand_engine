#!/bin/bash

# Script para diagnosticar configuração de Trusted Publishing
# Uso: ./check_pypi_config.sh

set -e

echo "🔍 Diagnóstico de Configuração PyPI Trusted Publishing"
echo "======================================================"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Informações do projeto
OWNER="marcoaureliomenezes"
REPO="rand_engine"
PACKAGE="rand-engine"

echo "📦 Projeto: $PACKAGE"
echo "👤 Owner: $OWNER"
echo "📁 Repository: $REPO"
echo ""

# Verificar workflows existentes
echo "📄 Workflows Configurados:"
echo "=========================="
if [ -d ".github/workflows" ]; then
    ls -1 .github/workflows/*.yml 2>/dev/null | while read file; do
        basename "$file"
    done
else
    echo -e "${RED}❌ Diretório .github/workflows não encontrado${NC}"
    exit 1
fi
echo ""

# Verificar workflows de publish
echo "🚀 Workflows de Publicação:"
echo "============================"
if [ -f ".github/workflows/auto_tag_publish_development.yml" ]; then
    echo -e "${GREEN}✅ auto_tag_publish_development.yml${NC}"
else
    echo -e "${RED}❌ auto_tag_publish_development.yml não encontrado${NC}"
fi

if [ -f ".github/workflows/auto_tag_publish_master.yml" ]; then
    echo -e "${GREEN}✅ auto_tag_publish_master.yml${NC}"
else
    echo -e "${RED}❌ auto_tag_publish_master.yml não encontrado${NC}"
fi
echo ""

# Verificar pyproject.toml
echo "📋 Versão Atual:"
echo "================"
if [ -f "pyproject.toml" ]; then
    VERSION=$(grep "^version = " pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    echo -e "${GREEN}✅ Versão no pyproject.toml: $VERSION${NC}"
else
    echo -e "${RED}❌ pyproject.toml não encontrado${NC}"
fi
echo ""

# Verificar últimas tags
echo "🏷️  Últimas Tags:"
echo "================="
git tag -l --sort=-version:refname | head -5 || echo "Nenhuma tag encontrada"
echo ""

# Verificar branch atual
echo "🌿 Branch Atual:"
echo "================"
BRANCH=$(git branch --show-current)
echo "Branch: $BRANCH"
if [ "$BRANCH" = "development" ]; then
    echo -e "${GREEN}✅ Você está na branch development${NC}"
elif [ "$BRANCH" = "master" ]; then
    echo -e "${YELLOW}⚠️  Você está na branch master${NC}"
else
    echo -e "${YELLOW}⚠️  Você está em uma branch feature: $BRANCH${NC}"
fi
echo ""

# Instruções de configuração PyPI
echo "🔐 Configuração Necessária no PyPI:"
echo "===================================="
echo ""
echo "1. Acesse: https://pypi.org/manage/project/$PACKAGE/settings/publishing/"
echo ""
echo "2. Adicione 2 Trusted Publishers:"
echo ""
echo "   Publisher 1 (Development):"
echo "   -------------------------"
echo "   Owner: $OWNER"
echo "   Repository: $REPO"
echo "   Workflow: auto_tag_publish_development.yml"
echo "   Environment: (deixe em branco)"
echo ""
echo "   Publisher 2 (Master):"
echo "   ---------------------"
echo "   Owner: $OWNER"
echo "   Repository: $REPO"
echo "   Workflow: auto_tag_publish_master.yml"
echo "   Environment: (deixe em branco)"
echo ""

# Verificar se há workflows antigos
echo "🗑️  Workflows Antigos:"
echo "====================="
if [ -d "z_ignore/old_workflows" ]; then
    OLD_COUNT=$(ls -1 z_ignore/old_workflows/*.yml 2>/dev/null | wc -l)
    echo -e "${YELLOW}⚠️  $OLD_COUNT workflows antigos encontrados em z_ignore/old_workflows/${NC}"
    echo "   (Estes workflows não são mais usados)"
else
    echo -e "${GREEN}✅ Nenhum workflow antigo encontrado${NC}"
fi
echo ""

# Próximos passos
echo "📝 Próximos Passos:"
echo "==================="
echo ""
echo "1. Configure os Trusted Publishers no PyPI (veja acima)"
echo "2. Faça um commit e push em 'development' para testar"
echo "3. Verifique os logs do GitHub Actions"
echo "4. Confirme publicação em: https://pypi.org/project/$PACKAGE/"
echo ""
echo "📚 Documentação completa: .github/PYPI_TRUSTED_PUBLISHING_SETUP.md"
echo ""
echo "✨ Diagnóstico completo!"
