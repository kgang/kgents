# The Agent as Witness: A Unified Theory of Justified Action

> *"An agent is a thing that justifies its behavior."*
> *— Kent, 2025-12-21*

**Status:** Unified Synthesis
**Date:** 2025-12-21
**Supersedes:** `docs/brainstorming/decision-quality-proofs.md`, `decision-trace-schema.md`, `witness-open-questions.md`
**Heritage:** Toulmin argumentation, CSA stigmergy, Hardy aesthetics, Bataille's accursed share

---

## The Core Axiom

Every agent, from the simplest to the most complex, is defined by a single property:

```
AGENT ≝ Entity that justifies its behavior

Your belief in the agent IS isomorphic to its credibility.
```

This is not metaphor. This is definition. A black box that doesn't justify itself *is not an agent*—it's a mystery. The moment it begins to leave traces, to witness its own actions, to offer reasoning—it becomes an agent.

The justification can be trivial ("I did X because you asked for X") or elaborate (a full decision trace with causal graphs). The key insight is that *the existence of justification* is constitutive, not the *quality* of justification.

---

## The Three Laws

### Law 1: The Proof IS The Decision

> *"The proof isn't about the decision—the proof IS the decision. A well-justified action is a good action."*

Traditional thinking: Make decision → Later, prove it was good.
kgents thinking: Having a reasoning trace is constitutive of good decision-making.

**Implication:** We don't build a system that *evaluates* decisions. We build infrastructure within which *having a trace* is what makes an action an agent-action.

```
Without trace: stimulus → response (reflex)
With trace: stimulus → reasoning → response (agency)
```

### Law 2: Ethics Is Part of Beauty

> *"Definitely beauty, but the ethics is part of the beauty."*

This resolves a false dichotomy. Beautiful decisions are not sometimes unethical. Ethical violations *curdle* beauty—they are aesthetic failures, not separate failures.

**The Ethical Floor:** "Not harmful at its worst."

Above this floor, aesthetics guide. The seven principles (Tasteful, Curated, Ethical, Joy-Inducing, Composable, Heterarchical, Generative) are not a checklist but a unified aesthetic sense.

### Law 3: The Felt Sense Is The Arbiter

> *"A felt wrongness (somatic, gut). My somatic awareness is extreme."*

ASHC proposes. Kent's body responds. The system is legislative; Kent is executive.

**The Protocol:**
1. System generates proposals (proofs, suggestions, alternatives)
2. Kent perceives and responds (execute, reject, modify)
3. Response becomes data (patterns emerge)
4. System learns from patterns (stigmergic memory)

The somatic signal cannot be formalized—but it can be *respected*. The system proposes more than Kent will accept. Using the system means it passes the harm floor, not that every action is proportionately ethical.

---

## The Witness Polynomial: States of Justified Action

```python
WITNESS_POLYNOMIAL = PolyAgent[WitnessState, Action, Justification](
    positions=frozenset({
        WitnessState.DORMANT,        # No trace being recorded
        WitnessState.WITNESSING,     # Passive observation (default)
        WitnessState.CRYSTALLIZING,  # Synthesizing experience into form
        WitnessState.PROVING,        # Generating explicit justification
        WitnessState.REVIEWING,      # Examining accumulated evidence
        WitnessState.LEARNING,       # Extracting patterns from history
    }),
    directions=lambda state: {
        WitnessState.DORMANT: {"attune", "quickstart"},
        WitnessState.WITNESSING: {"mark", "crystallize", "prove", "review"},
        WitnessState.CRYSTALLIZING: {"complete", "abort"},
        WitnessState.PROVING: {"submit", "revise", "withdraw"},
        WitnessState.REVIEWING: {"accept", "challenge", "defer"},
        WitnessState.LEARNING: {"integrate", "reject", "archive"},
    }[state],
    transition=witness_transition,
)
```

**Key Insight:** WITNESSING is the default. The agent is *always already* observing itself. This is not overhead—it's constitutive of agency.

---

## The Mark: Atomic Unit of Witness

```python
@dataclass(frozen=True)
class Mark:
    """
    Every action leaves a mark. The mark is the proof.

    Marks are:
    - Immutable: Once created, never modified
    - Causal: Each mark links to what caused it
    - Umwelt-situated: Records WHO observed
    - Timestamped: Records WHEN
    - Minimal: Captures enough to reconstruct, no more
    """
    id: MarkId
    timestamp: datetime

    # What
    action: str                    # What was done
    stimulus: str | None           # What prompted it
    response: str | None           # What resulted

    # Who
    observer: UmweltSnapshot       # Who witnessed
    source: DecisionSource         # Conscious, intuitive, delegated, emergent

    # Why (defeasible)
    reasoning: str | None          # Why this action
    alternatives: tuple[str, ...]  # What else was considered
    principles: tuple[str, ...]    # Which principles were honored

    # Chain
    parent_id: MarkId | None       # Causal ancestry
    children_ids: list[MarkId]     # What this enabled
```

