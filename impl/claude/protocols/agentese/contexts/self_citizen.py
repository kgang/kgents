"""
AGENTESE Self Citizen Context

Citizen memory nodes for self.citizen.<name>.* paths:
- CitizenMemoryNode: Access persistent citizen memory
- Chat with citizens who remember past conversations

Phase 3 Crown Jewels: Living Town with persistent citizen memory.

AGENTESE paths:
- self.citizen.<name>.memory.recall[query="..."]
- self.citizen.<name>.memory.conversations[limit=10]
- self.citizen.<name>.memory.store[key="...", content="..."]
- self.citizen.<name>.personality.manifest
- self.citizen.<name>.chat[message="..."]
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Citizen Affordances ===

CITIZEN_MEMORY_AFFORDANCES: tuple[str, ...] = (
    "recall",  # Recall memories by key or content
    "conversations",  # Get recent conversations
    "store",  # Store new memory
    "search",  # Search conversations
    "summary",  # Get memory summary
)

CITIZEN_PERSONALITY_AFFORDANCES: tuple[str, ...] = (
    "manifest",  # Show eigenvectors and cosmotechnics
    "drift",  # Show eigenvector drift over time
)

CITIZEN_AFFORDANCES: tuple[str, ...] = (
    "manifest",  # Show citizen overview
    "chat",  # Chat with citizen (LLM-powered)
    "memory",  # Access citizen's memory
    "personality",  # Access citizen's personality
)


# === Citizen Memory Node ===


@dataclass
class CitizenMemoryNode(BaseLogosNode):
    """
    self.citizen.<name>.memory - Citizen's persistent memory.

    Phase 3 Crown Jewels: Living Town with persistent memory.

    Provides access to:
    - Conversation history with Kent
    - Graph memory (episodic memories)
    - Memory search and recall

    AGENTESE: self.citizen.<name>.memory.*
    """

    _handle: str = "self.citizen"
    _citizen_name: str = ""
    _citizen_id: str = ""

    @property
    def handle(self) -> str:
        if self._citizen_name:
            return f"self.citizen.{self._citizen_name.lower()}.memory"
        return f"{self._handle}.memory"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Memory affordances available to all archetypes."""
        return CITIZEN_MEMORY_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show citizen memory summary."""
        memory = await self._get_persistent_memory()
        if memory is None:
            return BasicRendering(
                summary=f"No memory for {self._citizen_name}",
                content="Citizen not found or memory not loaded",
                metadata={"citizen_name": self._citizen_name},
            )

        summary = memory.memory_summary()
        return BasicRendering(
            summary=f"{self._citizen_name}'s Memory",
            content=(
                f"Graph memories: {summary['graph_memory_size']}\n"
                f"Conversations: {summary['conversation_count']}\n"
                f"Recent topics: {', '.join(summary['recent_topics']) or 'None'}"
            ),
            metadata=summary,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle memory-specific aspects."""
        match aspect:
            case "recall":
                return await self._recall(observer, **kwargs)
            case "conversations":
                return await self._conversations(observer, **kwargs)
            case "store":
                return await self._store(observer, **kwargs)
            case "search":
                return await self._search(observer, **kwargs)
            case "summary":
                return await self._summary(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _get_persistent_memory(self) -> Any:
        """Get persistent memory for this citizen."""
        try:
            from protocols.cli.handlers.town import (
                _persistent_memories,
                _simulation_state,
            )

            if self._citizen_id and self._citizen_id in _persistent_memories:
                return _persistent_memories[self._citizen_id]

            # Try to find by name
            if "environment" in _simulation_state and self._citizen_name:
                env = _simulation_state["environment"]
                citizen = env.get_citizen_by_name(self._citizen_name)
                if citizen and citizen.id in _persistent_memories:
                    self._citizen_id = citizen.id
                    return _persistent_memories[citizen.id]

            return None
        except ImportError:
            return None

    async def _recall(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Recall memories by key or content search."""
        memory = await self._get_persistent_memory()
        if memory is None:
            return {"error": "Memory not loaded", "citizen": self._citizen_name}

        key = kwargs.get("key")
        query = kwargs.get("query")
        k_hops = kwargs.get("k_hops", 2)

        if key:
            results = await memory.recall_memory(key, k_hops)
            return {
                "citizen": self._citizen_name,
                "key": key,
                "results": results,
                "count": len(results),
            }

        if query:
            results = await memory.recall_by_content(query, k_hops)
            return {
                "citizen": self._citizen_name,
                "query": query,
                "results": results,
                "count": len(results),
            }

        return {"error": "key or query required"}

    async def _conversations(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get recent conversations."""
        memory = await self._get_persistent_memory()
        if memory is None:
            return {"error": "Memory not loaded", "citizen": self._citizen_name}

        limit = kwargs.get("limit", 10)
        topic = kwargs.get("topic")

        convs = await memory.get_recent_conversations(limit=limit, topic=topic)
        return {
            "citizen": self._citizen_name,
            "conversations": [c.to_dict() for c in convs],
            "count": len(convs),
        }

    async def _store(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Store a new memory."""
        memory = await self._get_persistent_memory()
        if memory is None:
            return {"error": "Memory not loaded", "citizen": self._citizen_name}

        key = kwargs.get("key")
        content = kwargs.get("content")

        if not key or not content:
            return {"error": "key and content required"}

        connections = kwargs.get("connections", {})
        metadata = kwargs.get("metadata", {})

        await memory.store_memory(key, content, connections, metadata)
        return {
            "status": "stored",
            "citizen": self._citizen_name,
            "key": key,
        }

    async def _search(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Search conversations by content."""
        memory = await self._get_persistent_memory()
        if memory is None:
            return {"error": "Memory not loaded", "citizen": self._citizen_name}

        query = kwargs.get("query")
        if not query:
            return {"error": "query required"}

        results = await memory.search_conversations(query)
        return {
            "citizen": self._citizen_name,
            "query": query,
            "results": [c.to_dict() for c in results],
            "count": len(results),
        }

    async def _summary(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get memory summary."""
        memory = await self._get_persistent_memory()
        if memory is None:
            return {"error": "Memory not loaded", "citizen": self._citizen_name}

        return memory.memory_summary()


# === Citizen Personality Node ===


@dataclass
class CitizenPersonalityNode(BaseLogosNode):
    """
    self.citizen.<name>.personality - Citizen's eigenvector personality.

    AGENTESE: self.citizen.<name>.personality.*
    """

    _handle: str = "self.citizen"
    _citizen_name: str = ""

    @property
    def handle(self) -> str:
        if self._citizen_name:
            return f"self.citizen.{self._citizen_name.lower()}.personality"
        return f"{self._handle}.personality"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Personality affordances."""
        return CITIZEN_PERSONALITY_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show citizen personality (eigenvectors + cosmotechnics)."""
        citizen = await self._get_citizen()
        if citizen is None:
            return BasicRendering(
                summary=f"Unknown citizen: {self._citizen_name}",
                content="Citizen not found in simulation",
                metadata={"citizen_name": self._citizen_name},
            )

        ev = citizen.eigenvectors.to_dict()
        cosmo = citizen.cosmotechnics

        content_lines = [
            f"Archetype: {citizen.archetype}",
            f"Cosmotechnics: {cosmo.name}",
            f'Metaphor: "{cosmo.metaphor}"',
            "",
            "Eigenvectors:",
        ]
        for key, val in ev.items():
            bar = "▓" * int(val * 10) + "░" * (10 - int(val * 10))
            content_lines.append(f"  {key}: {bar} {val:.2f}")

        return BasicRendering(
            summary=f"{self._citizen_name}'s Personality",
            content="\n".join(content_lines),
            metadata={
                "eigenvectors": ev,
                "archetype": citizen.archetype,
                "cosmotechnics": cosmo.name,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle personality aspects."""
        match aspect:
            case "drift":
                return await self._drift(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _get_citizen(self) -> Any:
        """Get the citizen from simulation state."""
        try:
            from protocols.cli.handlers.town import _simulation_state

            if "environment" in _simulation_state and self._citizen_name:
                env = _simulation_state["environment"]
                return env.get_citizen_by_name(self._citizen_name)
            return None
        except ImportError:
            return None

    async def _drift(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get eigenvector drift over time."""
        try:
            from protocols.cli.handlers.town import _persistent_memories

            citizen = await self._get_citizen()
            if citizen is None:
                return {"error": "Citizen not found"}

            if citizen.id not in _persistent_memories:
                return {"error": "No persistent memory for citizen"}

            memory = _persistent_memories[citizen.id]
            window_size = kwargs.get("window_size", 10)
            drift = await memory.get_eigenvector_drift(window_size)

            if drift is None:
                return {
                    "citizen": self._citizen_name,
                    "drift": None,
                    "note": "Insufficient history",
                }

            return {
                "citizen": self._citizen_name,
                "drift": drift,
                "window_size": window_size,
            }
        except ImportError:
            return {"error": "Town module not available"}


# === Citizen Node (Main Entry Point) ===


@dataclass
class CitizenNode(BaseLogosNode):
    """
    self.citizen.<name> - Access a specific citizen.

    AGENTESE: self.citizen.<name>.*

    Sub-nodes:
    - self.citizen.<name>.memory.* - Memory operations
    - self.citizen.<name>.personality.* - Eigenvector personality
    - self.citizen.<name>.chat[message="..."] - LLM-powered chat
    """

    _handle: str = "self.citizen"
    _citizen_name: str = ""
    _memory_node: CitizenMemoryNode | None = None
    _personality_node: CitizenPersonalityNode | None = None

    @property
    def handle(self) -> str:
        if self._citizen_name:
            return f"self.citizen.{self._citizen_name.lower()}"
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Citizen affordances."""
        return CITIZEN_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show citizen overview."""
        citizen = await self._get_citizen()
        if citizen is None:
            return BasicRendering(
                summary=f"Unknown citizen: {self._citizen_name}",
                content="Citizen not found in simulation",
                metadata={"citizen_name": self._citizen_name},
            )

        manifest = citizen.manifest(lod=3)
        ev = manifest.get("eigenvectors", {})
        rels = manifest.get("relationships", {})

        content_lines = [
            f"Name: {manifest['name']}",
            f"Archetype: {manifest.get('archetype', 'unknown')}",
            f"Cosmotechnics: {manifest.get('cosmotechnics', 'unknown')}",
            f'Metaphor: "{manifest.get("metaphor", "")}"',
            f"Region: {manifest.get('region', 'unknown')}",
            f"Phase: {manifest.get('phase', 'IDLE')}",
        ]

        if ev:
            content_lines.append("\nEigenvectors:")
            for key, val in ev.items():
                content_lines.append(f"  {key}: {val:.2f}")

        if rels:
            content_lines.append(f"\nRelationships: {len(rels)}")

        return BasicRendering(
            summary=f"Citizen: {self._citizen_name}",
            content="\n".join(content_lines),
            metadata=manifest,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle citizen aspects."""
        match aspect:
            case "chat":
                return await self._chat(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _get_citizen(self) -> Any:
        """Get the citizen from simulation state."""
        try:
            from protocols.cli.handlers.town import _simulation_state

            if "environment" in _simulation_state and self._citizen_name:
                env = _simulation_state["environment"]
                return env.get_citizen_by_name(self._citizen_name)
            return None
        except ImportError:
            return None

    async def _chat(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Chat with the citizen using LLM.

        AGENTESE: self.citizen.<name>.chat[message="Hello!"]
        """
        message = kwargs.get("message")
        if not message:
            return {"error": "message required"}

        citizen = await self._get_citizen()
        if citizen is None:
            return {"error": f"Citizen '{self._citizen_name}' not found"}

        try:
            from protocols.cli.handlers.town import (
                _generate_citizen_response,
                _get_or_create_memory,
                _infer_topic,
            )

            # Get or create persistent memory
            memory = await _get_or_create_memory(citizen)

            # Store Kent's message
            await memory.add_conversation(
                speaker="kent",
                message=message,
                topic=_infer_topic(message),
            )

            # Generate response (uses LLM)
            response = _generate_citizen_response(citizen, message, memory)

            # Store citizen's response
            await memory.add_conversation(
                speaker=self._citizen_name.lower(),
                message=response,
                topic=_infer_topic(message),
            )

            return {
                "citizen": self._citizen_name,
                "message": message,
                "response": response,
            }
        except ImportError as e:
            return {"error": f"Town module not available: {e}"}


# === Factory Functions ===


def create_citizen_node(citizen_name: str) -> CitizenNode:
    """Create a citizen node for a specific citizen."""
    memory_node = CitizenMemoryNode(_citizen_name=citizen_name)
    personality_node = CitizenPersonalityNode(_citizen_name=citizen_name)

    return CitizenNode(
        _citizen_name=citizen_name,
        _memory_node=memory_node,
        _personality_node=personality_node,
    )


def create_citizen_memory_node(citizen_name: str) -> CitizenMemoryNode:
    """Create a citizen memory node."""
    return CitizenMemoryNode(_citizen_name=citizen_name)


def create_citizen_personality_node(citizen_name: str) -> CitizenPersonalityNode:
    """Create a citizen personality node."""
    return CitizenPersonalityNode(_citizen_name=citizen_name)


# === Exports ===

__all__ = [
    "CITIZEN_AFFORDANCES",
    "CITIZEN_MEMORY_AFFORDANCES",
    "CITIZEN_PERSONALITY_AFFORDANCES",
    "CitizenNode",
    "CitizenMemoryNode",
    "CitizenPersonalityNode",
    "create_citizen_node",
    "create_citizen_memory_node",
    "create_citizen_personality_node",
]
