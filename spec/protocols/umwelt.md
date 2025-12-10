# The Umwelt Protocol: Agent-Specific World Projection

**Each agent inhabits its own world; there is no view from nowhere.**

**Status:** Specification v1.0
**Date:** 2025-12-09
**Related:** `membrane.md`, `d-gents/lenses.md`, `f-gents/contracts.md`, `g-gents/tongue.md`

---

## Prologue: The Fallacy of the Universal View

The enterprise architecture approach to "world access" commits a fundamental error: it assumes there exists a **Universal View**—a God's-eye perspective from which all state is visible and all configuration accessible. This violates three kgents principles:

| Principle | Violation |
|-----------|-----------|
| **Heterarchical** (§6) | A singleton `World` creates a center; heterarchy requires no center |
| **Composable** (§5) | A `WorldContext` god-object couples everything to everything |
| **Generative** (§7) | Monolithic state prevents hypothetical world instantiation |

**The Umwelt Insight**: In biology, an *Umwelt* is an organism's subjective perceptual world. A tick perceives heat and butyric acid; a human perceives colors and faces. They share the same physical world but inhabit different Umwelts.

Agents are the same. K-gent perceives persona. B-gent perceives hypotheses. They share the same data lake but **inhabit different Umwelts**.

---

## Part I: The Three Components

Every agent receives an Umwelt composed of three elements:

```
┌─────────────────────────────────────────────────────────────┐
│                         UMWELT                               │
│                                                              │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│   │    State     │  │     DNA      │  │   Gravity    │      │
│   │   (Lens)     │  │   (Config)   │  │  (Ground)    │      │
│   │              │  │              │  │              │      │
│   │  "What I     │  │  "What I     │  │  "What I     │      │
│   │   touch"     │  │   am"        │  │   cannot do" │      │
│   └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│   D-gent Lens       G-gent Tongue     F-gent Contract       │
└─────────────────────────────────────────────────────────────┘
```

### 1.1 State as Lens (D-gent)

**Principle**: Agents never receive the World. They receive a **Lens** focused on their portion.

```python
# The agent sees only its focus
state_lens: Lens[World, AgentState]

# Agent thinks it owns the data
# The Lens handles storage, sync, isolation invisibly
await state_lens.get()  # My state
await state_lens.set(new_value)  # Update my state
```

**Properties**:
- **Isolation**: K-gent cannot see B-gent's state
- **Law-Abiding**: Lens laws (GetPut, PutGet, PutPut) are verified
- **Composable**: Lenses compose (`user_lens >> name_lens`)

**Why Not a Namespace?**
A namespace (`world.namespace("k")`) is still a lookup; it exposes the existence of other namespaces. A Lens is opaque—the agent literally cannot express "show me B-gent's state."

### 1.2 DNA as Config (G-gent)

**Principle**: Configuration is not loaded; it is **expressed**. The agent IS an expression of its config.

```python
@dataclass
class AgentDNA:
    """G-gent tongue defines the genetic code."""
    personality: str
    risk_tolerance: float
    exploration_budget: float  # The Accursed Share (§Meta)

    @classmethod
    def tongue(cls) -> Tongue:
        """Auto-generate G-gent grammar from dataclass."""
        return reify_schema(
            domain=f"dna.{cls.__name__}",
            schema=cls,
        )
```

**The Germination Pattern**:

```python
# Config doesn't "load"—it germinates
agent = AgentFactory.germinate(
    dna=AgentDNA(personality="curious", risk_tolerance=0.7),
    state_lens=world.lens("k.persona"),
)

# The agent IS its DNA
# Changing DNA requires re-germination (new agent instance)
```

**Properties**:
- **Validated**: G-gent tongue validates DNA structure
- **Procedural**: `creativity=0.8` may generate `temperature=1.2`
- **Immutable at Runtime**: DNA doesn't change; agent must be re-germinated

### 1.3 Gravity as Ground (F-gent)

**Principle**: Ground is not a dictionary of facts. It is a **validation field** that exerts force on outputs.

