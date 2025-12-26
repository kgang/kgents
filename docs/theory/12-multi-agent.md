# Chapter 12: Multi-Agent Coordination

> *"No man is an island, entire of itself."*
> — John Donne

---

## 12.1 The Coordination Problem

Consider a system with multiple agents:

- Agent A reasons about physics
- Agent B reasons about economics
- Agent C reasons about ethics

They must answer: "Should we build this technology?"

Each agent has partial information and specialized expertise. No single agent can answer alone. Yet simply combining their outputs—voting, averaging, concatenating—fails in subtle ways.

**Why simple aggregation fails**:

1. **Voting ignores expertise**: A majority of non-experts can outvote an expert
2. **Averaging destroys structure**: The average of "yes" and "no" isn't meaningful
3. **Concatenation lacks synthesis**: A list of opinions isn't a decision

The coordination problem asks: *When can multiple agents' reasoning combine into coherent group reasoning, and how?*

This chapter develops the categorical machinery for multi-agent coordination. Sheaves handle consensus; cocones handle disagreement; practical protocols approximate both.

---

## 12.2 Sheaves: The Architecture of Consensus

We introduced sheaves in Chapter 5 for single-agent coherence. Here we apply them to multi-agent consensus.

### Review: What is a Sheaf?

A sheaf is data that:
1. Lives locally (each agent has its own piece)
2. Restricts consistently (projecting from larger to smaller groups preserves structure)
3. Glues uniquely (compatible local pieces determine a unique global piece)

```
       Global Belief
            │
    ┌───────┼───────┐
    │       │       │
    ▼       ▼       ▼
  Agent₁  Agent₂  Agent₃    ← Local beliefs
    │       │       │
    └───┬───┴───┬───┘
        │       │
        ▼       ▼
    Overlap₁₂  Overlap₂₃    ← Compatibility conditions
```

### Definition 12.1 (Agent Belief Sheaf)

Let A = {A₁, ..., Aₙ} be a set of agents. A **belief sheaf** over A is:

- For each subset S ⊆ A, a set Belief(S) of possible group beliefs
- For each S' ⊆ S, a restriction map ρ_{S→S'} : Belief(S) → Belief(S')

Subject to:
- **Identity**: ρ_{S→S} = id
- **Transitivity**: ρ_{S'→S''} ∘ ρ_{S→S'} = ρ_{S→S''}

This is a **sheaf** if it additionally satisfies:
- **Locality**: If beliefs agree on all smaller subgroups, they're equal
- **Gluing**: Compatible beliefs on a cover uniquely determine a global belief

### Example 12.2 (Expert Panel)

Agents: {Physics, Economics, Ethics}

```
Belief({Physics}) = physical feasibility assessments
Belief({Economics}) = economic impact projections
Belief({Ethics}) = ethical evaluations
Belief({Physics, Economics}) = techno-economic analyses
Belief({Physics, Ethics}) = safety assessments
Belief({Economics, Ethics}) = social cost analyses
Belief({Physics, Economics, Ethics}) = comprehensive recommendations
```

The sheaf condition: If Physics and Economics agree on their techno-economic overlap, and Economics and Ethics agree on social costs, then their individual assessments glue to a coherent group recommendation.

---

## 12.3 The Sheaf Condition in Detail

### 12.3.1 Restriction: Global to Local

**Definition 12.3**: Given a global belief b ∈ Belief(S) and a subgroup S' ⊆ S, the **restriction** ρ_{S→S'}(b) projects b to what S' would believe.

```
    Belief({P, E, Eth})     "Build with safeguards, budget X, ethical review"
            │ ρ
            ▼
    Belief({P, E})          "Build with safeguards, budget X"
            │ ρ
            ▼
    Belief({P})             "Physically feasible with safeguards"
```

### 12.3.2 Compatibility: Agreement on Overlaps

**Definition 12.4**: Local beliefs {bᵢ ∈ Belief(Sᵢ)} are **compatible** if whenever Sᵢ ∩ Sⱼ ≠ ∅:

