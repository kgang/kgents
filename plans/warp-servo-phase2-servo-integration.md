---
path: warp-servo/phase2-servo-integration
status: dormant
progress: 0
last_touched: 2025-12-20
touched_by: claude-opus-4
blocking: [warp-servo/phase0-research, warp-servo/phase1-core-primitives]
enables: [warp-servo/phase3-jewel-refinement]
session_notes: |
  Initial creation. Servo projection substrate implementation.
  Depends on Phase 0 research (Servo viability) and Phase 1 (primitives).
phase_ledger:
  PLAN: complete
  DEVELOP: pending
  IMPLEMENT: pending
  TEST: pending
entropy:
  planned: 0.4
  spent: 0.0
  returned: 0.0
---

# Phase 2: Servo Projection Substrate Integration

> *"Servo is not 'a browser' inside kgents. It is the projection substrate that renders the ontology."*

**AGENTESE Context**: `world.terrarium.view.*` + projection targets
**Status**: Dormant (0 tests)
**Principles**: Composable (scene graphs), Joy-Inducing (breathing surfaces), Heterarchical (multi-webview)
**Cross-refs**: `spec/protocols/servo-substrate.md`, Phase 0/1 outputs

---

## Core Insight

Servo replaces the webapp as the **primary projection surface**. This phase implements:
1. Servo projection target registration
2. ServoScene graph primitives
3. TerrariumView multi-webview
4. TraceNode playback UI
5. Intent-based navigation

---

## Decision Gate

**⚠️ This phase depends on Phase 0 research outcomes.**

If Servo embedding is not viable in 2025:
- Fallback: Enhance existing React webapp with WARP primitives
- Fallback: Use Tauri + webview with Servo-like abstractions
- Keep ServoScene as abstract spec; implement in React first

---

## Chunks

### Chunk 1: Servo Projection Target (2-3 hours)

**Goal**: Register Servo as a projection target with fidelity 0.95.

**Files**:
```
impl/claude/protocols/agentese/projection/servo.py
impl/claude/protocols/agentese/projection/_tests/test_servo.py
```

**Tasks**:
- [ ] Register `servo` target in ProjectionRegistry
- [ ] Implement `servo_projector(widget) -> ServoScene`
- [ ] Set fidelity=0.95 (MAXIMUM)
- [ ] Implement fallback chain: servo → marimo → tui → cli → json
- [ ] Test with existing KgentsWidget implementations

**Code Skeleton**:
```python
@ProjectionRegistry.register(
    "servo",
    fidelity=0.95,
    description="Servo browser engine substrate"
)
def servo_projector(widget: KgentsWidget) -> ServoScene:
    """Convert widget state to ServoScene graph."""
    return ServoScene(
        nodes=widget_to_servo_nodes(widget),
        layout=infer_layout(widget),
        style=get_servo_stylesheet(),
        animations=infer_animations(widget),
    )
```

**Exit Criteria**: 5+ tests pass, any widget projects to Servo.

---

### Chunk 2: ServoScene Graph Primitives (3-4 hours)

**Goal**: Implement ServoScene graph structure.

**Files**:
```
impl/claude/protocols/agentese/projection/servo_primitives.py
impl/claude/protocols/agentese/projection/_tests/test_servo_primitives.py
```

**Tasks**:
- [ ] Implement `ServoScene` dataclass
- [ ] Implement `ServoNode` with kinds (PANEL, TRACE, INTENT, etc.)
- [ ] Implement `ServoEdge` for graph connections
- [ ] Implement `LayoutDirective` (elastic layouts)
- [ ] Implement `StyleSheet` (Living Earth palette)
- [ ] Implement `Animation` (breathing, unfurling)

**ServoNode Kinds**:
```python
class ServoNodeKind(Enum):
    PANEL = auto()       # Container with borders
    TRACE = auto()       # TraceNode visualization
    INTENT = auto()      # IntentTree node
    OFFERING = auto()    # Offering badge
    COVENANT = auto()    # Permission indicator
    WALK = auto()        # Walk timeline
    RITUAL = auto()      # Ritual state
```

