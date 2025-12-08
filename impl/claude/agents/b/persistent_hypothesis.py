"""
Persistent Hypothesis Storage for B-gents.

Provides durable storage for hypothesis history, enabling:
- Cross-session hypothesis continuity
- Hypothesis evolution tracking
- Duplicate hypothesis detection
- Research lineage preservation
"""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from agents.d import PersistentAgent
from .hypothesis_parser import Hypothesis, ParsedHypothesisResponse


@dataclass
class HypothesisMemory:
    """
    Structured memory for hypothesis storage.

    Stores hypotheses with metadata for retrieval and analysis.
    """

    hypotheses: list[Hypothesis] = field(default_factory=list)
    domains: dict[str, list[int]] = field(
        default_factory=dict
    )  # domain -> hypothesis indices
    total_generated: int = 0  # Total count across all sessions

    def add_response(self, response: ParsedHypothesisResponse, domain: str) -> None:
        """
        Add a hypothesis response to memory.

        Args:
            response: Parsed hypothesis response from engine
            domain: Scientific domain
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
