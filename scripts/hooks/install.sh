#!/usr/bin/env bash
#
# Install kgents git hooks
#
# Usage: ./scripts/hooks/install.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "Installing kgents git hooks..."
echo ""

# Ensure hooks are executable
chmod +x "$SCRIPT_DIR/lib.sh"
chmod +x "$SCRIPT_DIR/pre-commit"
chmod +x "$SCRIPT_DIR/pre-push"

# Create symlinks
ln -sf "$SCRIPT_DIR/pre-commit" "$HOOKS_DIR/pre-commit"
ln -sf "$SCRIPT_DIR/pre-push" "$HOOKS_DIR/pre-push"

echo "Installed hooks:"
echo "  pre-commit -> scripts/hooks/pre-commit (light: format, lint)"
echo "  pre-push   -> scripts/hooks/pre-push (heavy: tests, laws, integration)"
echo ""
echo "Configuration:"
echo "  KGENTS_SKIP_HEAVY=1    Skip pre-push heavy tests"
echo "  KGENTS_SKIP_PROPERTY=1 Skip property tests in pre-push"
echo "  KGENTS_RUN_CHAOS=1     Enable chaos tests in pre-push"
echo ""
echo "Done."
