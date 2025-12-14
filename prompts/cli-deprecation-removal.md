# CLI Deprecation Removal: Full Extraction

> **Process**: 11-phase cycle (AD-005)
> **Skill Reference**: `docs/skills/n-phase-cycle/README.md`
> **Plan Reference**: `plans/devex/cli-unification.md` (predecessor, complete)
> **Previous**: `impl/claude/plans/_epilogues/2025-12-14-cli-unification-reflect.md`

---

## Hydration Block

/hydrate
see plans/devex/cli-unification.md (complete)
see protocols/cli/hollow.py:DEPRECATION_MAP (69 commands)
see protocols/cli/contexts/ (5 context routers)

handles: scope=cli-deprecation-removal; phase=PLAN; ledger={PLAN:active,RESEARCH:pending,DEVELOP:pending,STRATEGIZE:pending,CROSS-SYNERGIZE:pending,IMPLEMENT:pending,QA:pending,TEST:pending,EDUCATE:pending,MEASURE:pending,REFLECT:pending}; entropy=0.08
mission: Remove deprecated CLI commands; AGENTESE contexts become the ONLY interface.
actions:
- SENSE: Map all 69 deprecated commands to removal strategy
- ACT: Remove command registrations, update tests, clean handlers
- REFLECT: Document migration complete, measure CLI simplification
exit: DEPRECATION_MAP empty; only context commands remain; all tests pass.
⟂[BLOCKED:breaking_change] if external consumers depend on old paths
⟂[BLOCKED:test_failure] if removal breaks critical tests

---

## Context

### What Was Done (CLI Unification Complete)
- Created 5 context routers: self, world, concept, void, time (1,020 lines)
- Added DEPRECATION_MAP with 69 commands → AGENTESE paths
- Deprecation warnings emit on stderr when old commands used
- All 1309 tests pass
- Startup time: 13.7ms (target <50ms)

### What Remains (This Cycle)
The deprecation warnings have been in place. Now we remove the deprecated commands entirely:

1. **Remove from COMMAND_REGISTRY** - The 69 deprecated entries
2. **Update/remove handler files** - Handlers only accessed via contexts
3. **Update tests** - Tests should use new AGENTESE paths
4. **Clean up DEPRECATION_MAP** - No longer needed after removal
5. **Update documentation** - Remove "Legacy Commands" section

---

## Scope

### In Scope
- Remove 69 deprecated command registrations from `hollow.py`
- Audit handler files - which can be deleted vs. kept for context delegation
- Update all tests to use AGENTESE paths
- Remove DEPRECATION_MAP after removal complete
- Update `docs/cli-reference.md` to remove legacy section

### Out of Scope
- Adding new commands
- Changing context router structure
- Performance optimization beyond removal

### Non-Goals
- Backward compatibility shims (the deprecation period is ending)
- New features or enhancements
- Refactoring handler internals

---

## Attention Budget

| Phase | Budget | Focus |
|-------|--------|-------|
| PLAN | 5% | This prompt |
| RESEARCH | 15% | Map command→handler→test dependencies |
| DEVELOP | 10% | Define removal contract |
| STRATEGIZE | 10% | Sequence removals (leaf→root) |
| CROSS-SYNERGIZE | 5% | Check agent-town, SaaS API impacts |
| IMPLEMENT | 30% | Execute removals |
| QA | 10% | Lint, type, security checks |
| TEST | 10% | Verify all tests pass with new paths |
| EDUCATE | 2% | Final doc cleanup |
| MEASURE | 2% | Before/after metrics |
| REFLECT | 1% | Learnings |

---

## Exit Criteria

### Must Have
1. `DEPRECATION_MAP` removed from `hollow.py`
2. `COMMAND_REGISTRY` contains ONLY:
   - `self`, `world`, `concept`, `void`, `time` (Tier 1)
   - `do`, `flow` (Intent/Pipeline - staying)
   - `init`, `wipe` (Bootstrap - staying)
3. All tests pass (may need updates to use new paths)
4. No orphaned handler files

### Should Have
1. Handler line count reduced by 20%+
2. `docs/cli-reference.md` simplified
3. Startup time maintained (<50ms)

