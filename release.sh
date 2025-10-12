#!/bin/bash
#
# Script helper para fazer releases do Rand Engine
# Uso: ./release.sh <version> [--rc|--beta|--alpha]
#

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções helper
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar argumentos
if [ $# -lt 1 ]; then
    print_error "Usage: ./release.sh <version> [--rc|--beta|--alpha]"
    echo "Examples:"
    echo "  ./release.sh 0.5.0           # Production release"
    echo "  ./release.sh 0.5.0 --rc      # Release candidate"
    echo "  ./release.sh 0.5.0 --beta    # Beta release"
    echo "  ./release.sh 0.5.0 --alpha   # Alpha release"
    exit 1
fi

VERSION=$1
SUFFIX=""

if [ $# -eq 2 ]; then
    case $2 in
        --rc)
            SUFFIX="rc1"
            ;;
        --beta)
            SUFFIX="b1"
            ;;
        --alpha)
            SUFFIX="a1"
            ;;
        *)
            print_error "Unknown suffix: $2"
            exit 1
            ;;
    esac
fi

if [ -n "$SUFFIX" ]; then
    TAG="${VERSION}${SUFFIX}"
    RELEASE_TYPE="Pre-release (${SUFFIX})"
else
    TAG="${VERSION}"
    RELEASE_TYPE="Production"
fi

echo ""
print_info "=========================================="
print_info "  Rand Engine Release Script"
print_info "=========================================="
echo ""
print_info "Version: ${TAG}"
print_info "Type: ${RELEASE_TYPE}"
echo ""

# Verificar que estamos no diretório correto
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Are you in the project root?"
    exit 1
fi

# Verificar que git está limpo
if [ -n "$(git status --porcelain)" ]; then
    print_warning "Working directory has uncommitted changes"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Release cancelled"
        exit 1
    fi
fi

# Verificar que estamos na branch correta
CURRENT_BRANCH=$(git branch --show-current)
print_info "Current branch: ${CURRENT_BRANCH}"

if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "release/1.0" ]; then
    print_warning "Not on main or release branch"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Release cancelled"
        exit 1
    fi
fi

# Executar testes
print_info "Running tests..."
if poetry run pytest tests/ -v --tb=short; then
    print_success "All tests passed"
else
    print_error "Tests failed. Fix issues before releasing."
    exit 1
fi

# Verificar cobertura (opcional, não bloqueia)
print_info "Checking test coverage..."
poetry run pytest tests/ --cov=rand_engine --cov-report=term-missing || true

# Verificar que tag não existe
if git rev-parse "$TAG" >/dev/null 2>&1; then
    print_error "Tag ${TAG} already exists"
    exit 1
fi

# Confirmar release
echo ""
print_warning "=========================================="
print_warning "  Ready to release ${TAG}"
print_warning "=========================================="
echo ""
print_info "This will:"
echo "  1. Create and push tag: ${TAG}"
echo "  2. Trigger GitHub Actions workflow"
echo "  3. Run tests on Python 3.10, 3.11, 3.12"
echo "  4. Build and validate package"
echo "  5. Publish to PyPI"
echo "  6. Create GitHub Release"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Release cancelled"
    exit 1
fi

# Criar e push tag
print_info "Creating tag ${TAG}..."
git tag "$TAG"

print_info "Pushing tag to origin..."
git push origin "$TAG"

print_success "Tag ${TAG} pushed successfully!"
echo ""
print_info "=========================================="
print_info "  Release in progress"
print_info "=========================================="
echo ""
print_info "Track progress at:"
echo "  https://github.com/marcoaureliomenezes/rand_engine/actions"
echo ""
print_info "Once complete, check:"
echo "  PyPI: https://pypi.org/project/rand-engine/${TAG}/"
echo "  GitHub: https://github.com/marcoaureliomenezes/rand_engine/releases/tag/${TAG}"
echo ""
print_success "Release initiated successfully! 🚀"
