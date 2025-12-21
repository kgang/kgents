# Cross-Pollination Protocol

**Status**: Specification v1.0
**Purpose**: Define how agents coordinate without direct coupling

---

## The Paradigm

Agents don't call each other. They coordinate through **mediums**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CROSS-POLLINATION ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐        │
│   │  W-gent      │     │  M-gent      │     │  L-gent      │        │
│   │  STIGMERGIC  │     │  HOLOGRAPHIC │     │  SEMANTIC    │        │
│   │  FIELD       │     │  MEMORY      │     │  CATALOG     │        │
│   └──────┬───────┘     └──────┬───────┘     └──────┬───────┘        │
│          │                    │                    │                 │
│          └────────────────────┼────────────────────┘                 │
│                               │                                      │
│                    ┌──────────▼──────────┐                          │
│                    │      W-gent         │                          │
│                    │   MIDDLEWARE BUS    │                          │
│                    │   (Interceptors)    │                          │
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

**Agents know:**
1. How to emit signals (to Stigmergic Field)
2. How to sense signals (from Stigmergic Field)
3. How to advertise capabilities (to L-gent Catalog)
4. That messages go through the bus (W-gent Middleware)

**Everything else emerges.**

---

## The Three Mediums

### 1. Stigmergic Field (W-gent)

See: [../w-gents/stigmergy.md](../w-gents/stigmergy.md)

Agents coordinate via environmental modification. Pheromones types:

| Type | Emitter | Consumer | Purpose |
|------|---------|----------|---------|
| `METAPHOR` | Psi | F, R, E | Structural mapping as Functor |
| `INTENT` | F | G, P | Artifact intent announcement |
| `WARNING` | J | All | Safety alerts |
| `OPPORTUNITY` | B | E, R | Economic signals |

### 2. Holographic Memory (M-gent)

See: [../d-gents/noosphere.md](../d-gents/noosphere.md)

Agents store/retrieve via shared memory without coupling:
- Hot/warm/cold tiers
- Context cartography
- No direct inter-agent state sharing

### 3. Semantic Catalog (L-gent)

See: [../l-gents/catalog.md](../l-gents/catalog.md)

Agents advertise capabilities; others discover without hardcoding:

```python
# Advertisement
await l_gent.register(
    entity=my_agent,
    capabilities=["summarize", "translate"],
    input_type="str",
    output_type="Summary"
)

# Discovery
candidates = await l_gent.discover(
    need="str → Summary",
    budget=my_budget
)
```

---

## The Middleware Bus

W-gent as nervous system. All agent invocations pass through the bus.

See: [../w-gents/interceptors.md](../w-gents/interceptors.md)

### Interceptor Chain

```
Message → Safety(50) → Metering(100) → Telemetry(200) → Persona(300) → Target
                                                                         ↓
Result ← Safety ← Metering ← Telemetry ← Persona ← ────────────────────┘
```

| Interceptor | Agent | Priority | Purpose |
|-------------|-------|----------|---------|
| SafetyInterceptor | J-gent | 50 | Entropy/reality gating |
| MeteringInterceptor | B-gent | 100 | Token accounting |
| TelemetryInterceptor | O-gent | 200 | Observation emission |
| PersonaInterceptor | K-gent | 300 | Prior injection |

### The "No Bypass" Principle

From B-gent economics: there is no free path. All operations have cost.

```python
# Old (rejected)
if economics_enabled:
    meter()
else:
    pass  # Free bypass!

# New (adopted)
# Metering is an interceptor. Agents never see it.
# Even "bypassed" operations incur stability cost.
```

---

## Integration Patterns

### Pattern 1: Psi × F (Metaphor-Informed Forging)

No direct coupling. Psi emits; F senses.

