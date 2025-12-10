# Unified World Access Layer: Consolidation Proposal

> **Status**: Implementation Proposal v1.0
> **Date**: 2025-12-09
> **Scope**: Consolidating worldmodel/ground/config/data access patterns across agents

---

## Executive Summary

After assessing `impl/claude/agents/`, I identified **significant fragmentation** in how agents access state, configuration, and "ground truth." This proposal introduces a **Unified World Access Layer (UWAL)** that consolidates these patterns while leveraging existing D-gent, F-gent, and G-gent infrastructure.

**Key Findings**:
1. **38 files** currently depend on D-gent (DataAgent/PersistentAgent/VolatileAgent)
2. **50+ Config classes** scattered across agents with no shared pattern
3. **Zero unified "world model"** or grounding infrastructure
4. **Each agent reinvents** state management, configuration, and reality grounding

**Proposed Solution**: Three-layer architecture unifying all world access:
```
┌─────────────────────────────────────────────────────────────┐
│                    WORLD ACCESS LAYER                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   World()    │  │   Ground()   │  │   Config()   │       │
│  │  (D-gent)    │  │  (F-gent)    │  │  (G-gent)    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                 │                 │                │
│         └─────────────────┴─────────────────┘                │
│                           │                                  │
│                    WorldContext                              │
│              (unified access protocol)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Part 1: Current State Assessment

### 1.1 Data Access Fragmentation (D-gent Usage)

**Files depending on D-gent primitives** (38 total):

| Agent | D-gent Usage | Pattern |
|-------|--------------|---------|
| K-gent | `PersistentAgent` | Persona state persistence |
| L-gent | `PersistentAgent` | Catalog/registry storage |
| B-gent | `PersistentAgent` | Hypothesis persistence |
| H-gent | `PersistentAgent` | Dialectic state |
| E-gent | `PersistentAgent` | Error memory |
| M-gent | `DataAgent` | Tiered memory |

**Problem**: Each agent creates its own `PersistentAgent(path="...")` with:
- Hardcoded paths
- No shared schema validation
- No cross-agent state visibility
- No coordinated lifecycle

### 1.2 Configuration Sprawl (50+ Config Classes)

**Sample of Config classes found**:

```
ParserConfig, ParallelConfig, MockConfig, CircuitBreakerConfig,
RetryConfig, PrototypeConfig, VoIObservationConfig, DSPyLLMConfig,
AdvancedRefineryConfig, ValidationConfig, StabilityConfig,
JGentConfig, BootstrapConfig, MemoryConfig, CompressionConfig,
FallbackConfig, SafetyConfig, EvolutionConfig, MeteredPromptConfig,
NoiseConfig, FailingConfig, PersistenceConfig...
```

**Problem**:
- No inheritance from a base `AgentConfig`
- No standard serialization/loading
- No G-gent grammar validation
- No F-gent contract enforcement

### 1.3 Missing WorldModel/Grounding

**Current grounding mentions** (very sparse):
- `o/semantic.py`: `grounding_failures` in hallucination detection
- `i/field.py`: `GROUND = "G"` pheromone type
- `i/forge_view.py`: `tags=["bootstrap", "grounding"]`

**What's Missing**:
- No unified "world model" agents can query
- No "ground truth" registry for facts
- No grounding protocol for LLM outputs
- J-gent's `Reality.CHAOTIC` collapses to "Ground" but Ground isn't defined

---

## Part 2: Proposed Architecture

### 2.1 The Three Pillars

#### Pillar 1: `World()` — Unified State (D-gent Integration)

```python
from agents.d import UnifiedMemory, MemoryConfig

class World:
    """
    Unified world state accessible to all agents.

    Single source of truth for:
    - Agent states (persona, dialectic, memory)
    - Session context
    - Cross-agent shared state
    """

    def __init__(self, root: Path = Path(".kgents")):
        self._root = root
        self._memory = UnifiedMemory(
            underlying=PersistentAgent(root / "world.json", dict),
            config=MemoryConfig(
                enable_semantic=True,
                enable_temporal=True,
                enable_relational=True,
            )
        )
        self._namespaces: dict[str, DataAgent] = {}

    def namespace(self, agent_id: str) -> DataAgent:
        """Get namespaced D-gent for an agent."""
        if agent_id not in self._namespaces:
            self._namespaces[agent_id] = PersistentAgent(
                path=self._root / f"{agent_id}.json",
                schema=dict
            )
        return self._namespaces[agent_id]

    async def get(self, path: str) -> Any:
        """Lens-based access: world.get("k.persona.preferences")"""
        # Uses D-gent lenses for path traversal
        ...

    async def set(self, path: str, value: Any) -> None:
        """Lens-based mutation with lineage tracking."""
        ...
