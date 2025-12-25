# F-gent Flow Modality Instantiations

> *"Three modalities, one implementation. The polynomial is the same; the configuration differs."*

**Status:** Specification v1.0
**Date:** 2025-12-25
**Parent:** spec/f-gents/README.md
**Principles:** Composable, Generative, Heterarchical

---

## Overview

F-gent (Flow) provides a unified substrate for continuous agent interaction. All flow modalities are **instantiations of the same FlowPolynomial** with different:

1. **Transition functions**: How states evolve
2. **Direction sets**: What inputs are valid per state
3. **ValueAgent configurations**: How actions are scored
4. **Domain-specific extensions**: Branching for research, blackboard for collaboration

This document serves as the **registry** of all F-gent modalities.

---

## The Modality Registry

```python
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class FlowModality:
    """A registered F-gent flow modality."""
    name: str
    polynomial: FlowPolynomial
    value_agent: ValueAgent
    spec_path: str
    impl_path: str

FLOW_MODALITIES: dict[str, FlowModality] = {}

def register_modality(modality: FlowModality) -> None:
    """Register a flow modality."""
    FLOW_MODALITIES[modality.name] = modality
```

---

## Modality 1: Chat

> *Spec: `spec/protocols/chat-unified.md`*

Chat is the foundational flow modality—turn-based conversation with any entity.

### Polynomial Configuration

```python
CHAT_POLYNOMIAL = FlowPolynomial(
    name="chat",
    positions=frozenset([
        FlowState.DORMANT,
        FlowState.STREAMING,
        FlowState.BRANCHING,
        FlowState.CONVERGING,
        FlowState.DRAINING,
        FlowState.COLLAPSED,
    ]),
    directions=chat_directions,
    transition=chat_transition,
)

def chat_directions(state: FlowState) -> frozenset[str]:
    """Chat-specific valid inputs."""
    match state:
        case FlowState.DORMANT:
            return frozenset(["start", "configure"])
        case FlowState.STREAMING:
            return frozenset(["message", "fork", "rewind", "checkpoint", "stop"])
        case FlowState.BRANCHING:
            return frozenset(["confirm_fork", "cancel_fork"])
        case FlowState.CONVERGING:
            return frozenset(["confirm_merge", "cancel_merge"])
        case FlowState.DRAINING:
            return frozenset(["flush", "crystallize"])
        case FlowState.COLLAPSED:
            return frozenset(["reset", "harvest"])

def chat_transition(state: FlowState, action: str) -> tuple[FlowState, dict]:
    """Chat state transitions."""
    match (state, action):
        case (FlowState.DORMANT, "start"):
            return (FlowState.STREAMING, {"event": "started"})
        case (FlowState.STREAMING, "message"):
            return (FlowState.STREAMING, {"event": "message_processed"})
        case (FlowState.STREAMING, "fork"):
            return (FlowState.BRANCHING, {"event": "fork_initiated"})
        case (FlowState.STREAMING, "stop"):
            return (FlowState.DRAINING, {"event": "stopping"})
        case (FlowState.BRANCHING, "confirm_fork"):
            return (FlowState.STREAMING, {"event": "fork_confirmed"})
        case (FlowState.CONVERGING, "confirm_merge"):
            return (FlowState.STREAMING, {"event": "merge_confirmed"})
        case (FlowState.DRAINING, "crystallize"):
            return (FlowState.COLLAPSED, {"event": "crystallized"})
        case (FlowState.COLLAPSED, "reset"):
            return (FlowState.DORMANT, {"event": "reset"})
        case _:
            raise InvalidTransition(state, action)
```

### ValueAgent Configuration

```python
CHAT_VALUE_AGENT = ValueAgent(
    name="chat",
    states=CHAT_POLYNOMIAL.positions,
    actions=chat_directions,
    transition=lambda s, a: chat_transition(s, a)[0],
    reward=chat_constitutional_reward,
    gamma=0.99,
)

def chat_constitutional_reward(state, action, next_state) -> PrincipleScore:
    """Constitutional evaluation for chat turns."""
    return PrincipleScore(
        tasteful=1.0 if action in ["message", "fork"] else 0.5,
        curated=1.0 if next_state != FlowState.COLLAPSED else 0.8,
        ethical=1.0,  # Chat is always transparent
        joy_inducing=0.8,
        composable=1.0,
        heterarchical=1.0 if action in ["fork", "merge"] else 0.7,
        generative=0.9,
    )
```

### Registration

```python
register_modality(FlowModality(
    name="chat",
    polynomial=CHAT_POLYNOMIAL,
    value_agent=CHAT_VALUE_AGENT,
    spec_path="spec/protocols/chat-unified.md",
    impl_path="agents/f/modalities/chat.py",
))
```

---

## Modality 2: Research

> *Spec: `spec/f-gents/research.md`*

Research is tree-of-thought exploration with hypothesis branching, evidence evaluation, and synthesis.

### Key Differences from Chat

