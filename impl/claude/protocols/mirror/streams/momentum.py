"""SemanticMomentumTracker: Track semantic drift using embeddings."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

try:
    import numpy as np
except ImportError:
    np = None  # type: ignore

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None  # type: ignore

from .base import EventStream, Window


@dataclass(frozen=True)
class SemanticMomentum:
    """The motion of meaning through time.

    From Noether's theorem: p⃗ = m · v⃗
    Where:
      p⃗ = momentum vector
      m = mass (attention/influence weight)
      v⃗ = velocity (rate of semantic change)
    """

    topic: str
    mass: float  # Attention density (references/mentions)
    velocity: Any  # Embedding drift vector (np.ndarray if numpy available)
    timestamp: datetime

    @property
    def momentum(self) -> Any:
        """p⃗ = m · v⃗"""
        if np is None:
            return self.mass * 0.0  # Fallback without numpy
        return self.mass * self.velocity

    @property
    def magnitude(self) -> float:
        """||p⃗||"""
        if np is None:
            return 0.0
        return float(np.linalg.norm(self.momentum))

    def is_conserved(self, threshold: float = 0.1) -> bool:
        """Momentum conserved (stable meaning)? velocity < threshold"""
        if np is None:
            return True
        return float(np.linalg.norm(self.velocity)) < threshold


class SemanticMomentumTracker:
    """Track semantic momentum using embeddings to measure topic drift."""

    def __init__(
        self, model_name: str = "all-MiniLM-L6-v2", window_size: timedelta | None = None
    ):
        if SentenceTransformer is None:
            raise ImportError(
                "sentence-transformers is required for SemanticMomentumTracker. "
                "Install with: pip install sentence-transformers"
            )
        if np is None:
            raise ImportError(
                "numpy is required for SemanticMomentumTracker. "
                "Install with: pip install numpy"
            )

        self.model = SentenceTransformer(model_name)
        self.window_size = window_size or timedelta(days=30)

    def track_topic(self, stream: EventStream, topic: str) -> list[SemanticMomentum]:
        """Track topic's semantic momentum across time (one per window)."""
        windowed = stream.window(self.window_size)
        momentum_history = []
        previous_embedding = None

        for window in windowed.windows():
            mentions = self._extract_topic_mentions(window, topic)
            if not mentions:
                continue

            mass = len(mentions)
            embeddings = self.model.encode(mentions)
            avg_embedding = np.mean(embeddings, axis=0)

            velocity = (
                avg_embedding - previous_embedding
                if previous_embedding is not None
                else np.zeros_like(avg_embedding)
            )

            momentum_history.append(
                SemanticMomentum(
                    topic=topic,
                    mass=mass,
                    velocity=velocity,
                    timestamp=window.end,
                )
            )

            previous_embedding = avg_embedding

        return momentum_history

    def detect_entropy_leaks(
        self, momentum_history: list[SemanticMomentum], threshold: float = 0.15
    ) -> list[str]:
        """Detect entropy leaks: momentum not conserved, high velocity, no explanation."""
        leaks = []
        for momentum in momentum_history:
            if not momentum.is_conserved(threshold):
                leaks.append(
                    f"Entropy leak at {momentum.timestamp}: "
                    f"Topic '{momentum.topic}' drifted with velocity {momentum.magnitude:.3f}"
                )
        return leaks

    def _extract_topic_mentions(self, window: Window, topic: str) -> list[str]:
        """Extract sentences/paragraphs mentioning the topic."""
        mentions = []
        for event in window.events:
            # Extract text from event data
            if "message" in event.data:
                text = event.data["message"]
                if topic.lower() in text.lower():
                    mentions.append(text)
        return mentions