**Exit Criteria**: 10+ tests pass, ServoScene composes correctly.

---

### Chunk 3: TerrariumView Multi-Webview (3-4 hours)

**Goal**: Implement TerrariumView as compositional lens over TraceNodes.

**Files**:
```
impl/claude/protocols/agentese/projection/terrarium_view.py
impl/claude/protocols/agentese/projection/_tests/test_terrarium_view.py
impl/claude/protocols/agentese/contexts/world_terrarium.py
```

**Tasks**:
- [ ] Implement `TerrariumView` dataclass
- [ ] Implement `SelectionQuery` (what to show)
- [ ] Implement `LensConfig` (how to transform)
- [ ] Wire to TraceNode stream
- [ ] Add AGENTESE node: `world.terrarium.view.*`
- [ ] Aspects: `manifest`, `create`, `update`, `project`

**Laws to Verify**:
```python
def test_terrarium_fault_isolation():
    """Law 3: Crashed view doesn't affect others."""
    view_a = TerrariumView(fault_isolated=True)
    view_b = TerrariumView(fault_isolated=True)
    # Crash view_a
    view_a.crash()
    # view_b still works
    assert view_b.project(trace_stream) is not None
```

**Exit Criteria**: 10+ tests pass, multiple views render independently.

---

### Chunk 4: TraceNode Playback UI (3-4 hours)

**Goal**: Implement Walk playback as cinematic UI.

**Files**:
```
impl/claude/web/src/components/servo/TracePlayback.tsx
impl/claude/web/src/components/servo/WalkTimeline.tsx
impl/claude/web/src/hooks/useTracePlayback.ts
```

**Tasks**:
- [ ] Implement `TracePlayback` component
- [ ] Implement `WalkTimeline` scrubber
- [ ] Implement playback controls (play, pause, seek, speed)
- [ ] Implement TraceNode detail expansion
- [ ] Wire to `time.walk.*` AGENTESE node
- [ ] Add teaching overlays (Pattern 14)

**UI Specification**:
```
┌─────────────────────────────────────────┐
│  Walk: "Implement WARP primitives"       │
│  ▶ ││ ◀◀ ▶▶  [━━━━━●━━━━━━] 3:42 / 8:15  │
├─────────────────────────────────────────┤
│  TraceNode #47                           │
│  ┌─────────────────────────────────────┐ │
│  │ Stimulus: "Create TraceNode spec"   │ │
│  │ Response: { ... }                   │ │
│  │ Links: [plan/warp.md] → [this]      │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Exit Criteria**: Walk playback works, TraceNodes visualize causality.

---

### Chunk 5: Intent-Based Navigation (2-3 hours)

**Goal**: Replace URL routing with Intent navigation.

**Files**:
```
impl/claude/web/src/hooks/useIntentRouter.ts
impl/claude/web/src/components/servo/IntentNav.tsx
```

**Tasks**:
- [ ] Implement `IntentRouter` hook
- [ ] Map Intent → TerrariumView
- [ ] Remove URL-based routing for operational surfaces
- [ ] Preserve URL for docs/marketing (allowed residuals)
- [ ] Wire to `concept.intent.*` AGENTESE node

**Intent Routing**:
```typescript
function useIntentRouter() {
  const navigate = (intent: Intent) => {
    // Intent determines view, not URL
    const view = findViewForIntent(intent);
    setActiveView(view);
    // URL is derived, not primary
    window.history.replaceState({}, '', intentToPath(intent));
  };
}
```

**Exit Criteria**: Navigation works via Intent, not URL.

---

### Chunk 6: Servo Aesthetic Primitives (3-4 hours)

**Goal**: Implement joy-inducing Servo primitives from mood board.

**Files**:
```
impl/claude/web/src/components/servo/BreathingSurface.tsx
impl/claude/web/src/components/servo/UnfurlingPanel.tsx
impl/claude/web/src/components/servo/FlowTrace.tsx
impl/claude/web/src/components/servo/TextureLayer.tsx
```

**Tasks**:
- [ ] Implement `BreathingSurface` (3-4s period, 2-3% amplitude)
- [ ] Implement `UnfurlingPanel` (organic easing, not mechanical)
- [ ] Implement `FlowTrace` (data moves like water)
- [ ] Implement `TextureLayer` (paper grain, not flat glass)
- [ ] Apply Living Earth palette
- [ ] Apply Nunito/Inter/JetBrains Mono typography

**Animation Specification**:
```typescript
const BREATHING_SURFACE = {
  period: 3500,        // 3.5 seconds
  amplitude: 0.025,    // 2.5% scale change
  easing: 'ease-in-out',
};