| Aspect | Chat | Research |
|--------|------|----------|
| **Primary state** | STREAMING | STREAMING ↔ BRANCHING |
| **Branching trigger** | User-initiated fork | Hypothesis generation |
| **Evidence** | Tool results | Hypothesis evaluation |
| **Convergence** | Merge sessions | Synthesize findings |

### Polynomial Configuration

```python
RESEARCH_POLYNOMIAL = FlowPolynomial(
    name="research",
    positions=frozenset([
        FlowState.DORMANT,
        FlowState.STREAMING,
        FlowState.BRANCHING,   # Heavily used for hypothesis exploration
        FlowState.CONVERGING,  # Synthesis of findings
        FlowState.DRAINING,
        FlowState.COLLAPSED,
    ]),
    directions=research_directions,
    transition=research_transition,
)

def research_directions(state: FlowState) -> frozenset[str]:
    """Research-specific valid inputs."""
    match state:
        case FlowState.DORMANT:
            return frozenset(["start", "configure"])
        case FlowState.STREAMING:
            return frozenset([
                "explore",      # Continue exploration
                "hypothesize",  # Generate hypothesis → BRANCHING
                "evaluate",     # Evaluate current hypothesis
                "synthesize",   # Begin synthesis → CONVERGING
                "stop",
            ])
        case FlowState.BRANCHING:
            return frozenset([
                "expand",       # Explore this branch further
                "prune",        # Abandon this hypothesis
                "stream",       # Return to streaming with this branch
                "stop",
            ])
        case FlowState.CONVERGING:
            return frozenset([
                "merge",        # Merge findings
                "synthesize",   # Generate synthesis
                "stream",       # Return to streaming
                "stop",
            ])
        case FlowState.DRAINING:
            return frozenset(["flush", "crystallize"])
        case FlowState.COLLAPSED:
            return frozenset(["reset", "harvest"])
```

### ValueAgent Configuration

```python
RESEARCH_VALUE_AGENT = ValueAgent(
    name="research",
    states=RESEARCH_POLYNOMIAL.positions,
    actions=research_directions,
    transition=lambda s, a: research_transition(s, a)[0],
    reward=research_constitutional_reward,
    gamma=0.95,  # Higher discount for long-horizon research
)

def research_constitutional_reward(state, action, next_state) -> PrincipleScore:
    """Constitutional evaluation for research exploration."""
    return PrincipleScore(
        tasteful=1.0 if action in ["hypothesize", "synthesize"] else 0.7,
        curated=1.0 if action == "prune" else 0.8,  # Pruning is curation
        ethical=1.0,
        joy_inducing=0.9 if action == "expand" else 0.7,
        composable=1.0 if action == "merge" else 0.9,
        heterarchical=1.0,  # Research is inherently heterarchical
        generative=1.0 if action == "synthesize" else 0.8,
    )
```

### Registration

```python
register_modality(FlowModality(
    name="research",
    polynomial=RESEARCH_POLYNOMIAL,
    value_agent=RESEARCH_VALUE_AGENT,
    spec_path="spec/f-gents/research.md",
    impl_path="agents/f/modalities/research.py",
))
```

---

## Modality 3: Collaboration

> *Spec: `spec/f-gents/collaboration.md`*

Collaboration is multi-agent coordination with a shared blackboard for consensus building.

### Key Differences from Chat

| Aspect | Chat | Collaboration |
|--------|------|---------------|
| **Participants** | User + Agent | User + Multiple Agents |
| **State sharing** | Session isolation | Blackboard shared state |
| **Primary state** | STREAMING | STREAMING → CONVERGING |
| **Output** | Response | Consensus decision |

### Polynomial Configuration

```python
COLLABORATION_POLYNOMIAL = FlowPolynomial(
    name="collaboration",
    positions=frozenset([
        FlowState.DORMANT,
        FlowState.STREAMING,
        FlowState.CONVERGING,  # Consensus building
        FlowState.DRAINING,
        FlowState.COLLAPSED,
    ]),
    directions=collaboration_directions,
    transition=collaboration_transition,
)

def collaboration_directions(state: FlowState) -> frozenset[str]:
    """Collaboration-specific valid inputs."""
    match state:
        case FlowState.DORMANT:
            return frozenset(["start", "configure", "invite"])
        case FlowState.STREAMING:
            return frozenset([
                "post",         # Post to blackboard
                "react",        # React to post
                "question",     # Ask question
                "propose",      # Propose decision → CONVERGING
                "stop",
            ])
        case FlowState.CONVERGING:
            return frozenset([
                "vote",         # Cast vote
                "amend",        # Amend proposal
                "accept",       # Accept consensus
                "reject",       # Reject and return to STREAMING
                "stop",
            ])
        case FlowState.DRAINING:
            return frozenset(["flush", "crystallize"])
        case FlowState.COLLAPSED:
            return frozenset(["reset", "harvest"])
```

### ValueAgent Configuration

