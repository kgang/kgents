"""
Tests for Stream Context Resolver: self.stream.*
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from agents.d.context_window import ContextWindow, TurnRole
from agents.d.linearity import ResourceClass
from protocols.agentese.contexts.stream import (
    StreamContextResolver,
    StreamFocusNode,
    StreamLinearityNode,
    StreamMapNode,
    StreamPressureNode,
    StreamProjectNode,
    StreamSeekNode,
    create_stream_resolver,
)


def make_observer() -> MagicMock:
    """Create a mock observer/Umwelt for testing."""
    observer = MagicMock()
    observer.dna = MagicMock()
    observer.dna.archetype = "test"
    observer.dna.name = "test-agent"
    observer.dna.capabilities = ["test"]
    return observer


class TestStreamContextResolver:
    """Tests for StreamContextResolver."""

    def test_create_resolver(self) -> None:
        """Can create a resolver."""
        resolver = StreamContextResolver()
        assert resolver._window is None

    def test_set_window(self) -> None:
        """Can set window and nodes are updated."""
        resolver = StreamContextResolver()
        window = ContextWindow()
        window.append(TurnRole.USER, "Hello")

        resolver.set_window(window)

        assert resolver._window is window
        assert resolver._focus is not None
        assert resolver._focus._window is window

    def test_resolve_focus(self) -> None:
        """Can resolve self.stream.focus."""
        resolver = create_stream_resolver()
        node = resolver.resolve("focus", [])
        assert isinstance(node, StreamFocusNode)

    def test_resolve_map(self) -> None:
        """Can resolve self.stream.map."""
        resolver = create_stream_resolver()
        node = resolver.resolve("map", [])
        assert isinstance(node, StreamMapNode)

    def test_resolve_seek(self) -> None:
        """Can resolve self.stream.seek."""
        resolver = create_stream_resolver()
        node = resolver.resolve("seek", [])
        assert isinstance(node, StreamSeekNode)

    def test_resolve_project(self) -> None:
        """Can resolve self.stream.project."""
        resolver = create_stream_resolver()
        node = resolver.resolve("project", [])
        assert isinstance(node, StreamProjectNode)

    def test_resolve_linearity(self) -> None:
        """Can resolve self.stream.linearity."""
        resolver = create_stream_resolver()
        node = resolver.resolve("linearity", [])
        assert isinstance(node, StreamLinearityNode)

    def test_resolve_pressure(self) -> None:
        """Can resolve self.stream.pressure."""
        resolver = create_stream_resolver()
        node = resolver.resolve("pressure", [])
        assert isinstance(node, StreamPressureNode)

    def test_resolve_unknown(self) -> None:
        """Unknown paths return generic node."""
        resolver = create_stream_resolver()
        node = resolver.resolve("unknown", [])
        assert node.handle == "self.stream.unknown"


class TestStreamFocusNode:
    """Tests for StreamFocusNode."""

    @pytest.mark.asyncio
    async def test_manifest_no_window(self) -> None:
        """Manifest handles no window."""
        node = StreamFocusNode()
        observer = make_observer()

        result = await node.manifest(observer)
        assert "not initialized" in result.content

    @pytest.mark.asyncio
    async def test_manifest_empty_window(self) -> None:
        """Manifest handles empty window."""
        node = StreamFocusNode(_window=ContextWindow())
        observer = make_observer()

        result = await node.manifest(observer)
        assert "No turns" in result.content or "Empty" in result.summary

    @pytest.mark.asyncio
    async def test_manifest_with_turns(self) -> None:
        """Manifest shows current focus."""
        window = ContextWindow()
        window.append(TurnRole.USER, "Hello world")
        node = StreamFocusNode(_window=window)
        observer = make_observer()

        result = await node.manifest(observer)
        assert "user" in result.summary.lower() or "user" in result.metadata.get(
            "role", ""
        )

    @pytest.mark.asyncio
    async def test_extract_aspect(self) -> None:
        """Can extract current turn."""
        window = ContextWindow()
        window.append(TurnRole.USER, "Test content")
        node = StreamFocusNode(_window=window)
        observer = make_observer()

        result = await node._invoke_aspect("extract", observer)
        assert result["content"] == "Test content"
        assert result["role"] == "user"

    @pytest.mark.asyncio
    async def test_peek_aspect(self) -> None:
        """Can peek at specific position."""
        window = ContextWindow()
        window.append(TurnRole.USER, "First")
        window.append(TurnRole.ASSISTANT, "Second")
        node = StreamFocusNode(_window=window)
        observer = make_observer()

        result = await node._invoke_aspect("peek", observer, position=1)
        assert result["content"] == "First"


class TestStreamMapNode:
    """Tests for StreamMapNode."""

    @pytest.mark.asyncio
    async def test_extend_content(self) -> None:
        """Can extend with content transform."""
        window = ContextWindow()
        window.append(TurnRole.USER, "A")
        window.append(TurnRole.ASSISTANT, "B")
        node = StreamMapNode(_window=window)
        observer = make_observer()

        result = await node._invoke_aspect("extend", observer, transform="content")
        assert result == ["", "A", "B"]

    @pytest.mark.asyncio
    async def test_extend_role(self) -> None:
        """Can extend with role transform."""
        window = ContextWindow()
        window.append(TurnRole.USER, "A")
        window.append(TurnRole.ASSISTANT, "B")
        node = StreamMapNode(_window=window)
        observer = make_observer()

        result = await node._invoke_aspect("extend", observer, transform="role")
        assert result == [None, "user", "assistant"]

    @pytest.mark.asyncio
    async def test_transform_aspect(self) -> None:
        """Transform returns turn summaries."""
        window = ContextWindow()
        window.append(TurnRole.USER, "Hello")
        window.append(TurnRole.ASSISTANT, "Hi")
        node = StreamMapNode(_window=window)
        observer = make_observer()

        result = await node._invoke_aspect("transform", observer)
        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[1]["role"] == "assistant"


class TestStreamSeekNode:
    """Tests for StreamSeekNode."""

    @pytest.mark.asyncio
    async def test_position_aspect(self) -> None:
        """Can get and set position."""
        window = ContextWindow()
        window.append(TurnRole.USER, "A")
        window.append(TurnRole.ASSISTANT, "B")
        node = StreamSeekNode(_window=window)
        observer = make_observer()

        # Get current
        result = await node._invoke_aspect("position", observer)
        assert result["position"] == 2

        # Set new position
        result = await node._invoke_aspect("position", observer, target=1)
        assert result["position"] == 1

    @pytest.mark.asyncio
    async def test_forward_backward(self) -> None:
        """Can move forward and backward."""
        window = ContextWindow()
        window.append(TurnRole.USER, "A")
        window.append(TurnRole.ASSISTANT, "B")
        window.append(TurnRole.USER, "C")
        node = StreamSeekNode(_window=window)
        observer = make_observer()

        assert window.position == 3

        await node._invoke_aspect("backward", observer, steps=2)
        assert window.position == 1

        await node._invoke_aspect("forward", observer, steps=1)
        assert window.position == 2

    @pytest.mark.asyncio
    async def test_start_end(self) -> None:
        """Can jump to start and end."""
        window = ContextWindow()
        window.append(TurnRole.USER, "A")
        window.append(TurnRole.ASSISTANT, "B")
        window.append(TurnRole.USER, "C")
        node = StreamSeekNode(_window=window)
        observer = make_observer()

        await node._invoke_aspect("start", observer)
        assert window.position == 1

        await node._invoke_aspect("end", observer)
        assert window.position == 3


class TestStreamProjectNode:
    """Tests for StreamProjectNode."""

    @pytest.mark.asyncio
    async def test_compress_aspect(self) -> None:
        """Can compress context."""
        window = ContextWindow(max_tokens=100)
        for i in range(10):
            window.append(TurnRole.ASSISTANT, f"Message {i} " * 10)
        node = StreamProjectNode(_window=window)
        observer = make_observer()

        result = await node._invoke_aspect("compress", observer, target_pressure=0.3)

        assert "compression_ratio" in result
        assert "dropped" in result or "summarized" in result

    @pytest.mark.asyncio
    async def test_threshold_aspect(self) -> None:
        """Can update adaptive threshold."""
        window = ContextWindow()
        node = StreamProjectNode(_window=window)
        observer = make_observer()

        result = await node._invoke_aspect(
            "threshold",
            observer,
            task_progress=0.5,
            error_rate=0.1,
        )

        assert "effective_threshold" in result
        assert result["task_progress"] == 0.5
        assert result["error_rate"] == 0.1

    @pytest.mark.asyncio
    async def test_stats_aspect(self) -> None:
        """Can get projection stats."""
        window = ContextWindow()
        window.append(TurnRole.USER, "Test")
        node = StreamProjectNode(_window=window)
        observer = make_observer()

        result = await node._invoke_aspect("stats", observer)

        assert "pressure" in result
        assert "total_tokens" in result
        assert "turn_count" in result


class TestStreamLinearityNode:
    """Tests for StreamLinearityNode."""

    @pytest.mark.asyncio
    async def test_tag_aspect(self) -> None:
        """Can tag a resource."""
        window = ContextWindow()
        node = StreamLinearityNode(_window=window)
        observer = make_observer()

        result = await node._invoke_aspect(
            "tag",
            observer,
            content="Important",
            resource_class="PRESERVED",
            provenance="test",
        )

        assert "resource_id" in result
        assert result["resource_class"] == "PRESERVED"

    @pytest.mark.asyncio
    async def test_promote_aspect(self) -> None:
        """Can promote a resource."""
        window = ContextWindow()
        turn = window.append(TurnRole.ASSISTANT, "temp")
        node = StreamLinearityNode(_window=window)
        observer = make_observer()

        result = await node._invoke_aspect(
            "promote",
            observer,
            resource_id=turn.resource_id,
            new_class="REQUIRED",
            rationale="became important",
        )

        assert result["success"] is True
        assert result["new_class"] == "REQUIRED"

    @pytest.mark.asyncio
    async def test_stats_aspect(self) -> None:
        """Can get linearity stats."""
        window = ContextWindow()
        window.append(TurnRole.USER, "A")  # PRESERVED
        window.append(TurnRole.ASSISTANT, "B")  # DROPPABLE
        node = StreamLinearityNode(_window=window)
        observer = make_observer()

        result = await node._invoke_aspect("stats", observer)

        assert "droppable" in result or "total" in result


class TestStreamPressureNode:
    """Tests for StreamPressureNode."""

    @pytest.mark.asyncio
    async def test_check_aspect(self) -> None:
        """Can check pressure."""
        window = ContextWindow(max_tokens=1000)
        window.append(TurnRole.USER, "Test")
        node = StreamPressureNode(_window=window)
        observer = make_observer()

        result = await node._invoke_aspect("check", observer)

        assert "pressure" in result
        assert "needs_compression" in result
        assert result["needs_compression"] is False  # Small content

    @pytest.mark.asyncio
    async def test_auto_compress_not_needed(self) -> None:
        """Auto compress skips when not needed."""
        window = ContextWindow(max_tokens=100000)
        window.append(TurnRole.USER, "Small content")
        node = StreamPressureNode(_window=window)
        observer = make_observer()

        result = await node._invoke_aspect("auto_compress", observer)

        assert result["compressed"] is False
        assert "below threshold" in result["reason"]

    @pytest.mark.asyncio
    async def test_auto_compress_when_needed(self) -> None:
        """Auto compress runs when needed."""
        window = ContextWindow(max_tokens=100)
        for i in range(10):
            window.append(TurnRole.ASSISTANT, f"Message {i} " * 50)
        node = StreamPressureNode(_window=window)
        observer = make_observer()

        assert window.needs_compression

        result = await node._invoke_aspect("auto_compress", observer)

        assert result["compressed"] is True
        assert "compression_ratio" in result


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_stream_resolver(self) -> None:
        """Can create resolver with window."""
        resolver = create_stream_resolver(max_tokens=5000)

        assert resolver._window is not None
        assert resolver._window.max_tokens == 5000

    def test_create_with_system(self) -> None:
        """Can create with system message."""
        resolver = create_stream_resolver(
            max_tokens=5000,
            initial_system="You are helpful.",
        )

        window = resolver.get_window()
        assert window is not None
        assert len(window) == 1

        turns = window.all_turns()
        assert turns[0].role == TurnRole.SYSTEM
