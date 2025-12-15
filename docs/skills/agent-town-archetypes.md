# Skill: Agent Town Archetypes

> Create and manage citizen archetypes with eigenvector biases

**Difficulty**: Easy-Medium
**Prerequisites**: Understanding of Agent Town citizens, eigenvectors
**Files Touched**: `agents/town/archetypes.py`, `agents/town/citizen.py`

---

## Overview

Archetypes represent cosmotechnical approaches to the world. Each archetype has:
1. **Eigenvector biases** — Deviations from 0.5 baseline
2. **Cosmotechnics** — Associated skill/technique
3. **Factory functions** — Create citizens with appropriate defaults

### The Five Archetypes

| Archetype | Cosmotechnics | Key Biases | Role |
|-----------|---------------|------------|------|
| **Builder** | CONSTRUCTION_V2 | creativity↑, patience↑, ambition↑ | Infrastructure creation |
| **Trader** | EXCHANGE_V2 | curiosity↑, trust↓, ambition↑↑ | Resource exchange |
| **Healer** | RESTORATION | warmth↑↑, patience↑, trust↑ | Social/emotional repair |
| **Scholar** | SYNTHESIS_V2 | curiosity↑↑, patience↑ | Skill discovery, teaching |
| **Watcher** | MEMORY_V2 | patience↑↑, trust↑, resilience↑ | Memory witnesses, historians |

---

## Quick Start

### Creating an Archetype Citizen

```python
from agents.town.archetypes import create_builder, create_healer

# Create a builder
bob = create_builder("bob", seed=42)
print(bob.eigenvectors.creativity)  # ~0.7 (baseline 0.5 + bias 0.2)

# Create a healer
eve = create_healer("eve")
print(eve.eigenvectors.warmth)  # ~0.75 (baseline 0.5 + bias 0.25)
```

### Creating Evolving Archetypes

```python
from agents.town.archetypes import create_archetype, ArchetypeKind
from agents.town.evolving import create_evolving_citizen

# Create via generic factory
scholar = create_archetype("ada", ArchetypeKind.SCHOLAR)

# Create evolving version (N-Phase lifecycle)
evolving_scholar = create_evolving_citizen(scholar)
```

---

## Archetype Specifications

### ArchetypeSpec Dataclass

```python
@dataclass(frozen=True)
class ArchetypeSpec:
    kind: ArchetypeKind
    cosmotechnics: Cosmotechnics
    warmth_bias: float = 0.0      # [-0.5, 0.5]
    curiosity_bias: float = 0.0
    trust_bias: float = 0.0
    creativity_bias: float = 0.0
    patience_bias: float = 0.0
    resilience_bias: float = 0.0
    ambition_bias: float = 0.0
```

### The Registry

```python
from agents.town.archetypes import ARCHETYPE_SPECS, ArchetypeKind

# Access spec
builder_spec = ARCHETYPE_SPECS[ArchetypeKind.BUILDER]
print(builder_spec.creativity_bias)  # 0.2
```

---

## Eigenvector Space (7D)

Each citizen has 7 eigenvector dimensions:

| Dimension | Description | Range |
|-----------|-------------|-------|
| **Warmth** | Social disposition | [0, 1] |
| **Curiosity** | Openness to new information | [0, 1] |
| **Trust** | Willingness to cooperate | [0, 1] |
| **Creativity** | Novel solution generation | [0, 1] |
| **Patience** | Tolerance for delay | [0, 1] |
| **Resilience** | Recovery from setbacks | [0, 1] |
| **Ambition** | Goal-seeking intensity | [0, 1] |

### Operations on Eigenvectors

```python
from agents.town.citizen import Eigenvectors

ev1 = citizen_a.eigenvectors
ev2 = citizen_b.eigenvectors

# Cosine similarity (for coalition detection)
similarity = ev1.similarity(ev2)  # [0, 1]

# Bounded drift (evolution)
new_ev = ev1.drift(warmth=0.05, creativity=-0.02)  # Clamped to [0, 1]
```

### Drift Laws (7D Metric)

The eigenvector space preserves metric laws:

| Law | Description | Verification |
|-----|-------------|--------------|
| **Identity** | `drift(0, ..., 0) = self` | `ev.drift() == ev` |
| **Symmetry** | `dist(a, b) = dist(b, a)` | `ev1.similarity(ev2) == ev2.similarity(ev1)` |
| **Triangle** | `dist(a, c) <= dist(a, b) + dist(b, c)` | Cosine distance forms metric |

---

## Factory Patterns

### Simple Factory

```python
def create_builder(name: str, seed: int | None = None) -> Citizen:
    """Create a Builder archetype citizen."""
    return create_archetype(name, ArchetypeKind.BUILDER, seed=seed)
```

### Generic Factory

```python
from agents.town.archetypes import create_archetype, ArchetypeKind

# Create any archetype
citizen = create_archetype(
    name="alice",
    kind=ArchetypeKind.HEALER,
    seed=42,  # Reproducible variance
)
```

### Evolving Factory

```python
from agents.town.archetypes import create_evolving_archetype, ArchetypeKind

# Create evolving citizen with N-Phase lifecycle
evolving = create_evolving_archetype(
    name="ada",
    kind=ArchetypeKind.SCHOLAR,
)
# evolving has: lifecycle_phase, evolve(), decay()
```

---

## Composing Archetypes

### Town with Mixed Archetypes

```python
from agents.town.environment import TownEnvironment
from agents.town.archetypes import (
    create_builder, create_trader, create_healer,
    create_scholar, create_watcher,
)

# Create a balanced town (Phase 4 recipe)
town = TownEnvironment(
    name="Harmony",
    citizens={
        "bob": create_builder("bob"),
        "eve": create_trader("eve"),
        "dan": create_healer("dan"),
        "ada": create_scholar("ada"),
        "max": create_watcher("max"),
    },
)
```

### 25-Citizen Town (Phase 4 Default)

```python
from agents.town.environment import create_phase4_environment

# Creates 25 citizens: 5 archetypes x 5 each
town = create_phase4_environment(name="Metropolis")
```

---

## Heritage Papers Realized

| Paper | Implementation |
|-------|---------------|
| **CHATDEV** | Multi-agent roles (Builder, Trader, Healer, Scholar, Watcher) |
| **SIMULACRA** | GraphMemory + eigenvector personalities |
| **AGENT HOSPITAL** | Domain-specific simulation template |

---

## Verification

```bash
# Run archetype tests
uv run pytest agents/town/_tests/test_archetypes.py -v

# Check eigenvector laws
uv run pytest agents/town/_tests/test_citizen.py -v -k "eigenvector"
```

---

## Common Pitfalls

1. **Bias overflow**: Biases are clamped, but large biases + variance can hit bounds
2. **Seed determinism**: Without seed, variance is random—tests may flake
3. **Coalition homogeneity**: All same archetype → no interesting dynamics

---

## Related Skills

- [polynomial-agent](polynomial-agent.md) — CitizenPolynomial state machine
- [agent-town-coalitions](agent-town-coalitions.md) — Coalition detection
- [agent-town-visualization](agent-town-visualization.md) — Eigenvector scatter plots

---

## Changelog

- 2025-12-14: Initial version (RE-METABOLIZE cycle)
