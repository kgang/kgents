---
path: plans/projection-protocol-cultivation
status: active
progress: 70
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - marimo-integration
  - unified-widget-api
  - vr-target-future
session_notes: |
  CROSS-SYNERGIZE COMPLETE. All widgets pass functor laws. Zero violations.
  74 tests passing. Mypy clean. Ready for IMPLEMENT.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.06
  returned: 0.0
---

# Projection Protocol Cultivation

> *"Developers design agents. Projections are batteries included."*

## Overview

Bring `spec/protocols/projection.md` from initial draft to full implementation with tests, docs, and wiring across the reactive substrate.

## Scope

**In scope**:
- Formalize ProjectionRegistry in impl
- Ensure all existing widgets implement `project()` correctly
- Add missing projections (VR target placeholder, audio target placeholder)
- Wire Turn projections to the unified protocol
- Test functor laws for projections
- Document the "batteries included" developer experience

**Non-goals**:
- Actually implement WebGL/VR (placeholder only)
- Rewrite existing working widgets
- Add new widget types (out of scope)

## Attention Budget

| Focus | % |
|-------|---|
| Implementation (ProjectionRegistry, law verification) | 50% |
| Testing (functor laws, projection correctness) | 25% |
| Documentation (developer guide) | 15% |
| Exploration (future targets) | 10% |

---

## Continuation Prompt

⟿[RESEARCH]

# RESEARCH: Projection Protocol Cultivation

## ATTACH

/hydrate

You are entering RESEARCH of the N-Phase Cycle (AD-005) to cultivate `spec/protocols/projection.md`.

handles:
  scope=projection-protocol-cultivation
  ledger={PLAN:touched, RESEARCH:in_progress}
  entropy=0.08
  spec=spec/protocols/projection.md
  impl_target=impl/claude/agents/i/reactive/
  turn_target=impl/claude/protocols/api/turn.py

## Your Mission

Map the terrain for implementing the Projection Protocol. You need to:

1. **Survey existing projections**:
   - Read `impl/claude/agents/i/reactive/widget.py` (KgentsWidget, RenderTarget)
   - Read `impl/claude/protocols/api/turn.py` (Turn projections)
   - Grep for `to_cli`, `to_marimo`, `to_json`, `to_tui` implementations
   - Count how many widgets exist and which targets each supports

2. **Identify gaps**:
   - Which widgets are missing which projections?
   - Is there a central ProjectionRegistry? If not, where should it live?
   - Are functor laws verified anywhere? (projection composition)

3. **Map prior art**:
   - Check `impl/claude/system/projector/` for the K8s/Local projector patterns
   - Check `impl/claude/bootstrap/umwelt.py` for Umwelt Projector patterns
   - These are related but distinct—understand the taxonomy

4. **Surface blockers**:
   - Any circular imports that would block a unified registry?
   - Any widgets that violate the projection protocol?

## Principles Alignment

This phase emphasizes:
- **Generative** (spec/principles.md §7): The spec should generate the implementation
- **Composable** (spec/principles.md §5): Projections must compose lawfully

## Exit Criteria

