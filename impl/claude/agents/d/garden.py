"""
MemoryGarden: Memory with lifecycle, trust, and cultivation.

The Memory Garden provides a joy-inducing metaphor for data management:
- Seeds: New ideas, unvalidated hypotheses (low trust, high potential)
- Saplings: Emerging patterns, growing certainty
- Trees: Established knowledge, high trust
- Flowers: Peak insights, ready for harvesting
- Compost: Deprecated ideas, recycled into new growth
- Mycelium: Hidden connections (relational lattice)

Philosophy: "Data management should feel like gardening, not filing."

Part of the Noosphere Layer (D-gent Phase 4).
"""

from __future__ import annotations

from typing import TypeVar, Generic, List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path

from .errors import NoosphereError

S = TypeVar("S")  # State type


class Lifecycle(Enum):
    """Lifecycle stages for garden entries."""

    SEED = "seed"  # New, unvalidated
    SAPLING = "sapling"  # Growing, partially validated
    TREE = "tree"  # Established, high trust
    FLOWER = "flower"  # Peak insight, ready for harvest
    COMPOST = "compost"  # Deprecated, being recycled


class EvidenceType(Enum):
    """Types of evidence that affect trust."""

    SUPPORTING = "supporting"  # Increases trust
    CONTRADICTING = "contradicting"  # Decreases trust
    NEUTRAL = "neutral"  # No effect, but recorded


@dataclass
class Evidence:
    """Evidence for or against an entry."""

    id: str
    entry_id: str
    evidence_type: EvidenceType
    content: str
    source: str
    confidence: float  # 0.0-1.0: How reliable is this evidence?
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def weight(self) -> float:
        """Effective weight based on type and confidence."""
        if self.evidence_type == EvidenceType.SUPPORTING:
            return self.confidence
        elif self.evidence_type == EvidenceType.CONTRADICTING:
            return -self.confidence
        return 0.0


@dataclass
class Contradiction:
    """A recorded contradiction to an entry."""

    id: str
    entry_id: str
    contradicting_entry_id: Optional[str]  # If from another entry
    description: str
    severity: float  # 0.0-1.0
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution: Optional[str] = None


@dataclass
class Insight:
    """A harvested insight from a flower."""

    id: str
    source_entry_id: str
    content: Any
    confidence: float
    harvest_timestamp: datetime = field(default_factory=datetime.now)
    applications: List[str] = field(default_factory=list)  # Where it's been used


@dataclass
class Nutrients:
    """Decomposed nutrients from composted entries."""

    source_entry_id: str
    concepts: List[str]  # Extracted concepts
    lessons: List[str]  # What was learned from deprecation
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class GardenEntry(Generic[S]):
    """
    An entry in the Memory Garden.

    Trust evolves based on:
    - Supporting evidence increases trust
    - Contradictions decrease trust (but don't immediately kill)
    - Time without nurturing causes decay (unused ideas wilt)
    - Successful harvests increase trust of connected entries
    """

    id: str
    content: S
    lifecycle: Lifecycle = Lifecycle.SEED
    trust: float = 0.3  # 0.0-1.0: Initial seed trust is low
    hypothesis: str = ""  # Description/hypothesis about this entry

    # Lifecycle timestamps
    planted_at: datetime = field(default_factory=datetime.now)
    last_nurtured: datetime = field(default_factory=datetime.now)
    last_pruned: Optional[datetime] = None
    composted_at: Optional[datetime] = None

    # Evidence tracking
    evidence: List[Evidence] = field(default_factory=list)
    contradictions: List[Contradiction] = field(default_factory=list)

    # Relationships (mycelium)
    connections: List[str] = field(default_factory=list)  # Connected entry IDs

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    @property
    def age_days(self) -> float:
        """Age since planting in days."""
        return (datetime.now() - self.planted_at).total_seconds() / 86400

    @property
    def days_since_nurture(self) -> float:
        """Days since last nurturing."""
        return (datetime.now() - self.last_nurtured).total_seconds() / 86400

    @property
    def is_wilting(self) -> bool:
        """Entry hasn't been nurtured recently."""
        return self.days_since_nurture > 7 and self.lifecycle != Lifecycle.COMPOST

    @property
    def net_evidence_weight(self) -> float:
        """Net weight of all evidence."""
        return sum(e.weight for e in self.evidence)


