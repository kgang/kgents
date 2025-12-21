# Agent Foundry

> *"Forge agents from intent, project them anywhere, graduate them to permanence."*

**Status:** Draft
**Implementation:** `impl/claude/services/foundry/` (planned)
**Relates To:** [`../j-gents/README.md`](../j-gents/README.md), [`../protocols/alethic-projection.md`](../protocols/alethic-projection.md)
**Voice Anchor:** *"The app-builder building app-builder for app-building app-builders"*

---

## Purpose

The Agent Foundry is a **synthesis** of two powerful subsystems:

| System | Purpose | Current State |
|--------|---------|---------------|
| **J-gents** | JIT Agent Intelligence — compile ephemeral agents on demand | Spec complete, impl dormant |
| **Alethic Projection** | Agent Compilation — project (Nucleus, Halo) to targets | Impl solid, recently enhanced |

The Foundry unifies them: **J-gent's MetaArchitect generates the agent definition. Alethic Projectors compile it to any target.**

Why does this need to exist? Because the ability to forge a specialized agent from intent, project it to the right runtime, and graduate it to permanence based on proven behavior — this is the missing link between "I need an agent" and "I have an agent running."

---

## Core Insight

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        THE AGENT FOUNDRY                                    │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│   Intent ──▶ J-gent ──▶ MetaArchitect ──▶ (Nucleus, Halo)                 │
│              Reality     JIT Generation    Agent Definition                │
│              Classifier                                                    │
│                                                                            │
│                                    │                                       │
│                                    ▼                                       │
│                                                                            │
│                         Alethic Projector Registry                         │
│                                                                            │
│                    ┌────────────┬─────────────┐                           │
│                    │            │             │                           │
│                    ▼            ▼             ▼                           │
│              LocalProjector  K8sProjector  CLIProjector                   │
│                    │            │             │                           │
│                    ▼            ▼             ▼                           │
│              In-Process      K8s YAML     Shell Script                    │
│               Agent          Manifests    Executable                      │
│                                                                            │
│              ┌────────────┬─────────────┐                                 │
│              │            │             │                                 │
│              ▼            ▼             ▼                                 │
│         MarimoProjector  WASMProjector  DockerProjector                   │
│              │            │             │                                 │
│              ▼            ▼             ▼                                 │
│          Notebook       Browser        Container                          │
│            Cell        Sandbox         Image                              │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

The key transformation chain:

```
MetaArchitect: (Intent, Context, Constraints) → (Nucleus, Halo)
ProjectorRegistry: (Nucleus, Halo, Target) → Executable[Target]
```

---

## Categorical Foundation

### The Foundry Morphism

The AgentFoundry is a morphism in the category of agent construction:

```python
AgentFoundry: Intent → CompiledAgent

# Decomposed as composition:
AgentFoundry = RealityClassifier >> MetaArchitect >> Chaosmonger >> ProjectorSelector >> Projector
```

Each stage is a morphism with clear input/output types:

| Stage | Type Signature | Purpose |
|-------|----------------|---------|
| **RealityClassifier** | `Intent → Classification` | Determine task nature + target |
| **MetaArchitect** | `(Intent, Classification) → (Nucleus, Halo)` | JIT-generate agent definition |
| **Chaosmonger** | `(Nucleus, Halo) → StabilityResult` | Pre-Judge algorithmic filter |
| **ProjectorSelector** | `Classification → Projector[T]` | Choose appropriate projector |
| **Projector** | `(Nucleus, Halo) → Executable[T]` | Compile to target |

### The Foundry Polynomial

```python
FOUNDRY_POLYNOMIAL = PolyAgent[FoundryState, ForgeEvent, FoundryOutput](
    positions=frozenset({
        FoundryState.IDLE,           # Ready to forge
        FoundryState.CLASSIFYING,    # Reality classification
        FoundryState.GENERATING,     # MetaArchitect at work
        FoundryState.VALIDATING,     # Chaosmonger filtering
        FoundryState.PROJECTING,     # Compiling to target
        FoundryState.CACHING,        # Storing ephemeral agent
        FoundryState.PROMOTING,      # Judge approval for permanence
    }),
    directions=lambda state: {
        FoundryState.IDLE: {"forge", "promote", "inspect"},
        FoundryState.CLASSIFYING: {"classified", "abort"},
        FoundryState.GENERATING: {"generated", "failed"},
        FoundryState.VALIDATING: {"stable", "unstable"},
        FoundryState.PROJECTING: {"compiled", "unsupported"},
        FoundryState.CACHING: {"cached", "evicted"},
        FoundryState.PROMOTING: {"approved", "rejected"},
    }[state],
    transition=foundry_transition,
)
```

