---
path: plans/visionary-ux-wave2-strategy-decision
status: active
progress: 100
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - plans/visionary-ux-wave3
  - agents/town/visualization-composition
  - agents/i/reactive/presets
session_notes: |
  STRATEGIZE complete. Widget coverage analyzed, integration priorities ranked,
  layout presets defined. Ready for CROSS-SYNERGIZE.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: deferred
  MEASURE: deferred
  REFLECT: pending
entropy:
  planned: 0.03
  spent: 0.03
  returned: 0.0
---

# Visionary UX Wave 2: STRATEGIZE Decision Document

**Phase**: STRATEGIZE (N-Phase 4 of 11) - COMPLETE
**Date**: 2025-12-15
**Decision Authority**: Auto-continuation (non-blocking strategic scope)

---

## Executive Summary

Wave 2 DEVELOP delivered `ComposableMixin` with `>>` (HStack) and `//` (VStack) operators. This STRATEGIZE phase analyzed:
1. Which widgets should gain `ComposableMixin`
2. Layout preset patterns to codify
3. Integration priorities with Agent Town and Turn projectors

**Key Decision**: Prioritize primitive composition; defer complex widgets.

---

## 1. Widget Coverage Analysis

### Current State

| Widget | Has ComposableMixin | Complexity | Priority |
|--------|---------------------|------------|----------|
| `GlyphWidget` | YES | Low | - (done) |
| `SparklineWidget` | YES | Low | - (done) |
| `BarWidget` | NO | Low | HIGH |
| `DensityFieldWidget` | NO | High (2D grid) | LOW |
| `AgentCardWidget` | NO | Medium (composite) | MEDIUM |
| `YieldCardWidget` | NO | Medium (composite) | MEDIUM |
| `ShadowCardWidget` | NO | Medium (composite) | LOW |
| `DialecticCardWidget` | NO | Medium (composite) | LOW |
| `EigenvectorScatterWidgetImpl` | NO | High (external) | DEFERRED |

### Strategic Decision: Tiered Rollout

**Tier 1 (Wave 2.1)**: Add to remaining primitives
- `BarWidget` - horizontal fill, composes naturally with glyphs/sparklines
- Rationale: Completes the "atomic layer" - all primitives become composable

**Tier 2 (Wave 2.2)**: Add to high-value composite widgets
- `AgentCardWidget` - agent identity cards as composable units
- `YieldCardWidget` - agent output as composable feed items
- Rationale: Enables Agent Town visualization composition

**Tier 3 (Wave 3+)**: Complex/specialized widgets
- `DensityFieldWidget` - needs special handling (2D rendering conflicts with 1D composition)
- `ShadowCardWidget` / `DialecticCardWidget` - H-gent specialized, lower usage
- `EigenvectorScatterWidgetImpl` - external to reactive substrate, different protocol

### Deferred: DensityFieldWidget

The `DensityFieldWidget` is inherently 2D. Adding `>>` / `//` would:
- Create semantic confusion (how do you "horizontally compose" a 40x20 grid?)
- Require viewport windowing (see `meta.md`: "Viewport windowing: render subset of grid")

**Decision**: DensityFieldWidget remains non-composable. Composition happens AT the card level, not within the field.

---

## 2. Layout Presets

### Identified Patterns

From codebase analysis and `meta.md` learning:

```python
# Pattern 1: Metric Row (horizontal alignment)
def metric_row(*widgets: ComposableWidget) -> HStack:
    """Compose widgets horizontally with standard gap."""
    return reduce(lambda a, b: a >> b, widgets)

# Pattern 2: Metric Stack (vertical alignment)
def metric_stack(*widgets: ComposableWidget) -> VStack:
    """Stack widgets vertically with separator lines."""
    return reduce(lambda a, b: a // b, widgets)

# Pattern 3: Dashboard Panel (header + body)
def panel(header: ComposableWidget, body: ComposableWidget) -> VStack:
    """Header row above body content."""
    return header // body

# Pattern 4: Labeled Metric (glyph + value)
def labeled(label: str, widget: ComposableWidget) -> HStack:
    """Prefix widget with label glyph."""
    label_glyph = GlyphWidget(GlyphState(char=label[0]))
    return label_glyph >> widget

# Pattern 5: Status Row (glyph + sparkline + bar)
def status_row(
    phase: Phase,
    activity: tuple[float, ...],
    health: float
) -> HStack:
    """Standard agent status display."""
    glyph = GlyphWidget(GlyphState(phase=phase))
    spark = SparklineWidget(SparklineState(values=activity, max_length=10))
    bar = BarWidget(BarState(value=health, width=5))
    return glyph >> spark >> bar
```

