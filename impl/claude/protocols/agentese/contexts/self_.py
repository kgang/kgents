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


# === Self Affordances ===

SELF_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "memory": ("consolidate", "prune", "checkpoint", "recall", "forget"),
    "capabilities": ("list", "acquire", "release"),
    "state": ("checkpoint", "restore", "inspect"),
    "identity": ("reflect", "evolve"),
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
    """

    _handle: str = "self.memory"

    # Memory state (D-gent Lens in full implementation)
    _memories: dict[str, Any] = field(default_factory=dict)
    _checkpoints: list[dict[str, Any]] = field(default_factory=list)

    # Integration points
    _d_gent: Any = None  # D-gent for persistence
    _n_gent: Any = None  # N-gent for tracing

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
    internal state, memory, capabilities, and identity.
    """

    # D-gent integration for persistence
    _d_gent: Any = None
    # N-gent integration for tracing
    _n_gent: Any = None

    # Singleton nodes for self context
    _memory: MemoryNode | None = None
    _capabilities: CapabilitiesNode | None = None
    _state: StateNode | None = None
    _identity: IdentityNode | None = None

    def __post_init__(self) -> None:
        """Initialize singleton nodes."""
        self._memory = MemoryNode(_d_gent=self._d_gent, _n_gent=self._n_gent)
        self._capabilities = CapabilitiesNode()
        self._state = StateNode()
        self._identity = IdentityNode()

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode:
        """
        Resolve a self.* path to a node.

        Args:
            holon: The self subsystem (memory, capabilities, state, identity)
            rest: Additional path components

        Returns:
            Resolved node
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
) -> SelfContextResolver:
    """Create a SelfContextResolver with optional integrations."""
    resolver = SelfContextResolver()
    resolver._d_gent = d_gent
    resolver._n_gent = n_gent
    resolver.__post_init__()  # Reinitialize with integrations
    return resolver
