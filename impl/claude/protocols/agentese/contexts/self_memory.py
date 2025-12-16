"""
AGENTESE Self Memory Context

Memory-related nodes for self.memory.* paths:
- MemoryNode: The agent's memory subsystem
- MemoryGhostNode: Ghost memory surfacing (Crown Jewel Brain)
- MemoryCartographyNode: Memory topology visualization

Extracted from self_.py for maintainability.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Memory Affordances ===

MEMORY_AFFORDANCES: tuple[str, ...] = (
    "consolidate",
    "prune",
    "checkpoint",
    "recall",
    "forget",
    # Crystal-based operations
    "crystallize",  # Create StateCrystal checkpoint
    "resume",  # Restore from StateCrystal
    "cherish",  # Pin crystal from reaping
    # Ghost cache operations
    "engram",  # Persist to Ghost cache
    # Four Pillars operations (Phase 6)
    "store",  # Store to MemoryCrystal
    "retrieve",  # Retrieve from MemoryCrystal by resonance
    "compress",  # Holographic compression
    "promote",  # Increase concept resolution
    "demote",  # Decrease concept resolution (graceful forgetting)
    "deposit",  # Deposit pheromone trace (stigmergy)
    "sense",  # Sense pheromone gradients
    "play",  # Play language game move
    "evaluate",  # Active inference evaluation
    "inference_consolidate",  # Active inference-guided consolidation
    # Phase 7: Crystallization Integration
    "reap",  # Trigger TTL-based reaping
    "expiring_soon",  # Get allocations expiring soon
    # Crown Jewel Brain: High-level memory operations
    "capture",  # Capture content to Brain (embed → store → crystallize)
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

    Provides access to memory operations:
    - manifest: View current memory state
    - consolidate: Trigger hypnagogic cycle (D-gent)
    - prune: Garbage collect old memories
    - checkpoint: Snapshot current state
    - recall: Retrieve specific memories
    - forget: Explicitly remove memories
    - crystallize: Create StateCrystal checkpoint (from ContextWindow)
    - resume: Restore ContextWindow from StateCrystal
    - cherish: Pin crystal from TTL-based reaping
    - engram: Persist state to Ghost cache

    AGENTESE: self.memory.*

    Architecture:
        Hot Memory (ContextWindow) → crystallize → Warm Memory (StateCrystal)
        Warm Memory (StateCrystal) → expire → Cold Memory (Ghost Cache)
    """

    _handle: str = "self.memory"

    # Memory state (D-gent Lens in full implementation)
    _memories: dict[str, Any] = field(default_factory=dict)
    _checkpoints: list[dict[str, Any]] = field(default_factory=list)

    # Integration points
    _d_gent: Any = None  # D-gent for persistence
    _n_gent: Any = None  # N-gent for tracing

    # Crystal infrastructure (for crystallize/resume/cherish)
    _crystallization_engine: Any = None  # CrystallizationEngine from agents.d.crystal

    # Ghost cache path (for engram/manifest fallback)
    _ghost_path: Path | None = None

    # Four Pillars integration (Phase 6)
    _memory_crystal: Any = None  # MemoryCrystal from agents.m
    _pheromone_field: Any = None  # PheromoneField from agents.m
    _inference_agent: Any = None  # ActiveInferenceAgent from agents.m
    _language_games: dict[str, Any] = field(
        default_factory=dict
    )  # name -> LanguageGame

    # Substrate integration (Phase 5)
    _substrate: Any = None  # SharedSubstrate from agents.m
    _allocation: Any = None  # Agent's Allocation in the substrate
    _router: Any = None  # CategoricalRouter from agents.m
    _compactor: Any = None  # Compactor from agents.m

    # L-gent semantic embedder (Session 4: Crown Jewel Brain)
    _embedder: Any = None  # L-gent Embedder for semantic embeddings

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Memory affordances available to all archetypes."""
        return MEMORY_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View current memory state."""
        return BasicRendering(
            summary="Memory State",
            content=f"Memories: {len(self._memories)} items\nCheckpoints: {len(self._checkpoints)}",
            metadata={
                "memory_count": len(self._memories),
                "checkpoint_count": len(self._checkpoints),
                "memory_keys": list(self._memories.keys())[:10],  # First 10
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
            # Crystal-based operations
            case "crystallize":
                return await self._crystallize(observer, **kwargs)
            case "resume":
                return await self._resume(observer, **kwargs)
            case "cherish":
                return await self._cherish(observer, **kwargs)
            # Ghost cache operations
            case "engram":
                return await self._engram(observer, **kwargs)
            # Four Pillars operations (Phase 6)
            case "store":
                return await self._store_crystal(observer, **kwargs)
            case "retrieve":
                return await self._retrieve_crystal(observer, **kwargs)
            case "compress":
                return await self._compress_crystal(observer, **kwargs)
            case "promote":
                return await self._promote_concept(observer, **kwargs)
            case "demote":
                return await self._demote_concept(observer, **kwargs)
            case "deposit":
                return await self._deposit_trace(observer, **kwargs)
            case "sense":
                return await self._sense_gradients(observer, **kwargs)
            case "play":
                return await self._play_game(observer, **kwargs)
            case "evaluate":
                return await self._evaluate_inference(observer, **kwargs)
            case "inference_consolidate":
                return await self._inference_consolidate(observer, **kwargs)
            # Substrate operations (Phase 5)
            case "allocate":
                return await self._allocate_in_substrate(observer, **kwargs)
            case "compact":
                return await self._compact_allocation(observer, **kwargs)
            case "route":
                return await self._route_task(observer, **kwargs)
            case "substrate_stats":
                return await self._substrate_stats(observer, **kwargs)
            # Phase 7: Crystallization Integration
            case "reap":
                return await self._reap(observer, **kwargs)
            case "expiring_soon":
                return await self._expiring_soon(observer, **kwargs)
            # Crown Jewel Brain: High-level operations
            case "capture":
                return await self._capture(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _consolidate(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Trigger hypnagogic memory consolidation.

        The Hypnagogic Cycle: consolidation during "sleep".
        """
        # In full implementation, this would trigger D-gent consolidation
        consolidated = 0
        for key, memory in list(self._memories.items()):
            if isinstance(memory, dict) and memory.get("temporary"):
                # Move temporary memories to consolidated state
                memory["temporary"] = False
                memory["consolidated_at"] = datetime.now().isoformat()
                consolidated += 1

        return {
            "consolidated": consolidated,
            "total_memories": len(self._memories),
            "status": "consolidation complete",
        }

    async def _prune(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Garbage collect old/unused memories."""
        threshold = kwargs.get("threshold", 0.1)  # Relevance threshold
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

    async def _recall(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Retrieve specific memories."""
        key = kwargs.get("key")
        query = kwargs.get("query")

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
        if key and key in self._memories:
            del self._memories[key]
            return {"forgotten": key, "status": "removed"}
        return {"status": "not found", "key": key}

    # --- Crystal Operations ---

    async def _crystallize(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create a StateCrystal checkpoint from current context.

        AGENTESE: self.memory.crystallize

        Args:
            context_window: The ContextWindow to crystallize
            task_id: Task identifier
            task_description: Human-readable task description
            task_status: active/paused/completed/yielded/failed
            working_memory: Optional key-value memory dict
            ttl_hours: TTL in hours (default 24)
            agent: Agent identifier (default from observer)

        Returns:
            Dict with crystal_id and crystallization details
        """
        if self._crystallization_engine is None:
            return {
                "error": "CrystallizationEngine not configured",
                "note": "Wire CrystallizationEngine to MemoryNode for crystal ops",
            }

        # Import here to avoid circular imports
        from agents.d.crystal import TaskState, TaskStatus

        context_window = kwargs.get("context_window")
        if context_window is None:
            return {"error": "context_window required for crystallization"}

        # Build task state
        task_state = TaskState(
            task_id=kwargs.get("task_id", "unknown"),
            description=kwargs.get("task_description", "No description"),
            status=TaskStatus(kwargs.get("task_status", "active")),
            progress=kwargs.get("progress", 0.0),
            metadata=kwargs.get("task_metadata", {}),
        )

        # Get agent from observer or kwargs
        meta = self._umwelt_to_meta(observer)
        agent = kwargs.get("agent", meta.name)

        # Optional TTL
        ttl_hours = kwargs.get("ttl_hours", 24)
        ttl = timedelta(hours=ttl_hours)

        # Optional parent crystal for lineage
        parent_crystal_id = kwargs.get("parent_crystal_id")
        parent_crystal = None
        if parent_crystal_id:
            parent_crystal = self._crystallization_engine.get_crystal(parent_crystal_id)

        # Crystallize
        result = await self._crystallization_engine.crystallize(
            window=context_window,
            task_state=task_state,
            agent=agent,
            working_memory=kwargs.get("working_memory"),
            parent_crystal=parent_crystal,
            ttl=ttl,
        )

        if result.success and result.crystal:
            return {
                "status": "crystallized",
                "crystal_id": result.crystal.crystal_id,
                "agent": result.crystal.agent,
                "preserved_count": result.preserved_count,
                "dropped_count": result.dropped_count,
                "summary_length": result.summary_length,
                "expires_at": result.crystal.expires_at.isoformat(),
                "pinned": result.crystal.pinned,
            }
        return {"error": result.error or "Crystallization failed"}

    async def _resume(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Restore ContextWindow from a StateCrystal.

        AGENTESE: self.memory.resume

        Args:
            crystal_id: ID of the crystal to resume from
            max_tokens: Max tokens for restored window (default 100000)

        Returns:
            Dict with restored window info or error
        """
        if self._crystallization_engine is None:
            return {
                "error": "CrystallizationEngine not configured",
                "note": "Wire CrystallizationEngine to MemoryNode for crystal ops",
            }

        crystal_id = kwargs.get("crystal_id")
        if not crystal_id:
            return {"error": "crystal_id required"}

        max_tokens = kwargs.get("max_tokens", 100_000)

        result = await self._crystallization_engine.resume(
            crystal_id=crystal_id,
            max_tokens=max_tokens,
        )

        if result.success and result.window and result.crystal:
            return {
                "status": "resumed",
                "crystal_id": crystal_id,
                "restored_fragments": result.restored_fragments,
                "task_id": result.crystal.task_state.task_id,
                "task_description": result.crystal.task_state.description,
                "task_status": result.crystal.task_state.status.value,
                "working_memory": result.crystal.working_memory,
                "window_turn_count": len(result.window.all_turns()),
            }
        return {"error": result.error or "Resume failed"}

    async def _cherish(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Pin a crystal from TTL-based reaping.

        AGENTESE: self.memory.cherish

        Cherished crystals survive until explicitly deleted.
        Use for important checkpoints worth preserving.

        Args:
            crystal_id: ID of the crystal to cherish
            uncherish: If True, unpin instead of pin

        Returns:
            Dict with cherish status
        """
        if self._crystallization_engine is None:
            return {
                "error": "CrystallizationEngine not configured",
                "note": "Wire CrystallizationEngine to MemoryNode for crystal ops",
            }

        crystal_id = kwargs.get("crystal_id")
        if not crystal_id:
            return {"error": "crystal_id required"}

        crystal = self._crystallization_engine.get_crystal(crystal_id)
        if crystal is None:
            return {"error": f"Crystal not found: {crystal_id}"}

        uncherish = kwargs.get("uncherish", False)
        if uncherish:
            crystal.uncherish()
            return {
                "status": "uncherished",
                "crystal_id": crystal_id,
                "pinned": False,
            }
        else:
            crystal.cherish()
            return {
                "status": "cherished",
                "crystal_id": crystal_id,
                "pinned": True,
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
            # Default ghost path
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

    # --- Four Pillars Operations (Phase 6) ---

    async def _store_crystal(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Store a concept in the holographic MemoryCrystal.

        AGENTESE: self.memory.store

        Args:
            concept_id: Unique identifier for the concept
            content: The content to store
            embedding: Vector representation (list of floats)

        Returns:
            Dict with storage result
        """
        if self._memory_crystal is None:
            return {
                "error": "MemoryCrystal not configured",
                "note": "Wire MemoryCrystal to MemoryNode for Four Pillars ops",
            }

        concept_id = kwargs.get("concept_id")
        content = kwargs.get("content")
        embedding = kwargs.get("embedding")

        if not concept_id:
            return {"error": "concept_id required"}
        if content is None:
            return {"error": "content required"}
        if not embedding:
            return {"error": "embedding required"}

        pattern = self._memory_crystal.store(concept_id, content, embedding)
        return {
            "status": "stored",
            "concept_id": pattern.concept_id,
            "resolution": pattern.resolution,
        }

    async def _retrieve_crystal(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Retrieve memories by resonance with cue.

        AGENTESE: self.memory.retrieve

        Args:
            cue: Query embedding vector
            threshold: Minimum similarity threshold (default 0.5)
            limit: Maximum results (default 10)

        Returns:
            List of ResonanceMatch results
        """
        if self._memory_crystal is None:
            return {"error": "MemoryCrystal not configured"}

        cue = kwargs.get("cue")
        if not cue:
            return {"error": "cue (embedding) required"}

        threshold = kwargs.get("threshold", 0.5)
        limit = kwargs.get("limit", 10)

        results = self._memory_crystal.retrieve(cue, threshold=threshold, limit=limit)
        return {
            "matches": [
                {
                    "concept_id": r.concept_id,
                    "similarity": r.similarity,
                    "resolution": r.resolution,
                }
                for r in results
            ],
            "count": len(results),
        }

    async def _compress_crystal(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Holographic compression (reduces resolution, not data).

        AGENTESE: self.memory.compress

        Args:
            ratio: Compression ratio (0.5 = halve resolution)

        Returns:
            Compression result with new stats
        """
        if self._memory_crystal is None:
            return {"error": "MemoryCrystal not configured"}

        ratio = kwargs.get("ratio", 0.8)
        try:
            self._memory_crystal = self._memory_crystal.compress(ratio)
            stats = self._memory_crystal.stats()
            return {
                "status": "compressed",
                "ratio": ratio,
                "stats": stats,
            }
        except ValueError as e:
            return {"error": str(e)}

    async def _promote_concept(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Increase resolution of a concept (reinforcement).

        AGENTESE: self.memory.promote

        Args:
            concept_id: Concept to promote
            factor: Increase factor (default 1.2 = 20% increase)

        Returns:
            Promotion result
        """
        if self._memory_crystal is None:
            return {"error": "MemoryCrystal not configured"}

        concept_id = kwargs.get("concept_id")
        if not concept_id:
            return {"error": "concept_id required"}

        factor = kwargs.get("factor", 1.2)
        self._memory_crystal.promote(concept_id, factor=factor)

        pattern = self._memory_crystal.get_pattern(concept_id)
        return {
            "status": "promoted",
            "concept_id": concept_id,
            "new_resolution": pattern.resolution if pattern else None,
        }

    async def _demote_concept(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Decrease resolution of a concept (graceful forgetting).

        AGENTESE: self.memory.demote

        Args:
            concept_id: Concept to demote
            factor: Reduction factor (default 0.5 = halve)

        Returns:
            Demotion result
        """
        if self._memory_crystal is None:
            return {"error": "MemoryCrystal not configured"}

        concept_id = kwargs.get("concept_id")
        if not concept_id:
            return {"error": "concept_id required"}

        factor = kwargs.get("factor", 0.5)
        self._memory_crystal.demote(concept_id, factor=factor)

        pattern = self._memory_crystal.get_pattern(concept_id)
        return {
            "status": "demoted",
            "concept_id": concept_id,
            "new_resolution": pattern.resolution if pattern else None,
        }

    async def _deposit_trace(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Deposit a pheromone trace (stigmergy).

        AGENTESE: self.memory.deposit

        The act of depositing IS the tithe—paying forward
        for future agents who will follow these trails.

        Args:
            concept: The concept to mark
            intensity: Trace strength (default 1.0)
            metadata: Optional metadata dict

        Returns:
            Deposit result
        """
        if self._pheromone_field is None:
            return {
                "error": "PheromoneField not configured",
                "note": "Wire PheromoneField to MemoryNode for stigmergic ops",
            }

        concept = kwargs.get("concept")
        if not concept:
            return {"error": "concept required"}

        intensity = kwargs.get("intensity", 1.0)
        metadata = kwargs.get("metadata")
        meta = self._umwelt_to_meta(observer)

        trace = await self._pheromone_field.deposit(
            concept=concept,
            intensity=intensity,
            depositor=meta.name,
            metadata=metadata,
        )
        return {
            "status": "deposited",
            "concept": trace.concept,
            "intensity": trace.intensity,
            "depositor": trace.depositor,
        }

    async def _sense_gradients(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Sense pheromone gradients.

        AGENTESE: self.memory.sense

        Returns concepts sorted by total trace intensity.

        Args:
            position: Optional current position for context

        Returns:
            List of gradients
        """
        if self._pheromone_field is None:
            return {"error": "PheromoneField not configured"}

        position = kwargs.get("position")
        gradients = await self._pheromone_field.sense(position)

        return {
            "gradients": [
                {
                    "concept": g.concept,
                    "total_intensity": g.total_intensity,
                    "trace_count": g.trace_count,
                    "dominant_depositor": g.dominant_depositor,
                }
                for g in gradients
            ],
            "count": len(gradients),
        }

    async def _play_game(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Play a move in a language game.

        AGENTESE: self.memory.play

        Memory access as playing a game (Wittgenstein).

        Args:
            game: Game name (recall, navigation, dialectical, etc.)
            position: Current position/state
            direction: Direction to move

        Returns:
            Move result
        """
        game_name = kwargs.get("game")
        if not game_name:
            return {
                "error": "game required",
                "available_games": list(self._language_games.keys()),
            }

        game = self._language_games.get(game_name)
        if game is None:
            return {
                "error": f"Unknown game: {game_name}",
                "available_games": list(self._language_games.keys()),
            }

        position = kwargs.get("position")
        direction = kwargs.get("direction")

        if position is None:
            return {"error": "position required"}
        if not direction:
            # Return available directions
            directions = game.directions(position)
            return {
                "game": game_name,
                "position": position,
                "available_directions": list(directions),
            }

        move = game.play(position, direction)
        return {
            "game": game_name,
            "from_position": move.from_position,
            "direction": move.direction,
            "to_position": move.to_position,
            "is_grammatical": move.is_grammatical,
        }

    async def _evaluate_inference(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Evaluate memory with Active Inference.

        AGENTESE: self.memory.evaluate

        Compute free energy budget for a memory.

        Args:
            concept_id: The concept to evaluate
            content: The content (for complexity calculation)
            relevance: Semantic relevance (0 to 1)

        Returns:
            Free energy evaluation
        """
        if self._inference_agent is None:
            return {
                "error": "ActiveInferenceAgent not configured",
                "note": "Wire ActiveInferenceAgent to MemoryNode for inference ops",
            }

        concept_id = kwargs.get("concept_id")
        content = kwargs.get("content", "")
        relevance = kwargs.get("relevance", 0.5)

        if not concept_id:
            return {"error": "concept_id required"}

        budget = await self._inference_agent.evaluate_memory(
            concept_id=concept_id,
            content=content,
            relevance=relevance,
        )

        return {
            "concept_id": concept_id,
            "free_energy": budget.free_energy,
            "complexity_cost": budget.complexity_cost,
            "accuracy_gain": budget.accuracy_gain,
            "should_retain": budget.should_retain(),
            "recommendation": (
                "promote"
                if budget.free_energy < -0.5
                else "retain"
                if budget.free_energy < 0
                else "demote"
                if budget.free_energy < 0.5
                else "forget"
            ),
        }

    async def _inference_consolidate(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Consolidate memory using Active Inference.

        AGENTESE: self.memory.inference_consolidate

        Uses free energy minimization to decide what to promote/demote.

        Args:
            promote_threshold: Free energy below this → promote (default -0.5)
            demote_threshold: Free energy above this → demote (default 0.5)

        Returns:
            Consolidation actions taken
        """
        if self._memory_crystal is None:
            return {"error": "MemoryCrystal not configured"}
        if self._inference_agent is None:
            return {"error": "ActiveInferenceAgent not configured"}

        try:
            from agents.m import InferenceGuidedCrystal

            guided = InferenceGuidedCrystal(self._memory_crystal, self._inference_agent)

            promote_threshold = kwargs.get("promote_threshold", -0.5)
            demote_threshold = kwargs.get("demote_threshold", 0.5)

            actions = await guided.consolidate(
                promote_threshold=promote_threshold,
                demote_threshold=demote_threshold,
            )

            promoted = sum(1 for a in actions.values() if a == "promoted")
            demoted = sum(1 for a in actions.values() if a == "demoted")
            retained = sum(1 for a in actions.values() if a == "retained")

            return {
                "status": "consolidated",
                "actions": actions,
                "summary": {
                    "promoted": promoted,
                    "demoted": demoted,
                    "retained": retained,
                },
            }
        except ImportError:
            return {"error": "agents.m module not available"}

    # --- Substrate Operations (Phase 5) ---
    #
    # Memory Flow:
    #
    #   SharedSubstrate (building)
    #        │
    #        ├── allocate() ──► Allocation (room)
    #        │                      │
    #        │                      ├── store/retrieve
    #        │                      │
    #        │                      └── compact() ──► Resolution↓
    #        │
    #        └── route() ─────► Task → Agent (via pheromone gradients)
    #
    # Adjunction: deposit ⊣ route (left adjoint creates gradients)

    async def _allocate_in_substrate(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Allocate memory in the shared substrate.

        AGENTESE: self.memory.allocate

        Each agent gets a "room" in the substrate building.
        The allocation provides namespaced storage with quota limits.

        Args:
            human_label: Human-readable label (required for no debris)
            max_patterns: Maximum patterns in allocation (default 1000)
            ttl_hours: Time-to-live in hours (default 24)

        Returns:
            Allocation details
        """
        if self._substrate is None:
            return {
                "error": "SharedSubstrate not configured",
                "note": "Wire SharedSubstrate to MemoryNode for substrate ops",
            }

        meta = self._umwelt_to_meta(observer)
        human_label = kwargs.get("human_label", f"{meta.name} working memory")
        max_patterns = kwargs.get("max_patterns", 1000)
        ttl_hours = kwargs.get("ttl_hours", 24)

        try:
            from agents.m.substrate import LifecyclePolicy, MemoryQuota

            quota = MemoryQuota(max_patterns=max_patterns)
            lifecycle = LifecyclePolicy(
                human_label=human_label,
                ttl=timedelta(hours=ttl_hours),
            )

            allocation = self._substrate.allocate(
                agent_id=meta.name,
                quota=quota,
                lifecycle=lifecycle,
            )

            # Store allocation for future use
            self._allocation = allocation

            return {
                "status": "allocated",
                "agent_id": str(allocation.agent_id),
                "namespace": allocation.namespace,
                "max_patterns": quota.max_patterns,
                "human_label": human_label,
                "ttl_hours": ttl_hours,
            }
        except ImportError:
            return {"error": "agents.m.substrate module not available"}
        except ValueError as e:
            return {"error": str(e)}

    async def _compact_allocation(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Compact the agent's memory allocation.

        AGENTESE: self.memory.compact

        Compaction = purposeful forgetting (Accursed Share).
        Reduces resolution to free space while preserving all concepts.

        Args:
            force: Force compaction even if below threshold (default False)

        Returns:
            Compaction event details or None if not needed
        """
        if self._allocation is None:
            return {
                "error": "No allocation exists",
                "note": "Use self.memory.allocate first",
            }

        if self._compactor is None:
            return {
                "error": "Compactor not configured",
                "note": "Wire Compactor to MemoryNode for compaction ops",
            }

        force = kwargs.get("force", False)

        try:
            event = await self._compactor.compact_allocation(
                allocation=self._allocation,
                force=force,
            )

            if event is None:
                return {
                    "status": "not_needed",
                    "reason": "Below compaction threshold",
                    "usage_ratio": self._allocation.usage_ratio(),
                }

            return {
                "status": "compacted",
                "ratio": event.ratio,
                "patterns_before": event.patterns_before,
                "patterns_after": event.patterns_after,
                "resolution_loss": event.resolution_loss,
                "duration_ms": event.duration_ms,
                "reason": event.reason,
            }
        except Exception as e:
            return {"error": f"Compaction failed: {e}"}

    async def _route_task(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Route a task to the best agent via pheromone gradients.

        AGENTESE: self.memory.route

        Uses stigmergic routing: tasks follow pheromone trails
        deposited by previous successful agent-task pairings.

        The adjunction: deposit ⊣ route
        Depositing creates gradients; routing follows them.

        Args:
            concept: Primary concept for routing
            content: Task content/description
            priority: Task priority (0 to 1)
            related: Related concepts for multi-gradient routing

        Returns:
            Routing decision with chosen agent and confidence
        """
        if self._router is None:
            return {
                "error": "CategoricalRouter not configured",
                "note": "Wire CategoricalRouter to MemoryNode for routing ops",
            }

        concept = kwargs.get("concept")
        if not concept:
            return {"error": "concept required"}

        try:
            from agents.m.routing import Task

            task = Task(
                concept=concept,
                content=kwargs.get("content", ""),
                priority=kwargs.get("priority", 0.5),
                related_concepts=kwargs.get("related", []),
            )

            decision = await self._router.route(task)

            return {
                "status": "routed",
                "agent_id": decision.agent_id,
                "confidence": decision.confidence,
                "gradient_strength": decision.gradient_strength,
                "reasoning": decision.reasoning,
                "alternatives": [
                    {"agent_id": aid, "score": score}
                    for aid, score in decision.alternatives
                ],
            }
        except ImportError:
            return {"error": "agents.m.routing module not available"}
        except Exception as e:
            return {"error": f"Routing failed: {e}"}

    async def _substrate_stats(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get substrate statistics.

        AGENTESE: self.memory.substrate_stats

        Returns metrics about the shared memory substrate.

        Returns:
            Substrate statistics including allocation counts, patterns, etc.
        """
        if self._substrate is None:
            return {
                "error": "SharedSubstrate not configured",
                "stats": None,
            }

        stats: dict[str, Any] = self._substrate.stats()

        # Add allocation-specific info if we have one
        if self._allocation is not None:
            stats["current_allocation"] = {
                "agent_id": str(self._allocation.agent_id),
                "pattern_count": self._allocation.pattern_count,
                "usage_ratio": self._allocation.usage_ratio(),
                "is_at_soft_limit": self._allocation.is_at_soft_limit(),
            }

        # Add compactor stats if available
        if self._compactor is not None:
            stats["compactor"] = self._compactor.stats()

        # Add router stats if available
        if self._router is not None:
            stats["router"] = self._router.stats()

        return stats

    # =========================================================================
    # Phase 7: Crystallization Integration
    # =========================================================================

    async def _reap(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Trigger TTL-based reaping of expired allocations.

        AGENTESE: self.memory.reap
                  self.memory.reap[policy=ttl]

        This triggers the ReaperIntegration to reap:
        1. Expired allocations (based on TTL)
        2. Expired crystals (via CrystalReaper)

        Args:
            policy: Optional policy type (default: "ttl")

        Returns:
            Dict with reap results including events emitted
        """
        if self._substrate is None:
            return {
                "error": "SharedSubstrate not configured",
                "reaped": 0,
            }

        # Import ReaperIntegration
        from agents.m.crystallization_integration import ReaperIntegration

        # Check if we have a reaper integration wired
        reaper_integration = getattr(self, "_reaper_integration", None)

        if reaper_integration is None:
            # Create a minimal reaper integration with mock CrystalReaper
            from agents.d.crystal import CrystalReaper

            reaper_integration = ReaperIntegration(
                reaper=CrystalReaper(),
                substrate=self._substrate,
            )

        events = await reaper_integration.reap_all()

        return {
            "reaped": len(events),
            "events": [
                {
                    "event_type": e.event_type,
                    "agent_id": e.agent_id,
                    "patterns_affected": e.patterns_affected,
                    "reason": e.reason,
                }
                for e in events
            ],
            "allocations_remaining": len(self._substrate.allocations),
        }

    async def _expiring_soon(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get allocations expiring soon.

        AGENTESE: self.memory.expiring_soon
                  self.memory.expiring_soon[threshold=1h]

        Args:
            threshold: Time until expiration to consider "soon" (default 1 hour)
                      Format: "1h", "30m", "2d"

        Returns:
            List of allocations that will expire within threshold
        """
        if self._substrate is None:
            return {
                "error": "SharedSubstrate not configured",
                "expiring": [],
            }

        # Parse threshold
        threshold_str = kwargs.get("threshold", "1h")
        threshold = self._parse_timedelta(threshold_str)

        # Find expiring allocations
        expiring = []
        now = datetime.now()
        for agent_id, allocation in self._substrate.allocations.items():
            expires_at = allocation.created_at + allocation.lifecycle.ttl
            time_remaining = expires_at - now
            if timedelta(0) < time_remaining < threshold:
                expiring.append(
                    {
                        "agent_id": str(agent_id),
                        "human_label": allocation.lifecycle.human_label,
                        "expires_at": expires_at.isoformat(),
                        "time_remaining_seconds": time_remaining.total_seconds(),
                        "pattern_count": allocation.pattern_count,
                    }
                )

        return {
            "threshold": threshold_str,
            "threshold_seconds": threshold.total_seconds(),
            "expiring": expiring,
            "count": len(expiring),
        }

    def _parse_timedelta(self, s: str) -> timedelta:
        """Parse a duration string like '1h', '30m', '2d' to timedelta."""
        import re

        # Pattern: digits + unit (s=seconds, m=minutes, h=hours, d=days)
        match = re.match(r"^(\d+)([smhd])$", s.lower())
        if not match:
            return timedelta(hours=1)  # Default

        value = int(match.group(1))
        unit = match.group(2)

        if unit == "s":
            return timedelta(seconds=value)
        elif unit == "m":
            return timedelta(minutes=value)
        elif unit == "h":
            return timedelta(hours=value)
        elif unit == "d":
            return timedelta(days=value)
        else:
            return timedelta(hours=1)

    # =========================================================================
    # Crown Jewel Brain: High-level operations
    # =========================================================================

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
        2. Generate embedding (via MemoryCrystal or simple hash)
        3. Store in Four Pillars MemoryCrystal
        4. Optionally queue for D-gent crystallization

        Args:
            content: The content to capture (required)
            concept_id: Optional concept identifier (auto-generated if not provided)
            crystallize: Whether to queue for D-gent crystallization (default False)
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
        should_crystallize = kwargs.get("crystallize", False)
        metadata = kwargs.get("metadata", {})

        # Generate concept_id if not provided
        if concept_id is None:
            import hashlib

            content_hash = hashlib.sha256(str(content).encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            concept_id = f"capture_{timestamp}_{content_hash}"

        # Attempt to store in Four Pillars MemoryCrystal
        if self._memory_crystal is not None:
            # MemoryCrystal supports store(concept_id, content, embedding)
            # Use L-gent semantic embedding if available (Session 4)
            embedding = await self._get_embedding(str(content))
            # Note: MemoryCrystal.store() is synchronous
            pattern = self._memory_crystal.store(concept_id, content, embedding)
            success = pattern is not None

            if success:
                result = {
                    "status": "captured",
                    "concept_id": concept_id,
                    "storage": "memory_crystal",
                    "metadata": metadata,
                }

                # Optionally queue for D-gent crystallization
                if should_crystallize and self._crystallization_engine is not None:
                    await self._crystallization_engine.queue_crystallization(
                        concept_id, content, metadata
                    )
                    result["crystallization_queued"] = True

                return result

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
            "note": "MemoryCrystal not configured, stored in local memory",
        }

    async def _get_embedding(self, text: str) -> list[float]:
        """
        Get semantic embedding for text.

        Uses L-gent embedder if configured, otherwise falls back to
        simple hash-based pseudo-embedding.

        Session 4 Crown Jewel Brain: Wire real semantic embeddings.
        """
        if self._embedder is not None:
            # Use L-gent semantic embedder (async)
            try:
                embedding = await self._embedder.embed(text)
                return embedding
            except Exception:
                # Fall back to simple embedding on error
                pass

        # Fallback: hash-based pseudo-embedding (no semantic similarity)
        return self._simple_embedding(text)

    def _simple_embedding(self, text: str) -> list[float]:
        """
        Generate simple hash-based embedding (NO semantic similarity).

        This is a fallback when L-gent embedder is not configured.
        Hash-based embeddings are deterministic but DO NOT capture
        semantic similarity - "Python code" and "Python programming"
        will have completely different embeddings.

        For real semantic search, wire L-gent embedder via create_brain_logos().
        """
        import hashlib

        # Create 64-dimensional pseudo-embedding from hash
        h = hashlib.sha256(text.encode()).digest()
        # Convert bytes to floats in [-1, 1] range
        embedding = [(b - 128) / 128.0 for b in h[:32]]
        # Pad to 64 dimensions by repeating
        embedding = embedding + embedding
        return embedding


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

    # GhostSyncManager for cache coherence
    _ghost_sync: Any = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Ghost affordances available to all archetypes."""
        return MEMORY_GHOST_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show current ghost state."""
        ghost_count = 0
        sync_events = 0

        if self._ghost_sync is not None:
            sync_events = len(self._ghost_sync.events)

        return BasicRendering(
            summary="Ghost Memory State",
            content=f"Ghost entries: {ghost_count}\nSync events: {sync_events}",
            metadata={
                "ghost_count": ghost_count,
                "sync_events": sync_events,
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

        # If we have a parent memory with MemoryCrystal, do semantic search
        if (
            self._parent_memory is not None
            and self._parent_memory._memory_crystal is not None
        ):
            # Generate embedding for context (uses L-gent if configured)
            embedding = await self._parent_memory._get_embedding(context)

            # Search for similar patterns (MemoryCrystal.retrieve() is synchronous)
            results = self._parent_memory._memory_crystal.retrieve(
                cue=embedding,
                threshold=0.3,  # Lower threshold for ghost surfacing
                limit=limit,
            )

            surfaced = []
            for pattern in results:
                # Results are ResonanceMatch objects with concept_id and similarity
                # Also retrieve the actual content for display
                content = None
                if hasattr(self._parent_memory._memory_crystal, "retrieve_content"):
                    concept_id = getattr(pattern, "concept_id", "unknown")
                    content = self._parent_memory._memory_crystal.retrieve_content(
                        concept_id
                    )

                surfaced.append(
                    {
                        "concept_id": getattr(pattern, "concept_id", "unknown"),
                        "relevance": getattr(pattern, "similarity", 0.5),
                        "content": content,
                        "faded_ago": "estimated",  # Would track actual time in production
                    }
                )

            return {
                "status": "surfaced",
                "context": context,
                "surfaced": surfaced,
                "count": len(surfaced),
            }

        # Fallback: Return empty list if no infrastructure
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

        AGENTESE: self.memory.ghost.dismiss[concept_id="..."]

        Args:
            concept_id: ID of the ghost to dismiss

        Returns:
            Confirmation of dismissal
        """
        concept_id = kwargs.get("concept_id")
        if concept_id is None:
            return {
                "error": "concept_id is required",
                "usage": "self.memory.ghost.dismiss[concept_id='...']",
            }

        # In full implementation, would track dismissals to learn user preferences
        return {
            "status": "dismissed",
            "concept_id": concept_id,
            "note": "Ghost dismissed (preference learning not yet implemented)",
        }


@dataclass
class MemoryCartographyNode(BaseLogosNode):
    """
    self.memory.cartography - Memory topology visualization.

    Crown Jewel Brain: Navigate the holographic memory landscape.
    Uses CartographerAgent to generate HoloMaps.

    AGENTESE: self.memory.cartography.*
    """

    _handle: str = "self.memory.cartography"
    _parent_memory: "MemoryNode | None" = None

    # CartographerAgent for map generation
    _cartographer: Any = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Cartography affordances available to all archetypes."""
        return MEMORY_CARTOGRAPHY_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show current memory topology."""
        if self._cartographer is not None:
            # Generate HoloMap via CartographerAgent.invoke()
            try:
                from agents.m.cartography import ContextVector

                # Create context vector from current state
                # Use simple embedding for now; in production, use L-gent
                context = ContextVector(
                    embedding=[0.0] * 64,  # Default position
                    label="current_context",
                )

                # If we have parent memory with stored memories, use their centroid
                if self._parent_memory is not None and self._parent_memory._memories:
                    # Average embedding of stored memories as context
                    pass  # Use default for now

                holo_map = await self._cartographer.invoke(context)
                return BasicRendering(
                    summary="Memory Topology",
                    content=f"Landmarks: {len(holo_map.landmarks)}\n"
                    f"Desire Lines: {len(holo_map.desire_lines)}\n"
                    f"Voids: {len(holo_map.voids)}",
                    metadata={
                        "landmarks": len(holo_map.landmarks),
                        "desire_lines": len(holo_map.desire_lines),
                        "voids": len(holo_map.voids),
                        "resolution": holo_map.resolution.value,
                    },
                )
            except Exception:
                pass

        # Fallback: Basic topology from parent memory
        if self._parent_memory is not None:
            memory_count = len(self._parent_memory._memories)
            return BasicRendering(
                summary="Memory Topology (Simplified)",
                content=f"Memory nodes: {memory_count}",
                metadata={
                    "memory_count": memory_count,
                    "note": "CartographerAgent not configured",
                },
            )

        return BasicRendering(
            summary="Memory Topology",
            content="No topology available",
            metadata={"note": "Memory infrastructure not configured"},
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

        AGENTESE: self.memory.cartography.navigate[target="...", mode="landmark"]

        Args:
            target: Target region or concept ID
            mode: Navigation mode ("landmark", "region", "concept")

        Returns:
            Navigation result with path and destination info
        """
        target = kwargs.get("target")
        mode = kwargs.get("mode", "concept")

        if target is None:
            return {
                "error": "target is required",
                "usage": "self.memory.cartography.navigate[target='...']",
            }

        # If we have CartographerAgent, use its navigation
        if self._cartographer is not None:
            try:
                nav_result = await self._cartographer.navigate_to(target, mode)
                return {
                    "status": "navigated",
                    "target": target,
                    "mode": mode,
                    "path": nav_result.get("path", []),
                    "distance": nav_result.get("distance", 0),
                }
            except Exception as e:
                return {
                    "error": f"Navigation failed: {e}",
                    "target": target,
                }

        return {
            "status": "navigation_unavailable",
            "target": target,
            "note": "CartographerAgent not configured",
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
