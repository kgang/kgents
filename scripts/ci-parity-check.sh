#!/usr/bin/env bash
# =============================================================================
# ci-parity-check.sh - Environment Functor Preservation
# =============================================================================
#
# Philosophy: If the functor Local → CI doesn't preserve structure, composition breaks.
#
# This script verifies that local development environment is isomorphic to CI.
# When they diverge, you get "works on my machine" failures.
#
# Checks:
#   F(python_version) = python_version   [CI uses 3.11, 3.12, 3.13]
#   F(node_version) = node_version       [CI uses 20]
#   F(dependencies) = dependencies       [uv.lock and package-lock.json]
#
# Usage:
#   ./scripts/ci-parity-check.sh         # Run all checks
#   ./scripts/ci-parity-check.sh --fix   # Attempt to fix issues
#
# Exit codes:
#   0 - Parity verified (functor preserves structure)
#   1 - Parity broken (fix issues or expect CI failures)
#
# =============================================================================

set -e

# Colors
BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# CI target versions (from .github/workflows/ci.yml)
CI_PYTHON_MIN="3.11"
CI_PYTHON_MAX="3.13"
CI_NODE="20"

# Get repo root
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Parse arguments
FIX_MODE=0
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix|-f)
            FIX_MODE=1
            shift
            ;;
        --help|-h)
            echo "Usage: ./scripts/ci-parity-check.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --fix, -f    Attempt to fix parity issues"
            echo "  --help, -h   Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Helper functions
check() {
    echo -e "${GREEN}✓${NC} $1"
}

warn() {
    echo -e "${YELLOW}!${NC} $1"
}

fail() {
    echo -e "${RED}✗${NC} $1"
}

info() {
    echo -e "${CYAN}→${NC} $1"
}

ISSUES=0

echo -e "${BOLD}${CYAN}CI Parity Check (Functor Preservation)${NC}"
echo "========================================"
echo ""

# =============================================================================
# Check 1: Python version
# =============================================================================
echo -e "${BOLD}Python Version${NC}"
echo "CI supports: $CI_PYTHON_MIN - $CI_PYTHON_MAX"

# Get local Python version
LOCAL_PYTHON=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1-2 || echo "not found")

if [ "$LOCAL_PYTHON" = "not found" ]; then
    fail "Python3 not found"
    info "Install Python $CI_PYTHON_MIN or later"
    ISSUES=$((ISSUES + 1))
else
    # Compare versions (basic check)
    MAJOR=$(echo "$LOCAL_PYTHON" | cut -d'.' -f1)
    MINOR=$(echo "$LOCAL_PYTHON" | cut -d'.' -f2)

    CI_MIN_MAJOR=$(echo "$CI_PYTHON_MIN" | cut -d'.' -f1)
    CI_MIN_MINOR=$(echo "$CI_PYTHON_MIN" | cut -d'.' -f2)
    CI_MAX_MAJOR=$(echo "$CI_PYTHON_MAX" | cut -d'.' -f1)
    CI_MAX_MINOR=$(echo "$CI_PYTHON_MAX" | cut -d'.' -f2)

    if [ "$MAJOR" -lt "$CI_MIN_MAJOR" ] || \
       ([ "$MAJOR" -eq "$CI_MIN_MAJOR" ] && [ "$MINOR" -lt "$CI_MIN_MINOR" ]); then
        fail "Python $LOCAL_PYTHON < $CI_PYTHON_MIN (CI minimum)"
        info "Upgrade to Python $CI_PYTHON_MIN or later"
        ISSUES=$((ISSUES + 1))
    elif [ "$MAJOR" -gt "$CI_MAX_MAJOR" ] || \
         ([ "$MAJOR" -eq "$CI_MAX_MAJOR" ] && [ "$MINOR" -gt "$CI_MAX_MINOR" ]); then
        warn "Python $LOCAL_PYTHON > $CI_PYTHON_MAX (CI maximum)"
        info "You may encounter issues not caught in CI"
    else
        check "Python $LOCAL_PYTHON (within CI range)"
    fi
