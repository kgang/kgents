"""
Persistent Hypothesis Storage for B-gents.

Provides durable storage for hypothesis history, enabling:
- Cross-session hypothesis continuity
- Hypothesis evolution tracking
- Duplicate hypothesis detection
- Research lineage preservation
- L-gent catalog integration
- D-gent lineage support
"""

from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from agents.d import PersistentAgent
from .hypothesis_parser import Hypothesis, ParsedHypothesisResponse


@dataclass
class HypothesisLineageEdge:
    """
    Represents a lineage relationship between hypotheses.

    Used to track hypothesis evolution, refinement, and falsification.
    """

    source_idx: int  # Index of source hypothesis in memory
    target_idx: int  # Index of target hypothesis in memory
    relationship: str  # "evolved_from", "refined_from", "falsified_by", "forked_from"
    created_at: str  # ISO timestamp
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class HypothesisMemory:
    """
    Structured memory for hypothesis storage.

    Stores hypotheses with metadata for retrieval and analysis.
    Enhanced with lineage tracking for D-gent integration.
    """

    hypotheses: list[Hypothesis] = field(default_factory=list)
    domains: dict[str, list[int]] = field(
        default_factory=dict
    )  # domain -> hypothesis indices
    total_generated: int = 0  # Total count across all sessions

    # Lineage tracking (D-gent integration)
    lineage_edges: list[HypothesisLineageEdge] = field(default_factory=list)

    # L-gent catalog IDs (for catalog integration)
    # NOTE: JSON serializes int keys as strings, so we use _fix_catalog_ids after load
    catalog_ids: dict[int, str] = field(default_factory=dict)  # hyp_idx -> catalog_id

    def __post_init__(self):
        """Fix catalog_ids keys that were converted to strings by JSON serialization."""
        # JSON doesn't support int keys, so they get serialized as strings
        # Convert them back to ints when loading
        if self.catalog_ids:
            self.catalog_ids = {
                int(k) if isinstance(k, str) else k: v
                for k, v in self.catalog_ids.items()
            }

    # Research session tracking
    sessions: list[dict[str, Any]] = field(default_factory=list)

    def add_response(
        self,
        response: ParsedHypothesisResponse,
        domain: str,
        session_id: str | None = None,
    ) -> list[int]:
        """
        Add a hypothesis response to memory.

        Args:
            response: Parsed hypothesis response from engine
            domain: Scientific domain
            session_id: Optional session identifier

        Returns:
            List of indices for newly added hypotheses
        """
        start_idx = len(self.hypotheses)

        # Add hypotheses
        self.hypotheses.extend(response.hypotheses)
        self.total_generated += len(response.hypotheses)

        # Index by domain
        if domain not in self.domains:
            self.domains[domain] = []

        new_indices = list(range(start_idx, len(self.hypotheses)))
        self.domains[domain].extend(new_indices)

        # Track session
        if session_id:
            self.sessions.append(
                {
                    "session_id": session_id,
                    "domain": domain,
                    "hypothesis_indices": new_indices,
                    "created_at": datetime.now().isoformat(),
                    "count": len(new_indices),
                }
            )

        return new_indices

    def add_lineage(
        self,
        source_idx: int,
        target_idx: int,
        relationship: str,
        context: dict[str, Any] | None = None,
    ) -> HypothesisLineageEdge:
        """
        Record a lineage relationship between hypotheses.

        Args:
            source_idx: Index of source hypothesis (newer)
            target_idx: Index of target hypothesis (older/parent)
            relationship: Type of relationship
            context: Additional context for the relationship

        Returns:
            Created lineage edge
        """
        edge = HypothesisLineageEdge(
            source_idx=source_idx,
            target_idx=target_idx,
            relationship=relationship,
            created_at=datetime.now().isoformat(),
            context=context or {},
        )
        self.lineage_edges.append(edge)
        return edge

    def get_by_domain(self, domain: str) -> list[Hypothesis]:
        """Get all hypotheses for a specific domain."""
        if domain not in self.domains:
            return []
        return [self.hypotheses[i] for i in self.domains[domain]]

    def get_recent(self, limit: int = 10) -> list[Hypothesis]:
        """Get most recent hypotheses."""
        return self.hypotheses[-limit:]

    def find_similar(self, statement: str, threshold: float = 0.8) -> list[Hypothesis]:
        """
        Find similar hypotheses using simple word overlap.

        Args:
            statement: Hypothesis statement to match against
            threshold: Similarity threshold (0.0-1.0)

        Returns:
            List of similar hypotheses
        """
        # Simple word-based similarity (can be enhanced with embeddings)
        statement_words = set(statement.lower().split())

        similar = []
        for hyp in self.hypotheses:
            hyp_words = set(hyp.statement.lower().split())
            overlap = len(statement_words & hyp_words)
            total = len(statement_words | hyp_words)

            if total > 0 and (overlap / total) >= threshold:
                similar.append(hyp)

        return similar

    def get_ancestors(self, hyp_idx: int, max_depth: int | None = None) -> list[int]:
        """
        Get ancestor hypotheses (what this evolved from).

        Args:
            hyp_idx: Index of hypothesis to find ancestors for
            max_depth: Maximum depth to traverse

        Returns:
            List of ancestor hypothesis indices
        """
        visited = set()
        queue = [(hyp_idx, 0)]

        while queue:
            current_idx, depth = queue.pop(0)

            if current_idx in visited:
                continue

            if current_idx != hyp_idx:
                visited.add(current_idx)

            if max_depth is not None and depth >= max_depth:
                continue

            # Find edges pointing from current to parents
            for edge in self.lineage_edges:
                if edge.source_idx == current_idx:
                    if edge.target_idx not in visited:
                        queue.append((edge.target_idx, depth + 1))

        return list(visited)

    def get_descendants(self, hyp_idx: int, max_depth: int | None = None) -> list[int]:
        """
        Get descendant hypotheses (what evolved from this).

        Args:
            hyp_idx: Index of hypothesis to find descendants for
            max_depth: Maximum depth to traverse

        Returns:
            List of descendant hypothesis indices
        """
        visited = set()
        queue = [(hyp_idx, 0)]

        while queue:
            current_idx, depth = queue.pop(0)

            if current_idx in visited:
                continue

            if current_idx != hyp_idx:
                visited.add(current_idx)

            if max_depth is not None and depth >= max_depth:
                continue

            # Find edges where current is the target (parent)
            for edge in self.lineage_edges:
                if edge.target_idx == current_idx:
                    if edge.source_idx not in visited:
                        queue.append((edge.source_idx, depth + 1))

        return list(visited)

    def set_catalog_id(self, hyp_idx: int, catalog_id: str) -> None:
        """Link a hypothesis to its L-gent catalog ID."""
        self.catalog_ids[hyp_idx] = catalog_id

    def get_catalog_id(self, hyp_idx: int) -> str | None:
        """Get L-gent catalog ID for a hypothesis."""
        return self.catalog_ids.get(hyp_idx)


