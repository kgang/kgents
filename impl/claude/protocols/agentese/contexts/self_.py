"""
AGENTESE Self Context Resolver

The Internal: memory, capability, state, agent boundaries.

self.* handles resolve to internal agent state and capabilities:
- self.memory - Agent's memory and recall
- self.capabilities - What the agent can do
- self.state - Current operational state
- self.identity - Agent's identity and DNA

Principle Alignment: Ethical (boundaries of agency)

Note: Named self_.py because 'self' is a Python reserved word.
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

from .self_judgment import CriticsLoop, Critique, RefinedArtifact
from .vitals import VitalsContextResolver, create_vitals_resolver

# === Self Affordances ===

SELF_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "memory": (
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
    ),
    "capabilities": ("list", "acquire", "release"),
    "state": ("checkpoint", "restore", "inspect"),
    "identity": ("reflect", "evolve"),
    "judgment": (
        "taste",
        "surprise",
        "expectations",
        "calibrate",
        "critique",
        "refine",
    ),
    "semaphore": ("pending", "yield", "status"),
    "vitals": ("triad", "synapse", "resonance", "circuit", "durability", "reflex"),
}


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

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Memory affordances available to all archetypes."""
        return SELF_AFFORDANCES["memory"]

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


# === Capabilities Node ===


@dataclass
class CapabilitiesNode(BaseLogosNode):
    """
    self.capabilities - What the agent can do.

    Provides introspection into agent capabilities.
    """

    _handle: str = "self.capabilities"
    _capabilities: set[str] = field(default_factory=set)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Capability introspection affordances."""
        return SELF_AFFORDANCES["capabilities"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """List current capabilities."""
        meta = self._umwelt_to_meta(observer)
        return BasicRendering(
            summary=f"Capabilities of {meta.name}",
            content="\n".join(sorted(self._capabilities))
            if self._capabilities
            else "No capabilities registered",
            metadata={
                "archetype": meta.archetype,
                "capability_count": len(self._capabilities),
                "capabilities": sorted(self._capabilities),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle capability aspects."""
        match aspect:
            case "list":
                return sorted(self._capabilities)
            case "acquire":
                capability = kwargs.get("capability")
                if capability:
                    self._capabilities.add(capability)
                    return {"acquired": capability, "total": len(self._capabilities)}
                return {"error": "capability required"}
            case "release":
                capability = kwargs.get("capability")
                if capability and capability in self._capabilities:
                    self._capabilities.discard(capability)
                    return {"released": capability, "total": len(self._capabilities)}
                return {"error": "capability not found"}
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# === State Node ===


