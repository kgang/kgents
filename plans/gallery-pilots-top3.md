---
path: gallery-pilots-top3
status: complete
progress: 100
last_touched: 2025-12-18
touched_by: claude-opus-4
blocking: []
enables:
  - plans/core-apps-synthesis
  - plans/design-language-consolidation
session_notes: |
  Created 3 flagship gallery pilots that teach categorical fundamentals.
  All pilots implemented with backend widgets, React components, and tests.
  Focus: polynomial_playground, operad_wiring_diagram, town_live.
  Backend: 32 tests passing. Frontend: 37 tests passing.
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: complete
  CROSS-SYNERGIZE: complete
  IMPLEMENT: complete
  QA: complete
  TEST: complete
  EDUCATE: pending
  MEASURE: deferred
  REFLECT: pending
entropy:
  planned: 0.15
  spent: 0.12
  returned: 0.03
---

# Gallery Pilots: Top 3 Flagship Implementations

> *"Make the abstract tangible. Let developers feel the categorical ground."*

**Goal**: Implement 3 flagship gallery pilots that make developers say "I want to build with this."

**Pilots**:
1. `polynomial_playground` - Interactive state machine builder
2. `operad_wiring_diagram` - Visual composition grammar
3. `town_live` - Live Agent Town simulation

---

## Core Insight

These pilots demonstrate the **Unified Categorical Foundation**:
- PolyAgent (state machines with mode-dependent inputs)
- Operad (composition grammar with laws)
- Sheaf (global coherence from local views)

Each pilot targets a different layer while using consistent UX patterns.

---

## Phase 1: Backend Pilot Infrastructure (2-3 hours)

**Goal**: Extend `pilots.py` with interactive pilot widgets.

### 1.1 Create PolynomialPlayground Widget

**File**: `impl/claude/protocols/projection/gallery/pilots.py`

```python
# New category for interactive pilots
class PilotCategory(Enum):
    # ... existing ...
    INTERACTIVE = auto()  # Pilots with rich interactivity

@dataclass
class InteractivePilot(Pilot):
    """Pilot with stateful interaction support."""
    initial_state: dict[str, Any] = field(default_factory=dict)
    state_schema: dict[str, Any] = field(default_factory=dict)  # For validation
```

**Key Features**:
- Define preset polynomials: `traffic_light`, `vending_machine`, `citizen`
- State definition interface
- Transition function visualization
- Input injection buttons
- Live trace panel

### 1.2 Create OperadWiringWidget

**Features**:
- Visual operation boxes with arities
- Connectable ports
- Law verification (identity, associativity)
- Real-time composition output

### 1.3 Create TownLiveWidget

**Features**:
- SSE-powered citizen updates
- Mini-mesa visualization
- Event feed
- Phase indicator

---

## Phase 2: React Components (3-4 hours)

**Goal**: Build interactive React components for each pilot.

### 2.1 PolynomialPlayground Component

**File**: `impl/claude/web/src/components/projection/gallery/PolynomialPlayground.tsx`

**UX Patterns Applied**:
- [x] Elastic breakpoints (compact/comfortable/spacious)
- [x] Visual flow builder (node-based canvas)
- [x] Live preview (see output as you build)
- [x] Dry run mode (test without execution)

**Structure**:
```
┌──────────────────────────────────────────────────────────────┐
│ [Traffic Light ▼] [Vending Machine] [Citizen] [Custom]      │ <- Preset selector
├────────────────────────────────┬─────────────────────────────┤
│                                │   ┌─────────┐               │
│    ●─────▶ ○ ─────▶ ●         │   │ States  │               │
│    │       │        │          │   ├─────────┤               │
│  RED    YELLOW   GREEN         │   │ ○ RED   │               │
│    ▲                │          │   │ ◉ YLW   │ <- Current    │
│    └────────────────┘          │   │ ○ GRN   │               │
│                                │   └─────────┘               │
│   State Machine Diagram        │   Valid Inputs:             │
│                                │   [tick] [reset]            │
├────────────────────────────────┴─────────────────────────────┤
│ Trace: RED → tick → YELLOW → tick → GREEN → tick → RED      │
└──────────────────────────────────────────────────────────────┘
```

**Mobile Layout** (BottomDrawer pattern):
- Mesa in main view
- States/inputs in bottom drawer
- Trace collapsed by default

