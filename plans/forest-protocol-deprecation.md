# Forest Protocol Deprecation Plan

**Status:** COMPLETE (2025-12-21)
**Priority:** HIGH
**Mood:** Cleanup
**Season:** COMPOSTING

> *"The forest was never planted. Time to acknowledge the clearing."*

---

## Summary

Deprecate and remove the Forest Protocol remnants. The Gardener-Evergreen system was already deleted (2025-12-21), but orphaned references remain:

- CLI handlers still exist and show in `kg --help`
- `self_.py` still references deleted `forest.py`, `garden.py`, `tend.py` contexts
- Commands fail at runtime with import errors

**Goal:** Clean removal of all Forest Protocol traces.

---

## Current State

### What Was Already Deleted (gardener-evergreen-deprecation.md)
- `protocols/agentese/contexts/forest.py`
- `protocols/agentese/contexts/garden.py`
- `protocols/agentese/contexts/tend.py`
- `protocols/agentese/contexts/gardener.py`
- `protocols/garden/` (entire directory)
- `protocols/gardener_logos/` (entire directory)
- Many synergy handlers and tests

### What Still Exists (Orphaned)

**CLI Handlers:**
- `protocols/cli/handlers/forest.py` - Routes to deleted nodes
- `protocols/cli/handlers/session.py` - Routes to `self.forest.session.*`
- `protocols/cli/handlers/gardener_thin.py` - Minimal stub

**Help System:**
- `protocols/cli/help_global.py` - Still lists `forest`, `garden`, `session`, `gardener`

**AGENTESE References:**
- `protocols/agentese/contexts/self_.py` (lines 969-988) - Imports deleted contexts
- `protocols/agentese/aliases.py` - May have forest aliases
- `protocols/agentese/subscription.py` - May have forest subscriptions
- `protocols/agentese/logos.py` - May reference forest paths
- `protocols/agentese/generated/garden.py` - JIT-generated stub

**Models:**
- `models/gardener.py` - May be unused

**Service Remnants:**
- `services/witness/session_walk.py` - References forest sessions
- `services/witness/walk.py` - May reference forest
- `agents/k/soul.py` - May reference forest
- `agents/k/garden.py` - Garden integration
- `agents/k/garden_sql.py` - SQL for garden

**Tests:**
- Various tests referencing forest/garden/session

**Docs:**
- `docs/cli-reference.md` - Lists forest commands
- `plans/_forest.md` - The meta file itself
- CLAUDE.md - References gardener in Crown Jewels

---

## Execution Phases

### Phase 1: Remove CLI Handlers

**Files to delete:**
```
protocols/cli/handlers/forest.py
protocols/cli/handlers/session.py
protocols/cli/handlers/gardener_thin.py
```

**Files to modify:**
- `protocols/cli/handlers/__init__.py` - Remove exports
- `protocols/cli/hollow.py` - Remove command routing

### Phase 2: Update Help System

**Already done in previous session:**
- `protocols/cli/help_global.py` - Forest commands already removed

**Verify:**
- `kg --help` shows no forest/garden/session/gardener commands

### Phase 3: Clean AGENTESE Self Context

**File: `protocols/agentese/contexts/self_.py`**

Remove lines 969-988:
```python
# Forest Protocol integration (Wave 2)
case "forest":
    # self.forest.* → ForestNode for plan management
    from .forest import create_forest_node
    return create_forest_node()
# Garden integration (Wave 2.5)
case "garden":
    # self.garden.* → GardenNode for garden state/seasons/health
    ...
```

### Phase 4: Clean Generated/Aliases

**Files to check:**
- `protocols/agentese/generated/garden.py` - Delete if JIT stub
- `protocols/agentese/aliases.py` - Remove forest aliases
- `protocols/agentese/subscription.py` - Remove forest subscriptions

### Phase 5: Clean Agent/Service Remnants

