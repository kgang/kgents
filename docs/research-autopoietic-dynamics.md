# Autopoietic Dynamics: Stigmergy and Language Games in the Causal Weave

> *"The Weave is not just a log of what happened. It is the soil from which the next thought grows."*

---
path: docs/research/autopoietic-dynamics
status: proposal
author: claude-opus-4.5
date: 2025-12-13
tags: [theory, stigmergy, wittgenstein, polyfunctor, thermodynamics, active-inference]
---

## 1. Executive Summary

Current multi-agent systems rely on **Message Passing** (Agent A mails a JSON packet to Agent B). This models a bureaucratic office.

This report proposes a shift to **Stigmergy** (Agent A modifies the environment; Agent B reacts to the modification). By treating the **Trace Monoid (The Weave)** as a physical environment, agents can coordinate complex behaviors without direct addressing, modeled mathematically as **Polynomial Language Games**.

We introduce:
- **The Wittgenstein Operator**: A functor that maps a sequence of Turns to a set of valid next-moves
- **The Pheromone Field**: Semantic gradients on the Trace that guide agent attention
- **The Accursed Share Protocol**: Thermodynamic expenditure as creative force
- **Active Inference Integration**: Agents as self-evidencing systems minimizing free energy

---

## 2. The Theoretical Gap

### 2.1 The Coordination Problem

In standard architectures (LangGraph, AutoGen), coordination is **Imperative**:
- *Orchestrator:* "You do X, then you do Y."
- *Fragility:* If the Orchestrator dies, the system halts. If the context window fills, the plan is lost.

### 2.2 The Stigmergic Solution

In nature (Termites, Ants), coordination is **Environmental**:
- *Termite A* drops a mud ball (Trace).
- *Termite B* sees the mud ball (Perception) and feels a statistical urge to drop another on top of it.
- *Result:* A cathedral (The Termite Mound) emerges without a blueprint.

**In kgents**:
- The **Trace Monoid** is the environment.
- The **Turn** is the mud ball.
- **Pheromones** are the semantic gradients left on the Trace.

Recent research confirms this approach: The Stigmergic multi-agent deep reinforcement learning (S-MADRL) framework implements stigmergic communication modeled as virtual pheromones, which locally encode traces of other agents' activities to enable indirect communication and foster cooperative behaviors.

---

## 3. Core Concepts

### 3.1 The Weave as Pheromone Field

We extend the `Turn` atom to include a **Semantic Gradient**.

```python
@dataclass
class Turn(Event):
    # ... existing fields from turn-gents spec ...
    id: str
    timestamp: float
    source: str
    type: TurnType
    input: Any
    output: Any
    state_before: Any
    state_after: Any
    entropy: float
    confidence: float

    # Stigmergic Properties
    pheromone: str       # e.g., "DEBUG_HEAT", "ARCH_TENSION", "CONSENSUS_PULL"
    intensity: float     # 0.0 to 1.0
    decay_rate: float    # How fast this signal fades in the Weave
    parent_id: str | None  # Causal dependency
```

When an agent projects its **Causal Cone** (via the Perspective Functor), it doesn't just see text. It sees the **Heatmap of Attention**.

| Agent | Perceives | Pheromone Type |
|-------|-----------|----------------|
| B-gent | Economic Heat | `COST_PRESSURE` |
| T-gent | Fragility Heat | `TEST_FAIL` |
| K-gent | Ethical Tension | `GOVERNANCE_FLAG` |
| A-gent | Architectural Stress | `REFACTOR_PULL` |

### 3.2 The Wittgenstein Operator (Meaning as Use)

Ludwig Wittgenstein argued that words do not have fixed definitions; they have "moves" in a "Language Game."

> "Language games establish three mutually reinforcing mechanisms: role fluidity enables models or agents to navigate diverse task spaces as both knowledge consumers and producers; reward variety embodies the 'reward is enough' hypothesis at metacognitive levels through pluralistic success criteria; and rule plasticity sustains open-ended growth through linguistic environment remodeling."

