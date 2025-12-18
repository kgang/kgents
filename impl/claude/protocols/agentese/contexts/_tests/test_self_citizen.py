"""
Tests for self.citizen.<name>.* AGENTESE paths.

Phase 3 Crown Jewels: Living Town with persistent citizen memory.
"""

import pytest

from protocols.agentese.contexts.self_citizen import (
    CITIZEN_AFFORDANCES,
    CITIZEN_MEMORY_AFFORDANCES,
    CITIZEN_PERSONALITY_AFFORDANCES,
    CitizenMemoryNode,
    CitizenNode,
    CitizenPersonalityNode,
    create_citizen_node,
)


class TestCitizenAffordances:
    """Test citizen affordance definitions."""

    def test_citizen_affordances_exist(self) -> None:
        """Citizen node has expected affordances."""
        assert "manifest" in CITIZEN_AFFORDANCES
        assert "chat" in CITIZEN_AFFORDANCES
        assert "memory" in CITIZEN_AFFORDANCES
        assert "personality" in CITIZEN_AFFORDANCES

    def test_memory_affordances_exist(self) -> None:
        """Memory sub-node has expected affordances."""
        assert "recall" in CITIZEN_MEMORY_AFFORDANCES
        assert "conversations" in CITIZEN_MEMORY_AFFORDANCES
        assert "store" in CITIZEN_MEMORY_AFFORDANCES
        assert "search" in CITIZEN_MEMORY_AFFORDANCES
        assert "summary" in CITIZEN_MEMORY_AFFORDANCES

    def test_personality_affordances_exist(self) -> None:
        """Personality sub-node has expected affordances."""
        assert "manifest" in CITIZEN_PERSONALITY_AFFORDANCES
        assert "drift" in CITIZEN_PERSONALITY_AFFORDANCES


class TestCitizenNode:
    """Test CitizenNode."""

    def test_handle_without_name(self) -> None:
        """Handle is self.citizen without name."""
        node = CitizenNode()
        assert node.handle == "self.citizen"

    def test_handle_with_name(self) -> None:
        """Handle includes citizen name (lowercase)."""
        node = CitizenNode(_citizen_name="Elara")
        assert node.handle == "self.citizen.elara"

    def test_factory_creates_with_subnodes(self) -> None:
        """Factory creates node with memory and personality subnodes."""
        node = create_citizen_node("Kira")
        assert node._citizen_name == "Kira"
        assert node._memory_node is not None
        assert node._personality_node is not None


class TestCitizenMemoryNode:
    """Test CitizenMemoryNode."""

    def test_handle_with_name(self) -> None:
        """Handle includes citizen name and memory suffix."""
        node = CitizenMemoryNode(_citizen_name="Finn")
        assert node.handle == "self.citizen.finn.memory"

    def test_affordances(self) -> None:
        """Memory node has correct affordances."""
        node = CitizenMemoryNode(_citizen_name="Finn")
        affs = node._get_affordances_for_archetype("any")
        assert "recall" in affs
        assert "conversations" in affs


class TestCitizenPersonalityNode:
    """Test CitizenPersonalityNode."""

    def test_handle_with_name(self) -> None:
        """Handle includes citizen name and personality suffix."""
        node = CitizenPersonalityNode(_citizen_name="Jorah")
        assert node.handle == "self.citizen.jorah.personality"

    def test_affordances(self) -> None:
        """Personality node has correct affordances."""
        node = CitizenPersonalityNode(_citizen_name="Jorah")
        affs = node._get_affordances_for_archetype("any")
        assert "manifest" in affs
        assert "drift" in affs


class TestPathIntegration:
    """Test AGENTESE path patterns."""

    def test_path_pattern_memory_recall(self) -> None:
        """self.citizen.<name>.memory supports recall path pattern."""
        node = CitizenMemoryNode(_citizen_name="Elara")
        # Path would be: self.citizen.elara.memory.recall[query="..."]
        assert "recall" in node._get_affordances_for_archetype("any")

    def test_path_pattern_chat(self) -> None:
        """self.citizen.<name> supports chat path pattern."""
        node = CitizenNode(_citizen_name="Kira")
        # Path would be: self.citizen.kira.chat[message="Hello!"]
        assert "chat" in node._get_affordances_for_archetype("any")
