# Git Hooks for kgents

This directory contains git hooks that enforce CLI strategy tools.

## Installation

```bash
# One-time setup
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

## Available Hooks

### `pre-commit`
Runs before every commit:
1. If spec files changed: `kg audit --system`
2. Always: `kg probe health --all`
3. Always: `kg compose --run "pre-commit"`

**Bypass**: Use `git commit --no-verify` to skip (not recommended)

## Philosophy

> *"The proof IS the decision. The mark IS the witness."*

Hooks ensure:
- Specs stay aligned with principles
- System health is validated
- Every commit is witnessed
- Technical debt is visible

## Troubleshooting

### Hook fails but you need to commit urgently
```bash
# Skip hooks (use sparingly)
git commit --no-verify -m "..."

# Then fix and create amendment commit
kg audit --system
# ... fix issues ...
git commit -m "fix: Address audit findings"
```

### Hook is too slow
The hooks run fast categorical checks only (no LLM calls).
If still too slow, consider:
1. Running `kg compose --run "pre-commit"` manually before commit
2. Adjusting hook to run on CI instead

### Health probe fails
```bash
# Diagnose specific jewel
kg probe health --jewel brain

# View recent errors
kg witness show --today --tag error

# Fix and retry
git commit
```

---

*For full documentation, see: `docs/skills/cli-strategy-tools.md`*
