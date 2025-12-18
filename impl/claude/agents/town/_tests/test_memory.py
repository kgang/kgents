"""
Tests for GraphMemory in Agent Town.

Tests k-hop retrieval, decay, reinforcement, and serialization.
"""

from datetime import datetime, timedelta

import pytest

from agents.town.memory import (
    ConnectionKind,
    GraphMemory,
    MemoryNode,
    RecallResult,
)


class TestMemoryNode:
    """Tests for MemoryNode dataclass."""

    def test_memory_node_creation(self) -> None:
        """Test basic node creation."""
        node = MemoryNode(id="test", content="Test memory")
        assert node.id == "test"
        assert node.content == "Test memory"
        assert node.strength == 1.0
        assert node.connections == {}

    def test_memory_node_strength_clamping(self) -> None:
        """Test that strength is clamped to [0, 1]."""
        node_over = MemoryNode(id="over", content="test", strength=1.5)
        assert node_over.strength == 1.0

        node_under = MemoryNode(id="under", content="test", strength=-0.5)
        assert node_under.strength == 0.0

    def test_memory_node_with_connections(self) -> None:
        """Test node with connections."""
        node = MemoryNode(
            id="test",
            content="Test",
            connections={"other": 0.8, "another": 0.5},
        )
        assert node.connections["other"] == 0.8
        assert node.connections["another"] == 0.5


class TestGraphMemory:
    """Tests for GraphMemory class."""

    def test_empty_memory(self) -> None:
        """Test empty memory initialization."""
        memory = GraphMemory()
        assert memory.size == 0
        assert len(memory) == 0

    def test_store_memory(self) -> None:
        """Test storing a memory."""
        memory = GraphMemory()
        node = memory.store("event1", "Alice met Bob")

        assert "event1" in memory
        assert memory.size == 1
        assert node.content == "Alice met Bob"
        assert node.strength == 1.0

    def test_store_with_connections(self) -> None:
        """Test storing memory with connections to existing memories."""
        memory = GraphMemory()
        memory.store("event1", "First event")
        node2 = memory.store("event2", "Second event", connections={"event1": 0.7})

        assert node2.connections.get("event1") == 0.7
        # Bidirectional connection
        event1 = memory.get("event1")
        assert event1 is not None
        assert event1.connections.get("event2") == 0.7

    def test_store_ignores_invalid_connections(self) -> None:
        """Test that connections to non-existent memories are ignored."""
        memory = GraphMemory()
        node = memory.store("event1", "Event", connections={"nonexistent": 0.5})
        assert "nonexistent" not in node.connections

    def test_recall_single_node(self) -> None:
        """Test recalling a single memory."""
        memory = GraphMemory()
        memory.store("event1", "Alice met Bob")

        result = memory.recall("event1", k_hops=0)
        assert len(result.nodes) == 1
        assert result.nodes[0].id == "event1"

    def test_recall_nonexistent(self) -> None:
        """Test recalling non-existent memory."""
        memory = GraphMemory()
        result = memory.recall("nonexistent")
        assert len(result.nodes) == 0
        assert result.total_strength == 0.0

    def test_recall_1_hop(self) -> None:
        """Test 1-hop recall."""
        memory = GraphMemory()
        memory.store("a", "Memory A")
        memory.store("b", "Memory B", connections={"a": 0.8})

        result = memory.recall("a", k_hops=1)
        assert len(result.nodes) == 2
        ids = {n.id for n in result.nodes}
        assert ids == {"a", "b"}

    def test_recall_2_hop(self) -> None:
        """Test 2-hop recall traverses chain."""
        memory = GraphMemory()
        memory.store("a", "Memory A")
        memory.store("b", "Memory B", connections={"a": 0.8})
        memory.store("c", "Memory C", connections={"b": 0.7})

        # From a, 2 hops should reach b and c
        result = memory.recall("a", k_hops=2)
        ids = {n.id for n in result.nodes}
        assert ids == {"a", "b", "c"}

    def test_recall_respects_k_limit(self) -> None:
        """Test that k_hops limits traversal depth."""
        memory = GraphMemory()
        memory.store("a", "A")
        memory.store("b", "B", connections={"a": 1.0})
        memory.store("c", "C", connections={"b": 1.0})
        memory.store("d", "D", connections={"c": 1.0})

        # From a with k=1, should only reach b
        result = memory.recall("a", k_hops=1)
        ids = {n.id for n in result.nodes}
        assert ids == {"a", "b"}
        assert "c" not in ids
        assert "d" not in ids

    def test_recall_max_k_hops_enforced(self) -> None:
        """Test that max_k_hops setting is enforced."""
        memory = GraphMemory(max_k_hops=2)
        memory.store("a", "A")
        memory.store("b", "B", connections={"a": 1.0})
        memory.store("c", "C", connections={"b": 1.0})
        memory.store("d", "D", connections={"c": 1.0})

        # Request k=5, but max is 2
        result = memory.recall("a", k_hops=5)
        ids = {n.id for n in result.nodes}
        # Should only reach up to 2 hops: a, b, c (not d at hop 3)
        assert "d" not in ids

    def test_recall_by_content(self) -> None:
        """Test content-based recall."""
        memory = GraphMemory()
        memory.store("e1", "Alice greeted Bob")
        memory.store("e2", "Charlie waved at Alice")
        memory.store("e3", "Bob traded with Dave")

        results = memory.recall_by_content("Alice")
        assert len(results) == 2  # Two memories mention Alice

    def test_decay(self) -> None:
        """Test memory decay."""
        memory = GraphMemory(decay_rate=0.1, prune_threshold=0.5)
        memory.store("event", "Test event")

        # Initial strength is 1.0
        node = memory.get("event")
        assert node is not None
        assert node.strength == 1.0

        # Apply decay
        memory.decay()
        node = memory.get("event")
        assert node is not None
        assert node.strength == 0.9

        # Multiple decays
        for _ in range(4):
            memory.decay()

        # After 5 total decays: 1.0 - 5*0.1 = 0.5, still above threshold
        node = memory.get("event")
        assert node is not None
        assert node.strength == pytest.approx(0.5, abs=0.01)

    def test_decay_prunes_weak_memories(self) -> None:
        """Test that decay prunes memories below threshold."""
        memory = GraphMemory(decay_rate=0.3, prune_threshold=0.5)
        memory.store("weak", "Weak memory")

        # Decay twice: 1.0 - 0.6 = 0.4 < 0.5 threshold
        memory.decay()  # 0.7
        assert "weak" in memory
        memory.decay()  # 0.4 < 0.5
        assert "weak" not in memory

    def test_reinforce(self) -> None:
        """Test memory reinforcement."""
        memory = GraphMemory()
        memory.store(
            "event",
            "Test",
        )

        # Decay first
        memory.decay(rate=0.3)
        node = memory.get("event")
        assert node is not None
        assert node.strength == pytest.approx(0.7, abs=0.01)

        # Reinforce
        success = memory.reinforce("event", amount=0.2)
        assert success
        node = memory.get("event")
        assert node is not None
        assert node.strength == pytest.approx(0.9, abs=0.01)

    def test_reinforce_clamps_to_max(self) -> None:
        """Test that reinforce clamps to 1.0."""
        memory = GraphMemory()
        memory.store("event", "Test")

        memory.reinforce("event", amount=0.5)  # Would be 1.5
        node = memory.get("event")
        assert node is not None
        assert node.strength == 1.0

    def test_reinforce_nonexistent(self) -> None:
        """Test reinforcing non-existent memory."""
        memory = GraphMemory()
        success = memory.reinforce("nonexistent")
        assert not success

    def test_serialization_roundtrip(self) -> None:
        """Test to_dict/from_dict roundtrip."""
        memory = GraphMemory(decay_rate=0.05, prune_threshold=0.2, max_k_hops=5)
        memory.store("a", "Memory A", metadata={"tag": "important"})
        memory.store("b", "Memory B", connections={"a": 0.8})
        memory.decay()  # Change some strengths

        # Serialize
        data = memory.to_dict()

        # Deserialize
        restored = GraphMemory.from_dict(data)

        # Verify
        assert restored.size == 2
        assert restored._decay_rate == 0.05
        assert restored._prune_threshold == 0.2
        assert restored._max_k_hops == 5

        node_a = restored.get("a")
        assert node_a is not None
        assert node_a.content == "Memory A"
        assert node_a.metadata["tag"] == "important"

        node_b = restored.get("b")
        assert node_b is not None
        assert node_b.connections.get("a") == 0.8

    def test_total_strength(self) -> None:
        """Test total_strength in RecallResult."""
        memory = GraphMemory()
        memory.store("a", "A")
        memory.store("b", "B", connections={"a": 1.0})

        memory.decay(rate=0.2)  # Both at 0.8 now

        result = memory.recall("a", k_hops=1)
        assert result.total_strength == pytest.approx(1.6, abs=0.01)  # 0.8 + 0.8


