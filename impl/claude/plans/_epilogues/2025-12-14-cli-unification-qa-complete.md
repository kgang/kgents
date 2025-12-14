# CLI Unification QA Complete

**Date**: 2025-12-14
**Phase**: QA (7/11)
**Plan**: `plans/devex/cli-unification.md`

---

## Summary

QA phase completed for AGENTESE CLI convergence. All static analysis passes,
deprecation warnings implemented for 69 legacy commands, and full test suite green.

---

## QA Findings

### 1. Type Errors Fixed (7 total)

Found and fixed handler signature mismatches in context routers:

| File | Handler | Issue |
|------|---------|-------|
| `contexts/time_.py` | `cmd_forest` | Was passing ctx to handler that doesn't accept it |
| `contexts/concept.py` | `cmd_laws` | Same issue |
| `contexts/concept.py` | `cmd_principles` | Same issue |
| `contexts/world.py` | `cmd_daemon` | Same issue |
| `contexts/world.py` | `cmd_infra` | Same issue |
| `contexts/world.py` | `cmd_exec` | Same issue |
| `contexts/world.py` | `cmd_dev` | Same issue |

**Resolution**: Updated context routers to only pass `args` (not `ctx`) to handlers
that don't support the InvocationContext parameter.

### 2. Static Analysis Results

| Tool | Status | Files Checked |
|------|--------|---------------|
| mypy | PASS | 7 context files |
| ruff | PASS | 7 context files |

### 3. Test Results

```
1309 passed, 1 skipped in 49.74s
```

All CLI tests pass including the 20 hollow.py tests.

### 4. Deprecation Warnings Implemented

Added deprecation infrastructure to `hollow.py`:

- **DEPRECATION_MAP**: 69 commands mapped to AGENTESE paths
- **_emit_deprecation_warning()**: Emits yellow warning to stderr
- **resolve_command()**: Now checks deprecation map before loading

Example warning:
```
⚠ Deprecated: 'kgents soul' → 'kgents self soul'
```

#### Deprecation Categories

| Context | Commands | Example |
|---------|----------|---------|
| self.* | 14 | `soul` → `self soul` |
| world.* | 13 | `a` → `world agents` |
| concept.* | 7 | `laws` → `concept laws` |
| void.* | 6 | `shadow` → `void shadow` |
| time.* | 9 | `trace` → `time trace` |
| do.* | 9 | `run` → `do run` |
| No change | 11 | `init`, genus commands, viz |

### 5. Circular Import Check

✓ All 5 context routers import successfully
✓ No circular dependencies detected

---

## Exit Criteria Met

- [x] `uv run mypy protocols/cli/contexts/` passes
- [x] `uv run ruff check protocols/cli/contexts/` passes
- [x] Full test suite passes (1309/1309)
- [x] Deprecation warnings added (69 commands)
- [x] No circular imports

---

## Next Phase: TEST

Focus: Integration testing of new AGENTESE paths

1. Test `kgents self` subcommands
2. Test `kgents world` subcommands
3. Test `kgents concept` subcommands
4. Test `kgents void` subcommands
5. Test `kgents time` subcommands
6. Verify deprecation warnings display correctly
7. Test backward compatibility

---

## Entropy Accounting

- **Planned**: 0.06
- **Spent**: 0.04 (fixing type errors, implementing deprecation)
- **Returned**: 0.02 (clean abstractions, reusable patterns)

---

*"The noun is a lie. There is only the rate of change."* — AGENTESE
