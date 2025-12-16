---
path: plans/_continuations/wave-1-hero-path-polish
status: pending
progress: 0
last_touched: 2025-12-16
touched_by: claude-opus-4
blocking: []
enables:
  - Wave 2 Tier 2 Enablement
  - Product-market fit
  - "Wow moment" for new users
session_notes: |
  Wave 0 (5 Foundations) is COMPLETE. Now entering Wave 1.

  Goal: Brain + Gestalt + Gardener at 100% - undeniably good.
  Success metric: New user experiences "wow moment" in < 5 minutes.
---

# Wave 1: Hero Path Polish - Continuation Prompt

> *"The Hero Path is not three apps. It is one experience in three movements."*
> *Understand (Gestalt) → Remember (Brain) → Grow (Gardener)*

## Context

You are the **Crown Jewel Executor** beginning Wave 1 of the Enlightened Crown strategy.

### Prerequisites (Complete)
- ✅ **Wave 0**: All 5 Foundations implemented
  - Foundation 1: AGENTESE Path Visibility (27 tests)
  - Foundation 2: Observer Switcher (ObserverSwitcher component)
  - Foundation 3: Polynomial Diagram (34 tests)
  - Foundation 4: Synergy Event Bus (34 tests)
  - Foundation 5: Animation Primitives (45 tests, Breathe/Pop/Shake/Shimmer/PersonalityLoading/EmpathyError/celebrate)

### Current Jewel Status

| Jewel | Progress | What Works | What's Missing |
|-------|----------|------------|----------------|
| **Brain** | 95% | Capture, ghost surfacing, 3D topology, API, tests | Observer switching detail view, auto-link feedback |
| **Gestalt** | 60% | Module analysis, health grades, 3D viz, drift detection | Governance UI polish, unified topology with Brain |
| **Gardener** | 25% | N-Phase tracking, partial CLI | Polynomial viz, Brain/Gestalt context, session orchestration |

## The Mission

**Create ONE undeniable experience that proves everything:**
- AGENTESE works (and users can see it)
- Observer-dependent perception is real (and users can feel it)
- Polynomial state machines are beautiful (and users can navigate them)
- Cross-jewel synergy is automatic (and users benefit without thinking)

### The Hero Path Flow

```
USER STARTS
     │
     ▼
┌─────────┐    captures     ┌─────────┐    analyzes    ┌─────────┐
│  Brain  │ ◄──────────────│ Gestalt │ ◄─────────────│ Gardener │
│         │                 │         │                │          │
│ Memory  │    provides     │  Code   │    context     │   Meta   │
│ Store   │ ───────────────▶│ Analysis│ ──────────────▶│ Interface│
└─────────┘    context      └─────────┘    for         └─────────┘
     │                            │                          │
     │                            │                          │
     └────────────────────────────┴──────────────────────────┘
                      ALL SYNCED VIA AGENTESE

DEMO PATH (< 5 minutes):
1. kg gestalt analyze .     → See your codebase health
2. kg brain capture <url>   → Capture research
3. kg gardener              → Orchestrate development session
```

## Tier 1 Tasks

### Brain Completion (95% → 100%)

| Task | Priority | Notes |
|------|----------|-------|
| Crystal detail with observer views | HIGH | Click crystal → show same data through different observers |
| Auto-link feedback in UI | MEDIUM | "Linked to: 3 crystals" with names visible |
| Observer switching in crystal modal | HIGH | Switch observers, see content transform |
| Capture success celebration | DONE | celebrate() integrated in Wave 0 |

**Key Files:**
- `impl/claude/web/src/pages/Brain.tsx`
- `impl/claude/web/src/components/path/ObserverSwitcher.tsx`
- `impl/claude/protocols/api/brain.py`

**User Story:**
```
As a user, when I click a crystal in the Brain topology:
1. I see a detail panel with the crystal's content
2. I see "Observer: technical" with a switcher
3. When I switch to "casual", the same content renders differently
4. I understand that the crystal is the same, but my perspective changes
```

### Gestalt Completion (60% → 100%)

| Task | Priority | Notes |
|------|----------|-------|
| Governance violations panel | HIGH | Beautiful visualization of drift violations |
| Module health trends | MEDIUM | Sparklines showing health over time |
| Architecture suggestions | LOW | "Consider extracting X into its own module" |
| Unified topology style with Brain | MEDIUM | Same visual language, different data |

**Key Files:**
- `impl/claude/web/src/pages/Gestalt.tsx`
- `impl/claude/web/src/components/gestalt/`
- `impl/claude/protocols/gestalt/governance.py`

**User Story:**
```
As a user, when I analyze my codebase:
1. I immediately see the overall health grade (with Breathe animation if A+)
2. I can explore modules in 3D, with violations highlighted in red
3. Clicking a violation shows me exactly what's wrong and how to fix it
4. The analysis auto-captures to Brain (synergy already working)
```

### Gardener Completion (25% → 100%)

| Task | Priority | Notes |
|------|----------|-------|
| Polynomial state visualization | HIGH | Show N-Phase state machine in CLI and Web |
| Brain context integration | HIGH | Show relevant crystals for current phase |
| Gestalt context integration | HIGH | Show codebase health in Gardener context |
| Session orchestration | HIGH | Plan 07 from crown-jewels-audit |
| CLI polish | MEDIUM | `kg gardener` as the main entry point |
| Web interface | LOW | Simple session viewer initially |

**Key Files:**
- `impl/claude/protocols/cli/handlers/grow.py` (gardener CLI)
- `impl/claude/protocols/agentese/contexts/gardener.py`
- `impl/claude/web/src/components/polynomial/PolynomialDiagram.tsx`