const UNFURLING_PANEL = {
  duration: 400,       // 400ms
  easing: 'cubic-bezier(0.4, 0, 0.2, 1)',  // Organic unfurl
};
```

**Exit Criteria**: Components feel alive, not mechanical.

---

### Chunk 7: ServoShell Host (4-5 hours)

**Goal**: Implement minimal Servo shell host process.

**Files**:
```
impl/claude/web/servo-shell/
├── shell.rs           # Rust host (if Servo viable)
├── shell.ts           # TypeScript fallback
├── projection_registry.ts
├── covenant_overlay.ts
└── intent_router.ts
```

**Tasks**:
- [ ] Implement windowing + projection registry
- [ ] Implement routing (Intent → View)
- [ ] Implement Covenant overlay (permission gates visible)
- [ ] Compose TerrariumViews
- [ ] Wire to AGENTESE gateway

**Decision Point**: If Servo not viable, implement in TypeScript with Servo-like abstractions.

**Exit Criteria**: Shell composes views, covenant gates visible.

---

## N-Phase Position

This plan covers phases:
- **PLAN**: ✅ Complete (this document)
- **DEVELOP**: ServoScene primitives, TerrariumView
- **STRATEGIZE**: Wire to CLI v7, existing webapp
- **IMPLEMENT**: Components, shell
- **TEST**: Law verification, visual regression

---

## Total Estimates

| Chunk | Hours | Tests |
|-------|-------|-------|
| Projection Target | 2-3 | 5+ |
| Scene Primitives | 3-4 | 10+ |
| TerrariumView | 3-4 | 10+ |
| Playback UI | 3-4 | 5+ |
| Intent Navigation | 2-3 | 5+ |
| Aesthetic Primitives | 3-4 | 5+ |
| ServoShell | 4-5 | 10+ |
| **Total** | **21-27** | **50+** |

---

## Webapp Transition Strategy

### Deprecation Path

1. **Phase 2A**: Servo runs alongside React webapp
2. **Phase 2B**: Operational UI migrates to Servo
3. **Phase 2C**: React webapp becomes docs/marketing only
4. **Phase 2D**: Full Servo-first (webapp is composition shell)

### Allowed Residuals

Keep webapp for:
- Docs, specs, onboarding
- Static marketing, dashboards
- Deep-linking into Servo sessions

---

## Anti-Sausage Check

Before marking complete, verify:
- ❓ Is Servo daring (substrate, not just webview)?
- ❓ Do animations feel alive (breathing, unfurling)?
- ❓ Is texture present (paper grain, not flat)?
- ❓ Is navigation intent-based (not URL-first)?

---

## Cross-References

- **Spec**: `spec/protocols/servo-substrate.md`
- **Plan**: `plans/warp-servo-phase1-core-primitives.md`
- **Skills**: `docs/skills/projection-target.md`
- **Skills**: `docs/skills/elastic-ui-patterns.md`

---

*"The webapp is not the UI. The webapp is the composition boundary."*