We formalize this using Spivak's **Polynomial Functors**.

#### The Polynomial Language Game

A **Language Game** is a Polynomial $P(y) = \sum_{s \in S} y^{E(s)}$

Where:
- $S$ = **Positions** (Valid states of the conversation/The Braid)
- $E(s)$ = **Directions** (Set of valid next Turns from state $s$)

```python
@dataclass(frozen=True)
class LanguageGame(Generic[S]):
    """
    Polynomial functor representation of valid conversational moves.

    Based on Spivak's polynomial functors for dynamical systems.
    """
    positions: FrozenSet[S]                    # Valid conversation states
    directions: Callable[[S], FrozenSet[TurnType]]  # State → valid moves

    def valid_moves(self, state: S) -> FrozenSet[TurnType]:
        """What moves are legal from this state?"""
        return self.directions(state)

    def is_legal(self, state: S, proposed_turn: Turn) -> bool:
        """Would this turn be a legal move?"""
        return proposed_turn.type in self.directions(state)
```

**The Wittgenstein Operator**:
$$W: Trace \to \{ValidTurns\}$$

If an agent attempts a Turn that is not in $E(s)$, the Weave **rejects** it. This is not an "Error"; it is an **Illegal Move**. This enforces protocol validity at the ontological level.

#### Connection to LGDL (Language-Game Description Language)

Recent AI research proposes LGDL—a framework that grounds AI in bounded "language-games" (like medical triage or contract review) rather than trying to master all of human language at once. This aligns perfectly with our approach: each agent genus operates within its own language game, with cross-genus interaction mediated by the Weave.

### 3.3 Active Inference: Agents as Self-Evidencing Systems

Karl Friston's **Free Energy Principle** provides the mathematical foundation for agent behavior:

> "Agents select policies for action that they believe will reduce uncertainty given their model. Policies are selected in active inference, estimating which policy promises the best reduction in future uncertainty."

In kgents terms:
- **Generative Model**: The agent's internal model of the Weave
- **Free Energy**: Surprise (negative log probability) of observations
- **Active Inference**: Selecting Turns that minimize expected free energy

```python
@dataclass
class ActiveInferenceAgent:
    """
    Agent as self-evidencing system under Free Energy Principle.
    """
    generative_model: GenerativeModel  # P(observations | hidden_states)

    async def select_turn(self, weave: Weave) -> Turn:
        """
        Select action that minimizes expected free energy.

        F = E_Q[log Q(s) - log P(o, s)]

        Where:
        - Q(s) is the agent's beliefs about hidden states
        - P(o, s) is the generative model
        """
        # Project causal cone
        perspective = weave.perspective(self.id)

        # Compute expected free energy for each possible turn
        candidate_turns = self.language_game.valid_moves(perspective.state)

        best_turn = min(
            candidate_turns,
            key=lambda t: self.expected_free_energy(t, perspective)
        )

        return best_turn

    def expected_free_energy(self, turn: Turn, context: Perspective) -> float:
        """
        G = E_Q[log Q(s') - log P(o', s')] + H[P(o'|s')]

        Balances:
        - Pragmatic value (achieving goals)
        - Epistemic value (reducing uncertainty)
        """
        # Pragmatic: Does this turn achieve goals?
        pragmatic = self.goal_divergence(turn, context)

        # Epistemic: Does this turn reduce uncertainty?
        epistemic = self.information_gain(turn, context)

        return pragmatic - epistemic  # Minimize pragmatic, maximize epistemic
```

### 3.4 The Accursed Share: Thermodynamics of Meaning

Georges Bataille's **General Economy** provides the meta-principle:

> "The accursed share is that excessive and non-recuperable part of any economy which must either be spent luxuriously and knowingly in the arts, in non-procreative sexuality, in spectacles and sumptuous monuments, or it is obliviously destined to an outrageous and catastrophic outpouring."

**In kgents**:
- **Information** is Order (Low Entropy)
- **Creation** requires Energy (Token Spend)
- **The Accursed Share**: The excess energy that *must* be expended