```
ρ_{Sᵢ→Sᵢ∩Sⱼ}(bᵢ) = ρ_{Sⱼ→Sᵢ∩Sⱼ}(bⱼ)
```

**Compatible**:
```
    Physics: "Possible       Economics: "Viable
     with safeguards"         with safeguards"
         │ ρ                       │ ρ
         └──────→ "safeguards" ←───┘   ✓ Same restriction
```

**Incompatible**:
```
    Physics: "Impossible"    Economics: "Viable"
         │ ρ                       │ ρ
         └────→ feasibility? ←─────┘   ✗ Contradictory
```

### 12.3.3 Gluing: Local to Global

**Definition 12.5**: If local beliefs {bᵢ} are compatible, the **gluing** operation produces a unique global belief b such that ρ_{S→Sᵢ}(b) = bᵢ for all i.

**The Sheaf Axiom**: For any compatible family, gluing exists and is unique.

```
    ┌───────────────────────────────────────┐
    │           Glue(b₁, b₂, b₃)            │
    │        ╱        │        ╲            │
    │       ▼         ▼         ▼           │
    │      b₁        b₂        b₃           │
    │    Physics  Economics  Ethics         │
    └───────────────────────────────────────┘
```

---

## 12.4 When the Sheaf Condition Fails

Real agents disagree. When local beliefs aren't compatible, no global belief exists.

### Types of Failure

**Factual Disagreement**: Agents disagree on shared facts.
```
Physics: "Requires 10MW" | Economics: "Budget supports 5MW"
```

**Value Disagreement**: Agents have different objectives.
```
Economics: "Maximize profit" | Ethics: "Minimize harm"
```

**Semantic Disagreement**: Same terms, different meanings.
```
Agent A: "Safe" = zero risk | Agent B: "Safe" = acceptable risk
```

### The Obstruction to Gluing

**Definition 12.6**: When beliefs fail compatibility, the **obstruction** measures *how* they fail:

```
Obstruction(b₁, b₂) = d(ρ(b₁), ρ(b₂))
```

**Proposition 12.7**: Gluing succeeds iff total obstruction vanishes.

---

## 12.5 Cocones for Disagreement

When sheaf gluing fails, we use **cocones**—synthesis without forced consensus.

### Definition 12.8 (Cocone)

Given beliefs {Bᵢ} with relationships fᵢⱼ, a **cocone** consists of:

- An apex C (the synthesis)
- Morphisms cᵢ : Bᵢ → C for each i
- Compatibility: cⱼ ∘ fᵢⱼ = cᵢ

```
     B₁ ─────f₁₂────→ B₂
      │                │
   c₁ │                │ c₂
      │                │
      └──────→ C ←─────┘
           (apex)
```

### The Key Insight

A cocone doesn't require B₁ and B₂ to agree. It requires only that their *images* in C are related correctly.

| Sheaf Gluing | Cocone |
|--------------|--------|
| Requires compatibility | Tolerates disagreement |
| Output restricts to inputs | Inputs embed into output |
| "These agree, so merge" | "These differ, but relate" |
| Consensus | Synthesis |

### Definition 12.9 (Colimit)

The **colimit** is the universal cocone—the "smallest" synthesis containing all beliefs.

### Example 12.10 (Dialectical Synthesis)

Physics: "Build with safeguards" (B₁)
Ethics: "Don't build—too risky" (B₂)

These don't glue. But they form a cocone:

```
C = "Build if and only if safeguards meet ethical standards"
c₁: "safeguards" embeds as the condition
c₂: "risk" embeds as the standard
```

The synthesis preserves both perspectives without forcing agreement.

---

## 12.6 Practical Protocols

### 12.6.1 Self-Consistency as Approximate Gluing

**Protocol**: Run N independent reasoning chains. Majority vote.

**Sheaf Interpretation**:
- Each chain is a local section
- Agreeing chains satisfy compatibility
- Majority voting approximates gluing

