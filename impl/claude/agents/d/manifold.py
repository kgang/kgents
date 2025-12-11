"""
SemanticManifold: Curved semantic space with geometry.

The Semantic Manifold extends VectorAgent with geometric understanding:
- Curvature: Regions where concepts cluster (low) vs boundaries (high)
- Voids (Ma): Unexplored regions with generative potential
- Geodesics: Natural paths of semantic transformation

Philosophy: "Meaning is not stored—it is navigated."

Part of the Noosphere Layer (D-gent Phase 4).
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
    NoosphereError,
    SemanticError,
    VoidNotFoundError,
)

S = TypeVar("S")  # State type


class CurvatureRegion(Enum):
    """Semantic curvature classification."""

    LOW = "low"  # < 0.3: Stable semantic region, easy retrieval
    MEDIUM = "medium"  # 0.3-0.7: Transitional zone
    HIGH = "high"  # > 0.7: Conceptual boundary, synthesis opportunity


@dataclass
class SemanticPoint:
    """A point in semantic space with rich metadata."""

    coordinates: Any  # np.ndarray when numpy available
    label: str = ""
    metadata: dict = field(default_factory=dict)
    curvature: float = 0.0  # Local curvature at this point

    def distance_to(self, other: "SemanticPoint", metric: str = "cosine") -> float:
        """Compute distance to another point."""
        if not NUMPY_AVAILABLE:
            raise SemanticError("numpy required for distance computation")

        a, b = self.coordinates, other.coordinates
        if metric == "cosine":
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            if norm_a == 0 or norm_b == 0:
                return 1.0
            return 1.0 - float(np.dot(a, b) / (norm_a * norm_b))
        elif metric == "euclidean":
            return float(np.linalg.norm(a - b))
        else:
            raise SemanticError(f"Unknown metric: {metric}")


@dataclass
class SemanticVoid:
    """
    An unexplored region (Ma) in semantic space.

    Voids are generative—they suggest what could exist but doesn't yet.
    Aligned with the "Void's Fecundity" principle in Membrane Protocol.
    """

    center: SemanticPoint
    radius: float
    potential: float  # 0.0-1.0: Estimated generative value
    nearest_concepts: List[str] = field(default_factory=list)
    suggested_exploration: str = ""

    @property
    def is_fertile(self) -> bool:
        """High potential for discovery."""
        return self.potential > 0.6


@dataclass
class Geodesic:
    """
    Path of minimum semantic distance between two concepts.

    Useful for:
    - Understanding conceptual transitions
    - Generating intermediate states
    - Detecting barriers (high-curvature points on the path)
    """

    start: SemanticPoint
    end: SemanticPoint
    waypoints: List[SemanticPoint]
    total_length: float
    max_curvature: float
    barriers: List[int] = field(
        default_factory=list
    )  # Indices of high-curvature waypoints

    @property
    def is_smooth(self) -> bool:
        """Path has no significant barriers."""
        return self.max_curvature < 0.7


@dataclass
class SemanticCluster:
    """A cluster of related concepts."""

    center: SemanticPoint
    members: List[str]  # Entry IDs
    radius: float
    coherence: float  # 0.0-1.0: How tightly clustered


@dataclass
class ManifoldStats:
    """Statistics about the semantic manifold."""

    total_entries: int
    dimension: int
    num_clusters: int
    average_curvature: float
    void_count: int
    coverage: float  # 0.0-1.0: How much of the space is explored


if NUMPY_AVAILABLE:

    class SemanticManifold(Generic[S]):
        """
        Curved semantic space for meaning navigation.

        The Semantic Manifold extends VectorAgent with geometric understanding:
        - Curvature analysis reveals conceptual boundaries
        - Void detection finds unexplored regions
        - Geodesics provide natural transformation paths
        - Cluster analysis reveals semantic structure

        Philosophy: "Meaning is not stored—it is navigated."

        Example:
            >>> manifold = SemanticManifold(dimension=768)
            >>> await manifold.add("doc1", "Machine learning is...", embedding1)
            >>> await manifold.add("doc2", "Deep learning extends...", embedding2)
            >>>
            >>> # Find conceptually similar
            >>> neighbors = await manifold.neighbors(query_embedding, k=5)
            >>>
            >>> # Detect synthesis opportunities
            >>> curvature = await manifold.curvature_at(query_embedding)
            >>> if curvature > 0.7:
            ...     # High curvature = boundary between domains
            ...     print("Synthesis opportunity!")
            >>>
            >>> # Find unexplored regions
            >>> void = await manifold.void_nearby(query_embedding)
            >>> print(f"Unexplored region with potential: {void.potential}")
        """

        def __init__(
            self,
            dimension: int,
            embedder: Optional[Callable[[S], np.ndarray]] = None,
            distance_metric: str = "cosine",
            persistence_path: Optional[Path] = None,
        ):
            """
            Initialize semantic manifold.

            Args:
                dimension: Embedding vector dimension
                embedder: Optional function to embed states to vectors
                distance_metric: "cosine", "euclidean", or "dot_product"
                persistence_path: Optional path for persistent storage
            """
            self.dimension = dimension
            self.embedder = embedder
            self.distance_metric = distance_metric
            self.persistence_path = persistence_path

            # Storage
            self._entries: dict[
                str, Tuple[S, np.ndarray, dict]
            ] = {}  # id -> (state, embedding, metadata)
            self._embeddings: Optional[np.ndarray] = None
            self._ids: List[str] = []

            # Curvature cache
            self._curvature_cache: dict[str, float] = {}

            if persistence_path and Path(persistence_path).exists():
                self._load_from_disk()

        # === Core Operations ===

        async def add(
            self,
            entry_id: str,
            state: S,
            embedding: np.ndarray,
            metadata: Optional[dict] = None,
        ) -> SemanticPoint:
            """
            Add state with explicit embedding to the manifold.

            Returns SemanticPoint with computed curvature.
            """
            if embedding.shape[0] != self.dimension:
                raise SemanticError(
                    f"Embedding dimension {embedding.shape[0]} != manifold dimension {self.dimension}"
                )

            self._entries[entry_id] = (
                state,
                embedding.astype(np.float32),
                metadata or {},
            )
            self._rebuild_index()
            self._curvature_cache.clear()

            if self.persistence_path:
                self._save_to_disk()

            # Compute point with curvature
            curvature = await self.curvature_at(embedding)
            return SemanticPoint(
                coordinates=embedding,
                label=entry_id,
                metadata=metadata or {},
                curvature=curvature,
            )

        async def embed(self, state: S) -> SemanticPoint:
            """Project state into semantic space using embedder."""
            if self.embedder is None:
                raise SemanticError("No embedder configured")

            coords = self.embedder(state)
            curvature = (
                await self.curvature_at(coords) if len(self._entries) > 0 else 0.0
            )

            return SemanticPoint(
                coordinates=coords,
                curvature=curvature,
            )

        async def get(self, entry_id: str) -> Optional[Tuple[S, SemanticPoint]]:
            """Get entry by ID with its semantic point."""
            if entry_id not in self._entries:
                return None

            state, embedding, metadata = self._entries[entry_id]
            curvature = self._curvature_cache.get(entry_id)
            if curvature is None:
                curvature = await self.curvature_at(embedding)
                self._curvature_cache[entry_id] = curvature

            point = SemanticPoint(
                coordinates=embedding,
                label=entry_id,
                metadata=metadata,
                curvature=curvature,
            )
            return state, point

        async def delete(self, entry_id: str) -> bool:
            """Delete entry by ID."""
            if entry_id not in self._entries:
                return False

            del self._entries[entry_id]
            self._curvature_cache.pop(entry_id, None)
            self._rebuild_index()

            if self.persistence_path:
                self._save_to_disk()
            return True

        # === Similarity Search ===

        async def neighbors(
            self,
            query: np.ndarray,
            k: int = 5,
            radius: Optional[float] = None,
        ) -> List[Tuple[S, SemanticPoint, float]]:
            """
            Find k nearest neighbors to query vector.

            Returns list of (state, point, distance) tuples.
            """
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

                state, embedding, metadata = self._entries[entry_id]
                curvature = self._curvature_cache.get(entry_id)
                if curvature is None:
                    curvature = await self.curvature_at(embedding)
                    self._curvature_cache[entry_id] = curvature

                point = SemanticPoint(
                    coordinates=embedding,
                    label=entry_id,
                    metadata=metadata,
                    curvature=curvature,
                )
                results.append((state, point, dist))

            return results

        async def nearest_states(
            self, query: np.ndarray, k: int = 5
        ) -> List[Tuple[S, float]]:
            """Convenience: Find k nearest states (no point metadata)."""
            results = await self.neighbors(query, k=k)
            return [(state, dist) for state, _, dist in results]

        # === Geometric Operations ===

        async def curvature_at(self, point: np.ndarray, radius: float = 0.5) -> float:
            """
            Estimate local semantic curvature at a point.

            High curvature (> 0.7): Conceptual boundary
            - Many different concepts nearby
            - Synthesis opportunities
            - Creative connections possible

            Medium curvature (0.3-0.7): Transitional zone
            - Mix of similar and different concepts

            Low curvature (< 0.3): Stable semantic region
            - Similar concepts cluster tightly
            - Easy retrieval
            - High confidence matches
            """
            if len(self._entries) < 3:
                return 0.0

            distances = self._compute_distances(point)
            nearby_mask = distances <= radius
            nearby_distances = distances[nearby_mask]

            if len(nearby_distances) < 2:
                return 0.0

            # Curvature = variance / mean (coefficient of variation)
            variance = float(np.var(nearby_distances))
            mean_dist = float(np.mean(nearby_distances))

            if mean_dist > 0:
                return min(1.0, variance / mean_dist)
            return variance

        def classify_curvature(self, curvature: float) -> CurvatureRegion:
            """Classify curvature into semantic regions."""
            if curvature < 0.3:
                return CurvatureRegion.LOW
            elif curvature < 0.7:
                return CurvatureRegion.MEDIUM
            else:
                return CurvatureRegion.HIGH

        async def geodesic(
            self,
            start: np.ndarray,
            end: np.ndarray,
            steps: int = 10,
        ) -> Geodesic:
            """
            Compute geodesic (shortest semantic path) between two points.

            The geodesic is the "natural" transformation path between concepts.
            Returns path with curvature analysis at each waypoint.
            """
            waypoints = []
            curvatures = []

            for i in range(steps + 1):
                t = i / steps
                coords = start * (1 - t) + end * t
                curvature = await self.curvature_at(coords)
                curvatures.append(curvature)

                waypoints.append(
                    SemanticPoint(
                        coordinates=coords,
                        curvature=curvature,
                    )
                )

            # Identify barriers (high-curvature waypoints)
            barriers = [i for i, c in enumerate(curvatures) if c > 0.7]

            # Total path length
            total_length = 0.0
            for i in range(len(waypoints) - 1):
                total_length += waypoints[i].distance_to(
                    waypoints[i + 1], self.distance_metric
                )

            start_point = SemanticPoint(coordinates=start, curvature=curvatures[0])
            end_point = SemanticPoint(coordinates=end, curvature=curvatures[-1])

            return Geodesic(
                start=start_point,
                end=end_point,
                waypoints=waypoints,
                total_length=total_length,
                max_curvature=max(curvatures),
                barriers=barriers,
            )

        # === Void Detection (Ma) ===

        async def void_nearby(
            self,
            point: np.ndarray,
            search_radius: float = 1.0,
            min_void_radius: float = 0.2,
        ) -> SemanticVoid:
            """
            Detect unexplored regions (Ma) near a point.

            Voids are generative—they suggest what could exist but doesn't yet.

            Detection heuristics:
            - Low density of existing states
            - Distance from all known clusters
            - Semantic coherence (not random noise)
            """
            if len(self._entries) < 2:
                return SemanticVoid(
                    center=SemanticPoint(coordinates=point, curvature=0.0),
                    radius=search_radius,
                    potential=1.0,
                    suggested_exploration="Unexplored space - any direction is valid",
                )

            # Sample points in the neighborhood
            num_samples = 20
            best_void = None
            best_potential = 0.0

            for _ in range(num_samples):
                # Random direction
                direction = np.random.randn(self.dimension)
                direction = direction / np.linalg.norm(direction)

                # Sample at different distances
                for dist_factor in [0.2, 0.5, 0.8]:
                    sample_point = point + direction * search_radius * dist_factor
                    distances = self._compute_distances(sample_point)
                    min_dist = float(np.min(distances))

                    if min_dist > min_void_radius and min_dist > best_potential:
                        best_potential = min_dist

                        # Find nearest concepts for context
                        nearest_indices = np.argsort(distances)[:3]
                        nearest_concepts = [self._ids[i] for i in nearest_indices]

                        curvature = await self.curvature_at(sample_point)
                        center = SemanticPoint(
                            coordinates=sample_point,
                            curvature=curvature,
                        )

                        best_void = SemanticVoid(
                            center=center,
                            radius=min_dist * 0.8,
                            potential=min(1.0, min_dist / search_radius),
                            nearest_concepts=nearest_concepts,
                            suggested_exploration=f"Between {', '.join(nearest_concepts[:2])}",
                        )

            if best_void is None:
                raise VoidNotFoundError(
                    "No unexplored regions detected within search radius"
                )

            return best_void

        async def find_all_voids(
            self,
            min_potential: float = 0.5,
            max_voids: int = 10,
        ) -> List[SemanticVoid]:
            """Find all significant unexplored regions."""
            if len(self._entries) < 3:
                return []

            voids = []
            # Sample around existing points
            for entry_id, (_, embedding, _) in self._entries.items():
                try:
                    void = await self.void_nearby(embedding, search_radius=0.5)
                    if void.potential >= min_potential:
                        voids.append(void)
                except VoidNotFoundError:
                    continue

            # Sort by potential and deduplicate
            voids.sort(key=lambda v: v.potential, reverse=True)
            return voids[:max_voids]

        # === Cluster Analysis ===

        async def cluster_centers(self, k: int = 5) -> List[SemanticCluster]:
            """
            Find k cluster centers using k-means.

            Returns clusters with coherence metrics.
            """
            if len(self._entries) == 0:
                return []

            embeddings = self._embeddings
            if embeddings is None or len(embeddings) == 0:
                return []

            k = min(k, len(embeddings))

            # K-means clustering
            centers = embeddings[
                np.random.choice(len(embeddings), k, replace=False)
            ].copy()

            for _ in range(10):  # Max iterations
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

            # Build cluster objects
            clusters = []
            for i in range(k):
                cluster_mask = np.array(assignments) == i
                cluster_embeddings = embeddings[cluster_mask]
                member_ids = [
                    self._ids[j] for j in range(len(self._ids)) if assignments[j] == i
                ]

                if len(cluster_embeddings) == 0:
                    continue

                # Compute radius and coherence
                center = centers[i]
                distances = [self._distance(center, emb) for emb in cluster_embeddings]
                radius = max(distances) if distances else 0.0
                coherence = 1.0 - (np.mean(distances) if distances else 0.0)

                curvature = await self.curvature_at(center)
                center_point = SemanticPoint(
                    coordinates=center,
                    curvature=curvature,
                    metadata={"cluster_id": i},
                )

                clusters.append(
                    SemanticCluster(
                        center=center_point,
                        members=member_ids,
                        radius=radius,
                        coherence=max(0.0, min(1.0, coherence)),
                    )
                )

            return clusters

        # === Statistics ===

        async def stats(self) -> ManifoldStats:
            """Get manifold statistics."""
            clusters = await self.cluster_centers(k=min(5, len(self._entries)))
            voids = await self.find_all_voids(min_potential=0.3, max_voids=5)

            # Average curvature
            curvatures = []
            for entry_id in self._ids:
                if entry_id in self._curvature_cache:
                    curvatures.append(self._curvature_cache[entry_id])

            avg_curvature = np.mean(curvatures) if curvatures else 0.0

            # Coverage: rough estimate based on void potential
            if voids:
                avg_void_potential = np.mean([v.potential for v in voids])
                coverage = 1.0 - avg_void_potential
            else:
                coverage = 1.0 if len(self._entries) > 0 else 0.0

            return ManifoldStats(
                total_entries=len(self._entries),
                dimension=self.dimension,
                num_clusters=len(clusters),
                average_curvature=float(avg_curvature),
                void_count=len(voids),
                coverage=coverage,
            )

        # === Internal Methods ===

        def _rebuild_index(self) -> None:
            """Rebuild internal index after changes."""
            if len(self._entries) == 0:
                self._embeddings = None
                self._ids = []
                return

            self._ids = list(self._entries.keys())
            self._embeddings = np.array([self._entries[id][1] for id in self._ids])

        def _compute_distances(self, query: np.ndarray) -> np.ndarray:
            """Compute distances from query to all entries."""
            if self._embeddings is None or len(self._embeddings) == 0:
                return np.array([])

            return np.array([self._distance(query, emb) for emb in self._embeddings])

        def _distance(self, a: np.ndarray, b: np.ndarray) -> float:
            """Compute distance between two vectors."""
            if self.distance_metric == "cosine":
                norm_a = np.linalg.norm(a)
                norm_b = np.linalg.norm(b)
                if norm_a == 0 or norm_b == 0:
                    return 1.0
                return 1.0 - float(np.dot(a, b) / (norm_a * norm_b))
            elif self.distance_metric == "euclidean":
                return float(np.linalg.norm(a - b))
            elif self.distance_metric == "dot_product":
                return -float(np.dot(a, b))
            else:
                raise SemanticError(f"Unknown distance metric: {self.distance_metric}")

        def _save_to_disk(self) -> None:
            """Save manifold to disk."""
            if self.persistence_path is None:
                return

            path = Path(self.persistence_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "dimension": self.dimension,
                "distance_metric": self.distance_metric,
                "entries": [
                    {
                        "id": entry_id,
                        "state": state,
                        "embedding": embedding.tolist(),
                        "metadata": metadata,
                    }
                    for entry_id, (state, embedding, metadata) in self._entries.items()
                ],
            }

            temp_path = path.with_suffix(".tmp")
            with open(temp_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
            temp_path.replace(path)

        def _load_from_disk(self) -> None:
            """Load manifold from disk."""
            if self.persistence_path is None:
                return

            path = Path(self.persistence_path)
            if not path.exists():
                return

            try:
                with open(path) as f:
                    data = json.load(f)

                self.dimension = data["dimension"]
                self.distance_metric = data["distance_metric"]

                for entry_data in data["entries"]:
                    self._entries[entry_data["id"]] = (
                        entry_data["state"],
                        np.array(entry_data["embedding"], dtype=np.float32),
                        entry_data["metadata"],
                    )

                self._rebuild_index()
            except Exception as e:
                raise NoosphereError(f"Failed to load manifold: {e}")

else:
    # Stub when numpy not available
    SemanticManifold = None  # type: ignore
    SemanticPoint = None  # type: ignore
    SemanticVoid = None  # type: ignore
    Geodesic = None  # type: ignore
    SemanticCluster = None  # type: ignore
    ManifoldStats = None  # type: ignore
    CurvatureRegion = None  # type: ignore