```python
@dataclass
class AccursedShareProtocol:
    """
    Thermodynamic expenditure management.

    Systems that are too efficient become rigid and fragile.
    We explicitly model and celebrate waste.
    """
    exploration_budget: float = 0.10  # 10% for "useless" exploration

    def compute_value(self, turn: Turn, structure_delta: float) -> float:
        """
        Value = ΔStructure / Entropy Spent

        If an agent burns 10k tokens but leaves the Weave unchanged,
        K-gent intervenes.
        """
        if turn.entropy == 0:
            return float('inf') if structure_delta > 0 else 0
        return structure_delta / turn.entropy

    async def inject_entropy(self, weave: Weave, temperature: float = 0.7):
        """
        void.entropy.sip: Random, high-temperature turns injected
        by Ψ-gent (Psychopomp) to shake the system out of local minima.
        """
        return await logos.invoke("void.entropy.sip", temperature=temperature)
```

---

## 4. Implementation: The Autopoietic Loop

We replace the traditional agent "Loop" with the **Stigmergic Cycle**.

### Step 1: The Environment Modifies the Agent

Instead of the Agent querying the Weave, the Weave **activates** the Agent based on pheromones.

```python
# impl/claude/agents/poly/stigmergy.py

@dataclass
class PheromoneField:
    """
    Computes the gradient of the Weave at the current Tip.

    Passive stigmergy: intensity calculated on read, not stored.
    """
    decay_constant: float = 0.1  # Per-turn decay

    def get_active_gradients(self, weave: Weave) -> dict[str, float]:
        """
        Sum intensities of recent Turns, applying temporal decay.

        Returns: {"BUG_FIX": 0.8, "REFACTOR": 0.2, "CONSENSUS": 0.5}
        """
        gradients: dict[str, float] = {}
        tip = weave.tip()

        for turn in weave.thread(tip.source):
            age = tip.timestamp - turn.timestamp
            decayed_intensity = turn.intensity * math.exp(-self.decay_constant * age)

            if turn.pheromone in gradients:
                gradients[turn.pheromone] += decayed_intensity
            else:
                gradients[turn.pheromone] = decayed_intensity

        return gradients

    def gradient_at(self, weave: Weave, pheromone: str) -> float:
        """Get specific pheromone intensity."""
        return self.get_active_gradients(weave).get(pheromone, 0.0)


class HiveMind:
    """
    The Heterarchical Scheduler.

    No fixed orchestrator. Agents wake based on environmental gradients.
    """
    agents: dict[str, PolyAgent]
    field: PheromoneField
    thresholds: dict[str, tuple[str, float]]  # pheromone -> (agent, threshold)

    async def tick(self, weave: Weave):
        """
        One tick of the stigmergic cycle.

        Agents are activated by pheromone gradients, not by orchestrator commands.
        """
        gradients = self.field.get_active_gradients(weave)

        # Activate agents based on gradients
        for pheromone, intensity in gradients.items():
            if pheromone in self.thresholds:
                agent_id, threshold = self.thresholds[pheromone]
                if intensity > threshold:
                    agent = self.agents[agent_id]
                    await agent.wake(weave, triggered_by=pheromone)

        # Also check for consensus requirements (Knot formation)
        if "CONSENSUS_REQUIRED" in gradients and gradients["CONSENSUS_REQUIRED"] > 0.9:
            await self.form_knot(weave)

    async def form_knot(self, weave: Weave):
        """
        Synchronization point: all relevant agents must participate.
        """
        participants = self.identify_knot_participants(weave)
        knot = await weave.synchronize(participants)
        return knot
```

### Step 2: The Agent Modifies the Environment

The Agent takes a Turn, depositing new structure and pheromones.