```

**Migration Path**:
```python
# BEFORE (per-agent state)
self._storage = PersistentAgent(path="k-gent/persona.json", schema=PersonaState)

# AFTER (unified world)
self._storage = world.namespace("k-gent")  # Automatic path management
```

#### Pillar 2: `Ground()` — Reality Grounding (F-gent Integration)

```python
from agents.f import Contract, Invariant

class Ground:
    """
    Ground truth registry for reality grounding.

    Agents can:
    - Register facts (with contracts)
    - Query facts
    - Ground LLM outputs against known truth
    """

    def __init__(self, world: World):
        self._world = world
        self._facts: dict[str, GroundedFact] = {}

    def register_fact(
        self,
        key: str,
        value: Any,
        contract: Contract | None = None,
        source: str = "manual",
    ) -> None:
        """Register a ground truth fact with optional F-gent contract."""
        self._facts[key] = GroundedFact(
            value=value,
            contract=contract,
            source=source,
            timestamp=datetime.now(),
        )

    async def ground(self, claim: str) -> GroundingResult:
        """
        Ground a claim against registered facts.

        Returns:
            GroundingResult with:
            - is_grounded: bool
            - supporting_facts: list[str]
            - contradictions: list[str]
            - confidence: float
        """
        # Integration with O-gent hallucination detection
        ...

    def as_context(self) -> str:
        """Export grounded facts as LLM context."""
        return "\n".join(
            f"FACT[{k}]: {v.value}"
            for k, v in self._facts.items()
        )
```

**Integration with J-gent Reality Classification**:
```python
# In J-gent reality.py
class RealityClassifier:
    def __init__(self, ground: Ground):
        self._ground = ground

    async def classify(self, intent: str) -> Reality:
        # Use ground() to check if intent is grounded
        grounding = await self._ground.ground(intent)
        if not grounding.is_grounded:
            return Reality.CHAOTIC  # Ungrounded → collapse
        ...
```

#### Pillar 3: `Config()` — Grammar-Validated Configuration (G-gent Integration)

```python
from agents.g import Tongue, reify_schema

class Config:
    """
    Grammar-validated configuration with G-gent tongues.

    Every Config class gets:
    - Auto-generated G-gent tongue (schema validation)
    - F-gent contract (invariant enforcement)
    - D-gent persistence (automatic save/load)
    """

    @classmethod
    def tongue(cls) -> Tongue:
        """Generate G-gent tongue from config dataclass."""
        return reify_schema(
            domain=f"config.{cls.__name__}",
            description=cls.__doc__ or f"Configuration for {cls.__name__}",
            schema=cls,
        )

    @classmethod
    async def load(cls, world: World, namespace: str) -> Self:
        """Load config from world with validation."""
        storage = world.namespace(namespace)
        data = await storage.load()
        # Validate against tongue
        tongue = cls.tongue()
        validated = tongue.parse(data)  # G-gent validation
        return cls(**validated)

    async def save(self, world: World, namespace: str) -> None:
        """Save config with F-gent contract verification."""
        storage = world.namespace(namespace)
        await storage.save(asdict(self))
```

**Migration Path**:
```python
# BEFORE (ad-hoc config)
@dataclass
class JGentConfig:
    max_depth: int = 5
    entropy_budget: float = 1.0

# AFTER (unified config with validation)
@dataclass
class JGentConfig(Config):
    """J-gent recursion and entropy configuration."""
    max_depth: int = 5
    entropy_budget: float = 1.0

    # Auto-generated:
    # - G-gent tongue for validation
    # - F-gent contract for invariants
    # - D-gent persistence
```

### 2.2 The WorldContext Protocol

```python
@dataclass
class WorldContext:
    """
    Unified context passed to all agents.

    Replaces ad-hoc context dictionaries with typed access.
    """
    world: World      # State access
    ground: Ground    # Reality grounding
    config: Config    # Configuration

    # Convenience accessors
    def get_state(self, path: str) -> Any:
        return self.world.get(path)

    def is_grounded(self, claim: str) -> bool:
        return self.ground.ground(claim).is_grounded

    def get_config(self, cls: Type[Config]) -> Config:
        return cls.load(self.world, cls.__name__)
```

**Agent Integration**:
```python
class Agent(Protocol[A, B]):
    """Base agent protocol with WorldContext."""

    @property
    def context(self) -> WorldContext | None:
        """Optional world context for grounded agents."""
        ...

    async def invoke(self, input: A) -> B:
        ...