**Files to audit:**
- `agents/k/garden.py` - Check if used elsewhere
- `agents/k/garden_sql.py` - Check if used elsewhere
- `services/witness/session_walk.py` - Remove forest references
- `models/gardener.py` - Delete if unused

### Phase 6: Clean Documentation

**Files to update:**
- `docs/cli-reference.md` - Remove forest commands (DONE)
- `CLAUDE.md` - Remove gardener from Crown Jewels status
- `plans/_forest.md` - Archive or delete
- `docs/README.md` - Remove any forest references

### Phase 7: Run Tests, Fix Breakage

```bash
cd impl/claude && uv run pytest -x -q
```

Fix any import errors or test failures.

---

## Files Summary

### DELETE
```
protocols/cli/handlers/forest.py
protocols/cli/handlers/session.py
protocols/cli/handlers/gardener_thin.py
protocols/agentese/generated/garden.py
agents/k/garden.py (if unused)
agents/k/garden_sql.py (if unused)
models/gardener.py (if unused)
```

### MODIFY
```
protocols/agentese/contexts/self_.py (remove forest/garden cases)
protocols/agentese/aliases.py (remove forest aliases)
protocols/agentese/subscription.py (remove forest subscriptions)
protocols/cli/handlers/__init__.py (remove exports)
protocols/cli/hollow.py (remove routing)
services/witness/session_walk.py (remove forest refs)
CLAUDE.md (update Crown Jewels)
```

### ARCHIVE
```
plans/_forest.md → plans/_archive/
```

---

## Verification Checklist

- [x] `kg --help` shows no forest/garden/session/gardener
- [x] `kg forest` returns "command not found" (clean error)
- [x] `kg garden` returns "command not found"
- [x] `kg session` returns "command not found"
- [x] `kg gardener` returns "command not found"
- [x] `uv run pytest` passes (3381 tests)
- [x] No orphan imports referencing deleted modules
- [x] CLAUDE.md Crown Jewels section updated

## Execution Summary (2025-12-21)

**Files Deleted:**
- `protocols/cli/handlers/forest.py`
- `protocols/cli/handlers/session.py`
- `protocols/cli/handlers/gardener_thin.py`
- `protocols/cli/handlers/grow.py` (also orphaned)
- `protocols/cli/handlers/_tests/test_grow.py`
- `models/gardener.py` (orphaned DB models)

**Files Modified:**
- `protocols/cli/hollow.py` - Removed forest/session/gardener/grow commands
- `protocols/agentese/contexts/self_.py` - Removed forest/garden cases (lines 969-988)
- `protocols/agentese/aliases.py` - Removed forest alias
- `protocols/agentese/subscription.py` - Updated docstring examples
- `protocols/cli/contexts/time_.py` - Removed time.forest holon
- `protocols/cli/handlers/query.py` - Removed gardener/forest handler imports
- `models/__init__.py` - Removed gardener exports
- `docs/cli-reference.md` - Removed Forest Protocol section
- `CLAUDE.md` - Removed Gardener from Crown Jewels
- `HYDRATE.md` - Removed Gardener from Crown Jewels

**Files Archived:**
- `plans/_forest.md` → `plans/_archive/_forest-archived-2025-12-21.md`

**NOT Removed (Still Used):**
- `agents/k/garden.py` (PersonaGarden - K-gent soul memory, 25 files reference it)
- `agents/k/garden_sql.py` (SQL-backed PersonaGarden)

---

## Notes

**Why remove Forest Protocol?**
1. Gardener-Evergreen already deleted - Forest is orphaned
2. Commands fail at runtime - broken user experience
3. `kg --help` advertises commands that don't work
4. Simplifies codebase - less maintenance burden

**What replaces it?**
- Session management → Witness marks (`kg witness`)
- Plan tracking → Manual plans in `plans/`
- Morning ritual → `kg coffee` (separate from forest)

**Heritage preserved:**
- `spec/protocols/_archive/gardener-evergreen-heritage.md` (from previous deprecation)

---

*"The clearing is honest. The forest was never there."*