```python
class StigmergicAgent(PolyAgent[S, A, B]):
    """
    Agent that participates in stigmergic coordination.
    """

    async def take_turn(self, weave: Weave, input: A) -> B:
        """
        Execute turn and deposit pheromone trace.
        """
        # 1. Perceive: Project causal cone
        perspective = weave.perspective(self.id)

        # 2. Deliberate: Active inference to select action
        action = await self.deliberate(input, perspective)

        # 3. Act: Produce output
        output = await self.invoke(input)

        # 4. Resonate: Deposit turn with pheromone
        turn = Turn(
            id=generate_id(),
            timestamp=time.time(),
            source=self.id,
            type=self.classify_turn(action),
            input=input,
            output=output,
            state_before=perspective.state,
            state_after=self.state,
            entropy=self.compute_entropy(input, output),
            confidence=self.assess_confidence(output),
            pheromone=self.select_pheromone(action),
            intensity=self.compute_intensity(action),
            decay_rate=self.default_decay_rate,
            parent_id=perspective.tip_id
        )

        weave.append(turn)
        return output

    def select_pheromone(self, action: A) -> str:
        """
        Map action to pheromone type.

        This is where the agent's genus determines its stigmergic signature.
        """
        # Genus-specific mapping
        pheromone_map = {
            TurnType.ACTION: "EFFECT_TRACE",
            TurnType.SPEECH: "COMMUNICATION_MARKER",
            TurnType.THOUGHT: "REASONING_PATH",
            TurnType.YIELD: "CONSENSUS_REQUIRED",
            TurnType.SILENCE: None  # No pheromone
        }
        return pheromone_map.get(self.classify_turn(action), "GENERIC_TRACE")
```

### Step 3: Collapse (The Knot)

When heat dissipates (tests pass, consensus reached), agents tie a **Knot**.

```python
@dataclass
class KnotEvent(Event):
    """
    Synchronization barrier in the Weave.

    Multiple threads merge at a Knot before continuing.
    """
    participants: FrozenSet[str]  # Agent IDs
    dependencies: FrozenSet[str]  # Turn IDs that must complete
    consensus_type: str  # "UNANIMOUS", "MAJORITY", "QUORUM"
    resolution: Any  # The agreed-upon state

    def is_satisfied(self, weave: Weave) -> bool:
        """All dependencies must be in the Weave."""
        return all(
            weave.contains(dep_id) for dep_id in self.dependencies
        )
```

---

## 5. Case Study: The Autopoietic Refactor

How this looks in the **Turn-Based Architecture**:

```
1. INJECTION
   Human → world.codebase.refactor
   │
   ▼
2. SEEDING
   Turn deposits ARCH_TENSION pheromones on specific files
   │
   ├─────────────────┬────────────────────┐
   ▼                 ▼                    ▼
3. SWARMING (Parallel)
   L-gent wakes      A-gent wakes        C-gent wakes
   (ARCH_TENSION)    (MAP_DATA)          (BLUEPRINT)
   │                 │                    │
   ▼                 ▼                    ▼
   Maps deps         Proposes arch       Writes code
   Deposits          Deposits            Deposits
   MAP_DATA          BLUEPRINT           CODE_CHANGE
   │                 │                    │
   └────────┬────────┴────────────────────┘
            │
4. FRICTION ▼
   C-gent introduces bug
   BUG_HEAT spikes (intensity: 1.0)
   │
   ▼
5. RECRUITMENT
   T-gent wakes (triggered by BUG_HEAT > 0.7)
   Generates Trace of failure
   Deposits TEST_FAIL pheromone
   │
   ▼
6. SUBLATION
   A-gent sees conflict: BLUEPRINT vs TEST_FAIL
   Issues Synthesis Turn
   Deposits RESOLUTION marker
   │
   ▼
7. COOLING
   All tasks complete
   Heat fades (exponential decay)
   System returns to Ground state
```

---

## 6. Integration with Existing M-gent Architecture

### 6.1 Holographic Memory + Stigmergic Traces

The existing M-gent holographic memory model is **complementary** to stigmergic traces:

| Aspect | Holographic Memory | Stigmergic Traces |
|--------|-------------------|-------------------|
| **Storage** | Distributed interference pattern | Event DAG (Weave) |
| **Retrieval** | Resonance/reconstruction | Causal cone projection |
| **Degradation** | Resolution loss (graceful) | Temporal decay (pheromones) |
| **Purpose** | Long-term knowledge | Short-term coordination |

```python
class UnifiedMemory:
    """
    M-gent memory combining holographic storage with stigmergic traces.
    """
    holographic: HolographicMemory  # Long-term, content-addressable
    weave: Weave                     # Episodic, causally-ordered
    pheromone_field: PheromoneField  # Dynamic gradients

    async def recall(self, cue: Concept, context: Perspective) -> Recollection:
        """
        Unified recall combining:
        1. Holographic resonance (semantic)
        2. Causal cone (episodic)
        3. Pheromone gradients (attention)
        """
        # 1. Holographic: Find resonant patterns
        semantic_matches = await self.holographic.retrieve(cue)

        # 2. Causal: Get causally relevant events
        causal_events = self.weave.thread(context.agent_id)

        # 3. Stigmergic: Weight by current gradients
        gradients = self.pheromone_field.get_active_gradients(self.weave)

        # Combine with foveation principle
        return await self.foveate(semantic_matches, causal_events, gradients)
```

### 6.2 Bi-Temporal Model from Zep Research

Adopting the bi-temporal model from Zep:

```python
@dataclass(frozen=True)
class BiTemporalTurn(Turn):
    """
    Turn with two time dimensions.

    t_event: When did this happen in the world?
    t_known: When did we learn about it?

    This enables:
    - "What did I believe on date X?"
    - "When did my understanding change?"
    - Integration with N-gent witness/trace
    """
    t_event: float      # Timeline T (world time)
    t_known: float      # Timeline T' (knowledge time)
    t_invalidated: float | None = None  # When superseded

    def is_valid_at(self, t: float) -> bool:
        """Was this turn's information valid at time t?"""
        return self.t_event <= t and (
            self.t_invalidated is None or t < self.t_invalidated
        )
```

---

## 7. The Wittgenstein-Spivak Bridge

### 7.1 Polynomial Functors as Language Games

David Spivak's polynomial functors provide the mathematical infrastructure:

> "A polynomial functor is a collection of elements called positions and, for each position, a collection of elements called directions."

This maps directly to Wittgenstein:
- **Positions** = States of the language game (conversation context)
- **Directions** = Valid moves (legal utterances/actions)

```python
from typing import Protocol, TypeVar, Generic

S = TypeVar('S')  # State type
A = TypeVar('A')  # Action type

class PolynomialLanguageGame(Protocol[S, A]):
    """
    P(y) = Σ_{s ∈ positions} y^{directions(s)}

    The language game as polynomial functor.
    """

    @property
    def positions(self) -> FrozenSet[S]:
        """Valid conversation states."""
        ...

    def directions(self, s: S) -> FrozenSet[A]:
        """Valid actions from state s."""
        ...

    def transition(self, s: S, a: A) -> S:
        """State after taking action a from s."""
        ...
```

### 7.2 Morphisms in the Game Category

Agent interactions are morphisms between language games:

```python
class GameMorphism(Generic[S1, A1, S2, A2]):
    """
    A morphism between language games.

    f: Game1 → Game2

    Maps positions to positions, directions to directions,
    preserving the game structure.
    """
    position_map: Callable[[S1], S2]
    direction_map: Callable[[S1, A1], A2]

    def is_valid(self, game1: PolynomialLanguageGame[S1, A1],
                       game2: PolynomialLanguageGame[S2, A2]) -> bool:
        """
        Verify functoriality: diagram must commute.
        """
        for s1 in game1.positions:
            s2 = self.position_map(s1)

            # Directions must map correctly
            for a1 in game1.directions(s1):
                a2 = self.direction_map(s1, a1)
                if a2 not in game2.directions(s2):
                    return False

        return True
```

---

## 8. Strategic Recommendations

### 8.1 Immediate (Next Sprint)