# Usage
class KgentAgent(Agent[DialogueInput, DialogueOutput]):
    def __init__(self, context: WorldContext):
        self._context = context
        self._state = context.world.namespace("k-gent")
```

---

## Part 3: Implementation Plan

### Phase 1: Core Infrastructure (Week 1)

| Task | File | Integration |
|------|------|-------------|
| World class | `impl/claude/agents/d/world.py` | UnifiedMemory |
| Ground class | `impl/claude/agents/f/ground.py` | Contract |
| Config base | `impl/claude/agents/g/config.py` | Tongue |
| WorldContext | `impl/claude/bootstrap/context.py` | All |

### Phase 2: D-gent Consolidation (Week 2)

| Agent | Current | Migration |
|-------|---------|-----------|
| K-gent | `persistent_persona.py` | `world.namespace("k")` |
| L-gent | `catalog.py` Registry | `world.namespace("l")` |
| B-gent | `persistent_hypothesis.py` | `world.namespace("b")` |
| H-gent | `persistent_dialectic.py` | `world.namespace("h")` |
| E-gent | `persistent_memory.py` | `world.namespace("e")` |

### Phase 3: Config Consolidation (Week 3)

| Config | Current | Migration |
|--------|---------|-----------|
| `JGentConfig` | Local dataclass | `extends Config` |
| `MemoryConfig` | Local dataclass | `extends Config` |
| `ParserConfig` | Local dataclass | `extends Config` |
| All 50+ | Local dataclass | `extends Config` |

### Phase 4: Grounding Integration (Week 4)

| Integration | Description |
|-------------|-------------|
| J-gent Reality | Ground() informs CHAOTIC classification |
| O-gent Hallucination | Ground() provides known facts |
| B-gent Hypothesis | Ground() validates against established science |
| K-gent Persona | Ground() anchors persona facts |

---

## Part 4: Benefits

### 4.1 Consolidation Wins

| Metric | Before | After |
|--------|--------|-------|
| State management files | 38 | 1 (world.py) |
| Config classes (unvalidated) | 50+ | 0 (all validated) |
| Grounding infrastructure | 0 | 1 (ground.py) |
| Cross-agent visibility | None | Full (WorldContext) |

### 4.2 Capability Unlocks

1. **Cross-Agent State Queries**: K-gent can query L-gent catalog
2. **Grounded LLM Outputs**: B-gent hypotheses validated against facts
3. **Grammar-Validated Config**: G-gent tongues enforce config schemas
4. **Observable State Changes**: O-gent watches all world mutations
5. **Economically Metered Access**: B-gent charges for world access

### 4.3 Alignment with Existing Patterns

| Existing | Enhanced By |
|----------|-------------|
| D-gent UnifiedMemory | World() as facade |
| F-gent Contracts | Ground() fact validation |
| G-gent Tongues | Config() schema generation |
| L-gent Catalog | World() namespace indexing |
| O-gent Observation | WorldContext observable |
| B-gent Economics | Metered world access |

---

## Part 5: Open Questions

1. **Namespace Collision**: How to prevent `world.namespace("k")` conflicts?
   - Proposal: Agent registration with L-gent catalog

2. **Distributed World**: How does World() scale beyond single process?
   - Proposal: D-gent Redis/SQL backends already exist

3. **Grounding Authority**: Who can register facts in Ground()?
   - Proposal: F-gent contracts + B-gent economic stake

4. **Config Migration**: How to migrate 50+ existing configs?
   - Proposal: Gradual adoption, backward compat layer

---

## Appendix A: Files to Create

```
impl/claude/agents/d/world.py       # World class
impl/claude/agents/f/ground.py      # Ground class
impl/claude/agents/g/config.py      # Config base class
impl/claude/bootstrap/context.py    # WorldContext
```

## Appendix B: Files to Modify

```
impl/claude/agents/k/persistent_persona.py  # Use World()
impl/claude/agents/l/catalog.py             # Use World()
impl/claude/agents/b/persistent_hypothesis.py
impl/claude/agents/h/persistent_dialectic.py
impl/claude/agents/e/persistent_memory.py
impl/claude/agents/j/reality.py             # Use Ground()
impl/claude/agents/o/semantic.py            # Use Ground()
```

## Appendix C: Test Coverage Required

- `test_world.py`: 50+ tests (namespace, lens, temporal)
- `test_ground.py`: 30+ tests (fact registration, grounding)
- `test_config.py`: 40+ tests (tongue generation, validation)
- `test_context.py`: 20+ tests (integration)
- Migration tests for each agent

---

*This proposal consolidates fragmented patterns into a coherent World Access Layer, leveraging existing D-gent, F-gent, and G-gent infrastructure.*
