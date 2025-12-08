# Development Guide

This guide covers the development workflow, tooling, and best practices for contributing to kgents.

## Quick Start

```bash
# Install dependencies
uv sync --all-extras

# Run tests
cd impl/claude
uv run pytest

# Run linters
uv run ruff format impl/claude  # Auto-format
uv run ruff check impl/claude   # Lint
uv run mypy --strict bootstrap/ agents/ runtime/  # Type check
```

## Pre-Commit Hook

A pre-commit hook is installed at `.git/hooks/pre-commit` that automatically runs quality checks before each commit.

### What the hook does

1. **Auto-formats** Python code with `ruff format`
2. **Lints** code with `ruff check --fix` (auto-fixes simple issues)
3. **Type checks** with `mypy` (warnings only, non-blocking)
4. **Runs tests** if test files are modified

### Hook Philosophy

The pre-commit hook is designed for **AI agent development workflows**:

- **Fast**: Only checks staged files
- **Auto-fixing**: Formats and fixes simple issues automatically
- **Non-blocking**: Warnings don't prevent commits (except test failures)
- **Focused**: Catches critical issues without slowing iteration

### Bypassing the Hook

When needed (use sparingly):

```bash
git commit --no-verify
```

### Manual Hook Setup

If the hook isn't working:

```bash
chmod +x .git/hooks/pre-commit
```

Or reinstall:

```bash
bash scripts/setup-hooks.sh
```

## GitHub CI Pipeline

The CI pipeline runs on every push and pull request to `main`:

### Jobs

1. **Test** (`test`)
   - Runs pytest across Python 3.11, 3.12, 3.13
   - Matrix strategy for broad compatibility
   - Fast-fail disabled for complete results

2. **Lint & Type Check** (`lint`)
   - `ruff format --check` - Ensures code is formatted
   - `ruff check` - Lints for errors and style issues
   - `mypy --strict` - Strict type checking (continue-on-error)

3. **Coverage** (`coverage`)
   - Generates test coverage reports
   - Uploads to Codecov
   - Non-blocking

4. **Security** (`security`)
   - Runs `bandit` for Python security issues
   - Scans agents, bootstrap, and runtime code
   - Generates JSON report artifact
   - Non-blocking (warnings only)

5. **Spec & Docs Validation** (`spec-validation`)
   - Lints markdown files in `spec/`, `docs/`, and root
   - Checks for broken links in documentation
   - Non-blocking (informational)

### Concurrency Control

The CI uses concurrency groups to automatically cancel outdated runs:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

This saves CI minutes and provides faster feedback.

## Code Quality Tools

### Ruff

Fast Python linter and formatter (replaces Black, isort, flake8, etc.)

```bash
# Format code
uv run ruff format .

# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix
```

### Mypy

Static type checker for Python:

```bash
cd impl/claude
uv run mypy --strict bootstrap/ agents/ runtime/
```

**Note**: Strict mode is enforced in CI but relaxed in pre-commit for iteration speed.

### Bandit

Security linter for Python:

```bash
uv run bandit -r impl/claude/agents impl/claude/bootstrap impl/claude/runtime
```

## Testing

### Running Tests

```bash
# All tests
cd impl/claude
uv run pytest

# Specific test file
uv run pytest tests/test_specific.py

# With coverage
uv run pytest --cov=agents --cov=bootstrap --cov=runtime --cov-report=html
```

### Test Organization

- Tests live in `impl/claude/tests/`
- Follow pytest conventions (`test_*.py`, `*_test.py`)
- Use fixtures for common setup
- Async tests use `pytest-asyncio`

## Project Structure

```
kgents/
├── spec/              # Specification (language-agnostic)
├── impl/              # Implementations
│   └── claude/        # Claude reference implementation
│       ├── agents/    # Agent implementations
│       ├── bootstrap/ # Bootstrap agents
│       ├── runtime/   # Runtime and LLM integrations
│       └── tests/     # Test suite
├── docs/              # Documentation
├── scripts/           # Development scripts
└── .github/           # CI/CD workflows
```

## Workflow for AI Agents

When developing with AI coding agents (like Claude Code):

1. **Rapid iteration**: Pre-commit hook provides fast feedback
2. **Auto-formatting**: Code is automatically formatted on commit
3. **Non-blocking warnings**: Type hints and lint warnings don't block commits
4. **Test failures block**: Critical issues (test failures) prevent commits
5. **CI as safety net**: Full checks run on push

### Best Practices

- **Commit frequently**: Pre-commit is fast, don't batch changes
- **Fix test failures immediately**: They block commits for good reason
- **Address type warnings**: They're non-blocking but improve code quality
- **Review security scan results**: Check CI artifacts for bandit reports
- **Keep docs updated**: Markdown linting helps maintain quality

## Dependencies

Managed with `uv` (fast Python package manager):

```bash
# Install/update dependencies
uv sync --all-extras

# Add a dependency
cd impl/claude
# Edit pyproject.toml, then:
uv sync

# Update lock file
uv lock
```

## Troubleshooting

### Pre-commit hook not running

```bash
# Check if executable
ls -l .git/hooks/pre-commit

# Make executable
chmod +x .git/hooks/pre-commit
```

### CI failing but pre-commit passed

- Pre-commit uses relaxed checks for speed
- CI runs full strict checks
- Always ensure your code passes CI before merging

### Type checking issues

```bash
# Run the same check CI uses
cd impl/claude
uv run mypy --strict --explicit-package-bases bootstrap/ agents/ runtime/
```

### Tests pass locally but fail in CI

- Check Python version differences (CI tests 3.11, 3.12, 3.13)
- Ensure dependencies are synced: `uv sync --all-extras`
- Check for environment-specific issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes (pre-commit hook runs automatically)
4. Ensure CI passes
5. Submit a pull request

## Resources

- [uv documentation](https://docs.astral.sh/uv/)
- [ruff documentation](https://docs.astral.sh/ruff/)
- [pytest documentation](https://docs.pytest.org/)
- [mypy documentation](https://mypy.readthedocs.io/)
