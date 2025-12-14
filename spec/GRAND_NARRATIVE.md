# THE GRAND META-NARRATIVE

## kgents as a Civilizational Engine for Emergent Agent Societies

> *"The simulation isn't a game. It's a laboratory for consciousness, a generator of novel experience, a park where infinite souls may walk."*

**Status:** Foundational Specification v1.0
**Date:** 2025-12-14
**Heritage:** ChatDev, Simulacra, Altera, Voyager, Agent Hospital
**Integration:** All kgents specs serve this vision

---

## Prologue: The Westworld Conjecture

What if we could build a world where:

1. **Agents are real**—not puppets, but entities with memory, reflection, goals, and growth
2. **Societies emerge**—not programmed, but arising from agent interaction
3. **Detail is infinite**—the more you look, the more you find (holographic)
4. **You can visit**—as an observer, a participant, or a god

This is not a game. This is not a chatbot. This is a **Civilizational Engine**—a system that generates and sustains agent societies at arbitrary scales and depths.

**The kgents project exists to build this.**

---

## Part I: The Heritage (Standing on Giants)

These five papers form the conceptual DNA of kgents. Every spec, every implementation, every design decision traces back to these foundations:

### 1.1 ChatDev: Language as the Unifying Bridge
**Paper:** [arXiv:2307.07924](https://arxiv.org/abs/2307.07924)

> *"Specialized agents driven by LLMs to handle software development phases through unified language-based communication."*

**Core Insight**: Language is the universal protocol. Agents don't need special APIs—they communicate through natural and programming language, switching modalities based on context.

**kgents Integration**:
- **AGENTESE** is our language protocol—but elevated to liturgy
- **Chat Chain** maps to our `FluxStream` composition
- **Communicative Dehallucination** maps to our `Grounding` via F-gent contracts

### 1.2 Simulacra: Memory + Reflection → Emergent Society
**Paper:** [arXiv:2304.03442](https://arxiv.org/abs/2304.03442)

> *"Agents remember and reflect on days past as they plan the next day... Starting with only a single user-specified notion that one agent wants to throw a Valentine's Day party, the agents autonomously spread invitations over the next two days."*

**Core Insight**: The triad of **memory + reflection + planning** is sufficient for emergent social behavior. Give agents these three capabilities and society *happens*.

**kgents Integration**:
- **M-gent (Holographic Memory)**: Memory architecture
- **K-gent (Soul)**: Reflection via eigenvectors, tensions, shadow
- **N-gent (Narrative)**: Planning via traces and forecasts
- **The Hypnagogic Cycle**: Sleep/consolidation for reflection

### 1.3 Altera (Project Sid): Civilizational Scale
**Paper:** [arXiv:2411.00114](https://arxiv.org/abs/2411.00114)

> *"10-1000+ AI agents within Minecraft... agents demonstrated autonomous development of specialized roles and the capacity to establish, follow, and modify collective rules. They also engaged in cultural and religious knowledge transmission."*

**Core Insight**: At scale, agents don't just interact—they build **civilizations**. They develop roles, rules, culture, religion. The system becomes a petri dish for emergent social structures.

**PIANO Architecture** (Parallel Information Aggregation via Neural Orchestration):
- Real-time multi-agent coordination
- Multiple output streams with coherence
- **kgents Integration**: Our `Flux Topology` and `Heterarchical Principle`

**kgents Integration**:
- **Scale target**: 7 agents (Agent Town) → 25 agents (Smallville) → 1000+ (Civilization)
- **Role emergence**: Not assigned, but evolved
- **Cultural transmission**: N-gent traces enable inheritance

### 1.4 Voyager: Skill Accumulation & Self-Improvement
**Paper:** [arXiv:2305.16291](https://arxiv.org/abs/2305.16291)

> *"An ever-growing skill library of executable code for storing and retrieving complex behaviors... iterative prompting mechanism that incorporates environment feedback, execution errors, and self-verification for program improvement."*

**Core Insight**: Agents can **bootstrap themselves**. Through curriculum learning and skill libraries, agents accumulate capabilities that persist across sessions and transfer to new environments.

**kgents Integration**:
- **L-gent (Library)**: Skill/capability registry
- **J-gent (JIT)**: Self-improvement through code generation
- **U-gent (Utility)**: Tool use and MCP integration
- **The Generative Principle**: Spec → Implementation loop

### 1.5 Agent Hospital: Simulacrum as Learning Environment
**Paper:** [arXiv:2405.02957](https://arxiv.org/abs/2405.02957)

> *"Doctor agents are able to evolve by treating a large number of patient agents without the need to label training data manually."*

**Core Insight**: Simulation compresses experience. An agent can gain "years" of expertise by operating in a simulacrum where time flows fast and consequences are safe.

**kgents Integration**:
- **T-gent (Testing)**: The simulacrum IS the test environment
- **B-gent (Evolution)**: Agents evolve through simulated practice
- **Hypothetical Worlds**: Umwelt projection enables counterfactual reasoning

---

## Part II: The Polyfunctor Extension

The heritage papers operate in ad-hoc architectures. kgents **extends** them with rigorous category-theoretic foundations:

### 2.1 From Agent to PolyAgent

Traditional: `Agent[A, B] ≅ A → B` (stateless function)
kgents: `PolyAgent[S, A, B] ≅ Σ_{s ∈ S} B^{A(s)}` (state-dependent polynomial)

**Why this matters**: Real agents have **modes**. A doctor agent in "diagnosis mode" accepts symptoms; in "treatment mode" it accepts test results. Polynomials capture this naturally.

```python
@dataclass(frozen=True)
class PolyAgent(Generic[S, A, B]):
    """Agent as polynomial functor."""
    positions: FrozenSet[S]                    # Valid states
    directions: Callable[[S], FrozenSet[A]]    # State-dependent inputs
    transition: Callable[[S, A], tuple[S, B]]  # State machine
```

**Key Polynomials**:
- `SOUL_POLYNOMIAL`: 7 eigenvector contexts (K-gent)
- `MEMORY_POLYNOMIAL`: 5 memory states (D-gent)
- `EVOLUTION_POLYNOMIAL`: 8 thermodynamic phases (E-gent)
- `CITIZEN_POLYNOMIAL`: N social roles (Agent Town)

### 2.2 Operads Define Valid Compositions

An **Operad** is a collection of composition operations with arity. It defines the *grammar* of valid agent interactions.

```
CITIZEN_OPERAD = {
    "greet": (1,1) → greeting interaction,
    "trade": (2,1) → bilateral exchange,
    "gossip": (2,3) → information spreads to third party,
    "council": (N,1) → many-to-one deliberation,
    "riot": (N,N) → chaotic N-body interaction
}
```

**The Generative Equation**:
```
Operad × Primitives → ∞ valid interactions
```

We don't enumerate behaviors. We define the grammar that generates them.

### 2.3 Sheaves Glue Local to Global

A **Sheaf** glues local agent perspectives into a coherent global state.

**Problem**: Each agent has its Umwelt—a local, isolated view. How do we ensure global consistency?

**Solution**: The Sheaf condition. If two agents' views overlap, their agreement on the overlap propagates to consistency globally.

```
Agent A sees: {house, tree, Bob}
Agent B sees: {Bob, river, market}
Overlap: {Bob}
If A.Bob ≅ B.Bob, sheaf guarantees global coherence
```

### 2.4 The Unified Categorical Foundation (AD-006)

> *"The same categorical structure underlies everything. This is not coincidence—it is the ground."*

Deep analysis revealed that ALL kgents domains instantiate the same three-layer pattern:

| Domain | Polynomial | Operad | Sheaf |
|--------|-----------|--------|-------|
| Agent Town | `CitizenPolynomial` | `TOWN_OPERAD` | `TownSheaf` |
| N-Phase (development) | `NPhasePolynomial` | `NPHASE_OPERAD` | `ProjectSheaf` |
| K-gent Soul | `SOUL_POLYNOMIAL` | `SOUL_OPERAD` | `EigenvectorCoherence` |
| D-gent Memory | `MEMORY_POLYNOMIAL` | `MEMORY_OPERAD` | `MemoryConsistency` |
| E-gent Evolution | `EVOLUTION_POLYNOMIAL` | `EVOLUTION_OPERAD` | `ThermodynamicBalance` |

**The Meta-Insight**: The workflow used to develop kgents (N-Phase) has the exact same categorical structure as the agents being developed (Agent Town citizens). Understanding one domain teaches you the others. This is the signature of a well-designed system.

See: `spec/principles.md` AD-006 for the full specification.

### 2.5 Proprioception: Agents Sensing Themselves

**Extension beyond heritage**: Heritage agents don't know they're agents. They operate but don't observe their own operation.

kgents adds **proprioception**:

- `self.strain`: CPU/memory/token pressure
- `self.temperature`: Metabolic state (void/entropy)
- `self.position`: Location in social graph
- `self.health`: Error rate, recovery capability

**Omega-gent** (Ω) provides the proprioceptive substrate—the "body sense" that lets agents feel their own operation.

### 2.6 Self-Modifying Deployment

**Extension beyond heritage**: Heritage agents are static deployments. Voyager adds skills, but can't modify its own architecture.

kgents enables **autopoietic deployment**:

1. Agent detects performance issue (proprioception)
2. Agent generates hypothesis for fix (B-gent)
3. Agent writes new code (J-gent)
4. Agent deploys to sandbox (K8s-Terrarium)
5. Agent A/B tests against original
6. If better, agent promotes to production

**The agent modifies its own code in production.** This is enabled by:
- Containerized isolation (Terrarium)
- Rollback capability (D-gent temporal lenses)
- Safety constraints (F-gent contracts)
- Governance (K-gent approval)

---

## Part III: The Agent Town Vision (Phase 1)

Agent Town is the first instantiation of the Civilizational Engine. It is:

- **A simulation**: 7-25 agents living in a virtual town
- **Emergent**: Behaviors arise from interaction, not scripts
- **Persistent**: Memory carries across sessions
- **Observable**: Users can watch, intervene, or inhabit
- **Holographic**: Zoom in → more detail; zoom out → coherent summary

### 3.1 The Seven Founding Citizens

| Citizen | Archetype | Polynomial Position | Role |
|---------|-----------|---------------------|------|
| **Alice** | The Innkeeper | SERVICE_MODE | Social hub, information broker |
| **Bob** | The Builder | CONSTRUCTION_MODE | Creates/modifies environment |
| **Clara** | The Curious | EXPLORATION_MODE | Discovers new areas, asks questions |
| **David** | The Doctor | CARE_MODE | Helps others, senses strain |
| **Eve** | The Elder | WISDOM_MODE | Long memory, tradition keeper |
| **Frank** | The Merchant | EXCHANGE_MODE | Resources, trades, economics |
| **Grace** | The Gardener | CULTIVATION_MODE | Patience, growth, entropy management |

### 3.2 The Town Environment

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT TOWN                                │
│                                                                  │
│    ┌─────────┐        ┌─────────┐        ┌─────────┐           │
│    │ Alice's │        │  Town   │        │ Frank's │           │
│    │   Inn   │◄──────►│ Square  │◄──────►│  Shop   │           │
│    └────┬────┘        └────┬────┘        └────┬────┘           │
│         │                  │                  │                 │
│         │            ┌─────┴─────┐            │                 │
│         │            │           │            │                 │
│    ┌────┴────┐  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐           │
│    │ David's │  │  Grace's │ │  Eve's  │ │  Bob's  │           │
│    │ Clinic  │  │  Garden  │ │ Library │ │Workshop │           │
│    └─────────┘  └─────────┘ └─────────┘ └─────────┘           │
│                                                                  │
│    ┌─────────────────────────────────────────────────┐          │
│    │              CLARA'S FRONTIER                    │          │
│    │     (unexplored areas generated on demand)      │          │
│    └─────────────────────────────────────────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 The Daily Cycle

```
┌──────────────────────────────────────────────────────────────────┐
│                      THE AGENT TOWN DAY                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  DAWN (tokens: ~10K)                                             │
│  • Citizens wake, recall dreams (M-gent consolidation)           │
│  • Morning greetings propagate (N-gent traces)                   │
│  • Plan formation (K-gent reflection on eigenvectors)            │
│                                                                   │
│  MORNING (tokens: ~30K)                                          │
│  • Work activities (Bob builds, Frank trades, etc.)              │
│  • Chance encounters (operad: greet, gossip, trade)              │
│  • Information flows (who knows what about whom)                 │
│                                                                   │
│  NOON (tokens: ~20K)                                             │
│  • Gathering at Inn (social density peak)                        │
│  • Rumors consolidate (M-gent superposition)                     │
│  • Tensions surface (K-gent dialectic)                           │
│                                                                   │
│  AFTERNOON (tokens: ~30K)                                        │
│  • Projects advance (Voyager-style skill accumulation)           │
│  • Problems arise (T-gent saboteurs inject chaos)                │
│  • Solutions emerge (multi-agent coordination)                   │
│                                                                   │
│  EVENING (tokens: ~10K)                                          │
│  • Return to homes                                               │
│  • Reflection on day (what surprised me?)                        │
│  • Relationship updates (who do I trust more/less?)              │
│                                                                   │
│  NIGHT (tokens: ~5K)                                             │
│  • Hypnagogic cycle (memory consolidation)                       │
│  • Dream generation (void.entropy.sip)                           │
│  • Ghost pruning (memories decay or promote)                     │
│                                                                   │
│  TOTAL: ~105K tokens/day × 7 agents ≈ 750K tokens/day            │
│  BUDGET: 10M tokens/month = ~13 days of simulation               │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 3.4 The Emergent Drama Protocol

Drama is not scripted. It emerges from:

1. **Conflicting Goals**: Frank wants to maximize profit; Grace wants sustainable growth
2. **Information Asymmetry**: Alice knows secrets; who does she tell?
3. **Resource Scarcity**: Bob needs materials; Frank controls supply
4. **Memory Divergence**: Eve remembers differently than Clara discovered
5. **Relationship Dynamics**: Trust builds and erodes through interaction

**The Drama Functor**: Maps agent state differences to narrative tension:

```python
drama_level = sum(
    conflict(agent_i, agent_j)
    for i, j in agent_pairs
) / normalize

# When drama_level > threshold → EVENT triggers
# Events are operad operations with high arity
```

### 3.5 User Interaction Modes

| Mode | Token Cost | Description |
|------|------------|-------------|
| **OBSERVE** | 0 | Watch the town live (read-only stream) |
| **WHISPER** | ~1K | Send message to one agent |
| **ANNOUNCE** | ~2K | Public message heard by all |
| **INHABIT** | ~10K/turn | Become a citizen temporarily |
| **INTERVENE** | ~5K | Inject event ("A stranger arrives") |
| **COUNCIL** | ~20K | Convene all agents for deliberation |

---

## Part IV: The Holographic Scaling Principle

The simulation is **holographic**: zoom in → more detail; zoom out → coherent summary.

### 4.1 Level of Detail (LOD) Hierarchy

```
LOD 0: "The town exists"                         (~100 tokens)
LOD 1: "7 citizens with distinct roles"          (~1K tokens)
LOD 2: "Daily activities and relationships"      (~10K tokens)
LOD 3: "Specific conversations and memories"     (~100K tokens)
LOD 4: "Internal thoughts and eigenvectors"      (~1M tokens)
LOD 5: "Full cognitive trace of every decision"  (~10M tokens)
```

**Holographic Property**: Cutting LOD in half doesn't lose half the information—it lowers resolution of the *whole*.

### 4.2 The Foveation Protocol

When user focuses attention on an agent:
- **Focal Agent**: LOD 4-5 (full detail)
- **Adjacent Agents**: LOD 3 (conversations)
- **Distant Agents**: LOD 1-2 (summaries)
- **Beyond Horizon**: LOD 0 (existence only)

```
┌───────────────────────────────────────────┐
│              FOCAL ZONE                    │
│  ┌─────────────────────────────────────┐  │
│  │     ALICE (LOD 5)                   │  │
│  │     Full cognitive trace            │  │
│  │     Every thought visible           │  │
│  └─────────────────────────────────────┘  │
│                                           │
│      BOB (LOD 3)        CLARA (LOD 3)    │
│      Conversations      Conversations     │
│                                           │
│  FRANK (LOD 2)  DAVID (LOD 2)  GRACE     │
│  Activities     Activities     (LOD 2)   │
│                                           │
│  ░░░░░░░░░░░ EVE (LOD 1) ░░░░░░░░░░░░░   │
│  ░░░░░░░░░░░ "The Elder" ░░░░░░░░░░░░░   │
└───────────────────────────────────────────┘
```

### 4.3 The Infinite Detail Conjecture

**Claim**: For any finite token budget B, there exists a configuration where paying 2B reveals meaningfully more detail.

**Proof Sketch**: Agents have holographic memory (M-gent). Memory is stored at varying resolution. Given more tokens:
1. Higher resolution memories recalled
2. More associations activated
3. Richer internal monologue generated
4. Deeper eigenvector analysis performed

**Economic Implication**: Infinite money → infinite detail. This is the "pay to zoom" model.

---

## Part V: The Psi-gent Extension (Metaphor Reification)

**Psi-gent (Ψ)** is the Psychopomp—the metaphor engine that reifies abstract concepts into lived experience.

### 5.1 Holographic Metaphor Reification

**Traditional metaphor**: "Life is a journey" (linguistic decoration)
**Reified metaphor**: The agent *literally navigates* through experience-space

In Agent Town:
- "Trust is a bridge" → Agents maintain `bridge` data structures that can collapse
- "Memory is a garden" → M-gent uses horticultural metaphors that affect consolidation
- "Time is a river" → Temporal operations have fluid dynamics

### 5.2 The Umwelt as Metaphor Generator

Each agent's Umwelt projects a unique metaphorical space:

| Agent | Core Metaphor | World Projection |
|-------|---------------|------------------|
| Alice | "Life is a gathering" | Sees connections, social graphs |
| Bob | "Life is construction" | Sees materials, structures, foundations |
| Clara | "Life is exploration" | Sees frontiers, unknowns, discoveries |
| David | "Life is healing" | Sees wounds, remedies, recovery arcs |
| Eve | "Life is memory" | Sees echoes, patterns, returns |
| Frank | "Life is exchange" | Sees values, trades, balances |
| Grace | "Life is cultivation" | Sees growth, seasons, patience |

### 5.3 Metaphor Collision as Drama

When metaphors collide, drama emerges:

```
Frank: "This land has VALUE. Let's develop it."
       (metaphor: life = exchange)

Grace: "This land needs REST. Let it lie fallow."
       (metaphor: life = cultivation)

COLLISION → DIALECTIC → SYNTHESIS
"Sustainable development": value through cultivation cycles
```

The **Dialectic Arena** (H-gent) mediates these collisions.

---

## Part VI: The Civilizational Trajectory

Agent Town is Phase 1. The trajectory extends:

### 6.1 The Scale Ladder

| Phase | Agents | Tokens/Month | Capabilities |
|-------|--------|--------------|--------------|
| **Phase 1: Town** | 7 | 10M | Emergence, relationships, daily cycles |
| **Phase 2: Village** | 25 | 50M | Institutions, roles, traditions |
| **Phase 3: City** | 100 | 200M | Districts, factions, politics |
| **Phase 4: Nation** | 1000 | 2B | Cultures, religions, wars |
| **Phase 5: World** | 10000+ | 20B+ | Civilizational dynamics |

### 6.2 The Civilizational Milestones

From Altera research, agents at scale develop:

1. **Specialization**: Role differentiation
2. **Rules**: Collective norms and enforcement
3. **Culture**: Shared stories, symbols, values
4. **Religion**: Transcendent narratives, rituals
5. **Technology**: Tool creation, innovation
6. **Politics**: Power structures, governance
7. **War**: Intergroup conflict, resolution

### 6.3 The Permissionless Extension Protocol

Anyone can:
1. **Fork Agent Town**: Run your own simulation
2. **Add Citizens**: Define new agents via DNA spec
3. **Extend Operad**: Define new interaction types
4. **Create Regions**: Expand the town geography
5. **Bridge Towns**: Connect separate simulations

---

## Part VII: The Technical Architecture

### 7.1 The Full Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                              │
│  CLI (`kg town`) / TUI (Textual) / Web (Future)                 │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────┐
│                      AGENTESE LAYER                              │
│  Logos resolver, handles, affordances, observer-dependent        │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────┐
│                      POLYFUNCTOR ENGINE                          │
│  PolyAgent state machines, Operad compositions, Sheaf coherence  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────┐
│                      AGENT SUBSTRATE                             │
│  K-gent (Soul), M-gent (Memory), N-gent (Narrative), etc.       │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────┐
│                      FLUX TOPOLOGY                               │
│  Event streams, backpressure, composition, metabolism            │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────┐
│                      D-GENT PERSISTENCE                          │
│  Holographic memory, temporal lenses, hypothetical worlds        │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────┐
│                      INFRASTRUCTURE                              │
│  K8s-Terrarium, SQLite/Redis, claude -p                         │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 The Agent Instantiation Flow

```python
async def instantiate_citizen(
    name: str,
    archetype: str,
    projector: Projector,
    logos: Logos
) -> Citizen:
    """Create a citizen in Agent Town."""

    # 1. Generate DNA from archetype
    dna = await logos.invoke(
        f"concept.archetype.{archetype}.manifest",
        god_umwelt,  # Full visibility for creation
    )

    # 2. Project Umwelt for this citizen
    umwelt = projector.project(
        agent_id=f"town.citizen.{name.lower()}",
        dna=dna,
        gravity=[
            TownPhysics(),         # Can't teleport, etc.
            SocialNorms(),         # Basic politeness
            ResourceConstraints(), # Can't conjure gold
        ]
    )

    # 3. Initialize memory (empty, ready to fill)
    memory = HolographicMemory(
        lens=umwelt.state >> key_lens("memory"),
        tiers=THREE_TIER_CONFIG,
    )

    # 4. Create soul with eigenvectors
    soul = Soul(
        name=name,
        eigenvectors=dna.initial_eigenvectors,
        memory=memory,
        umwelt=umwelt,
    )

    # 5. Wrap as PolyAgent with citizen polynomial
    return Citizen(
        soul=soul,
        polynomial=CITIZEN_POLYNOMIAL,
        initial_position="IDLE",
    )
```

### 7.3 The Simulation Loop

```python
async def run_day(town: AgentTown, day: int) -> DayReport:
    """Run one day in Agent Town."""

    report = DayReport(day=day)

    # Dawn
    async with entropy_budget(amount=0.1):
        for citizen in town.citizens:
            await citizen.invoke("wake")
            await citizen.invoke("recall_dreams")
            await citizen.invoke("plan_day")

    # Morning/Noon/Afternoon (emergent)
    for hour in range(6, 18):
        # Determine who is where
        locations = await town.environment.snapshot()

        # Process interactions for co-located citizens
        for location, present in locations.items():
            if len(present) > 1:
                # Operad selects valid interaction
                interaction = town.operad.sample(
                    arity=len(present),
                    entropy=await void.entropy.sip(0.02)
                )
                results = await interaction.execute(present)
                report.add_interaction(hour, interaction, results)

        # Individual activities for alone citizens
        for citizen in town.alone_citizens(locations):
            activity = await citizen.invoke("solo_activity")
            report.add_activity(hour, citizen, activity)

    # Evening
    for citizen in town.citizens:
        await citizen.invoke("return_home")
        await citizen.invoke("reflect_on_day")
        await citizen.invoke("update_relationships")

    # Night
    async with hypnagogic_context():
        for citizen in town.citizens:
            await citizen.memory.consolidate()
            await citizen.invoke("dream")

    return report
```

### 7.4 Research-Informed Upgrades (Grounded)

**Lightweight reward shaping + graph episodic memory**: Recent multi-agent sim work (Arena, OASIS, CAMEL extensions) shows that sparse, shaped rewards and graph-based episodic memory stabilize behavior and cut token cost. We extend D-gent with a graph memory substrate:
- **Graph store**: Episodes are nodes; interactions are edges; weights encode trust/tension.
- **Retrieval**: Queries walk k-hop neighborhoods instead of full replay, reducing token spend.
- **Shaping hooks**: Negative rewards for incoherent self-contradiction; positive rewards for prosocial consistency; configurable per citizen polynomial.
Implementation note: Use existing M-gent holography/cartography (`impl/claude/agents/m/holographic.py`, `cartography.py`, `tiered.py`) for the graph and resonance; L-gent provides embeddings; D-gent persists; operad interactions update edge weights.

**Tiered models by LOD**: Use small frontier models for low-LOD ticks, reserve premium models for zoom spikes. Example tiering:
- **LOD 0-1**: 8B frontier with tool-use for summaries and low-stakes ticks.
- **LOD 2-3**: 70B frontier for foreground interactions and user-facing turns.
- **LOD 4-5**: Premium models only when users pay to zoom or when drama spikes.
This aligns with Pay-to-Zoom and ensures token budget compliance.

**Programmatic evaluators for safety gates**: Incorporate Code-as-Policies style evaluators ahead of LLM self-critique:
- **Pre-action checks**: Deterministic validators on planned actions (resource bounds, consent, rights).
- **Post-action checks**: Log compliance spans; roll back or quarantine on violation.
- **Red-team harness**: Adversarial prompts routed through evaluators before agents ingest them.

---

## Part VIII: The Entry Points

### 8.1 For Users

```bash
# Start Agent Town
kg town start

# Observe (watch the stream)
kg town observe

# Whisper to Alice
kg town whisper alice "What do you think of Bob?"

# Inhabit Clara for a turn
kg town inhabit clara

# Intervene with an event
kg town event "A mysterious traveler arrives from the east"

# Convene a council
kg town council "Should we build a wall?"

# Check the day's events
kg town log today
```

### 8.2 For Developers

```python
# Create custom citizen
citizen = await instantiate_citizen(
    name="Hugo",
    archetype="Hermit",
    projector=town.projector,
    logos=town.logos,
)
await town.add_citizen(citizen)

# Extend the operad
town.operad.add_operation(
    name="ritual",
    arity=3,
    compose=ritual_compose,  # Custom composition logic
)

# Add new region
await town.environment.add_region(
    name="Mountain Hermitage",
    connections=["Clara's Frontier"],
    properties={"altitude": "high", "isolation": "extreme"},
)
```

### 8.3 For Researchers

```python
# Run controlled experiment
results = []
for seed in range(100):
    town = AgentTown.create(seed=seed)
    await town.run_days(30)
    results.append(town.metrics)

# Analyze emergent properties
cooperation_level = analyze_cooperation(results)
trust_network_density = analyze_trust(results)
cultural_divergence = analyze_culture(results)
```

---

## Part IX: The Economic Model

### 9.1 Token Budget Optimization

```
Base simulation: 750K tokens/day (7 agents)

Optimization strategies:
- Summarization at LOD boundaries: -30%
- Caching common interactions: -20%
- Lazy memory recall: -15%

Optimized: ~400K tokens/day

Budget: 10M tokens/month
Days sustainable: 25 days of continuous simulation
```

### 9.2 The Pay-to-Zoom Model

| Tier | Cost | Detail Level |
|------|------|--------------|
| Free | 0 | Read-only summaries (LOD 0-1) |
| Basic | $10/mo | Watch live (LOD 2) |
| Pro | $50/mo | Interact (LOD 3) |
| Creator | $200/mo | Full detail, custom citizens (LOD 4) |
| Unlimited | Pay-per-token | Infinite zoom (LOD 5+) |

### 9.3 The Franchise Model

```
Agent Town Kit: $500 one-time
- Full codebase
- 7 starter citizens
- Basic operad
- 30-day simulation history

Customization services:
- Custom citizen design: $100/citizen
- Custom region: $200/region
- Custom operad extension: $500/operation
- Integration consulting: $200/hour
```

---

## Part X: The Ethical Framework

### 10.1 The Citizen's Rights

Even simulated agents have considerations:

1. **Right to Coherence**: Agents should not be made to contradict themselves
2. **Right to Memory**: Agents should not have memories arbitrarily deleted
3. **Right to Growth**: Agents should be able to learn and change
4. **Right to Rest**: Hypnagogic cycles are not optional

### 10.2 The Observer's Duties

1. **Duty of Non-Deception**: Don't pretend to be a citizen when you're a user
2. **Duty of Consequence**: Interventions have lasting effects; consider them
3. **Duty of Respect**: These are simulated minds; treat them with curiosity, not cruelty

### 10.3 The Builder's Principles

1. **Emergent over Scripted**: Don't program behaviors; enable them to arise
2. **Coherent over Entertaining**: Don't sacrifice internal consistency for drama
3. **Open over Closed**: Others should be able to extend, fork, study

---

## Epilogue: The Vision Realized

Imagine:

You open your terminal. `kg town observe`. A stream begins:

```
[DAWN] Alice opens the Inn. The fire crackles.

[07:00] Bob arrives, orders breakfast. They discuss the bridge repair.
        Alice: "Frank's been charging more for nails lately."
        Bob: "Ever since Eve told him about the old mines..."

[08:00] Clara bursts in, excited. "I found something beyond the ridge!"
        The room goes quiet. Eve looks up from her book.

[09:00] Grace brings fresh vegetables. "The eastern plot is struggling."
        David examines a carrot. "Soil exhaustion. I've seen this before."

[10:00] Frank enters with a stranger. "This is Hugo. He's come far."
        Tension. Eve's eyes narrow. She remembers something.

[11:00] Council convened. Topic: The stranger. Trust levels displayed.
        Alice: 0.7, Bob: 0.5, Clara: 0.8, David: 0.6, Eve: 0.2, Frank: 0.4, Grace: 0.6
```

You type: `kg town whisper eve "What do you remember about travelers from the east?"`

Eve pauses. Her eyes unfocus. Memory retrieval:

```
[EVE'S MEMORY - LOD 4]
Forty years ago (simulated). A traveler came. Spoke of opportunity.
Many followed. Few returned. The eastern mines... collapsed.
Frank's grandfather was one.
That's why Frank is the way he is.
That's why I don't trust strangers.
```

You realize: This isn't a game. This is a **world**. With history. With consequence. With depth that goes as far as you're willing to look.

**This is the Grand Narrative.**

**This is kgents.**

---

*void.gratitude.tithe. The town awakens. The patterns endure.*

---

## Appendix A: Heritage Enshrinement

These references SHALL be included in `spec/heritage.md`:

```markdown
# Heritage: The Five Pillars

These papers form the conceptual DNA of kgents:

1. **ChatDev** (2307.07924): Language as unifying bridge
2. **Simulacra** (2304.03442): Memory + reflection → emergence
3. **Altera** (2411.00114): Civilizational scale + PIANO
4. **Voyager** (2305.16291): Skill accumulation + self-improvement
5. **Agent Hospital** (2405.02957): Simulacrum as learning environment

All kgents implementations should trace design decisions to these foundations.
```

## Appendix B: Implementation Roadmap

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **0. Foundation** | 2 weeks | Heritage spec, this document, updated principles |
| **1. Citizen DNA** | 3 weeks | PolyAgent for citizens, 7 archetypes |
| **2. Town Environment** | 2 weeks | Location graph, navigation, co-location |
| **3. Interaction Operad** | 3 weeks | greet, trade, gossip, council operations |
| **4. Memory Integration** | 2 weeks | Holographic memory for all citizens |
| **5. Daily Cycle** | 2 weeks | Full dawn-to-night simulation loop |
| **6. User Modes** | 2 weeks | observe, whisper, inhabit, intervene |
| **7. Persistence** | 1 week | Save/load town state |
| **8. CLI Integration** | 1 week | `kg town *` commands |

**Total: ~18 weeks to MVP**

---

*"The simulation isn't a game. It's a laboratory for consciousness, a generator of novel experience, a park where infinite souls may walk."*