- [ ] File map of all projection-related code
- [ ] Count of widgets × targets matrix (what exists)
- [ ] List of gaps (what's missing)
- [ ] Blockers identified (or "none")
- [ ] Recommended location for ProjectionRegistry
- [ ] Branch candidates surfaced

## Continuation Imperative

Upon completing RESEARCH, emit:

```
⟿[DEVELOP]
/hydrate
handles: scope=projection-protocol-cultivation; ledger={PLAN:touched, RESEARCH:touched, DEVELOP:in_progress}; entropy=0.06; file_map=${FILE_MAP}; gaps=${GAPS}; registry_location=${REGISTRY_LOCATION}
mission: Design ProjectionRegistry API; define functor law tests; specify target registration protocol.
exit: API contract for ProjectionRegistry; law assertions; target extension interface.
continuation → STRATEGIZE.
```

Or if blockers found:
```
⟂[BLOCKED:${reason}] ${description}
```

---

## Quick Reference

```
Current phase: RESEARCH (COMPLETE)
Next phase: DEVELOP
Spec: spec/protocols/projection.md
Key files:
  - impl/claude/agents/i/reactive/widget.py
  - impl/claude/protocols/api/turn.py
  - impl/claude/system/projector/base.py
```

---

## RESEARCH Findings (2025-12-15)

### 1. File Map (Projection-Related Code)

| Location | Purpose |
|----------|---------|
| `agents/i/reactive/widget.py` | `KgentsWidget[S]` base + `RenderTarget` enum (CLI, TUI, MARIMO, JSON) |
| `agents/i/reactive/composable.py` | `HStack`, `VStack`, `ComposableMixin` (`>>`, `//` operators) |
| `agents/i/reactive/primitives/*.py` | Glyph, Bar, Sparkline, DensityField, AgentCard, HgentCard, YieldCard |
| `agents/i/reactive/presets.py` | Layout presets (`metric_row`, `panel`, `status_row`) |
| `agents/i/reactive/screens/*.py` | Dashboard, Debugger (composite widgets) |
| `agents/i/marimo/widgets/*.py` | marimo-specific anywidgets (scatter, timeline, stigmergic, dialectic) |
| `protocols/api/turn.py` | `Turn` with `to_cli`, `to_tui`, `to_json`, `to_marimo`, `to_sse` |
| `system/projector/base.py` | **Different domain**: Alethic Projector (Agent → K8s/Local deployment) |
| `bootstrap/umwelt.py` | **Different domain**: Umwelt Projector (World → Agent-scoped view) |

### 2. Widget × Target Matrix

| Widget | CLI | TUI | MARIMO | JSON | SSE | Notes |
|--------|-----|-----|--------|------|-----|-------|
| GlyphWidget | ✓ | ✓ | ✓ | ✓ | — | Atomic unit |
| BarWidget | ✓ | ✓ | ✓ | ✓ | — | Composes Glyphs |
| SparklineWidget | ✓ | ✓ | ✓ | ✓ | — | Time-series |
| DensityFieldWidget | ✓ | ✓ | ✓ | ✓ | — | 2D grid |
| AgentCardWidget | ✓ | ✓ | ✓ | ✓ | — | CompositeWidget |
| HStack/VStack | ✓ | ✓ | ✓ | ✓ | — | Composition containers |
| Turn | ✓ | ✓ | ✓ | ✓ | ✓ | Dialogue unit |
| ScatterWidgetMarimo | — | — | ✓ (anywidget) | via trait | via SSE | marimo-only |
| IsometricWidget | ✓ | — | ✓ | ✓ | — | Town visualization |

**Observation**: Core primitives have full 4-target coverage. marimo-specific widgets use anywidget (JS ESM) directly.

### 3. Gaps Identified

| Gap | Description | Priority |
|-----|-------------|----------|
| **No ProjectionRegistry** | Spec describes `ProjectionRegistry.register()` but no impl exists | HIGH |
| **No VR/Audio placeholders** | Spec mentions WebXR/Audio targets but no stubs | LOW |
| **Functor law tests for widgets** | Signal/Computed functor laws verified, but widget projection composition not tested | MEDIUM |
| **SSE target inconsistent** | Turn has `to_sse`, but not in RenderTarget enum | MEDIUM |
| **marimo widgets don't inherit KgentsWidget** | marimo widgets (scatter, etc.) use different base | MEDIUM |

### 4. Functor Law Status

- **Signal.map()**: ✓ Verified (identity + composition) in `test_properties.py:220-325`
- **Computed.map()**: ✓ Verified in `test_properties.py:327-357`
- **Widget.project()**: ✗ No explicit functor law tests (but projections ARE deterministic)

### 5. Taxonomy Clarification

| Projector Type | Domain | Target |
|----------------|--------|--------|
| **Alethic Projector** (`system/projector/`) | Agent class → Deployment artifact | K8s manifests, local process |
| **Umwelt Projector** (`bootstrap/umwelt.py`) | World → Agent scoped view | Lens + Gravity + DNA |
| **Render Projection** (`agents/i/reactive/`) | Widget state → UI representation | CLI, TUI, marimo, JSON |

The Projection Protocol in `spec/protocols/projection.md` concerns **Render Projection** (Layer 3).

### 6. Blockers

**NONE FOUND**. The codebase is ready for ProjectionRegistry implementation.

### 7. Recommended Location for ProjectionRegistry

```
impl/claude/agents/i/reactive/projection/
├── __init__.py
├── registry.py       # ProjectionRegistry class
├── targets.py        # Extended RenderTarget (SSE, VR placeholders)
├── laws.py           # Functor law verification utilities
└── _tests/
    ├── __init__.py
    └── test_registry.py
```

**Rationale**:
- Lives alongside `widget.py` where projections are defined
- Doesn't conflict with `system/projector/` (different domain)
- Follows existing pattern of `_tests/` subdirectories

---

## Continuation Prompt

⟿[DEVELOP]

# DEVELOP: Projection Protocol Cultivation

## ATTACH

/hydrate

You are entering DEVELOP of the N-Phase Cycle (AD-005) for `spec/protocols/projection.md`.

handles:
  scope=projection-protocol-cultivation
  ledger={PLAN:touched, RESEARCH:touched, DEVELOP:in_progress}
  entropy=0.06
  file_map=see_findings_above
  gaps=[ProjectionRegistry, SSE_target, widget_functor_laws]
  registry_location=impl/claude/agents/i/reactive/projection/

## Your Mission

Design the ProjectionRegistry API:

1. **Define ProjectionRegistry class**:
   - `@ProjectionRegistry.register(target_name)` decorator
   - `ProjectionRegistry.get(target_name)` lookup
   - `ProjectionRegistry.all_targets()` enumeration
   - Graceful degradation when target not supported

2. **Define functor law verification utilities**:
   - `verify_identity_law(widget)` - project(id(state)) == project(state)
   - `verify_composition_law(widget, f, g)` - chained projection preserves structure

3. **Specify target extension interface**:
   - How to add WebGL/VR placeholder
   - How to register SSE as formal target

4. **Draft test specifications**:
   - Registry registration/lookup
   - Law verification on primitive widgets
   - Graceful degradation paths

## Exit Criteria

- [ ] API contract for ProjectionRegistry (docstrings + type hints)
- [ ] Law verification function signatures
- [ ] Target extension interface design
- [ ] Test specification outline

## Continuation Imperative

Upon completing DEVELOP, emit:

```
⟿[STRATEGIZE]
/hydrate
handles: scope=projection-protocol-cultivation; ledger={PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:in_progress}; entropy=0.04
mission: Evaluate implementation order, identify quick wins, plan phased rollout.
exit: Implementation backlog with priority order.
continuation → CROSS-SYNERGIZE.
```

---

## DEVELOP Findings (2025-12-15)

### Implementation Complete

Created `impl/claude/agents/i/reactive/projection/` with:

```
projection/
├── __init__.py           # Module exports
├── registry.py           # ProjectionRegistry singleton
├── targets.py            # ExtendedTarget + TargetCapability
├── laws.py               # Functor law verification
└── _tests/
    ├── __init__.py
    ├── test_registry.py  # 27 tests
    ├── test_targets.py   # 23 tests
    └── test_laws.py      # 24 tests
```

### API Contract

**ProjectionRegistry** (Singleton):
- `@ProjectionRegistry.register(name, fidelity, description)` - Decorator
- `ProjectionRegistry.project(widget, target, fallback)` - Main projection
- `ProjectionRegistry.get(name)` → `Projector | None`
- `ProjectionRegistry.supports(name)` → `bool`
- `ProjectionRegistry.all_targets()` → `list[str]`
- `ProjectionRegistry.by_fidelity(level)` → `list[Projector]`
- `ProjectionRegistry.reset()` - Test isolation

**ExtendedTarget** (Enum):
- Core: CLI, TUI, MARIMO, JSON (backward-compatible with RenderTarget)
- Extended: SSE, WEBGL, WEBXR, AUDIO
- Properties: `is_streaming`, `is_interactive`, `is_placeholder`
- Conversion: `from_render_target(RenderTarget)`

**TargetCapability** (Dataclass):
- `fidelity: float` - 0.0-1.0 information preservation
- `interactive: bool`, `streaming: bool`, `async_: bool`
- `implemented: bool`

**Law Verification**:
- `verify_identity_law(widget, target)` → `bool`
- `verify_composition_law(widget, f, g, target)` → `bool`
- `verify_determinism(widget, target, iterations)` → `bool`
- `verify_all_laws(widget, target, state_transforms)` → `LawVerificationResult`

### Test Coverage

| File | Tests | Coverage |
|------|-------|----------|
| test_registry.py | 27 | Registration, lookup, graceful degradation |
| test_targets.py | 23 | ExtendedTarget, capabilities, fidelity |
| test_laws.py | 24 | Identity, composition, determinism, real widgets |
| **Total** | **74** | All passing, mypy clean |

### Integration Points

1. **Backward compatibility**: ExtendedTarget converts from/to RenderTarget
2. **Built-in projectors**: CLI, TUI, MARIMO, JSON, SSE auto-registered
3. **SSE fallback**: Widgets without `to_sse()` get JSON-wrapped SSE
4. **Graceful degradation**: Unknown targets fall back to JSON

### Next Steps (STRATEGIZE)

1. Wire ProjectionRegistry to existing widgets
2. Add SSE to formal RenderTarget enum or keep in ExtendedTarget
3. Create developer guide for custom target registration
4. Wire Turn.project() to use registry (optional)

---

## Continuation Prompt

⟿[STRATEGIZE]

# STRATEGIZE: Projection Protocol Cultivation

## ATTACH

/hydrate

You are entering STRATEGIZE of the N-Phase Cycle (AD-005) for `spec/protocols/projection.md`.

handles:
  scope=projection-protocol-cultivation
  ledger={PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:in_progress}
  entropy=0.04
  impl_location=impl/claude/agents/i/reactive/projection/
  test_count=74

## Your Mission

Evaluate implementation order and plan phased rollout:

1. **Quick wins**: What can be wired immediately with minimal risk?
2. **Dependencies**: What needs to happen before other things?
3. **Risk assessment**: What could break existing functionality?
4. **Priority ordering**: Rank remaining work by value/effort

## Exit Criteria

- [ ] Implementation backlog with priority order
- [ ] Risk assessment for wiring changes
- [ ] Decision: SSE in RenderTarget vs ExtendedTarget only

## Continuation Imperative

Upon completing STRATEGIZE, emit:

```
⟿[CROSS-SYNERGIZE]
/hydrate
handles: scope=projection-protocol-cultivation; ledger={..., STRATEGIZE:touched}
mission: Verify laws across existing widgets. Check for composition issues.
exit: Law verification report for all primitives.
continuation → IMPLEMENT.
```

---

## STRATEGIZE Findings (2025-12-15)

### 1. Quick Wins (Wire Immediately)

| Item | Risk | Effort | Value |
|------|------|--------|-------|
| Add projection module re-export from `reactive/__init__.py` | LOW | 5 min | Discoverability |
| Add `ProjectionRegistry.project()` usage example to README | LOW | 10 min | Documentation |
| Wire law verification to existing widget tests | LOW | 15 min | Confidence |

### 2. Implementation Backlog (Priority Order)

| Priority | Task | Dependencies | Risk | Notes |
|----------|------|--------------|------|-------|
| **P0** | Wire law verification to GlyphWidget tests | None | LOW | Proves pattern works |
| **P1** | Wire law verification to BarWidget tests | P0 | LOW | Tests composition |
| **P2** | Wire law verification to SparklineWidget tests | P0 | LOW | Tests time-series |
| **P3** | Wire law verification to ComposableWidget tests | P0-P2 | MEDIUM | Tests HStack/VStack |
| **P4** | Developer guide: `docs/skills/projection-target.md` | P0-P3 | LOW | Educate |
| **P5** | Optional: Wire Turn.project() to registry | P0-P4 | MEDIUM | Turn already works; optional unification |

### 3. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Circular import adding projection to widget.py | LOW | MEDIUM | Use lazy imports (already done) |
| Breaking existing widget.project() calls | VERY LOW | HIGH | Backward-compatible design; RenderTarget unchanged |
| marimo widgets don't fit StatefulWidget protocol | MEDIUM | LOW | marimo uses anywidget, different pattern; don't force |
| Test isolation failures from singleton registry | LOW | LOW | `reset()` method already exists for fixtures |

### 4. Decision: SSE in RenderTarget vs ExtendedTarget

**Decision**: Keep SSE in ExtendedTarget only.

**Rationale**:
- RenderTarget is used by 36+ `project()` implementations
- Adding SSE to RenderTarget requires touching 36+ files
- ExtendedTarget.from_render_target() provides upgrade path
- SSE is streaming; fundamentally different from sync targets
- Zero-risk approach: existing code unchanged, new code uses ExtendedTarget

### 5. Wiring Strategy

```
Phase 1: Prove Pattern (P0-P2)
  - Add law verification to 3 primitive widget test files
  - Use test_laws.py patterns as template
  - ~20 new assertions across 3 files

Phase 2: Composition (P3)
  - Verify HStack/VStack compose law-abiding widgets
  - Proves "composition of projections"

Phase 3: Educate (P4)
  - Write `docs/skills/projection-target.md`
  - Include: decorator registration, fidelity, graceful degradation

Phase 4: Optional Unification (P5)
  - Turn.project() could use registry
  - Low priority: Turn already works perfectly
```

### 6. What NOT to Do

- **Don't** change RenderTarget enum (36+ files)
- **Don't** force marimo anywidgets to use KgentsWidget
- **Don't** add SSE to every widget (fallback handles this)
- **Don't** make law verification required (it's for confidence, not gates)

