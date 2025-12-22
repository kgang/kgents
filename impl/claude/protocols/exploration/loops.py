"""
Loop Detection: Prevent trivially bad navigation loops.

Three types of loops are detected:
1. EXACT: Same node visited twice (hash match)
2. SEMANTIC: Similar nodes visited (embedding similarity > threshold)
3. STRUCTURAL: Repeating navigation pattern (A->B->A->B)

Loop response escalates:
- First occurrence: Warn, continue
- Second occurrence: Auto-backtrack
- Third occurrence: Halt exploration

Teaching:
    gotcha: Semantic loop detection requires embeddings. If no embedding
            function is provided, semantic detection is skipped.

    gotcha: Structural patterns are detected with a sliding window.
            Very long patterns (>10 edges) may not be detected.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Protocol

from .types import ContextNode, LoopStatus

if TYPE_CHECKING:
    import numpy as np


# =============================================================================
# Embedding Protocol
# =============================================================================


class EmbeddingFunction(Protocol):
    """Protocol for embedding functions."""

    def __call__(self, text: str) -> list[float]:
        """Embed text to vector."""
        ...


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0

    dot: float = sum(x * y for x, y in zip(a, b))
    norm_a: float = sum(x * x for x in a) ** 0.5
    norm_b: float = sum(x * x for x in b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot / (norm_a * norm_b))


# =============================================================================
# Loop Response
# =============================================================================


class LoopResponse(Enum):
    """How to respond to a detected loop."""

    CONTINUE = auto()  # Warn but continue
    BACKTRACK = auto()  # Auto-backtrack to last non-looping node
    HALT = auto()  # Stop exploration


@dataclass
class LoopEvent:
    """Record of a loop occurrence."""

    loop_type: LoopStatus
    node_path: str
    edge: str
    occurrence: int  # 1st, 2nd, 3rd occurrence


# =============================================================================
# Loop Detector
# =============================================================================


@dataclass
class LoopDetector:
    """
    Detect trivially bad loops in navigation.

    Tracks three loop types and escalates response on repeated occurrences.

    Configuration:
        history_size: How many nodes to remember for exact/semantic checks
        pattern_size: How many edges to check for structural patterns
        semantic_threshold: Cosine similarity threshold for semantic loops
        embed_fn: Optional function to embed node content for semantic checks
    """

    history_size: int = 100
    pattern_size: int = 20
    semantic_threshold: float = 0.95
    embed_fn: EmbeddingFunction | None = None

    # State (mutable for tracking)
    _path_history: deque[str] = field(default_factory=lambda: deque(maxlen=100))
    _embeddings: deque[list[float]] = field(default_factory=lambda: deque(maxlen=100))
    _edge_pattern: deque[str] = field(default_factory=lambda: deque(maxlen=20))
    _loop_counts: dict[str, int] = field(default_factory=dict)  # node_path -> count

    def __post_init__(self) -> None:
        """Initialize deques with correct maxlen."""
        self._path_history = deque(maxlen=self.history_size)
        self._embeddings = deque(maxlen=self.history_size)
        self._edge_pattern = deque(maxlen=self.pattern_size)

    def check(self, node: ContextNode, edge: str) -> LoopStatus:
        """
        Check for loops when visiting a node via an edge.

        Returns LoopStatus indicating what kind of loop (if any) was detected.
        """
        # 1. Exact loop: same path visited before
        if node.path in self._path_history:
            return LoopStatus.EXACT_LOOP

        # 2. Semantic loop: similar content
        if self.embed_fn is not None:
            try:
                # Get content synchronously for now (may need async version)
                content = node._content or node.path
                embedding = self.embed_fn(content)

                for prev_embedding in self._embeddings:
                    similarity = cosine_similarity(embedding, prev_embedding)
                    if similarity > self.semantic_threshold:
                        return LoopStatus.SEMANTIC_LOOP

                self._embeddings.append(embedding)
            except Exception:
                # If embedding fails, skip semantic check
                pass

        # 3. Structural loop: repeating edge pattern
        self._edge_pattern.append(edge)
        if self._is_repeating_pattern():
            return LoopStatus.STRUCTURAL_LOOP

        # Record for future checks
        self._path_history.append(node.path)

        return LoopStatus.OK

    def record_visit(self, node: ContextNode, edge: str) -> None:
        """Record a visit without checking (for initialization)."""
        self._path_history.append(node.path)
        self._edge_pattern.append(edge)

    def get_response(self, node: ContextNode, loop_status: LoopStatus) -> LoopResponse:
        """
        Determine response based on loop type and occurrence count.

        Response escalation:
        - 1st occurrence: CONTINUE (warn)
        - 2nd occurrence: BACKTRACK
        - 3rd+ occurrence: HALT
        """
        if loop_status == LoopStatus.OK:
            return LoopResponse.CONTINUE

        # Track occurrences
        key = f"{node.path}:{loop_status.name}"
        self._loop_counts[key] = self._loop_counts.get(key, 0) + 1
        occurrence = self._loop_counts[key]

        if occurrence == 1:
            return LoopResponse.CONTINUE
        elif occurrence == 2:
            return LoopResponse.BACKTRACK
        else:
            return LoopResponse.HALT

    def get_loop_event(
        self, node: ContextNode, edge: str, loop_status: LoopStatus
    ) -> LoopEvent | None:
        """Get a LoopEvent if a loop was detected."""
        if loop_status == LoopStatus.OK:
            return None

        key = f"{node.path}:{loop_status.name}"
        occurrence = self._loop_counts.get(key, 0)

        return LoopEvent(
            loop_type=loop_status,
            node_path=node.path,
            edge=edge,
            occurrence=occurrence,
        )

    def reset(self) -> None:
        """Clear all history (for new exploration)."""
        self._path_history.clear()
        self._embeddings.clear()
        self._edge_pattern.clear()
        self._loop_counts.clear()

    def check_portal(self, portal_key: str) -> LoopStatus:
        """
        Check for repeated portal expansions.

        Portal keys track expansion history separately from navigation.
        This prevents expanding the same portal multiple times in a session.

        Args:
            portal_key: Unique key for the portal (e.g., "tests/covers" or file path)

        Returns:
            LoopStatus.EXACT_LOOP if portal was already expanded
            LoopStatus.OK otherwise
        """
        # Use a simple prefix to namespace portal checks
        prefixed_key = f"portal:{portal_key}"

        if prefixed_key in self._path_history:
            return LoopStatus.EXACT_LOOP

        # Record this portal expansion
        self._path_history.append(prefixed_key)
        return LoopStatus.OK

    def get_portal_response(self, portal_key: str, loop_status: LoopStatus) -> LoopResponse:
        """
        Determine response for a portal loop.

        Portal loops use the same escalation as navigation loops:
        - 1st occurrence: CONTINUE (warn)
        - 2nd occurrence: BACKTRACK (skip expansion)
        - 3rd+ occurrence: HALT

        Args:
            portal_key: The portal key that triggered the loop
            loop_status: The detected loop status

        Returns:
            LoopResponse indicating how to handle the loop
        """
        if loop_status == LoopStatus.OK:
            return LoopResponse.CONTINUE

        # Track occurrences with portal prefix
        key = f"portal:{portal_key}:{loop_status.name}"
        self._loop_counts[key] = self._loop_counts.get(key, 0) + 1
        occurrence = self._loop_counts[key]

        if occurrence == 1:
            return LoopResponse.CONTINUE
        elif occurrence == 2:
            return LoopResponse.BACKTRACK
        else:
            return LoopResponse.HALT

    def _is_repeating_pattern(self) -> bool:
        """
        Detect A->B->A->B patterns in edge history.

        Checks for repeating periods from 1 to len/2.
        """
        if len(self._edge_pattern) < 4:
            return False

        pattern = "".join(self._edge_pattern)

        # Check for repeating patterns of increasing period
        for period in range(1, len(pattern) // 2 + 1):
            base = pattern[:period]
            # Check if the pattern is just this base repeated
            reconstructed = (base * (len(pattern) // period + 1))[: len(pattern)]
            if pattern == reconstructed:
                # Found a repeating pattern of at least 2 repetitions
                if len(pattern) >= period * 2:
                    return True

        return False


# =============================================================================
# Factory Functions
# =============================================================================


def create_loop_detector(
    history_size: int = 100,
    semantic_threshold: float = 0.95,
    embed_fn: EmbeddingFunction | None = None,
) -> LoopDetector:
    """Create a configured LoopDetector."""
    return LoopDetector(
        history_size=history_size,
        semantic_threshold=semantic_threshold,
        embed_fn=embed_fn,
    )


def strict_loop_detector() -> LoopDetector:
    """Strict detector: lower semantic threshold."""
    return LoopDetector(
        history_size=200,
        semantic_threshold=0.9,  # Stricter
    )


def relaxed_loop_detector() -> LoopDetector:
    """Relaxed detector: higher semantic threshold, smaller history."""
    return LoopDetector(
        history_size=50,
        semantic_threshold=0.98,  # More permissive
    )


__all__ = [
    "LoopDetector",
    "LoopResponse",
    "LoopEvent",
    "EmbeddingFunction",
    "cosine_similarity",
    # Factories
    "create_loop_detector",
    "strict_loop_detector",
    "relaxed_loop_detector",
]