@dataclass
class StateNode(BaseLogosNode):
    """
    self.state - Current operational state.

    Provides state inspection and management.
    """

    _handle: str = "self.state"
    _state: dict[str, Any] = field(default_factory=dict)
    _snapshots: list[dict[str, Any]] = field(default_factory=list)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """State management affordances."""
        return SELF_AFFORDANCES["state"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Inspect current state."""
        return BasicRendering(
            summary="Agent State",
            content=f"State keys: {list(self._state.keys())}",
            metadata={
                "state": self._state,
                "snapshot_count": len(self._snapshots),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle state aspects."""
        match aspect:
            case "checkpoint":
                snapshot = {
                    "timestamp": datetime.now().isoformat(),
                    "state": dict(self._state),
                    "label": kwargs.get("label", f"snapshot_{len(self._snapshots)}"),
                }
                self._snapshots.append(snapshot)
                return snapshot
            case "restore":
                index = kwargs.get("index", -1)
                if self._snapshots:
                    snapshot = self._snapshots[index]
                    self._state = dict(snapshot["state"])
                    return {"restored": snapshot["label"]}
                return {"error": "no snapshots available"}
            case "inspect":
                key = kwargs.get("key")
                if key:
                    return self._state.get(key, {"not_found": key})
                return dict(self._state)
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# === Judgment Node ===


@dataclass
class JudgmentNode(BaseLogosNode):
    """
    self.judgment - Aesthetic judgment and taste.

    Provides access to the Wundt Curator for aesthetic filtering:
    - taste: Evaluate aesthetic quality (returns TasteScore)
    - surprise: Measure Bayesian surprise
    - expectations: View/set prior expectations
    - calibrate: Learn optimal thresholds from feedback
    - critique: SPECS-based evaluation (novelty, utility, surprise)
    - refine: Iterative refinement loop with critique feedback

    AGENTESE: self.judgment.*

    Principle Alignment:
    - Tasteful: Architectural quality filtering
    - Joy-Inducing: Interesting > Boring or Chaotic
    """

    _handle: str = "self.judgment"

    # Wundt Curator configuration
    _low_threshold: float = 0.1
    _high_threshold: float = 0.9
    _expectations: dict[str, Any] = field(default_factory=dict)

    # Critics Loop for SPECS-based evaluation
    _critics_loop: CriticsLoop | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Judgment affordances available to all archetypes."""
        return SELF_AFFORDANCES["judgment"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View current judgment configuration."""
        return BasicRendering(
            summary="Judgment Configuration",
            content=(
                f"Wundt Curve Thresholds:\n"
                f"  Boring threshold: < {self._low_threshold}\n"
                f"  Chaotic threshold: > {self._high_threshold}\n"
                f"  Expectations: {len(self._expectations)} priors set"
            ),
            metadata={
                "low_threshold": self._low_threshold,
                "high_threshold": self._high_threshold,
                "expectation_keys": list(self._expectations.keys()),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle judgment aspects."""
        match aspect:
            case "taste":
                return await self._evaluate_taste(observer, **kwargs)
            case "surprise":
                return await self._measure_surprise(observer, **kwargs)
            case "expectations":
                return self._manage_expectations(observer, **kwargs)
            case "calibrate":
                return self._calibrate(observer, **kwargs)
            case "critique":
                return await self._critique_artifact(observer, **kwargs)
            case "refine":
                return await self._refine_artifact(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _evaluate_taste(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Evaluate aesthetic taste via Wundt Curve.

        Args:
            content: The content to evaluate
            prior: Optional prior expectation (defaults to observer context)

        Returns:
            TasteScore-like dict with novelty, complexity, verdict
        """
        from ..middleware.curator import (
            SemanticDistance,
            TasteScore,
            structural_surprise,
        )

        content = kwargs.get("content")
        prior = kwargs.get("prior")

        if content is None:
            return {"error": "content required"}

        # Get prior from context if not provided
        if prior is None:
            prior = self._expectations.get("prior")
            # Also check observer context (using getattr for type safety)
            if prior is None:
                obs_context = getattr(observer, "context", {})
                if isinstance(obs_context, dict):
                    obs_expectations = obs_context.get("expectations", {})
                    if isinstance(obs_expectations, dict):
                        prior = obs_expectations.get("prior")

        # Compute surprise
        if prior is not None:
            content_str = str(content)
            prior_str = str(prior)
            novelty = structural_surprise(content_str, prior_str)
        else:
            novelty = 0.5  # Neutral when no prior

        # Create TasteScore
        score = TasteScore.from_novelty(
            novelty=novelty,
            complexity=0.5,  # Default complexity
            low_threshold=self._low_threshold,
            high_threshold=self._high_threshold,
        )

        return {
            "novelty": score.novelty,
            "complexity": score.complexity,
            "wundt_score": score.wundt_score,
            "verdict": score.verdict,
            "is_acceptable": score.is_acceptable,
        }

    async def _measure_surprise(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> float:
        """
        Measure Bayesian surprise between content and prior.

        Args:
            content: The content to measure
            prior: The expected content

        Returns:
            Surprise value between 0.0 and 1.0
        """
        from ..middleware.curator import structural_surprise

        content = kwargs.get("content")
        prior = kwargs.get("prior", self._expectations.get("prior"))

        if content is None:
            return 0.5  # Neutral

        if prior is None:
            return 0.5  # Neutral when no prior

        return structural_surprise(str(content), str(prior))

    def _manage_expectations(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        View or set prior expectations.

        Args:
            set_key: Key to set (if setting)
            set_value: Value to set (if setting)
            get_key: Key to get (if getting)
            clear: If True, clear all expectations

        Returns:
            Current expectations or operation result
        """
        if kwargs.get("clear"):
            self._expectations.clear()
            return {"status": "cleared", "expectations": {}}

        set_key = kwargs.get("set_key")
        set_value = kwargs.get("set_value")
        if set_key and set_value is not None:
            self._expectations[set_key] = set_value
            return {"status": "set", "key": set_key}

        get_key = kwargs.get("get_key")
        if get_key:
            return {"key": get_key, "value": self._expectations.get(get_key)}

        return {"expectations": dict(self._expectations)}

    def _calibrate(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Calibrate thresholds from feedback.

        Args:
            low: New low threshold
            high: New high threshold
            feedback: List of (content, rating) tuples for learning

        Returns:
            Updated thresholds
        """
        low = kwargs.get("low")
        high = kwargs.get("high")

        if low is not None:
            self._low_threshold = max(0.0, min(low, 1.0))
        if high is not None:
            self._high_threshold = max(0.0, min(high, 1.0))

        # Ensure low < high
        if self._low_threshold >= self._high_threshold:
            self._high_threshold = min(self._low_threshold + 0.1, 1.0)

        return {
            "status": "calibrated",
            "low_threshold": self._low_threshold,
            "high_threshold": self._high_threshold,
        }

    def _get_or_create_loop(self) -> CriticsLoop:
        """Get or create the CriticsLoop instance."""
        if self._critics_loop is None:
            self._critics_loop = CriticsLoop()
        return self._critics_loop

    async def _critique_artifact(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        SPECS-based critique of an artifact.

        Args:
            artifact: The artifact to evaluate
            purpose: Optional purpose for utility assessment
            prior_work: Optional list of prior work for novelty comparison

        Returns:
            Critique result as dict (novelty, utility, surprise, overall, reasoning)
        """
        artifact = kwargs.get("artifact")
        if artifact is None:
            return {"error": "artifact required"}

        purpose = kwargs.get("purpose")
        prior_work = kwargs.get("prior_work")

        loop = self._get_or_create_loop()
        critique = await loop.critique(
            artifact, observer, purpose=purpose, prior_work=prior_work
        )
        return critique.to_dict()

    async def _refine_artifact(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Iterative refinement loop with critique feedback.

        Requires a Logos instance to be passed for generation.

        Args:
            logos: Logos instance for invocations
            generator_path: AGENTESE path for generation
            purpose: Optional purpose for utility assessment
            threshold: Optional threshold (default 0.7)
            max_iterations: Optional max iterations (default 3)
            **generator_kwargs: Additional args for the generator

        Returns:
            RefinedArtifact result as dict
        """
        logos = kwargs.get("logos")
        generator_path = kwargs.get("generator_path")

        if logos is None:
            return {"error": "logos required"}
        if generator_path is None:
            return {"error": "generator_path required"}

        purpose = kwargs.get("purpose")
        threshold = kwargs.get("threshold", 0.7)
        max_iterations = kwargs.get("max_iterations", 3)

        # Extract generator kwargs (remove our params)
        generator_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k
            not in ("logos", "generator_path", "purpose", "threshold", "max_iterations")
        }

        loop = CriticsLoop(threshold=threshold, max_iterations=max_iterations)
        result = await loop.generate_with_trace(
            logos, observer, generator_path, purpose=purpose, **generator_kwargs
        )
        return result.to_dict()


# === Semaphore Node ===


@dataclass
class SemaphoreNode(BaseLogosNode):
    """
    self.semaphore - Agent's pending semaphores.

    Provides access to semaphore tokens that require human intervention:
    - pending: List pending semaphores for this agent
    - yield: Create a new semaphore (agent yields control)
    - status: Get status of a specific semaphore

    Integration with Purgatory:
    The SemaphoreNode bridges the AGENTESE path system with the
    Agent Semaphore system, allowing agents to query and create
    semaphores through the standard AGENTESE interface.

    AGENTESE: self.semaphore.*
    """

    _handle: str = "self.semaphore"

    # Integration points
    _purgatory: Any = None  # Purgatory instance for token storage

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Semaphore affordances available to all archetypes."""
        return SELF_AFFORDANCES["semaphore"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View pending semaphores for this agent."""
        pending = await self._get_pending(observer)
        return BasicRendering(
            summary="Pending Semaphores",
            content=f"Pending: {len(pending)} semaphores awaiting response",
            metadata={
                "pending_count": len(pending),
                "semaphore_ids": [t.get("id") for t in pending],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle semaphore-specific aspects."""
        match aspect:
            case "pending":
                return await self._get_pending(observer, **kwargs)
            case "yield":
                return await self._yield_semaphore(observer, **kwargs)
            case "status":
                return await self._get_status(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _get_pending(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        List pending semaphores for this agent.

        Returns list of token summaries (not full token objects to avoid
        leaking frozen state).
        """
        if self._purgatory is None:
            return []

        try:
            tokens = self._purgatory.list_pending()
            # Filter by agent if agent_id is available in observer
            agent_id = kwargs.get("agent_id")
            if agent_id:
                # Would need to track agent_id in token for filtering
                pass

            # Return summaries, not full tokens
            return [
                {
                    "id": t.id,
                    "reason": t.reason.value
                    if hasattr(t.reason, "value")
                    else str(t.reason),
                    "prompt": t.prompt,
                    "options": t.options,
                    "severity": t.severity,
                    "deadline": t.deadline.isoformat() if t.deadline else None,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
                for t in tokens
            ]
        except Exception:
            return []

    async def _yield_semaphore(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create a new semaphore (agent yields control).

        This is the AGENTESE interface for creating semaphores.
        Agents call this when they need human intervention.

        Args:
            reason: Why the semaphore is needed (approval_needed, context_required, etc.)
            prompt: Human-readable question/prompt
            options: Optional list of options to present
            severity: info, warning, or critical
            deadline: Optional deadline as ISO string or timedelta
            escalation: Optional escalation contact

        Returns:
            Dict with token_id and status
        """
        if self._purgatory is None:
            return {
                "error": "Purgatory not configured",
                "note": "SemaphoreNode requires Purgatory integration",
            }

        try:
            # Import here to avoid circular imports
            from agents.flux.semaphore import SemaphoreReason, SemaphoreToken

            # Parse reason
            reason_str = kwargs.get("reason", "approval_needed")
            try:
                reason = SemaphoreReason(reason_str)
            except ValueError:
                reason = SemaphoreReason.APPROVAL_NEEDED

            # Parse deadline
            deadline = None
            deadline_arg = kwargs.get("deadline")
            if deadline_arg:
                from datetime import timedelta

                if isinstance(deadline_arg, timedelta):
                    deadline = datetime.now() + deadline_arg
                elif isinstance(deadline_arg, str):
                    deadline = datetime.fromisoformat(deadline_arg)

            # Create token
            token: SemaphoreToken[Any] = SemaphoreToken(
                reason=reason,
                prompt=kwargs.get("prompt", ""),
                options=kwargs.get("options", []),
                severity=kwargs.get("severity", "info"),
                deadline=deadline,
                escalation=kwargs.get("escalation"),
            )

            # Save to purgatory
            await self._purgatory.save(token)

            return {
                "token_id": token.id,
                "status": "pending",
                "reason": reason.value,
                "prompt": token.prompt,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_status(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get status of a specific semaphore.

        Args:
            token_id: The semaphore token ID

        Returns:
            Token status dict or error
        """
        token_id = kwargs.get("token_id")
        if not token_id:
            return {"error": "token_id required"}

        if self._purgatory is None:
            return {"error": "Purgatory not configured"}

        try:
            token = self._purgatory.get(token_id)
            if token is None:
                return {"error": "Token not found", "token_id": token_id}

            return {
                "token_id": token.id,
                "status": (
                    "resolved"
                    if token.is_resolved
                    else "cancelled"
                    if token.is_cancelled
                    else "voided"
                    if token.is_voided
                    else "pending"
                ),
                "reason": token.reason.value
                if hasattr(token.reason, "value")
                else str(token.reason),
                "prompt": token.prompt,
                "severity": token.severity,
                "created_at": token.created_at.isoformat()
                if token.created_at
                else None,
                "resolved_at": token.resolved_at.isoformat()
                if token.resolved_at
                else None,
                "cancelled_at": token.cancelled_at.isoformat()
                if token.cancelled_at
                else None,
                "voided_at": token.voided_at.isoformat() if token.voided_at else None,
            }
        except Exception as e:
            return {"error": str(e)}


# === Identity Node ===


@dataclass
class IdentityNode(BaseLogosNode):
    """
    self.identity - Agent's identity and DNA.

    Provides introspection into the agent's identity.
    """

    _handle: str = "self.identity"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Identity introspection affordances."""
        return SELF_AFFORDANCES["identity"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View identity from observer's DNA."""
        meta = self._umwelt_to_meta(observer)
        dna = observer.dna

        return BasicRendering(
            summary=f"Identity: {meta.name}",
            content=f"Archetype: {meta.archetype}\nCapabilities: {meta.capabilities}",
            metadata={
                "name": meta.name,
                "archetype": meta.archetype,
                "capabilities": meta.capabilities,
                "dna_type": type(dna).__name__,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle identity aspects."""
        match aspect:
            case "reflect":
                meta = self._umwelt_to_meta(observer)
                return {
                    "name": meta.name,
                    "archetype": meta.archetype,
                    "capabilities": list(meta.capabilities),
                    "reflection": f"I am {meta.name}, a {meta.archetype}.",
                }
            case "evolve":
                # Evolution requires careful consideration
                return {
                    "status": "identity evolution requires deliberation",
                    "note": "Use concept.identity.refine for deep evolution",
                }
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# === Self Context Resolver ===


@dataclass
class SelfContextResolver:
    """
    Resolver for self.* context.

    The self context provides introspection into the agent's
    internal state, memory, capabilities, identity, judgment, and semaphores.
    """

    # D-gent integration for persistence
    _d_gent: Any = None
    # N-gent integration for tracing
    _n_gent: Any = None
    # Purgatory for semaphore integration
    _purgatory: Any = None
    # CrystallizationEngine for memory crystal operations
    _crystallization_engine: Any = None
    # Ghost cache path for offline capability
    _ghost_path: Path | None = None
    # Four Pillars integration (Phase 6)
    _memory_crystal: Any = None  # MemoryCrystal from agents.m
    _pheromone_field: Any = None  # PheromoneField from agents.m
    _inference_agent: Any = None  # ActiveInferenceAgent from agents.m
    _language_games: dict[str, Any] = field(default_factory=dict)

    # Singleton nodes for self context
    _memory: MemoryNode | None = None
    _capabilities: CapabilitiesNode | None = None
    _state: StateNode | None = None
    _identity: IdentityNode | None = None
    _judgment: JudgmentNode | None = None
    _semaphore: SemaphoreNode | None = None
    # Vitals context resolver for self.vitals.*
    _vitals_resolver: VitalsContextResolver | None = None

    def __post_init__(self) -> None:
        """Initialize singleton nodes."""
        self._memory = MemoryNode(
            _d_gent=self._d_gent,
            _n_gent=self._n_gent,
            _crystallization_engine=self._crystallization_engine,
            _ghost_path=self._ghost_path,
            _memory_crystal=self._memory_crystal,
            _pheromone_field=self._pheromone_field,
            _inference_agent=self._inference_agent,
            _language_games=self._language_games,
        )
        self._capabilities = CapabilitiesNode()
        self._state = StateNode()
        self._identity = IdentityNode()
        self._judgment = JudgmentNode()
        self._semaphore = SemaphoreNode(_purgatory=self._purgatory)
        self._vitals_resolver = create_vitals_resolver()

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode:
        """
        Resolve a self.* path to a node.

        Args:
            holon: The self subsystem (memory, capabilities, state, identity, judgment, semaphore, vitals)
            rest: Additional path components

        Returns:
            Resolved node

        Note:
            For vitals, rest contains the vitals component (triad, synapse, resonance, circuit).
            E.g., self.vitals.triad → holon="vitals", rest=["triad"]
        """
        match holon:
            case "memory":
                return self._memory or MemoryNode()
            case "capabilities":
                return self._capabilities or CapabilitiesNode()
            case "state":
                return self._state or StateNode()
            case "identity":
                return self._identity or IdentityNode()
            case "judgment":
                return self._judgment or JudgmentNode()
            case "semaphore":
                return self._semaphore or SemaphoreNode()
            case "vitals":
                # Delegate to vitals resolver
                if self._vitals_resolver is None:
                    self._vitals_resolver = create_vitals_resolver()
                if rest:
                    # self.vitals.triad → VitalsContextResolver.resolve("triad", [])
                    return self._vitals_resolver.resolve(rest[0], rest[1:])
                # self.vitals → Return triad health as default
                return self._vitals_resolver.resolve("triad", [])
            case _:
                # Generic self node for undefined holons
                return GenericSelfNode(holon)


# === Generic Self Node ===


@dataclass
class GenericSelfNode(BaseLogosNode):
    """Fallback node for undefined self.* paths."""

    holon: str
    _handle: str = ""

    def __post_init__(self) -> None:
        self._handle = f"self.{self.holon}"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("inspect",)

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        return BasicRendering(
            summary=f"Self: {self.holon}",
            content=f"Generic self node for {self.holon}",
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        return {"holon": self.holon, "aspect": aspect, "kwargs": kwargs}


# === Factory Functions ===


def create_self_resolver(
    d_gent: Any = None,
    n_gent: Any = None,
    purgatory: Any = None,
    crystallization_engine: Any = None,
    ghost_path: Path | None = None,
    # Four Pillars integration (Phase 6)
    memory_crystal: Any = None,
    pheromone_field: Any = None,
    inference_agent: Any = None,
    language_games: dict[str, Any] | None = None,
) -> SelfContextResolver:
    """
    Create a SelfContextResolver with optional integrations.

    Args:
        d_gent: D-gent for persistence
        n_gent: N-gent for tracing
        purgatory: Purgatory for semaphore integration
        crystallization_engine: CrystallizationEngine for crystal operations
        ghost_path: Path for Ghost cache (defaults to ~/.kgents/ghost)
        memory_crystal: MemoryCrystal for Four Pillars holographic memory
        pheromone_field: PheromoneField for stigmergic coordination
        inference_agent: ActiveInferenceAgent for free energy-based retention
        language_games: Dict of language games for Wittgensteinian access

    Returns:
        Configured SelfContextResolver
    """
    resolver = SelfContextResolver()
    resolver._d_gent = d_gent
    resolver._n_gent = n_gent
    resolver._purgatory = purgatory
    resolver._crystallization_engine = crystallization_engine
    resolver._ghost_path = ghost_path
    # Four Pillars
    resolver._memory_crystal = memory_crystal
    resolver._pheromone_field = pheromone_field
    resolver._inference_agent = inference_agent
    resolver._language_games = language_games or {}
    resolver.__post_init__()  # Reinitialize with integrations
    return resolver