### 2.2 OperadWiringDiagram Component

**File**: `impl/claude/web/src/components/projection/gallery/OperadWiring.tsx`

**UX Patterns Applied**:
- [x] Node-based canvas (drag components, draw connections)
- [x] Live preview (see composition result)
- [x] Governance dashboards (law verification indicators)

**Structure**:
```
┌──────────────────────────────────────────────────────────────┐
│ [TOWN_OPERAD ▼]    Laws: ✓ Identity  ✓ Assoc  ○ Unitality   │
├────────────────────────────────┬─────────────────────────────┤
│                                │   Operations                │
│   ┌──────┐   ┌──────┐         │   ├─────────────────────────┤
│   │greet │──▶│gossip│─┐       │   │ greet  (2) Citizen×Cit  │
│   │ (2)  │   │ (2)  │ │       │   │ gossip (2) Cit×Info     │
│   └──────┘   └──────┘ │       │   │ trade  (2) Exchange      │
│                       ▼       │   │ solo   (1) Reflection    │
│              ┌────────────┐   │   └─────────────────────────┤
│              │ composed   │   │   γ(greet; gossip, id)       │
│              │ operation  │   │   = greet >> gossip          │
│              └────────────┘   │                              │
│                               │   [Verify Laws]              │
├───────────────────────────────┴─────────────────────────────┤
│ Output: greet×gossip : Citizen×Citizen×Citizen → Info       │
└──────────────────────────────────────────────────────────────┘
```

**Interaction**:
- Drag operation boxes from palette
- Connect ports by drawing lines
- Real-time type checking
- Red highlight on law violations

### 2.3 TownLive Component

**File**: `impl/claude/web/src/components/projection/gallery/TownLive.tsx`

**UX Patterns Applied**:
- [x] Live sync (real-time updates via SSE)
- [x] Semantic zoom (overview → detail)
- [x] Cursor awareness (show selected citizen)
- [x] Time pressure (visible countdown/tick)

**Structure**:
```
┌──────────────────────────────────────────────────────────────┐
│ Town: demo   Day 3   AFTERNOON   ▶ Playing   [1x ▼]         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│        K           M    •    H                               │
│    Socrates     Marcus  •  Hypatia                          │
│    (active)    (idle)   •  (working)                        │
│         \       /       •      |                            │
│          \     /        •      |                            │
│           \   /         •      |                            │
│            \ /          •      |                            │
│             A           •      L                            │
│           Ada           •   Leonardo                        │
│        (reflecting)     •   (resting)                       │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ Events: [10:42] Socrates greeted Marcus                     │
│         [10:41] Hypatia started working on task             │
│         [10:40] Leonardo began rest (Right to Rest)         │
└──────────────────────────────────────────────────────────────┘
```

**Streaming**:
- Reuse `useTownStreamWidget` hook
- Mini-mesa with simplified rendering
- Compact citizen cards
- Auto-scrolling event feed

---

## Phase 3: Integration & Gallery Registration (1-2 hours)

### 3.1 Register Pilots in Registry

**File**: `impl/claude/protocols/projection/gallery/pilots.py`

```python
register_pilot(
    Pilot(
        name="polynomial_playground",
        category=PilotCategory.INTERACTIVE,
        description="Build and run state machines interactively",
        widget_factory=_create_polynomial_playground,
        tags=["polynomial", "interactive", "state-machine", "flagship"],
    )
)

register_pilot(
    Pilot(
        name="operad_wiring_diagram",
        category=PilotCategory.INTERACTIVE,
        description="Wire operations together, verify composition laws",
        widget_factory=_create_operad_wiring,
        tags=["operad", "interactive", "composition", "flagship"],
    )
)

register_pilot(
    Pilot(
        name="town_live",
        category=PilotCategory.INTERACTIVE,
        description="Watch Agent Town citizens in real-time",
        widget_factory=_create_town_live,
        tags=["streaming", "town", "citizens", "flagship"],
    )
)
```

### 3.2 Add Interactive Route Handling

**File**: `impl/claude/web/src/pages/GalleryPage.tsx`

- Add special handling for INTERACTIVE category
- Full-page mode for flagship pilots
- Route: `/gallery/polynomial_playground`, etc.

### 3.3 Update Navigation Tree

**File**: `impl/claude/web/src/shell/NavigationTree.tsx`

