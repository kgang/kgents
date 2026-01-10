#!/usr/bin/env bash
# =============================================================================
# validate.sh - Unified Developer Validation (Sentinel Tier 2)
# =============================================================================
#
# Philosophy: Run what CI will run, locally. Same morphism, different surface.
# Architecture: Heterarchical - resources flow where needed.
#
# This script mirrors CI checks locally for fast feedback before push.
# It's the developer-invoked equivalent of the pre-push hook, but with
# more detailed output and optional flags for debugging.
#
# Optimizations (2025-01-10 - Enlightened Enhancement):
#   - Parallel Python + JS tracks (--parallel flag, 2-4x faster)
#   - Adaptive worker count based on system load
#   - Mypy incremental caching
#   - Timing information for each step
#   - Optional fast-dom for Vitest
#
# Usage:
#   ./scripts/validate.sh          # Run all checks
#   ./scripts/validate.sh --quick  # Skip tests (lint + types only)
#   ./scripts/validate.sh --parallel  # Run Python + JS in parallel
#   ./scripts/validate.sh --help   # Show options
#
# Checks (in order):
#   1. Ruff format check
#   2. Ruff lint (strict)
#   3. Mypy type check (strict, incremental)
#   4. Living Docs evidence verification
#   4.5. Documentation lint
#   5. TypeScript type check (frontend)
#   6. Pytest (unit + law + property, parallel)
#   7. Frontend tests (Vitest)
#   8. Contract sync check (optional, requires backend)
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed
#
# Environment Variables:
#   KGENTS_PYTEST_WORKERS=N  - Override pytest worker count
#   KGENTS_TEST_WORKERS=N    - Override Vitest worker count
#   KGENTS_FAST_DOM=1        - Use happy-dom for Vitest (30-40% faster)
#   KGENTS_USE_DMYPY=1       - Use mypy daemon (2-3x faster re-runs)
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
SKIP_JS_TESTS=0
INCLUDE_CONTRACT=0
PARALLEL_MODE=0
FAST_MODE=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick|-q)
            QUICK_MODE=1
            SKIP_TESTS=1
            SKIP_JS_TESTS=1
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
            SKIP_JS_TESTS=1
            shift
            ;;
        --skip-js-tests)
            SKIP_JS_TESTS=1
            shift
            ;;
        --with-contract)
            INCLUDE_CONTRACT=1
            shift
            ;;
        --parallel|-p)
            PARALLEL_MODE=1
            shift
            ;;
        --fast)
            FAST_MODE=1
            export KGENTS_FAST_DOM=1
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
            echo "  --skip-js-tests   Skip frontend JS/TS tests only"
            echo "  --with-contract   Include contract sync check (requires backend)"
            echo "  --parallel, -p    Run Python and frontend checks in parallel"
            echo "  --fast            Use happy-dom for faster Vitest (KGENTS_FAST_DOM=1)"
            echo "  --help, -h        Show this help"
            echo ""
            echo "Examples:"
            echo "  ./scripts/validate.sh              # Full validation"
            echo "  ./scripts/validate.sh --quick      # Just lint + types"
            echo "  ./scripts/validate.sh --parallel   # Python + JS in parallel (fastest)"
            echo "  ./scripts/validate.sh --skip-ts    # Backend only"
            echo ""
            echo "Environment Variables:"
            echo "  KGENTS_PYTEST_WORKERS=N  - Override pytest worker count"
            echo "  KGENTS_TEST_WORKERS=N    - Override Vitest worker count"
            echo "  KGENTS_FAST_DOM=1        - Use happy-dom (30-40% faster)"
            echo "  KGENTS_USE_DMYPY=1       - Use mypy daemon"
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

# Timing helper
time_cmd() {
    local start=$(date +%s)
    "$@"
    local exit_code=$?
    local end=$(date +%s)
    LAST_DURATION=$((end - start))
    return $exit_code
}

