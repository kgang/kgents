---
path: plans/design-language-consolidation
status: complete
progress: 100
last_touched: 2025-12-18
touched_by: claude-opus-4-5
blocking: []
enables:
  - plans/core-apps/atelier-experience
  - plans/core-apps/punchdrunk-park
  - plans/web-refactor
session_notes: |
  2025-12-17: Plan created from deep audit of creative docs and UI components.
  - Audit covered 15+ files across docs, skills, specs, plans, implementations
  - Identified ~1200 lines of documentation redundancy
  - Identified component fragmentation across gallery/, projection/, three/
  - Core insight: Three functors compose all UI behavior: Layout[D], Content[D], Motion[M]
  - Decision: Create agents/design/ with DESIGN_OPERAD for generative patterns
  - Decision: Physically move gallery/ into projection/gallery/
  - Decision: Keep three/ separate (not under elastic/)
  2025-12-17 (Session 2): Phase 1 + Phase 2 + Phase 3 partial COMPLETE:
  - Created agents/design/ with types.py, polynomial.py, operad.py
  - Implemented LAYOUT_OPERAD, CONTENT_OPERAD, MOTION_OPERAD, DESIGN_OPERAD
  - 40 tests passing for design module
  - Moved gallery/ to projection/gallery/, updated imports
  - Trimmed elastic-ui-patterns.md from 970 to 263 lines (73% reduction)
  2025-12-17 (Session 3): Phase 3 + Phase 4 COMPLETE:
  - Added AD-008 Applied section to spec/protocols/projection.md
  - Merged ui-isomorphism-detection.md to summary + redirect (450 → 125 lines)
  - Merged docs/gallery/index.md into README.md (deleted duplicate)
  - Created protocols/agentese/contexts/design.py with concept.design.* paths
  - Updated crown_jewels.py with DESIGN_PATHS (21 paths documented)
  - All 40 tests passing
  2025-12-17 (Session 4): Hardened AGENTESE integration:
  - Added @node decorators to all design nodes (layout, content, motion, operad, context)
  - Added design import to gateway.py for node discovery
  - Verified 5 design paths registered in AGENTESE registry
  - All 40 tests passing
  2025-12-17 (Session 5 - HONESTY AUDIT):
  - Applied spec/principles.md rigorously to audit implementation
  - FIXED: Tautological law verifications → now use LawStatus.STRUCTURAL with honest messages
  - FIXED: Missing DesignSheaf → now stub that raises NotImplementedError
  - FIXED: Missing React projection → created useDesignPolynomial hook
  - DOCUMENTED: Gap between PolyAgent composition and actual React components
  - Status downgraded from 100% to 85% (honest assessment)
  - Remaining: Sheaf implementation, true generative UI, runtime law testing
  2025-12-18 (Session 6 - COMPLETION):
  - GAP #1: Created agents/design/generate.py with generative UI functor (27 tests)
    - ComponentSpec dataclass for JSX generation
    - generate_component(operad, operation, *children) → JSX string
    - Implements split/drawer equivalence at compact density
  - GAP #2: Implemented DesignSheaf with all 4 methods (25 tests)
    - overlap(): Computes context intersection (hierarchy + siblings)
    - restrict(): Extracts local state with density override support
    - compatible(): Validates sibling consistency
    - glue(): Combines locals into global with law enforcement
  - GAP #3: Added property-based tests with Hypothesis (15 tests)
    - composition_natural: Verified order independence for L×C×M
    - content_lattice: Verified transitivity and reflexivity
    - motion_identity: Verified identity is unit for composition
    - motion_should_animate: Verified animation gating law
  - GAP #4: Refactored ElasticSplit to use useDesignPolynomial
    - Uses state.density instead of raw width comparison
    - Added collapseAtDensity prop (deprecates collapseAt)
    - TypeScript compiles, all 107 design tests pass
  - Plan marked COMPLETE at 100%
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: complete
  CROSS-SYNERGIZE: complete
  IMPLEMENT: complete
  QA: complete
  TEST: complete
  EDUCATE: complete
  MEASURE: complete
  REFLECT: complete
entropy:
  planned: 0.08
  spent: 0.07
  returned: 0.01
---

# Design Language Consolidation

> *"Three functors are necessary and sufficient: Layout[D], Content[D], Motion[M]. Everything else is composition."*

**Audit Source**: Deep analysis of 15+ creative/UI files (2025-12-17)
**Core Outcome**: Unified Design Language System grounded in category theory

---

## Overview

| Aspect | Detail |
|--------|--------|
| **Problem** | Conceptual redundancy across 18 docs, component fragmentation across 9 categories |
| **Solution** | Consolidate into unified system with three composition operads |
| **Savings** | ~1200 lines documentation, clearer component boundaries |
| **Status** | Plan complete, ready for implementation |