@dataclass
class GardenStats:
    """Statistics about the garden."""

    total_entries: int
    seeds: int
    saplings: int
    trees: int
    flowers: int
    compost: int
    average_trust: float
    wilting_count: int
    total_evidence: int
    total_contradictions: int
    connection_count: int


class MemoryGarden(Generic[S]):
    """
    Joy-inducing memory management as gardening.

    The Memory Garden provides:
    - Lifecycle tracking: seed → sapling → tree → flower → compost
    - Trust evolution: Evidence increases/decreases trust
    - Nurturing: Active engagement keeps entries healthy
    - Harvesting: Extract peak insights
    - Composting: Recycle deprecated ideas
    - Mycelium: Track hidden connections

    Philosophy: "Data management should feel like gardening, not filing."

    Example:
        >>> garden = MemoryGarden()
        >>>
        >>> # Plant a seed (new hypothesis)
        >>> entry = await garden.plant(
        ...     {"idea": "Composable agents are better"},
        ...     hypothesis="Composition leads to maintainability"
        ... )
        >>>
        >>> # Nurture with evidence
        >>> await garden.nurture(entry.id, Evidence(
        ...     id="ev1",
        ...     entry_id=entry.id,
        ...     evidence_type=EvidenceType.SUPPORTING,
        ...     content="Reduced code by 60%",
        ...     source="zen-agents experiment",
        ...     confidence=0.9
        ... ))
        >>>
        >>> # Check lifecycle
        >>> entry = await garden.get(entry.id)
        >>> print(f"Lifecycle: {entry.lifecycle}, Trust: {entry.trust}")
        >>>
        >>> # When ready, harvest the insight
        >>> if entry.lifecycle == Lifecycle.FLOWER:
        ...     insight = await garden.harvest(entry.id)
        ...     print(f"Insight: {insight.content}")
    """

    def __init__(
        self,
        persistence_path: Optional[str] = None,
        trust_decay_rate: float = 0.01,  # Trust decay per day without nurturing
        wilting_threshold_days: float = 7.0,
        auto_lifecycle: bool = True,  # Auto-promote based on trust
    ):
        """
        Initialize memory garden.

        Args:
            persistence_path: Optional path for persistent storage
            trust_decay_rate: How fast trust decays without nurturing
            wilting_threshold_days: Days without nurturing before wilting
            auto_lifecycle: Automatically promote lifecycle based on trust
        """
        self.persistence_path = Path(persistence_path) if persistence_path else None
        self.trust_decay_rate = trust_decay_rate
        self.wilting_threshold_days = wilting_threshold_days
        self.auto_lifecycle = auto_lifecycle

        # Storage
        self._entries: Dict[str, GardenEntry[S]] = {}
        self._insights: Dict[str, Insight] = {}
        self._nutrients: List[Nutrients] = []
        self._evidence_counter = 0
        self._contradiction_counter = 0
        self._insight_counter = 0

        if self.persistence_path and self.persistence_path.exists():
            self._load_from_disk()

    # === Planting ===

    async def plant(
        self,
        content: S,
        hypothesis: str = "",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        initial_trust: float = 0.3,
    ) -> GardenEntry[S]:
        """
        Plant a new seed in the garden.

        Seeds have low trust but high potential.
        They need nurturing (evidence) to grow.
        """
        entry_id = f"entry_{len(self._entries)}_{datetime.now().timestamp()}"

        entry = GardenEntry(
            id=entry_id,
            content=content,
            lifecycle=Lifecycle.SEED,
            trust=initial_trust,
            hypothesis=hypothesis,
            tags=tags or [],
            metadata=metadata or {},
        )

        # Auto-update lifecycle based on initial trust
        if self.auto_lifecycle:
            entry = self._update_lifecycle(entry)

        self._entries[entry_id] = entry
        self._save_if_persistent()

        return entry

    # === Nurturing ===

    async def nurture(
        self,
        entry_id: str,
        evidence: Evidence,
    ) -> GardenEntry[S]:
        """
        Nurture an entry with evidence.

        As a sapling receives evidence, it grows toward tree status.
        Contradictory evidence may cause trust decay.
        """
        entry = self._entries.get(entry_id)
        if entry is None:
            raise NoosphereError(f"Entry not found: {entry_id}")

        if entry.lifecycle == Lifecycle.COMPOST:
            raise NoosphereError(f"Cannot nurture composted entry: {entry_id}")

        # Add evidence
        entry.evidence.append(evidence)
        entry.last_nurtured = datetime.now()

        # Update trust based on evidence
        trust_delta = evidence.weight * 0.1  # Scale weight to trust impact
        entry.trust = max(0.0, min(1.0, entry.trust + trust_delta))

        # Auto-promote lifecycle if enabled
        if self.auto_lifecycle:
            entry = self._update_lifecycle(entry)

        self._save_if_persistent()
        return entry

    async def add_contradiction(
        self,
        entry_id: str,
        description: str,
        severity: float = 0.5,
        contradicting_entry_id: Optional[str] = None,
    ) -> Contradiction:
        """
        Record a contradiction to an entry.

        Contradictions decrease trust but don't immediately kill.
        They can be resolved later.
        """
        entry = self._entries.get(entry_id)
        if entry is None:
            raise NoosphereError(f"Entry not found: {entry_id}")

        self._contradiction_counter += 1
        contradiction = Contradiction(
            id=f"contradiction_{self._contradiction_counter}",
            entry_id=entry_id,
            contradicting_entry_id=contradicting_entry_id,
            description=description,
            severity=severity,
        )

        entry.contradictions.append(contradiction)
        entry.trust = max(0.0, entry.trust - severity * 0.2)
        entry.last_nurtured = datetime.now()

        if self.auto_lifecycle:
            self._update_lifecycle(entry)

        self._save_if_persistent()
        return contradiction

    async def resolve_contradiction(
        self,
        entry_id: str,
        contradiction_id: str,
        resolution: str,
    ) -> None:
        """Resolve a contradiction."""
        entry = self._entries.get(entry_id)
        if entry is None:
            raise NoosphereError(f"Entry not found: {entry_id}")

        for contradiction in entry.contradictions:
            if contradiction.id == contradiction_id:
                contradiction.resolved = True
                contradiction.resolution = resolution
                # Partial trust recovery
                entry.trust = min(1.0, entry.trust + 0.05)
                break

        self._save_if_persistent()

    # === Harvesting ===

    async def harvest(self, entry_id: str) -> Insight:
        """
        Harvest a flower for its insight.

        Peak insights (flowers) are ready for use.
        Harvesting doesn't destroy—it transforms.
        """
        entry = self._entries.get(entry_id)
        if entry is None:
            raise NoosphereError(f"Entry not found: {entry_id}")

        if entry.lifecycle != Lifecycle.FLOWER:
            raise NoosphereError(
                f"Entry {entry_id} is not ready for harvest "
                f"(lifecycle={entry.lifecycle}, need FLOWER)"
            )

        self._insight_counter += 1
        insight = Insight(
            id=f"insight_{self._insight_counter}",
            source_entry_id=entry_id,
            content=entry.content,
            confidence=entry.trust,
        )

        self._insights[insight.id] = insight

        # Entry can return to tree status after harvest
        entry.lifecycle = Lifecycle.TREE
        entry.last_nurtured = datetime.now()

        self._save_if_persistent()
        return insight

    # === Pruning ===

    async def prune(
        self,
        entry_id: str,
        reason: str,
    ) -> GardenEntry[S]:
        """
        Prune outdated branches from an entry.

        Even established trees need pruning.
        Removed material is noted but entry remains.
        """
        entry = self._entries.get(entry_id)
        if entry is None:
            raise NoosphereError(f"Entry not found: {entry_id}")

        entry.last_pruned = datetime.now()
        entry.metadata["last_prune_reason"] = reason

        # Slight trust decrease from pruning (removes certainty)
        entry.trust = max(0.0, entry.trust - 0.05)

        if self.auto_lifecycle:
            self._update_lifecycle(entry)

        self._save_if_persistent()
        return entry

    # === Composting ===

    async def compost(self, entry_id: str) -> Nutrients:
        """
        Compost a deprecated entry.

        Nothing is truly deleted—deprecated ideas become nutrients
        for future growth. This is the Accursed Share principle:
        excess feeds the system's evolution.
        """
        entry = self._entries.get(entry_id)
        if entry is None:
            raise NoosphereError(f"Entry not found: {entry_id}")

        # Extract nutrients before composting
        concepts = entry.tags + [entry.hypothesis] if entry.hypothesis else entry.tags
        lessons = [
            f"Deprecated with trust {entry.trust:.2f}",
            f"Had {len(entry.evidence)} evidence items",
            f"Had {len(entry.contradictions)} contradictions",
        ]

        nutrients = Nutrients(
            source_entry_id=entry_id,
            concepts=concepts,
            lessons=lessons,
        )

        self._nutrients.append(nutrients)

        # Mark as compost
        entry.lifecycle = Lifecycle.COMPOST
        entry.composted_at = datetime.now()

        self._save_if_persistent()
        return nutrients

    # === Mycelium (Connections) ===

    async def connect(
        self,
        entry_a: str,
        entry_b: str,
        bidirectional: bool = True,
    ) -> None:
        """
        Establish a mycelium connection between entries.

        The mycelium connects entries in non-obvious ways,
        like fungal networks in forests.
        """
        a = self._entries.get(entry_a)
        b = self._entries.get(entry_b)

        if a is None:
            raise NoosphereError(f"Entry not found: {entry_a}")
        if b is None:
            raise NoosphereError(f"Entry not found: {entry_b}")

        if entry_b not in a.connections:
            a.connections.append(entry_b)

        if bidirectional and entry_a not in b.connections:
            b.connections.append(entry_a)

        self._save_if_persistent()

    async def trace_mycelium(
        self,
        entry_id: str,
        max_depth: int = 3,
    ) -> List[GardenEntry[S]]:
        """
        Trace mycelium connections from an entry.

        Find hidden connections in the garden.
        """
        entry = self._entries.get(entry_id)
        if entry is None:
            raise NoosphereError(f"Entry not found: {entry_id}")

        visited = {entry_id}
        to_visit = [(c, 1) for c in entry.connections]
        connected = []

        while to_visit:
            current_id, depth = to_visit.pop(0)
            if current_id in visited:
                continue
            if depth > max_depth:
                continue

            visited.add(current_id)
            current = self._entries.get(current_id)
            if current:
                connected.append(current)
                for c in current.connections:
                    if c not in visited:
                        to_visit.append((c, depth + 1))

        return connected

    # === Retrieval ===

    async def get(self, entry_id: str) -> Optional[GardenEntry[S]]:
        """Get entry by ID."""
        entry = self._entries.get(entry_id)
        if entry and self.auto_lifecycle:
            # Check for wilting/decay
            self._apply_decay(entry)
        return entry

    async def list_entries(
        self,
        lifecycle: Optional[Lifecycle] = None,
        min_trust: float = 0.0,
        tags: Optional[List[str]] = None,
    ) -> List[GardenEntry[S]]:
        """List entries with optional filters."""
        results = []
        for entry in self._entries.values():
            if lifecycle and entry.lifecycle != lifecycle:
                continue
            if entry.trust < min_trust:
                continue
            if tags and not any(t in entry.tags for t in tags):
                continue
            results.append(entry)
        return results

    async def seeds(self) -> List[GardenEntry[S]]:
        """Get all seeds."""
        return await self.list_entries(lifecycle=Lifecycle.SEED)

    async def saplings(self) -> List[GardenEntry[S]]:
        """Get all saplings."""
        return await self.list_entries(lifecycle=Lifecycle.SAPLING)

    async def trees(self) -> List[GardenEntry[S]]:
        """Get all established trees."""
        return await self.list_entries(lifecycle=Lifecycle.TREE)

    async def flowers(self) -> List[GardenEntry[S]]:
        """Get all flowers ready for harvest."""
        return await self.list_entries(lifecycle=Lifecycle.FLOWER)

    async def wilting(self) -> List[GardenEntry[S]]:
        """Get all wilting entries that need attention."""
        return [e for e in self._entries.values() if e.is_wilting]

    async def insights(self, limit: Optional[int] = None) -> List[Insight]:
        """Get harvested insights."""
        results = list(self._insights.values())
        results.sort(key=lambda i: i.harvest_timestamp, reverse=True)
        return results[:limit] if limit else results

    async def nutrients_available(self) -> List[Nutrients]:
        """Get available nutrients from composted entries."""
        return list(self._nutrients)

    # === Statistics ===

    async def stats(self) -> GardenStats:
        """Get garden statistics."""
        entries = list(self._entries.values())

        lifecycle_counts = {lc: 0 for lc in Lifecycle}
        for entry in entries:
            lifecycle_counts[entry.lifecycle] += 1

        trusts = [e.trust for e in entries if e.lifecycle != Lifecycle.COMPOST]
        avg_trust = sum(trusts) / len(trusts) if trusts else 0.0

        total_evidence = sum(len(e.evidence) for e in entries)
        total_contradictions = sum(len(e.contradictions) for e in entries)
        total_connections = sum(len(e.connections) for e in entries)

        return GardenStats(
            total_entries=len(entries),
            seeds=lifecycle_counts[Lifecycle.SEED],
            saplings=lifecycle_counts[Lifecycle.SAPLING],
            trees=lifecycle_counts[Lifecycle.TREE],
            flowers=lifecycle_counts[Lifecycle.FLOWER],
            compost=lifecycle_counts[Lifecycle.COMPOST],
            average_trust=avg_trust,
            wilting_count=len([e for e in entries if e.is_wilting]),
            total_evidence=total_evidence,
            total_contradictions=total_contradictions,
            connection_count=total_connections // 2,  # Bidirectional counted once
        )

    # === Internal Methods ===

    def _update_lifecycle(self, entry: GardenEntry[S]) -> GardenEntry[S]:
        """Auto-update lifecycle based on trust."""
        if entry.lifecycle == Lifecycle.COMPOST:
            return entry

        if entry.trust < 0.1:
            # Very low trust - consider composting
            entry.lifecycle = Lifecycle.SEED
        elif entry.trust < 0.3:
            entry.lifecycle = Lifecycle.SEED
        elif entry.trust < 0.5:
            entry.lifecycle = Lifecycle.SAPLING
        elif entry.trust < 0.8:
            entry.lifecycle = Lifecycle.TREE
        else:
            entry.lifecycle = Lifecycle.FLOWER

        return entry

    def _apply_decay(self, entry: GardenEntry[S]) -> None:
        """Apply trust decay for entries not recently nurtured."""
        if entry.lifecycle == Lifecycle.COMPOST:
            return

        days_since = entry.days_since_nurture
        if days_since > 1:
            decay = self.trust_decay_rate * days_since
            entry.trust = max(0.0, entry.trust - decay)

            if self.auto_lifecycle:
                self._update_lifecycle(entry)

    def _save_if_persistent(self) -> None:
        """Save to disk if persistence is enabled."""
        if self.persistence_path:
            self._save_to_disk()

    def _save_to_disk(self) -> None:
        """Save garden to disk."""
        if self.persistence_path is None:
            return

        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "entries": {
                entry_id: {
                    "id": e.id,
                    "content": e.content,
                    "lifecycle": e.lifecycle.value,
                    "trust": e.trust,
                    "hypothesis": e.hypothesis,
                    "planted_at": e.planted_at.isoformat(),
                    "last_nurtured": e.last_nurtured.isoformat(),
                    "last_pruned": e.last_pruned.isoformat() if e.last_pruned else None,
                    "composted_at": e.composted_at.isoformat()
                    if e.composted_at
                    else None,
                    "evidence": [
                        {
                            "id": ev.id,
                            "entry_id": ev.entry_id,
                            "evidence_type": ev.evidence_type.value,
                            "content": ev.content,
                            "source": ev.source,
                            "confidence": ev.confidence,
                            "timestamp": ev.timestamp.isoformat(),
                            "metadata": ev.metadata,
                        }
                        for ev in e.evidence
                    ],
                    "contradictions": [
                        {
                            "id": c.id,
                            "entry_id": c.entry_id,
                            "contradicting_entry_id": c.contradicting_entry_id,
                            "description": c.description,
                            "severity": c.severity,
                            "timestamp": c.timestamp.isoformat(),
                            "resolved": c.resolved,
                            "resolution": c.resolution,
                        }
                        for c in e.contradictions
                    ],
                    "connections": e.connections,
                    "metadata": e.metadata,
                    "tags": e.tags,
                }
                for entry_id, e in self._entries.items()
            },
            "insights": {
                insight_id: {
                    "id": i.id,
                    "source_entry_id": i.source_entry_id,
                    "content": i.content,
                    "confidence": i.confidence,
                    "harvest_timestamp": i.harvest_timestamp.isoformat(),
                    "applications": i.applications,
                }
                for insight_id, i in self._insights.items()
            },
            "nutrients": [
                {
                    "source_entry_id": n.source_entry_id,
                    "concepts": n.concepts,
                    "lessons": n.lessons,
                    "timestamp": n.timestamp.isoformat(),
                }
                for n in self._nutrients
            ],
            "counters": {
                "evidence": self._evidence_counter,
                "contradiction": self._contradiction_counter,
                "insight": self._insight_counter,
            },
        }

        temp_path = self.persistence_path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        temp_path.replace(self.persistence_path)

    def _load_from_disk(self) -> None:
        """Load garden from disk."""
        if self.persistence_path is None or not self.persistence_path.exists():
            return

        try:
            with open(self.persistence_path) as f:
                data = json.load(f)

            # Load entries
            for entry_id, e_data in data.get("entries", {}).items():
                evidence = [
                    Evidence(
                        id=ev["id"],
                        entry_id=ev["entry_id"],
                        evidence_type=EvidenceType(ev["evidence_type"]),
                        content=ev["content"],
                        source=ev["source"],
                        confidence=ev["confidence"],
                        timestamp=datetime.fromisoformat(ev["timestamp"]),
                        metadata=ev.get("metadata", {}),
                    )
                    for ev in e_data.get("evidence", [])
                ]

                contradictions = [
                    Contradiction(
                        id=c["id"],
                        entry_id=c["entry_id"],
                        contradicting_entry_id=c.get("contradicting_entry_id"),
                        description=c["description"],
                        severity=c["severity"],
                        timestamp=datetime.fromisoformat(c["timestamp"]),
                        resolved=c.get("resolved", False),
                        resolution=c.get("resolution"),
                    )
                    for c in e_data.get("contradictions", [])
                ]

                entry = GardenEntry(
                    id=e_data["id"],
                    content=e_data["content"],
                    lifecycle=Lifecycle(e_data["lifecycle"]),
                    trust=e_data["trust"],
                    hypothesis=e_data.get("hypothesis", ""),
                    planted_at=datetime.fromisoformat(e_data["planted_at"]),
                    last_nurtured=datetime.fromisoformat(e_data["last_nurtured"]),
                    last_pruned=datetime.fromisoformat(e_data["last_pruned"])
                    if e_data.get("last_pruned")
                    else None,
                    composted_at=datetime.fromisoformat(e_data["composted_at"])
                    if e_data.get("composted_at")
                    else None,
                    evidence=evidence,
                    contradictions=contradictions,
                    connections=e_data.get("connections", []),
                    metadata=e_data.get("metadata", {}),
                    tags=e_data.get("tags", []),
                )
                self._entries[entry_id] = entry

            # Load insights
            for insight_id, i_data in data.get("insights", {}).items():
                insight = Insight(
                    id=i_data["id"],
                    source_entry_id=i_data["source_entry_id"],
                    content=i_data["content"],
                    confidence=i_data["confidence"],
                    harvest_timestamp=datetime.fromisoformat(
                        i_data["harvest_timestamp"]
                    ),
                    applications=i_data.get("applications", []),
                )
                self._insights[insight_id] = insight

            # Load nutrients
            for n_data in data.get("nutrients", []):
                nutrients = Nutrients(
                    source_entry_id=n_data["source_entry_id"],
                    concepts=n_data["concepts"],
                    lessons=n_data["lessons"],
                    timestamp=datetime.fromisoformat(n_data["timestamp"]),
                )
                self._nutrients.append(nutrients)

            # Load counters
            counters = data.get("counters", {})
            self._evidence_counter = counters.get("evidence", 0)
            self._contradiction_counter = counters.get("contradiction", 0)
            self._insight_counter = counters.get("insight", 0)

        except Exception as e:
            raise NoosphereError(f"Failed to load garden: {e}")
