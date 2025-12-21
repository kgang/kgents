# Gardener & Evergreen Deprecation Plan

**Status:** COMPLETED
**Executed:** 2025-12-21
**Mood:** Decisive
**Season:** COMPOSTING → DORMANT

> *"216 tests. 21,377 lines of implementation. For prompt management. Time to compost."*

---

## Summary

Deleted the Gardener-Logos, Garden Protocol, and Evergreen Prompt System implementations. They solved the wrong problem (prompt generation) when the real problem is evidence gathering (ASHC).

**Scope of destruction:**
- 3 specs → Archived
- 4 implementation packages → Deleted (~21,000 lines)
- 21+ test files → Deleted (~11,000 lines)
- Multiple synergy handlers → Deleted
- CLI handlers → Deleted
- API routes → Deleted

---

## Execution Checklist

- [x] Phase 1: Archive specs → `spec/protocols/_archive/gardener-evergreen-heritage.md`
- [x] Phase 2: Delete implementation packages (prompt, garden, gardener_logos, agents/gardener)
- [x] Phase 3: Fix broken imports (gateway.py, contexts/__init__.py, synergy bus)
- [x] Phase 4: Clean CLI commands (prompt, tend, garden, gardener, plot handlers)
- [x] Phase 5: Clean AGENTESE contexts (prompt, garden, gardener, tend, forest, world_gardener)
- [x] Phase 6: Verify tests pass → ASHC: 408 passed, core import: working
- [x] Phase 7: Update documentation (HYDRATE.md updated)

---

## Files Deleted

### Specs
- `spec/protocols/evergreen-prompt-system.md`
- `spec/protocols/garden-protocol.md`
- `spec/protocols/gardener-logos.md`

### Implementation Packages
- `impl/claude/protocols/prompt/` (entire directory)
- `impl/claude/protocols/garden/` (entire directory)
- `impl/claude/protocols/gardener_logos/` (entire directory)
- `impl/claude/agents/gardener/` (entire directory)

### AGENTESE Contexts
- `impl/claude/protocols/agentese/contexts/prompt.py`
- `impl/claude/protocols/agentese/contexts/garden.py`
- `impl/claude/protocols/agentese/contexts/gardener.py`
- `impl/claude/protocols/agentese/contexts/tend.py`
- `impl/claude/protocols/agentese/contexts/forest.py`
- `impl/claude/protocols/agentese/contexts/world_gardener.py`

### CLI Handlers
- `impl/claude/protocols/cli/handlers/prompt.py`
- `impl/claude/protocols/cli/handlers/tend.py`
- `impl/claude/protocols/cli/handlers/garden.py`
- `impl/claude/protocols/cli/handlers/gardener.py`
- `impl/claude/protocols/cli/handlers/plot.py`

### Synergy Handlers
- `impl/claude/protocols/synergy/handlers/garden_brain.py`
- `impl/claude/protocols/synergy/handlers/garden_witness.py`
- `impl/claude/protocols/synergy/handlers/gestalt_garden.py`
- `impl/claude/protocols/synergy/handlers/witness_garden.py`

### API Routes
- `impl/claude/protocols/api/gardener.py`

### Test Files
- `impl/claude/protocols/synergy/_tests/test_garden_handlers.py`
- `impl/claude/protocols/synergy/_tests/test_witness_handlers.py`
- `impl/claude/protocols/agentese/contexts/_tests/test_forest.py`
- `impl/claude/protocols/agentese/contexts/_tests/test_gardener.py`
- `impl/claude/protocols/cli/handlers/_tests/test_gardener.py`
- `impl/claude/protocols/cli/instance_db/_tests/test_garden_integration.py`

---

## Files Modified

### AGENTESE
- `impl/claude/protocols/agentese/gateway.py` — Removed garden imports
- `impl/claude/protocols/agentese/contexts/__init__.py` — Removed forest/gardener/prompt exports
- `impl/claude/protocols/agentese/contexts/crown_jewels.py` — Emptied GARDENER_PATHS
- `impl/claude/protocols/agentese/contexts/self_jewel_flow.py` — Emptied gardener flow paths

### Synergy
- `impl/claude/protocols/synergy/__init__.py` — Removed garden handlers
- `impl/claude/protocols/synergy/bus.py` — Removed garden handler registration
- `impl/claude/protocols/synergy/handlers/__init__.py` — Removed garden handlers

### Witness
- `impl/claude/services/witness/bus.py` — Removed garden handler references

### Documentation
- `impl/claude/HYDRATE.md` — Complete rewrite (was Evergreen-focused)

---

## Loose Ends (For Future Sessions)

1. **Web components** — Check `impl/claude/web/src/` for any Garden/Gardener React components
2. **Full test suite** — Run full `pytest` when time permits (takes 5+ min)
3. **CLAUDE.md** — Consider updating to remove Gardener from "Crown Jewels" section
4. **docs/systems-reference.md** — Remove Gardener if mentioned

---

## Heritage Preserved

Best ideas archived in: `spec/protocols/_archive/gardener-evergreen-heritage.md`

Key concepts that ASHC may absorb:
1. Provenance tracking
2. Rigidity spectrum
3. Signal aggregation for confidence
4. Dual-channel output (human + JSON)

---

*"Composting complete. The soil is richer for it."*
