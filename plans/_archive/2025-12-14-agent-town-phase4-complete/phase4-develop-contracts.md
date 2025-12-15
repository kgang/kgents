---
path: plans/agent-town/phase4-develop-contracts
status: active
progress: 100
last_touched: 2025-12-14
touched_by: opus-4.5
blocking: []
enables:
  - agent-town/phase4-civilizational
session_notes: |
  DEVELOP phase complete. All 5 contracts defined with laws.
  7D eigenvectors, coalition detection, EigenTrust, API, marimo dashboard.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
entropy:
  planned: 0.05
  spent: 0.05
  returned: 0.0
---

# Agent Town Phase 4: DEVELOP Contracts

> *"Design compression: minimal specs that can regenerate code."*

---

## Executive Summary

Five contracts defined for Phase 4 implementation:

| Contract | Laws | Examples | Status |
|----------|------|----------|--------|
| CitizenEigenvectors (7D) | 3 | drift, similarity | ✓ |
| Coalition | 3 | k-clique, overlap | ✓ |
| ReputationEngine | 3 | convergence, normalization | ✓ |
| Town API | 7 endpoints | REST + SSE | ✓ |
| marimo Dashboard | 6 cells | reactive DAG | ✓ |

---

## Contract 1: CitizenEigenvectors (7D)

### Schema

```python
from dataclasses import dataclass
from math import sqrt
from typing import Iterator

@dataclass
class CitizenEigenvectors:
    """
    7D personality eigenvectors for Phase 4 citizens.

    Extends the existing 5D Eigenvectors with resilience and ambition.
    These coordinates capture personality, not behavior—behavior emerges
    from the interaction of eigenvectors with cosmotechnics and context.
    """

    # Existing 5D (from citizen.py:Eigenvectors)
    warmth: float = 0.5      # [0,1] - cold ↔ warm
    curiosity: float = 0.5   # [0,1] - incurious ↔ intensely curious
    trust: float = 0.5       # [0,1] - suspicious ↔ trusting
    creativity: float = 0.5  # [0,1] - conventional ↔ inventive
    patience: float = 0.5    # [0,1] - impatient ↔ patient

    # NEW Phase 4 dimensions
    resilience: float = 0.5  # [0,1] - fragile ↔ resilient (recovery from setbacks)
    ambition: float = 0.5    # [0,1] - content ↔ ambitious (drive for status/influence)

    def __post_init__(self) -> None:
        """Clamp all values to [0, 1]."""
        for name in self._dimension_names():
            value = getattr(self, name)
            setattr(self, name, max(0.0, min(1.0, value)))

    @staticmethod
    def _dimension_names() -> tuple[str, ...]:
        """All eigenvector dimension names."""
        return ("warmth", "curiosity", "trust", "creativity",
                "patience", "resilience", "ambition")

    def to_vector(self) -> tuple[float, ...]:
        """Convert to 7D tuple for mathematical operations."""
        return tuple(getattr(self, name) for name in self._dimension_names())

    @classmethod
    def from_vector(cls, v: tuple[float, ...]) -> "CitizenEigenvectors":
        """Create from 7D tuple."""
        names = cls._dimension_names()
        if len(v) != len(names):
            raise ValueError(f"Expected {len(names)} dimensions, got {len(v)}")
        return cls(**dict(zip(names, v)))

    def drift(self, other: "CitizenEigenvectors") -> float:
        """
        Calculate eigenvector drift (L2 distance).

        Used to enforce bounded evolution: drift must be ≤ max_drift per cycle.

        Law 1 (Identity): drift(a, a) == 0
        Law 2 (Symmetry): drift(a, b) == drift(b, a)
        Law 3 (Triangle): drift(a, c) <= drift(a, b) + drift(b, c)
        """
        v1, v2 = self.to_vector(), other.to_vector()
        return sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

    def similarity(self, other: "CitizenEigenvectors") -> float:
        """
        Calculate personality similarity (cosine similarity).

        Returns value in [-1, 1], where 1 = identical direction.
        Used for coalition formation and relationship prediction.
        """
        v1, v2 = self.to_vector(), other.to_vector()
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = sqrt(sum(a ** 2 for a in v1))
        mag2 = sqrt(sum(b ** 2 for b in v2))
        if mag1 * mag2 < 1e-10:
            return 0.0
        return dot / (mag1 * mag2)

    def apply_bounded_drift(
        self,
        deltas: dict[str, float],
        max_drift: float = 0.1
    ) -> "CitizenEigenvectors":
        """
        Apply deltas with bounded total drift.

        Scales deltas proportionally if total would exceed max_drift.
        """
        # Create proposed new eigenvectors
        new_values = {name: getattr(self, name) for name in self._dimension_names()}
        for name, delta in deltas.items():
            if name in new_values:
                new_values[name] = max(0.0, min(1.0, new_values[name] + delta))

        proposed = CitizenEigenvectors(**new_values)
        actual_drift = self.drift(proposed)

        # Scale down if exceeds max
        if actual_drift > max_drift and actual_drift > 0:
            scale = max_drift / actual_drift
            scaled_values = {}
            for name in self._dimension_names():
                old = getattr(self, name)
                new = new_values[name]
                scaled_values[name] = old + (new - old) * scale
            return CitizenEigenvectors(**scaled_values)

        return proposed

    def __iter__(self) -> Iterator[tuple[str, float]]:
        """Iterate over (dimension_name, value) pairs."""
        for name in self._dimension_names():
            yield name, getattr(self, name)
```