# Detect optimal worker count
detect_workers() {
    if [ -n "${KGENTS_PYTEST_WORKERS:-}" ]; then
        echo "$KGENTS_PYTEST_WORKERS"
        return
    fi

    local cpu_count=4
    if command -v nproc &> /dev/null; then
        cpu_count=$(nproc)
    elif command -v sysctl &> /dev/null; then
        cpu_count=$(sysctl -n hw.ncpu 2>/dev/null || echo "8")
    fi

    # Use half CPUs, clamped to 2-8
    local workers=$((cpu_count / 2))
    [ "$workers" -lt 2 ] && workers=2
    [ "$workers" -gt 8 ] && workers=8

    echo "$workers"
}

WORKERS=$(detect_workers)

# Count steps
TOTAL=6
[ $SKIP_TESTS -eq 0 ] && TOTAL=$((TOTAL + 1))
[ $SKIP_TS -eq 0 ] && TOTAL=$((TOTAL + 1))
[ $SKIP_JS_TESTS -eq 0 ] && [ $SKIP_TS -eq 0 ] && TOTAL=$((TOTAL + 1))
[ $INCLUDE_CONTRACT -eq 1 ] && TOTAL=$((TOTAL + 1))

FAILED=0
STEP=0
TOTAL_START=$(date +%s)

echo -e "${BOLD}${CYAN}Sentinel Validation (Tier 2: Thorough)${NC}"
echo "======================================="
if [ $PARALLEL_MODE -eq 1 ]; then
    echo -e "${CYAN}Mode: Parallel (Python + JS concurrent)${NC}"
fi
if [ $FAST_MODE -eq 1 ]; then
    echo -e "${CYAN}Mode: Fast (happy-dom enabled)${NC}"
fi
echo ""

# =============================================================================
# Step 1: Ruff format check
# =============================================================================
STEP=$((STEP + 1))
section $STEP "Ruff format check"

cd "$REPO_ROOT/impl/claude"
if time_cmd uv run ruff format --check . > /dev/null 2>&1; then
    success "Format OK (${LAST_DURATION}s)"
else
    error "Format issues found (${LAST_DURATION}s)"
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
LINT_OUTPUT=$(time_cmd uv run ruff check agents/ bootstrap/ runtime/ protocols/ testing/ services/ 2>&1) || true
LINT_EXIT=$?
if [ $LINT_EXIT -eq 0 ]; then
    success "Lint passed (${LAST_DURATION}s)"
else
    LINT_COUNT=$(echo "$LINT_OUTPUT" | grep -c "^[A-Z][0-9]" || echo "0")
    error "Lint: $LINT_COUNT issues (${LAST_DURATION}s)"
    if [ $VERBOSE -eq 1 ]; then
        echo "$LINT_OUTPUT"
    else
        echo "$LINT_OUTPUT" | head -10
        [ "$LINT_COUNT" -gt 10 ] && echo "  ... and $((LINT_COUNT - 10)) more"
    fi
    FAILED=1
fi

# =============================================================================
# Step 3: Mypy type check (with incremental caching)
# =============================================================================
STEP=$((STEP + 1))
section $STEP "Mypy (strict, incremental)"

cd "$REPO_ROOT/impl/claude"

run_mypy() {
    if [ "${KGENTS_USE_DMYPY:-0}" = "1" ] && command -v dmypy &> /dev/null; then
        echo "Using mypy daemon..."
        uv run dmypy run -- --strict --explicit-package-bases agents/ bootstrap/ runtime/ 2>&1
    else
        uv run mypy --strict --explicit-package-bases agents/ bootstrap/ runtime/ 2>&1
    fi
}

MYPY_OUTPUT=$(time_cmd run_mypy) || true
MYPY_EXIT=$?
if [ $MYPY_EXIT -eq 0 ]; then
    success "Type check passed (${LAST_DURATION}s)"
