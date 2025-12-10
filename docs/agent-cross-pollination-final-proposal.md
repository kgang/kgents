# Agent Cross-Pollination: Final Implementation Proposal

*Synthesized from initial analysis + systems/category/economic critique*

**Core Insight**: Move from **Integration-by-Wire** (pairwise factory functions) to **Integration-by-Field** (stigmergic mediums + functor-based message passing).

---

## Part I: The Paradigm Shift

### From Bridges to Mediums

| Old Model (Rejected) | New Model (Adopted) |
|---------------------|---------------------|
| `create_personalized_bard(K, N)` | K writes to Field; N reads from Field |
| `if economics: meter() else: pass` | W-gent intercepts; agent never knows |
| `IntentSketch` as text blob | `Functor[ProblemSpace, KnownDomain]` |
| N×(N-1) pairwise integrations | 3 Mediums + 1 Bus |

### The Three Mediums + One Bus

```
┌─────────────────────────────────────────────────────────────────────┐
│                        THE INTEGRATION ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐        │
│   │  I-gent      │     │  M-gent      │     │  L-gent      │        │
│   │  STIGMERGIC  │     │  HOLOGRAPHIC │     │  SEMANTIC    │        │
│   │  FIELD       │     │  MEMORY      │     │  CATALOG     │        │
│   └──────┬───────┘     └──────┬───────┘     └──────┬───────┘        │
│          │                    │                    │                 │
│          └────────────────────┼────────────────────┘                 │
│                               │                                      │
│                    ┌──────────▼──────────┐                          │
│                    │      W-gent         │                          │
│                    │   MIDDLEWARE BUS    │                          │
│                    │  (Functor Dispatch) │                          │
│                    └──────────┬──────────┘                          │
│                               │                                      │
│          ┌────────────────────┼────────────────────┐                │
│          │                    │                    │                 │
│    ┌─────▼─────┐       ┌─────▼─────┐       ┌─────▼─────┐           │
│    │  Agents   │       │  Agents   │       │  Agents   │           │
│    │  (K,N,H)  │       │  (E,F,R)  │       │  (B,J,T)  │           │
│    │  PERSONA  │       │  CREATION │       │  CONTROL  │           │
│    └───────────┘       └───────────┘       └───────────┘           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Agents don't call each other. They:**
1. **Emit signals** to the Stigmergic Field (I-gent)
2. **Store/retrieve** via Holographic Memory (M-gent)
3. **Advertise capabilities** to Semantic Catalog (L-gent)
4. **Receive intercepted messages** via Middleware Bus (W-gent)

---

## Part II: The Four Infrastructure Components

### 1. The Middleware Bus (W-gent × C-gent)

**Purpose**: Functor-based message passing. Agents never call each other directly.

**Spec Location**: `spec/protocols/middleware-bus.md`

```python
# The Bus intercepts all agent invocations
@dataclass
class BusMessage(Generic[A, B]):
    """Every agent call becomes a message on the bus."""
    source: AgentId
    target: AgentId
    payload: A
    functor: Functor[A, B] | None  # C-gent structural mapping

class MiddlewareBus:
    """W-gent as the nervous system."""

    interceptors: list[Interceptor]  # B-gent, J-gent, O-gent register here

    async def dispatch(self, msg: BusMessage[A, B]) -> B:
        # 1. Run through interceptors (metering, safety, telemetry)
        for interceptor in self.interceptors:
            msg = await interceptor.before(msg)
            if msg.blocked:
                return interceptor.fallback(msg)

        # 2. Apply functor if present (C-gent structural transform)
        if msg.functor:
            msg.payload = msg.functor.map(msg.payload)

        # 3. Dispatch to target
        result = await self.registry.invoke(msg.target, msg.payload)

        # 4. Post-interceptors
        for interceptor in reversed(self.interceptors):
            result = await interceptor.after(msg, result)

        return result
