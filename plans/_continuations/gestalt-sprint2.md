# Gestalt Sprint 2: Perception & Synergy (80% → 90%) ✅ COMPLETE

## Context
- **Sprint 1 Complete**: SSE streaming backend + `useGestaltStream` hook
- **Sprint 2 Complete**: Observer-dependent views + Drift synergy
- **Tests**: 189 passing (+43 new)
- **Goal**: Observer-dependent views + Brain synergy

## Sprint 2 Tasks

### 1. Observer Umwelts (4 roles)
```python
# protocols/gestalt/umwelt.py
class GestaltUmwelt(Enum):
    TECH_LEAD = "tech_lead"      # Health, drift, governance focus
    SECURITY = "security"        # Vulnerable deps, access paths
    PERFORMANCE = "performance"  # Bottlenecks, complexity hotspots
    PRODUCT = "product"          # Features, integration points
```

### 2. Role Query Param
- Add `?role=tech_lead|security|performance|product` to `/v1/world/codebase/topology`
- Filter/reweight metrics based on role
- Different nodes emphasized, different links visible

### 3. Web UI Role Selector
- Dropdown in Gestalt page header
- Smooth transition between views
- Persist selection in localStorage

### 4. Brain Synergy Handler
```python
# protocols/synergy/handlers/gestalt_brain.py
@on_event("gestalt.drift_detected")
async def capture_drift(event: DriftEvent):
    await logos("self.memory.capture", {
        "content": f"Drift: {event.source} → {event.target}",
        "metadata": {"jewel": "gestalt", "severity": event.severity}
    })
```

### 5. Auto-Capture Events
- Drift violations → Brain capture
- Health degradation (A→B, B→C) → Brain capture
- New module detected → Brain capture

## Files to Create/Modify

| File | Action |
|------|--------|
| `protocols/gestalt/umwelt.py` | Create |
| `protocols/api/gestalt.py` | Add role param |
| `protocols/synergy/handlers/gestalt_brain.py` | Extend |
| `web/src/pages/Gestalt.tsx` | Add role selector |

## Success Criteria
- Same codebase, 4 meaningfully different views
- Drift events auto-captured to Brain
- 15+ new tests

## Quick Start
```bash
cd impl/claude
uv run pytest protocols/gestalt/ -q  # Should see 146 pass
uv run pytest protocols/synergy/ -k gestalt -q  # Synergy tests
```

## Completion Summary

### Delivered

1. **GestaltUmwelt** (`protocols/gestalt/umwelt.py`)
   - 6 observer roles: tech_lead, developer, reviewer, product, security, performance
   - UmweltConfig with metric weights and visibility rules
   - Frontend observer → backend umwelt mapping

2. **Role Query Parameter** (`protocols/api/gestalt.py`)
   - `/v1/world/codebase/topology?role=architect`
   - Applies umwelt-based filtering and scoring
   - Returns umwelt config in response

3. **Drift Detection Handler** (`protocols/synergy/handlers/gestalt_brain.py`)
   - Handles DRIFT_DETECTED events
   - Creates drift violation crystals in Brain
   - Severity-tagged content with governance context

4. **Web Integration**
   - `gestaltApi.getTopology()` accepts role parameter
   - Gestalt.tsx passes observer to API
   - Observer changes trigger topology reload

### Test Coverage
- `test_umwelt.py`: 28 tests (roles, configs, filtering, scoring)
- `test_drift_handler.py`: 15 tests (events, handler, integration)
- **Total: 43 new tests**

### Files Created/Modified
| File | Action |
|------|--------|
| `protocols/gestalt/umwelt.py` | ✅ Created |
| `protocols/api/gestalt.py` | ✅ Modified |
| `protocols/synergy/events.py` | ✅ Modified |
| `protocols/synergy/handlers/gestalt_brain.py` | ✅ Modified |
| `web/src/api/client.ts` | ✅ Modified |
| `web/src/api/types.ts` | ✅ Modified |
| `web/src/pages/Gestalt.tsx` | ✅ Modified |

---
*Sprint 1 completed: 2025-12-16*
*Sprint 2 completed: 2025-12-16*