**User Story:**
```
As a user, when I start a Gardener session:
1. I see "concept.gardener.manifest" path displayed
2. I see my current N-Phase state (PLAN → RESEARCH → DEVELOP → ...)
3. I see relevant Brain crystals: "3 crystals match this context"
4. I see Gestalt status: "impl/claude/ health: B+"
5. I can transition states and see the polynomial diagram update
```

## Implementation Guide

### Phase 1: Brain Crystal Detail View (2-3 days)

```tsx
// New component: CrystalDetailModal.tsx
interface CrystalDetailModalProps {
  crystal: Crystal;
  isOpen: boolean;
  onClose: () => void;
}

function CrystalDetailModal({ crystal, isOpen, onClose }) {
  const [observer, setObserver] = useObserverState('brain', 'technical');
  const { data: manifestedContent } = useCrystalManifest(crystal.id, observer);

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      {/* Header with crystal info */}
      <div className="flex justify-between">
        <h2>{crystal.title}</h2>
        <ObserverSwitcher
          current={observer}
          available={DEFAULT_OBSERVERS.brain}
          onChange={setObserver}
        />
      </div>

      {/* Content rendered for current observer */}
      <div className="prose">
        {manifestedContent}
      </div>

      {/* Auto-links */}
      {crystal.links.length > 0 && (
        <div className="mt-4">
          <h3>Linked to:</h3>
          {crystal.links.map(link => (
            <CrystalLink key={link.id} crystal={link} />
          ))}
        </div>
      )}
    </Modal>
  );
}
```

### Phase 2: Gestalt Governance Polish (2-3 days)

```tsx
// Enhanced violation display in ModuleDetailPanel
function ViolationsPanel({ violations }) {
  return (
    <div className="space-y-2">
      {violations.map(v => (
        <Shake trigger={v.isNew} intensity="gentle">
          <div className="bg-red-900/20 border-l-2 border-red-500 p-3">
            <div className="font-semibold text-red-400">{v.rule}</div>
            <div className="text-sm text-red-300/80">
              {v.source} → {v.target}
            </div>
            <div className="mt-2 text-xs text-gray-400">
              💡 {v.suggestion}
            </div>
          </div>
        </Shake>
      ))}
    </div>
  );
}
```

### Phase 3: Gardener Integration (3-4 days)

```python
# Enhanced Gardener CLI with context
@hollow.command()
async def gardener(ctx: HollowContext):
    """The autopoietic development interface."""

    # Display AGENTESE path
    display_path_header(
        path="concept.gardener.manifest",
        aspect="manifest",
    )

    # Get current session state
    session = await get_or_create_session()

    # Show polynomial state
    print_polynomial_diagram(session.state_machine)

    # Show Brain context
    crystals = await brain.ghost_surface(
        context=session.current_phase,
        limit=3
    )
    if crystals:
        print(f"\n🧠 Relevant memories ({len(crystals)}):")
        for c in crystals:
            print(f"   • {c.title} ({c.relevance:.0%})")

    # Show Gestalt context
    gestalt = await gestalt_store.get_summary()
    print(f"\n🏗️ Codebase health: {gestalt.overall_grade}")
    if gestalt.violations:
        print(f"   ⚠️ {len(gestalt.violations)} drift violations")

    # Prompt for action
    print(f"\nCurrent phase: {session.current_phase}")
    print(f"Available: {session.valid_transitions}")
```

## Success Criteria

- [ ] **Brain**: Crystal detail modal with observer switching
- [ ] **Brain**: Auto-link feedback visible in UI
- [ ] **Gestalt**: Governance violations panel with suggestions
- [ ] **Gardener**: Polynomial state visualization (CLI)
- [ ] **Gardener**: Brain context integration
- [ ] **Gardener**: Gestalt context integration
- [ ] **Hero Path**: New user completes demo path in < 5 minutes
- [ ] **Hero Path**: Each jewel has at least one "wow moment"

## Testing Strategy

```bash
# Run all Hero Path tests
npm run test:run -- tests/unit/joy/
npm run test:run -- tests/unit/polynomial/
pytest impl/claude/protocols/cli/handlers/_tests/test_brain.py
pytest impl/claude/protocols/cli/handlers/_tests/test_grow.py
pytest impl/claude/protocols/gestalt/_tests/
```

## Session Protocol

1. **Start**: Read this file + `plans/crown-jewels-enlightened.md`
2. **Focus**: Pick ONE task from one jewel (Brain → Gestalt → Gardener)
3. **Implement**: Code + tests + integration
4. **Integrate**: Ensure cross-jewel synergies work
5. **Test**: Run hero path manually
6. **Update**: Mark tasks complete, update progress

## Recommended Order

1. **Brain Crystal Detail** - Quick visual win, builds on existing topology
2. **Gestalt Violations Panel** - Improves existing functionality
3. **Gardener Polynomial CLI** - Core Gardener feature
4. **Gardener Context Integration** - Ties it all together
5. **Hero Path Manual Test** - Verify < 5 minute experience

## Reference Files

| File | Purpose |
|------|---------|
| `plans/crown-jewels-enlightened.md` | Master plan |
| `plans/core-apps/holographic-brain.md` | Brain status |
| `plans/core-apps/gestalt-architecture-visualizer.md` | Gestalt status |
| `plans/core-apps/the-gardener.md` | Gardener spec |
| `impl/claude/web/src/components/joy/` | Animation primitives |
| `impl/claude/web/src/components/path/` | Observer switching |
| `impl/claude/web/src/components/polynomial/` | State visualization |

## After Wave 1

When all success criteria are met, **Wave 1 is complete**.

Next: **Wave 2: Tier 2 Enablement**
- Atelier uses Brain for memory
- Coalition uses Gardener for orchestration
- Both feel like extensions, not separate apps

---

*"The garden tends itself, but only because we planted it together."*

*Created: 2025-12-16*
