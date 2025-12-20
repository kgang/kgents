"""
Hypothesis tree structures for Research Flow.

The hypothesis tree captures the exploration space during tree-of-thought
research. Each hypothesis represents a potential answer or sub-answer
to the research question.

See: spec/f-gents/research.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from agents.f.state import HypothesisStatus


@dataclass
class Evidence:
    """Evidence for or against a hypothesis."""

    content: str
    """What the evidence says."""

    supports: bool
    """True if supports hypothesis, False if contradicts."""

    strength: float
    """Evidence strength from 0.0 (weak) to 1.0 (strong)."""

    source: str
    """Where this evidence came from (e.g., 'exploration', 'LLM', 'tool')."""

    timestamp: datetime = field(default_factory=datetime.now)
    """When this evidence was discovered."""


@dataclass
class Hypothesis:
    """A node in the exploration tree."""

    id: str
    """Unique hypothesis ID."""

    content: str
    """The hypothesis text."""

    parent_id: str | None
    """Parent hypothesis ID. None for root."""

    depth: int
    """Distance from root (root has depth 0)."""

    confidence: float
    """Current confidence in this hypothesis (0.0 to 1.0)."""

    promise: float
    """Expected value of exploring this hypothesis further."""

    status: HypothesisStatus
    """Current status (exploring, expanded, pruned, merged, confirmed)."""

    evidence: list[Evidence] = field(default_factory=list)
    """Evidence supporting or contradicting this hypothesis."""

    children: list[str] = field(default_factory=list)
    """IDs of child hypotheses."""

    created_at: datetime = field(default_factory=datetime.now)
    """When this hypothesis was created."""

    explored_at: datetime | None = None
    """When exploration of this hypothesis completed."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata."""

    def add_evidence(self, evidence: Evidence) -> None:
        """Add evidence and update confidence."""
        self.evidence.append(evidence)
        # Update confidence based on new evidence
        self._update_confidence()

    def _update_confidence(self) -> None:
        """Update confidence based on accumulated evidence."""
        if not self.evidence:
            return

        # Simple evidence aggregation:
        # - Supporting evidence increases confidence
        # - Contradicting evidence decreases confidence
        # - Weight by strength
        total_support = sum(e.strength for e in self.evidence if e.supports)
        total_contradict = sum(e.strength for e in self.evidence if not e.supports)

        # Bayes-like update
        if total_support + total_contradict > 0:
            self.confidence = total_support / (total_support + total_contradict)


@dataclass
class Insight:
    """A finding during exploration."""

    type: Literal["discovery", "evidence", "contradiction", "synthesis"]
    """Type of insight."""

    content: str
    """The insight content."""

    confidence: float
    """Confidence in this insight (0.0 to 1.0)."""

    hypothesis_id: str
    """Which hypothesis yielded this insight."""

    depth: int
    """At what depth this was discovered."""

    timestamp: datetime = field(default_factory=datetime.now)
    """When this insight was discovered."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata."""


@dataclass
class Synthesis:
    """Result of merging multiple hypotheses."""

    content: str
    """The synthesized understanding."""

    confidence: float
    """Confidence in the synthesis (0.0 to 1.0)."""

    sources: list[str]
    """IDs of hypotheses that were merged."""

    method: Literal["best_first", "weighted_vote", "synthesis"]
    """Merge strategy used."""

    timestamp: datetime = field(default_factory=datetime.now)
    """When synthesis was created."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata."""