### Module Location

Create: `impl/claude/agents/i/reactive/presets.py`

This follows existing pattern of putting reusable patterns in dedicated modules.

---

## 3. Integration Priorities

### Priority Ranking

| Integration | Priority | Effort | Impact | Notes |
|-------------|----------|--------|--------|-------|
| Agent Town scatter → cards | HIGH | Medium | High | Citizens as composable AgentCards |
| Turn projectors → composition | HIGH | Low | High | Turn → HStack/VStack is natural |
| Dashboard screens | MEDIUM | Medium | Medium | Replace manual layout |
| marimo notebooks | MEDIUM | Low | Medium | Composed widgets in cells |
| Textual TUI | LOW | High | Medium | Different rendering model |

### High Priority: Agent Town Integration

The `EigenvectorScatterWidgetImpl` already projects to multiple targets. The integration path:

```
Environment → scatter.points → map to AgentCards → compose via >>
```

From `meta.md`:
> "Bridge pattern: environment → scatter → isometric is clean functor chain"

The composition layer sits between `scatter.points` and `isometric` rendering.

### High Priority: Turn Projectors

From `meta.md`:
> "Turn projectors are natural transformations: Turn → CLI/TUI/JSON/marimo/SSE preserve structure"

Adding composition to Turn projectors:
```python
# Existing: Turn → single widget
# New: Turn → composed layout

def turn_to_dashboard(turn: Turn) -> VStack:
    header = phase_glyph(turn.phase) >> GlyphWidget(GlyphState(char=turn.agent_id))
    body = SparklineWidget(SparklineState(values=turn.activity_history))
    return header // body
```

---

## 4. Advanced Composition (Future Waves)

### Wave 3 Candidates

| Container | Type | Use Case |
|-----------|------|----------|
| `Grid` | 2D | n-column layouts |
| `Tabs` | Temporal | Show one of N views |
| `Overlay` | Z-axis | Tooltips, modals |
| `Conditional` | State | if/else rendering |

### Grid Design Sketch

```python
@dataclass
class Grid(KgentsWidget[None]):
    """2D grid composition with configurable columns."""
    children: list[ComposableWidget]
    columns: int = 3

    def project(self, target: RenderTarget) -> Any:
        # Chunk into rows, render each as HStack
        rows = [self.children[i:i+self.columns]
                for i in range(0, len(self.children), self.columns)]
        vstacked = reduce(lambda a, b: a // b,
                         [reduce(lambda x, y: x >> y, row) for row in rows])
        return vstacked.project(target)
```

---

## 5. Success Criteria Checklist

- [x] Strategic decision on widget coverage documented
- [x] Integration priorities ranked
- [x] Layout presets identified
- [x] Next wave scope defined

---

## 6. Next Wave Scope

### Wave 2.1: Complete Primitive Layer
1. Add `ComposableMixin` to `BarWidget`
2. Create `agents/i/reactive/presets.py` with 5 patterns
3. Tests: ~20 additional tests

### Wave 2.2: Composite Layer
1. Add `ComposableMixin` to `AgentCardWidget`
2. Add `ComposableMixin` to `YieldCardWidget`
3. Wire Agent Town scatter → composed cards
4. Tests: ~30 additional tests

### Wave 3: Advanced Containers (deferred scope)
1. `Grid` container
2. `Conditional` container
3. Turn projector composition integration

---

## 7. Auto-Continuation

**STRATEGIZE**: COMPLETE

Ledger updated: `{PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched}`

Next phase: CROSS-SYNERGIZE (verify BarWidget can adopt ComposableMixin without breaking existing tests)

---

## Appendix: Code References

- `composable.py`: `impl/claude/agents/i/reactive/composable.py` (377 lines)
- `glyph.py`: `impl/claude/agents/i/reactive/primitives/glyph.py:56` (ComposableMixin)
- `sparkline.py`: `impl/claude/agents/i/reactive/primitives/sparkline.py:49` (ComposableMixin)
- `bar.py`: `impl/claude/agents/i/reactive/primitives/bar.py:62` (candidate)
- `agent_card.py`: `impl/claude/agents/i/reactive/primitives/agent_card.py:52` (Wave 2.2)
- `test_composable.py`: `impl/claude/agents/i/reactive/_tests/test_composable.py` (37 tests)
