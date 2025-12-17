"""
Persistent Memory for Agent Town Citizens.

Uses D-gent for persistence. Citizens remember conversations, relationships,
and experiences across restarts.

Phase 3 Crown Jewels: Living Town with persistent citizen memory.

Architecture:
    - Each citizen has a namespace: "citizen:{citizen_id}:memory"
    - Memories stored as Datum with content = JSON-serialized GraphMemory
    - Conversation history stored as Datum with content = JSON-serialized list
    - Relationship snapshots stored periodically

Use patterns from V-gent (DgentVectorBackend) for the D-gent integration.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from agents.d import Datum, DgentProtocol, DgentRouter
from agents.town.memory import GraphMemory

if TYPE_CHECKING:
    from agents.town.citizen import Citizen


# =============================================================================
# ConversationEntry: A single conversation turn with Kent
# =============================================================================


@dataclass
class ConversationEntry:
    """
    A single conversation turn.

    Stores both what was said and the emotional/relational context.
    """

    timestamp: str
    speaker: str  # "kent" or citizen name
    message: str
    topic: str | None = None
    emotion: str | None = None  # inferred from context
    eigenvector_deltas: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "timestamp": self.timestamp,
            "speaker": self.speaker,
            "message": self.message,
            "topic": self.topic,
            "emotion": self.emotion,
            "eigenvector_deltas": self.eigenvector_deltas,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConversationEntry:
        """Deserialize from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            speaker=data["speaker"],
            message=data["message"],
            topic=data.get("topic"),
            emotion=data.get("emotion"),
            eigenvector_deltas=data.get("eigenvector_deltas", {}),
        )


# =============================================================================
# PersistentCitizenMemory: D-gent backed memory for citizens
# =============================================================================


