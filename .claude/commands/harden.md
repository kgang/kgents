Harden, robustify, and shore up the specified target. Apply defensive engineering.

## Target: $ARGUMENTS

If no arguments provided, ask which module/feature to harden.

## Hardening Protocol

### Phase 1: Reconnaissance (Read-Only)

1. **Identify scope**: Find all files related to the target
2. **Assess test coverage**: Count tests, check for gaps
3. **Check types**: Run mypy on target, note any `# type: ignore`
4. **Review error handling**: Look for bare `except:`, missing edge cases
5. **Scan TODOs/FIXMEs**: Catalog technical debt markers

### Phase 2: Analysis Report

Before making changes, produce a brief report:

```
[HARDEN] Target: <target>
Files: <count> | Tests: <count> | Type coverage: <%>

Findings:
- [ ] <Issue 1>: <description>
- [ ] <Issue 2>: <description>
...

Risk Assessment: Low | Medium | High
Recommended Actions: <prioritized list>
```

### Phase 3: Hardening Actions (With Permission)

After analysis, propose and execute (with user approval):

| Category | Actions |
|----------|---------|
| **Durability** | Add missing error handling, retry logic, graceful degradation |
| **Type Safety** | Add/fix type annotations, remove `# type: ignore` where possible |
| **Edge Cases** | Handle None, empty, boundary conditions |
| **Tests** | Add missing tests, especially for error paths |
| **Documentation** | Add docstrings, update inline comments, note gotchas |
| **Defensive Code** | Input validation, assertion guards, invariant checks |
| **Future Signifiers** | Add `# TODO(future):` markers for known extensions |
| **Cross-Synergy** | Note integration opportunities, add compatibility shims |

### Phase 4: Verification

1. Run tests: `uv run pytest <target_tests> -v`
2. Run mypy: `uv run mypy <target_files>`
3. Verify no regressions
4. Document changes in session notes

## Hardening Principles

From spec/principles.md:

- **Minimal intervention**: Fix what's broken, don't over-engineer
- **Preserve behavior**: No functional changes unless fixing bugs
- **Test first**: Add test before fixing, to prove the issue exists
- **Communicate**: Document WHY something was hardened, not just WHAT

## Future Feature Signifiers

When you see potential extensions, mark them clearly:

```python
# TODO(future): Support batch operations when needed
# TODO(future): Add caching layer for performance
# EXTENSION_POINT: Additional handlers can register here
```

## Output Format

End with a summary:

```
[HARDEN] Complete

Changes:
- <file>: <what changed>
- <file>: <what changed>

Tests: <before> → <after>
Type coverage: <before> → <after>

Remaining debt:
- <item that couldn't be addressed>
```

## Arguments

The target to harden. Examples:
- `agents/flux` — Harden the Flux agent system
- `protocols/agentese` — Harden AGENTESE paths
- `protocols/cli/handlers/soul.py` — Harden a specific file
- `self.semaphore.*` — Harden by AGENTESE path
