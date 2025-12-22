"""
Tests for Dawn Cockpit AGENTESE node.

Verifies node registration, aspect invocation, and Witness integration.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from protocols.agentese.node import Observer
from protocols.agentese.registry import get_registry

from ..contracts import (
    FocusAddResponse,
    FocusListResponse,
    FocusMoveResponse,
    FocusRemoveResponse,
    SnippetAddResponse,
    SnippetCopyResponse,
    SnippetListResponse,
    SnippetRemoveResponse,
)
from ..focus import Bucket, FocusManager
from ..node import (
    DAWN_AFFORDANCES,
    DawnNode,
    create_dawn_node,
    get_dawn_node,
    reset_dawn_node,
)
from ..snippets import SnippetLibrary


class TestNodeRegistration:
    """Tests for AGENTESE node registration."""

    def test_node_registered_in_registry(self) -> None:
        """DawnNode is registered at time.dawn path."""
        # Import triggers registration
        from .. import node  # noqa: F401

        registry = get_registry()
        assert registry.has("time.dawn")

    def test_node_handle(self) -> None:
        """DawnNode has correct handle."""
        node = create_dawn_node()
        assert node.handle == "time.dawn"

    def test_dawn_affordances(self) -> None:
        """DAWN_AFFORDANCES includes all expected aspects."""
        expected = {
            "manifest",
            "focus_list",
            "focus_add",
            "focus_remove",
            "focus_promote",
            "focus_demote",
            "snippets_list",
            "snippets_copy",
            "snippets_add",
            "snippets_remove",
        }
        assert set(DAWN_AFFORDANCES) == expected


class TestNodeConstruction:
    """Tests for DawnNode construction."""

    def test_create_with_defaults(self) -> None:
        """DawnNode initializes with default managers."""
        node = create_dawn_node()
        assert node.focus_manager is not None
        assert node.snippet_library is not None

    def test_create_with_injected_dependencies(self) -> None:
        """DawnNode accepts injected dependencies."""
        fm = FocusManager()
        sl = SnippetLibrary()
        node = create_dawn_node(
            focus_manager=fm,
            snippet_library=sl,
        )
        assert node.focus_manager is fm
        assert node.snippet_library is sl

    def test_singleton_pattern(self) -> None:
        """get_dawn_node returns singleton."""
        reset_dawn_node()
        node1 = get_dawn_node()
        node2 = get_dawn_node()
        assert node1 is node2
        reset_dawn_node()

    def test_reset_singleton(self) -> None:
        """reset_dawn_node clears singleton."""
        node1 = get_dawn_node()
        reset_dawn_node()
        node2 = get_dawn_node()
        assert node1 is not node2
        reset_dawn_node()


class TestManifestAspect:
    """Tests for manifest aspect."""

    @pytest.mark.asyncio
    async def test_manifest_returns_counts(self) -> None:
        """manifest returns focus and snippet counts."""
        fm = FocusManager()
        fm.add("target1", label="Item 1")
        fm.add("target2", label="Item 2")

        node = create_dawn_node(focus_manager=fm)
        observer = Observer.test()

        result = await node.manifest(observer)

        assert "Dawn Cockpit" in result.to_text()
        assert result.metadata["focus_count"] == 2
        assert result.metadata["today_count"] == 2

    @pytest.mark.asyncio
    async def test_manifest_counts_snippets(self) -> None:
        """manifest counts all snippet types."""
        sl = SnippetLibrary()
        sl.load_defaults()  # Adds static and query snippets
        sl.add_custom("Custom", "Content")

        node = create_dawn_node(snippet_library=sl)
        observer = Observer.test()

        result = await node.manifest(observer)

        assert result.metadata["snippet_count"] == len(sl)


class TestFocusAspects:
    """Tests for focus-related aspects."""

    @pytest.mark.asyncio
    async def test_focus_list_all(self) -> None:
        """focus_list returns all items."""
        fm = FocusManager()
        fm.add("target1", label="Item 1")
        fm.add("target2", label="Item 2", bucket=Bucket.WEEK)

        node = create_dawn_node(focus_manager=fm)
        observer = Observer.test()

        result = await node.focus_list(observer)

        assert isinstance(result, FocusListResponse)
        assert result.total_count == 2

    @pytest.mark.asyncio
    async def test_focus_list_by_bucket(self) -> None:
        """focus_list filters by bucket."""
        fm = FocusManager()
        fm.add("target1", label="Today Item")
        fm.add("target2", label="Week Item", bucket=Bucket.WEEK)

        node = create_dawn_node(focus_manager=fm)
        observer = Observer.test()

        result = await node.focus_list(observer, bucket="today")

        assert result.total_count == 1
        assert result.items[0].label == "Today Item"

    @pytest.mark.asyncio
    async def test_focus_add(self) -> None:
        """focus_add creates new item."""
        fm = FocusManager()
        node = create_dawn_node(focus_manager=fm)
        observer = Observer.test()

        result = await node.focus_add(
            observer,
            target="path/to/file.md",
            label="New Task",
        )

        assert isinstance(result, FocusAddResponse)
        assert result.success is True
        assert result.item.label == "New Task"
        assert len(fm) == 1

    @pytest.mark.asyncio
    async def test_focus_add_with_bucket(self) -> None:
        """focus_add respects bucket parameter."""
        fm = FocusManager()
        node = create_dawn_node(focus_manager=fm)
        observer = Observer.test()

        result = await node.focus_add(
            observer,
            target="path/to/file.md",
            bucket="week",
        )

        assert result.item.bucket == "week"

    @pytest.mark.asyncio
    async def test_focus_remove(self) -> None:
        """focus_remove deletes item."""
        fm = FocusManager()
        item = fm.add("target", label="To Remove")

        node = create_dawn_node(focus_manager=fm)
        observer = Observer.test()

        result = await node.focus_remove(observer, item_id=item.id)

        assert isinstance(result, FocusRemoveResponse)
        assert result.removed is True
        assert len(fm) == 0

    @pytest.mark.asyncio
    async def test_focus_remove_not_found(self) -> None:
        """focus_remove returns False for missing item."""
        fm = FocusManager()
        node = create_dawn_node(focus_manager=fm)
        observer = Observer.test()

        result = await node.focus_remove(observer, item_id="nonexistent")

        assert result.removed is False

    @pytest.mark.asyncio
    async def test_focus_promote(self) -> None:
        """focus_promote moves item to higher bucket."""
        fm = FocusManager()
        item = fm.add("target", label="To Promote", bucket=Bucket.WEEK)

        node = create_dawn_node(focus_manager=fm)
        observer = Observer.test()

        result = await node.focus_promote(observer, item_id=item.id)

        assert isinstance(result, FocusMoveResponse)
        assert result.previous_bucket == "week"
        assert result.new_bucket == "today"

    @pytest.mark.asyncio
    async def test_focus_demote(self) -> None:
        """focus_demote moves item to lower bucket."""
        fm = FocusManager()
        item = fm.add("target", label="To Demote", bucket=Bucket.TODAY)

        node = create_dawn_node(focus_manager=fm)
        observer = Observer.test()

        result = await node.focus_demote(observer, item_id=item.id)

        assert isinstance(result, FocusMoveResponse)
        assert result.previous_bucket == "today"
        assert result.new_bucket == "week"

    @pytest.mark.asyncio
    async def test_focus_promote_not_found(self) -> None:
        """focus_promote returns None for missing item."""
        fm = FocusManager()
        node = create_dawn_node(focus_manager=fm)
        observer = Observer.test()

        result = await node.focus_promote(observer, item_id="nonexistent")

        assert result is None


class TestSnippetAspects:
    """Tests for snippet-related aspects."""

    @pytest.mark.asyncio
    async def test_snippets_list(self) -> None:
        """snippets_list returns all snippets."""
        sl = SnippetLibrary()
        sl.load_defaults()

        node = create_dawn_node(snippet_library=sl)
        observer = Observer.test()

        result = await node.snippets_list(observer)

        assert isinstance(result, SnippetListResponse)
        assert result.total_count > 0
        assert result.query_count > 0  # Only query snippets by default

    @pytest.mark.asyncio
    async def test_snippets_copy_without_witness(self) -> None:
        """snippets_copy works without Witness."""
        sl = SnippetLibrary()
        snippet = sl.add_static(
            kind="voice_anchor",
            label="Test Voice",
            content="Voice content",
            source="test",
        )

        node = create_dawn_node(snippet_library=sl)
        observer = Observer.test()

        result = await node.snippets_copy(observer, snippet_id=snippet.id)

        assert isinstance(result, SnippetCopyResponse)
        assert result.copied is True
        assert result.content == "Voice content"
        assert result.witness_mark_id is None

    @pytest.mark.asyncio
    async def test_snippets_copy_with_witness(self) -> None:
        """snippets_copy records in Witness when available."""
        sl = SnippetLibrary()
        snippet = sl.add_static(
            kind="voice_anchor",
            label="Test Voice",
            content="Voice content",
            source="test",
        )

        # Mock WitnessPersistence
        mock_witness = MagicMock()
        mock_result = MagicMock()
        mock_result.mark_id = "mark-123"
        mock_witness.save_mark = AsyncMock(return_value=mock_result)

        node = create_dawn_node(
            snippet_library=sl,
            witness_persistence=mock_witness,
        )
        observer = Observer.test()

        result = await node.snippets_copy(observer, snippet_id=snippet.id)

        assert result.witness_mark_id == "mark-123"
        mock_witness.save_mark.assert_called_once()

    @pytest.mark.asyncio
    async def test_snippets_copy_not_found(self) -> None:
        """snippets_copy returns None for missing snippet."""
        sl = SnippetLibrary()
        node = create_dawn_node(snippet_library=sl)
        observer = Observer.test()

        result = await node.snippets_copy(observer, snippet_id="nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_snippets_copy_query_fallback(self) -> None:
        """snippets_copy returns fallback for unloaded QuerySnippet when AGENTESE unavailable."""
        sl = SnippetLibrary()
        # Add a query snippet (content will be None until loaded)
        snippet = sl.add_query(
            kind="now",
            label="Test Query",
            query="self.nonexistent.path",  # Non-existent path for testing
        )
        assert snippet.content is None  # Verify not loaded

        node = create_dawn_node(snippet_library=sl)
        observer = Observer.test()

        result = await node.snippets_copy(observer, snippet_id=snippet.id)

        assert isinstance(result, SnippetCopyResponse)
        assert result.copied is True
        # Should contain fallback message since AGENTESE path doesn't exist
        assert "self.nonexistent.path" in result.content

    @pytest.mark.asyncio
    async def test_snippets_add(self) -> None:
        """snippets_add creates custom snippet."""
        sl = SnippetLibrary()
        node = create_dawn_node(snippet_library=sl)
        observer = Observer.test()

        result = await node.snippets_add(
            observer,
            label="My Note",
            content="Important thing",
        )

        assert isinstance(result, SnippetAddResponse)
        assert result.success is True
        assert result.snippet.label == "My Note"

    @pytest.mark.asyncio
    async def test_snippets_remove(self) -> None:
        """snippets_remove deletes custom snippet."""
        sl = SnippetLibrary()
        snippet = sl.add_custom("Custom", "Content")

        node = create_dawn_node(snippet_library=sl)
        observer = Observer.test()

        result = await node.snippets_remove(observer, snippet_id=snippet.id)

        assert isinstance(result, SnippetRemoveResponse)
        assert result.removed is True

    @pytest.mark.asyncio
    async def test_snippets_remove_static_fails(self) -> None:
        """snippets_remove cannot delete static snippets."""
        sl = SnippetLibrary()
        snippet = sl.add_static(
            kind="voice_anchor",
            label="Static",
            content="Content",
            source="test",
        )

        node = create_dawn_node(snippet_library=sl)
        observer = Observer.test()

        result = await node.snippets_remove(observer, snippet_id=snippet.id)

        assert result.removed is False


class TestAspectRouting:
    """Tests for aspect routing."""

    @pytest.mark.asyncio
    async def test_invoke_with_underscores(self) -> None:
        """Aspects work with underscore names."""
        node = create_dawn_node()
        observer = Observer.test()

        result = await node._invoke_aspect("focus_list", observer)

        assert isinstance(result, FocusListResponse)

    @pytest.mark.asyncio
    async def test_invoke_with_dots(self) -> None:
        """Aspects work with dot names."""
        node = create_dawn_node()
        observer = Observer.test()

        result = await node._invoke_aspect("focus.list", observer)

        assert isinstance(result, FocusListResponse)

    @pytest.mark.asyncio
    async def test_invoke_unknown_aspect(self) -> None:
        """Unknown aspect raises ValueError."""
        node = create_dawn_node()
        observer = Observer.test()

        with pytest.raises(ValueError, match="Unknown aspect"):
            await node._invoke_aspect("unknown_aspect", observer)
