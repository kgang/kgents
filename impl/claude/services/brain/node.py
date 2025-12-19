"""
Brain AGENTESE Node: @node("self.memory")

Wraps BrainPersistence as an AGENTESE node for universal gateway access.

AGENTESE Paths:
- self.memory.manifest  - Brain health status
- self.memory.capture   - Store content to holographic memory
- self.memory.search    - Semantic search for memories
- self.memory.surface   - Serendipity from the void
- self.memory.get       - Get specific crystal by ID
- self.memory.recent    - List recent crystals
- self.memory.bytag     - List crystals by tag
- self.memory.delete    - Delete a crystal
- self.memory.heal      - Heal ghost memories

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    BrainManifestResponse,
    ByTagRequest,
    CaptureRequest,
    CaptureResponse,
    DeleteRequest,
    DeleteResponse,
    GetRequest,
    GetResponse,
    HealResponse,
    RecentRequest,
    SearchRequest,
    SearchResponse,
    SurfaceRequest,
    SurfaceResponse,
    TopologyRequest,
    TopologyResponse,
)
from .persistence import BrainPersistence, BrainStatus, CaptureResult, SearchResult

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === BrainNode Rendering ===


@dataclass(frozen=True)
class BrainManifestRendering:
    """Rendering for brain status manifest."""

    status: BrainStatus

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "brain_manifest",
            "total_crystals": self.status.total_crystals,
            "vector_count": self.status.vector_count,
            "has_semantic": self.status.has_semantic,
            "coherency_rate": self.status.coherency_rate,
            "ghosts_healed": self.status.ghosts_healed,
            "storage_path": self.status.storage_path,
            "storage_backend": self.status.storage_backend,
        }

    def to_text(self) -> str:
        lines = [
            "Brain Status",
            "============",
            f"Total Crystals: {self.status.total_crystals}",
            f"Storage Backend: {self.status.storage_backend}",
            f"Storage Path: {self.status.storage_path}",
            f"Coherency: {self.status.coherency_rate:.1%}",
        ]
        if self.status.has_semantic:
            lines.append(f"Vector Count: {self.status.vector_count}")
        if self.status.ghosts_healed > 0:
            lines.append(f"Ghosts Healed: {self.status.ghosts_healed}")
        return "\n".join(lines)


@dataclass(frozen=True)
class CaptureRendering:
    """Rendering for capture result."""

    result: CaptureResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "capture_result",
            "crystal_id": self.result.crystal_id,
            "content": self.result.content[:200]
            + ("..." if len(self.result.content) > 200 else ""),
            "summary": self.result.summary,
            "captured_at": self.result.captured_at,
            "has_embedding": self.result.has_embedding,
            "storage": self.result.storage,
            "datum_id": self.result.datum_id,
            "tags": self.result.tags,
        }

    def to_text(self) -> str:
        return (
            f"Captured: {self.result.crystal_id}\n"
            f"Summary: {self.result.summary}\n"
            f"Tags: {', '.join(self.result.tags) if self.result.tags else 'none'}"
        )


@dataclass(frozen=True)
class SearchRendering:
    """Rendering for search results."""

    results: list[SearchResult]
    query: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "search_results",
            "query": self.query,
            "count": len(self.results),
            "results": [
                {
                    "crystal_id": r.crystal_id,
                    "summary": r.summary,
                    "similarity": r.similarity,
                    "captured_at": r.captured_at,
                }
                for r in self.results
            ],
        }

    def to_text(self) -> str:
        if not self.results:
            return f"No results for: {self.query}"
        lines = [f"Search: {self.query} ({len(self.results)} results)", ""]
        for i, r in enumerate(self.results[:10], 1):
            lines.append(f"{i}. [{r.similarity:.0%}] {r.summary[:80]}")
        return "\n".join(lines)


# === BrainNode ===


@node(
    "self.memory",
    description="Holographic Brain - spatial cathedral of memory",
    dependencies=("brain_persistence",),
    contracts={
        # Perception aspects (Response only - no request needed)
        "manifest": Response(BrainManifestResponse),
        # Mutation aspects (Contract with request + response)
        "capture": Contract(CaptureRequest, CaptureResponse),
        "search": Contract(SearchRequest, SearchResponse),
        "surface": Contract(SurfaceRequest, SurfaceResponse),
        "get": Contract(GetRequest, GetResponse),
        "recent": Contract(RecentRequest, SearchResponse),
        "bytag": Contract(ByTagRequest, SearchResponse),
        "delete": Contract(DeleteRequest, DeleteResponse),
        "heal": Response(HealResponse),
        "topology": Contract(TopologyRequest, TopologyResponse),
    },
    examples=[
        ("search", {"query": "Python tips", "limit": 5}, "Search for Python"),
        ("recent", {"limit": 10}, "Show recent memories"),
        ("surface", {"entropy": 0.7}, "Surface from the void"),
        ("topology", {"max_nodes": 200}, "Visualize knowledge graph"),
    ],
)
class BrainNode(BaseLogosNode):
    """
    AGENTESE node for Brain Crown Jewel.

    Exposes BrainPersistence through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/self/memory/capture
        {"content": "Python is great for data science"}

        # Via Logos directly
        await logos.invoke("self.memory.capture", observer, content="...")

        # Via CLI
        kgents brain capture "..."
    """

    def __init__(self, brain_persistence: BrainPersistence) -> None:
        """
        Initialize BrainNode.

        BrainPersistence is REQUIRED. When Logos tries to instantiate
        without dependencies, it will fail and fall back to the existing
        SelfMemoryContext resolver. Use ServiceContainer for full DI.

        Args:
            brain_persistence: The persistence layer (injected by container)

        Raises:
            TypeError: If brain_persistence is not provided (intentional for fallback)
        """
        self._persistence = brain_persistence

    @property
    def handle(self) -> str:
        return "self.memory"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Core operations (capture, search, surface) available to all archetypes.
        Mutation operations (delete, heal) restricted to privileged archetypes.

        This matches the existing SelfMemoryContext behavior to maintain
        backward compatibility when Logos resolves self.memory paths.
        """
        # Core operations available to all archetypes
        # (matches existing MEMORY_AFFORDANCES)
        base = ("capture", "search", "surface", "get", "recent", "bytag")

        if archetype in ("developer", "admin", "system"):
            # Full access including mutations
            return base + ("delete", "heal", "topology")
        elif archetype in ("architect", "artist", "poet", "researcher"):
            # Enhanced read access with topology visualization
            return base + ("topology",)
        else:
            # Standard access - includes capture for all archetypes
            return base

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest brain status to observer.

        AGENTESE: self.memory.manifest
        """
        if self._persistence is None:
            return BasicRendering(
                summary="Brain not initialized",
                content="No persistence layer configured",
                metadata={"error": "no_persistence"},
            )

        status = await self._persistence.manifest()
        return BrainManifestRendering(status=status)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to persistence methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if self._persistence is None:
            return {"error": "Brain persistence not configured"}

        # Route to appropriate persistence method
        if aspect == "capture":
            content = kwargs.get("content", "")
            tags = kwargs.get("tags", [])
            source_type = kwargs.get("source_type", "capture")
            source_ref = kwargs.get("source_ref")
            metadata = kwargs.get("metadata")

            result = await self._persistence.capture(
                content=content,
                tags=tags,
                source_type=source_type,
                source_ref=source_ref,
                metadata=metadata,
            )
            return CaptureRendering(result=result).to_dict()

        elif aspect == "search":
            query = kwargs.get("query", "")
            limit = kwargs.get("limit", 10)
            tags = kwargs.get("tags")

            results = await self._persistence.search(
                query=query,
                limit=limit,
                tags=tags,
            )
            return SearchRendering(results=results, query=query).to_dict()

        elif aspect == "surface":
            context = kwargs.get("context")
            entropy = kwargs.get("entropy", 0.7)

            result = await self._persistence.surface(
                context=context,
                entropy=entropy,
            )
            if result is None:
                return {"surface": None, "message": "Brain is empty"}
            return {
                "surface": {
                    "crystal_id": result.crystal_id,
                    "content": result.content,
                    "summary": result.summary,
                    "similarity": result.similarity,
                },
                "entropy": entropy,
            }

        elif aspect == "get":
            crystal_id = kwargs.get("crystal_id") or kwargs.get("id")
            if not crystal_id:
                return {"error": "crystal_id required"}

            result = await self._persistence.get_by_id(crystal_id)
            if result is None:
                return {"error": f"Crystal not found: {crystal_id}"}
            return {
                "crystal_id": result.crystal_id,
                "content": result.content,
                "summary": result.summary,
                "captured_at": result.captured_at,
            }

        elif aspect == "recent":
            limit = kwargs.get("limit", 10)
            results = await self._persistence.list_recent(limit=limit)
            return SearchRendering(results=results, query="recent").to_dict()

        elif aspect == "bytag":
            tag = kwargs.get("tag", "")
            limit = kwargs.get("limit", 10)

            if not tag:
                return {"error": "tag required"}

            results = await self._persistence.list_by_tag(tag=tag, limit=limit)
            return SearchRendering(results=results, query=f"tag:{tag}").to_dict()

        elif aspect == "delete":
            crystal_id = kwargs.get("crystal_id") or kwargs.get("id")
            if not crystal_id:
                return {"error": "crystal_id required"}

            success = await self._persistence.delete(crystal_id)
            return {"deleted": success, "crystal_id": crystal_id}

        elif aspect == "heal":
            healed = await self._persistence.heal_ghosts()
            return {"healed": healed, "message": f"Healed {healed} ghost memories"}

        elif aspect == "topology":
            # Return brain topology for 3D visualization
            # Format matches BrainTopologyResponse expected by frontend
            status = await self._persistence.manifest()
            _similarity_threshold = kwargs.get(
                "similarity_threshold", 0.3
            )  # TODO: use for edge filtering

            # Get recent crystals for node generation
            crystals = await self._persistence.list_recent(limit=200)

            # Generate nodes from crystals
            nodes = []
            for i, crystal in enumerate(crystals):
                # Simple 3D positioning - spiral layout
                import math

                angle = i * 0.5
                radius = 2 + i * 0.1
                nodes.append(
                    {
                        "id": crystal.crystal_id,
                        "label": crystal.summary[:50]
                        if crystal.summary
                        else crystal.crystal_id[:8],
                        "x": radius * math.cos(angle),
                        "y": (i % 5) * 0.5 - 1,  # Layer by recency
                        "z": radius * math.sin(angle),
                        "resolution": crystal.similarity if crystal.similarity else 0.5,
                        "content": crystal.content[:200] if crystal.content else "",
                        "summary": crystal.summary or "",
                        "captured_at": crystal.captured_at or "",
                        "tags": [],
                    }
                )

            # Generate edges based on similarity (simplified - connect sequential)
            edges = []
            for i in range(len(nodes) - 1):
                if i < len(nodes) - 1:
                    edges.append(
                        {
                            "source": nodes[i]["id"],
                            "target": nodes[i + 1]["id"],
                            "similarity": 0.5 + (0.3 * (1 - i / max(len(nodes), 1))),
                        }
                    )

            # Identify hubs (nodes with high connectivity - for now, first few)
            hub_ids = [n["id"] for n in nodes[:3]] if nodes else []

            return {
                "nodes": nodes,
                "edges": edges,
                "gaps": [],  # Knowledge gaps - not yet implemented
                "hub_ids": hub_ids,
                "stats": {
                    "concept_count": status.total_crystals,
                    "edge_count": len(edges),
                    "hub_count": len(hub_ids),
                    "gap_count": 0,
                    "avg_resolution": 0.5,
                },
            }

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# === Exports ===

__all__ = [
    "BrainNode",
    "BrainManifestRendering",
    "CaptureRendering",
    "SearchRendering",
]
