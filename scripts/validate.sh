#!/usr/bin/env bash
# =============================================================================
# validate.sh - Unified Developer Validation (Sentinel Tier 2)
# =============================================================================
#
# Philosophy: Run what CI will run, locally. Same morphism, different surface.
#
# This script mirrors CI checks locally for fast feedback before push.
# It's the developer-invoked equivalent of the pre-push hook, but with
# more detailed output and optional flags for debugging.
#
# Usage:
#   ./scripts/validate.sh          # Run all checks
#   ./scripts/validate.sh --quick  # Skip tests (lint + types only)
#   ./scripts/validate.sh --help   # Show options
#
# Checks (in order):
#   1. Ruff format check
#   2. Ruff lint (strict)
#   3. Mypy type check (strict)
#   4. Living Docs evidence verification
#   4.5. Documentation lint
#   5. TypeScript type check (frontend)
#   6. Pytest (unit + law + property, parallel)
#   7. Contract sync check (optional, requires backend)
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed
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

# Get repo root
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

# Parse arguments
QUICK_MODE=0
VERBOSE=0
SKIP_TESTS=0
SKIP_TS=0
INCLUDE_CONTRACT=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick|-q)
            QUICK_MODE=1
            SKIP_TESTS=1
            shift
            ;;
        --verbose|-v)
            VERBOSE=1
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=1
            shift
            ;;
        --skip-ts)
            SKIP_TS=1
            shift
            ;;
        --with-contract)
            INCLUDE_CONTRACT=1
            shift
            ;;
        --help|-h)
            echo "Usage: ./scripts/validate.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --quick, -q       Quick mode (lint + types only, skip tests)"
            echo "  --verbose, -v     Show full output from each check"
            echo "  --skip-tests      Skip Python tests"
            echo "  --skip-ts         Skip TypeScript checks"
            echo "  --with-contract   Include contract sync check (requires backend)"
            echo "  --help, -h        Show this help"
            echo ""
            echo "Examples:"
            echo "  ./scripts/validate.sh              # Full validation"
            echo "  ./scripts/validate.sh --quick      # Just lint + types"
            echo "  ./scripts/validate.sh --skip-ts    # Backend only"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Helper functions
