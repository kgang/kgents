---
path: plans/agent-town/phase4-cross-synergize
status: active
progress: 100
last_touched: 2025-12-14
touched_by: opus-4.5
blocking: []
enables:
  - agent-town/phase4-civilizational
session_notes: |
  CROSS-SYNERGIZE phase complete. 7 synergies identified, 2 rejected.
  Key leverage: K-gent eigenvectors (wrap, don't extend), NATS bridge (reuse), marimo cells (LOD semantics).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
entropy:
  planned: 0.05
  spent: 0.05
  returned: 0.0
---

# Agent Town Phase 4: CROSS-SYNERGIZE

> *"Discover compositions and entanglements that unlock nonlinear value."*

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Synergies identified | 7 |
| Rejected compositions | 2 |
| Dormant plans checked | 3 |
| Functor reuse opportunities | 3 |
| Law conflicts | 0 |

---

## Identified Synergies

### S1: K-gent Eigenvectors → 7D Town Eigenvectors (WRAP)

**Source**: `agents/k/eigenvectors.py`
**Target**: `agents/town/eigenvectors.py` (to create)

**Composition Strategy**: **WRAP, don't extend**

K-gent eigenvectors are 6D (aesthetic, categorical, gratitude, heterarchy, generativity, joy) with `EigenvectorCoordinate` containing confidence tracking and prompt generation. Town eigenvectors are 7D (warmth, curiosity, trust, creativity, patience, resilience, ambition).

**Interface**:
```python
from agents.k.eigenvectors import EigenvectorCoordinate

@dataclass
class CitizenEigenvectors:
    """7D personality eigenvectors wrapping K-gent pattern."""

    warmth: EigenvectorCoordinate
    curiosity: EigenvectorCoordinate
    trust: EigenvectorCoordinate
    creativity: EigenvectorCoordinate
    patience: EigenvectorCoordinate
    resilience: EigenvectorCoordinate
    ambition: EigenvectorCoordinate

    def drift(self, other: "CitizenEigenvectors") -> float:
        """L2 distance (metric laws preserved)."""
        ...

    def similarity(self, other: "CitizenEigenvectors") -> float:
        """Cosine similarity for coalition formation."""
        ...
```

**Rationale**:
- Reuse `EigenvectorCoordinate` for confidence tracking
- Don't inherit K-gent's axes—personality spaces are different
- `to_prompt_fragment()` pattern valuable for LLM-backed citizens

**Laws Preserved**: L1-Identity, L2-Symmetry, L3-Triangle (metric space laws)

**Leverage**: ~20% code reduction in eigenvector implementation

---

### S2: GraphAgent BFS → Coalition k-hop Detection (REUSE)

**Source**: `agents/d/graph.py:534-568` (BFS traversal pattern)
**Target**: `agents/town/coalition.py`

**Composition Strategy**: **Pattern reuse, not import**

D-gent's `GraphAgent` provides BFS traversal with depth limits. The same pattern applies to k-clique percolation's neighbor finding.

**Interface**:
```python
# Pattern from agents/d/graph.py
visited: Set[str] = {start}
queue: deque[tuple[str, int]] = deque([(start, 0)])

while queue:
    current, depth = queue.popleft()
    if depth >= max_depth:
        continue
    # process neighbors...
```

**Application**:
- Coalition `k-hop` neighborhood detection
- Bridge node identification (nodes in multiple coalitions)
- Reputation propagation (EigenTrust power iteration)

**Rationale**:
- Proven pattern, verified in 770+ D-gent tests
- No import needed—structural pattern suffices
- Same queue/visited/depth structure

**Laws Preserved**: BFS correctness (visits each node once, respects depth)

**Leverage**: Pattern confidence, not code reuse

---

### S3: NATS Bridge → Town Event Streaming (EXTEND)

**Source**: `protocols/streaming/nats_bridge.py`
**Target**: `protocols/streaming/town_bridge.py` (to create)

**Composition Strategy**: **EXTEND existing bridge**

NATSBridge provides:
- Circuit breaker for resilience
- Fallback queues when NATS unavailable
- SSE-compatible event formatting
- Multi-consumer scenarios

**Interface**:
```python
from protocols.streaming.nats_bridge import NATSBridge

class TownEventBridge:
    """Town-specific events via shared NATS infrastructure."""

    def __init__(self, nats_bridge: NATSBridge | None = None):
        self._bridge = nats_bridge or NATSBridge()

    async def publish_town_event(
        self,
        town_id: str,
        event: TownEvent,
    ) -> None:
        """Publish using kgent.town.{town_id}.{event_type} subject."""
        subject = f"kgent.town.{town_id}.{event.action}"
        await self._bridge._js.publish(subject, event.to_json())

    async def subscribe_town(
        self,
        town_id: str,
    ) -> AsyncIterator[TownEvent]:
        """Subscribe to all events for a town."""
        async for payload in self._bridge.subscribe_session(f"town-{town_id}"):
            yield TownEvent.from_dict(payload)
```

**Rationale**:
- Stream name `kgent-events` already configured for `kgent.>`
- Circuit breaker handles NATS failures gracefully
- Fallback queues enable local development without NATS
- SSE endpoint pattern proven in sessions.py

**Laws Preserved**: Circuit breaker state machine laws

**Leverage**: ~80% infrastructure reuse

---

### S4: API Router Pattern → Town API (MOUNT)

**Source**: `protocols/api/app.py`, `protocols/api/sessions.py`
**Target**: `protocols/api/town.py` (to create)

**Composition Strategy**: **MOUNT as sub-router**

Existing API patterns:
- `create_<feature>_router()` factory
- TenantContextMiddleware integration
- MeteringMiddleware for usage tracking
- Pydantic models for request/response

**Interface**:
```python
# protocols/api/app.py additions
from .town import create_town_router

town_router = create_town_router()
if town_router is not None:
    app.include_router(town_router)

# Root endpoint update
"endpoints": {
    ...
    "town": {
        "create": "/v1/town/create",
        "step": "/v1/town/{id}/step",
        "citizens": "/v1/town/{id}/citizens",
        "coalitions": "/v1/town/{id}/coalitions",
        "events": "/v1/town/{id}/events",
        "reputation": "/v1/town/{id}/reputation",
    },
}
```

**Rationale**:
- Router pattern proven across soul, agentese, sessions
- MeteringMiddleware handles per-citizen-turn billing automatically
- TenantContextMiddleware provides multi-tenant isolation
- SSE pattern from sessions.py applies directly

**Laws Preserved**: REST semantics (idempotent GET, mutating POST)

**Leverage**: ~60% boilerplate elimination

---

### S5: TOWN→NPHASE Functor → Citizen Evolution Cycles (LIFT)

**Source**: `agents/town/functor.py`
**Target**: `agents/town/evolving.py` (extend)

**Composition Strategy**: **LIFT citizen operations through functor**

The existing functor maps town operations to NPHASE categories:
- SENSE: branch, trace, id
- ACT: greet, gossip, trade, dispute, celebrate, teach
- REFLECT: solo, mourn

**Application to EvolvingCitizen**:
```python
# Current: EvolvingCitizen has inline SENSE→ACT→REFLECT
async def evolve(self, observation: Observation) -> "EvolvingCitizen":
    sensed = await self.sense(observation)   # NPhase.SENSE
    result = await self.act(sensed)          # NPhase.ACT
    await self.reflect(result)               # NPhase.REFLECT

# Enhanced: Use functor to validate transitions
from agents.town.functor import compose_via_functor

async def evolve_validated(self, observation: Observation) -> "EvolvingCitizen":
    sensed = await self.sense(observation)
    phase_a, phase_b, valid = compose_via_functor("observe", "greet")
    if not valid:
        raise InvalidTransitionError(f"{phase_a} >> {phase_b}")
    ...
```

**Rationale**:
- Functor laws already verified (identity, composition)
- Phase transition validation prevents illegal state sequences
- `classify_town_operation()` provides rich metadata

**Laws Preserved**: Functor laws (identity, composition preservation)

**Leverage**: Formal correctness guarantees for evolution

---

### S6: I-gent LOD Semantics → marimo Dashboard Cells (TRANSLATE)

**Source**: `agents/i/screens/base.py`, citizen LOD 0-5
**Target**: `agents/town/dashboard.py` (marimo)

**Composition Strategy**: **TRANSLATE LOD pattern to reactive cells**

I-gent screens use:
- `KgentsScreen.PASSTHROUGH_KEYS` for navigation
- `ANCHOR` and `ANCHOR_MORPHS_TO` for visual transitions
- LOD 0-5 in citizen.manifest()

**marimo Translation**:
```python
# LOD slider maps to citizen detail level
lod_slider = mo.ui.slider(start=0, stop=5, value=2, step=1)

# Cell reactivity provides "visual anchor" equivalent
@mo.reactive
def citizen_detail(selected_citizen: str, lod: int) -> str:
    citizen = env.citizens.get(selected_citizen)
    return citizen.manifest(lod=lod)

# Navigation via dropdown + cell dependencies (not keybindings)
citizen_selector = mo.ui.dropdown(
    options={c.name: c.id for c in env.citizens.values()}
)
```

**Rationale**:
- LOD 0-5 semantics transfer directly
- marimo's DAG replaces Textual's key passthrough
- Cell dependencies are the "anchors"

**Laws Preserved**: LOD monotonicity (higher LOD ⊇ lower LOD content)

**Leverage**: Conceptual reuse, implementation differs

---

### S7: MeteringMiddleware → Per-Citizen-Turn Billing (INTEGRATE)

**Source**: `protocols/api/metering.py`
**Target**: Town API endpoints

**Composition Strategy**: **INTEGRATE existing middleware**

MeteringMiddleware already handles:
- Token counting
- Per-tenant metering
- OpenMeter integration
- Rate limiting

**Town-specific Metering**:
```python
# In town API step endpoint
@router.post("/v1/town/{id}/step")
async def step_simulation(
    id: UUID,
    request: StepRequest,
    api_key: ApiKeyData = Depends(get_api_key),
) -> StepResponse:
    # MeteringMiddleware adds usage headers automatically
    # Additional town-specific metering:
    await record_usage(
        tenant_id=tenant.id,
        event_type=UsageEventType.TOWN_STEP,
        source="town",
        metadata={
            "citizens": len(env.citizens),
            "llm_citizens": count_llm_citizens(env),
            "cycles": request.cycles,
        },
    )
```

**Rationale**:
- Metering middleware is already in request pipeline
- Just need town-specific event types
- Per-citizen LLM calls tracked separately

**Laws Preserved**: Metering correctness (all billable events recorded)

**Leverage**: ~90% metering infrastructure reuse

---

## Rejected Compositions

### R1: Extend K-gent 6D Eigenvectors to 7D (REJECTED)

**Reason**: Different semantic domains

K-gent eigenvectors (aesthetic, categorical, gratitude, heterarchy, generativity, joy) describe Kent's personality coordinates for prompt generation. Town eigenvectors (warmth, curiosity, trust, creativity, patience, resilience, ambition) describe citizen social dynamics.

**Problem**: Mixing domains would create:
- Confusing inheritance (`KentEigenvectors` → `CitizenEigenvectors`)
- Semantic pollution (what does "aesthetic" mean for a citizen?)
- Law violations (metric space properties must hold for different bases)

**Alternative Chosen**: S1 (wrap `EigenvectorCoordinate` pattern, not KentEigenvectors)

---

### R2: Import D-gent GraphAgent for Town Memory (REJECTED)

**Reason**: Over-coupling

D-gent's `GraphAgent` is a full-featured graph store with persistence, lattice operations (meet, join), and provenance tracking. Town's `GraphMemory` needs only:
- k-hop BFS recall
- Decay/reinforce dynamics
- Simple serialization

**Problem**: Importing GraphAgent would:
- Add unnecessary EdgeKind enum (IS_A, HAS_A, etc.)
- Require async for simple operations
- Create circular dependencies (town → d → shared)

**Alternative Chosen**: S2 (pattern reuse, standalone GraphMemory)

---

## Dormant Plans Check

### plans/reactive-substrate-unification (15%)

**Relevance**: HIGH

marimo dashboard (chunk 4.4) aligns with unified reactive substrate vision. Town can be the first consumer of:
- Reactive DAG for state updates
- Widget protocol for citizen visualization
- Time-downward projection for animation

**Action**: Reference in 4.4 implementation, don't block on full unification.

---

### plans/k-terrarium-llm-agents (superseded)

**Relevance**: ABSORBED

This plan is superseded by Agent Town scope. Town Phase 4 directly implements:
- LLM-backed citizens (3-5 of 25)
- Evolution cycles
- Memory with decay

**Action**: None needed—functionality flows via crown-jewel-next.

---

### plans/agentese-universal-protocol (0%)

**Relevance**: MEDIUM

Town is a natural AGENTESE showcase:
- `world.town.citizens` → handle to citizen collection
- `world.town.{name}.manifest` → LOD projection
- Observer umwelt → different views for economist vs poet

**Action**: Note as future integration point. Not blocking for Phase 4.

---

## Functor Registry Check

### F1: TOWN→NPHASE Functor (EXISTS)

**Location**: `agents/town/functor.py`
**Reuse**: S5 (lift citizen operations, validate transitions)

### F2: NPHASE_OPERAD Operations (EXISTS)

**Location**: `protocols/nphase/operad.py`
**Reuse**: Phase transition validation for evolution cycles

### F3: SOUL_POLYNOMIAL Patterns (PARTIAL)

**Location**: `agents/k/soul.py` (implicit)
**Relevance**: Eigenvector drift similar to personality drift
**Action**: Pattern awareness, no direct import

---

## Implementation-Ready Interfaces

### Interface 1: CitizenEigenvectors (S1)

```python
@dataclass
class CitizenEigenvectors:
    warmth: float = 0.5
    curiosity: float = 0.5
    trust: float = 0.5
    creativity: float = 0.5
    patience: float = 0.5
    resilience: float = 0.5  # NEW
    ambition: float = 0.5    # NEW

    def drift(self, other: "CitizenEigenvectors") -> float: ...
    def similarity(self, other: "CitizenEigenvectors") -> float: ...
    def apply_bounded_drift(self, deltas: dict[str, float], max_drift: float = 0.1) -> "CitizenEigenvectors": ...
```

### Interface 2: TownEventBridge (S3)

```python
class TownEventBridge:
    def __init__(self, nats_bridge: NATSBridge | None = None): ...
    async def publish_town_event(self, town_id: str, event: TownEvent) -> None: ...
    async def subscribe_town(self, town_id: str) -> AsyncIterator[TownEvent]: ...
```

### Interface 3: Town API Router (S4)

```python
def create_town_router() -> APIRouter:
    router = APIRouter(prefix="/v1/town", tags=["town"])

    @router.post("/create")
    @router.post("/{id}/step")
    @router.get("/{id}/citizens")
    @router.get("/{id}/citizen/{name}")
    @router.get("/{id}/coalitions")
    @router.get("/{id}/events")  # SSE
    @router.get("/{id}/reputation")

    return router
```

---

## Exit Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| 5+ cross-synergies identified with rationale | ✓ | S1-S7 (7 synergies) |
| Dormant plans checked (compose or explicit "none") | ✓ | 3 plans checked |
| No conflicting implementations (law violations documented if any) | ✓ | 0 conflicts |
| Rejected paths documented | ✓ | R1-R2 documented |
| Implementation-ready interfaces defined | ✓ | 3 interfaces |
| ledger.CROSS-SYNERGIZE=touched | ✓ | Frontmatter updated |

---

## Process Metrics

| Metric | Value |
|--------|-------|
| Phase | CROSS-SYNERGIZE |
| Synergies identified | 7 |
| Rejected compositions | 2 |
| Dormant plans checked | 3 |
| Law conflicts | 0 |
| Entropy sip | 0.05 |

---

## Continuation

```
⟿[IMPLEMENT]
exit: synergies=7, conflicts=0, dormant_unblocked=1, rejected_paths=2
continuation → IMPLEMENT (Track A: chunk 4.1 first)
```

---

*"Composition is the primitive. Everything else is derived."*