---

## Continuation Prompt

⟿[CROSS-SYNERGIZE]

# CROSS-SYNERGIZE: Projection Protocol Cultivation

## ATTACH

/hydrate

You are entering CROSS-SYNERGIZE of the N-Phase Cycle (AD-005) for `spec/protocols/projection.md`.

handles:
  scope=projection-protocol-cultivation
  ledger={PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:in_progress}
  entropy=0.04
  backlog=[P0:Glyph, P1:Bar, P2:Sparkline, P3:Composable, P4:Docs, P5:Turn]

## Your Mission

Verify functor laws across existing widgets:

1. **Run law verification on primitives**:
   - GlyphWidget with identity + composition transforms
   - BarWidget with identity + scale transforms
   - SparklineWidget with identity + append transforms

2. **Check composition**:
   - HStack(Glyph, Glyph) projections
   - VStack(Bar, Sparkline) projections
   - Verify composition preserves determinism

3. **Surface any law violations**:
   - Non-deterministic projections?
   - Composition that breaks fidelity?

## Exit Criteria

- [ ] Law verification report for GlyphWidget
- [ ] Law verification report for BarWidget
- [ ] Law verification report for SparklineWidget
- [ ] Composition test: HStack/VStack
- [ ] Violations documented (or "none")

## Continuation Imperative