### Laws

| Law | Statement | Verification |
|-----|-----------|--------------|
| **L1-Identity** | `drift(a, a) == 0` | Trivially true: L2 of zero vector is 0 |
| **L2-Symmetry** | `drift(a, b) == drift(b, a)` | L2 is symmetric by definition |
| **L3-Triangle** | `drift(a, c) <= drift(a, b) + drift(b, c)` | L2 satisfies triangle inequality |

### Property Tests

```python
from hypothesis import given, strategies as st

eigenvector_st = st.fixed_dictionaries({
    name: st.floats(0.0, 1.0)
    for name in CitizenEigenvectors._dimension_names()
})

@given(e=eigenvector_st)
def test_drift_identity(e):
    """L1: drift(a, a) == 0"""
    eigen = CitizenEigenvectors(**e)
    assert eigen.drift(eigen) == 0.0

@given(e1=eigenvector_st, e2=eigenvector_st)
def test_drift_symmetry(e1, e2):
    """L2: drift(a, b) == drift(b, a)"""
    a, b = CitizenEigenvectors(**e1), CitizenEigenvectors(**e2)
    assert abs(a.drift(b) - b.drift(a)) < 1e-10

@given(e1=eigenvector_st, e2=eigenvector_st, e3=eigenvector_st)
def test_drift_triangle(e1, e2, e3):
    """L3: drift(a, c) <= drift(a, b) + drift(b, c)"""
    a = CitizenEigenvectors(**e1)
    b = CitizenEigenvectors(**e2)
    c = CitizenEigenvectors(**e3)
    assert a.drift(c) <= a.drift(b) + b.drift(c) + 1e-10
```

---

## Contract 2: 12 Cosmotechnics

### Schema

```python
from dataclasses import dataclass
from typing import Literal

CosmoName = Literal[
    # Original (Phases 1-2)
    "gathering", "construction", "exploration",
    "healing", "memory", "exchange", "cultivation",
    # Evolving (Phase 3)
    "growth", "adaptation", "synthesis",
    # NEW Phase 4
    "watchfulness", "restoration",
]

@dataclass(frozen=True)
class Cosmotechnics:
    """
    A citizen's cosmotechnics—their unique moral-cosmic-technical unity.

    12 cosmotechnics for Phase 4 (up from 10 in Phase 3).
    """
    name: CosmoName
    description: str
    metaphor: str
    opacity_statement: str = ""
    archetype_affinity: str = ""  # Which archetype this maps to


# NEW Phase 4 cosmotechnics
WATCHFULNESS = Cosmotechnics(
    name="watchfulness",
    description="Meaning arises through vigilant observation",
    metaphor="Life is watching",
    opacity_statement="There are patterns I perceive that you cannot see.",
    archetype_affinity="Watcher",
)

RESTORATION = Cosmotechnics(
    name="restoration",
    description="Meaning arises through returning to wholeness",
    metaphor="Life is restoration",
    opacity_statement="There are ruptures I mend in silence.",
    archetype_affinity="Healer",
)

# Complete cosmotechnics registry (12 total)
ALL_COSMOTECHNICS: dict[CosmoName, Cosmotechnics] = {
    "gathering": GATHERING,
    "construction": CONSTRUCTION,
    "exploration": EXPLORATION,
    "healing": HEALING,
    "memory": MEMORY,
    "exchange": EXCHANGE,
    "cultivation": CULTIVATION,
    "growth": GROWTH,
    "adaptation": ADAPTATION,
    "synthesis": SYNTHESIS,
    "watchfulness": WATCHFULNESS,
    "restoration": RESTORATION,
}
```

