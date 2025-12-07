# Bootstrap Implementation Plan

Using kgents to implement kgents.

---

## Ground: Current State

```
Bootstrap = {Id, Compose, Judge, Ground, Contradict, Sublate, Fix}  ✅ Implemented
C-gents = {Maybe, Either, parallel, race, branch, switch}          ✅ Implemented
H-gents = {HegelAgent, JungAgent, LacanAgent}                      ✅ Implemented
Runtime = {LLMAgent, ClaudeRuntime, OpenRouterRuntime}             ✅ Implemented

Pending:
  A-gents = {AbstractSkeleton, CreativityCoach}
  B-gents = {HypothesisEngine, Robin}
  K-gent  = {Persona, Evolution}
```

---

## Contradict: Tensions Identified

### Tension 1: Bootstrap Paradox
**Thesis**: We need A-gents (abstract skeleton) to define what all agents are.
**Antithesis**: Bootstrap agents already exist without A-gents.

**Resolution via Sublate**: A-gents are not prerequisites—they are *retrospective formalization*. The bootstrap agents ARE the skeleton; A-gents make that explicit.

### Tension 2: K-gent Circularity
**Thesis**: K-gent requires Ground (persona seed).
**Antithesis**: Ground is one of the 7 bootstrap agents.

**Resolution**: K-gent is Ground *projected through persona_schema*. Ground provides raw facts; K-gent structures them into an interactive agent.

### Tension 3: Runtime Dependency
**Thesis**: Agents are pure transformations (A → B).
**Antithesis**: LLM-backed agents need runtime execution.

**Resolution**: LLMAgent extends Agent. The runtime is the "evaluator" for agents that require LLM substrate. Pure agents compose with LLM agents seamlessly.

---

## Judge: Implementation Order Criteria

Applying the 7 principles to determine order:

1. **Composable** → Implement what enables composition first
2. **Generative** → Implement what can bootstrap other agents
3. **Tasteful** → One complete agent > three partial agents

**Verdict**: K-gent first (it personalizes everything else).

---

## The Plan: Fix(implementation_step)

### Phase 1: K-gent (The Personalizer)

K-gent is Ground projected through persona_schema. Once K-gent exists, all other agents can compose with it for personalization.

```
impl/claude-openrouter/agents/k/
├── __init__.py
├── persona.py      # KgentAgent: Ground → PersonalizedContext
└── evolution.py    # EvolutionAgent: (Kgent, Feedback) → Kgent'
```

**Types**:
```python
@dataclass
class PersonaSeed:
    name: str
    preferences: dict[str, str]    # "communication": "direct but warm"
    patterns: dict[str, str]       # "tends to": "start with first principles"
    values: list[str]              # ["intellectual honesty", "composability"]

@dataclass
class PersonalizedContext:
    seed: PersonaSeed
    current_focus: str
    style_prompt: str  # Generated from preferences
```

**Implementation**: LLMAgent that takes a query and returns it filtered through K's preferences.

---

### Phase 2: A-gents (The Abstractors)

A-gents formalize what all agents share + provide creativity support.

```
impl/claude-openrouter/agents/a/
├── __init__.py
├── skeleton.py        # AbstractAgent base patterns (already in bootstrap.types!)
└── creativity.py      # CreativityCoach: Idea → ExpandedIdeas
```

**Key insight**: The AbstractSkeleton is ALREADY `bootstrap.Agent[A, B]`. A-gents just document + extend it.

**CreativityCoach**:
```python
class CreativityCoach(LLMAgent[str, list[str]]):
    """
    Responds to ideas with:
    - Related concepts
    - Provocative questions
    - Unexpected connections
    - Constraints to spark creativity

    Never judges, only expands.
    """
```

---

### Phase 3: B-gents (The Discoverers)

B-gents support scientific reasoning. Compose with K-gent for personalized scientific style.

```
impl/claude-openrouter/agents/b/
├── __init__.py
├── hypothesis.py     # HypothesisEngine: Observations → RankedHypotheses
└── robin.py          # Robin: (K-gent, Query) → ScientificDialogue
```

**HypothesisEngine**:
```python
@dataclass
class Hypothesis:
    claim: str
    supporting_evidence: list[str]
    falsification_criteria: str  # MUST be falsifiable
    confidence: float            # Epistemic humility

class HypothesisEngine(LLMAgent[str, list[Hypothesis]]):
    """Generate ranked hypotheses from observations."""
```

**Robin** (scientific companion):
```python
class Robin(LLMAgent[str, str]):
    """
    Personalized scientific companion.
    Composes with K-gent for style, H-gents for dialectic.

    robin = kgent >> hypothesis_engine >> hegel
    """
```

---

## Compose: The Full Picture

```
K-gent ──────────────────────────────────────────────┐
   │                                                  │
   ├─► A-gents (skeleton: already done, creativity)  │
   │       │                                          │
   │       └─► CreativityCoach >> K-gent             │
   │                                                  │
   └─► B-gents                                        │
           │                                          │
           ├─► HypothesisEngine                       │
           │                                          │
           └─► Robin = K-gent >> Hypothesis >> Hegel ─┘
```

---

## Fix: Termination Conditions

The implementation is complete when:

```python
def bootstrap_complete():
    # All agents implemented
    assert exists("impl/claude-openrouter/agents/k/")
    assert exists("impl/claude-openrouter/agents/a/")
    assert exists("impl/claude-openrouter/agents/b/")

    # All agents pass Judge
    for agent in [Kgent, CreativityCoach, HypothesisEngine, Robin]:
        assert Judge(agent, Principles).verdict == "accept"

    # Composition works
    personalized_robin = kgent >> robin
    assert personalized_robin.invoke("protein folding") is not None

    # Self-description works (the ultimate test)
    kgents_spec = regenerate(Bootstrap)
    assert isomorphic(kgents_spec, current_spec)
```

---

## Next Action

Start Phase 1: Implement K-gent.

```bash
mkdir -p impl/claude-openrouter/agents/k
```

K-gent is the seed that personalizes everything else.