---

## The Core Insight

All creative UI concepts reduce to three orthogonal **projection functors**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    UNIFIED DESIGN LANGUAGE SYSTEM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Layout[D] : WidgetTree → Structure[D]                                       │
│    D ∈ {compact, comfortable, spacious}                                     │
│    Components: ElasticSplit, ElasticContainer, BottomDrawer, FloatingActions │
│                                                                              │
│  Content[D] : State → ContentDetail[D]                                       │
│    D ∈ {icon, title, summary, full}                                         │
│    Behavior: What to show at what space                                      │
│                                                                              │
│  Motion[M] : Component → AnimatedComponent[M]                                │
│    M ∈ {breathe, pop, shake, shimmer, page-transition}                      │
│    Components: Joy library primitives                                        │
│                                                                              │
│  Composition: UI = Layout[D] ∘ Content[D] ∘ Motion[M]                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Create `agents/design/` Foundation

**Goal**: Establish categorical foundation for design language

**Deliverables**:
- [x] Create `agents/design/__init__.py` with exports
- [x] Create `agents/design/polynomial.py` — DESIGN_POLYNOMIAL state machine
- [x] Create `agents/design/operad.py` — Three composition operads
- [x] Create `agents/design/types.py` — Density, ContentLevel, MotionType enums
- [x] Create `agents/design/_tests/test_operad.py` — Law verification tests (40 tests passing)

**The Three Operads**:

```python
# agents/design/operad.py

from agents.operad import Operad, Operation, verify_laws

# LAYOUT_OPERAD: Structural composition grammar
LAYOUT_OPERAD = Operad(
    name="LAYOUT",
    operations={
        "split": Operation(
            name="split",
            arity=2,
            signature="(Widget, Widget) → ElasticSplit",
            description="Two-pane layout with collapse behavior",
        ),
        "stack": Operation(
            name="stack",
            arity=-1,  # variadic
            signature="(*Widget) → ElasticContainer",
            description="Vertical/horizontal stack",
        ),
        "drawer": Operation(
            name="drawer",
            arity=2,
            signature="(Trigger, Content) → BottomDrawer",
            description="Collapsible drawer pattern",
        ),
        "float": Operation(
            name="float",
            arity=-1,
            signature="(*Action) → FloatingActions",
            description="Floating action buttons",
        ),
    },
    laws=[
        "split(a, drawer(t, b)) ≅ drawer(t, split(a, b)) at compact",
        "stack(split(a,b), c) ≅ split(stack(a,c), b)",
    ],
)

# CONTENT_OPERAD: Content degradation grammar
CONTENT_OPERAD = Operad(
    name="CONTENT",
    operations={
        "degrade": Operation(
            name="degrade",
            arity=2,
            signature="(Full, Level) → Truncated",
            description="Reduce content to fit space",
        ),
        "compose": Operation(
            name="compose",
            arity=2,
            signature="(Widget, Widget) → Combined",
            description="Combine widget content",
        ),
    },
    laws=[
        "degrade(x, icon) ⊆ degrade(x, title) ⊆ degrade(x, summary) ⊆ degrade(x, full)",
        "compose(degrade(a, L), degrade(b, L)) = degrade(compose(a, b), L)",
    ],
)

# MOTION_OPERAD: Animation composition grammar
MOTION_OPERAD = Operad(
    name="MOTION",
    operations={
        "breathe": Operation(name="breathe", arity=1, signature="Widget → Animated"),
        "pop": Operation(name="pop", arity=1, signature="Widget → Animated"),
        "shake": Operation(name="shake", arity=1, signature="Widget → Animated"),
        "shimmer": Operation(name="shimmer", arity=1, signature="Widget → Animated"),
        "chain": Operation(
            name="chain",
            arity=2,
            signature="(Motion, Motion) → Sequential",
            description="Sequential animation",
        ),
        "parallel": Operation(
            name="parallel",
            arity=2,
            signature="(Motion, Motion) → Simultaneous",
            description="Parallel animation",
        ),
    },
    laws=[
        "chain(identity, m) = m",
        "chain(m, identity) = m",
        "parallel(m, identity) = m",
        "!shouldAnimate => all operations = identity",
    ],
)

# Combined design operad
DESIGN_OPERAD = Operad(
    name="DESIGN",
    operations={
        **LAYOUT_OPERAD.operations,
        **CONTENT_OPERAD.operations,
        **MOTION_OPERAD.operations,
    },
    laws=[
        *LAYOUT_OPERAD.laws,
        *CONTENT_OPERAD.laws,
        *MOTION_OPERAD.laws,
        "Layout[D] ∘ Content[D] ∘ Motion[M] is natural",
    ],
)
```