### Archetype Mapping

| Archetype | Primary Cosmotechnics | Secondary | Eigenvector Bias |
|-----------|----------------------|-----------|------------------|
| **Builder** | construction | synthesis | creativity↑, patience↑ |
| **Trader** | exchange | gathering | curiosity↑, trust↓, ambition↑ |
| **Healer** | healing | restoration | warmth↑, resilience↑ |
| **Scholar** | memory | synthesis | curiosity↑, patience↑ |
| **Watcher** | watchfulness | memory | patience↑, trust↑, resilience↑ |

---

## Contract 3: Coalition Detection

### Schema

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

@dataclass
class Coalition:
    """
    A group of citizens forming a coalition.

    Coalitions are detected via k-clique percolation:
    - k-clique: Complete subgraph of k nodes
    - Percolation: Two k-cliques are adjacent if they share k-1 nodes
    - Coalition: Union of adjacent k-cliques (community)

    Coalitions can overlap (same citizen in multiple coalitions).
    """

    id: str
    members: frozenset[str]  # Citizen IDs
    strength: float          # Average relationship weight, [0, 1]
    formed_at: datetime = field(default_factory=datetime.now)
    purpose: str | None = None  # Inferred or declared purpose

    # Coalition dynamics
    coherence: float = 1.0   # Internal alignment (decays without activity)
    influence: float = 0.0   # External reputation

    def overlaps(self, other: "Coalition") -> frozenset[str]:
        """Citizens in both coalitions (bridges)."""
        return self.members & other.members

    def jaccard(self, other: "Coalition") -> float:
        """Jaccard similarity between coalitions."""
        intersection = len(self.members & other.members)
        union = len(self.members | other.members)
        return intersection / union if union > 0 else 0.0

    @property
    def size(self) -> int:
        """Number of members."""
        return len(self.members)


class CoalitionDetector(Protocol):
    """Protocol for coalition detection algorithms."""

    def detect(
        self,
        env: "TownEnvironment",
        k: int = 3,
        min_weight: float = 0.5,
    ) -> list[Coalition]:
        """
        Detect coalitions in the town relationship graph.

        Args:
            env: Town environment with citizens and relationships
            k: Clique size (k=3 means triangles)
            min_weight: Minimum relationship weight to consider as edge

        Returns:
            List of detected coalitions (may overlap)
        """
        ...


class KCliqueCoalitionDetector:
    """
    k-clique percolation for overlapping coalition detection.

    Uses CDlib or pure-Python fallback.
    """

    def detect(
        self,
        env: "TownEnvironment",
        k: int = 3,
        min_weight: float = 0.5,
    ) -> list[Coalition]:
        """Detect coalitions as k-clique communities."""
        import networkx as nx

        # Build relationship graph
        G = nx.Graph()
        for citizen in env.citizens.values():
            G.add_node(citizen.id)
            for other_id, weight in citizen.relationships.items():
                if weight >= min_weight:
                    G.add_edge(citizen.id, other_id, weight=weight)

        # Find k-clique communities
        # Law: |coalition.members| >= k
        try:
            from cdlib.algorithms import kclique
            communities = kclique(G, k=k)
            raw_communities = communities.communities
        except ImportError:
            # Pure Python fallback using networkx
            from networkx.algorithms.community import k_clique_communities
            raw_communities = list(k_clique_communities(G, k))

        # Convert to Coalition objects
        coalitions = []
        for i, community in enumerate(raw_communities):
            members = frozenset(community)

            # Calculate average strength
            weights = []
            for m1 in members:
                for m2 in members:
                    if m1 < m2 and G.has_edge(m1, m2):
                        weights.append(G[m1][m2]["weight"])
            strength = sum(weights) / len(weights) if weights else 0.0

            coalition = Coalition(
                id=f"coalition_{i}",
                members=members,
                strength=strength,
            )
            coalitions.append(coalition)

        return coalitions