```

**Key Insight**: The "Bypass Pattern" is eliminated. B-gent metering is an *interceptor*, not a conditional branch. Agents are blissfully unaware of economics.

**Interceptors**:
| Interceptor | Agent | Purpose |
|-------------|-------|---------|
| `MeteringInterceptor` | B-gent | Token accounting |
| `SafetyInterceptor` | J-gent | Entropy/reality check |
| `TelemetryInterceptor` | O-gent | Observation emission |
| `PersonaInterceptor` | K-gent | Prior injection |

---

### 2. The Stigmergic Field (I-gent)

**Purpose**: Indirect coordination via environmental modification. Agents leave "pheromones"; others sense them.

**Spec Location**: `spec/i-gents/stigmergic-field.md`

```python
@dataclass
class Pheromone:
    """A signal left in the field."""
    emitter: AgentId
    kind: PheromoneKind  # METAPHOR, INTENT, WARNING, OPPORTUNITY
    payload: Any
    intensity: float  # Decays over time
    position: FieldCoordinate  # Where in problem space

class StigmergicField:
    """The shared environment all agents inhabit."""

    pheromones: SpatialIndex[Pheromone]

    def deposit(self, p: Pheromone) -> None:
        """Agent leaves a signal."""
        self.pheromones.insert(p)

    def sense(self, position: FieldCoordinate, radius: float) -> list[Pheromone]:
        """Agent senses nearby signals."""
        return self.pheromones.query_radius(position, radius)

    def decay(self, dt: float) -> None:
        """Pheromones fade over time (forgetting)."""
        for p in self.pheromones:
            p.intensity *= exp(-self.decay_rate * dt)
            if p.intensity < self.threshold:
                self.pheromones.remove(p)
```

**Integration Example: Psi × F (Decoupled)**

```python
# Psi-gent: Leaves metaphor pheromone, doesn't know F exists
async def solve_and_signal(engine: MetaphorEngine, problem: Problem) -> None:
    solution = await engine.solve(problem)
    field.deposit(Pheromone(
        emitter="psi",
        kind=PheromoneKind.METAPHOR,
        payload=solution.functor,  # C-gent Functor, not text!
        intensity=solution.confidence,
        position=problem.embedding,
    ))

# F-gent: Senses metaphor pheromones, doesn't know Psi exists
async def forge_with_environment(intent: Intent) -> Artifact:
    nearby = field.sense(intent.embedding, radius=0.5)
    metaphors = [p for p in nearby if p.kind == PheromoneKind.METAPHOR]

    if metaphors:
        # Apply strongest metaphor's functor
        best = max(metaphors, key=lambda p: p.intensity)
        transformed_intent = best.payload.map(intent)  # Functor application
        return await forge(transformed_intent)
    else:
        return await forge(intent)  # No metaphor available, proceed normally
```

**Result**: Psi and F are completely decoupled. They coordinate through the *field*, not through each other.

---

### 3. The Integration Tongue (G-gent DSL)

**Purpose**: Declarative integration specification. No manual factory code.

**Spec Location**: `spec/g-gents/integration-tongue.md`

```yaml
# integrations/k_priors.tongue
# K-gent personality as decision-making priors, not cosmetic voice

tongue: integration/1.0

integration K_into_B:
  """Personality modifies economic parameters."""
  type: PriorInjection
  source: K.PersonaState
  target: B.UtilityFunction
  mapping:
    risk_tolerance:
      Low:  { discount_rate: 0.95, loss_aversion: 2.5 }
      High: { discount_rate: 0.80, loss_aversion: 1.0 }
    time_preference:
      Patient:   { horizon: 1000 }
      Impatient: { horizon: 10 }
  mechanism: interceptor  # W-gent applies this

integration K_into_J:
  """Personality modifies safety thresholds."""
  type: PriorInjection
  source: K.PersonaState
  target: J.EntropyBudget
  mapping:
    creativity:
      Conservative: { max_entropy: 0.3, reality_threshold: 0.9 }
      Exploratory:  { max_entropy: 0.8, reality_threshold: 0.5 }
  mechanism: interceptor