class TestGraphMemoryGraph:
    """Tests for graph structure behavior."""

    def test_diamond_graph(self) -> None:
        """Test traversal of diamond-shaped graph."""
        memory = GraphMemory()
        #     a
        #    / \
        #   b   c
        #    \ /
        #     d
        memory.store("a", "Top")
        memory.store("b", "Left", connections={"a": 1.0})
        memory.store("c", "Right", connections={"a": 1.0})
        memory.store("d", "Bottom", connections={"b": 1.0, "c": 1.0})

        # From a, k=2 should reach all
        result = memory.recall("a", k_hops=2)
        ids = {n.id for n in result.nodes}
        assert ids == {"a", "b", "c", "d"}

    def test_cycle_graph(self) -> None:
        """Test traversal doesn't infinite loop on cycles."""
        memory = GraphMemory()
        # a -> b -> c -> a (cycle)
        memory.store("a", "A")
        memory.store("b", "B", connections={"a": 1.0})
        memory.store("c", "C", connections={"b": 1.0})
        # Add cycle back
        memory._nodes["a"].connections["c"] = 1.0
        memory._nodes["c"].connections["a"] = 1.0

        # Should not infinite loop
        result = memory.recall("a", k_hops=10)
        ids = {n.id for n in result.nodes}
        assert ids == {"a", "b", "c"}  # All visited exactly once

    def test_disconnected_nodes(self) -> None:
        """Test that disconnected nodes aren't reached."""
        memory = GraphMemory()
        memory.store("a", "A")
        memory.store("b", "B", connections={"a": 1.0})
        memory.store("isolated", "Isolated node")  # No connections

        result = memory.recall("a", k_hops=3)
        ids = {n.id for n in result.nodes}
        assert "isolated" not in ids