```

### Laws

| Law | Statement | Verification |
|-----|-----------|--------------|
| **L1-MinSize** | `len(coalition.members) >= k` | k-clique definition requires k nodes |
| **L2-Bounded** | `strength ∈ [0, 1]` | Average of weights in [0,1] |
| **L3-Overlap** | Coalition membership can overlap | k-clique percolation allows overlap |

---

## Contract 4: EigenTrust Reputation

### Schema

```python
from dataclasses import dataclass
from typing import Protocol

@dataclass
class ReputationSnapshot:
    """Snapshot of reputation state."""
    scores: dict[str, float]  # citizen_id -> reputation
    iteration: int
    converged: bool
    delta: float  # L2 change from previous iteration


class ReputationEngine(Protocol):
    """Protocol for reputation propagation."""

    def propagate(
        self,
        env: "TownEnvironment",
        pre_trusted: dict[str, float] | None = None,
        alpha: float = 0.15,
        max_iter: int = 20,
        epsilon: float = 1e-6,
    ) -> dict[str, float]:
        """
        Propagate reputation using personalized PageRank.

        trust[i] = α * pre_trusted[i] + (1-α) * Σ(trust[j] * local[j→i])

        Laws:
        - L1-Normalized: sum(reputation.values()) == 1.0
        - L2-Convergence: ||trust_n - trust_{n-1}|| < ε for some n < max_iter
        - L3-PreTrust: Pre-trusted anchors prevent sybil dominance
        """
        ...


class EigenTrustEngine:
    """
    EigenTrust-inspired reputation propagation.

    Based on: nlp.stanford.edu/pubs/eigentrust.pdf

    Key insight: Your reputation depends on WHO trusts you,
    not just HOW MANY trust you.
    """

    def propagate(
        self,
        env: "TownEnvironment",
        pre_trusted: dict[str, float] | None = None,
        alpha: float = 0.15,
        max_iter: int = 20,
        epsilon: float = 1e-6,
    ) -> dict[str, float]:
        """
        Propagate reputation using personalized PageRank variant.

        Args:
            env: Town environment
            pre_trusted: Pre-trusted citizens (archetype leaders).
                         If None, uniform distribution.
            alpha: Teleport probability (higher = more weight to pre-trusted)
            max_iter: Maximum iterations
            epsilon: Convergence threshold

        Returns:
            Normalized reputation scores (sum to 1.0)
        """
        citizen_ids = list(env.citizens.keys())
        n = len(citizen_ids)

        if n == 0:
            return {}

        # Initialize trust uniformly
        trust = {cid: 1.0 / n for cid in citizen_ids}

        # Pre-trusted anchors (default: uniform)
        if pre_trusted is None:
            pre_trusted = {cid: 1.0 / n for cid in citizen_ids}
        else:
            # Normalize pre_trusted
            total = sum(pre_trusted.values()) or 1.0
            pre_trusted = {k: v / total for k, v in pre_trusted.items()}
            # Fill missing with zero
            for cid in citizen_ids:
                if cid not in pre_trusted:
                    pre_trusted[cid] = 0.0

        # Build transition matrix (normalized outgoing trust)
        def get_outgoing_trust(citizen_id: str) -> dict[str, float]:
            """Get normalized outgoing trust from citizen."""
            citizen = env.citizens.get(citizen_id)
            if not citizen:
                return {}

            # Only positive relationships
            positive = {k: v for k, v in citizen.relationships.items() if v > 0}
            total = sum(positive.values()) or 1.0
            return {k: v / total for k, v in positive.items()}

        # Iterate until convergence
        for iteration in range(max_iter):
            new_trust = {}

            for i in citizen_ids:
                # Teleport term
                teleport = alpha * pre_trusted.get(i, 0.0)

                # Propagation term: sum of trust from those who trust me
                propagation = 0.0
                for j in citizen_ids:
                    if j == i:
                        continue
                    j_outgoing = get_outgoing_trust(j)
                    weight_j_to_i = j_outgoing.get(i, 0.0)
                    propagation += trust[j] * weight_j_to_i

                new_trust[i] = teleport + (1 - alpha) * propagation

            # Normalize (Law L1)
            total = sum(new_trust.values()) or 1.0
            new_trust = {k: v / total for k, v in new_trust.items()}

            # Check convergence (Law L2)
            delta = sum((new_trust[k] - trust[k]) ** 2 for k in citizen_ids) ** 0.5
            trust = new_trust

            if delta < epsilon:
                break

        return trust

    def update_eigenvectors(
        self,
        env: "TownEnvironment",
        reputation: dict[str, float],
        trust_scale: float = 0.1,
    ) -> None:
        """
        Apply reputation to citizen eigenvectors (trust axis).

        High reputation → trust eigenvector increases.
        Low reputation → trust eigenvector decreases.
        """
        n = len(reputation)
        mean_rep = 1.0 / n if n > 0 else 0.0

        for citizen_id, rep in reputation.items():
            citizen = env.citizens.get(citizen_id)
            if citizen is None:
                continue

            # Scale relative to mean
            delta = (rep - mean_rep) * trust_scale * n
            new_trust = max(0.0, min(1.0, citizen.eigenvectors.trust + delta))
            citizen.eigenvectors.trust = new_trust