class PersistentHypothesisStorage:
    """
    Persistent storage for hypothesis memory.

    Wraps HypothesisMemory with PersistentAgent to enable
    durable hypothesis tracking across sessions.

    Example:
        >>> storage = PersistentHypothesisStorage(
        ...     path=Path("~/.kgents/hypotheses.json")
        ... )
        >>> await storage.load()
        >>>
        >>> # Generate new hypotheses
        >>> response = await hypothesis_engine.invoke(...)
        >>> await storage.add_response(response, domain="biology")
        >>>
        >>> # Query history
        >>> bio_hyps = await storage.get_by_domain("biology")
        >>> recent = await storage.get_recent(limit=5)
    """

    def __init__(
        self,
        path: Path | str,
        auto_save: bool = True,
    ):
        """
        Initialize persistent hypothesis storage.

        Args:
            path: Path to JSON file for hypothesis memory
            auto_save: Whether to save after each operation
        """
        self._dgent = PersistentAgent[HypothesisMemory](
            path=Path(path),
            schema=HypothesisMemory,
            max_history=100,  # Track hypothesis evolution
        )
        self.auto_save = auto_save
        self._memory: Optional[HypothesisMemory] = None

    async def load(self) -> HypothesisMemory:
        """
        Load hypothesis memory from disk.

        Returns:
            Loaded or initialized memory
        """
        try:
            self._memory = await self._dgent.load()
        except Exception:
            # No state exists yet, initialize
            self._memory = HypothesisMemory()
            if self.auto_save:
                await self._dgent.save(self._memory)

        return self._memory

    async def save(self) -> None:
        """Persist current hypothesis memory to disk."""
        if self._memory is not None:
            await self._dgent.save(self._memory)

    async def add_response(
        self,
        response: ParsedHypothesisResponse,
        domain: str,
    ) -> None:
        """
        Add a hypothesis response to storage.

        Args:
            response: Parsed hypothesis response
            domain: Scientific domain
        """
        if self._memory is None:
            await self.load()

        assert self._memory is not None
        self._memory.add_response(response, domain)

        if self.auto_save:
            await self.save()

    async def get_by_domain(self, domain: str) -> list[Hypothesis]:
        """Get all hypotheses for a domain."""
        if self._memory is None:
            await self.load()

        assert self._memory is not None
        return self._memory.get_by_domain(domain)

    async def get_recent(self, limit: int = 10) -> list[Hypothesis]:
        """Get most recent hypotheses."""
        if self._memory is None:
            await self.load()

        assert self._memory is not None
        return self._memory.get_recent(limit)

    async def find_similar(
        self,
        statement: str,
        threshold: float = 0.8,
    ) -> list[Hypothesis]:
        """Find similar hypotheses."""
        if self._memory is None:
            await self.load()

        assert self._memory is not None
        return self._memory.find_similar(statement, threshold)

    async def get_evolution_history(
        self,
        limit: int = 10,
    ) -> list[HypothesisMemory]:
        """
        Get history of hypothesis memory states.

        Args:
            limit: Maximum number of historical states

        Returns:
            List of past memory states (newest first)
        """
        return await self._dgent.history(limit=limit)

    @property
    def total_generated(self) -> int:
        """Total hypotheses generated across all sessions."""
        if self._memory is None:
            return 0
        return self._memory.total_generated

    # ─────────────────────────────────────────────────────────────────
    # Lineage Methods (D-gent integration)
    # ─────────────────────────────────────────────────────────────────

    async def add_lineage(
        self,
        source_idx: int,
        target_idx: int,
        relationship: str,
        context: dict | None = None,
    ) -> HypothesisLineageEdge:
        """
        Record a lineage relationship between hypotheses.

        Args:
            source_idx: Index of source hypothesis (newer)
            target_idx: Index of target hypothesis (older/parent)
            relationship: Type of relationship
            context: Additional context

        Returns:
            Created lineage edge
        """
        if self._memory is None:
            await self.load()

        assert self._memory is not None
        edge = self._memory.add_lineage(source_idx, target_idx, relationship, context)

        if self.auto_save:
            await self.save()

        return edge

    async def get_ancestors(
        self,
        hyp_idx: int,
        max_depth: int | None = None,
    ) -> list[int]:
        """Get ancestor hypothesis indices."""
        if self._memory is None:
            await self.load()

        assert self._memory is not None
        return self._memory.get_ancestors(hyp_idx, max_depth)

    async def get_descendants(
        self,
        hyp_idx: int,
        max_depth: int | None = None,
    ) -> list[int]:
        """Get descendant hypothesis indices."""
        if self._memory is None:
            await self.load()

        assert self._memory is not None
        return self._memory.get_descendants(hyp_idx, max_depth)

    async def set_catalog_id(self, hyp_idx: int, catalog_id: str) -> None:
        """Link a hypothesis to its L-gent catalog ID."""
        if self._memory is None:
            await self.load()

        assert self._memory is not None
        self._memory.set_catalog_id(hyp_idx, catalog_id)

        if self.auto_save:
            await self.save()

    async def get_catalog_id(self, hyp_idx: int) -> str | None:
        """Get L-gent catalog ID for a hypothesis."""
        if self._memory is None:
            await self.load()

        assert self._memory is not None
        return self._memory.get_catalog_id(hyp_idx)

    async def get_hypothesis_by_idx(self, hyp_idx: int) -> Hypothesis | None:
        """Get hypothesis by index."""
        if self._memory is None:
            await self.load()

        assert self._memory is not None
        if 0 <= hyp_idx < len(self._memory.hypotheses):
            return self._memory.hypotheses[hyp_idx]
        return None

    async def add_response_with_session(
        self,
        response: ParsedHypothesisResponse,
        domain: str,
        session_id: str,
    ) -> list[int]:
        """
        Add a hypothesis response with session tracking.

        Args:
            response: Parsed hypothesis response
            domain: Scientific domain
            session_id: Session identifier

        Returns:
            List of indices for newly added hypotheses
        """
        if self._memory is None:
            await self.load()

        assert self._memory is not None
        indices = self._memory.add_response(response, domain, session_id)

        if self.auto_save:
            await self.save()

        return indices


# Convenience function


def persistent_hypothesis_storage(
    path: Path | str = "~/.kgents/hypotheses.json",
) -> PersistentHypothesisStorage:
    """
    Create persistent hypothesis storage.

    Args:
        path: Path to hypothesis memory file

    Returns:
        Configured PersistentHypothesisStorage
    """
    return PersistentHypothesisStorage(path=path)