```python
# Ground is constraints, not data
gravity: list[Contract] = [
    FactConsistency(known_facts),  # Cannot contradict established facts
    EthicalBoundary(level="strict"),  # Cannot violate ethical constraints
    DomainInvariant("k.persona", PersonaContract),  # Domain-specific rules
]
```

**The Grounded Pattern**:

```python
# Agent wrapped with gravitational constraints
grounded_agent = Grounded(
    inner=raw_agent,
    gravity=gravity,
)

# Every output passes through gravity
# Violations are caught, not data looked up
result = await grounded_agent.invoke(input)
# → F-gent contracts validate before returning
```

**Why Gravity, Not a Database?**

A fact database (`ground.get("sky_color")`) is passive lookup. Gravity is **active constraint**. The difference:

| Fact Database | Gravitational Field |
|---------------|---------------------|
| Queried on demand | Applied automatically |
| Agent decides when to check | Agent cannot bypass |
| "Is the sky blue?" | "You cannot say the sky is green" |
| Data retrieval | Constraint enforcement |

---

## Part II: The Projector

The Projector is the factory that creates Umwelts. It slices the infinite into the finite.

```python
class Projector:
    """
    Projects the infinite World into finite agent Umwelts.

    The Projector:
    1. Does NOT give agents access to the World
    2. Creates scoped Lenses for state access
    3. Validates DNA against G-gent tongues
    4. Assembles gravitational constraints from F-gent contracts
    """

    def __init__(self, root: DataAgent):
        """
        Initialize with a root D-gent (the "Real").

        Args:
            root: The underlying state store (could be volatile,
                  persistent, or hypothetical)
        """
        self._root = root
        self._gravity_registry: dict[str, list[Contract]] = {}

    def project(
        self,
        agent_id: str,
        dna: Config,
        gravity: list[Contract] | None = None,
    ) -> Umwelt:
        """
        Create an Umwelt for an agent.

        The agent receives:
        - A Lens (cannot see outside its focus)
        - Validated DNA (G-gent checked)
        - Gravitational constraints (F-gent enforced)
        """
        # 1. Create scoped lens
        state_lens = self._root.lens(f"agents.{agent_id}")

        # 2. Validate DNA against tongue
        tongue = dna.tongue()
        if not tongue.validate(dna):
            raise DNAValidationError(f"Invalid DNA for {agent_id}")

        # 3. Assemble gravity
        agent_gravity = gravity or self._gravity_registry.get(agent_id, [])

        return Umwelt(
            state=state_lens,
            dna=dna,
            gravity=agent_gravity,
        )
```

### 2.1 Hypothetical Worlds (Ergodicity)

**The Critical Capability**: B-gent needs to spawn counter-factual worlds.

```python
# Create a hypothetical world in memory
hypothetical_root = VolatileAgent()

# Clone current state into hypothetical
await hypothetical_root.save(await real_root.load())

# Create a projector for the hypothetical
hypothetical_projector = Projector(hypothetical_root)

# Spawn agents in hypothetical world
world_a = hypothetical_projector.project("b.hypothesis", dna_a)
world_b = hypothetical_projector.project("b.hypothesis", dna_b)

# Agents in hypothetical worlds don't know they're hypothetical
# They operate identically to "real" agents
result_a = await agent_a.invoke(input)
result_b = await agent_b.invoke(input)

# Compare outcomes
# The "real" world is unchanged
```

**Why This Works**:
- `Projector` accepts any `DataAgent` as root
- `VolatileAgent` is in-memory (hypothetical)
- `PersistentAgent` is disk-backed (real)
- `SQLAgent` is database-backed (production)
- Agents are **root-agnostic**—they only see their Lens

### 2.2 Temporal Projection (Time Lenses)

Umwelts can also be projected in time:

```python
# Project agent's view at a past timestamp
past_lens = temporal_lens(
    base=state_lens,
    timestamp=one_hour_ago,
)

# Agent sees state as it was
historical_umwelt = Umwelt(
    state=past_lens,
    dna=current_dna,  # DNA is always current
    gravity=current_gravity,
)
```