### Won't Have
1. New commands
2. New deprecations

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| External scripts using old paths | Medium | High | Announce in CHANGELOG, version bump |
| Tests hardcoded to old paths | High | Low | Grep and update systematically |
| Handler deletion breaks contexts | Low | High | Verify context imports before deletion |
| Circular import after cleanup | Low | Medium | Test imports in isolation |

---

## Removal Categories

### Category A: Pure Aliases (Safe to Remove)
Commands that are pure aliases to context paths - remove registration only.

```python
# These just delegate, safe to remove from registry:
"soul": "protocols.cli.handlers.soul:cmd_soul"  # → self soul
"reflect": "protocols.cli.handlers.soul:cmd_reflect"  # → self soul reflect
"status": "protocols.cli.handlers.status:cmd_status"  # → self status
```

### Category B: Handler Still Needed (Remove Registration, Keep Handler)
The handler is imported by context routers - remove registry entry but keep file.

```python
# Context routers import these:
"trace": "protocols.cli.handlers.trace:cmd_trace"  # imported by time_.py
"laws": "protocols.cli.bootstrap.laws:cmd_laws"  # imported by concept.py
```

### Category C: Orphaned Handlers (Remove Registration AND Handler)
After removal, if no context router imports the handler, delete the file.

```
# Audit needed - check which handlers become orphaned
```

---

## Phase Roadmap

### RESEARCH (Next)
```
⟿[RESEARCH]
handles: scope=cli-deprecation-removal; phase=RESEARCH; ledger={PLAN:touched,RESEARCH:active}; entropy=0.07
mission: Map all 69 commands to categories (A/B/C); identify orphaned handlers.
actions:
- Grep COMMAND_REGISTRY for all 69 deprecated entries
- For each, check if context router imports the handler
- Categorize: alias-only / imported / orphaned
- Map test files that use old command paths
exit: Categorized list; test file map; ready for DEVELOP.
```

### DEVELOP
```
Define removal contract:
- COMMAND_REGISTRY entries to remove (list)
- Handler files to keep (imported by contexts)
- Handler files to delete (orphaned)
- Test files to update (use new paths)
```

### STRATEGIZE
```
Sequence the work:
1. Update tests FIRST (so they pass after removal)
2. Remove COMMAND_REGISTRY entries
3. Delete orphaned handlers
4. Remove DEPRECATION_MAP
5. Update docs
```

### CROSS-SYNERGIZE
```
Check for impacts:
- agent-town CLI commands
- SaaS API endpoints
- MCP server commands
- Any external scripts in docs/examples
```

### IMPLEMENT
```
Execute in order:
1. Batch update tests to AGENTESE paths
2. Remove entries from COMMAND_REGISTRY
3. Delete orphaned handler files
4. Remove DEPRECATION_MAP and _emit_deprecation_warning
5. Simplify HELP_TEXT
```

### QA
```
Run checks:
- uv run mypy protocols/cli/
- uv run ruff check protocols/cli/
- Check for unused imports
- Verify no broken imports
```

### TEST
```
Run full suite:
- uv run pytest protocols/cli/ -v
- Verify startup time still <50ms
- Manual smoke test of context commands
```

### EDUCATE
```
Update docs:
- Remove "Legacy Commands (Deprecated)" section
- Update any examples using old paths
- Add migration note to CHANGELOG
```

### MEASURE
```
Capture metrics:
- Lines removed from hollow.py
- Handler files deleted
- Test file changes
- Final command count
```

### REFLECT
```
Document:
- What patterns emerged
- Any surprises
- Seeds for future work
```

---

## Entropy Budget

| Draw | Return |
|------|--------|
| 0.08 (planned) | Cleaner codebase, simpler mental model |

The entropy cost is justified by the permanent simplification.

---

## Quick Start

To begin this cycle:

```bash
# 1. Read this prompt
# 2. Confirm scope is understood
# 3. Proceed to RESEARCH phase

/hydrate
see prompts/cli-deprecation-removal.md
```

---

## Signifiers

After PLAN review:
```
⟿[RESEARCH]
```

If scope concerns:
```
⟂[BLOCKED:scope_unclear] Need clarification on which commands to preserve
```

---

*"The noun is a lie. There is only the rate of change."* — AGENTESE

*Deprecation was the warning. Removal is the follow-through.*