fi
echo ""

# =============================================================================
# Check 2: Node version
# =============================================================================
echo -e "${BOLD}Node Version${NC}"
echo "CI uses: Node $CI_NODE"

LOCAL_NODE=$(node --version 2>/dev/null | cut -d'v' -f2 | cut -d'.' -f1 || echo "not found")

if [ "$LOCAL_NODE" = "not found" ]; then
    fail "Node not found"
    info "Install Node.js $CI_NODE"
    ISSUES=$((ISSUES + 1))
elif [ "$LOCAL_NODE" != "$CI_NODE" ]; then
    warn "Node $LOCAL_NODE (CI uses $CI_NODE)"
    info "Consider using nvm: nvm use $CI_NODE"
else
    check "Node $LOCAL_NODE (matches CI)"
fi
echo ""

# =============================================================================
# Check 3: UV lockfile sync
# =============================================================================
echo -e "${BOLD}UV Lockfile Sync${NC}"

cd "$REPO_ROOT/impl/claude"
if uv lock --check 2>/dev/null; then
    check "uv.lock in sync with pyproject.toml"
else
    fail "uv.lock out of sync"
    if [ $FIX_MODE -eq 1 ]; then
        info "Fixing: uv lock"
        uv lock
        check "Fixed uv.lock"
    else
        info "Run: cd impl/claude && uv lock"
    fi
    ISSUES=$((ISSUES + 1))
fi
echo ""

# =============================================================================
# Check 4: NPM lockfile sync
# =============================================================================
echo -e "${BOLD}NPM Lockfile Sync${NC}"

cd "$REPO_ROOT/impl/claude/web"
# Check if package-lock.json exists and matches package.json
if [ -f "package-lock.json" ]; then
    # npm ci will fail if lock is out of sync
    if npm ci --dry-run 2>/dev/null | grep -q "up to date"; then
        check "package-lock.json in sync"
    else
        # More reliable: check if npm install would make changes
        LOCK_BEFORE=$(md5sum package-lock.json 2>/dev/null | cut -d' ' -f1 || echo "none")
        npm install --package-lock-only --silent 2>/dev/null || true
        LOCK_AFTER=$(md5sum package-lock.json 2>/dev/null | cut -d' ' -f1 || echo "changed")

        if [ "$LOCK_BEFORE" = "$LOCK_AFTER" ]; then
            check "package-lock.json in sync"
        else
            fail "package-lock.json out of sync"
            if [ $FIX_MODE -eq 1 ]; then
                info "Fixing: npm install"
                npm install
                check "Fixed package-lock.json"
            else
                info "Run: cd impl/claude/web && npm install"
            fi
            ISSUES=$((ISSUES + 1))
            # Restore original lockfile if not fixing
            [ $FIX_MODE -eq 0 ] && git checkout package-lock.json 2>/dev/null || true
        fi
    fi
else
    fail "package-lock.json missing"
    info "Run: cd impl/claude/web && npm install"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# =============================================================================
# Check 5: Required tools
# =============================================================================
echo -e "${BOLD}Required Tools${NC}"

# Check uv
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version | cut -d' ' -f2)
    check "uv $UV_VERSION"
else
    fail "uv not found"
    info "Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    ISSUES=$((ISSUES + 1))
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    check "npm $NPM_VERSION"
else
    fail "npm not found"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# =============================================================================
# Summary
# =============================================================================
echo "========================================"
if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}${BOLD}Parity verified!${NC}"
    echo ""
    echo "F(local_env) = ci_env"
    echo "Your local environment matches CI."
    exit 0
else
    echo -e "${RED}${BOLD}Parity broken: $ISSUES issue(s)${NC}"
    echo ""
    echo "F(local_env) != ci_env"
    echo "Fix the issues above to avoid 'works on my machine' failures."
    if [ $FIX_MODE -eq 0 ]; then
        echo ""
        echo "Tip: Run with --fix to auto-fix lockfile issues"
    fi
    exit 1
fi
