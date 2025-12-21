# Witness Primitives Rename: Execution Strategy

> *"Every action leaves a mark. Every mark joins a walk. Every walk follows a playbook."*

## Overview

This document outlines a programmatic, multi-phase approach to renaming Witness primitives from research-artifact names to intuitive names.

| Old Name | New Name | Rationale |
|----------|----------|-----------|
| Covenant | Grant | "Grant of permission" - OAuth-adjacent, clear |
| Offering | Scope | "What's in scope" - immediately understood |
| Ritual | Playbook | Action-oriented; what a coach follows |
| TraceNode | Mark | "Every action leaves a mark" - short, evocative |
| Terrace | Lesson | "Lessons learned" - direct, no metaphor needed |

**Scope**: ~539 occurrences across ~43 files

---

## Phase 1: Foundation (DONE)

The core primitive files have already been renamed with backwards compatibility:

```
services/witness/covenant.py → services/witness/grant.py ✓
services/witness/offering.py → services/witness/scope.py ✓
services/witness/ritual.py   → services/witness/playbook.py ✓
services/witness/trace_node.py → services/witness/mark.py ✓
services/witness/terrace.py  → services/witness/lesson.py ✓
```

Each new file exports:
- New names (Grant, Scope, Playbook, Mark, Lesson)
- Backwards compat aliases (Covenant = Grant, etc.)
- Property aliases on Playbook (covenant_id, offering_id)

---

## Phase 2: Consumer Updates (NEXT)

Use the programmatic rename tool to update all consuming code:

```bash
# Step 1: Analyze what will change
python /tmp/witness_rename.py --analyze --verbose

# Step 2: Execute the renames
python /tmp/witness_rename.py --execute

# Step 3: Verify tests pass
python /tmp/witness_rename.py --verify
```

### Files to Update

**AGENTESE Contexts** (heaviest changes):
- `self_ritual.py` - 110+ changes (Covenant→Grant, Offering→Scope, Ritual→Playbook)
- `self_covenant.py` - 55+ changes
- `concept_offering.py` - 46+ changes
- `brain_terrace.py` - 28+ changes
- `time_trace_warp.py` - 19+ changes

**AGENTESE Tests**:
- `test_ritual_integration.py` - 68+ changes
- `test_gateway.py` - 15 changes
- `test_warp_nodes.py` - 14 changes

**Projection Layer**:
- `warp_converters.py` - 28 changes
- `scene.py` - 5 changes

---

## Phase 3: API Alignment (CAREFUL)

Some old types had APIs that differ from new types. These need individual attention:

### Missing Properties (add backwards compat)

```python
# In playbook.py - Playbook class:
@property
def current_step(self) -> int:
    """Backwards compat: phases are the new steps."""
    return self.phase_history[-1] if self.phase_history else 0

@property
def total_steps(self) -> int:
    """Backwards compat: count of phases."""
    return len(self.phases)
```

### Missing Methods

```python
# In grant.py - Grant class:
@property
def trust_level(self) -> str:
    """Backwards compat: derive from status."""
    if self.status == GrantStatus.GRANTED:
        return "high"
    return "low"

@property
def proposed_at(self) -> datetime:
    """Backwards compat: alias for created_at."""
    return self.created_at
```

```python
# In scope.py - Scope class:
@property
def kind(self) -> str:
    """Backwards compat: all scopes are 'resource' kind."""
    return "resource"

@property
def scope(self) -> tuple[str, ...]:
    """Backwards compat: alias for scoped_handles."""
    return self.scoped_handles
```

---

## Phase 4: Verification

```bash
# Run all witness tests
uv run pytest services/witness/ -x -q --tb=short

# Run AGENTESE tests
uv run pytest protocols/agentese/ -x -q --tb=short

# Type check
uv run mypy protocols/agentese/ services/witness/ --no-error-summary

# Full test suite
uv run pytest -x -q --tb=short
```

---

## Phase 5: Cleanup

After verification passes:

1. **Remove backwards compat aliases** (optional, can leave for gradual migration)
2. **Update docstrings** to use new terminology
3. **Update specs** in `spec/protocols/witness-primitives.md`
4. **Commit and push**

---

## The Rename Tool

Location: `/tmp/witness_rename.py`

```bash
# Usage
python /tmp/witness_rename.py --analyze       # Show what would change
python /tmp/witness_rename.py --execute       # Make changes
python /tmp/witness_rename.py --dry-run       # Preview execute
python /tmp/witness_rename.py --verify        # Run tests
```

The tool:
1. Uses regex with word boundaries for safe replacement
2. Orders renames from specific to general (CovenantId before Covenant)
3. Skips the core primitive files (they have compat aliases)
4. Processes only relevant directories

---

## Execution Order

```
Phase 1: Foundation ✓ (DONE)
   └── Core files renamed with backwards compat

Phase 2: Consumer Updates (10 min)
   └── Run rename tool on consuming code

Phase 3: API Alignment (20 min)
   └── Add missing properties to new types

Phase 4: Verification (5 min)
   └── Run tests, fix any issues

Phase 5: Commit (2 min)
   └── Single atomic commit with all changes
```

---

## Rollback Plan

If something goes wrong:

```bash
# Restore all witness-related files
git checkout -- services/witness/ protocols/agentese/

# Or use stash
git stash
```

---

*"The name is not the thing, but a good name makes the thing findable."*