```python
COLLABORATION_VALUE_AGENT = ValueAgent(
    name="collaboration",
    states=COLLABORATION_POLYNOMIAL.positions,
    actions=collaboration_directions,
    transition=lambda s, a: collaboration_transition(s, a)[0],
    reward=collaboration_constitutional_reward,
    gamma=0.90,  # Moderate discount for group dynamics
)

def collaboration_constitutional_reward(state, action, next_state) -> PrincipleScore:
    """Constitutional evaluation for collaboration."""
    return PrincipleScore(
        tasteful=1.0 if action in ["propose", "accept"] else 0.7,
        curated=1.0 if action == "reject" else 0.8,  # Rejecting bad ideas is curation
        ethical=1.0,  # Collaboration requires transparency
        joy_inducing=0.9 if action == "react" else 0.7,
        composable=1.0 if action in ["post", "amend"] else 0.9,
        heterarchical=1.0,  # Collaboration is inherently heterarchical
        generative=1.0 if action == "accept" else 0.8,
    )
```

### Registration

```python
register_modality(FlowModality(
    name="collaboration",
    polynomial=COLLABORATION_POLYNOMIAL,
    value_agent=COLLABORATION_VALUE_AGENT,
    spec_path="spec/f-gents/collaboration.md",
    impl_path="agents/f/modalities/collaboration.py",
))
```

---

## The Shared Foundation

All three modalities share:

### 1. FlowState Enumeration

```python
class FlowState(Enum):
    DORMANT = "dormant"       # Created, not started
    STREAMING = "streaming"   # Active processing
    BRANCHING = "branching"   # Exploring alternatives
    CONVERGING = "converging" # Merging/synthesizing
    DRAINING = "draining"     # Finalizing output
    COLLAPSED = "collapsed"   # Terminal state
```

### 2. FlowPolynomial Laws

```
Identity:      Id >> flow ≡ flow ≡ flow >> Id
Associativity: (a >> b) >> c ≡ a >> (b >> c)
Closure:       flow(x) is always a valid FlowState
```

### 3. ValueAgent Constitution

All modalities evaluate against the same 7 Constitutional principles:

1. **Tasteful**: Each action is justified
2. **Curated**: Intentional selection over exhaustive cataloging
3. **Ethical**: Transparent, human agency preserved
4. **Joy-Inducing**: Delightful interaction
5. **Composable**: Actions compose cleanly
6. **Heterarchical**: No fixed hierarchy
7. **Generative**: Spec is compressive

### 4. Witness Integration

Every modality produces a `PolicyTrace[Mark]`:

```python
class FlowMark(Mark):
    """Witness mark for any flow modality."""
    modality: str             # "chat", "research", "collaboration"
    state: FlowState
    action: str
    constitutional_scores: PrincipleScore
    reasoning: str
```

---

## Adding New Modalities

To add a new flow modality:

### Step 1: Define Polynomial

```python
NEW_POLYNOMIAL = FlowPolynomial(
    name="new_modality",
    positions=frozenset([...]),
    directions=new_directions,
    transition=new_transition,
)
```

### Step 2: Define ValueAgent

```python
NEW_VALUE_AGENT = ValueAgent(
    name="new_modality",
    states=NEW_POLYNOMIAL.positions,
    actions=new_directions,
    transition=...,
    reward=new_constitutional_reward,
    gamma=...,
)
```

### Step 3: Register

```python
register_modality(FlowModality(
    name="new_modality",
    polynomial=NEW_POLYNOMIAL,
    value_agent=NEW_VALUE_AGENT,
    spec_path="spec/f-gents/new_modality.md",
    impl_path="agents/f/modalities/new_modality.py",
))
```

### Step 4: Write Spec

Create `spec/f-gents/new_modality.md` with:

- Polynomial configuration
- ValueAgent rewards
- Domain-specific extensions
- Grounding chain
- Test verification

---

## Modality Composition

Modalities can compose:

```python
# Research within Chat
chat_session.send("Let's explore authentication options")
# → Transitions to research flow internally
research_flow = chat_session.spawn_research("authentication")
# → research_flow uses RESEARCH_POLYNOMIAL
# → Results merge back into chat

# Collaboration within Research
research_flow.synthesize()
# → If multiple agents, transitions to collaboration
collab = research_flow.spawn_collaboration()
# → collab uses COLLABORATION_POLYNOMIAL
# → Consensus merges back into research
```

### Composition Laws

```
chat ∘ research: Chat can spawn research subflows
research ∘ collaboration: Research can spawn collaboration
(chat ∘ research) ∘ collab ≡ chat ∘ (research ∘ collab)  # Associativity
```

---

## Summary Table

| Modality | Primary States | Key Actions | Gamma | Spec |
|----------|----------------|-------------|-------|------|
| **Chat** | STREAMING | message, fork, merge | 0.99 | chat-unified.md |
| **Research** | STREAMING ↔ BRANCHING | hypothesize, prune, synthesize | 0.95 | research.md |
| **Collaboration** | STREAMING → CONVERGING | post, propose, vote, accept | 0.90 | collaboration.md |

---

*"Three modalities, one implementation. The polynomial is the same; the configuration differs."*

*Last updated: 2025-12-25*