```python
def self_consistency_as_sheaf(chains: list[ReasoningChain]) -> GlobalBelief:
    answers = [chain.final_answer for chain in chains]
    agreement_rate = max(Counter(answers).values()) / len(answers)

    if agreement_rate > THRESHOLD:
        return GlobalBelief(answer=mode(answers), confidence=agreement_rate)
    else:
        return GluingFailure(obstruction=Counter(answers))
```

### 12.6.2 Weighted Consensus

**Protocol**: Weight agents by expertise, then combine.

```python
def weighted_consensus(beliefs: dict[Agent, Belief],
                       expertise: dict[Agent, float]) -> GlobalBelief:
    total = sum(expertise[a] for a in beliefs.keys())
    weights = {a: expertise[a] / total for a in beliefs.keys()}
    return GlobalBelief(content=combine_weighted(beliefs, weights))
```

### 12.6.3 Dialectical Resolution

**Protocol**: When beliefs conflict, construct explicit synthesis via dialogue.

```python
async def dialectical_resolution(belief_a: Belief, belief_b: Belief,
                                  mediator: Agent) -> Synthesis:
    synthesis = await mediator.generate(f"""
    View A: {belief_a}
    View B: {belief_b}
    Construct a synthesis that preserves valid insights from each.
    """)
    return Synthesis(apex=synthesis, method="dialectical_cocone")
```

### 12.6.4 Hierarchical Consensus

**Protocol**: Decompose hierarchically. Achieve consensus bottom-up.

```
Level 3: Global Decision
            │
    ┌───────┴───────┐
Level 2: Physics-Econ    Ethics-Social
    │       │         │       │
Level 1: Physics  Econ  Ethics  Social
```

---

## 12.7 Connection to Distributed Systems

Multi-agent coordination is distributed consensus. The analogies run deep.

### 12.7.1 CAP Theorem Echoes

| CAP Property | Agent Interpretation |
|--------------|---------------------|
| Consistency | Sheaf condition holds |
| Availability | Every agent can produce output |
| Partition | Agents can't communicate fully |

**Proposition 12.11**: Multi-agent systems face an analogous tradeoff. When agents are partitioned, maintaining sheaf consistency requires sacrificing availability.

### 12.7.2 Eventual Consistency

**Definition 12.12**: A system is **eventually consistent** if, given no new updates, all nodes eventually agree.

**Agent Interpretation**: Given time and no new evidence, agents eventually achieve sheaf gluing.

```
Time 0: Incompatible beliefs
Time 1: Share reasoning, update
Time 2: Beliefs compatible
Time 3: Gluing succeeds → consensus
```

### 12.7.3 Consensus Protocols

Paxos/Raft interpreted via sheaves:
- Leader election ≈ choosing "ground truth" section
- Replication ≈ restriction
- Commit ≈ verifying compatibility
- Apply ≈ gluing

---

## 12.8 Examples

### 12.8.1 Multi-Model Ensemble

**Setup**: Three LLMs answer a question.

**When Outputs Glue**:
- All three same answer → trivially compatible
- Two agree, one differs → glue majority (approximate)
- All differ → gluing fails

```python
class ModelEnsembleSheaf:
    def compatible(self, beliefs: list[Belief]) -> bool:
        return len(set(b.answer for b in beliefs)) == 1

    def glue(self, beliefs: list[Belief]) -> Belief:
        if not self.compatible(beliefs):
            raise SheafConditionFailure()
        return Belief(answer=beliefs[0].answer,
                     reasoning={b.model: b.reasoning for b in beliefs})
```

### 12.8.2 Agent Debate

**Setup**: Two agents argue opposing sides. A judge synthesizes.

**Cocone Structure** (designed to disagree):

```
    Agent_Pro ────→ Synthesis ←──── Agent_Con
                        │
                        ▼
                      Judge
```

The judge constructs a cocone: both perspectives embed into the judgment.

### 12.8.3 Coalition Formation

**Setup**: N agents. Some subsets compatible; others not.

```
All agents: {A, B, C, D, E}

Compatible: {A,B} ✓, {B,C} ✓, {A,B,C} ✓, {D,E} ✓
Incompatible: {A,D} ✗

Maximal coalitions: {A,B,C} or {D,E}
```