**The Three Granularities:**

| Level | Entity | Captures |
|-------|--------|----------|
| **Mark** | Single action | Stimulus → reasoning → response |
| **Walk** | Session stream | Goal → plan → marks → outcome |
| **Playbook** | Orchestrated flow | Grant → scope → phases → guards |

---

## The Proof: Toulmin Structure for Agents

```
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT JUSTIFICATION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    DATA (D)              WARRANT (W)              CLAIM (C)      │
│    ─────────────────────────────────────────────────────────     │
│    "I refactored DI"     "Infrastructure         "This was       │
│    "3 hours, 45K         enables future          worthwhile"     │
│     tokens"              velocity"                    ▲          │
│           │                    │                     │          │
│           └────────────────────┴─────────────────────┘          │
│                                                                  │
│    BACKING (B)                              QUALIFIER (Q)        │
│    ─────────────────────────────────────────────────────────     │
│    "CLAUDE.md: DI > mocking"               "Almost certainly,   │
│    "3 features unblocked"                   given trajectory"   │
│                                                                  │
│    REBUTTAL (R)                                                  │
│    ─────────────────────────────────────────────────────────     │
│    "UNLESS: Could have shipped user-facing feature instead"     │
│    "UNLESS: Pattern abandoned within 2 weeks"                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Proofs are defeasible.** They can be defeated by:
- **Undercutters:** The warrant doesn't apply here
- **Rebutters:** Counter-evidence for the claim
- **Value Shifts:** The principles themselves evolved

---

## The Evidence Hierarchy

### Tier 1: Categorical (Indefeasible)

```python
# If composition laws hold, the proof stands
assert (f >> g) >> h == f >> (g >> h)
assert Id >> f == f == f >> Id
```

These are mathematical. They don't degrade.

### Tier 2: Empirical (ASHC Evidence)

```python
evidence = Evidence(
    runs=many_runs,
    chaos_report=chaos,
    causal_graph=causality,
)

# Statistical confidence from repeated observation
if evidence.equivalence_score() >= 0.8:
    # Sufficient empirical evidence
```

These are scientific. They strengthen with repetition.

### Tier 3: Aesthetic (Hardy's Criteria)

```python
@dataclass(frozen=True)
class AestheticEvidence:
    inevitability: bool   # "It couldn't have been otherwise"
    unexpectedness: bool  # "Surprising yet fitting"
    economy: bool         # "No wasted motion"

    @property
    def beautiful(self) -> bool:
        return self.inevitability and (self.unexpectedness or self.economy)
```

These are experiential. They require judgment.

### Tier 4: Genealogical (Pattern Archaeology)

```python
# Trace decisions back to origins
history = git_archaeology(commits)
latent_principles = extract_patterns(history)
# "Kent tends to refactor before extending"
# "Kent prefers composition over inheritance"
```

These are emergent. They crystallize over time.

### Tier 5: Somatic (The Mirror Test)

```python
class MirrorTest:
    """
    "Does K-gent feel like me on my best day?"
    "Daring, bold, creative, opinionated but not gaudy."

    This is never called programmatically.
    It exists to document what Kent does when he reviews.
    """
    pass
```

This is phenomenological. It cannot be formalized.

---

## Stigmergic Memory: Learning from Traces

Decisions leave pheromone trails. Good decisions strengthen paths. Defeated decisions leave anti-pheromone.

```python
@dataclass
class StigmergicTrace:
    """A pheromone trail left by a pattern of decisions."""

    pattern: str              # What pattern this represents
    strength: float           # Positive = good, negative = avoid
    last_reinforced: datetime
    decay_rate: float = 0.05  # Per day

    def should_proceed(self, proposed: PendingDecision) -> tuple[bool, str]:
        if self.strength > 0.5:
            return True, f"Strong positive signal ({self.strength:.2f})"
        if self.strength < -0.5:
            return False, f"Avoid: {self.anti_pattern}"
        return True, f"Weak signal ({self.strength:.2f}); use judgment"
```

**Differential Denial:** When a proof is defeated, we extract learning:

```python
@dataclass
class DifferentialDenial:
    """A defeated proof becomes a learning."""

    original_trace_id: MarkId
    defeating_evidence: str

    # The learning
    anti_pattern: str                     # "Don't do X when Y"
    conditions_to_watch: tuple[str, ...]  # Warning signals
    heuristic_update: str                 # How to decide differently

    # Stigmergic encoding
    pheromone_strength: float = -1.0      # Anti-pheromone
