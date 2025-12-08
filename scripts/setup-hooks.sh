#!/usr/bin/env bash
#
# Setup script for installing git hooks
#

set -e

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOK_SOURCE="$REPO_ROOT/scripts/pre-commit-hook.sh"

echo "Setting up git hooks for kgents..."

# Ensure .git/hooks directory exists
if [ ! -d "$HOOKS_DIR" ]; then
    echo "Error: Not in a git repository or .git/hooks directory not found"
    exit 1
fi

# Copy the pre-commit hook
if [ -f "$HOOK_SOURCE" ]; then
    cp "$HOOK_SOURCE" "$HOOKS_DIR/pre-commit"
    chmod +x "$HOOKS_DIR/pre-commit"
    echo "✓ Pre-commit hook installed"
else
    echo "Warning: Pre-commit hook source not found at $HOOK_SOURCE"
    echo "Creating from template..."

    # The hook is already in .git/hooks, just ensure it's executable
    if [ -f "$HOOKS_DIR/pre-commit" ]; then
        chmod +x "$HOOKS_DIR/pre-commit"
        echo "✓ Pre-commit hook is ready"
    else
        echo "Error: Could not find or create pre-commit hook"
        exit 1
    fi
fi

echo ""
echo "Git hooks installed successfully!"
echo ""
echo "To skip hooks for a commit (use sparingly):"
echo "  git commit --no-verify"
echo ""
echo "To uninstall hooks:"
echo "  rm .git/hooks/pre-commit"
