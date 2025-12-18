"""
Town Coalition Service: Coalition Detection and Reputation System.

Migrated from agents/town/coalition.py to services/ per Metaphysical
Fullstack pattern (AD-009). Business logic separated from categorical primitives.

Implements:
- k-clique percolation for overlapping coalition detection
- EigenTrust-style reputation propagation
- Coalition lifecycle (formation, action, decay)

Heritage:
- k-clique percolation: Palla et al. (2005) - overlapping community detection
- EigenTrust: Kamvar et al. (2003) - reputation in P2P networks
- Synergy S2 (agents/d/graph.py BFS pattern)

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Iterator
from uuid import uuid4

if TYPE_CHECKING:
    from agents.town.citizen import Citizen, Eigenvectors


# =============================================================================
# Coalition Types
# =============================================================================


@dataclass
class Coalition:
    """
    A coalition is a group of citizens with aligned eigenvectors.

    Coalitions are detected via k-clique percolation and evolve over time.
    They can take collective actions and share reputation.
    """

    id: str = field(default_factory=lambda: str(uuid4())[:8])
    name: str = ""
    members: set[str] = field(default_factory=set)  # citizen IDs
    formed_at: datetime = field(default_factory=datetime.now)
    strength: float = 1.0  # 0.0-1.0, decays without action
    purpose: str = ""  # Optional coalition purpose

    # Derived metrics (updated on computation)
    _centroid: Any | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if not self.name:
            self.name = f"coalition-{self.id}"

    @property
    def size(self) -> int:
        """Number of members."""
        return len(self.members)

    def add_member(self, citizen_id: str) -> None:
        """Add a member to the coalition."""
        self.members.add(citizen_id)
        self._centroid = None  # Invalidate cache

    def remove_member(self, citizen_id: str) -> None:
        """Remove a member from the coalition."""
        self.members.discard(citizen_id)
        self._centroid = None  # Invalidate cache

    def compute_centroid(self, citizens: dict[str, "Citizen"]) -> "Eigenvectors":
        """
        Compute the centroid eigenvector of the coalition.

        The centroid represents the "average personality" of the coalition.
        """
        from agents.town.citizen import Eigenvectors

        if not self.members:
            return Eigenvectors()

        # Sum eigenvectors
        totals = {
            "warmth": 0.0,
            "curiosity": 0.0,
            "trust": 0.0,
            "creativity": 0.0,
            "patience": 0.0,
            "resilience": 0.0,
            "ambition": 0.0,
        }

        count = 0
        for cid in self.members:
            citizen = citizens.get(cid)
            if citizen:
                ev = citizen.eigenvectors
                totals["warmth"] += ev.warmth
                totals["curiosity"] += ev.curiosity
                totals["trust"] += ev.trust
                totals["creativity"] += ev.creativity
                totals["patience"] += ev.patience
                totals["resilience"] += ev.resilience
                totals["ambition"] += ev.ambition
                count += 1

        if count == 0:
            return Eigenvectors()

        self._centroid = Eigenvectors(
            warmth=totals["warmth"] / count,
            curiosity=totals["curiosity"] / count,
            trust=totals["trust"] / count,
            creativity=totals["creativity"] / count,
            patience=totals["patience"] / count,
            resilience=totals["resilience"] / count,
            ambition=totals["ambition"] / count,
        )
        return self._centroid

    def decay(self, rate: float = 0.05) -> None:
        """Apply decay to coalition strength."""
        self.strength = max(0.0, self.strength - rate)

    def reinforce(self, amount: float = 0.1) -> None:
        """Reinforce coalition strength (from collective action)."""
        self.strength = min(1.0, self.strength + amount)

    def is_alive(self, threshold: float = 0.1) -> bool:
        """Check if coalition is still alive."""
        return self.strength >= threshold and len(self.members) >= 2

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "members": list(self.members),
            "formed_at": self.formed_at.isoformat(),
            "strength": self.strength,
            "purpose": self.purpose,
            "size": self.size,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Coalition:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            members=set(data["members"]),
            formed_at=datetime.fromisoformat(data["formed_at"]),
            strength=data["strength"],
            purpose=data.get("purpose", ""),
        )


# =============================================================================
# Coalition Detection (k-clique percolation)
# =============================================================================


def find_k_cliques(
    adjacency: dict[str, set[str]],
    k: int = 3,
) -> list[frozenset[str]]:
    """
    Find all k-cliques in an adjacency graph.

    A k-clique is a fully connected subgraph of k nodes.
    Uses BFS pattern from S2 (agents/d/graph.py).

    Args:
        adjacency: Node ID -> set of neighbor IDs
        k: Clique size (default 3 for triads)

    Returns:
        List of k-cliques (as frozen sets)
    """
    if k < 2:
        return []

    nodes = list(adjacency.keys())
    cliques: list[frozenset[str]] = []

    # For k=2, return all edges
    if k == 2:
        seen: set[frozenset[str]] = set()
        for node, neighbors in adjacency.items():
            for neighbor in neighbors:
                edge = frozenset([node, neighbor])
                if edge not in seen:
                    seen.add(edge)
                    cliques.append(edge)
        return cliques

    # For k>=3, use recursive extension
    def extend_clique(current: set[str], candidates: set[str]) -> Iterator[frozenset[str]]:
        if len(current) == k:
            yield frozenset(current)
            return

        for node in list(candidates):
            # Node must be connected to all current members
            if all(node in adjacency.get(m, set()) for m in current):
                new_candidates = candidates & adjacency.get(node, set())
                current.add(node)
                yield from extend_clique(current, new_candidates)
                current.remove(node)
            candidates.discard(node)

    # Start from each node
    for i, start in enumerate(nodes):
        initial_candidates = set(nodes[i + 1 :]) & adjacency.get(start, set())
        cliques.extend(extend_clique({start}, initial_candidates))

    return cliques


def percolate_cliques(
    cliques: list[frozenset[str]],
    k: int = 3,
) -> list[set[str]]:
    """
    Percolate k-cliques to find overlapping communities.

    Two k-cliques are adjacent if they share k-1 nodes.
    Communities are formed by merging adjacent cliques.

    Args:
        cliques: List of k-cliques
        k: Clique size

    Returns:
        List of communities (sets of node IDs)
    """
    if not cliques:
        return []

    # Build clique adjacency
    n = len(cliques)
    clique_adj: list[set[int]] = [set() for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            # Adjacent if share k-1 nodes
            overlap = len(cliques[i] & cliques[j])
            if overlap >= k - 1:
                clique_adj[i].add(j)
                clique_adj[j].add(i)

    # BFS to find connected components of cliques
    visited: set[int] = set()
    communities: list[set[str]] = []

    for start in range(n):
        if start in visited:
            continue

        # BFS from this clique
        community: set[str] = set()
        queue: deque[int] = deque([start])
        visited.add(start)

        while queue:
            current = queue.popleft()
            community.update(cliques[current])

            for neighbor in clique_adj[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        communities.append(community)

    return communities


def detect_coalitions(
    citizens: dict[str, "Citizen"],
    similarity_threshold: float = 0.8,
    k: int = 3,
) -> list[Coalition]:
    """
    Detect coalitions via k-clique percolation on eigenvector similarity.

    Args:
        citizens: Dict of citizen_id -> Citizen
        similarity_threshold: Min similarity for edge (default 0.8)
        k: Clique size for percolation (default 3)

    Returns:
        List of detected coalitions
    """
    # Build adjacency based on eigenvector similarity
    citizen_ids = list(citizens.keys())
    adjacency: dict[str, set[str]] = {cid: set() for cid in citizen_ids}

    for i, cid1 in enumerate(citizen_ids):
        for cid2 in citizen_ids[i + 1 :]:
            sim = citizens[cid1].eigenvectors.similarity(citizens[cid2].eigenvectors)
            if sim >= similarity_threshold:
                adjacency[cid1].add(cid2)
                adjacency[cid2].add(cid1)

    # Find k-cliques
    cliques = find_k_cliques(adjacency, k)

    # Percolate to communities
    communities = percolate_cliques(cliques, k)

    # Convert to Coalition objects
    coalitions = []
    for community in communities:
        coalition = Coalition(
            members=community,
            purpose=f"eigenvector-aligned (k={k})",
        )
        coalition.compute_centroid(citizens)
        coalitions.append(coalition)

    return coalitions


# =============================================================================
# Reputation System (EigenTrust variant)
# =============================================================================


@dataclass
class ReputationGraph:
    """
    EigenTrust-style reputation graph.

    Each citizen has a local trust rating for other citizens.
    Global reputation is computed via power iteration.
    """

    # Local trust: (truster_id, trustee_id) -> trust value
    _local_trust: dict[tuple[str, str], float] = field(default_factory=dict)
    # Global reputation: citizen_id -> reputation score
    _reputation: dict[str, float] = field(default_factory=dict)
    # Pre-trusted nodes (for convergence)
    _pretrusted: set[str] = field(default_factory=set)

    def set_trust(self, truster: str, trustee: str, value: float) -> None:
        """Set local trust from truster to trustee."""
        value = max(0.0, min(1.0, value))
        self._local_trust[(truster, trustee)] = value

    def get_trust(self, truster: str, trustee: str) -> float:
        """Get local trust from truster to trustee."""
        return self._local_trust.get((truster, trustee), 0.0)

    def add_pretrusted(self, citizen_id: str) -> None:
        """Mark a citizen as pre-trusted (anchor for convergence)."""
        self._pretrusted.add(citizen_id)

    def get_reputation(self, citizen_id: str) -> float:
        """Get global reputation for a citizen."""
        return self._reputation.get(citizen_id, 0.0)

    def compute_reputation(
        self,
        citizens: dict[str, "Citizen"],
        alpha: float = 0.5,
        iterations: int = 20,
        epsilon: float = 0.001,
    ) -> dict[str, float]:
        """
        Compute global reputation via EigenTrust power iteration.

        t(i) = (1-alpha) * sum_j(c(j,i) * t(j)) + alpha * p(i)

        Where:
        - t(i) is global trust of i
        - c(j,i) is normalized local trust from j to i
        - p(i) is pre-trust (uniform or specified)
        - alpha is mixing parameter

        Args:
            citizens: Dict of citizen_id -> Citizen
            alpha: Pre-trust mixing parameter (default 0.5)
            iterations: Max iterations (default 20)
            epsilon: Convergence threshold (default 0.001)

        Returns:
            Dict of citizen_id -> reputation score
        """
        citizen_ids = list(citizens.keys())
        n = len(citizen_ids)

        if n == 0:
            return {}

        # Initialize uniform
        reputation = {cid: 1.0 / n for cid in citizen_ids}

        # Pre-trust vector
        if self._pretrusted:
            pretrust = {cid: 0.0 for cid in citizen_ids}
            for pt in self._pretrusted:
                if pt in pretrust:
                    pretrust[pt] = 1.0 / len(self._pretrusted)
        else:
            pretrust = {cid: 1.0 / n for cid in citizen_ids}

        # Normalize local trust per truster
        normalized: dict[str, dict[str, float]] = {cid: {} for cid in citizen_ids}
        for truster in citizen_ids:
            total = sum(self._local_trust.get((truster, trustee), 0.0) for trustee in citizen_ids)
            if total > 0:
                for trustee in citizen_ids:
                    trust = self._local_trust.get((truster, trustee), 0.0)
                    if trust > 0:
                        normalized[truster][trustee] = trust / total

        # Power iteration
        for _ in range(iterations):
            new_reputation: dict[str, float] = {}

            for i in citizen_ids:
                # Sum of weighted trust from others
                trust_sum = 0.0
                for j in citizen_ids:
                    c_ji = normalized[j].get(i, 0.0)
                    trust_sum += c_ji * reputation[j]

                # Mix with pre-trust
                new_reputation[i] = (1 - alpha) * trust_sum + alpha * pretrust[i]

            # Check convergence
            max_diff = max(abs(new_reputation[cid] - reputation[cid]) for cid in citizen_ids)
            reputation = new_reputation

            if max_diff < epsilon:
                break

        self._reputation = reputation
        return reputation

    def update_from_interaction(
        self,
        truster: str,
        trustee: str,
        success: bool,
        weight: float = 0.1,
    ) -> None:
        """
        Update local trust based on interaction outcome.

        Positive interactions increase trust, negative decrease.
        """
        current = self.get_trust(truster, trustee)
        delta = weight if success else -weight
        self.set_trust(truster, trustee, current + delta)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "local_trust": [
                {"truster": k[0], "trustee": k[1], "value": v} for k, v in self._local_trust.items()
            ],
            "reputation": dict(self._reputation),
            "pretrusted": list(self._pretrusted),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReputationGraph:
        """Deserialize from dictionary."""
        graph = cls()
        for entry in data.get("local_trust", []):
            graph._local_trust[(entry["truster"], entry["trustee"])] = entry["value"]
        graph._reputation = dict(data.get("reputation", {}))
        graph._pretrusted = set(data.get("pretrusted", []))
        return graph


# =============================================================================
# Coalition Service (Manager)
# =============================================================================


class CoalitionService:
    """
    Service for managing coalition lifecycle and reputation.

    Combines:
    - Coalition detection via k-clique percolation
    - Reputation tracking via EigenTrust
    - Coalition decay and reinforcement
    """

    def __init__(
        self,
        similarity_threshold: float = 0.8,
        k: int = 3,
    ) -> None:
        """
        Initialize coalition service.

        Args:
            similarity_threshold: Min similarity for coalition edge
            k: Clique size for detection
        """
        self._similarity_threshold = similarity_threshold
        self._k = k
        self._coalitions: dict[str, Coalition] = {}
        self._reputation = ReputationGraph()

    @property
    def coalitions(self) -> dict[str, Coalition]:
        """Get all coalitions."""
        return self._coalitions

    @property
    def reputation(self) -> ReputationGraph:
        """Get reputation graph."""
        return self._reputation

    def detect(self, citizens: dict[str, "Citizen"]) -> list[Coalition]:
        """Detect coalitions and update internal state."""
        coalitions = detect_coalitions(
            citizens,
            self._similarity_threshold,
            self._k,
        )
        self._coalitions = {c.id: c for c in coalitions}
        return coalitions

    def get_coalition(self, coalition_id: str) -> Coalition | None:
        """Get a coalition by ID."""
        return self._coalitions.get(coalition_id)

    def get_citizen_coalitions(self, citizen_id: str) -> list[Coalition]:
        """Get all coalitions a citizen belongs to."""
        return [c for c in self._coalitions.values() if citizen_id in c.members]

    def get_bridge_citizens(self) -> list[str]:
        """Get citizens that belong to multiple coalitions (bridge nodes)."""
        membership_count: dict[str, int] = {}
        for coalition in self._coalitions.values():
            for member in coalition.members:
                membership_count[member] = membership_count.get(member, 0) + 1
        return [cid for cid, count in membership_count.items() if count > 1]

    def decay_all(self, rate: float = 0.05) -> int:
        """Apply decay to all coalitions. Returns number pruned."""
        pruned = 0
        to_remove = []
        for cid, coalition in self._coalitions.items():
            coalition.decay(rate)
            if not coalition.is_alive():
                to_remove.append(cid)
                pruned += 1
        for cid in to_remove:
            del self._coalitions[cid]
        return pruned

    def reinforce_coalition(self, coalition_id: str, amount: float = 0.1) -> bool:
        """Reinforce a coalition's strength."""
        if coalition_id in self._coalitions:
            self._coalitions[coalition_id].reinforce(amount)
            return True
        return False

    def record_interaction(
        self,
        actor: str,
        target: str,
        success: bool,
    ) -> None:
        """Record an interaction for reputation updates."""
        self._reputation.update_from_interaction(actor, target, success)

    def compute_reputation(
        self, citizens: dict[str, "Citizen"], alpha: float = 0.5
    ) -> dict[str, float]:
        """Compute global reputation scores."""
        return self._reputation.compute_reputation(citizens, alpha)

    def summary(self) -> dict[str, Any]:
        """Get summary statistics."""
        return {
            "total_coalitions": len(self._coalitions),
            "alive_coalitions": sum(1 for c in self._coalitions.values() if c.is_alive()),
            "total_members": sum(c.size for c in self._coalitions.values()),
            "bridge_citizens": len(self.get_bridge_citizens()),
            "avg_strength": (
                sum(c.strength for c in self._coalitions.values()) / len(self._coalitions)
                if self._coalitions
                else 0.0
            ),
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize service state."""
        return {
            "coalitions": [c.to_dict() for c in self._coalitions.values()],
            "reputation": self._reputation.to_dict(),
            "config": {
                "similarity_threshold": self._similarity_threshold,
                "k": self._k,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CoalitionService:
        """Deserialize service state."""
        config = data.get("config", {})
        service = cls(
            similarity_threshold=config.get("similarity_threshold", 0.8),
            k=config.get("k", 3),
        )
        for c_data in data.get("coalitions", []):
            coalition = Coalition.from_dict(c_data)
            service._coalitions[coalition.id] = coalition
        if "reputation" in data:
            service._reputation = ReputationGraph.from_dict(data["reputation"])
        return service


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Types
    "Coalition",
    "ReputationGraph",
    # Detection functions
    "find_k_cliques",
    "percolate_cliques",
    "detect_coalitions",
    # Service
    "CoalitionService",
]