```

### Laws

| Law | Statement | Verification |
|-----|-----------|--------------|
| **L1-Normalized** | `sum(reputation.values()) == 1.0` | Explicit normalization step |
| **L2-Convergence** | `||trust_n - trust_{n-1}|| < ε` for some n | Power iteration convergence |
| **L3-PreTrust** | Pre-trusted anchors prevent sybil dominance | α term in update equation |

---

## Contract 5: Town API

### Endpoints

```yaml
openapi: 3.0.0
info:
  title: Agent Town API
  version: 4.0.0
paths:
  /v1/town/create:
    post:
      summary: Create a new town simulation
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TownCreateRequest'
      responses:
        201:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TownCreateResponse'

  /v1/town/{id}/step:
    post:
      summary: Advance simulation by one cycle
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TownStepResponse'

  /v1/town/{id}/citizens:
    get:
      summary: List all citizens
      responses:
        200:
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CitizenSummary'

  /v1/town/{id}/citizen/{name}:
    get:
      summary: Get citizen details at specified LOD
      parameters:
        - name: lod
          in: query
          schema:
            type: integer
            minimum: 0
            maximum: 5
            default: 2
      responses:
        200:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CitizenDetail'

  /v1/town/{id}/coalitions:
    get:
      summary: Get detected coalitions
      responses:
        200:
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Coalition'

  /v1/town/{id}/events:
    get:
      summary: Server-Sent Events stream
      responses:
        200:
          content:
            text/event-stream: {}

  /v1/town/{id}/reputation:
    get:
      summary: Get EigenTrust reputation scores
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                additionalProperties:
                  type: number
```

### Pydantic Models

```python
from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID
from datetime import datetime

class TownCreateRequest(BaseModel):
    """Request to create a new town."""
    name: str = Field(..., min_length=1, max_length=100)
    template: Literal["mpp", "phase2", "phase3", "phase4"] = "phase4"
    custom_citizens: list["CitizenCreate"] | None = None

class TownCreateResponse(BaseModel):
    """Response from town creation."""
    id: UUID
    name: str
    citizens: int
    regions: int
    tier: Literal["free", "pro", "enterprise"]
    created_at: datetime

class TownStepResponse(BaseModel):
    """Response from simulation step."""
    cycle: int
    events: list["TownEvent"]
    coalitions_formed: int
    reputation_delta: dict[str, float]
    tokens_used: int
    elapsed_ms: int

class CitizenSummary(BaseModel):
    """LOD 0-1 citizen summary."""
    id: str
    name: str
    archetype: str
    region: str
    phase: str
    mood: str | None = None

class CitizenDetail(BaseModel):
    """LOD 0-5 citizen detail."""
    id: str
    name: str
    archetype: str
    region: str
    phase: str
    lod: int
    # LOD 1+
    mood: str | None = None
    # LOD 2+
    cosmotechnics: str | None = None
    metaphor: str | None = None
    # LOD 3+
    eigenvectors: dict[str, float] | None = None
    relationships: dict[str, float] | None = None
    # LOD 4+
    accursed_surplus: float | None = None
    # LOD 5
    opacity: dict | None = None

