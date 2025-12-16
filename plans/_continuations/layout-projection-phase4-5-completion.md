# Continuation Prompt: Layout Projection Functor → 100%

> Use this prompt to complete the Layout Projection Functor plan by implementing Phase 4 (Gallery Pilots) and Phase 5 (AGENTESE Integration).

---

## Context

The Layout Projection Functor implementation is at 85% completion. Phases 1-3 are fully implemented with 169 passing tests. The remaining work is:

- **Phase 4**: Gallery pilots demonstrating layout projection (0/8 pilots)
- **Phase 5**: AGENTESE integration with Umwelt layout capacity (0/5 paths)

**Plan File**: `plans/web-refactor/layout-projection-functor.md`
**Elastic Components**: `impl/claude/web/src/components/elastic/`
**Types**: `impl/claude/web/src/components/elastic/types.ts`

---

## The Prompt

```
Continue working on plans/web-refactor/layout-projection-functor.md to bring it to 100%.

## Current State (85% Complete)

### What's Done
- Canonical types in `elastic/types.ts`: Density, LayoutHints, DensityMap, PHYSICAL_CONSTRAINTS
- BottomDrawer and FloatingActions components extracted and spec-compliant
- Gestalt.tsx and Brain.tsx refactored to use elastic/ components
- 169 tests passing including edge cases for density boundaries
- Composition laws verified: 4/4

### What Remains

#### Phase 4: Projection Gallery Extension (8 pilots needed)

Create layout pilots in a gallery that demonstrate the structural isomorphism between compact and spacious layouts.

**Location**: `impl/claude/web/src/pages/Workshop.tsx` or new `GalleryPage.tsx`

**Required Pilots** (from plan):

| Pilot | Description | Demonstrates |
|-------|-------------|--------------|
| `panel_sidebar` | Panel in sidebar mode | Spacious layout |
| `panel_drawer` | Same panel as drawer | Compact layout |
| `panel_isomorphism` | Side-by-side comparison | Structural isomorphism |
| `actions_toolbar` | Actions as toolbar | Spacious layout |
| `actions_fab` | Same actions as FAB | Compact layout |
| `split_resizable` | Split with drag handle | Desktop layout |
| `split_collapsed` | Same split collapsed | Mobile layout |
| `touch_targets` | 48px minimum demo | Physical constraints |

**Implementation Pattern**:
```tsx
// Each pilot should be a self-contained component
function PanelSidebarPilot() {
  return (
    <div className="pilot-container">
      <h3>Panel (Spacious Mode)</h3>
      <div style={{ width: 1200 }}> {/* Force spacious */}
        <ElasticSplit primary={<MainContent />} secondary={<SidePanel />} />
      </div>
    </div>
  );
}

function PanelDrawerPilot() {
  const [open, setOpen] = useState(false);
  return (
    <div className="pilot-container">
      <h3>Panel (Compact Mode)</h3>
      <div style={{ width: 400 }}> {/* Force compact */}
        <MainContent />
        <FloatingActions actions={[{ id: 'panel', icon: '📋', label: 'Open Panel', onClick: () => setOpen(true) }]} />
        <BottomDrawer isOpen={open} onClose={() => setOpen(false)} title="Panel">
          <SidePanel />
        </BottomDrawer>
      </div>
    </div>
  );
}

// Isomorphism pilot shows both side-by-side
function PanelIsomorphismPilot() {
  return (
    <div className="flex gap-8">
      <div className="flex-1">
        <PanelSidebarPilot />
        <p className="text-sm text-gray-500">Spacious: Fixed sidebar</p>
      </div>
      <div className="flex-1">
        <PanelDrawerPilot />
        <p className="text-sm text-gray-500">Compact: Bottom drawer (same content)</p>
      </div>
    </div>
  );
}
```

#### Phase 5: AGENTESE Integration (5 paths needed)

Extend the AGENTESE umwelt to include layout capacity, so agent perceptions can vary based on device/density.

**Location**: `impl/claude/protocols/agentese/contexts/projection.py`

**Required Paths**:
1. `self.layout.density` → Current density accessor
2. `self.layout.modality` → Current interaction modality (touch|pointer)
3. `world.panel.manifest(umwelt)` → Layout-appropriate panel projection
4. `world.actions.manifest(umwelt)` → FAB vs toolbar based on density
5. `world.split.manifest(umwelt)` → Collapse vs resize based on density

**Implementation Pattern**:
```python
from dataclasses import dataclass
from enum import Enum
from typing import Literal

class Density(Enum):
    COMPACT = "compact"
    COMFORTABLE = "comfortable"
    SPACIOUS = "spacious"

class Modality(Enum):
    TOUCH = "touch"
    POINTER = "pointer"

@dataclass(frozen=True)
class PhysicalCapacity:
    """Physical constraints of the observer's device."""
    density: Density
    modality: Modality
    bandwidth: Literal["low", "medium", "high"] = "high"

@dataclass(frozen=True)
class LayoutUmwelt:
    """Umwelt extension for layout-aware perception."""
    observer_id: str
    capacity: PhysicalCapacity

# AGENTESE path handlers
async def self_layout_density(ctx: AgentContext) -> Density:
    """self.layout.density → Current density level."""
    return ctx.umwelt.capacity.density

async def world_panel_manifest(ctx: AgentContext) -> dict:
    """world.panel.manifest → Layout-appropriate panel projection."""
    density = ctx.umwelt.capacity.density
    if density == Density.COMPACT:
        return {"layout": "drawer", "trigger": "floating_action", "touch_target": 48}
    elif density == Density.COMFORTABLE:
        return {"layout": "collapsible", "trigger": "toggle_button"}
    else:
        return {"layout": "sidebar", "resizable": True, "min_width": 200}
```

## Success Criteria

To reach 100%, the plan needs:

| Metric | Current | Target |
|--------|---------|--------|
| Gallery layout pilots | 0 | 8+ |
| AGENTESE paths with layout | 0 | 5+ |

## Phase Order

1. **Phase 4 first**: Gallery pilots provide visual demonstration
2. **Phase 5 second**: AGENTESE integration adds semantic layer
3. **EDUCATE phase**: Documentation using gallery as examples

## Testing Requirements

**Phase 4 Tests** (in `tests/unit/gallery/` or similar):
- Each pilot renders without error
- Pilots show correct layout at correct density
- Isomorphism pilots preserve same information

**Phase 5 Tests** (in `protocols/agentese/_tests/`):
- `self.layout.density` returns correct density from umwelt
- `world.panel.manifest` varies by density
- `world.actions.manifest` varies by density
- All 5 paths registered and invocable

## Update Plan File

After completing each phase:
1. Update `phase_ledger` to mark phases complete
2. Update `progress` to 95% after Phase 4, 100% after Phase 5
3. Add session notes documenting pilots and paths created
4. Mark EDUCATE as complete once gallery is documented
```

---

## Exit Criteria

The plan is 100% complete when:
- [ ] 8 gallery pilots implemented and rendering
- [ ] 5 AGENTESE paths implemented with tests
- [ ] EDUCATE phase documented
- [ ] Plan file updated with `progress: 100` and all phases `complete`

---

## References

- **Spec**: `spec/protocols/projection.md` (lines 213-424)
- **Plan**: `plans/web-refactor/layout-projection-functor.md`
- **Types**: `impl/claude/web/src/components/elastic/types.ts`
- **Components**: `impl/claude/web/src/components/elastic/`
- **AGENTESE**: `impl/claude/protocols/agentese/`
- **Skills**: `docs/skills/projection-gallery.md`, `docs/skills/agentese-path.md`
