"""
Tests for ConductorNode AGENTESE integration.

CLI v7 Phase 2: Deep Conversation

Test categories (per test-patterns.md T-gent taxonomy):
- Type I (Unit): Node creation and affordances
- Type II (Integration): Node + ConversationWindow
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

# =============================================================================
# Fixtures
# =============================================================================


@dataclass
class MockMeta:
    """Mock observer metadata."""

    name: str = "test_observer"
    archetype: str = "developer"


@dataclass
class MockUmwelt:
    """Mock Umwelt for testing."""

    meta: MockMeta = field(default_factory=MockMeta)


# =============================================================================
# Type I: Unit Tests
# =============================================================================


class TestConductorNodeBasic:
    """Basic unit tests for ConductorNode."""

    def test_create_node(self) -> None:
        """Node creates with correct handle."""
        from protocols.agentese.contexts.self_conductor import ConductorNode

        node = ConductorNode()
        assert node.handle == "self.conductor"

    def test_affordances(self) -> None:
        """Node exposes correct affordances."""
        from protocols.agentese.contexts.self_conductor import (
            CONDUCTOR_AFFORDANCES,
            ConductorNode,
        )

        node = ConductorNode()
        affordances = node._get_affordances_for_archetype("developer")

        assert affordances == CONDUCTOR_AFFORDANCES
        assert "manifest" in affordances
        assert "snapshot" in affordances
        assert "history" in affordances
        assert "summary" in affordances
        assert "reset" in affordances
        assert "sessions" in affordances
        assert "config" in affordances

    def test_factory_function(self) -> None:
        """Factory creates ConductorNode."""
        from protocols.agentese.contexts.self_conductor import (
            ConductorNode,
            create_conductor_node,
        )

        node = create_conductor_node()
        assert isinstance(node, ConductorNode)


class TestConductorNodeRegistration:
    """Tests for AGENTESE registry integration."""

    def test_node_registers_on_import(self) -> None:
        """Node registers with AGENTESE registry on import."""
        # Import to trigger registration
        from protocols.agentese.contexts.self_conductor import ConductorNode  # noqa: F401
        from protocols.agentese.registry import get_registry

        registry = get_registry()
        node = registry.get("self.conductor")

        assert node is not None
        # Registry stores the class or instance - check it's the right type
        # Handle both class and instance cases
        if isinstance(node, type):
            assert node.__name__ == "ConductorNode"
        else:
            assert type(node).__name__ == "ConductorNode"


# =============================================================================
# Type II: Integration Tests
# =============================================================================


class TestConductorNodeManifest:
    """Tests for manifest aspect."""

    @pytest.mark.asyncio
    async def test_manifest_returns_rendering(self) -> None:
        """Manifest returns valid rendering."""
        from protocols.agentese.contexts.self_conductor import ConductorNode

        node = ConductorNode()
        observer = MockUmwelt()

        result = await node.manifest(observer)

        assert result.summary == "Conductor: Conversation Window Manager"
        assert "Strategies available" in result.content
        assert "sliding" in result.content
        assert "summarize" in result.content
        assert "hybrid" in result.content
        assert "affordances" in result.metadata


class TestConductorNodeAspects:
    """Tests for conductor aspects."""

    @pytest.mark.asyncio
    async def test_snapshot_without_window(self) -> None:
        """Snapshot returns error when no window."""
        from protocols.agentese.contexts.self_conductor import ConductorNode

        node = ConductorNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("snapshot", observer, session_id="nonexistent")

        assert "error" in result
        assert result["error"] == "Window not found"

    @pytest.mark.asyncio
    async def test_history_without_window(self) -> None:
        """History returns empty when no window."""
        from protocols.agentese.contexts.self_conductor import ConductorNode

        node = ConductorNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("history", observer, session_id="nonexistent")

        assert "error" in result
        assert result["messages"] == []
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_summary_without_content(self) -> None:
        """Summary get mode when no content provided."""
        from protocols.agentese.contexts.self_conductor import ConductorNode

        node = ConductorNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("summary", observer, session_id="nonexistent")

        # Should return error or no summary state
        assert "error" in result or "has_summary" in result

    @pytest.mark.asyncio
    async def test_sessions_list_empty(self) -> None:
        """Sessions list returns empty when no sessions."""
        from protocols.agentese.contexts.self_conductor import ConductorNode

        node = ConductorNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("sessions", observer)

        # Should return list (possibly empty or error)
        assert "sessions" in result or "error" in result

    @pytest.mark.asyncio
    async def test_config_without_window(self) -> None:
        """Config returns error when no window."""
        from protocols.agentese.contexts.self_conductor import ConductorNode

        node = ConductorNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("config", observer, session_id="nonexistent")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_unknown_aspect(self) -> None:
        """Unknown aspect returns not implemented."""
        from protocols.agentese.contexts.self_conductor import ConductorNode

        node = ConductorNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("unknown", observer)

        assert result["status"] == "not implemented"


# =============================================================================
# Integration with Window
# =============================================================================


class TestConductorWithWindow:
    """Tests for ConductorNode with actual ConversationWindow."""

    @pytest.mark.asyncio
    async def test_snapshot_with_window(self) -> None:
        """Snapshot returns window state when window exists."""
        from services.conductor.window import ConversationWindow

        window = ConversationWindow(max_turns=5, strategy="sliding")
        window.add_turn("Hello", "Hi there!")
        window.add_turn("How are you?", "I'm fine!")

        snapshot = window.snapshot()

        assert snapshot.turn_count == 2
        assert snapshot.strategy == "sliding"
        assert not snapshot.has_summary

    @pytest.mark.asyncio
    async def test_history_format(self) -> None:
        """History returns properly formatted messages."""
        from services.conductor.window import ConversationWindow

        window = ConversationWindow(max_turns=10)
        window.set_system_prompt("Be helpful.")
        window.add_turn("Hello", "World")

        messages = window.get_context_messages()

        # Should have system + user + assistant
        assert len(messages) == 3
        assert messages[0].role == "system"
        assert messages[1].role == "user"
        assert messages[2].role == "assistant"
