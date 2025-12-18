---
path: docs/skills/vertical-slice-pattern
status: active
progress: 100
last_touched: 2025-12-18
touched_by: claude-opus-4-5
blocking: []
enables: [all-crown-jewels, autopoietic-architecture]
session_notes: |
  Created during autopoietic-architecture Phase 3.
  Reference agent: Agent Town (world.town) - 8/8 layer compliance.
  Proves: chat + web + SaaS all work through unified stack.
  2025-12-18: Integrated SpecGraph Discovery Mode workflow.
  2025-12-18: Added Three Modes philosophy (Advisory/Gatekeeping/Aspirational).
  Key insight: SpecGraph serves creativity, not the reverse.
phase_ledger:
  PLAN: complete
  REFLECT: complete
---

# Skill: Vertical Slice Pattern (AD-009)

> *"Every agent is a vertical slice from persistence to projection."*

**Difficulty**: Advanced
**Prerequisites**: `polynomial-agent.md`, `crown-jewel-patterns.md`, `metaphysical-fullstack.md`
**Source**: Phase 3 of Autopoietic Architecture (Reference Agent Proof)
**Reference Implementation**: Agent Town (`world.town`)

---

## The Philosophy: SpecGraph Serves You

> *"The scaffold enables the building. When the building stands, the scaffold can be removed."*

SpecGraph is a **tool for alignment**, not a **master to obey**. The autopoietic vision is regenerability—the ability to delete and recreate. But regenerability requires **creativity first, verification second**.

### The Paradox of Rigid Specification

If spec-impl alignment is enforced rigidly:
- Exploratory impl is blocked before it can discover what spec should say
- The Accursed Share (entropy budget for creativity) is crushed
- "Joy-Inducing" becomes "Friction-Inducing"

**The enlightened path**: SpecGraph modes that match your intent.

### The Bidirectional Contract

Autopoiesis is not `Spec → Impl`. It's an **adjunction**:

```
Compile ⊣ Reflect

Spec ←──Reflect──← Impl
  │                  ↑
  └───Compile───────→┘
```

Neither direction is privileged. Sometimes you know what you want (spec → impl). Sometimes you discover what exists (impl → spec). Both flows are valid.

---

## Overview

The Vertical Slice Pattern ensures every Crown Jewel implements ALL seven layers of the Metaphysical Agent Stack. This creates uniform composability and enables the compiler contract (spec → impl → projection).

---

## The Seven-Layer Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES   CLI │ TUI │ Web │ marimo │ JSON │ SSE            │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL     logos.invoke(path, observer, **kwargs)           │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE         @node decorator, aspects, effects, affordances   │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE        services/<name>/ — Crown Jewel business logic    │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR        Composition laws, operation signatures           │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT      PolyAgent[S, A, B]: state × input → output       │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. SHEAF COHERENCE       Local views → global consistency                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Reference Implementation: Agent Town

Town scored 8/8 on the layer compliance check and serves as the gold standard.

### Layer 1: Sheaf Coherence

Citizens compose coherently across regions. Local citizen views (per-region) glue into global town state.

**Location**: `agents/town/memory.py`, `agents/town/coalition.py`

### Layer 2: Polynomial Agent

```python
# agents/town/polynomial.py
CITIZEN_POLYNOMIAL: PolyAgent[CitizenPhase, Any, CitizenOutput] = PolyAgent(
    name="CitizenPolynomial",
    positions=frozenset(CitizenPhase),  # 5 phases
    _directions=citizen_directions,      # mode-dependent inputs
    _transition=citizen_transition,      # state machine
)
```

**Key Features**:
- 5 positions: `IDLE`, `SOCIALIZING`, `WORKING`, `REFLECTING`, `RESTING`
- Right to Rest: `RESTING` phase only accepts `WakeInput`
- Mode-dependent directions: each phase has different valid inputs

### Layer 3: Operad Grammar