---

## Part III: The Protocol

### 3.1 The Umwelt Type

```python
@dataclass(frozen=True)
class Umwelt(Generic[S, D]):
    """
    An agent's projected world.

    Immutable after creation. To change an Umwelt,
    re-project through the Projector.
    """
    state: Lens[Any, S]  # Scoped state access
    dna: D  # Agent configuration (validated)
    gravity: tuple[Contract, ...]  # Ground constraints

    async def get(self) -> S:
        """Read state through lens."""
        return await self.state.get()

    async def set(self, value: S) -> None:
        """Write state through lens (gravity checked on agent output, not here)."""
        await self.state.set(value)

    def is_grounded(self, output: Any) -> bool:
        """Check if output satisfies all gravitational constraints."""
        return all(contract.validate(output) for contract in self.gravity)
```

### 3.2 Agent Signature with Umwelt

```python
class Agent(Protocol[A, B]):
    """
    Base agent protocol.

    Agents MAY have an Umwelt. Pure agents (no state) don't need one.
    Stateful agents receive their Umwelt at construction.
    """

    @property
    def umwelt(self) -> Umwelt | None:
        """Agent's projected world, if any."""
        ...

    async def invoke(self, input: A) -> B:
        """Transform input to output."""
        ...

# Stateful agent construction
class KgentAgent(Agent[DialogueInput, DialogueOutput]):
    def __init__(self, umwelt: Umwelt[PersonaState, KgentDNA]):
        self._umwelt = umwelt

    @property
    def umwelt(self) -> Umwelt:
        return self._umwelt

    async def invoke(self, input: DialogueInput) -> DialogueOutput:
        # Access state through lens
        persona = await self._umwelt.get()

        # Use DNA for behavior
        if self._umwelt.dna.personality == "playful":
            # ... playful response generation
            pass

        # Output will be checked against gravity by caller
        return response
```

### 3.3 The Grounded Wrapper

```python
class Grounded(Agent[A, B]):
    """
    Wraps an agent with gravitational constraint checking.

    Every output passes through gravity. Violations raise
    GroundingError, not silent failures.
    """

    def __init__(self, inner: Agent[A, B], gravity: list[Contract]):
        self._inner = inner
        self._gravity = tuple(gravity)

    async def invoke(self, input: A) -> B:
        # Get raw output
        output = await self._inner.invoke(input)

        # Apply gravity
        for contract in self._gravity:
            violation = contract.check(output)
            if violation:
                raise GroundingError(
                    agent=self._inner.name,
                    contract=contract.name,
                    violation=violation,
                )

        return output
```

---

## Part IV: Integration with Existing Systems

### 4.1 D-gent Integration

The Umwelt's state lens IS a D-gent lens. No new abstraction needed.

```python
# Existing D-gent lens
from agents.d import Lens, key_lens

# Umwelt uses it directly
umwelt = Umwelt(
    state=root_lens >> key_lens("k") >> key_lens("persona"),
    dna=KgentDNA(...),
    gravity=[...],
)
```

### 4.2 G-gent Integration

DNA validation uses G-gent tongues.

```python
# G-gent tongue for DNA validation
from agents.g import reify_schema, Tongue

@dataclass
class KgentDNA(Config):
    personality: str
    warmth: float  # 0.0 to 1.0

    @classmethod
    def tongue(cls) -> Tongue:
        return reify_schema(
            domain="dna.kgent",
            schema=cls,
            constraints=[
                ("warmth", lambda x: 0 <= x <= 1),
            ],
        )
```

### 4.3 F-gent Integration

Gravity uses F-gent contracts.

```python
# F-gent contracts for gravity
from agents.f import Contract, Invariant

persona_contract = Contract(
    name="PersonaConsistency",
    invariants=[
        Invariant(
            name="name_stable",
            check=lambda old, new: old.name == new.name,
            message="Persona name cannot change",
        ),
    ],
)
```