integration Psi_via_Field:
  """Psi emits functors to stigmergic field."""
  type: Stigmergic
  emitter: Psi.MetaphorEngine
  pheromone:
    kind: METAPHOR
    payload: Functor[ProblemSpace, KnownDomain]
    decay_rate: 0.1
  consumers: [F, R, E]  # Any of these may sense

integration M_consolidation:
  """Memory consolidation during system idle."""
  type: Temporal
  trigger: SystemIdle > 30s
  source: M.ColdMemories
  pipeline:
    - E.retrieve(source)
    - R.compress(retrieved)
    - M.store(compressed, tier=WARM)
  budget: B.maintenance_reserve
```

**Compilation**: J-gent compiles `.tongue` files into:
1. **Interceptor registrations** for W-gent
2. **Pheromone schemas** for I-gent
3. **Type contracts** for C-gent verification

---

### 4. The Semantic Catalog (L-gent Registry)

**Purpose**: Capability advertisement and discovery. Agents don't hardcode dependencies.

**Spec Location**: `spec/l-gents/capability-registry.md`

```python
@dataclass
class Capability:
    """What an agent can do."""
    agent: AgentId
    name: str
    input_type: Type
    output_type: Type
    functor: Functor | None  # C-gent structural signature
    cost: TokenEstimate  # B-gent pricing

class CapabilityRegistry:
    """L-gent as Yellow Pages."""

    def advertise(self, cap: Capability) -> None:
        """Agent registers what it can do."""
        self.index.add(cap)

    def discover(self,
                 need: Type,
                 budget: TokenBudget | None = None) -> list[Capability]:
        """Find agents that can satisfy a need."""
        candidates = self.index.query_by_type(need)
        if budget:
            candidates = [c for c in candidates if c.cost <= budget]
        return sorted(candidates, key=lambda c: c.cost)

    def compose(self, caps: list[Capability]) -> Capability | None:
        """C-gent: Can these capabilities compose?"""
        # Verify functor composition laws
        for i in range(len(caps) - 1):
            if not caps[i].output_type.compatible(caps[i+1].input_type):
                return None
        return ComposedCapability(caps)
```

---

## Part III: Agent-Specific Enhancements

### K-gent: From Voice to Prior

**Old Model**: K-gent adjusts N-gent's narrative voice (cosmetic).
**New Model**: K-gent injects Bayesian priors into decision-making agents.

**Spec Location**: `spec/k-gents/priors.md`

```python
@dataclass
class PersonaPriors:
    """Personality as decision-making biases."""

    # Economic priors (B-gent)
    discount_rate: float  # Time preference
    loss_aversion: float  # Prospect theory
    risk_tolerance: float  # Variance acceptance

    # Safety priors (J-gent)
    entropy_tolerance: float  # Creativity vs stability
    reality_threshold: float  # Hallucination rejection

    # Narrative priors (N-gent) - still present, but not primary
    genre_preference: NarrativeGenre
    formality: float

class PersonaInterceptor(Interceptor):
    """K-gent as W-gent interceptor."""

    def __init__(self, priors: PersonaPriors):
        self.priors = priors

    async def before(self, msg: BusMessage) -> BusMessage:
        if msg.target == "B":
            # Inject economic priors
            msg.payload = self.priors.bias_utility(msg.payload)
        elif msg.target == "J":
            # Inject safety priors
            msg.payload = self.priors.bias_entropy(msg.payload)
        return msg