```python
# agents/town/operad.py
TOWN_OPERAD = create_town_operad()  # 8 operations, registered in OperadRegistry

# Operations with metabolics (token costs)
ops["greet"] = Operation(name="greet", arity=2, compose=_greet_compose, ...)
ops["gossip"] = Operation(name="gossip", arity=2, compose=_gossip_compose, ...)
ops["trade"] = Operation(name="trade", arity=2, compose=_trade_compose, ...)
ops["solo"] = Operation(name="solo", arity=1, compose=_solo_compose, ...)

# Phase 2: dispute, celebrate, mourn, teach

# Laws: locality, rest_inviolability, coherence_preservation
```

**Key Features**:
- Extends `AGENT_OPERAD` universal operations
- Registered in `OperadRegistry` (CI gate verified)
- Metabolics: token costs per operation for budget management

### Layer 4: Service Module

```
services/town/
├── __init__.py
├── node.py           # TownNode (AGENTESE interface)
├── persistence.py    # TownPersistence (data layer)
├── inhabit_node.py   # InhabitNode (nested experience)
└── _tests/
    └── test_node.py  # 37 tests
```

**Key Features**:
- Persistence layer with TableAdapter + D-gent integration
- Clear separation: node (interface) vs persistence (storage)
- Nested node for INHABIT mode

### Layer 5: AGENTESE Node

```python
# services/town/node.py
@node(
    "world.town",
    description="Agent Town - Westworld simulation with polynomial citizens",
    dependencies=("town_persistence",),
)
class TownNode(BaseLogosNode):
    """
    AGENTESE node for Agent Town Crown Jewel.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.
    """

    async def manifest(self, observer: Observer) -> Renderable:
        """world.town.manifest"""
        status = await self._persistence.manifest()
        return TownManifestRendering(status=status)

    async def _invoke_aspect(self, aspect: str, observer: Observer, **kwargs):
        """Route to: citizen.list, citizen.get, converse, turn, etc."""
        ...
```

**Key Features**:
- `@node` decorator for registry auto-registration
- Observer-dependent affordances
- Rendering types for multi-projection

### Layer 6: AGENTESE Protocol

```python
# Via Logos
await logos.invoke("world.town.manifest", observer)
await logos.invoke("world.town.citizen.list", observer, active_only=True)
await logos.invoke("world.town.converse", observer, name="Socrates")

# Gateway verifies registration
from protocols.agentese.registry import get_registry
registry = get_registry()
assert registry.has("world.town")  # True
```

**Key Features**:
- Path registered at import time via `@node`
- Gateway auto-imports service node modules
- Discovery endpoint: `/agentese/discover`

### Layer 7: Projection Surfaces

```tsx
// web/src/pages/Town.tsx - Thin wrapper (<50 LOC)
export default function TownPage() {
  const loader = useTownLoader(paramTownId);
  const stream = useTownStreamWidget({ townId: loader.townId || '' });

  return (
    <StreamPathProjection jewel="coalition" loader={loader} stream={stream}>
      {(s, ctx) => (
        <TownVisualization
          townId={ctx.entityId}
          dashboard={s.dashboard}
          events={s.events}
          ...
        />
      )}
    </StreamPathProjection>
  );
}
```

**Key Features**:
- Projection-first: page is thin wrapper
- SSE streaming for real-time updates
- Density-adaptive (mobile/tablet/desktop)

### API/SaaS Integration

```python
# protocols/api/app.py - Gateway mount
gateway = mount_gateway(
    app,
    prefix="/agentese",
    container=container,
    enable_streaming=True,
    enable_websocket=True,
)

# Town endpoints auto-exposed via gateway:
# GET  /agentese/world/town/manifest
# POST /agentese/world/town/citizen/list
# POST /agentese/world/town/converse
# WS   /ws/town/{town_id}
```

---

## Second Reference: Emergence (Cymatics Design Experience)