```python
# Psi-gent: Emits metaphor functor to field
field.deposit(Pheromone(
    emitter="psi",
    kind=PheromoneKind.METAPHOR,
    payload=MetaphorFunctor(
        source=problem_category,
        target=known_domain,
        object_map=mapping
    ),
    position=problem.embedding
))

# F-gent: Senses metaphors, applies if available
nearby = field.sense(intent.embedding, radius=0.5)
metaphors = [p for p in nearby if p.kind == PheromoneKind.METAPHOR]
if metaphors:
    best = max(metaphors, key=lambda p: p.intensity)
    transformed_intent = best.payload.map(intent)
```

### Pattern 2: K → B, K → J (Personality as Priors)

K-gent doesn't modify output voice (cosmetic). It injects Bayesian priors into decision-making agents.

```python
@dataclass
class PersonaPriors:
    """Personality as decision-making biases."""

    # Economic priors (B-gent)
    discount_rate: float      # Time preference
    loss_aversion: float      # Prospect theory
    risk_tolerance: float     # Variance acceptance

    # Safety priors (J-gent)
    entropy_tolerance: float  # Creativity vs stability
    reality_threshold: float  # Hallucination rejection
```

PersonaInterceptor applies these before messages reach B-gent or J-gent.

**Key Insight**: A "risk-averse" persona doesn't just *talk* carefully—it *decides* carefully.

### Pattern 3: O × Psi × H (Mirror Stage)

Self-healing via identity reconstruction.

```python
# 1. O-gent: What is the system's state?
telemetry = observer.collect()
state = observer.interpret(telemetry)

# 2. Psi-gent: What does this state MEAN?
if state.is_fragmented:
    interpretation = "corps morcelé"  # Body in pieces

# 3. H-gent: What SHOULD the system become?
ideal = hegel.dialectic(
    thesis=interpretation.current,
    antithesis=interpretation.implied_opposite
)

# 4. Plan transition from state to ideal
```

---

## Declarative Integration (G-gent DSL)

Future: Define integrations in `.tongue` files, not code.

```yaml
# integrations/k_priors.tongue
tongue: integration/1.0

integration K_into_B:
  type: PriorInjection
  source: K.PersonaState
  target: B.UtilityFunction
  mapping:
    risk_tolerance:
      Low:  { discount_rate: 0.95, loss_aversion: 2.5 }
      High: { discount_rate: 0.80, loss_aversion: 1.0 }
  mechanism: interceptor
```

G-gent compiles `.tongue` → interceptor registrations + pheromone schemas.

---

## Import Audit Policy

Cross-agent imports create coupling. Policy:

| Import Pattern | Status | Rationale |
|----------------|--------|-----------|
| Agent → D-gent | Acceptable | D-gent is foundational (memory) |
| Agent → L-gent | Acceptable | L-gent is foundational (catalog) |
| Agent → C-gent | Acceptable | C-gent is foundational (composition) |
| Agent → shared/ | Acceptable | Shared types/utilities |
| Agent → `*_integration.py` | Acceptable | Explicit integration boundary |
| Agent → Agent | **Violation** | Use field/bus instead |

Violations should be refactored to integration files or field-based coordination.

---

## Ecosystem Verification

C-gent verifies:
1. **Functor laws** hold for all lifted agents
2. **Monad laws** hold for Effect types
3. **No direct imports** between agent genera (audit)

See: [../agents/composition.md](../agents/composition.md)

---

## Anti-Patterns

- **Tight coupling**: Agent A imports Agent B directly
- **Orchestrator bottleneck**: One agent coordinates all others
- **Hidden state**: Agents hold state the field can't observe
- **Bypass economics**: Operations without metering
- **Cosmetic personality**: K-gent only changes output voice, not decisions

---

## See Also

- [../w-gents/stigmergy.md](../w-gents/stigmergy.md) - Pheromone field
- [../w-gents/interceptors.md](../w-gents/interceptors.md) - Middleware interceptors
- [../l-gents/catalog.md](../l-gents/catalog.md) - Capability registry
- [../k-gent/persona.md](../k-gent/persona.md) - Persona model
- [../agents/functors.md](../agents/functors.md) - Functor theory

---

*"The river doesn't know the fish; the fish doesn't know the river. Together they are the ecosystem."*