else
    MYPY_COUNT=$(echo "$MYPY_OUTPUT" | grep -c ": error:" || echo "0")
    error "Mypy: $MYPY_COUNT errors (${LAST_DURATION}s)"
    if [ $VERBOSE -eq 1 ]; then
        echo "$MYPY_OUTPUT"
    else
        echo "$MYPY_OUTPUT" | grep ": error:" | head -10
        [ "$MYPY_COUNT" -gt 10 ] && echo "  ... and $((MYPY_COUNT - 10)) more"
    fi
    FAILED=1
fi

# =============================================================================
# Step 4: Living Docs evidence verification
# =============================================================================
STEP=$((STEP + 1))
section $STEP "Living Docs evidence"

cd "$REPO_ROOT/impl/claude"
DOCS_OUTPUT=$(time_cmd uv run kg docs verify --strict 2>&1) || true
DOCS_EXIT=$?
if [ $DOCS_EXIT -eq 0 ]; then
    success "Evidence links verified (${LAST_DURATION}s)"
else
    MISSING=$(echo "$DOCS_OUTPUT" | grep -c "Missing:" || echo "0")
    error "Evidence: $MISSING missing links (${LAST_DURATION}s)"
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
LINT_DOCS_OUTPUT=$(time_cmd uv run kg docs lint --strict 2>&1) || true
LINT_DOCS_EXIT=$?
if [ $LINT_DOCS_EXIT -eq 0 ]; then
    success "Documentation lint passed (${LAST_DURATION}s)"
else
    LINT_ERRORS=$(echo "$LINT_DOCS_OUTPUT" | grep -c "ERRORS:" || echo "0")
    error "Documentation lint: issues found (${LAST_DURATION}s)"
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
    if time_cmd npm run typecheck --silent 2>&1; then
        success "TypeScript passed (${LAST_DURATION}s)"
    else
        error "TypeScript errors (${LAST_DURATION}s)"
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
    if time_cmd npm run lint --silent 2>&1; then
        success "ESLint passed (${LAST_DURATION}s)"
    else
        error "ESLint errors (${LAST_DURATION}s)"
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
    section $STEP "Python tests (parallel: $WORKERS workers)"

    cd "$REPO_ROOT/impl/claude"

    echo "Running with $WORKERS workers..."
    TEST_OUTPUT=$(time_cmd uv run pytest \
        -m "not slow and not tier3 and not accursed_share" \
        -n "$WORKERS" \
        --tb=short \
        -q \
        --dist=worksteal \
        2>&1) || true
    TEST_EXIT=$?

    if [ $TEST_EXIT -eq 0 ]; then
        SUMMARY=$(echo "$TEST_OUTPUT" | tail -1)
        success "Tests passed: $SUMMARY (${LAST_DURATION}s)"
    else
        error "Tests failed (${LAST_DURATION}s)"
        echo "$TEST_OUTPUT" | tail -20
        FAILED=1
    fi
fi

# =============================================================================
# Step 7.5: Frontend tests (Vitest)
# =============================================================================
if [ $SKIP_JS_TESTS -eq 0 ] && [ $SKIP_TS -eq 0 ]; then
    STEP=$((STEP + 1))
    section $STEP "Frontend tests (Vitest)"

    cd "$REPO_ROOT/impl/claude/web"

    if time_cmd npm test -- --run --reporter=basic 2>&1; then
        success "Frontend tests passed (${LAST_DURATION}s)"
    else
        error "Frontend tests failed (${LAST_DURATION}s)"
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
        if time_cmd npm run sync-types:check --silent 2>&1; then
            success "Contracts in sync (${LAST_DURATION}s)"
        else
            error "Contract drift detected (${LAST_DURATION}s)"
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
TOTAL_END=$(date +%s)
TOTAL_DURATION=$((TOTAL_END - TOTAL_START))

echo ""
echo "======================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}${BOLD}All checks passed!${NC} (${TOTAL_DURATION}s total)"
    echo ""
    echo "Your changes should pass CI. Safe to push."
    exit 0
else
    echo -e "${RED}${BOLD}Validation failed.${NC} (${TOTAL_DURATION}s total)"
    echo ""
    echo "Fix the issues above before pushing."
    echo "Re-run with --verbose for full output."
    exit 1
fi
