#!/usr/bin/env bash
#
# Install kgents git hooks (UNIFIED: Python + JS/TS)
#
# Usage: ./scripts/hooks/install.sh
#
# The hooks are organized as:
#   - impl/claude/web/.husky/pre-commit  -> UNIFIED hook (runs Python + JS/TS checks)
#   - impl/claude/web/.husky/pre-push    -> UNIFIED hook (runs Python + JS/TS checks)
#   - scripts/hooks/pre-commit           -> Python-only hook (called by unified hook)
#   - scripts/hooks/pre-push             -> Python-only hook (called by unified hook)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
HUSKY_DIR="$REPO_ROOT/impl/claude/web/.husky"

echo "Installing kgents git hooks (UNIFIED: Python + JS/TS)..."
echo ""

# Ensure Python-only hooks are executable (called by unified hooks)
chmod +x "$SCRIPT_DIR/lib.sh"
chmod +x "$SCRIPT_DIR/pre-commit"
chmod +x "$SCRIPT_DIR/pre-push"

# Ensure unified hooks are executable
chmod +x "$HUSKY_DIR/pre-commit"
chmod +x "$HUSKY_DIR/pre-push"

# Create symlinks to UNIFIED hooks (which call Python hooks internally)
ln -sf "$HUSKY_DIR/pre-commit" "$HOOKS_DIR/pre-commit"
ln -sf "$HUSKY_DIR/pre-push" "$HOOKS_DIR/pre-push"

echo "Installed hooks:"
echo "  pre-commit -> impl/claude/web/.husky/pre-commit"
echo "               (Python: ruff format, lint, mypy)"
echo "               (JS/TS:  eslint, prettier via lint-staged)"
echo ""
echo "  pre-push   -> impl/claude/web/.husky/pre-push"
echo "               (Python: tests, laws, property tests)"
echo "               (JS/TS:  typecheck, unit tests, build)"
echo ""
echo "Configuration:"
echo "  KGENTS_SKIP_HEAVY=1    Skip Python pre-push heavy tests"
echo "  KGENTS_SKIP_CHAOS=1    Skip chaos tests in pre-push"
echo "  KGENTS_E2E_TESTS=1     Run E2E Playwright tests on push"
echo ""
echo "Done."