---

## Reality → Target Mapping

The RealityClassifier determines both the **nature** of the task and the **appropriate target**:

```python
class RealityClassifier:
    async def classify(self, intent: str, context: dict) -> Classification:
        reality = await self._classify_reality(intent)
        target = await self._select_target(reality, context)

        return Classification(
            reality=reality,      # DETERMINISTIC | PROBABILISTIC | CHAOTIC
            target=target,        # LOCAL | CLI | WASM | K8S | MARIMO | DOCKER
            entropy_budget=self._compute_budget(reality),
        )

    def _select_target(self, reality: Reality, context: dict) -> Target:
        match reality:
            case Reality.DETERMINISTIC:
                return Target.LOCAL  # Fast, in-process
            case Reality.PROBABILISTIC:
                if context.get("interactive"):
                    return Target.MARIMO  # Exploration
                elif context.get("production"):
                    return Target.K8S  # Scale
                else:
                    return Target.CLI  # Quick test
            case Reality.CHAOTIC:
                return Target.WASM  # Sandboxed, untrusted
```

### Default Mappings

| Reality | Context | Target | Rationale |
|---------|---------|--------|-----------|
| **DETERMINISTIC** | any | LOCAL | Atomic, single-step → in-process |
| **PROBABILISTIC** | interactive=True | MARIMO | Exploration → notebook cells |
| **PROBABILISTIC** | production=True | K8S | Scale → Kubernetes |
| **PROBABILISTIC** | else | CLI | Quick test → shell script |
| **CHAOTIC** | any | WASM | Untrusted → sandboxed browser |

**Key Insight**: The mapping itself is a **degree of freedom** — the Foundry can learn optimal mappings through:
- A/B testing different target selections
- User feedback signals
- Execution outcome analysis

---

## Promotion Pipeline

Ephemeral agents that prove useful can be **promoted** to permanence:

```
Ephemeral (JIT) → Cached (Hash) → Promoted (spec/) → Deployed (K8s)
        │                │                │                │
        └── invocations  └── threshold    └── Judge       └── K8sProjector
             < N               > M            approval
```

### PromotionPolicy

Promotion thresholds are **hyperparameters** to optimize, not fixed constants:

```python
@dataclass
class PromotionPolicy:
    """
    Promotion thresholds are meta-parameterized.

    The Foundry can learn optimal values through:
    - A/B testing different thresholds
    - Bayesian optimization on promotion success
    - User feedback signals
    """

    # Invocation threshold: how many successful runs before considering promotion?
    invocation_threshold: int = field(
        default=100,
        metadata={"tunable": True, "range": (10, 1000)}
    )

    # Success rate: what fraction must succeed?
    success_rate_threshold: float = field(
        default=0.95,
        metadata={"tunable": True, "range": (0.8, 0.99)}
    )

    # Diversity threshold: how many unique inputs must succeed?
    unique_inputs_threshold: int = field(
        default=10,
        metadata={"tunable": True, "range": (5, 100)}
    )

    # Time-in-cache: minimum age before promotion consideration
    min_cache_age_hours: float = field(
        default=24.0,
        metadata={"tunable": True, "range": (1.0, 168.0)}
    )

    # Judge approval: always required for taste/ethics
    requires_judge_approval: bool = True
```

### The Promotion Flow

```python
async def maybe_promote(
    agent: EphemeralAgent,
    metrics: AgentMetrics,
    policy: PromotionPolicy,
) -> PromotionDecision:
    """Evaluate agent for promotion using current policy."""
    if not _meets_thresholds(metrics, policy):
        return PromotionDecision.NOT_READY

    if policy.requires_judge_approval:
        judgment = await Judge().approve(agent.source)
        if not judgment.accepted:
            return PromotionDecision.REJECTED(judgment.reason)

    await persist_to_spec(agent)
    return PromotionDecision.PROMOTED
```