class TownEvent(BaseModel):
    """Event in the town simulation."""
    timestamp: datetime
    actor: str
    action: str
    target: str | None = None
    effect: str
    span_id: str | None = None  # OpenTelemetry span
```

### Laws

| Law | Statement | Verification |
|-----|-----------|--------------|
| **L1-LOD** | LOD 0-5 follows existing citizen.manifest() semantics | Test coverage |
| **L2-SSE** | Events include tracing span IDs | span_id field |
| **L3-Metering** | Endpoints hook into MeteringMiddleware | Integration test |

---

## Contract 6: marimo Dashboard

### Cell Structure

```python
# town_dashboard.py - marimo notebook for Agent Town Phase 4

import marimo as mo
from agents.town.environment import create_phase4_environment, TownEnvironment
from agents.town.coalition import KCliqueCoalitionDetector
from agents.town.reputation import EigenTrustEngine

# =============================================================================
# Cell 1: State Management
# =============================================================================
env = mo.state(create_phase4_environment())
coalitions = mo.state([])
reputation = mo.state({})
events_log = mo.state([])

# =============================================================================
# Cell 2: Controls
# =============================================================================
step_button = mo.ui.button("Step Simulation", kind="primary")
citizen_selector = mo.ui.dropdown(
    options={c.name: c.id for c in env.value.citizens.values()},
    label="Select Citizen",
)
lod_slider = mo.ui.slider(
    start=0, stop=5, value=2, step=1, label="Level of Detail"
)
k_slider = mo.ui.slider(
    start=2, stop=5, value=3, step=1, label="Coalition k-clique size"
)

controls = mo.vstack([
    mo.hstack([step_button, citizen_selector]),
    mo.hstack([lod_slider, k_slider]),
])

# =============================================================================
# Cell 3: Town Map (plotly network graph)
# =============================================================================
import plotly.graph_objects as go

def town_map(env: TownEnvironment, coalitions: list) -> go.Figure:
    """Render citizens as nodes, relationships as edges."""
    import networkx as nx

    G = nx.Graph()
    for c in env.citizens.values():
        G.add_node(c.id, name=c.name, region=c.region)
        for other_id, weight in c.relationships.items():
            if weight > 0.3:
                G.add_edge(c.id, other_id, weight=weight)

    pos = nx.spring_layout(G, seed=42)

    # Create edge traces
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Create node traces (colored by coalition)
    node_x = [pos[n][0] for n in G.nodes()]
    node_y = [pos[n][1] for n in G.nodes()]
    node_text = [G.nodes[n]['name'] for n in G.nodes()]

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition='top center',
        marker=dict(size=20, line_width=2),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title='Town Network',
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )
    )
    return fig

map_chart = mo.ui.plotly(town_map(env.value, coalitions.value))

# =============================================================================
# Cell 4: Eigenvector Inspector (7D radar chart)
# =============================================================================
def eigenvector_radar(citizen_id: str, env: TownEnvironment) -> go.Figure:
    """7D radar chart of personality eigenvectors."""
    citizen = env.citizens.get(citizen_id)
    if not citizen:
        return go.Figure()

    categories = ['warmth', 'curiosity', 'trust', 'creativity',
                  'patience', 'resilience', 'ambition']
    values = [getattr(citizen.eigenvectors, cat, 0.5) for cat in categories]
    values.append(values[0])  # Close the polygon

    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],
        fill='toself',
        name=citizen.name,
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title=f'{citizen.name} - 7D Eigenvectors',
    )
    return fig

inspector = mo.ui.plotly(
    eigenvector_radar(citizen_selector.value, env.value)
)

# =============================================================================
# Cell 5: Event Stream Table
# =============================================================================
events_table = mo.ui.table(
    data=events_log.value,
    pagination=True,
    page_size=10,
    label="Event Stream",
)