---

## 12.9 Implementation Sketch

```python
class AgentSheaf(ABC, Generic[Agent, Belief]):
    """Sheaf over an agent space for multi-agent consensus."""

    @abstractmethod
    def restrict(self, belief: Belief, from_agents: frozenset[Agent],
                 to_agents: frozenset[Agent]) -> Belief:
        """Project belief to subgroup. Must satisfy identity and transitivity."""
        ...

    @abstractmethod
    def compatible(self, local_beliefs: dict[frozenset[Agent], Belief]) -> bool:
        """Check if local beliefs agree on overlaps."""
        ...

    @abstractmethod
    def glue(self, local_beliefs: dict[frozenset[Agent], Belief]) -> Optional[Belief]:
        """Glue compatible beliefs into global. Returns None if incompatible."""
        ...

    def coherence_gap(self, local_beliefs: dict[frozenset[Agent], Belief]) -> float:
        """Quantify deviation from compatibility. 0 = perfectly compatible."""
        total, count = 0.0, 0
        for (s1, b1), (s2, b2) in pairs(local_beliefs.items()):
            if overlap := s1 & s2:
                total += self.belief_distance(
                    self.restrict(b1, s1, overlap),
                    self.restrict(b2, s2, overlap)
                )
                count += 1
        return total / count if count else 0.0
```

```python
class BeliefCocone(Generic[Agent, Belief]):
    """Construct cocones when sheaf gluing fails."""

    def dialectical_synthesis(self, thesis: Belief, antithesis: Belief,
                               synthesizer: Callable) -> CoconeResult[Belief]:
        apex = synthesizer(thesis, antithesis)
        return CoconeResult(
            apex=apex,
            embeddings={"thesis": self._embed_thesis, "antithesis": self._embed_antithesis},
            universal=False
        )
```

---

## 12.10 Formal Summary

**Theorem 12.13** (Multi-Agent Coordination Structure)

| Concept | Mathematical Structure |
|---------|----------------------|
| Agent beliefs | Presheaf over agent subsets |
| Compatible beliefs | Sheaf condition on overlaps |
| Consensus | Glued global section |
| Disagreement | Sheaf condition failure |
| Synthesis without consensus | Cocone/colimit construction |
| Eventual consensus | Eventual sheaf condition |

**Proposition 12.14**: Self-consistency approximates sheaf gluing. Agreement rate measures sheaf condition satisfaction.

**Proposition 12.15**: Dialectical synthesis constructs a cocone. The synthesis is the apex; original beliefs embed into it.

**Conjecture 12.16** (Coordination Optimality): Optimal multi-agent coordination is characterized by:
1. Maximizing compatible coalition size (sheaf)
2. Constructing minimal cocones for disagreements
3. Balancing consensus value against coordination cost

---

## 12.11 The Deeper Pattern

Multi-agent coordination reveals a pattern throughout this monograph:

**Local + Compatibility → Global**

- Sheaves: local sections + compatibility → global section
- Operads: local operations + laws → valid compositions
- Monads: local effects + coherence → composed effects
- DP: local values + Bellman → global policy

The pattern: **structured locality enables principled globality**.

When structure fails, we move to weaker structures (cocone vs glue, approximate vs exact) that preserve what can be preserved. This is categorical philosophy: understand ideal structure, measure deviation, adapt gracefully.

---

## 12.12 Exercises

1. **Construct**: Define a belief sheaf for five agents where not all pairs are compatible. Find maximal coalitions.

2. **Compute**: For a three-model ensemble with outputs "A", "A", "B", compute the coherence gap.

3. **Prove**: If the sheaf condition holds pairwise and agents form a connected graph, it holds globally.

4. **Explore**: Define a "dynamic sheaf" where agents update beliefs during coordination.

5. **Contemplate**: In dialectical synthesis, is the apex unique? What characterizes valid syntheses?

---

*Previous: [Chapter 11: Meta-DP and Self-Improvement](./11-meta-dp.md)*
*Next: [Chapter 13: Heterarchical Systems](./13-heterarchy.md)*