class HypothesisTree:
    """
    Tree structure for managing hypotheses.

    The tree maintains parent-child relationships and provides
    efficient operations for branching, pruning, and traversal.
    """

    def __init__(self, root_content: str) -> None:
        """
        Initialize with a root hypothesis.

        Args:
            root_content: The initial question or hypothesis
        """
        self.root = Hypothesis(
            id=self._generate_id(),
            content=root_content,
            parent_id=None,
            depth=0,
            confidence=0.5,  # Neutral initial confidence
            promise=1.0,  # Root always has max promise
            status=HypothesisStatus.EXPLORING,
        )
        self._nodes: dict[str, Hypothesis] = {self.root.id: self.root}

    def _generate_id(self) -> str:
        """Generate unique hypothesis ID."""
        return f"hyp_{uuid.uuid4().hex[:8]}"

    def add_node(
        self,
        content: str,
        parent_id: str,
        confidence: float = 0.5,
        promise: float = 0.5,
    ) -> Hypothesis:
        """
        Add a new hypothesis to the tree.

        Args:
            content: Hypothesis text
            parent_id: Parent hypothesis ID
            confidence: Initial confidence
            promise: Expected exploration value

        Returns:
            The newly created hypothesis

        Raises:
            ValueError: If parent_id doesn't exist
        """
        if parent_id not in self._nodes:
            msg = f"Parent hypothesis {parent_id} not found"
            raise ValueError(msg)

        parent = self._nodes[parent_id]
        hypothesis = Hypothesis(
            id=self._generate_id(),
            content=content,
            parent_id=parent_id,
            depth=parent.depth + 1,
            confidence=confidence,
            promise=promise,
            status=HypothesisStatus.EXPLORING,
        )

        self._nodes[hypothesis.id] = hypothesis
        parent.children.append(hypothesis.id)

        return hypothesis

    def get_node(self, hypothesis_id: str) -> Hypothesis | None:
        """Get hypothesis by ID."""
        return self._nodes.get(hypothesis_id)

    def get_children(self, hypothesis_id: str) -> list[Hypothesis]:
        """Get all children of a hypothesis."""
        hypothesis = self.get_node(hypothesis_id)
        if hypothesis is None:
            return []
        return [self._nodes[child_id] for child_id in hypothesis.children]

    def get_path(self, hypothesis_id: str) -> list[Hypothesis]:
        """
        Get path from root to hypothesis.

        Returns list from root to target hypothesis.
        """
        path = []
        current = self.get_node(hypothesis_id)

        while current is not None:
            path.append(current)
            if current.parent_id is None:
                break
            current = self.get_node(current.parent_id)

        return list(reversed(path))

    def get_leaves(self) -> list[Hypothesis]:
        """Get all leaf hypotheses (no children)."""
        return [h for h in self._nodes.values() if not h.children]

    def get_active(self) -> list[Hypothesis]:
        """Get all hypotheses currently being explored."""
        return [h for h in self._nodes.values() if h.status == HypothesisStatus.EXPLORING]

    def prune(self, hypothesis_id: str, recursive: bool = False) -> None:
        """
        Mark hypothesis as pruned.

        Args:
            hypothesis_id: ID of hypothesis to prune
            recursive: If True, also prune all descendants
        """
        hypothesis = self.get_node(hypothesis_id)
        if hypothesis is None:
            return

        hypothesis.status = HypothesisStatus.PRUNED

        if recursive:
            for child_id in hypothesis.children:
                self.prune(child_id, recursive=True)

    def get_statistics(self) -> dict[str, Any]:
        """Get tree statistics."""
        nodes_by_status = {}
        for status in HypothesisStatus:
            nodes_by_status[status.value] = len(
                [h for h in self._nodes.values() if h.status == status]
            )

        max_depth = max((h.depth for h in self._nodes.values()), default=0)

        leaves = self.get_leaves()
        avg_confidence = sum(h.confidence for h in leaves) / len(leaves) if leaves else 0.0

        return {
            "total_nodes": len(self._nodes),
            "max_depth": max_depth,
            "nodes_by_status": nodes_by_status,
            "avg_leaf_confidence": avg_confidence,
            "num_leaves": len(leaves),
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert tree to dictionary for serialization."""
        return {
            "root_id": self.root.id,
            "nodes": {
                node_id: {
                    "id": h.id,
                    "content": h.content,
                    "parent_id": h.parent_id,
                    "depth": h.depth,
                    "confidence": h.confidence,
                    "promise": h.promise,
                    "status": h.status.value,
                    "evidence": [
                        {
                            "content": e.content,
                            "supports": e.supports,
                            "strength": e.strength,
                            "source": e.source,
                        }
                        for e in h.evidence
                    ],
                    "children": h.children,
                }
                for node_id, h in self._nodes.items()
            },
        }


__all__ = [
    "Evidence",
    "Hypothesis",
    "Insight",
    "Synthesis",
    "HypothesisTree",
]