Add routes:
```typescript
{ path: "world.gallery.polynomial_playground", route: "/gallery/polynomial_playground" },
{ path: "world.gallery.operad_wiring", route: "/gallery/operad_wiring" },
{ path: "world.gallery.town_live", route: "/gallery/town_live" },
```

---

## Phase 4: Testing & Refinement (1-2 hours)

### 4.1 Backend Tests

**File**: `impl/claude/protocols/projection/gallery/_tests/test_interactive_pilots.py`

```python
def test_polynomial_playground_renders_all_targets():
    """Interactive pilot renders CLI, HTML, JSON."""
    pilot = PILOT_REGISTRY["polynomial_playground"]
    widget = pilot.create_widget({"preset": "traffic_light"})

    assert "RED" in widget.project(RenderTarget.CLI)
    assert "state-machine" in widget.project(RenderTarget.JSON)["type"]

def test_operad_wiring_validates_laws():
    """Operad pilot validates composition laws."""
    pilot = PILOT_REGISTRY["operad_wiring_diagram"]
    widget = pilot.create_widget({"operad": "TOWN_OPERAD"})

    json_output = widget.project(RenderTarget.JSON)
    assert json_output["laws"]["identity"]["verified"] is True

def test_town_live_provides_sse_endpoint():
    """Town live pilot provides streaming endpoint."""
    pilot = PILOT_REGISTRY["town_live"]
    widget = pilot.create_widget({})

    json_output = widget.project(RenderTarget.JSON)
    assert "sse_endpoint" in json_output
```

### 4.2 Frontend Tests

**File**: `impl/claude/web/src/components/projection/gallery/__tests__/InteractivePilots.test.tsx`

```typescript
describe("PolynomialPlayground", () => {
  it("renders preset selector", () => {
    render(<PolynomialPlayground />);
    expect(screen.getByRole("combobox")).toBeInTheDocument();
  });

  it("shows state diagram for traffic_light preset", async () => {
    render(<PolynomialPlayground preset="traffic_light" />);
    await waitFor(() => {
      expect(screen.getByText("RED")).toBeInTheDocument();
    });
  });

  it("executes transition on input button click", async () => {
    render(<PolynomialPlayground preset="traffic_light" />);
    const tickButton = screen.getByRole("button", { name: /tick/i });
    fireEvent.click(tickButton);
    await waitFor(() => {
      expect(screen.getByText(/YELLOW/)).toBeInTheDocument();
    });
  });
});
```

### 4.3 Mobile Testing

Test at breakpoints: 375px, 768px, 1024px, 1440px

Checklist:
- [ ] PolynomialPlayground: Bottom drawer for states/inputs on mobile
- [ ] OperadWiring: Horizontal scroll for canvas on mobile
- [ ] TownLive: Compact event feed, floating actions

---

## Phase 5: Documentation (30 min)

### 5.1 Update skills/projection-gallery.md

Add section on interactive pilots.

### 5.2 Update Gallery README

Document the flagship pilots and their teaching goals.

---

## Exit Criteria

- [ ] 3 pilots registered in PILOT_REGISTRY
- [ ] React components render at all densities
- [ ] Backend tests pass (>10 tests)
- [ ] Frontend tests pass (>6 tests)
- [ ] Mobile layouts work (tested at 375px)
- [ ] Streaming works for town_live
- [ ] Laws verification works for operad_wiring

---

## Dependencies

**Backend**:
- `impl/claude/agents/poly/protocol.py` - PolyAgent
- `impl/claude/agents/operad/core.py` - Operad registry
- `impl/claude/agents/town/` - Town simulation

**Frontend**:
- `impl/claude/web/src/components/elastic/` - Layout primitives
- `impl/claude/web/src/hooks/useTownStreamWidget.ts` - SSE hook
- `impl/claude/web/src/components/town/` - Mesa components

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Canvas rendering performance | Use React-konva or simple SVG |
| SSE connection handling | Reuse existing town streaming |
| Mobile touch interactions | Use larger touch targets (48px min) |
| Operad complexity | Start with TOWN_OPERAD only |

---

## Cross-References

- **Skills**: `polynomial-agent.md`, `elastic-ui-patterns.md`, `ux-reference-patterns.md`
- **Spec**: `spec/protocols/projection.md`
- **Plan**: `plans/design-language-consolidation.md`