Emergence demonstrates **operad inheritance** and **circadian modulation**—patterns not shown in Town.

### Key Distinguishing Patterns

| Pattern | Implementation |
|---------|----------------|
| **Operad Inheritance** | `EMERGENCE_OPERAD` extends `DESIGN_OPERAD` via `**DESIGN_OPERAD.operations` |
| **Circadian Modulation** | 4 phases (dawn/noon/dusk/midnight) modify qualia coordinates |
| **Qualia Space** | 7-dimensional cross-modal aesthetics (warmth, weight, tempo, texture, brightness, saturation, complexity) |
| **Law Honesty** | `pattern_commutativity` returns STRUCTURAL (design constraint, not runtime invariant) |

### Layer Highlights

```python
# Layer 2: 5-phase polynomial
EMERGENCE_POLYNOMIAL: PolyAgent[EmergencePhase, Any, EmergenceOutput]
# Phases: IDLE → LOADING → GALLERY → EXPLORING → EXPORTING

# Layer 3: Operad inheritance
EMERGENCE_OPERAD = Operad(
    operations={
        "select_family": ...,
        "modulate_qualia": ...,
        **DESIGN_OPERAD.operations,  # Inherit layout/content/motion
    },
    laws=[*DESIGN_OPERAD.laws, ...],  # Inherit laws too
)

# Layer 1: Sheaf with overlap semantics
class EmergenceSheaf:
    def overlap(self, a: Context, b: Context) -> set[str]:
        # Always share: circadian
        # Same family: qualia
```

### Frontend Circadian Pattern

```typescript
// useCircadian hook with manual override for demos
const { phase, modifier, setOverride } = useCircadian();

// Apply circadian to pattern hue
const adjustedHue = applyCircadianToHue(baseHue, modifier);
```

**Files**: `agents/emergence/`, `protocols/agentese/contexts/world_emergence.py`, `web/src/pages/EmergenceDemo.tsx`

**Tests**: 113 (polynomial: 45, operad: 43, sheaf: 25)

---

## Compliance Checklist

Use this checklist to verify a Crown Jewel implements the full vertical slice:

| Layer | Check | Pass Criteria |
|-------|-------|---------------|
| **1. Sheaf** | Local views compose | `coherence_test` passes |
| **2. PolyAgent** | State machine exists | Imports from `agents/poly/` |
| **3. Operad** | Grammar registered | `OperadRegistry.has(NAME_OPERAD)` |
| **4. Service** | Module structure | `services/<name>/` with persistence |
| **5. Node** | AGENTESE registered | `@node` decorator present |
| **5b. Contracts** | BE/FE types sync'd | `contracts={}` on `@node` (Phase 7) |
| **6. Protocol** | Gateway discovery | Path in `/agentese/discover` |
| **7. Projection** | Multi-target render | CLI + Web + JSON all work |
| **API** | Gateway exposed | `POST /agentese/{path}` returns 200 |

---

## The Three Modes of SpecGraph

SpecGraph operates in three modes. **Choose the mode that matches your intent.**

### Mode 1: Advisory (Default)

> *"Tell me what's missing, but don't block me."*

| Aspect | Behavior |
|--------|----------|
| **When to use** | Exploratory work, creative sessions, prototyping |
| **Gaps** | Reported as information |
| **CI** | Never blocks |
| **Entropy** | Full Accursed Share preserved |

```bash
# Advisory mode (default)
uv run python -c "
from protocols.agentese.specgraph import full_audit, print_audit_report
from pathlib import Path
_, audit = full_audit(Path('spec/'), Path('impl/claude/'))
print(print_audit_report(audit))
# Gaps shown, never blocking
"
```

**Use this when**: You're exploring, prototyping, or in a creative session. You want to see where you stand without being stopped.

### Mode 2: Gatekeeping (Opt-In)

> *"Block me if critical components are missing."*

