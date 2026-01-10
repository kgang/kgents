---
description: Audit and report on technical debt in the codebase
argument-hint: [target-path]
---

Audit and report on technical debt in the codebase.

## Target: $ARGUMENTS

If no arguments provided, scan the entire codebase.

## Debt Detection

### Automated Scans

```bash
# TODOs and FIXMEs
grep -rn "TODO\|FIXME\|XXX\|HACK" --include="*.py"

# Type ignores
grep -rn "# type: ignore" --include="*.py"

# Bare excepts
grep -rn "except:" --include="*.py"

# Magic numbers/strings
grep -rn "sleep(.*[0-9]" --include="*.py"

# Skip markers in tests
grep -rn "pytest.mark.skip\|@skip" --include="*.py"
```

### Manual Patterns to Check

- [ ] Functions > 50 lines
- [ ] Classes > 300 lines
- [ ] Files > 500 lines
- [ ] Cyclomatic complexity > 10
- [ ] Deeply nested code (> 4 levels)
- [ ] Duplicate code blocks
- [ ] Dead code (unused functions/imports)
- [ ] Outdated comments
- [ ] Missing docstrings on public APIs

## Debt Categories

| Category | Severity | Example |
|----------|----------|---------|
| **Critical** | Must fix soon | Security issues, data loss risks |
| **High** | Should fix | Breaking abstractions, no tests |
| **Medium** | Plan to fix | Missing types, unclear code |
| **Low** | Nice to fix | Style issues, minor cleanup |
| **Accepted** | Intentional | Documented trade-offs |

## Output Format

```
[DEBT] Audit: <target>

Summary:
- Critical: <N>
- High: <N>
- Medium: <N>
- Low: <N>
- Accepted: <N>

Top Issues:

1. [HIGH] <file>:<line>
   Type: <category>
   Issue: <description>
   Suggested fix: <action>

2. [MEDIUM] <file>:<line>
   ...

Trends:
- <observation about debt patterns>
- <areas accumulating debt>

Recommendations:
1. <prioritized action>
2. <prioritized action>
```

## Debt Paydown Protocol

When fixing debt:

1. **Document first**: Note WHY the debt exists
2. **Test before fixing**: Prove current behavior
3. **Incremental**: Small fixes, frequent commits
4. **Track progress**: Update debt markers

## Arguments

- `<path>` — Audit specific path
- `--critical` — Only show critical issues
- `--by-file` — Group by file
- `--by-type` — Group by debt type
- `--json` — Output as JSON for tooling

## Examples

```
/debt agents/flux
/debt --critical
/debt protocols/cli --by-file
```