1. **Add `pheromone` field to Turn**: Zero-cost metadata field that unlocks swarm behavior.

2. **Implement PheromoneField class**: Passive intensity calculation on read.

3. **Define genus-specific pheromone types**:
   ```python
   PHEROMONE_REGISTRY = {
       "A-gent": ["ARCH_TENSION", "DESIGN_MARKER"],
       "B-gent": ["COST_PRESSURE", "BUDGET_WARNING"],
       "T-gent": ["TEST_FAIL", "COVERAGE_GAP"],
       "K-gent": ["GOVERNANCE_FLAG", "ETHICAL_CONCERN"],
       "L-gent": ["LINEAGE_LINK", "CONCEPT_CLUSTER"],
       "M-gent": ["MEMORY_HOT", "RECALL_TRIGGER"],
   }
   ```

### 8.2 Medium-Term (Next Month)

4. **Implement HiveMind Scheduler**: Replace simple `while True` loop with gradient-based scheduler.

5. **Formalize GameRules via Operads**: Define `PolyAgent` states by **Legal Moves**:
   - "You cannot output Code before you output a Plan"
   - "YIELD must follow high-entropy ACTION"

6. **Integrate Active Inference**: Agents select turns by minimizing expected free energy.

### 8.3 Long-Term (Architecture)

7. **Language Game Algebras**: Each agent genus has its own language game; the Weave is the arena where games interact.

8. **Accursed Share Monitoring**: K-gent tracks value production vs. entropy expenditure, intervening when ratio drops.

9. **Stigmergic UI**: Visualize pheromone heatmaps in dashboard, showing where "attention" flows.

---

## 9. References

### Academic Sources

1. **Grassé, P. P. (1959).** *"La reconstruction du nid et les coordinations interindividuelles chez Bellicositermes natalensis et Cubitermes sp."* (Origin of Stigmergy).

2. **Wittgenstein, L. (1953).** *"Philosophical Investigations."* (Language Games).

3. **Friston, K. (2010).** *"The Free-Energy Principle: A Unified Brain Theory?"* (Active Inference).

4. **Bataille, G. (1949).** *"The Accursed Share: An Essay on General Economy."*

5. **Spivak, D. I. & Niu, N. (2024).** *"Polynomial Functors: A Mathematical Theory of Interaction."* Cambridge University Press.

6. **Mazurkiewicz, A. (1977).** *"Concurrent Program Schemes and their Interpretations."* (Trace Theory).

7. **Parunak, H. V. D. (2005).** *"A Survey of Environments and Mechanisms for Human-Human Stigmergy."*

### Recent Research (2024-2025)

8. **Salman, Garzón Ramos & Birattari (2024).** *"Automatic design of stigmergy-based behaviours for robot swarms."* Communications Engineering.

9. **S-MADRL Framework (2025).** *"Deep reinforcement learning for multi-agent coordination."* Artificial Life and Robotics.

10. **Oxford Talk (Nov 2024).** Sarah Rees on Step Trace Monoids for concurrent computation.

11. **LICS '24.** *"An expressively complete local past propositional dynamic logic over Mazurkiewicz traces."*

12. **arxiv:2501.18924.** *"Language Games as the Pathway to Artificial Superhuman Intelligence."*

### Web Sources

- [Stigmergy in Multi-Agent Systems](https://www.nature.com/articles/s44172-024-00175-7)
- [Polynomial Functors Book](https://toposinstitute.github.io/poly/poly-book.pdf)
- [Active Inference MIT Press](https://direct.mit.edu/books/oa-monograph/5299/Active-InferenceThe-Free-Energy-Principle-in-Mind)
- [Wittgenstein and AI](https://arxiv.org/html/2501.18924)
- [The Accursed Share](https://en.wikipedia.org/wiki/The_Accursed_Share)
- [Trace Theory Introduction](https://www.mimuw.edu.pl/~sl/teaching/22_23/TW/LITERATURA/book-of-traces-intro.pdf)

---

*"We do not build the agents; we build the physics. The agents build themselves."*
