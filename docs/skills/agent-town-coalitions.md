# Skill: Agent Town Coalitions

> Detect overlapping coalitions via k-clique percolation and manage reputation with EigenTrust

**Difficulty**: Medium
**Prerequisites**: Understanding of Agent Town citizens, eigenvectors, graph algorithms
**Files Touched**: `agents/town/coalition.py`, `agents/town/environment.py`

---

## Overview

Coalitions are groups of citizens with aligned eigenvectors. Agent Town uses:

1. **k-clique percolation** — Detect overlapping community structure
2. **EigenTrust reputation** — Weight trust by trustworthiness of assigners
3. **Coalition lifecycle** — Formation, action, decay

### Heritage

| Source | Pattern | Application |
|--------|---------|-------------|
| Palla et al. (2005) | k-clique percolation | Overlapping community detection |
| Kamvar et al. (2003) | EigenTrust | Reputation in P2P networks |
| D-gent BFS pattern | Graph traversal | k-hop neighbor discovery |

---

## Quick Start

### Detecting Coalitions

```python
from agents.town.coalition import detect_coalitions
from agents.town.environment import TownEnvironment

# Create town with citizens
town = TownEnvironment(name="Test", citizens={...})

# Detect coalitions (k=3, similarity threshold 0.6)
coalitions = detect_coalitions(
    citizens=town.citizens,
    k=3,
    similarity_threshold=0.6,
)

for c in coalitions:
    print(f"{c.name}: {c.members} (strength={c.strength:.2f})")
```

### Computing Reputation

```python
from agents.town.coalition import compute_reputation, EigenTrustConfig

# Compute EigenTrust reputation scores
reputation = compute_reputation(
    citizens=town.citizens,
    interactions=town.interaction_history,
    config=EigenTrustConfig(
        alpha=0.5,  # Damping factor
        epsilon=0.001,  # Convergence threshold
        max_iterations=100,
    ),
)

# reputation: dict[str, float] — citizen_id → reputation score [0, 1]
```

---

## Coalition Dataclass

```python
@dataclass
class Coalition:
    id: str                     # UUID prefix
    name: str                   # Human-readable name
    members: set[str]           # Citizen IDs
    formed_at: datetime         # Formation timestamp
    strength: float             # [0, 1] — decays without action
    purpose: str                # Optional coalition purpose
```

### Coalition Methods

```python
# Add/remove members
coalition.add_member("alice")
coalition.remove_member("bob")

# Compute centroid eigenvector
centroid = coalition.compute_centroid(town.citizens)

# Lifecycle
coalition.decay(rate=0.05)      # Passive decay
coalition.reinforce(amount=0.1)  # Action reinforcement

# Check if alive
if coalition.is_alive(threshold=0.1):
    ...
```

---

## K-Clique Percolation Algorithm

### How It Works

1. **Build similarity graph**: Edge between citizens if `similarity(a, b) > threshold`
2. **Find all k-cliques**: Complete subgraphs of k vertices
3. **Build clique overlap graph**: Cliques share k-1 vertices → edge
4. **Connected components**: Each component is a coalition

### Why k=3?

| k | Behavior | Use Case |
|---|----------|----------|
| 2 | Edges → clusters | Too loose for coalitions |
| **3** | Triangles → communities | Good for 25-100 citizens |
| 4 | Tetrahedra → tight groups | Too restrictive for small towns |

### Complexity

- **k-clique finding**: O(n^k) worst case
- **Practical**: O(n²) for sparse graphs (low similarity threshold)
- **Scaling**: Works well for ~100 citizens; beyond that, consider sampling

---

## EigenTrust Reputation

### The Problem

Simple trust aggregation is vulnerable to Sybil attacks (fake identities boost reputation).

### The Solution

Weight trust by the **trustworthiness of the assigner**:

```
reputation[i] = Σ_j (trust[j→i] × reputation[j])
```

Iterating to fixed point produces stable reputation scores.

### Configuration

```python
@dataclass
class EigenTrustConfig:
    alpha: float = 0.5          # Damping factor (0.5 = balanced)
    epsilon: float = 0.001      # Convergence threshold
    max_iterations: int = 100   # Safety limit
    pre_trust: dict[str, float] = field(default_factory=dict)  # Bootstrap
```