```

**Key Insight**: Personality is structural, not cosmetic. A "risk-averse" persona doesn't just *talk* carefully—it *decides* carefully.

---

### Psi-gent: From Sketch to Functor

**Old Model**: `IntentSketch` as text blob ("this is like plumbing").
**New Model**: `Functor[ProblemSpace, KnownDomain]` as mathematical isomorphism.

**Spec Location**: `spec/psi-gents/functors.md`

```python
@dataclass
class MetaphorFunctor(Generic[P, K]):
    """A structural mapping from Problem space to Known domain."""

    source_category: Category[P]  # The problem we don't understand
    target_category: Category[K]  # The domain we understand

    object_map: Callable[[P.Object], K.Object]
    morphism_map: Callable[[P.Morphism], K.Morphism]

    # Functor laws (verified by C-gent)
    # F(id_A) = id_{F(A)}
    # F(g ∘ f) = F(g) ∘ F(f)

    def apply(self, problem: P.Object) -> K.Object:
        """Map problem to known domain."""
        return self.object_map(problem)

    def transfer_solution(self, solution: K.Morphism) -> P.Morphism:
        """Pull solution back to problem domain."""
        # This requires the functor to have a right adjoint
        return self.right_adjoint.morphism_map(solution)

class MetaphorEngine:
    """Psi-gent: Functor discovery."""

    async def find_functor(self, problem: Problem) -> MetaphorFunctor | None:
        """Find a functor from problem space to a known domain."""
        # 1. Embed problem in semantic space
        embedding = await self.embed(problem)

        # 2. Query catalog for structurally similar domains
        candidates = self.catalog.query_by_structure(problem.signature)

        # 3. Attempt to construct functor for each
        for domain in candidates:
            functor = self.try_construct_functor(problem, domain)
            if functor and self.verify_laws(functor):
                return functor

        return None
```

**Example**:
```
Problem: "Optimize database query ordering"
Functor Found: DatabaseQuery → TopologicalSort
  - Tables → Nodes
  - Foreign Keys → Edges
  - Query Order → Topological Order
Solution Transfer: Apply Kahn's algorithm, map back to query plan
```

---

### B-gent: Tax the Bypass (Coase Theorem)

**Old Model**: `if economics: meter() else: pass`
**New Model**: No bypass. All paths have cost. Stability has price.

**Spec Location**: `spec/b-gents/coase.md`

```python
class EconomicInterceptor(Interceptor):
    """B-gent: Everything has a price."""

    async def before(self, msg: BusMessage) -> BusMessage:
        # Price the operation
        cost = self.oracle.estimate(msg)

        # Check budget
        if not self.treasury.can_afford(msg.source, cost):
            # Inject artificial scarcity: latency or entropy
            if self.policy == "latency":
                await asyncio.sleep(self.scarcity_delay)
            elif self.policy == "entropy":
                msg.payload = self.inject_noise(msg.payload, self.entropy_amount)

            # Log the "loan" for future accounting
            self.ledger.record_deficit(msg.source, cost)
        else:
            self.treasury.debit(msg.source, cost)

        return msg
```

**Key Insight**: The "bypass" isn't free—it costs *stability*. Agents that don't pay for metering get noisier results. This aligns incentives with system health.

---

## Part IV: Novel Recursive Capabilities

### The Mirror Stage (Psi × H × O)

**Purpose**: Self-healing via identity reconstruction, not rule-based repair.

**Spec Location**: `spec/protocols/mirror-stage.md`

```python
class MirrorStage:
    """Lacanian self-healing: System recognizes itself in telemetry."""

    def __init__(self, observer: OGent, psi: PsiGent, hegel: HGent):
        self.observer = observer
        self.psi = psi
        self.hegel = hegel

    async def diagnose(self) -> SystemState:
        """O-gent: What is the system's current state?"""
        telemetry = await self.observer.collect()
        return self.observer.interpret(telemetry)

    async def interpret(self, state: SystemState) -> Interpretation:
        """Psi-gent: What does this state MEAN?"""
        if state.is_fragmented:
            # Lacanian: "Corps morcelé" - body in pieces
            return Interpretation(
                condition="fragmentation",
                metaphor=self.psi.corpus.get("body_without_organs"),
                severity=state.fragmentation_score,
            )
        elif state.is_conflicted:
            # Lacanian: Internal conflict
            return Interpretation(
                condition="conflict",
                metaphor=self.psi.corpus.get("mirror_misrecognition"),
                severity=state.conflict_score,
            )
        # ... other interpretations

    async def synthesize(self, interpretation: Interpretation) -> EgoIdeal:
        """H-gent (Hegel): What SHOULD the system become?"""
        # Thesis: Current state
        # Antithesis: The interpretation's implied opposite
        # Synthesis: The Ego Ideal (target state)
        return await self.hegel.dialectic(
            thesis=interpretation.current,
            antithesis=interpretation.implied_opposite,
        )

    async def heal(self) -> HealingPlan:
        """Full mirror stage: Recognize → Interpret → Synthesize → Plan."""
        state = await self.diagnose()
        interpretation = await self.interpret(state)
        ideal = await self.synthesize(interpretation)

        # Generate healing actions to move from state to ideal
        return self.plan_transition(state, ideal)
