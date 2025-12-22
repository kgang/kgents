"""
AGENTESE Self Vector Context

Vector-related nodes for self.vector.* paths:
- VectorNode: The agent's vector/embedding subsystem (V-gent)

Provides AGENTESE interface to V-gent (Vector Agents):
- add: Insert vector with ID and metadata
- search: Find similar vectors
- get: Retrieve vector by ID
- remove: Delete vector by ID
- count: Get number of vectors
- clear: Remove all vectors

V-gent is geometry—it maps meaning to distance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Vector Affordances ===

VECTOR_AFFORDANCES: tuple[str, ...] = (
    # Core operations
    "add",  # Insert vector
    "add_batch",  # Insert multiple vectors
    "search",  # Find similar vectors
    "get",  # Retrieve by ID
    "remove",  # Delete by ID
    "clear",  # Remove all
    "count",  # Get total count
    "exists",  # Check if ID exists
    # Introspection
    "dimension",  # Get vector dimension
    "metric",  # Get distance metric
    "status",  # Overall status
)


# === Vector Node ===


@dataclass
class VectorNode(BaseLogosNode):
    """
    self.vector - The agent's vector/embedding subsystem.

    AGENTESE interface to V-gent (Vector Agents).
    V-gent provides semantic vector operations as shared infrastructure.

    Provides access to vector operations:
    - manifest: View current vector state
    - add: Insert vector with ID and metadata
    - add_batch: Insert multiple vectors
    - search: Find similar vectors
    - get: Retrieve by ID
    - remove: Delete by ID
    - clear: Remove all
    - count: Get total count
    - exists: Check if ID exists
    - dimension: Get vector dimension
    - metric: Get distance metric
    - status: Overall status

    AGENTESE: self.vector.*
    """

    _handle: str = "self.vector"

    # V-gent integration
    _vgent: Any = None  # VgentProtocol from agents.v

    # Fallback: in-memory vectors (for graceful degradation)
    _fallback_vectors: dict[str, tuple[list[float], dict[str, str]]] = field(default_factory=dict)
    _fallback_dimension: int = 384  # Default dimension

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Vector affordances available to all archetypes."""
        return VECTOR_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View current vector state."""
        if self._vgent is not None:
            try:
                count = await self._vgent.count()
                return BasicRendering(
                    summary="Vector State (V-gent)",
                    content=(
                        f"Total vectors: {count}\n"
                        f"Dimension: {self._vgent.dimension}\n"
                        f"Metric: {self._vgent.metric.value}"
                    ),
                    metadata={
                        "total_vectors": count,
                        "dimension": self._vgent.dimension,
                        "metric": self._vgent.metric.value,
                        "backend": "vgent",
                    },
                )
            except Exception:
                pass

        # Fallback
        return BasicRendering(
            summary="Vector State (Fallback)",
            content=(
                f"Total vectors: {len(self._fallback_vectors)}\n"
                f"Dimension: {self._fallback_dimension}\n"
                f"Metric: cosine (default)"
            ),
            metadata={
                "total_vectors": len(self._fallback_vectors),
                "dimension": self._fallback_dimension,
                "metric": "cosine",
                "backend": "fallback",
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle vector-specific aspects."""
        match aspect:
            case "add":
                return await self._add(observer, **kwargs)
            case "add_batch":
                return await self._add_batch(observer, **kwargs)
            case "search":
                return await self._search(observer, **kwargs)
            case "get":
                return await self._get(observer, **kwargs)
            case "remove":
                return await self._remove(observer, **kwargs)
            case "clear":
                return await self._clear(observer, **kwargs)
            case "count":
                return await self._count(observer, **kwargs)
            case "exists":
                return await self._exists(observer, **kwargs)
            case "dimension":
                return await self._dimension(observer, **kwargs)
            case "metric":
                return await self._metric(observer, **kwargs)
            case "status":
                return await self._status(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # === Core Operations ===

    async def _add(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Add a vector to the index.

        AGENTESE: self.vector.add[id="doc1", embedding=[0.1, 0.2, ...]]

        Args:
            id: Unique identifier for this vector (required)
            embedding: The vector as list of floats (required)
            metadata: Optional filterable metadata dict

        Returns:
            Dict with add result
        """
        vector_id = kwargs.get("id")
        embedding = kwargs.get("embedding")

        if vector_id is None:
            return {
                "error": "id is required",
                "usage": "self.vector.add[id='doc1', embedding=[0.1, 0.2, ...]]",
            }

        if embedding is None:
            return {
                "error": "embedding is required",
                "usage": "self.vector.add[id='doc1', embedding=[0.1, 0.2, ...]]",
            }

        metadata = kwargs.get("metadata", {})

        # Try V-gent
        if self._vgent is not None:
            try:
                result_id = await self._vgent.add(
                    id=vector_id,
                    embedding=embedding,
                    metadata=metadata,
                )
                return {
                    "status": "added",
                    "id": result_id,
                    "backend": "vgent",
                }
            except Exception as e:
                return {"error": str(e), "backend": "vgent"}

        # Fallback
        if not isinstance(embedding, list):
            return {"error": "embedding must be a list of floats"}

        self._fallback_vectors[vector_id] = (embedding, metadata or {})
        return {
            "status": "added",
            "id": vector_id,
            "backend": "fallback",
        }

    async def _add_batch(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Add multiple vectors efficiently.

        AGENTESE: self.vector.add_batch[entries=[("id1", [0.1,...], {}), ...]]

        Args:
            entries: List of (id, embedding, metadata) tuples

        Returns:
            Dict with batch add result
        """
        entries = kwargs.get("entries")

        if entries is None:
            return {
                "error": "entries is required",
                "usage": "self.vector.add_batch[entries=[('id1', [0.1,...], {})]]",
            }

        if not isinstance(entries, list):
            return {"error": "entries must be a list"}

        # Try V-gent
        if self._vgent is not None:
            try:
                ids = await self._vgent.add_batch(entries)
                return {
                    "status": "added",
                    "ids": ids,
                    "count": len(ids),
                    "backend": "vgent",
                }
            except Exception as e:
                return {"error": str(e), "backend": "vgent"}

        # Fallback
        ids = []
        for entry in entries:
            if len(entry) >= 2:
                vid = entry[0]
                emb = entry[1]
                meta = entry[2] if len(entry) > 2 else {}
                self._fallback_vectors[vid] = (emb, meta or {})
                ids.append(vid)

        return {
            "status": "added",
            "ids": ids,
            "count": len(ids),
            "backend": "fallback",
        }

    async def _search(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Find similar vectors.

        AGENTESE: self.vector.search[query=[0.1, 0.2, ...], limit=10]

        Args:
            query: The query vector (required)
            limit: Maximum results to return (default 10)
            filters: Optional metadata filters (exact match)
            threshold: Optional minimum similarity (0.0 to 1.0)

        Returns:
            Dict with search results
        """
        query = kwargs.get("query")

        if query is None:
            return {
                "error": "query is required",
                "usage": "self.vector.search[query=[0.1, 0.2, ...]]",
            }

        limit = kwargs.get("limit", 10)
        filters = kwargs.get("filters")
        threshold = kwargs.get("threshold")

        # Try V-gent
        if self._vgent is not None:
            try:
                results = await self._vgent.search(
                    query=query,
                    limit=limit,
                    filters=filters,
                    threshold=threshold,
                )
                return {
                    "status": "found",
                    "results": [
                        {
                            "id": r.id,
                            "similarity": r.similarity,
                            "metadata": r.metadata,
                        }
                        for r in results
                    ],
                    "count": len(results),
                    "backend": "vgent",
                }
            except Exception as e:
                return {"error": str(e), "backend": "vgent"}

        # Fallback: simple cosine similarity
        import math

        def cosine_sim(a: list[float], b: list[float]) -> float:
            if len(a) != len(b):
                return 0.0
            dot = sum(x * y for x, y in zip(a, b))
            mag_a = math.sqrt(sum(x * x for x in a))
            mag_b = math.sqrt(sum(x * x for x in b))
            if mag_a == 0 or mag_b == 0:
                return 0.0
            return dot / (mag_a * mag_b)

        results = []
        for vid, (emb, meta) in self._fallback_vectors.items():
            # Apply filters
            if filters:
                if not all(meta.get(k) == v for k, v in filters.items()):
                    continue

            sim = cosine_sim(query, emb)

            # Apply threshold
            if threshold is not None and sim < threshold:
                continue

            results.append({"id": vid, "similarity": sim, "metadata": meta})

        # Sort by similarity (highest first)
        results.sort(key=lambda x: x["similarity"], reverse=True)
        results = results[:limit]

        return {
            "status": "found",
            "results": results,
            "count": len(results),
            "backend": "fallback",
        }

    async def _get(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Retrieve a vector by ID.

        AGENTESE: self.vector.get[id="doc1"]

        Args:
            id: The vector ID (required)

        Returns:
            Dict with vector entry or not_found
        """
        vector_id = kwargs.get("id")

        if vector_id is None:
            return {
                "error": "id is required",
                "usage": "self.vector.get[id='doc1']",
            }

        # Try V-gent
        if self._vgent is not None:
            try:
                entry = await self._vgent.get(vector_id)
                if entry is not None:
                    return {
                        "status": "found",
                        "id": entry.id,
                        "embedding": list(entry.embedding.values),
                        "metadata": entry.metadata,
                        "backend": "vgent",
                    }
                return {"status": "not_found", "id": vector_id, "backend": "vgent"}
            except Exception as e:
                return {"error": str(e), "backend": "vgent"}

        # Fallback
        if vector_id in self._fallback_vectors:
            emb, meta = self._fallback_vectors[vector_id]
            return {
                "status": "found",
                "id": vector_id,
                "embedding": emb,
                "metadata": meta,
                "backend": "fallback",
            }

        return {"status": "not_found", "id": vector_id, "backend": "fallback"}

    async def _remove(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Remove a vector by ID.

        AGENTESE: self.vector.remove[id="doc1"]

        Args:
            id: The vector ID (required)

        Returns:
            Dict with removal result
        """
        vector_id = kwargs.get("id")

        if vector_id is None:
            return {
                "error": "id is required",
                "usage": "self.vector.remove[id='doc1']",
            }

        # Try V-gent
        if self._vgent is not None:
            try:
                removed = await self._vgent.remove(vector_id)
                return {
                    "status": "removed" if removed else "not_found",
                    "id": vector_id,
                    "backend": "vgent",
                }
            except Exception as e:
                return {"error": str(e), "backend": "vgent"}

        # Fallback
        if vector_id in self._fallback_vectors:
            del self._fallback_vectors[vector_id]
            return {
                "status": "removed",
                "id": vector_id,
                "backend": "fallback",
            }

        return {"status": "not_found", "id": vector_id, "backend": "fallback"}

    async def _clear(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Remove all vectors from the index.

        AGENTESE: self.vector.clear

        Returns:
            Dict with clear result
        """
        # Try V-gent
        if self._vgent is not None:
            try:
                count = await self._vgent.clear()
                return {
                    "status": "cleared",
                    "removed": count,
                    "backend": "vgent",
                }
            except Exception as e:
                return {"error": str(e), "backend": "vgent"}

        # Fallback
        count = len(self._fallback_vectors)
        self._fallback_vectors.clear()
        return {
            "status": "cleared",
            "removed": count,
            "backend": "fallback",
        }

    async def _count(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get number of vectors in the index.

        AGENTESE: self.vector.count

        Returns:
            Dict with count
        """
        # Try V-gent
        if self._vgent is not None:
            try:
                count = await self._vgent.count()
                return {
                    "count": count,
                    "backend": "vgent",
                }
            except Exception as e:
                return {"error": str(e), "backend": "vgent"}

        # Fallback
        return {
            "count": len(self._fallback_vectors),
            "backend": "fallback",
        }

    async def _exists(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Check if a vector exists.

        AGENTESE: self.vector.exists[id="doc1"]

        Args:
            id: The vector ID (required)

        Returns:
            Dict with exists result
        """
        vector_id = kwargs.get("id")

        if vector_id is None:
            return {
                "error": "id is required",
                "usage": "self.vector.exists[id='doc1']",
            }

        # Try V-gent
        if self._vgent is not None:
            try:
                exists = await self._vgent.exists(vector_id)
                return {
                    "exists": exists,
                    "id": vector_id,
                    "backend": "vgent",
                }
            except Exception as e:
                return {"error": str(e), "backend": "vgent"}

        # Fallback
        return {
            "exists": vector_id in self._fallback_vectors,
            "id": vector_id,
            "backend": "fallback",
        }

    async def _dimension(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get vector dimension.

        AGENTESE: self.vector.dimension

        Returns:
            Dict with dimension
        """
        # Try V-gent
        if self._vgent is not None:
            try:
                return {
                    "dimension": self._vgent.dimension,
                    "backend": "vgent",
                }
            except Exception as e:
                return {"error": str(e), "backend": "vgent"}

        # Fallback
        return {
            "dimension": self._fallback_dimension,
            "backend": "fallback",
        }

    async def _metric(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get distance metric.

        AGENTESE: self.vector.metric

        Returns:
            Dict with metric
        """
        # Try V-gent
        if self._vgent is not None:
            try:
                return {
                    "metric": self._vgent.metric.value,
                    "backend": "vgent",
                }
            except Exception as e:
                return {"error": str(e), "backend": "vgent"}

        # Fallback
        return {
            "metric": "cosine",
            "backend": "fallback",
        }

    async def _status(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get overall vector system status.

        AGENTESE: self.vector.status

        Returns:
            Dict with status
        """
        # Try V-gent
        if self._vgent is not None:
            try:
                count = await self._vgent.count()
                return {
                    "configured": True,
                    "backend": "vgent",
                    "dimension": self._vgent.dimension,
                    "metric": self._vgent.metric.value,
                    "count": count,
                }
            except Exception as e:
                return {
                    "configured": True,
                    "backend": "vgent",
                    "error": str(e),
                }

        # Fallback
        return {
            "configured": False,
            "backend": "fallback",
            "dimension": self._fallback_dimension,
            "metric": "cosine",
            "count": len(self._fallback_vectors),
            "note": "V-gent not configured; using in-memory fallback",
        }