# =============================================================================
# Cell 6: Coalition View
# =============================================================================
def coalition_graph(coalitions: list) -> go.Figure:
    """Overlapping coalition visualization as Venn-style."""
    if not coalitions:
        return go.Figure().add_annotation(text="No coalitions detected")

    # Simple bar chart of coalition sizes
    names = [f"Coalition {i}" for i in range(len(coalitions))]
    sizes = [len(c.members) for c in coalitions]
    strengths = [c.strength for c in coalitions]

    fig = go.Figure(data=[
        go.Bar(name='Size', x=names, y=sizes),
        go.Bar(name='Strength', x=names, y=[s * 10 for s in strengths]),
    ])
    fig.update_layout(barmode='group', title='Coalitions')
    return fig

coalition_chart = mo.ui.plotly(coalition_graph(coalitions.value))

# =============================================================================
# Reactive Update Handler
# =============================================================================
@mo.on_change(step_button)
def on_step():
    """Handle step button click - advance simulation."""
    from agents.town.simulation import step_simulation

    new_env, new_events = step_simulation(env.value)
    env.set(new_env)

    # Update coalitions
    detector = KCliqueCoalitionDetector()
    new_coalitions = detector.detect(new_env, k=k_slider.value)
    coalitions.set(new_coalitions)

    # Update reputation
    engine = EigenTrustEngine()
    new_rep = engine.propagate(new_env)
    reputation.set(new_rep)

    # Append events
    events_log.set(events_log.value + new_events)

# =============================================================================
# Layout
# =============================================================================
mo.vstack([
    mo.md("# Agent Town Phase 4 Dashboard"),
    controls,
    mo.hstack([map_chart, inspector]),
    mo.hstack([events_table, coalition_chart]),
])
```

### Laws

| Law | Statement | Verification |
|-----|-----------|--------------|
| **L1-Reactive** | Change citizen_selector → inspector updates | marimo DAG |
| **L2-Pure** | Cells have no side effects except through mo.state | Code review |
| **L3-Export** | Runnable as standalone via `marimo run` | CI test |

---

## Risks

### R1: marimo Learning Curve

**Risk**: Team unfamiliarity with marimo could slow development.

**Mitigation**:
- marimo has good documentation and examples
- DAG model is simpler than Jupyter's hidden state
- Fallback: Textual TUI exists for basic visualization

**Impact**: Medium | **Likelihood**: Low

### R2: CDlib Dependency

**Risk**: CDlib may have incompatible dependencies or version conflicts.

**Mitigation**:
- NetworkX `k_clique_communities` as pure-Python fallback
- Test both paths in CI
- Pin CDlib version in pyproject.toml

**Impact**: Low | **Likelihood**: Medium

### R3: LLM Cost Overrun

**Risk**: LLM-backed citizens (3-5) could exceed budget in high-frequency simulations.

**Mitigation**:
- Hard token limit per turn (2000 tokens)
- Per-session metering via MeteringMiddleware
- Tier enforcement: Free tier caps at 10 cycles/day

**Impact**: High | **Likelihood**: Medium

### R4: Coalition Algorithm Performance

**Risk**: k-clique percolation is O(n³) worst case.

**Mitigation**:
- 25 citizens is small enough (625 operations)
- Cache coalitions between steps (invalidate on relationship change)
- Async detection for UI responsiveness

**Impact**: Low | **Likelihood**: Low

---

## Exit Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| 7D Eigenvector contract with 3 laws | ✓ | Contract 1: L1-L3 |
| Coalition contract with k-clique invariants | ✓ | Contract 3: L1-L3 |
| EigenTrust contract with convergence law | ✓ | Contract 4: L1-L3 |
| Town API spec with 7 endpoints | ✓ | Contract 5: OpenAPI |
| marimo dashboard sketch with 6 cells | ✓ | Contract 6: cells 1-6 |
| Risks documented (3+ items) | ✓ | R1-R4 |
| ledger.DEVELOP=touched | ✓ | Frontmatter |

---

## Process Metrics

| Metric | Value |
|--------|-------|
| Phase | DEVELOP |
| Contracts defined | 5 |
| Laws stated | 12 |
| Examples drafted | 6 |
| Risks documented | 4 |
| Entropy sip | 0.05 |

---

## Continuation

```
⟿[STRATEGIZE]
exit: contracts=5, laws=12, risks=4, examples=6
continuation → STRATEGIZE for chunk ordering and parallel track planning
```

---

*"The contract is the compression. From these schemas, the implementation regenerates."*