| Aspect | Behavior |
|--------|----------|
| **When to use** | Pre-release, Crown Jewel stabilization, production prep |
| **Gaps** | CRITICAL/IMPORTANT block, MINOR warns |
| **CI** | Fails on CRITICAL gaps |
| **Entropy** | Narrowed (you've chosen rigor) |

```bash
# Gatekeeping mode via CI
uv run pytest protocols/agentese/specgraph/_tests/test_ci_gate.py -v

# Or explicit check
uv run python -c "
from protocols.agentese.specgraph import full_audit
from pathlib import Path
_, audit = full_audit(Path('spec/'), Path('impl/claude/'))
if audit.critical_gaps:
    raise SystemExit(f'BLOCKED: {len(audit.critical_gaps)} critical gaps')
"
```

**Use this when**: You're preparing a Crown Jewel for release, or you want the discipline of enforced alignment.

**Opt-in via frontmatter**:
```yaml
# In your plan file
specgraph_mode: gatekeeping
```

### Mode 3: Aspirational

> *"Track gaps as TODOs for the roadmap."*

| Aspect | Behavior |
|--------|----------|
| **When to use** | Quarterly planning, tech debt tracking, evolution |
| **Gaps** | Become tracked items in Forest Protocol |
| **CI** | Never blocks |
| **Entropy** | Preserved; progress tracked over time |

```bash
# Aspirational mode creates tracking
uv run python -c "
from protocols.agentese.specgraph import full_audit
from pathlib import Path
_, audit = full_audit(Path('spec/'), Path('impl/claude/'))
for gap in audit.gaps:
    print(f'TODO: {gap.spec_path}.{gap.component.value} - {gap.message}')
"
```

**Use this when**: You're planning the next quarter, tracking technical debt, or documenting aspirations for a system that isn't complete yet.

---

## Choosing Your Mode

| Situation | Recommended Mode | Rationale |
|-----------|------------------|-----------|
| New feature exploration | Advisory | Don't block creativity |
| Creative session / jamming | Advisory | Accursed Share preserved |
| Crown Jewel pre-release | Gatekeeping | Ensure full vertical slice |
| Quarterly planning | Aspirational | Track progress over time |
| Refactoring existing code | Advisory → Gatekeeping | Start loose, tighten when stable |
| Documenting discovered patterns | Reflect → Advisory | Impl teaches spec |

### Grace Periods

New Crown Jewels get **30 days of Advisory mode** by default. After stabilization:
- Switch to Gatekeeping for release
- Or stay Advisory if still evolving

Control via plan frontmatter:
```yaml
specgraph_mode: advisory  # or: gatekeeping, aspirational
specgraph_grace_until: 2025-01-15  # Advisory until this date
```

---

## Creating a New Vertical Slice

### Step 0: Choose Your Starting Point

There are **two valid paths** to a vertical slice:

**Path A: Spec-First** (when you know what you want)
- Write spec with YAML frontmatter
- Run audit to see gaps
- Generate stubs
- Fill in implementation

**Path B: Impl-First** (when you're discovering)
- Build exploratory implementation
- Run Reflect to extract spec
- Refine spec with what you learned
- Iterate

Both paths lead to the same destination. Choose based on your current knowledge.

### Step 0a: Spec-First with SpecGraph

If you know what you want, define your vertical slice in a spec file with YAML frontmatter:

```yaml
# spec/world/my-jewel.md
---
domain: world
holon: my-jewel

polynomial:
  positions: [idle, active, processing, complete]
  transition: jewel_transition
  directions: jewel_directions

operad:
  operations:
    process:
      arity: 1
      signature: "Input → Output"
    combine:
      arity: 2
      signature: "A × B → C"
    broadcast:
      arity: -1
      variadic: true
      signature: "Item* → Notification"
  laws:
    idempotence: "process(process(x)) = process(x)"
  extends: AGENT_OPERAD

agentese:
  path: world.my-jewel
  aspects:
    - manifest
    - name: process
      category: generation
      effects: [state_mutation]

service:
  crown_jewel: true
  adapters: [crystals]
  frontend: true

dependencies: [self.memory]
---

# My Jewel

Description of the jewel...
```

Then use SpecGraph to audit and generate stubs:

```python
from protocols.agentese.specgraph import full_audit, generate_stubs, print_audit_report
from pathlib import Path

# Audit what's missing
discovery, audit = full_audit(Path("spec/"), Path("impl/claude/"))
print(print_audit_report(audit))

# Generate stubs for gaps (preview first with dry_run=True)
if audit.has_gaps:
    result = generate_stubs(audit.gaps, Path("impl/claude/"), dry_run=False)
    print(f"Generated: {result.files_generated}")
```

**Why Spec-First?**
- Generated stubs follow the canonical patterns
- Spec documents intent before implementation
- Useful when you know the shape you want

### Step 0b: Impl-First with Reflect

If you're exploring and don't know the final shape, start with implementation:

```python
# 1. Build your exploratory implementation
#    agents/my-jewel/polynomial.py, operad.py, etc.

# 2. Run Reflect to extract spec structure
from protocols.agentese.specgraph import reflect_impl, generate_frontmatter
from pathlib import Path

result = reflect_impl(Path("impl/claude/agents/my-jewel/"))
if result.spec_node:
    yaml = generate_frontmatter(result.spec_node)
    print(yaml)
    # Copy to spec/world/my-jewel.md

# 3. Refine the generated spec with your learnings
# 4. Iterate: impl teaches spec, spec documents intent
```

**Why Impl-First?**
- Preserves creative exploration
- Spec emerges from discovery
- Impl is the authority until you're ready to crystallize

### Step 1: Define Polynomial (Layer 2)

```python
# agents/<jewel>/polynomial.py
from agents.poly.protocol import PolyAgent

class JewelPhase(Enum):
    PHASE_A = auto()
    PHASE_B = auto()

JEWEL_POLYNOMIAL: PolyAgent[JewelPhase, Any, Output] = PolyAgent(
    name="JewelPolynomial",
    positions=frozenset(JewelPhase),
    _directions=jewel_directions,
    _transition=jewel_transition,
)
```

### Step 2: Define Operad (Layer 3)

```python
# agents/<jewel>/operad.py
from agents.operad.core import AGENT_OPERAD, Operad, Operation, OperadRegistry

def create_jewel_operad() -> Operad:
    ops = dict(AGENT_OPERAD.operations)
    ops["custom_op"] = Operation(name="custom_op", arity=2, ...)
    laws = list(AGENT_OPERAD.laws) + [Law(...)]
    return Operad(name="JewelOperad", operations=ops, laws=laws)

JEWEL_OPERAD = create_jewel_operad()
OperadRegistry.register(JEWEL_OPERAD)
```

### Step 3: Create Service Module (Layer 4)

```
services/<jewel>/
├── __init__.py
├── persistence.py   # Data layer
├── node.py          # AGENTESE node
└── _tests/
    └── test_node.py
```

### Step 4: Implement AGENTESE Node (Layer 5)

```python
# services/<jewel>/node.py
from protocols.agentese.contract import Contract, Response

@dataclass
class ManifestResponse:
    name: str
    count: int

@node(
    "<context>.<jewel>",
    dependencies=("<jewel>_persistence",),
    contracts={
        "manifest": Response(ManifestResponse),  # Phase 7: BE/FE type sync
    }
)
class JewelNode(BaseLogosNode):
    @property
    def handle(self) -> str:
        return "<context>.<jewel>"

    async def manifest(self, observer: Observer) -> Renderable:
        ...
```

**Phase 7 Enhancement**: Add `contracts={}` parameter for automatic BE/FE type sync. See `agentese-contract-protocol.md` for full details.

### Step 5: Ensure Gateway Import (Layer 6)

```python
# protocols/agentese/gateway.py - Add to _import_node_modules()
def _import_node_modules() -> None:
    ...
    import services.<jewel>.node  # noqa: F401
```

### Step 6: Create Web Page (Layer 7)

```tsx
// web/src/pages/<Jewel>.tsx
export default function JewelPage() {
  return (
    <PathProjection path="<context>.<jewel>" jewel="<jewel>">
      {(data, ctx) => <JewelVisualization data={data} {...ctx} />}
    </PathProjection>
  );
}
```

---

## Scoring a Jewel with SpecGraph

Use SpecGraph Discovery Mode for automated gap detection:

```python
from protocols.agentese.specgraph import full_audit, print_audit_report
from pathlib import Path

# One-liner audit
discovery, audit = full_audit(Path("spec/"), Path("impl/claude/"))
print(print_audit_report(audit))

# Check alignment score
print(f"Alignment: {audit.alignment_score:.1%}")
print(f"Critical gaps: {len(audit.critical_gaps)}")
```

**Sample Output:**

```
============================================================
SPECGRAPH AUDIT REPORT
============================================================

Total components specified: 18
Aligned: 16 (88.9%)
Missing: 2
Critical gaps: 1

------------------------------------------------------------
GAPS:
------------------------------------------------------------
🔴 [CRITICAL] world.coalition
   Component: polynomial
   polynomial.py missing (spec defines 4 positions)

🟡 [IMPORTANT] world.coalition
   Component: node
   node.py missing (spec defines path world.coalition with 3 aspects)
```

### Manual Compliance Check

For jewels without spec YAML frontmatter, use the manual check:

```python
def score_vertical_slice(jewel_path: str) -> tuple[int, list[str]]:
    """Score a jewel's vertical slice compliance."""
    score = 0
    gaps = []

    # Layer 1: Sheaf (check for coherence methods)
    # Layer 2: PolyAgent (check for polynomial.py)
    # Layer 3: Operad (check OperadRegistry)
    # Layer 4: Service (check services/<name>/)
    # Layer 5: Node (check @node registration)
    # Layer 6: Protocol (check gateway discovery)
    # Layer 7: Projection (check web page exists)
    # API: Check endpoint returns 200

    return score, gaps
```

**Current Jewel Scores** (as of 2025-12-18):

| Jewel | Score | Gaps |
|-------|-------|------|
| Town | 8/8 | None (reference) |
| Brain | 8/8 | None (Phase 4 - BRAIN_POLYNOMIAL + BRAIN_OPERAD) |
| Atelier | 8/8 | None (Phase 4 - WORKSHOP_POLYNOMIAL + ATELIER_OPERAD) |
| Park | 8/8 | None (Phase 4 - DIRECTOR_POLYNOMIAL + DIRECTOR_OPERAD) |
| Flow | 8/8 | None (FLOW_POLYNOMIAL + FLOW_OPERAD + modality variants) |
| Chat | 8/8 | Via composition (uses Flow polynomial/operad) |
| Gestalt | 7/8 | GESTALT_POLYNOMIAL + GESTALT_OPERAD added; sheaf formalization pending |
| **Emergence** | **8/8** | **Full Crown Jewel** (EMERGENCE_POLYNOMIAL + EMERGENCE_OPERAD + EmergenceSheaf + circadian) |
| Design | pending | DESIGN_POLYNOMIAL + 3 sub-operads (Layout, Content, Motion) planned |

---

## CI Gate Integration

The SpecGraph CI gate is **opt-in**, not default. Use it when you want enforced alignment.

### Default Behavior (Advisory)

By default, SpecGraph audits report gaps but **never block**:

```bash
# Advisory mode: shows gaps, doesn't fail
uv run python -c "
from protocols.agentese.specgraph import full_audit, print_audit_report
from pathlib import Path
_, audit = full_audit(Path('spec/'), Path('impl/claude/'))
print(print_audit_report(audit))
"
```

### Opt-In Gatekeeping

When you want enforcement (pre-release, stabilization):

```bash
# Gatekeeping mode via explicit CI test
uv run pytest protocols/agentese/specgraph/_tests/test_ci_gate.py -v
```

**What the CI Gate Checks (in Gatekeeping mode):**

| Severity | Component | CI Action |
|----------|-----------|-----------|
| 🔴 CRITICAL | polynomial, operad | **FAILS** build |
| 🟡 IMPORTANT | node (@node decorator) | **FAILS** build |
| ⚪ MINOR | sheaf | Warns only |

### Pre-commit Hook (Optional, for Gatekeeping)

Only add this if you've chosen Gatekeeping mode:

```bash
# .git/hooks/pre-commit (only for Gatekeeping projects)
#!/bin/bash
uv run pytest protocols/agentese/specgraph/_tests/test_ci_gate.py::TestCIGate::test_no_critical_gaps -v
```

### Escape Hatches

Even in Gatekeeping mode, escape hatches exist for emergencies:

```bash
# Skip CI gate (document why in commit message!)
SPECGRAPH_SKIP_CI_GATE=1 uv run pytest ...
```

**The Philosophy**: Escape hatches exist because creativity sometimes needs to break rules. Use them, but document why. The Accursed Share requires slack.

---

## Related

- `specgraph-workflow.md` — SpecGraph Discovery Mode workflow
- `autopoietic-architecture.md` — Source plan (Phase 3)
- `metaphysical-fullstack.md` — AD-009 stack overview
- `crown-jewel-patterns.md` — Implementation patterns
- `polynomial-agent.md` — Layer 2 details
- `agentese-node-registration.md` — Layer 5 details
- `agentese-contract-protocol.md` — Phase 7 BE/FE type sync

---

## The Enlightened Path: Summary

> *"The scaffold enables the building. When the building stands, the scaffold can be removed."*

### Core Insights

1. **SpecGraph is a tool, not a tyrant**
   - It serves creativity; creativity does not serve it
   - Advisory mode is default; Gatekeeping is opt-in

2. **Bidirectional flow is categorical**
   - `Compile ⊣ Reflect` form an adjunction
   - Neither spec nor impl is sole authority
   - Choose direction based on your knowledge

3. **The Accursed Share must be preserved**
   - Rigid enforcement crushes creative entropy
   - Escape hatches exist for a reason
   - Some gaps are intentional and valuable

4. **Coherence, not conformance**
   - Goal is not "no gaps" but "understood gaps"
   - gaps_in_spec (undocumented impl) is valuable info
   - Grace periods acknowledge evolution

5. **The Three Modes match intent**
   - Advisory: exploration, creativity
   - Gatekeeping: release, stabilization
   - Aspirational: planning, roadmaps

### The Test

Ask yourself: "Is SpecGraph helping me right now, or blocking me?"

- If helping → continue
- If blocking → switch to Advisory mode
- If blocking feels wrong → use the escape hatch, document why

**The system should spark joy. If it doesn't, you're using the wrong mode.**

---

## Changelog

- 2025-12-18: Added Phase 7 Contract Protocol to Layer 5 (BE/FE type sync via `contracts={}`)
- 2025-12-18: **Emergence Crown Jewel** added (EMERGENCE_POLYNOMIAL + EMERGENCE_OPERAD + EmergenceSheaf, 113 tests)
- 2025-12-18: Added Three Modes philosophy (Advisory/Gatekeeping/Aspirational)
- 2025-12-18: Added bidirectional flow emphasis (Compile ⊣ Reflect)
- 2025-12-18: Integrated SpecGraph Discovery Mode (Step 0, CI gate, automated scoring)
- 2025-12-17: Gestalt vertical slice added (GESTALT_POLYNOMIAL + GESTALT_OPERAD, 75 tests)
- 2025-12-17: Initial version from Phase 3 Reference Agent Proof