**Success Criteria**: All operad laws verify, 50+ tests passing

---

### Phase 2: Component Consolidation

**Goal**: Reduce component fragmentation, establish clear boundaries

#### 2.1: Move `gallery/` into `projection/gallery/`

**Current**:
```
web/src/components/
├── gallery/
│   ├── PilotCard.tsx
│   ├── ProjectionView.tsx
│   ├── OverrideControls.tsx
│   ├── CategoryFilter.tsx
│   └── index.ts
├── projection/
│   ├── widgets/
│   └── ...
```

**Target**:
```
web/src/components/projection/
├── gallery/              # MOVED FROM components/gallery/
│   ├── PilotCard.tsx
│   ├── ProjectionView.tsx
│   ├── OverrideControls.tsx
│   ├── CategoryFilter.tsx
│   └── index.ts
├── widgets/
└── index.ts              # Re-export gallery components
```

**Tasks**:
- [x] Move `components/gallery/` to `components/projection/gallery/`
- [x] Update all imports in consuming files
- [x] Add re-exports from `components/projection/index.ts`
- [x] Remove empty `components/gallery/` directory
- [x] Update `GalleryPage.tsx` imports

#### 2.2: Keep `three/` Separate (Decision: No Change)

Per user decision, 3D components remain in `components/three/`. Document the relationship to elastic in comments.

**Success Criteria**: No broken imports, all tests pass

---

### Phase 3: Documentation Deduplication

**Goal**: Reduce ~1200 lines of redundant documentation

#### 3.1: Enhance `spec/protocols/projection.md`

Add new sections:
- [x] **AD-008 Applied**: Move isomorphism detection content here
- [x] **Motion Projection**: Add motion functor documentation
- [x] **Composition Laws**: Add operad references

#### 3.2: Trim `docs/skills/elastic-ui-patterns.md`

Current: 970 lines → **Actual: 263 lines** (73% reduction!)

Remove:
- [x] Density-Content Isomorphism section (moved to projection.md)
- [x] Physical Constraints section (moved to projection.md)
- [x] Duplicated Layout Primitives table
- [x] Verbose refactoring guide and real-world examples
- [x] Detailed floating overlay pattern (kept essentials)

Keep:
- [x] Quick reference for developers
- [x] Code examples and patterns
- [x] Links to spec for theory

#### 3.3: Merge `docs/skills/ui-isomorphism-detection.md`

- [x] Move core content to `spec/protocols/projection.md` AD-008 section
- [x] Convert original file to redirect/summary pointing to spec
- [x] Keep audit workflow section (practical, unique)

#### 3.4: Merge `docs/gallery/` Files

- [x] Merge `index.md` content into `README.md`
- [x] Delete `index.md`

**Success Criteria**: Net reduction of ~800 lines, no information loss

---

### Phase 4: AGENTESE Integration

**Goal**: Wire design operads to AGENTESE paths

**New Paths**:
```
concept.design.layout.manifest     — Current layout state
concept.design.layout.compose      — Apply layout operation
concept.design.content.manifest    — Current content level
concept.design.content.degrade     — Apply degradation
concept.design.motion.manifest     — Current motion state
concept.design.motion.apply        — Apply motion primitive
concept.design.operad.verify       — Verify composition laws
```

**Tasks**:
- [x] Create `protocols/agentese/contexts/design.py`
- [x] Register nodes with BaseLogosNode pattern
- [x] Wire to `agents/design/` operads
- [x] Add to `crown_jewels.py` PATHS documentation (21 paths)

---

## File Changes Summary

### Creates
| File | Purpose |
|------|---------|
| `agents/design/__init__.py` | Module exports |
| `agents/design/polynomial.py` | DESIGN_POLYNOMIAL |
| `agents/design/operad.py` | Three composition operads |
| `agents/design/types.py` | Enums and type definitions |
| `agents/design/_tests/test_operad.py` | Law verification |
| `protocols/agentese/contexts/design.py` | AGENTESE wiring |

### Moves
| From | To |
|------|-----|
| `web/src/components/gallery/*` | `web/src/components/projection/gallery/*` |

### Modifies
| File | Change |
|------|--------|
| `spec/protocols/projection.md` | Add AD-008, Motion sections |
| `docs/skills/elastic-ui-patterns.md` | Trim to 400 lines |
| `docs/skills/ui-isomorphism-detection.md` | Convert to summary + redirect |
| `docs/gallery/README.md` | Merge index.md content |
| `docs/systems-reference.md` | Add Design Operads section |

### Deletes
| File | Reason |
|------|--------|
| `docs/gallery/index.md` | Merged into README.md |
| `web/src/components/gallery/` | Moved to projection/gallery/ |

