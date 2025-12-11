"""
VectorAgent: Semantic search over state using vector embeddings.

Provides foundation for the Semantic Manifold concept from noosphere.md.
Uses numpy for vector operations with optional FAISS for fast search.

Note: Requires numpy. Install with: pip install numpy
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Generic, List, Optional, Tuple, TypeVar

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    np = None  # type: ignore
    NUMPY_AVAILABLE = False

from .errors import (
    SemanticError,
    StorageError,
    VoidNotFoundError,
)

S = TypeVar("S")  # State type


class DistanceMetric(Enum):
    """Distance metrics for semantic similarity."""

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"


# Guard numpy-dependent code
if NUMPY_AVAILABLE:

    @dataclass
    class Point:
        """A point in semantic space."""

        coordinates: np.ndarray
        metadata: dict = field(default_factory=dict)

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Point):
                return False
            return np.allclose(self.coordinates, other.coordinates)

    @dataclass
    class Void:
        """An unexplored region (Ma)."""

        center: Point
        radius: float
        potential: float  # Estimated generative value (0.0 to 1.0)

    @dataclass
    class VectorEntry(Generic[S]):
        """An entry in the vector store."""

        id: str
        state: S
        embedding: np.ndarray
        metadata: dict = field(default_factory=dict)

    class VectorAgent(Generic[S]):
        """
        Vector-based D-gent for semantic state storage and retrieval.

        Features:
        - Store states with vector embeddings
        - Semantic similarity search (k-NN)
        - Curvature estimation (conceptual boundary detection)
        - Void detection (unexplored regions with generative potential)

        This is the foundation for the Semantic Manifold in the Noosphere layer.

        Note: Requires numpy. Install with: pip install numpy
        """

        def __init__(
            self,
            dimension: int,
            embedder: Optional[Callable[[S], Any]] = None,
            distance: DistanceMetric = DistanceMetric.COSINE,
            persistence_path: Optional[Path] = None,
        ):
            self.dimension = dimension
            self.embedder = embedder
            self.distance = distance
            self.persistence_path = persistence_path

            self._entries: dict[str, VectorEntry[S]] = {}
            self._embeddings: Optional[np.ndarray] = None
            self._ids: list[str] = []

            if persistence_path and Path(persistence_path).exists():
                self._load_from_disk()

        async def load(self) -> dict[str, VectorEntry[S]]:
            """Load all entries."""
            return dict(self._entries)

        async def save(self, state: S) -> None:
            """Save state with automatic embedding."""
            if self.embedder is None:
                raise SemanticError(
                    "No embedder configured; use add() with explicit embedding"
                )

            entry_id = f"entry_{len(self._entries)}"
            embedding = self.embedder(state)
            await self.add(entry_id, state, embedding)

        async def history(self, limit: int | None = None) -> List[S]:
            """Return states in order of addition (newest first)."""
            states = [e.state for e in self._entries.values()]
            states.reverse()
            return states[:limit] if limit else states

        async def add(
            self,
            entry_id: str,
            state: S,
            embedding: np.ndarray,
            metadata: Optional[dict] = None,
        ) -> None:
            """Add state with explicit embedding."""
            if embedding.shape[0] != self.dimension:
                raise SemanticError(
                    f"Embedding dimension {embedding.shape[0]} != agent dimension {self.dimension}"
                )

            entry = VectorEntry(
                id=entry_id,
                state=state,
                embedding=embedding.astype(np.float32),
                metadata=metadata or {},
            )
            self._entries[entry_id] = entry
            self._rebuild_index()

            if self.persistence_path:
                self._save_to_disk()

        async def get(self, entry_id: str) -> Optional[VectorEntry[S]]:
            """Get entry by ID."""
            return self._entries.get(entry_id)

        async def delete(self, entry_id: str) -> bool:
            """Delete entry by ID."""
            if entry_id in self._entries:
                del self._entries[entry_id]
                self._rebuild_index()
                if self.persistence_path:
                    self._save_to_disk()
                return True
            return False

        async def neighbors(
            self,
            query: np.ndarray,
            k: int = 5,
            radius: Optional[float] = None,
        ) -> List[Tuple[VectorEntry[S], float]]:
            """Find k nearest neighbors to query vector."""
            if len(self._entries) == 0:
                return []

            distances = self._compute_distances(query)
            indices = np.argsort(distances)[:k]

            results = []
            for idx in indices:
                entry_id = self._ids[idx]
                dist = float(distances[idx])
                if radius is not None and dist > radius:
                    continue
                results.append((self._entries[entry_id], dist))

            return results

        async def nearest(self, query: np.ndarray, k: int = 5) -> List[Tuple[S, float]]:
            """Find k nearest states (convenience method)."""
            results = await self.neighbors(query, k=k)
            return [(entry.state, dist) for entry, dist in results]

        async def embed(self, state: S) -> Point:
            """Embed state into semantic space."""
            if self.embedder is None:
                raise SemanticError("No embedder configured")

            coords = self.embedder(state)
            return Point(coordinates=coords)

        async def curvature_at(self, point: np.ndarray, radius: float = 0.5) -> float:
            """Estimate local semantic curvature."""
            if len(self._entries) < 3:
                return 0.0

            distances = self._compute_distances(point)
            nearby_mask = distances <= radius
            nearby_distances = distances[nearby_mask]

            if len(nearby_distances) < 2:
                return 0.0

            variance = float(np.var(nearby_distances))
            mean_dist = float(np.mean(nearby_distances))

            if mean_dist > 0:
                return variance / mean_dist
            return variance

        async def geodesic(
            self,
            start: np.ndarray,
            end: np.ndarray,
            steps: int = 10,
        ) -> List[Point]:
            """Compute geodesic (shortest semantic path) between two points."""
            points = []
            for i in range(steps + 1):
                t = i / steps
                coords = start * (1 - t) + end * t
                points.append(Point(coordinates=coords))
            return points

        async def void_nearby(
            self,
            point: np.ndarray,
            search_radius: float = 1.0,
            min_void_radius: float = 0.2,
        ) -> Optional[Void]:
            """Detect unexplored regions (Ma) near a point."""
            if len(self._entries) < 2:
                return Void(
                    center=Point(coordinates=point),
                    radius=search_radius,
                    potential=1.0,
                )

            num_samples = 20
            best_void = None
            best_potential = 0.0

            for _ in range(num_samples):
                direction = np.random.randn(self.dimension)
                direction = direction / np.linalg.norm(direction)

                for dist in [0.2, 0.5, 0.8]:
                    sample_point = point + direction * search_radius * dist
                    distances = self._compute_distances(sample_point)
                    min_dist = float(np.min(distances))

                    if min_dist > min_void_radius and min_dist > best_potential:
                        best_potential = min_dist
                        best_void = Void(
                            center=Point(coordinates=sample_point),
                            radius=min_dist * 0.8,
                            potential=min(1.0, min_dist / search_radius),
                        )

            if best_void is None:
                raise VoidNotFoundError(
                    "No unexplored regions detected within search radius"
                )

            return best_void

        async def cluster_centers(self, k: int = 5) -> List[Point]:
            """Find k cluster centers using simple k-means."""
            if len(self._entries) == 0:
                return []

            embeddings = self._embeddings
            if embeddings is None or len(embeddings) == 0:
                return []

            k = min(k, len(embeddings))
            centers = embeddings[
                np.random.choice(len(embeddings), k, replace=False)
            ].copy()

            for _ in range(10):
                assignments = []
                for emb in embeddings:
                    dists = [self._distance(emb, c) for c in centers]
                    assignments.append(np.argmin(dists))

                new_centers = []
                for i in range(k):
                    cluster_points = embeddings[np.array(assignments) == i]
                    if len(cluster_points) > 0:
                        new_centers.append(np.mean(cluster_points, axis=0))
                    else:
                        new_centers.append(centers[i])
                centers = np.array(new_centers)

            return [Point(coordinates=c) for c in centers]

        def _rebuild_index(self) -> None:
            """Rebuild the internal index after changes."""
            if len(self._entries) == 0:
                self._embeddings = None
                self._ids = []
                return

            self._ids = list(self._entries.keys())
            self._embeddings = np.array(
                [self._entries[id].embedding for id in self._ids]
            )

        def _compute_distances(self, query: np.ndarray) -> np.ndarray:
            """Compute distances from query to all entries."""
            if self._embeddings is None or len(self._embeddings) == 0:
                return np.array([])

            return np.array([self._distance(query, emb) for emb in self._embeddings])

        def _distance(self, a: np.ndarray, b: np.ndarray) -> float:
            """Compute distance between two vectors."""
            if self.distance == DistanceMetric.COSINE:
                norm_a = np.linalg.norm(a)
                norm_b = np.linalg.norm(b)
                if norm_a == 0 or norm_b == 0:
                    return 1.0
                return 1.0 - float(np.dot(a, b) / (norm_a * norm_b))
            elif self.distance == DistanceMetric.EUCLIDEAN:
                return float(np.linalg.norm(a - b))
            elif self.distance == DistanceMetric.DOT_PRODUCT:
                return -float(np.dot(a, b))
            else:
                raise SemanticError(f"Unknown distance metric: {self.distance}")

        def _save_to_disk(self) -> None:
            """Save entries to disk."""
            if self.persistence_path is None:
                return

            path = Path(self.persistence_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "dimension": self.dimension,
                "distance": self.distance.value,
                "entries": [
                    {
                        "id": e.id,
                        "state": e.state,
                        "embedding": e.embedding.tolist(),
                        "metadata": e.metadata,
                    }
                    for e in self._entries.values()
                ],
            }

            temp_path = path.with_suffix(".tmp")
            with open(temp_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
            temp_path.replace(path)

        def _load_from_disk(self) -> None:
            """Load entries from disk."""
            if self.persistence_path is None:
                return

            path = Path(self.persistence_path)
            if not path.exists():
                return

            try:
                with open(path) as f:
                    data = json.load(f)

                self.dimension = data["dimension"]
                self.distance = DistanceMetric(data["distance"])

                for entry_data in data["entries"]:
                    entry = VectorEntry(
                        id=entry_data["id"],
                        state=entry_data["state"],
                        embedding=np.array(entry_data["embedding"], dtype=np.float32),
                        metadata=entry_data["metadata"],
                    )
                    self._entries[entry.id] = entry

                self._rebuild_index()
            except Exception as e:
                raise StorageError(f"Failed to load vector store: {e}")

else:
    # Stubs for when numpy is not available
    Point = None  # type: ignore
    Void = None  # type: ignore
    VectorEntry = None  # type: ignore
    VectorAgent = None  # type: ignore