section() {
    echo ""
    echo -e "${BOLD}[$1/$TOTAL] $2${NC}"
    echo "---"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

warn() {
    echo -e "${YELLOW}!${NC} $1"
}

# Count steps
TOTAL=6
[ $SKIP_TESTS -eq 0 ] && TOTAL=$((TOTAL + 1))
[ $SKIP_TS -eq 0 ] && TOTAL=$((TOTAL + 1))
[ $INCLUDE_CONTRACT -eq 1 ] && TOTAL=$((TOTAL + 1))

FAILED=0
STEP=0

echo -e "${BOLD}${CYAN}Sentinel Validation (Tier 2: Thorough)${NC}"
echo "======================================="

# =============================================================================
# Step 1: Ruff format check
# =============================================================================
STEP=$((STEP + 1))
section $STEP "Ruff format check"

cd "$REPO_ROOT/impl/claude"
if uv run ruff format --check . > /dev/null 2>&1; then
    success "Format OK"
else
    error "Format issues found"
    if [ $VERBOSE -eq 1 ]; then
        uv run ruff format --diff .
    else
        echo "  Run: uv run ruff format . (to auto-fix)"
    fi
    FAILED=1
fi

# =============================================================================
# Step 2: Ruff lint
# =============================================================================
STEP=$((STEP + 1))
section $STEP "Ruff lint (strict)"

cd "$REPO_ROOT/impl/claude"
LINT_OUTPUT=$(uv run ruff check agents/ bootstrap/ runtime/ protocols/ testing/ 2>&1) || true
LINT_EXIT=$?
if [ $LINT_EXIT -eq 0 ]; then
    success "Lint passed"
else
    LINT_COUNT=$(echo "$LINT_OUTPUT" | grep -c "^[A-Z][0-9]" || echo "0")
    error "Lint: $LINT_COUNT issues"
    if [ $VERBOSE -eq 1 ]; then
        echo "$LINT_OUTPUT"
    else
        echo "$LINT_OUTPUT" | head -10
        [ $LINT_COUNT -gt 10 ] && echo "  ... and $((LINT_COUNT - 10)) more"
    fi
    FAILED=1
fi

# =============================================================================
# Step 3: Mypy type check
# =============================================================================
STEP=$((STEP + 1))
section $STEP "Mypy (strict)"

cd "$REPO_ROOT/impl/claude"
MYPY_OUTPUT=$(uv run mypy --strict --explicit-package-bases agents/ bootstrap/ runtime/ 2>&1) || true
MYPY_EXIT=$?
if [ $MYPY_EXIT -eq 0 ]; then
    success "Type check passed"
else
    MYPY_COUNT=$(echo "$MYPY_OUTPUT" | grep -c ": error:" || echo "0")
    error "Mypy: $MYPY_COUNT errors"
    if [ $VERBOSE -eq 1 ]; then
        echo "$MYPY_OUTPUT"
    else
        echo "$MYPY_OUTPUT" | grep ": error:" | head -10
        [ $MYPY_COUNT -gt 10 ] && echo "  ... and $((MYPY_COUNT - 10)) more"
    fi
    FAILED=1
fi

# =============================================================================
# Step 4: Living Docs evidence verification
# =============================================================================
STEP=$((STEP + 1))
section $STEP "Living Docs evidence"

cd "$REPO_ROOT/impl/claude"
DOCS_OUTPUT=$(uv run kg docs verify --strict 2>&1) || true
DOCS_EXIT=$?
if [ $DOCS_EXIT -eq 0 ]; then
    success "Evidence links verified"
else
    MISSING=$(echo "$DOCS_OUTPUT" | grep -c "Missing:" || echo "0")
    error "Evidence: $MISSING missing links"
    if [ $VERBOSE -eq 1 ]; then
        echo "$DOCS_OUTPUT"
    else
        echo "$DOCS_OUTPUT" | grep -A5 "Missing Evidence" | head -10
    fi
    FAILED=1
fi

# =============================================================================
# Step 4.5: Documentation lint
# =============================================================================
STEP=$((STEP + 1))
section $STEP "Documentation lint"

cd "$REPO_ROOT/impl/claude"
LINT_DOCS_OUTPUT=$(uv run kg docs lint --strict 2>&1) || true
LINT_DOCS_EXIT=$?
if [ $LINT_DOCS_EXIT -eq 0 ]; then
    success "Documentation lint passed"
else
    LINT_ERRORS=$(echo "$LINT_DOCS_OUTPUT" | grep -c "ERRORS:" || echo "0")
    error "Documentation lint: issues found"
    if [ $VERBOSE -eq 1 ]; then
        echo "$LINT_DOCS_OUTPUT"
    else
        echo "$LINT_DOCS_OUTPUT" | tail -20
    fi
    FAILED=1
fi

# =============================================================================
# Step 5: TypeScript type check (frontend)
# =============================================================================
if [ $SKIP_TS -eq 0 ]; then
    STEP=$((STEP + 1))
    section $STEP "TypeScript (frontend)"

    cd "$REPO_ROOT/impl/claude/web"
    if npm run typecheck --silent 2>&1; then
        success "TypeScript passed"
    else
        error "TypeScript errors"
        FAILED=1
    fi
fi

# =============================================================================
# Step 6: ESLint (frontend)
# =============================================================================
STEP=$((STEP + 1))
section $STEP "ESLint (frontend)"

if [ $SKIP_TS -eq 0 ]; then
    cd "$REPO_ROOT/impl/claude/web"
    if npm run lint --silent 2>&1; then
        success "ESLint passed"
    else
        error "ESLint errors"
        FAILED=1
    fi
else
    warn "Skipped (--skip-ts)"
fi

# =============================================================================
# Step 7: Python tests
# =============================================================================
if [ $SKIP_TESTS -eq 0 ]; then
    STEP=$((STEP + 1))
    section $STEP "Python tests (parallel)"

    cd "$REPO_ROOT/impl/claude"

    # Detect optimal worker count
    if [ -n "${KGENTS_PYTEST_WORKERS:-}" ]; then
        WORKERS="$KGENTS_PYTEST_WORKERS"
    else
        WORKERS=5
    fi

    echo "Running with $WORKERS workers..."
    TEST_OUTPUT=$(uv run pytest \
        -m "not slow and not tier3 and not accursed_share" \
        -n "$WORKERS" \
        --tb=short \
        -q \
        --dist=loadfile \
        2>&1) || true
    TEST_EXIT=$?

    if [ $TEST_EXIT -eq 0 ]; then
        SUMMARY=$(echo "$TEST_OUTPUT" | tail -1)
        success "Tests passed: $SUMMARY"
    else
        error "Tests failed"
        echo "$TEST_OUTPUT" | tail -20
        FAILED=1
    fi
fi

# =============================================================================
# Step 8: Contract sync (optional)
# =============================================================================
if [ $INCLUDE_CONTRACT -eq 1 ]; then
    STEP=$((STEP + 1))
    section $STEP "Contract sync"

    cd "$REPO_ROOT/impl/claude/web"

    # Check if backend is running
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        if npm run sync-types:check --silent 2>&1; then
            success "Contracts in sync"
        else
            error "Contract drift detected"
            echo "  Run: npm run sync-types (to update)"
            FAILED=1
        fi
    else
        warn "Backend not running. Start with:"
        echo "  cd impl/claude && uv run uvicorn protocols.api.app:create_app --factory --port 8000"
    fi
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "======================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}${BOLD}All checks passed!${NC}"
    echo ""
    echo "Your changes should pass CI. Safe to push."
    exit 0
else
    echo -e "${RED}${BOLD}Validation failed.${NC}"
    echo ""
    echo "Fix the issues above before pushing."
    echo "Re-run with --verbose for full output."
    exit 1
fi
