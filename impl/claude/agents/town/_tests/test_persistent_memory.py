"""
Tests for Persistent Citizen Memory.

Phase 3 Crown Jewels: Living Town with persistent citizen memory.
"""

import pytest
from agents.d import MemoryBackend
from agents.town.citizen import GATHERING, Citizen, Eigenvectors
from agents.town.memory import GraphMemory
from agents.town.persistent_memory import (
    ConversationEntry,
    PersistentCitizenMemory,
    create_persistent_memory,
    save_citizen_state,
)


@pytest.fixture
def dgent() -> MemoryBackend:
    """Create in-memory D-gent backend for testing."""
    return MemoryBackend()


@pytest.fixture
def citizen() -> Citizen:
    """Create a test citizen."""
    return Citizen(
        name="Alice",
        archetype="Scholar",
        region="library",
        eigenvectors=Eigenvectors(
            warmth=0.7,
            curiosity=0.9,
            trust=0.6,
            creativity=0.5,
            patience=0.8,
            resilience=0.5,
            ambition=0.4,
        ),
        cosmotechnics=GATHERING,
    )


class TestConversationEntry:
    """Tests for ConversationEntry dataclass."""

    def test_create_entry(self) -> None:
        """Test creating a conversation entry."""
        entry = ConversationEntry(
            timestamp="2025-01-01T12:00:00",
            speaker="kent",
            message="Hello Alice!",
            topic="greeting",
            emotion="happy",
        )

        assert entry.speaker == "kent"
        assert entry.message == "Hello Alice!"
        assert entry.topic == "greeting"

    def test_serialization(self) -> None:
        """Test entry serialization round-trip."""
        entry = ConversationEntry(
            timestamp="2025-01-01T12:00:00",
            speaker="alice",
            message="Hi there!",
            eigenvector_deltas={"warmth": 0.05},
        )

        data = entry.to_dict()
        restored = ConversationEntry.from_dict(data)

        assert restored.speaker == entry.speaker
        assert restored.message == entry.message
        assert restored.eigenvector_deltas == entry.eigenvector_deltas


class TestPersistentCitizenMemory:
    """Tests for PersistentCitizenMemory."""

    @pytest.mark.asyncio
    async def test_create_memory(self, dgent: MemoryBackend) -> None:
        """Test creating persistent memory."""
        memory = PersistentCitizenMemory("test_citizen", dgent)
        await memory.load()

        assert memory.citizen_id == "test_citizen"
        assert memory.namespace == "citizen:test_citizen"

    @pytest.mark.asyncio
    async def test_store_and_recall_memory(self, dgent: MemoryBackend) -> None:
        """Test storing and recalling graph memories."""
        memory = PersistentCitizenMemory("test_citizen", dgent)
        await memory.load()

        # Store a memory
        await memory.store_memory(
            key="memory_1",
            content="Met Kent at the library today",
            metadata={"type": "encounter"},
        )

        # Recall it
        results = await memory.recall_memory("memory_1")
        assert len(results) == 1
        assert "Kent" in results[0]["content"]

    @pytest.mark.asyncio
    async def test_conversation_history(self, dgent: MemoryBackend) -> None:
        """Test conversation storage and retrieval."""
        memory = PersistentCitizenMemory("test_citizen", dgent)
        await memory.load()

        # Add conversations
        await memory.add_conversation(
            speaker="kent",
            message="Hello!",
            topic="greeting",
        )
        await memory.add_conversation(
            speaker="alice",
            message="Hi Kent!",
            topic="greeting",
        )

        # Retrieve recent
        recent = await memory.get_recent_conversations(limit=5)
        assert len(recent) == 2
        assert recent[0].speaker == "kent"
        assert recent[1].speaker == "alice"

    @pytest.mark.asyncio
    async def test_conversation_search(self, dgent: MemoryBackend) -> None:
        """Test searching conversations."""
        memory = PersistentCitizenMemory("test_citizen", dgent)
        await memory.load()

        await memory.add_conversation(
            speaker="kent",
            message="What do you think about category theory?",
            topic="philosophy",
        )
        await memory.add_conversation(
            speaker="alice",
            message="I find it fascinating, especially functors!",
            topic="philosophy",
        )

        # Search
        results = await memory.search_conversations("functor")
        assert len(results) == 1
        assert "functors" in results[0].message

    @pytest.mark.asyncio
    async def test_persistence_across_reload(self, dgent: MemoryBackend) -> None:
        """Test that memory persists across reload."""
        # Create and populate
        memory1 = PersistentCitizenMemory("persist_test", dgent)
        await memory1.load()
        await memory1.add_conversation(
            speaker="kent",
            message="Remember this!",
            topic="test",
        )
        await memory1.save()

        # Create new instance
        memory2 = PersistentCitizenMemory("persist_test", dgent)
        await memory2.load()

        # Should have the conversation
        recent = await memory2.get_recent_conversations()
        assert len(recent) == 1
        assert recent[0].message == "Remember this!"

    @pytest.mark.asyncio
    async def test_relationship_persistence(self, dgent: MemoryBackend) -> None:
        """Test relationship weight persistence."""
        memory = PersistentCitizenMemory("rel_test", dgent)
        await memory.load()

        # Save relationships
        relationships = {"citizen_a": 0.5, "citizen_b": -0.2}
        await memory.save_relationships(relationships)

        # Load them back
        loaded = await memory.load_relationships()
        assert loaded == relationships

    @pytest.mark.asyncio
    async def test_eigenvector_history(self, dgent: MemoryBackend) -> None:
        """Test eigenvector history tracking."""
        memory = PersistentCitizenMemory("ev_test", dgent)
        await memory.load()

        # Save snapshots
        await memory.save_eigenvectors({"warmth": 0.5, "curiosity": 0.6})
        await memory.save_eigenvectors({"warmth": 0.6, "curiosity": 0.7})

        # Get drift
        drift = await memory.get_eigenvector_drift(window_size=10)
        assert drift is not None
        assert drift["warmth"] == pytest.approx(0.1, abs=0.01)
        assert drift["curiosity"] == pytest.approx(0.1, abs=0.01)

    @pytest.mark.asyncio
    async def test_memory_summary(self, dgent: MemoryBackend) -> None:
        """Test memory summary."""
        memory = PersistentCitizenMemory("summary_test", dgent)
        await memory.load()

        await memory.store_memory("m1", "Memory one")
        await memory.store_memory("m2", "Memory two")
        await memory.add_conversation("kent", "Hello", "greeting")

        summary = memory.memory_summary()
        assert summary["citizen_id"] == "summary_test"
        assert summary["graph_memory_size"] == 2
        assert summary["conversation_count"] == 1
        assert "greeting" in summary["recent_topics"]

    @pytest.mark.asyncio
    async def test_clear_memory(self, dgent: MemoryBackend) -> None:
        """Test clearing all memory."""
        memory = PersistentCitizenMemory("clear_test", dgent)
        await memory.load()

        await memory.store_memory("m1", "Memory")
        await memory.add_conversation("kent", "Hello")

        await memory.clear()

        summary = memory.memory_summary()
        assert summary["graph_memory_size"] == 0
        assert summary["conversation_count"] == 0


