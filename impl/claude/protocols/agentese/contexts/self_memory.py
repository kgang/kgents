"""
AGENTESE Self Memory Context

Memory-related nodes for self.memory.* paths:
- MemoryNode: The agent's memory subsystem
- MemoryGhostNode: Ghost memory surfacing (Crown Jewel Brain)
- MemoryCartographyNode: Memory topology visualization

Updated for data-architecture-rewrite Phase 6:
- Uses new M-gent (AssociativeMemory, Memory, SoulMemory)
- Removed deprecated crystal/substrate/routing modules
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..affordances import (
    AspectCategory,
    Effect,
    aspect,
)
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Memory Affordances ===

MEMORY_AFFORDANCES: tuple[str, ...] = (
    # Core operations
    "consolidate",
    "prune",
    "checkpoint",
    "recall",
    "forget",
    "cherish",  # Pin from forgetting
    # Ghost cache operations
    "engram",  # Persist to Ghost cache
    # M-gent operations (new architecture)
    "remember",  # Store in AssociativeMemory
    "wake",  # End consolidation
    "status",  # Memory status
    # Crown Jewel Brain: High-level memory operations
    "capture",  # Capture content to Brain (embed → store)
)

# Crown Jewel Brain: Additional affordances for self.memory.*
BRAIN_AFFORDANCES: tuple[str, ...] = (
    "capture",  # Crown Jewel: capture content to Brain
)

# Affordances for ghost and cartography sub-nodes
MEMORY_GHOST_AFFORDANCES: tuple[str, ...] = (
    "manifest",  # Show current ghost state
    "surface",  # Proactively surface forgotten knowledge
    "dismiss",  # Dismiss a surfaced ghost
)

MEMORY_CARTOGRAPHY_AFFORDANCES: tuple[str, ...] = (
    "manifest",  # Show current map/topology
    "navigate",  # Navigate to a region
    "zoom",  # Zoom in/out of detail level
)


# === Memory Node ===


@dataclass
class MemoryNode(BaseLogosNode):
    """
    self.memory - The agent's memory subsystem.

    Updated for data-architecture-rewrite Phase 6.
    Uses new M-gent (AssociativeMemory, Memory, SoulMemory).

    Provides access to memory operations:
    - manifest: View current memory state
    - consolidate: Trigger hypnagogic cycle
    - prune: Garbage collect old memories
    - checkpoint: Snapshot current state
    - recall: Retrieve specific memories
    - forget: Explicitly remove memories
    - cherish: Pin from forgetting
    - remember: Store new memory
    - engram: Persist to Ghost cache

    AGENTESE: self.memory.*
    """

    _handle: str = "self.memory"

    # Memory state (simple dict fallback)
    _memories: dict[str, Any] = field(default_factory=dict)
    _checkpoints: list[dict[str, Any]] = field(default_factory=list)

    # New M-gent integration (data-architecture-rewrite)
    _associative_memory: Any = None  # AssociativeMemory from agents.m
    _soul_memory: Any = None  # SoulMemory for K-gent identity

    # Ghost cache path (for engram/manifest fallback)
    _ghost_path: Path | None = None

    # L-gent semantic embedder (Session 4: Crown Jewel Brain)
    _embedder: Any = None  # L-gent Embedder for semantic embeddings

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Memory affordances available to all archetypes."""
        return MEMORY_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("memory_state")],
        help="Display brain status and health metrics",
        examples=["kg brain", "kg brain status"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View current memory state."""
        # Try AssociativeMemory first
        if self._associative_memory is not None:
            try:
                status = await self._associative_memory.status()
                return BasicRendering(
                    summary="Memory State (M-gent)",
                    content=(
                        f"Total memories: {status.total_memories}\n"
                        f"Active: {status.active_count}\n"
                        f"Dormant: {status.dormant_count}\n"
                        f"Composting: {status.composting_count}\n"
                        f"Avg relevance: {status.average_relevance:.2f}"
                    ),
                    metadata={
                        "total_memories": status.total_memories,
                        "active_count": status.active_count,
                        "dormant_count": status.dormant_count,
                        "composting_count": status.composting_count,
                        "average_relevance": status.average_relevance,
                        "is_consolidating": status.is_consolidating,
                    },
                )
            except Exception:
                pass

        # Fallback to local dict
        return BasicRendering(
            summary="Memory State (Local)",
            content=f"Memories: {len(self._memories)} items\nCheckpoints: {len(self._checkpoints)}",
            metadata={
                "memory_count": len(self._memories),
                "checkpoint_count": len(self._checkpoints),
                "memory_keys": list(self._memories.keys())[:10],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle memory-specific aspects."""
        match aspect:
            case "consolidate":
                return await self._consolidate(observer, **kwargs)
            case "prune":
                return await self._prune(observer, **kwargs)
            case "checkpoint":
                return await self._checkpoint(observer, **kwargs)
            case "recall":
                return await self._recall(observer, **kwargs)
            case "forget":
                return await self._forget(observer, **kwargs)
            case "cherish":
                return await self._cherish(observer, **kwargs)
            case "remember":
                return await self._remember(observer, **kwargs)
            case "wake":
                return await self._wake(observer, **kwargs)
            case "status":
                return await self._status(observer, **kwargs)
            case "engram":
                return await self._engram(observer, **kwargs)
            case "capture":
                return await self._capture(observer, **kwargs)
            case "topology":
                return await self._topology(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # === Core Operations ===

    async def _consolidate(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Trigger hypnagogic memory consolidation.

        The Hypnagogic Cycle: consolidation during "sleep".
        """
        # Try AssociativeMemory
        if self._associative_memory is not None:
            try:
                report = await self._associative_memory.consolidate()
                return {
                    "dreaming_count": report.dreaming_count,
                    "demoted_count": report.demoted_count,
                    "merged_count": report.merged_count,
                    "strengthened_count": report.strengthened_count,
                    "duration_ms": report.duration_ms,
                    "status": "consolidation complete",
                }
            except Exception as e:
                return {"error": str(e)}

        # Fallback: local consolidation
        consolidated = 0
        for key, memory in list(self._memories.items()):
            if isinstance(memory, dict) and memory.get("temporary"):
                memory["temporary"] = False
                memory["consolidated_at"] = datetime.now().isoformat()
                consolidated += 1

        return {
            "consolidated": consolidated,
            "total_memories": len(self._memories),
            "status": "consolidation complete (local)",
        }

    async def _prune(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Garbage collect old/unused memories."""
        threshold = kwargs.get("threshold", 0.1)
        pruned = 0

        for key in list(self._memories.keys()):
            memory = self._memories[key]
            if isinstance(memory, dict):
                relevance = memory.get("relevance", 1.0)
                if relevance < threshold:
                    del self._memories[key]
                    pruned += 1

        return {
            "pruned": pruned,
            "remaining": len(self._memories),
            "threshold": threshold,
        }

    async def _checkpoint(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a memory checkpoint."""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "memory_count": len(self._memories),
            "keys": list(self._memories.keys()),
            "label": kwargs.get("label", f"checkpoint_{len(self._checkpoints)}"),
        }
        self._checkpoints.append(checkpoint)
        return checkpoint

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("memory_crystals"), Effect.CALLS("embedder")],
        help="Semantic search for similar memories",
        examples=["kg brain search 'category theory'", "kg brain ghost 'agents'"],
        budget_estimate="~50 tokens (embedding)",
    )
    async def _recall(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Retrieve specific memories."""
        key = kwargs.get("key")
        query = kwargs.get("query")
        limit = kwargs.get("limit", 5)

        # Try AssociativeMemory semantic search
        if self._associative_memory is not None and query:
            try:
                results = await self._associative_memory.recall(
                    cue=query,
                    limit=limit,
                    threshold=kwargs.get("threshold", 0.5),
                )
                return {
                    "query": query,
                    "results": [
                        {
                            "datum_id": r.memory.datum_id,
                            "similarity": r.similarity,
                            "relevance": r.memory.relevance,
                            "lifecycle": r.memory.lifecycle.value,
                        }
                        for r in results
                    ],
                    "count": len(results),
                }
            except Exception:
                pass

        # Fallback: local key lookup
        if key:
            return self._memories.get(key, {"not_found": key})

        if query:
            # Simple keyword search
            matches = [
                (k, v)
                for k, v in self._memories.items()
                if query.lower() in str(k).lower() or query.lower() in str(v).lower()
            ]
            return {"query": query, "matches": matches[:10]}

        return {"memories": list(self._memories.keys())[:20]}

    async def _forget(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Explicitly remove memories."""
        key = kwargs.get("key")
        memory_id = kwargs.get("memory_id", key)

        # Try AssociativeMemory
        if self._associative_memory is not None and memory_id:
            try:
                success = await self._associative_memory.forget(memory_id)
                if success:
                    return {"forgotten": memory_id, "status": "composting"}
                return {"status": "cannot forget", "reason": "cherished or not found"}
            except Exception:
                pass

        # Fallback: local
        if key and key in self._memories:
            del self._memories[key]
            return {"forgotten": key, "status": "removed"}
        return {"status": "not found", "key": key}

    async def _cherish(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Pin a memory from forgetting."""
        memory_id = kwargs.get("memory_id")

        # Try AssociativeMemory
        if self._associative_memory is not None and memory_id:
            try:
                success = await self._associative_memory.cherish(memory_id)
                if success:
                    return {"cherished": memory_id, "status": "pinned"}
                return {"status": "not found", "memory_id": memory_id}
            except Exception:
                pass

        # Fallback: local
        key = kwargs.get("key", memory_id)
        if key and key in self._memories:
            if isinstance(self._memories[key], dict):
                self._memories[key]["cherished"] = True
            return {"cherished": key, "status": "pinned (local)"}
        return {"status": "not found", "key": key}

    async def _remember(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Store new memory (M-gent remember)."""
        content = kwargs.get("content")
        if content is None:
            return {"error": "content required"}

        # Try AssociativeMemory
        if self._associative_memory is not None:
            try:
                content_bytes = content.encode() if isinstance(content, str) else content
                memory_id = await self._associative_memory.remember(
                    content=content_bytes,
                    metadata=kwargs.get("metadata", {}),
                )
                return {"remembered": True, "memory_id": memory_id}
            except Exception as e:
                return {"error": str(e)}

        # Fallback: local
        import hashlib

        key = kwargs.get("key")
        if not key:
            content_hash = hashlib.sha256(str(content).encode()).hexdigest()[:8]
            key = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{content_hash}"

        self._memories[key] = {
            "content": content,
            "metadata": kwargs.get("metadata", {}),
            "remembered_at": datetime.now().isoformat(),
            "relevance": 1.0,
        }
        return {"remembered": True, "memory_id": key, "storage": "local"}

    async def _wake(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Wake from consolidation (DREAMING → DORMANT)."""
        if self._associative_memory is not None:
            try:
                await self._associative_memory.wake()
                return {"status": "awake"}
            except Exception:
                pass
        return {"status": "awake (no-op)"}

    async def _status(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get memory system status."""
        if self._associative_memory is not None:
            try:
                status = await self._associative_memory.status()
                return {
                    "total_memories": status.total_memories,
                    "active_count": status.active_count,
                    "dormant_count": status.dormant_count,
                    "dreaming_count": status.dreaming_count,
                    "composting_count": status.composting_count,
                    "average_resolution": status.average_resolution,
                    "average_relevance": status.average_relevance,
                    "is_consolidating": status.is_consolidating,
                }
            except Exception:
                pass

        return {
            "total_memories": len(self._memories),
            "checkpoint_count": len(self._checkpoints),
            "storage": "local",
        }

    # --- Ghost Cache Operations ---

    async def _engram(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Persist state to Ghost cache for offline CLI capability.

        AGENTESE: self.memory.engram

        Ghost cache provides resilience when cluster is unavailable.

        Args:
            key: Key for the engram (e.g., "status", "map", "agents/_index")
            data: Data to persist (will be JSON serialized)
            subdirectory: Optional subdirectory (e.g., "agents", "pheromones")

        Returns:
            Dict with engram status
        """
        if self._ghost_path is None:
            self._ghost_path = Path.home() / ".kgents" / "ghost"

        key = kwargs.get("key")
        data = kwargs.get("data")

        if not key:
            return {"error": "key required"}
        if data is None:
            return {"error": "data required"}

        # Ensure ghost directory exists
        self._ghost_path.mkdir(parents=True, exist_ok=True)

        # Handle subdirectory
        subdirectory = kwargs.get("subdirectory")
        if subdirectory:
            target_dir = self._ghost_path / subdirectory
            target_dir.mkdir(parents=True, exist_ok=True)
        else:
            target_dir = self._ghost_path

        # Write engram
        engram_file = target_dir / f"{key}.json"
        try:
            engram_data = {
                "key": key,
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "agent": self._umwelt_to_meta(observer).name,
            }
            engram_file.write_text(json.dumps(engram_data, indent=2, default=str))
            return {
                "status": "engrammed",
                "key": key,
                "path": str(engram_file),
            }
        except Exception as e:
            return {"error": f"Failed to write engram: {e}"}

    # =========================================================================
    # Crown Jewel Brain: High-level operations
    # =========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[
            Effect.WRITES("memory_crystals"),
            Effect.CALLS("embedder"),
        ],
        help="Capture content to holographic memory",
        examples=["kg brain capture 'Python is great for data science'"],
        budget_estimate="~50 tokens (embedding)",
    )
    async def _capture(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Crown Jewel Brain: Capture content to holographic memory.

        AGENTESE: self.memory.capture[content="...", concept_id="..."]

        High-level flow:
        1. Accept content (text, concept, or structured data)
        2. Generate embedding (via AssociativeMemory or simple hash)
        3. Store in M-gent AssociativeMemory

        Args:
            content: The content to capture (required)
            concept_id: Optional concept identifier (auto-generated if not provided)
            metadata: Optional metadata dict to attach

        Returns:
            Dict with capture result including concept_id and storage location
        """
        content = kwargs.get("content")
        if content is None:
            return {
                "error": "content is required",
                "usage": "self.memory.capture[content='your content here']",
            }

        concept_id = kwargs.get("concept_id")
        metadata = kwargs.get("metadata", {})

        # Generate concept_id if not provided
        if concept_id is None:
            import hashlib

            content_hash = hashlib.sha256(str(content).encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            concept_id = f"capture_{timestamp}_{content_hash}"

        # Store via M-gent AssociativeMemory
        if self._associative_memory is not None:
            try:
                content_bytes = content.encode() if isinstance(content, str) else content
                memory_id = await self._associative_memory.remember(
                    content=content_bytes,
                    metadata={**metadata, "concept_id": concept_id},
                )
                return {
                    "status": "captured",
                    "concept_id": concept_id,
                    "memory_id": memory_id,
                    "storage": "associative_memory",
                    "metadata": metadata,
                }
            except Exception:
                # Fall through to local storage
                pass

        # Fallback: Store in local memory dict
        self._memories[concept_id] = {
            "content": content,
            "metadata": metadata,
            "captured_at": datetime.now().isoformat(),
        }

        return {
            "status": "captured",
            "concept_id": concept_id,
            "storage": "local_memory",
            "metadata": metadata,
            "note": "AssociativeMemory not configured, stored in local memory",
        }

    async def _topology(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Return brain topology for 3D visualization.

        AGENTESE: self.memory.topology

        Returns format matching BrainTopologyResponse expected by frontend:
        - nodes: list of topology nodes with 3D positions
        - edges: list of connections between nodes
        - gaps: list of knowledge gaps (not yet implemented)
        - hub_ids: list of hub node IDs
        - stats: aggregate statistics
        """
        import math

        # Get memories from local dict or AssociativeMemory
        memories = list(self._memories.items())
        total_count = len(memories)

        # Generate nodes from memories
        nodes = []
        for i, (key, memory) in enumerate(memories[:200]):  # Limit to 200
            # Simple 3D positioning - spiral layout
            angle = i * 0.5
            radius = 2 + i * 0.1

            content = ""
            summary = key
            captured_at = ""

            if isinstance(memory, dict):
                content = str(memory.get("content", ""))[:200]
                summary = memory.get("concept_id", key)[:50]
                captured_at = memory.get("captured_at", "")

            nodes.append(
                {
                    "id": key,
                    "label": summary,
                    "x": radius * math.cos(angle),
                    "y": (i % 5) * 0.5 - 1,  # Layer by index
                    "z": radius * math.sin(angle),
                    "resolution": 0.5,
                    "content": content,
                    "summary": summary,
                    "captured_at": captured_at,
                    "tags": [],
                }
            )

        # Generate edges (connect sequential nodes)
        edges = []
        for i in range(len(nodes) - 1):
            edges.append(
                {
                    "source": nodes[i]["id"],
                    "target": nodes[i + 1]["id"],
                    "similarity": 0.5 + (0.3 * (1 - i / max(len(nodes), 1))),
                }
            )

        # Identify hubs (first few nodes)
        hub_ids = [n["id"] for n in nodes[:3]] if nodes else []

        return {
            "nodes": nodes,
            "edges": edges,
            "gaps": [],  # Knowledge gaps - not yet implemented
            "hub_ids": hub_ids,
            "stats": {
                "concept_count": total_count,
                "edge_count": len(edges),
                "hub_count": len(hub_ids),
                "gap_count": 0,
                "avg_resolution": 0.5,
            },
        }


# === Crown Jewel Brain: Memory Sub-Nodes ===


@dataclass
class MemoryGhostNode(BaseLogosNode):
    """
    self.memory.ghost - Ghost memory surfacing.

    Crown Jewel Brain: Proactive recall of forgotten knowledge.
    Ghosts are memories that have faded but can resurface
    based on context relevance.

    AGENTESE: self.memory.ghost.*
    """

    _handle: str = "self.memory.ghost"
    _parent_memory: "MemoryNode | None" = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Ghost affordances available to all archetypes."""
        return MEMORY_GHOST_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show current ghost state."""
        ghost_count = 0
        composting_count = 0

        # Check parent memory for composting memories (ghosts)
        if self._parent_memory is not None and self._parent_memory._associative_memory is not None:
            try:
                from agents.m import Lifecycle

                composting = await self._parent_memory._associative_memory.by_lifecycle(
                    Lifecycle.COMPOSTING
                )
                composting_count = len(composting)
            except Exception:
                pass

        return BasicRendering(
            summary="Ghost Memory State",
            content=f"Composting (ghost) memories: {composting_count}",
            metadata={
                "ghost_count": ghost_count,
                "composting_count": composting_count,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle ghost-specific aspects."""
        match aspect:
            case "surface":
                return await self._surface(observer, **kwargs)
            case "dismiss":
                return await self._dismiss(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    @aspect(
        category=AspectCategory.ENTROPY,
        effects=[Effect.READS("memory_crystals")],
        help="Surface a serendipitous memory from the void",
        examples=["kg brain surface", "kg brain surface 'agents'"],
    )
    async def _surface(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Proactively surface forgotten knowledge based on context.

        AGENTESE: self.memory.ghost.surface[context="...", limit=5]

        Args:
            context: Context string to find relevant ghosts
            limit: Maximum number of ghosts to surface (default 5)

        Returns:
            List of surfaced ghost memories with relevance scores
        """
        context = kwargs.get("context", "")
        limit = kwargs.get("limit", 5)

        # Try parent memory's AssociativeMemory
        if self._parent_memory is not None and self._parent_memory._associative_memory is not None:
            try:
                # Search with lower threshold for ghosts
                results = await self._parent_memory._associative_memory.recall(
                    cue=context,
                    limit=limit,
                    threshold=0.3,  # Lower threshold for ghost surfacing
                )

                surfaced = [
                    {
                        "datum_id": r.memory.datum_id,
                        "relevance": r.similarity,
                        "lifecycle": r.memory.lifecycle.value,
                    }
                    for r in results
                ]

                return {
                    "status": "surfaced",
                    "context": context,
                    "surfaced": surfaced,
                    "count": len(surfaced),
                }
            except Exception:
                pass

        return {
            "status": "no_ghosts",
            "context": context,
            "surfaced": [],
            "count": 0,
            "note": "Ghost infrastructure not configured",
        }

    async def _dismiss(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Dismiss a surfaced ghost (mark as not relevant).

        AGENTESE: self.memory.ghost.dismiss[memory_id="..."]

        Args:
            memory_id: ID of the ghost to dismiss

        Returns:
            Confirmation of dismissal
        """
        memory_id = kwargs.get("memory_id")
        if memory_id is None:
            return {
                "error": "memory_id is required",
                "usage": "self.memory.ghost.dismiss[memory_id='...']",
            }

        # In full implementation, would track dismissals to learn user preferences
        return {
            "status": "dismissed",
            "memory_id": memory_id,
            "note": "Ghost dismissed (preference learning not yet implemented)",
        }


@dataclass
class MemoryCartographyNode(BaseLogosNode):
    """
    self.memory.cartography - Memory topology visualization.

    Crown Jewel Brain: Navigate the holographic memory landscape.

    AGENTESE: self.memory.cartography.*
    """

    _handle: str = "self.memory.cartography"
    _parent_memory: "MemoryNode | None" = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Cartography affordances available to all archetypes."""
        return MEMORY_CARTOGRAPHY_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show current memory topology."""
        # Get memory count from parent
        memory_count = 0
        if self._parent_memory is not None:
            if self._parent_memory._associative_memory is not None:
                try:
                    count = await self._parent_memory._associative_memory.count()
                    memory_count = count
                except Exception:
                    pass
            else:
                memory_count = len(self._parent_memory._memories)

        return BasicRendering(
            summary="Memory Topology",
            content=f"Memory nodes: {memory_count}",
            metadata={
                "memory_count": memory_count,
                "note": "Full cartography requires visualization layer",
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle cartography-specific aspects."""
        match aspect:
            case "navigate":
                return await self._navigate(observer, **kwargs)
            case "zoom":
                return await self._zoom(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _navigate(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Navigate to a region in memory topology.

        AGENTESE: self.memory.cartography.navigate[target="...", mode="concept"]

        Args:
            target: Target region or concept
            mode: Navigation mode ("concept", "region")

        Returns:
            Navigation result with nearby memories
        """
        target = kwargs.get("target")
        mode = kwargs.get("mode", "concept")

        if target is None:
            return {
                "error": "target is required",
                "usage": "self.memory.cartography.navigate[target='...']",
            }

        # Try semantic search to find memories near target
        if self._parent_memory is not None and self._parent_memory._associative_memory is not None:
            try:
                results = await self._parent_memory._associative_memory.recall(
                    cue=str(target),
                    limit=10,
                    threshold=0.3,
                )
                return {
                    "status": "navigated",
                    "target": target,
                    "mode": mode,
                    "nearby": [
                        {
                            "datum_id": r.memory.datum_id,
                            "similarity": r.similarity,
                        }
                        for r in results
                    ],
                    "count": len(results),
                }
            except Exception:
                pass

        return {
            "status": "navigation_unavailable",
            "target": target,
            "note": "AssociativeMemory not configured",
        }

    async def _zoom(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Zoom in/out of memory topology detail.

        AGENTESE: self.memory.cartography.zoom[level="overview"|"detail"|"focus"]

        Args:
            level: Zoom level ("overview", "detail", "focus")
            region: Optional region to zoom into

        Returns:
            Updated view at the specified zoom level
        """
        level = kwargs.get("level", "overview")
        region = kwargs.get("region")

        valid_levels = ("overview", "detail", "focus")
        if level not in valid_levels:
            return {
                "error": f"Invalid level. Must be one of: {valid_levels}",
                "usage": "self.memory.cartography.zoom[level='overview']",
            }

        return {
            "status": "zoomed",
            "level": level,
            "region": region,
            "note": "Zoom visualization requires I-gent reactive UI",
        }