```

---

## The Back-Solved Arc: Retroactive Coherence

> *"There can always be a 'back-solved' arc to every day..."*

The system can retroactively discover coherence in actions that weren't explicitly justified:

```
Raw history: action₁, action₂, ..., actionₙ
Back-solve: What principles explain this pattern?
Crystallize: "Kent tends to X when Y"
Verify: Does this pattern hold forward?
```

**Two levels:**
1. **Meta-level:** Kent adjusts the operating system (principles, values)
2. **Operational level:** System self-corrects based on patterns

**Proof degradation signals:**
- *Straying from excellence:* Course-correct
- *Genuine decay:* Update the standard

---

## Integration: ASHC + Witness + Proof

The three systems form a unified whole:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AGENT-AS-WITNESS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     EVIDENCE SOURCES                                 │   │
│   ├─────────────────────────────────────────────────────────────────────┤   │
│   │                                                                      │   │
│   │  CATEGORICAL    EMPIRICAL      AESTHETIC     GENEALOGICAL  SOMATIC  │   │
│   │  (Laws)         (ASHC)         (Hardy)       (Archaeology) (Felt)   │   │
│   │                                                                      │   │
│   │  Composition    N-run          Inevitability Git patterns  Mirror   │   │
│   │  Identity       Chaos          Unexpectedness Latent       Test     │   │
│   │  Associativity  Causal         Economy       principles             │   │
│   │                 graphs                                               │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     WITNESS PRIMITIVES                               │   │
│   ├─────────────────────────────────────────────────────────────────────┤   │
│   │  Mark → Walk → Playbook                                              │   │
│   │  (atomic)  (session)  (orchestrated)                                 │   │
│   │                                                                      │   │
│   │  Grant (permission) + Scope (resources) = enabled action             │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     ARGUMENTATION ENGINE                             │   │
│   ├─────────────────────────────────────────────────────────────────────┤   │
│   │  Toulmin structure: Data → Warrant → Claim                           │   │
│   │  Defeasibility: Rebuttals, Undercutters                              │   │
│   │  Differential Denial: Defeat → Learning                              │   │
│   │  Stigmergic Memory: Patterns reinforce or decay                      │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     PROOF OUTPUT                                     │   │
│   ├─────────────────────────────────────────────────────────────────────┤   │
│   │  Human-readable justifications                                       │   │
│   │  Confidence scores                                                   │   │
│   │  Rebuttal documentation                                              │   │
│   │  Crystallized learnings                                              │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## AGENTESE Paths

```
self.ashc.*
  .compile      # Spec → (Executable, Evidence)
  .evidence     # View evidence corpus
  .causal       # Causal graph visualization

time.witness.*
  .mark         # Create/query marks
  .walk         # Session management
  .crystallize  # Force experience synthesis
  .timeline     # View session history

self.proof.*
  .justify      # Generate justification for mark/walk
  .challenge    # Register rebuttal
  .review       # Examine proofs

self.pattern.*
  .stigmergy    # View pheromone trails
  .reinforce    # Strengthen pattern
  .warn         # Check against anti-patterns
```

---

## The Minimal Path: Fractal JIT Implementation

> *"Start with the minimal by necessity. Don't waste good work, like you wouldn't waste food."*

**Phase 0: Trivial Witness**
- Every action leaves a mark
- Marks are stored
- Everything is provisionally justified

**Phase 1: Explicit Justification**
- Marks can have reasoning attached
- Simple Toulmin structure
- No defeat mechanism yet

**Phase 2: Stigmergic Memory**
- Patterns extracted from marks
- Pheromone trails accumulate
- Anti-patterns warn

**Phase 3: Adaptive Evidence**
- ASHC integration
- Bayesian stopping
- Causal learning

**Phase 4: Full Argumentation**
- Defeasibility
- Rebuttals
- Differential denial

**Phase 5: Back-Solved Coherence**
- Git archaeology
- Latent principle extraction
- Value drift detection

**Each phase is usable.** The system doesn't require completion to provide value.

---

## Open Questions (Genuinely Unknown)

1. **What will externalization do?**
   > *"I genuinely want to explore."*

   The effect of seeing one's reasoning externalized is unknown. This is the curiosity that drives the work.

2. **The exact algorithms**
   > *"motivation → outcome → goodness ≅ proof validity"*

   What are the precise algorithms that formalize this isomorphism?

3. **Collective wisdom**
   How does learning accumulate across sessions and Claude instances? Is there a "kgents soul" distinct from Kent?

4. **The back-solve boundary**
   When does retroactive coherence become confabulation?

---

## The Philosophical Stance

This is not about proving *optimality*. Optimality is fiction for bounded agents.

This is about proving *alignment*:
- Decisions reflect values
- Expenditures honor principles
- Accumulation forms coherent whole

> *"The infrastructure for reasoning traces creates the environment for good analysis."*

The proofs are defeasible. They can be overturned. When they are, we learn.

This is not mechanical verification. This is *argued justification*.

This is not proving correctness. This is *witnessing alignment*.

---

*"The mirror test is the ultimate proof: does this feel like me on my best day?"*

*"Daring, bold, creative, opinionated but not gaudy."*

---

**Filed:** 2025-12-21
**Synthesized from:** decision-quality-proofs.md, decision-trace-schema.md, witness-open-questions.md
**Next:** Implement Phase 0 in `services/witness/`