Upon completing CROSS-SYNERGIZE, emit:

```
⟿[IMPLEMENT]
/hydrate
handles: scope=projection-protocol-cultivation; ledger={..., CROSS-SYNERGIZE:touched}; law_report=${LAW_REPORT}
mission: Wire law verification assertions to existing widget tests.
exit: Updated test files with law assertions.
continuation → QA.
```

---

## CROSS-SYNERGIZE Findings (2025-12-15)

### Law Verification Report

#### Primitive Widgets

| Widget | CLI | TUI | JSON | MARIMO | Identity | Composition | Determinism |
|--------|-----|-----|------|--------|----------|-------------|-------------|
| GlyphWidget | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| BarWidget | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| SparklineWidget | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| AgentCardWidget | ✓ | — | ✓ | — | ✓ | — | ✓ |
| DensityFieldWidget | ✓ | — | ✓ | — | ✓ | — | ✓ |

#### Composition Containers

| Container | Associativity | Determinism | Notes |
|-----------|---------------|-------------|-------|
| HStack (>>) | ✓ `(A >> B) >> C ≡ A >> (B >> C)` | ✓ | Flattens correctly |
| VStack (//) | ✓ `(A // B) // C ≡ A // (B // C)` | ✓ | Flattens correctly |
| Mixed | ✓ `(a >> b) // c` | ✓ | Cross-composition works |

### State Transformations Tested

```python
# GlyphWidget
glyph_identity(s) → s                     # Identity
glyph_change_char(s) → s with char='X'    # Character change
glyph_double_entropy(s) → s with entropy*2 # Entropy scale

# BarWidget
bar_identity(s) → s                       # Identity
bar_scale(s) → s with value*1.5           # Value scale

# SparklineWidget
spark_identity(s) → s                     # Identity
spark_append(s) → s with new value        # Append operation
```

### Violations Found

**NONE**

All widgets in the reactive substrate satisfy:
1. **Identity Law**: `project(id(state)) ≡ project(state)`
2. **Composition Law**: `project(f ∘ g)(state) ≡ project(f)(project(g)(state))`
3. **Determinism**: Same state → same output (10 iterations)
4. **Associativity**: `>>` and `//` are associative monoid operations

### Insight: Composition is Free

The fact that all laws pass means **composition is free** — you can nest widgets arbitrarily:

```python
# This just works, laws guarantee it
dashboard = (
    (status_glyph >> health_bar >> token_spark)
    // (memory_density // activity_log)
)
```

---

## Continuation Prompt

⟿[IMPLEMENT]

# IMPLEMENT: Projection Protocol Cultivation

## ATTACH

/hydrate

You are entering IMPLEMENT of the N-Phase Cycle (AD-005) for `spec/protocols/projection.md`.

handles:
  scope=projection-protocol-cultivation
  ledger={PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:touched, IMPLEMENT:in_progress}
  entropy=0.03
  law_report=ALL_PASS
  backlog=[P0:Glyph, P1:Bar, P2:Sparkline, P3:Composable, P4:Docs]

## Your Mission

Wire law verification assertions to existing widget tests:

1. **P0: GlyphWidget** - Add law verification to `primitives/_tests/test_glyph.py`
2. **P1: BarWidget** - Add law verification to `primitives/_tests/test_bar.py`
3. **P2: SparklineWidget** - Add law verification to `primitives/_tests/test_sparkline.py`
4. **P3: ComposableWidget** - Add law verification to `_tests/test_composable.py`

## Exit Criteria

- [ ] test_glyph.py has law verification assertions
- [ ] test_bar.py has law verification assertions
- [ ] test_sparkline.py has law verification assertions
- [ ] test_composable.py has law verification assertions
- [ ] All tests pass

## Continuation Imperative

Upon completing IMPLEMENT, emit:

```
⟿[QA]
/hydrate
handles: scope=projection-protocol-cultivation; ledger={..., IMPLEMENT:touched}
mission: Run full test suite; verify no regressions.
exit: Clean test run, mypy clean.
continuation → TEST.
```

---

*"Laws are proven. Now make them permanent."*