class PersistentCitizenMemory:
    """
    Persistent memory for a citizen using D-gent.

    Stores:
    - Graph memory (episodic memories with connections)
    - Conversation history (with Kent)
    - Relationship snapshots (with other citizens)

    Architecture:
        - Namespace: "citizen:{citizen_id}:*"
        - Memory IDs:
            - "citizen:{id}:graph" - serialized GraphMemory
            - "citizen:{id}:conversations" - conversation history
            - "citizen:{id}:relationships" - relationship weights
            - "citizen:{id}:eigenvectors" - eigenvector history
    """

    def __init__(
        self,
        citizen_id: str,
        dgent: DgentProtocol | None = None,
    ) -> None:
        """
        Initialize persistent memory for a citizen.

        Args:
            citizen_id: Unique identifier for the citizen
            dgent: D-gent backend (auto-creates DgentRouter if None)
        """
        self._citizen_id = citizen_id
        self._dgent = dgent or DgentRouter()
        self._namespace = f"citizen:{citizen_id}"

        # In-memory caches (loaded from D-gent on startup)
        self._graph_memory: GraphMemory | None = None
        self._conversations: list[ConversationEntry] = []
        self._loaded = False

    @property
    def citizen_id(self) -> str:
        """The citizen this memory belongs to."""
        return self._citizen_id

    @property
    def namespace(self) -> str:
        """D-gent namespace prefix."""
        return self._namespace

    # =========================================================================
    # Initialization
    # =========================================================================

    async def load(self) -> None:
        """
        Load memory from D-gent on startup.

        Call this after creating the memory to restore persisted state.
        """
        # Load graph memory
        graph_datum = await self._dgent.get(f"{self._namespace}:graph")
        if graph_datum:
            try:
                data = json.loads(graph_datum.content.decode("utf-8"))
                self._graph_memory = GraphMemory.from_dict(data)
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._graph_memory = GraphMemory()
        else:
            self._graph_memory = GraphMemory()

        # Load conversations
        conv_datum = await self._dgent.get(f"{self._namespace}:conversations")
        if conv_datum:
            try:
                data = json.loads(conv_datum.content.decode("utf-8"))
                self._conversations = [ConversationEntry.from_dict(e) for e in data]
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._conversations = []
        else:
            self._conversations = []

        self._loaded = True

    async def save(self) -> None:
        """
        Persist current memory state to D-gent.

        Call this after significant changes to ensure persistence.
        """
        # Save graph memory
        if self._graph_memory:
            graph_data = json.dumps(self._graph_memory.to_dict()).encode("utf-8")
            datum = Datum.create(
                content=graph_data,
                id=f"{self._namespace}:graph",
                metadata={"citizen_id": self._citizen_id, "type": "graph_memory"},
            )
            await self._dgent.put(datum)

        # Save conversations
        conv_data = json.dumps([c.to_dict() for c in self._conversations]).encode(
            "utf-8"
        )
        datum = Datum.create(
            content=conv_data,
            id=f"{self._namespace}:conversations",
            metadata={"citizen_id": self._citizen_id, "type": "conversations"},
        )
        await self._dgent.put(datum)

    # =========================================================================
    # Graph Memory Operations
    # =========================================================================

    @property
    def graph(self) -> GraphMemory:
        """Access the graph memory (lazy initialization)."""
        if self._graph_memory is None:
            self._graph_memory = GraphMemory()
        return self._graph_memory

    async def store_memory(
        self,
        key: str,
        content: str,
        connections: dict[str, float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Store an episodic memory.

        Args:
            key: Unique identifier for this memory
            content: The memory content
            connections: Optional connections to related memories
            metadata: Optional metadata
        """
        self.graph.store(key, content, connections, metadata)
        await self.save()

    async def recall_memory(self, query: str, k_hops: int = 2) -> list[dict[str, Any]]:
        """
        Recall memories by graph traversal.

        Args:
            query: Memory ID to start from
            k_hops: How many connection hops to traverse

        Returns:
            List of memory dictionaries
        """
        result = self.graph.recall(query, k_hops)
        return [
            {
                "id": node.id,
                "content": node.content,
                "strength": node.strength,
                "connections": list(node.connections.keys()),
            }
            for node in result.nodes
        ]

    async def recall_by_content(
        self, substring: str, k_hops: int = 2
    ) -> list[dict[str, Any]]:
        """
        Recall memories by content search.

        Args:
            substring: Text to search for
            k_hops: How many connection hops to traverse

        Returns:
            List of memory dictionaries
        """
        results = self.graph.recall_by_content(substring, k_hops)
        memories = []
        for result in results:
            for node in result.nodes:
                memories.append(
                    {
                        "id": node.id,
                        "content": node.content,
                        "strength": node.strength,
                    }
                )
        return memories

    async def reinforce_memory(self, key: str, amount: float = 0.1) -> bool:
        """
        Reinforce a memory (increase strength).

        Args:
            key: Memory ID to reinforce
            amount: How much to increase strength

        Returns:
            True if reinforced, False if not found
        """
        if self.graph.reinforce(key, amount):
            await self.save()
            return True
        return False

    async def decay_memories(self, rate: float | None = None) -> int:
        """
        Apply decay to all memories.

        Args:
            rate: Decay rate (uses default if None)

        Returns:
            Number of memories pruned
        """
        pruned = self.graph.decay(rate)
        if pruned > 0:
            await self.save()
        return pruned

    # =========================================================================
    # Conversation History
    # =========================================================================

    @property
    def conversations(self) -> list[ConversationEntry]:
        """All conversation entries."""
        return self._conversations

    async def add_conversation(
        self,
        speaker: str,
        message: str,
        topic: str | None = None,
        emotion: str | None = None,
        eigenvector_deltas: dict[str, float] | None = None,
    ) -> ConversationEntry:
        """
        Add a conversation entry.

        Args:
            speaker: Who said this ("kent" or citizen name)
            message: What was said
            topic: Optional conversation topic
            emotion: Optional inferred emotion
            eigenvector_deltas: Optional changes to eigenvectors from this message

        Returns:
            The created ConversationEntry
        """
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            speaker=speaker,
            message=message,
            topic=topic,
            emotion=emotion,
            eigenvector_deltas=eigenvector_deltas or {},
        )
        self._conversations.append(entry)
        await self.save()
        return entry

    async def get_recent_conversations(
        self, limit: int = 10, topic: str | None = None
    ) -> list[ConversationEntry]:
        """
        Get recent conversations.

        Args:
            limit: Maximum number to return
            topic: Optional topic filter

        Returns:
            List of recent conversation entries
        """
        filtered = self._conversations
        if topic:
            filtered = [c for c in filtered if c.topic == topic]
        return filtered[-limit:]

    async def search_conversations(self, query: str) -> list[ConversationEntry]:
        """
        Search conversations by content.

        Args:
            query: Text to search for (case-insensitive)

        Returns:
            Matching conversation entries
        """
        query_lower = query.lower()
        return [c for c in self._conversations if query_lower in c.message.lower()]

    # =========================================================================
    # Relationship Persistence
    # =========================================================================

    async def save_relationships(self, relationships: dict[str, float]) -> None:
        """
        Save relationship weights to D-gent.

        Args:
            relationships: Dict of citizen_id -> weight
        """
        data = json.dumps(relationships).encode("utf-8")
        datum = Datum.create(
            content=data,
            id=f"{self._namespace}:relationships",
            metadata={"citizen_id": self._citizen_id, "type": "relationships"},
        )
        await self._dgent.put(datum)

    async def load_relationships(self) -> dict[str, float]:
        """
        Load relationship weights from D-gent.

        Returns:
            Dict of citizen_id -> weight
        """
        datum = await self._dgent.get(f"{self._namespace}:relationships")
        if datum:
            try:
                return json.loads(datum.content.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return {}
        return {}

    # =========================================================================
    # Eigenvector History
    # =========================================================================

    async def save_eigenvectors(self, eigenvectors: dict[str, float]) -> None:
        """
        Save current eigenvector snapshot with timestamp.

        This creates a history of eigenvector evolution over time.

        Args:
            eigenvectors: Current eigenvector values
        """
        # Load existing history
        history = await self._load_eigenvector_history()

        # Add current snapshot
        history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "values": eigenvectors,
            }
        )

        # Keep last 100 snapshots
        history = history[-100:]

        # Save
        data = json.dumps(history).encode("utf-8")
        datum = Datum.create(
            content=data,
            id=f"{self._namespace}:eigenvectors",
            metadata={"citizen_id": self._citizen_id, "type": "eigenvector_history"},
        )
        await self._dgent.put(datum)

    async def _load_eigenvector_history(self) -> list[dict[str, Any]]:
        """Load eigenvector history from D-gent."""
        datum = await self._dgent.get(f"{self._namespace}:eigenvectors")
        if datum:
            try:
                return json.loads(datum.content.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return []
        return []

    async def get_eigenvector_drift(
        self, window_size: int = 10
    ) -> dict[str, float] | None:
        """
        Calculate eigenvector drift over recent history.

        Args:
            window_size: Number of snapshots to compare

        Returns:
            Dict of dimension -> drift amount, or None if insufficient history
        """
        history = await self._load_eigenvector_history()
        if len(history) < 2:
            return None

        # Compare most recent to window_size ago
        recent = history[-1]["values"]
        past_idx = max(0, len(history) - window_size)
        past = history[past_idx]["values"]

        drift = {}
        for key in recent:
            if key in past:
                drift[key] = recent[key] - past[key]

        return drift

    # =========================================================================
    # Utility
    # =========================================================================

    async def clear(self) -> None:
        """Clear all memory (graph, conversations, relationships)."""
        self._graph_memory = GraphMemory()
        self._conversations = []

        # Delete from D-gent
        await self._dgent.delete(f"{self._namespace}:graph")
        await self._dgent.delete(f"{self._namespace}:conversations")
        await self._dgent.delete(f"{self._namespace}:relationships")
        await self._dgent.delete(f"{self._namespace}:eigenvectors")

    def memory_summary(self) -> dict[str, Any]:
        """
        Get a summary of this citizen's memory.

        Returns:
            Summary dict with counts and recent activity
        """
        return {
            "citizen_id": self._citizen_id,
            "graph_memory_size": len(self.graph) if self._graph_memory else 0,
            "conversation_count": len(self._conversations),
            "recent_topics": list(
                {c.topic for c in self._conversations[-10:] if c.topic is not None}
            ),
            "loaded": self._loaded,
        }


# =============================================================================
# Factory Functions
# =============================================================================


async def create_persistent_memory(
    citizen: "Citizen",
    dgent: DgentProtocol | None = None,
) -> PersistentCitizenMemory:
    """
    Create and load persistent memory for a citizen.

    This is the recommended way to create memory - it handles
    initialization and loading from D-gent.

    Args:
        citizen: The citizen to create memory for
        dgent: Optional D-gent backend (auto-creates if None)

    Returns:
        Loaded PersistentCitizenMemory instance
    """
    memory = PersistentCitizenMemory(citizen.id, dgent)
    await memory.load()

    # Also load and restore relationships
    relationships = await memory.load_relationships()
    if relationships:
        citizen.relationships = relationships

    return memory


async def save_citizen_state(
    citizen: "Citizen",
    memory: PersistentCitizenMemory,
) -> None:
    """
    Save a citizen's full state to persistent memory.

    Args:
        citizen: The citizen to save
        memory: The citizen's persistent memory
    """
    # Save relationships
    await memory.save_relationships(citizen.relationships)

    # Save eigenvector snapshot
    await memory.save_eigenvectors(citizen.eigenvectors.to_dict())

    # Graph memory and conversations are auto-saved on update


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "ConversationEntry",
    "PersistentCitizenMemory",
    "create_persistent_memory",
    "save_citizen_state",
]