### Convergence

EigenTrust converges if:
- Damping factor α ∈ (0, 1)
- Trust matrix is row-stochastic
- Typically converges in 10-20 iterations

---

## Coalition Lifecycle

```
FORMATION → ACTION → DECAY → (DISSOLUTION | REINFORCEMENT)
                       ↑                ↓
                       └────────────────┘
```

### Formation

Coalitions form when k-clique percolation detects community structure.

```python
# Run detection periodically
coalitions = detect_coalitions(citizens, k=3, threshold=0.6)
```

### Action

Collective actions reinforce coalition strength.

```python
# When coalition acts together
coalition.reinforce(amount=0.15)
```

### Decay

Without action, coalitions decay passively.

```python
# Apply decay each time step
for coalition in coalitions:
    coalition.decay(rate=0.05)
```

### Dissolution

Coalitions dissolve when strength drops below threshold OR members < 2.

```python
alive_coalitions = [c for c in coalitions if c.is_alive(threshold=0.1)]
```

---

## Integration with Town Simulation

### In TownFlux Step

```python
async def step(self) -> AsyncIterator[TownEvent]:
    # ... generate events ...

    # Periodic coalition update
    if self.total_events % 10 == 0:
        self._update_coalitions()

    yield event

def _update_coalitions(self) -> None:
    # Detect new coalitions
    detected = detect_coalitions(self.environment.citizens, k=3)

    # Merge with existing (preserve strength)
    for new_c in detected:
        existing = self._find_matching(new_c)
        if existing:
            existing.reinforce(0.05)
        else:
            self._coalitions.append(new_c)

    # Decay all
    for c in self._coalitions:
        c.decay(0.02)

    # Prune dead coalitions
    self._coalitions = [c for c in self._coalitions if c.is_alive()]
```

### In API Response

```python
@router.get("/{town_id}/coalitions")
async def get_coalitions(town_id: str) -> list[dict]:
    flux = get_flux(town_id)
    return [c.to_dict() for c in flux._coalitions]
```

---

## Visualization

Coalitions appear in the eigenvector scatter plot as **clusters**:

```
+----------------------------------------------------------+
|                    Eigenvector Space (WT)                |
|                                                          |
|          b b b           Coalition A                     |
|           b              (Builders)                      |
|                                                          |
|                   h h           Coalition B              |
|                    h h          (Healers)                |
|                                                          |
|   t t t              Bridge nodes: t (shared k-1)        |
|    t                                                     |
+----------------------------------------------------------+
```

Bridge nodes (○) are members of multiple coalitions via shared k-1 cliques.

---

## Serialization

```python
# Coalition to dict
data = coalition.to_dict()
# {
#   "id": "abc123",
#   "name": "builders-coalition",
#   "members": ["bob", "eve", "ada"],
#   "formed_at": "2025-12-14T10:00:00",
#   "strength": 0.85,
#   "purpose": ""
# }

# Dict to Coalition
restored = Coalition.from_dict(data)
```

---

## Verification

```bash
# Run coalition tests
uv run pytest agents/town/_tests/test_coalition.py -v

# Check k-clique detection
uv run pytest agents/town/_tests/test_coalition.py -v -k "clique"

# Check EigenTrust convergence
uv run pytest agents/town/_tests/test_coalition.py -v -k "eigentrust"
```

---

## Common Pitfalls

1. **High similarity threshold**: Too high → no coalitions; too low → one giant coalition
2. **Forgetting decay**: Coalitions grow forever without passive decay
3. **EigenTrust divergence**: Check alpha and iteration limits
4. **Bridge node confusion**: Members of multiple coalitions appear in both

---

## Related Skills

- [agent-town-archetypes](agent-town-archetypes.md) — Archetype eigenvector biases
- [agent-town-visualization](agent-town-visualization.md) — Scatter plot with coalition markers
- [polynomial-agent](polynomial-agent.md) — CitizenPolynomial state machine

---

## Changelog

- 2025-12-14: Initial version (RE-METABOLIZE cycle)