```

**Example**:
```
Telemetry: Error rate spike in E-gent, memory fragmentation in M-gent
Interpretation: "Corps morcelé" - evolution and memory are disconnected
Synthesis: "Unified body" - E-gent mutations should consolidate in M-gent
Healing: Create M×E integration (mutations as memories)
```

---

### The Hypnagogic Refinery (R × M × E)

**Purpose**: Automatic codebase optimization during "sleep" (idle time).

**Spec Location**: `spec/protocols/hypnagogic-refinery.md`

```python
class HypnagogicRefinery:
    """Optimization through dreaming: Compress cold memories."""

    def __init__(self, memory: MGent, retriever: EGent, refinery: RGent):
        self.memory = memory
        self.retriever = retriever
        self.refinery = refinery

    async def dream_cycle(self) -> RefineryReport:
        """Run during system idle (Night Watch)."""

        # 1. M-gent: Identify cold memories (rarely accessed code paths)
        cold = await self.memory.query_by_temperature(max_temp=0.2)

        # 2. E-gent: Retrieve the actual code
        code_blocks = []
        for memory in cold:
            if memory.kind == MemoryKind.CODE:
                code_blocks.append(await self.retriever.retrieve(memory.ref))

        # 3. R-gent: Compress/optimize using DSPy
        optimized = []
        for block in code_blocks:
            result = await self.refinery.optimize(
                block,
                objective="compression",  # Make smaller
                constraints=["preserve_semantics", "maintain_tests"],
            )
            if result.improvement > 0.1:  # >10% improvement
                optimized.append(result)

        # 4. Apply optimizations (with rollback capability)
        applied = []
        for opt in optimized:
            if await self.verify_safe(opt):
                await self.apply(opt)
                applied.append(opt)

        return RefineryReport(
            examined=len(cold),
            optimized=len(applied),
            bytes_saved=sum(o.size_reduction for o in applied),
        )
