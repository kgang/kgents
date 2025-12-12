#!/usr/bin/env bash
#
# kgents hooks library
# Shared functions for pre-commit and pre-push hooks
#

# Colors
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'
export CYAN='\033[0;36m'
export BOLD='\033[1m'
export NC='\033[0m'

# Avoid VIRTUAL_ENV mismatch warnings from other projects
unset VIRTUAL_ENV

# Get repo root
get_repo_root() {
    git rev-parse --show-toplevel
}

# Check if uv is available
require_uv() {
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}Error: uv not found. Please install: https://docs.astral.sh/uv/${NC}"
        exit 1
    fi
}

# Get staged Python files
get_staged_python_files() {
    git diff --cached --name-only --diff-filter=ACM | grep -E '\.py$' || true
}

# Get all changed Python files (staged + modified)
get_changed_python_files() {
    git diff --name-only --diff-filter=ACM HEAD | grep -E '\.py$' || true
}

# Get impl/claude Python files from a list
filter_impl_claude() {
    echo "$1" | grep "impl/claude" || true
}

# Get test files from a list
filter_test_files() {
    echo "$1" | grep "test_" || true
}

# Print section header
section() {
    local name="$1"
    local step="$2"
    local total="$3"
    echo -e "${BLUE}[${step}/${total}] ${name}${NC}"
}

# Print success
success() {
    echo -e "${GREEN}$1${NC}"
}

# Print warning (non-blocking)
warn() {
    echo -e "${YELLOW}$1${NC}"
}

# Print error (blocking)
error() {
    echo -e "${RED}$1${NC}"
}

# Print info
info() {
    echo -e "${CYAN}$1${NC}"
}

# Run ruff format on files (auto-fix)
run_ruff_format() {
    local files="$1"
    local failed=0

    for file in $files; do
        if [ -f "$file" ]; then
            if ! uv run ruff format "$file" 2>&1 | grep -v "files left unchanged"; then
                :  # Silence "unchanged" messages
            fi
            # Re-stage formatted file
            git add "$file" 2>/dev/null || true
        fi
    done

    return $failed
}

# Run ruff lint on files (with auto-fix)
run_ruff_lint() {
    local files="$1"
    local strict="${2:-false}"
    local failed=0

    for file in $files; do
        if [ -f "$file" ]; then
            if ! uv run ruff check "$file" --fix 2>&1; then
                failed=1
            else
                git add "$file" 2>/dev/null || true
            fi
        fi
    done

    if [ "$strict" = "true" ] && [ $failed -eq 1 ]; then
        return 1
    fi
    return 0
}

# Run mypy on directories
run_mypy() {
    local dirs="$1"
    local strict="${2:-false}"
    local failed=0

    cd "$(get_repo_root)/impl/claude"

    for dir in $dirs; do
        if [ -d "$dir" ]; then
            local flags="--explicit-package-bases"
            if [ "$strict" = "true" ]; then
                flags="$flags --strict"
            fi
            if ! uv run mypy $flags "$dir" 2>&1; then
                failed=1
            fi
        fi
    done

    cd "$(get_repo_root)"
    return $failed
}

# Run pytest with specific markers
run_pytest() {
    local path="$1"
    local markers="$2"
    local extra_args="${3:-}"

    cd "$(get_repo_root)/impl/claude"

    local cmd="uv run pytest"
    if [ -n "$markers" ]; then
        cmd="$cmd -m \"$markers\""
    fi
    if [ -n "$extra_args" ]; then
        cmd="$cmd $extra_args"
    fi
    cmd="$cmd $path"

    eval $cmd
    local result=$?

    cd "$(get_repo_root)"
    return $result
}

# Print horizontal rule
hr() {
    echo -e "${GREEN}════════════════════════════════════════${NC}"
}