### 4.4 J-gent Reality Integration

J-gent's `Reality.CHAOTIC` now has a proper Ground:

```python
class RealityClassifier:
    def __init__(self, gravity: list[Contract]):
        self._gravity = gravity

    async def classify(self, intent: str) -> Reality:
        # Check if intent is grounded
        for contract in self._gravity:
            if not contract.admits(intent):
                return Reality.CHAOTIC  # Ungrounded → collapse

        # Continue classification...
```

---

## Part V: Migration from WorldContext

### 5.1 What Changes

| Old (WorldContext) | New (Umwelt) |
|--------------------|--------------|
| `context.world.get("k.persona")` | `umwelt.get()` (lens is pre-focused) |
| `context.ground.register_fact(...)` | `gravity=[FactContract(...)]` (constraints, not data) |
| `context.config.load(JGentConfig)` | `umwelt.dna` (DNA is immutable) |
| Singleton `World()` | `Projector(root)` (root can be any D-gent) |

### 5.2 Migration Steps

1. **Replace WorldContext injection** with Umwelt injection
2. **Replace config.load()** with DNA at construction
3. **Replace ground.register_fact()** with F-gent contracts in gravity
4. **Replace world.namespace()** with pre-focused Lens

### 5.3 Backward Compatibility

For gradual migration:

```python
class LegacyWorldContext:
    """Adapter from Umwelt to old WorldContext interface."""

    def __init__(self, projector: Projector, agent_id: str):
        self._projector = projector
        self._agent_id = agent_id
        self._umwelt = None

    @property
    def world(self) -> "LegacyWorld":
        return LegacyWorld(self._projector, self._agent_id)

# Usage during migration
legacy_context = LegacyWorldContext(projector, "k")
agent = KgentAgent(context=legacy_context)  # Old interface

# Eventually migrate to:
umwelt = projector.project("k", dna)
agent = KgentAgent(umwelt=umwelt)  # New interface
```

---

## Part VI: Properties Achieved

### 6.1 Principle Compliance

| Principle | How Umwelt Satisfies |
|-----------|---------------------|
| **Heterarchical** | No center; Projector creates and steps away |
| **Composable** | Lenses compose; agents compose; gravity composes |
| **Generative** | Hypothetical worlds instantiate from spec |
| **Tasteful** | Each agent gets exactly what it needs |
| **Ethical** | Gravity enforces constraints automatically |

### 6.2 Critical Capabilities

| Capability | Mechanism |
|------------|-----------|
| **Agent Isolation** | Lens scope prevents cross-agent access |
| **Hypothetical Worlds** | Projector on VolatileAgent root |
| **Config Validation** | G-gent tongue on DNA |
| **Constraint Enforcement** | F-gent contracts as gravity |
| **Temporal Projection** | Time lenses on Umwelt state |

### 6.3 The Biological Metaphor

| Biological | Umwelt |
|------------|--------|
| Organism's perceived world | Agent's Umwelt |
| Genetic code | DNA (Config) |
| Physical laws | Gravity (Ground) |
| Sensory organs | Lens (State access) |
| Germination | Agent construction |
| Environment | Root DataAgent |

---

## Appendix A: Files to Create

```
impl/claude/agents/d/projector.py    # Projector class
impl/claude/bootstrap/umwelt.py      # Umwelt type
impl/claude/agents/f/gravity.py      # Grounded wrapper
spec/protocols/config.md             # Config as DNA spec
```

## Appendix B: Files to Modify

```
impl/claude/agents/k/persona.py      # Inject Umwelt instead of state
impl/claude/agents/j/reality.py      # Use gravity for grounding
impl/claude/agents/b/hypothesis.py   # Use Projector for hypothetical worlds
docs/unified-world-access-proposal.md # Mark as superseded
```

---

*The tick knows only warmth and acid. The human knows only light and sound. Neither is wrong—each inhabits its Umwelt. So too with agents: K-gent knows persona, B-gent knows hypothesis, and neither needs to know the other exists.*