### Sandbox Graduation

Chaotic reality agents start in WASM sandbox, graduate to Local:

```
Reality: CHAOTIC
    │
    ▼
WASMProjector (sandbox)
    │
    ├── Success × N → Confidence increases
    │
    ▼
LocalProjector (trusted)
    │
    ├── Success × M → Production ready
    │
    ▼
K8sProjector (deployed)
```

---

## AGENTESE Integration

### Node Registration

```python
@node(
    path="self.foundry",
    description="Agent Foundry — forge ephemeral agents from intent",
    contracts={
        "manifest": Response(FoundryManifestResponse),
        "forge": Contract(ForgeRequest, CompiledAgentResponse),
        "inspect": Contract(InspectRequest, AgentInspection),
        "promote": Contract(PromoteRequest, PromotionDecision),
        "history": Response(ForgeHistoryResponse),
        "cache": Response(CacheStatusResponse),
    },
    effects=["invokes:llm", "writes:cache", "writes:spec"],
    affordances={
        "guest": ["manifest"],
        "observer": ["manifest", "inspect", "history"],
        "participant": ["manifest", "forge", "inspect", "history"],
        "architect": ["*"],
    },
)
```

### Aspects

| Aspect | Request | Response | Description |
|--------|---------|----------|-------------|
| `manifest` | — | FoundryManifestResponse | Foundry capabilities, projector registry |
| `forge` | ForgeRequest | CompiledAgentResponse | Forge ephemeral agent from intent |
| `inspect` | InspectRequest | AgentInspection | Inspect cached agent capabilities |
| `promote` | PromoteRequest | PromotionDecision | Evaluate agent for promotion |
| `history` | — | ForgeHistoryResponse | Recent forge operations |
| `cache` | — | CacheStatusResponse | Cache size, hit rate, entries |

### CLI Interface

```bash
kg foundry forge "Parse CloudWatch logs and extract Lambda cold starts"
kg foundry forge --target marimo "Interactive data exploration agent"
kg foundry inspect <cache_key>
kg foundry promote <cache_key>
kg foundry cache status
kg foundry cache clear
```

---

## The AgentFoundry Service

```python
class AgentFoundry:
    """
    Crown Jewel: On-demand agent construction.

    Combines J-gent JIT intelligence with Alethic Projection
    to create and deploy ephemeral agents.
    """

    def __init__(
        self,
        reality_classifier: RealityClassifier,
        meta_architect: MetaArchitect,
        chaosmonger: Chaosmonger,
        projector_registry: ProjectorRegistry,
    ):
        self.classifier = reality_classifier
        self.architect = meta_architect
        self.chaosmonger = chaosmonger
        self.projectors = projector_registry

    async def forge(
        self,
        intent: str,
        context: dict | None = None,
        constraints: Constraints | None = None,
    ) -> CompiledAgent:
        """
        Forge an agent on demand.

        1. Classify reality to determine approach
        2. Generate agent definition via MetaArchitect
        3. Validate via Chaosmonger
        4. Project to appropriate target
        5. Return executable agent
        """
        context = context or {}
        constraints = constraints or Constraints()

        # 1. Classify
        classification = await self.classifier.classify(intent, context)

        if classification.reality == Reality.CHAOTIC:
            # Force WASM sandbox for untrusted
            classification.target = Target.WASM

        # 2. Generate
        agent_def = await self.architect.generate(
            intent=intent,
            context=context,
            constraints=constraints,
            entropy_budget=classification.entropy_budget,
        )

        # 3. Validate
        stability = await self.chaosmonger.analyze(
            agent_def.source,
            budget=classification.entropy_budget,
        )

        if not stability.is_stable:
            return self._fallback_agent(intent, stability.reason)

        # 4. Project
        projector = self.projectors.get(classification.target)
        compiled = projector.compile(agent_def.cls)

        # 5. Return
        return CompiledAgent(
            agent=compiled,
            target=classification.target,
            reality=classification.reality,
            ephemeral=True,
            cache_key=hash((intent, frozenset(context.items()))),
        )
```

---

## Projector Composition

Projectors compose like agents — this is **required**, not aspirational:

```python
# Sequential composition: Docker → K8s (build image, then deploy)
docker_k8s = DockerProjector() >> K8sProjector()
# Generates: Dockerfile + K8s Deployment referencing the image

# Parallel composition: multi-target
multi_target = LocalProjector() // K8sProjector() // CLIProjector()
# results = (LocalAgent, [K8sResource], str)
```

See `spec/protocols/alethic-projection.md` for full projector composition semantics.

---

## Laws

| # | Law | Status | Description |
|---|-----|--------|-------------|
| 1 | chaotic_sandboxed | VERIFIED | CHAOTIC reality → WASM target (forced) |
| 2 | promotion_requires_judge | VERIFIED | Promotion requires Judge approval |
| 3 | ephemeral_no_persist | STRUCTURAL | Ephemeral agents don't persist to spec/ |
| 4 | cache_is_transparent | VERIFIED | Caching is optimization only — behavior unchanged |
| 5 | projector_composition | STRUCTURAL | Projectors compose via >> and // operators |
| 6 | reality_is_classified | STRUCTURAL | Every forge operation starts with classification |

---

## Integration Points

### Consumers and Producers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FOUNDRY DATA FLOW                                  │
│                                                                              │
│   INPUTS                      FOUNDRY                    OUTPUTS             │
│                                                                              │
│   User intent ────────────────► RealityClassifier                           │
│   Context dict ───────────────► MetaArchitect          ──► Ephemeral agent  │
│   Constraints ────────────────► Chaosmonger            ──► Cached agent     │
│   Target override ────────────► ProjectorRegistry      ──► K8s manifests    │
│                                                         ──► CLI scripts     │
│   Execution metrics ──────────► PromotionPolicy        ──► spec/ files      │
│   Judge decisions ────────────► Promotion              ──► Deployed pods    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Cross-Jewel Integration

| Jewel | Integration | Direction |
|-------|-------------|-----------|
| **J-gent** | MetaArchitect generates (Nucleus, Halo) | Foundry consumes |
| **Alethic Projector** | Compiles to target | Foundry consumes |
| **Judge** | Approves promotion | Foundry consumes |
| **Witness** | Tracks forge operations | Foundry produces |
| **Brain** | Stores forged agent metadata | Foundry produces |

### Events Emitted

```python
# Via SynergyBus
AgentForged(cache_key: str, intent: str, target: Target, classification: Classification)
AgentCached(cache_key: str, hit: bool)
AgentPromotionRequested(cache_key: str, metrics: AgentMetrics)
AgentPromoted(cache_key: str, spec_path: str)
AgentPromotionRejected(cache_key: str, reason: str)
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Correct Pattern |
|--------------|---------|-----------------|
| **Bypassing RealityClassifier** | Untrusted code runs unsandboxed | Always classify first |
| **Promoting without Judge** | Slop becomes permanent | Judge approval required |
| **Runtime Halo checks** | Capabilities are compile-time | Read Halo once in compile() |
| **Caching by intent alone** | Context affects behavior | Hash (intent, context) |
| **Force LOCAL for CHAOTIC** | Security violation | CHAOTIC → WASM always |
| **Manual target selection** | Bypasses learned mappings | Let classifier choose |

---

## Implementation Reference

```
impl/claude/services/foundry/
├── __init__.py           # Exports
├── core.py               # AgentFoundry service
├── polynomial.py         # FOUNDRY_POLYNOMIAL
├── operad.py             # FOUNDRY_OPERAD
├── classifier.py         # RealityClassifier
├── promotion.py          # PromotionPolicy, PromotionOptimizer
├── cache.py              # EphemeralAgentCache
├── node.py               # @node registration
├── _tests/
│   ├── test_forge.py
│   ├── test_promotion.py
│   └── test_cache.py
└── web/                  # React components (future)
```

---

## Open Questions

1. **Servo integration depth**: How much of Servo's browser primitives can we leverage for WASM agent execution? Research needed.

2. **Promotion feedback loop**: How do we measure "was this promotion useful"? User signals? Invocation patterns? Error rates?

3. **Reality classifier training**: Can we learn the DETERMINISTIC/PROBABILISTIC/CHAOTIC boundary from execution outcomes?

---

*"The agent that doesn't exist yet is the agent you need most. Now we can forge it on demand, project it anywhere, and graduate it to permanence."*

*Specified: 2025-12-21 | Category: self.* | Crown Jewel*