```

**Result**: The codebase *improves itself* over time. Cold, bloated code paths get compressed. The system becomes more efficient through "dreaming."

---

## Part V: Revised Implementation Roadmap

### Phase 0: Infrastructure (The Four Components)

| Component | Owner | Deliverable | Tests |
|-----------|-------|-------------|-------|
| Middleware Bus | W-gent × C-gent | `protocols/bus/` | ~60 |
| Stigmergic Field | I-gent | `agents/i/field.py` | ~40 |
| Integration Tongue | G-gent | `spec/g-gents/integration-tongue.md` + compiler | ~50 |
| Capability Registry | L-gent | `agents/l/registry.py` | ~30 |

**Milestone**: Any agent can emit to field, dispatch via bus, advertise capability.

### Phase 1: Core Interceptors

| Interceptor | Agent | Purpose |
|-------------|-------|---------|
| `EconomicInterceptor` | B-gent | Universal metering (no bypass) |
| `SafetyInterceptor` | J-gent | Entropy/reality gating |
| `TelemetryInterceptor` | O-gent | Observation emission |
| `PersonaInterceptor` | K-gent | Prior injection |

**Milestone**: All agent invocations go through bus with interceptors.

### Phase 2: Stigmergic Integrations

| Integration | Emitter | Pheromone | Consumers |
|-------------|---------|-----------|-----------|
| Metaphor Field | Psi | `Functor[P,K]` | F, R, E |
| Intent Field | F | `ArtifactIntent` | G, P |
| Warning Field | J | `SafetyAlert` | All |
| Opportunity Field | B | `EconomicSignal` | E, R |

**Milestone**: Psi×F works without direct coupling.

### Phase 3: Declarative Integrations

Write `.tongue` files for:
- K priors (K→B, K→J, K→N)
- Memory consolidation (M×E×R)
- Test archaeology (T×M)

**Milestone**: New integrations require only `.tongue` file, not code.

### Phase 4: Recursive Capabilities

| Capability | Components | Purpose |
|------------|------------|---------|
| Mirror Stage | O×Psi×H | Self-healing via identity |
| Hypnagogic Refinery | M×E×R | Sleep optimization |
| Dream Narrative | N×M×Psi | Story-based consolidation |

**Milestone**: System heals and optimizes itself.

### Phase 5: Ecosystem Verification

- C-gent verifies all functor compositions
- Remove any remaining direct agent calls
- Audit: No agent imports another agent

**Milestone**: True field-based ecosystem.

---

## Part VI: Open Questions (Revised)

### Resolved by This Proposal

| Original Question | Resolution |
|-------------------|------------|
| How to prevent integration debt? | Integration Tongue: declarative, verifiable |
| Can integrations be hot-swapped? | Field-based: just change pheromone emission |
| What's the observability story? | TelemetryInterceptor on bus |
| How do AI agents discover integrations? | Capability Registry |

### New Questions

| Question | Stakes |
|----------|--------|
| **How do we handle pheromone conflicts?** | Multiple agents emit contradictory signals |
| **What's the functor discovery complexity?** | Psi-gent may not find isomorphism |
| **How do interceptors compose?** | Order-dependent side effects? |
| **What's the field's spatial structure?** | Embedding space? Problem taxonomy? |
| **Can the Mirror Stage hallucinate?** | Self-diagnosis may be wrong |

---

## Part VII: Spec Generation Targets

This proposal should generate the following specs in `spec/`:

```
spec/
├── protocols/
│   ├── middleware-bus.md        # W-gent bus architecture
│   ├── stigmergic-field.md      # I-gent field protocol
│   ├── mirror-stage.md          # Self-healing protocol
│   └── hypnagogic-refinery.md   # Sleep optimization protocol
├── g-gents/
│   └── integration-tongue.md    # DSL for integrations
├── k-gents/
│   └── priors.md                # Personality as Bayesian priors
├── psi-gents/
│   └── functors.md              # Metaphor as category functor
├── b-gents/
│   └── coase.md                 # Economic interceptor (no bypass)
└── l-gents/
    └── capability-registry.md   # Capability advertisement
```

---

## Appendix: The Paradigm in One Diagram

```
                    ┌─────────────────────────────────────┐
                    │         STIGMERGIC FIELD            │
                    │    (Pheromones: Metaphor, Intent,   │
                    │     Warning, Opportunity)           │
                    └──────────────┬──────────────────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
            ▼                      ▼                      ▼
    ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
    │   EMITTERS    │      │   MIDDLEWARE  │      │   CONSUMERS   │
    │               │      │      BUS      │      │               │
    │  Psi (Functor)│ ───► │               │ ───► │  F (Forge)    │
    │  F (Intent)   │      │  Interceptors │      │  R (Refine)   │
    │  J (Warning)  │      │  ┌─────────┐  │      │  E (Evolve)   │
    │  B (Opp)      │      │  │ B-meter │  │      │  N (Narrate)  │
    └───────────────┘      │  │ J-safety│  │      └───────────────┘
                           │  │ K-prior │  │
                           │  │ O-telem │  │
                           │  └─────────┘  │
                           └───────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │       CAPABILITY REGISTRY           │
                    │   (L-gent: Advertise, Discover,     │
                    │    Compose)                         │
                    └─────────────────────────────────────┘
```

**Agents don't know each other. They know:**
1. How to emit signals
2. How to sense signals
3. How to advertise capabilities
4. That messages go through the bus

**Everything else emerges.**