---

## Categorical Alignment

### The Unified Structure

Every design element instantiates the same pattern:

| Layer | Layout | Content | Motion |
|-------|--------|---------|--------|
| **Polynomial** | `LayoutPolynomial[Density]` | `ContentPolynomial[Level]` | `MotionPolynomial[Type]` |
| **Operad** | `LAYOUT_OPERAD` | `CONTENT_OPERAD` | `MOTION_OPERAD` |
| **Sheaf** | ViewportCoherence | ContentConsistency | MotionHarmony |

### Connection to Existing Infrastructure

```python
# Design operads compose with existing infrastructure
from agents.poly import PolyAgent
from agents.design import LAYOUT_OPERAD, DESIGN_POLYNOMIAL

# Layout follows polynomial state machine
layout_agent = PolyAgent(
    initial_state=LayoutState(density="spacious"),
    directions=DESIGN_POLYNOMIAL.directions,
    transition=DESIGN_POLYNOMIAL.transition,
)

# Verify composition laws
LAYOUT_OPERAD.verify_laws()  # Must pass before use
```

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Documentation lines reduced | ~800 |
| Component directories consolidated | 1 (gallery → projection) |
| New operad tests | 50+ |
| Broken imports | 0 |
| AGENTESE paths added | 7 |

---

## Dependencies

| System | Usage |
|--------|-------|
| `agents/operad/` | Base operad infrastructure |
| `agents/poly/` | Polynomial agent patterns |
| `protocols/agentese/` | AGENTESE wiring |
| `web/src/components/elastic/` | Layout components |
| `web/src/components/joy/` | Motion components |
| `web/src/components/projection/` | Target for gallery merge |

---

## Open Questions

1. **Sheaf formalization**: Should we create explicit sheaf gluing for cross-component coherence?
2. **Runtime verification**: Should operad laws be verified at runtime or just in tests?
3. **Migration path**: How to handle external consumers of `components/gallery/` imports?

---

## Honesty Audit (Session 5)

Applied `spec/principles.md` rigorously. Findings:

### What Was Fixed

| Issue | Fix | File |
|-------|-----|------|
| Tautological law verifications (stubs returning PASSED) | Added `LawStatus.STRUCTURAL` for type-level laws, honest messages | `operad/core.py`, `design/operad.py` |
| Missing Sheaf layer (2/3 categorical stack) | Added `DesignSheaf` stub that raises `NotImplementedError` | `design/sheaf.py` |
| Missing React projection (Layer 7) | Created `useDesignPolynomial` hook mirroring Python polynomial | `hooks/useDesignPolynomial.ts` |
| Undocumented PolyAgent vs UI gap | Added caveat documentation to `design/operad.py` docstring | `design/operad.py` |

### What Gaps Remain

**ALL GAPS RESOLVED (Session 6)**

| Gap | Status | Resolution |
|-----|--------|------------|
| `DesignSheaf` implementation | ✅ Complete | `agents/design/sheaf.py` - 25 tests |
| True generative UI | ✅ Complete | `agents/design/generate.py` - 27 tests |
| Runtime law verification | ✅ Complete | `test_laws_property.py` - 15 Hypothesis tests |
| React components consuming hook | ✅ Complete | `ElasticSplit.tsx` uses `useDesignPolynomial` |

### Categorical Stack Status

**ALL LAYERS COMPLETE**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES   useDesignPolynomial ✓ | ElasticSplit consuming ✓ │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL     concept.design.* paths ✓                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE         @node decorators ✓                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE        agents/design/ ✓                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR        DESIGN_OPERAD with laws ✓                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT      DESIGN_POLYNOMIAL (144 states) ✓                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. SHEAF COHERENCE       DesignSheaf (complete) ✓                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Principle Violations Found (Now Fixed)

1. **Ethical (transparency)**: Law verifications claimed "verified" but were stubs → Now marked `STRUCTURAL` with honest messages
2. **Composable (morphisms)**: Claimed operads compose UI but only compose PolyAgents → Now documented the gap
3. **Generative (spec→impl)**: Claimed "generative UI" without generation code → Now honestly scoped as "future work"

---

## References

- Audit session: 2025-12-17 deep creative/UI audit
- `spec/protocols/projection.md` — Projection Protocol spec
- `spec/principles.md` — Core principles (AD-008 Simplifying Isomorphisms)
- `docs/skills/elastic-ui-patterns.md` — Current elastic patterns
- `docs/skills/ui-isomorphism-detection.md` — Isomorphism extraction skill
- `plans/autopoietic-architecture.md` — AD-009 metaphysical stack

---

*Last updated: 2025-12-17*