class TestCreatePersistentMemory:
    """Tests for factory function."""

    @pytest.mark.asyncio
    async def test_create_for_citizen(
        self, citizen: Citizen, dgent: MemoryBackend
    ) -> None:
        """Test creating memory for a citizen."""
        memory = await create_persistent_memory(citizen, dgent)

        assert memory.citizen_id == citizen.id
        assert memory._loaded is True


class TestSaveCitizenState:
    """Tests for state saving."""

    @pytest.mark.asyncio
    async def test_save_state(self, citizen: Citizen, dgent: MemoryBackend) -> None:
        """Test saving citizen state."""
        memory = await create_persistent_memory(citizen, dgent)

        # Add relationship
        citizen.relationships["other_citizen"] = 0.3

        # Save
        await save_citizen_state(citizen, memory)

        # Verify relationships saved
        loaded = await memory.load_relationships()
        assert loaded.get("other_citizen") == pytest.approx(0.3)


class TestGraphMemoryIntegration:
    """Tests for GraphMemory integration."""

    @pytest.mark.asyncio
    async def test_graph_memory_connections(self, dgent: MemoryBackend) -> None:
        """Test graph memory with connections."""
        memory = PersistentCitizenMemory("graph_test", dgent)
        await memory.load()

        # Store connected memories
        await memory.store_memory("root", "Root memory")
        await memory.store_memory(
            "child",
            "Connected to root",
            connections={"root": 0.8},
        )

        # Recall with k-hops
        results = await memory.recall_memory("root", k_hops=1)
        assert len(results) == 2  # root + connected child

    @pytest.mark.asyncio
    async def test_memory_reinforcement(self, dgent: MemoryBackend) -> None:
        """Test memory reinforcement."""
        memory = PersistentCitizenMemory("reinforce_test", dgent)
        await memory.load()

        await memory.store_memory("m1", "A memory")

        # First decay to lower strength
        await memory.decay_memories(rate=0.3)

        # Now reinforce
        result = await memory.reinforce_memory("m1", 0.2)
        assert result is True

        # Check strength increased from decayed value (0.7 + 0.2 = 0.9)
        node = memory.graph.get("m1")
        assert node is not None
        assert node.strength == pytest.approx(0.9, abs=0.01)

    @pytest.mark.asyncio
    async def test_memory_decay(self, dgent: MemoryBackend) -> None:
        """Test memory decay."""
        memory = PersistentCitizenMemory("decay_test", dgent)
        await memory.load()

        await memory.store_memory("m1", "A memory")

        # Decay
        pruned = await memory.decay_memories(rate=0.5)

        # Check strength decreased
        node = memory.graph.get("m1")
        assert node is not None
        assert node.strength < 1.0

    @pytest.mark.asyncio
    async def test_content_search(self, dgent: MemoryBackend) -> None:
        """Test searching by content."""
        memory = PersistentCitizenMemory("search_test", dgent)
        await memory.load()

        await memory.store_memory("m1", "Kent discussed category theory")
        await memory.store_memory("m2", "Weather was nice")
        await memory.store_memory("m3", "More category thoughts")

        results = await memory.recall_by_content("category")
        assert len(results) >= 2  # At least m1 and m3
