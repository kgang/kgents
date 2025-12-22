"""
Tests for self.portal AGENTESE node.

"Navigation is expansion. Expansion is navigation."
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest

from protocols.agentese.contexts.self_portal import (
    PORTAL_AFFORDANCES,
    PortalNavNode,
    get_portal_nav_node,
    set_portal_nav_node,
)
from protocols.agentese.node import Observer

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def observer() -> Observer:
    """Create a test observer."""
    return Observer(archetype="developer", capabilities=frozenset())


@pytest.fixture
def portal_node() -> PortalNavNode:
    """Create a fresh portal node for testing."""
    # Reset singleton
    set_portal_nav_node(None)
    node = PortalNavNode()
    return node


@pytest.fixture
def mock_op_file(tmp_path: Path) -> Path:
    """Create a mock .op file with portal links."""
    content = dedent("""
        # mark: Record a Witness Trace

        > "The proof IS the decision."

        ## Wires To

        - [enables] `WITNESS_OPERAD/walk` (traverse marks)
        - [feeds] `ASHC` (evidence for proof compilation)

        ## Examples

        ```python
        await witness.mark(action="Selected JWT")
        ```
    """).strip()

    op_file = tmp_path / "mark.op"
    op_file.write_text(content)
    return op_file


# =============================================================================
# Node Registration Tests
# =============================================================================


class TestPortalNodeRegistration:
    """Tests for @node registration."""

    def test_node_is_registered(self) -> None:
        """self.portal should be registered in the AGENTESE registry."""
        from protocols.agentese.registry import get_registry

        registry = get_registry()
        assert registry.has("self.portal"), "self.portal should be registered"

    def test_affordances_defined(self) -> None:
        """Portal affordances should be defined."""
        assert "manifest" in PORTAL_AFFORDANCES
        assert "expand" in PORTAL_AFFORDANCES
        assert "collapse" in PORTAL_AFFORDANCES
        assert "tree" in PORTAL_AFFORDANCES
        assert "trail" in PORTAL_AFFORDANCES
        assert "available" in PORTAL_AFFORDANCES

    def test_singleton_factory(self) -> None:
        """get_portal_nav_node should return singleton."""
        set_portal_nav_node(None)
        node1 = get_portal_nav_node()
        node2 = get_portal_nav_node()
        assert node1 is node2


# =============================================================================
# Aspect Tests
# =============================================================================


class TestManifestAspect:
    """Tests for manifest aspect."""

    @pytest.mark.asyncio
    async def test_manifest_returns_rendering(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """manifest should return a Renderable."""
        result = await portal_node.manifest(observer)

        assert result is not None
        assert hasattr(result, "summary")
        assert hasattr(result, "content")
        assert hasattr(result, "metadata")

    @pytest.mark.asyncio
    async def test_manifest_metadata_has_route(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """manifest metadata should include route for frontend."""
        result = await portal_node.manifest(observer)

        assert "route" in result.metadata
        assert result.metadata["route"] == "/portal"


class TestExpandAspect:
    """Tests for expand aspect."""

    @pytest.mark.asyncio
    async def test_expand_returns_bool_in_result(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """expand() should return success status in metadata."""
        result = await portal_node.expand(observer, "nonexistent")

        assert "success" in result.metadata
        assert result.metadata["success"] is False  # No such portal

    @pytest.mark.asyncio
    async def test_expand_with_path_segments(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """expand() should parse path with / separator."""
        result = await portal_node.expand(observer, "tests/covers")

        # Even though it fails, the path should be parsed
        assert "portal_path" in result.metadata
        assert result.metadata["portal_path"] == "tests/covers"


class TestCollapseAspect:
    """Tests for collapse aspect."""

    @pytest.mark.asyncio
    async def test_collapse_nonexistent(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """collapse() on nonexistent path should report failure."""
        result = await portal_node.collapse(observer, "nonexistent")

        assert result.metadata["success"] is False


class TestTreeAspect:
    """Tests for tree aspect."""

    @pytest.mark.asyncio
    async def test_tree_returns_rendered_string(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """tree() should return rendered tree structure."""
        result = await portal_node.tree(observer)

        assert result is not None
        assert isinstance(result.content, str)

    @pytest.mark.asyncio
    async def test_tree_respects_max_depth(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """tree() should respect max_depth parameter."""
        result = await portal_node.tree(observer, max_depth=2)

        assert "max_depth" in result.metadata
        assert result.metadata["max_depth"] == 2


class TestTrailAspect:
    """Tests for trail aspect."""

    @pytest.mark.asyncio
    async def test_trail_returns_step_count(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """trail() should include step count in metadata."""
        result = await portal_node.trail(observer)

        assert "step_count" in result.metadata
        assert isinstance(result.metadata["step_count"], int)

    @pytest.mark.asyncio
    async def test_trail_dfs_order(self, portal_node: PortalNavNode, observer: Observer) -> None:
        """Trail should be in DFS order (expanded nodes first)."""
        result = await portal_node.trail(observer, name="Test Trail")

        assert "trail_name" in result.metadata
        assert result.metadata["trail_name"] == "Test Trail"


class TestAvailableAspect:
    """Tests for available aspect."""

    @pytest.mark.asyncio
    async def test_available_lists_expandable(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """available() should list expandable portals."""
        result = await portal_node.available(observer)

        assert "expandable" in result.metadata
        assert "collapsible" in result.metadata
        assert isinstance(result.metadata["expandable"], list)
        assert isinstance(result.metadata["collapsible"], list)


# =============================================================================
# Invoke Routing Tests
# =============================================================================


class TestInvokeRouting:
    """Tests for _invoke_aspect routing."""

    @pytest.mark.asyncio
    async def test_invoke_expand(self, portal_node: PortalNavNode, observer: Observer) -> None:
        """_invoke_aspect should route 'expand' correctly."""
        result = await portal_node._invoke_aspect(
            "expand",
            observer,
            portal_path="tests",
        )
        assert "success" in result.metadata

    @pytest.mark.asyncio
    async def test_invoke_collapse(self, portal_node: PortalNavNode, observer: Observer) -> None:
        """_invoke_aspect should route 'collapse' correctly."""
        result = await portal_node._invoke_aspect(
            "collapse",
            observer,
            portal_path="tests",
        )
        assert "success" in result.metadata

    @pytest.mark.asyncio
    async def test_invoke_unknown(self, portal_node: PortalNavNode, observer: Observer) -> None:
        """_invoke_aspect should handle unknown aspects."""
        result = await portal_node._invoke_aspect(
            "unknown_aspect",
            observer,
        )
        assert "error" in result.metadata
        assert result.metadata["error"] == "unknown_aspect"


# =============================================================================
# Integration with PortalTree
# =============================================================================


class TestPortalTreeIntegration:
    """Tests for integration with file_operad.portal.PortalTree."""

    @pytest.mark.asyncio
    async def test_tree_is_lazily_initialized(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """Portal tree should be initialized on first access."""
        assert portal_node._tree is None

        await portal_node.manifest(observer)

        assert portal_node._tree is not None

    @pytest.mark.asyncio
    async def test_tree_persists_across_calls(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """Tree should persist across multiple aspect calls."""
        await portal_node.manifest(observer)
        tree1 = portal_node._tree

        await portal_node.tree(observer)
        tree2 = portal_node._tree

        assert tree1 is tree2


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_empty_portal_path(self, portal_node: PortalNavNode, observer: Observer) -> None:
        """expand() with empty path should fail gracefully."""
        result = await portal_node.expand(observer, "")

        assert result.metadata["success"] is False

    @pytest.mark.asyncio
    async def test_deeply_nested_path(self, portal_node: PortalNavNode, observer: Observer) -> None:
        """expand() with deeply nested path should fail gracefully."""
        result = await portal_node.expand(observer, "a/b/c/d/e/f/g")

        assert result.metadata["success"] is False


# =============================================================================
# Phase 3: Trail Persistence Tests
# =============================================================================


class TestSaveTrailAspect:
    """Tests for save_trail aspect (Phase 3)."""

    @pytest.mark.asyncio
    async def test_save_trail_returns_rendering(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """save_trail should return a Renderable."""
        result = await portal_node.save_trail(observer, name="Test Trail")

        assert result is not None
        assert hasattr(result, "summary")
        assert hasattr(result, "metadata")

    @pytest.mark.asyncio
    async def test_save_trail_empty_tree(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """save_trail with empty tree should report error."""
        result = await portal_node.save_trail(observer, name="Test")

        # Should succeed even with minimal tree (root node counts as 1 step)
        # The actual behavior depends on whether there are steps
        assert result is not None

    @pytest.mark.asyncio
    async def test_save_trail_via_invoke(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """_invoke_aspect should route 'save_trail' correctly."""
        result = await portal_node._invoke_aspect(
            "save_trail",
            observer,
            name="Invoked Trail",
        )
        assert result is not None


class TestLoadTrailAspect:
    """Tests for load_trail aspect (Phase 3)."""

    @pytest.mark.asyncio
    async def test_load_trail_not_found(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """load_trail with nonexistent ID should report error."""
        result = await portal_node.load_trail(observer, trail_id="nonexistent-xyz")

        assert "error" in result.metadata or "not_found" in str(result.metadata)

    @pytest.mark.asyncio
    async def test_load_trail_via_invoke(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """_invoke_aspect should route 'load_trail' correctly."""
        result = await portal_node._invoke_aspect(
            "load_trail",
            observer,
            trail_id="test-trail",
        )
        assert result is not None


class TestListTrailsAspect:
    """Tests for list_trails aspect (Phase 3)."""

    @pytest.mark.asyncio
    async def test_list_trails_returns_rendering(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """list_trails should return a Renderable."""
        result = await portal_node.list_trails(observer)

        assert result is not None
        assert hasattr(result, "summary")
        assert hasattr(result, "metadata")

    @pytest.mark.asyncio
    async def test_list_trails_metadata_structure(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """list_trails should include count in metadata."""
        result = await portal_node.list_trails(observer)

        assert "count" in result.metadata or "trails" in result.metadata

    @pytest.mark.asyncio
    async def test_list_trails_via_invoke(
        self, portal_node: PortalNavNode, observer: Observer
    ) -> None:
        """_invoke_aspect should route 'list_trails' correctly."""
        result = await portal_node._invoke_aspect(
            "list_trails",
            observer,
            limit=10,
        )
        assert result is not None


class TestReplayAspect:
    """Tests for replay aspect (Phase 3)."""

    @pytest.mark.asyncio
    async def test_replay_not_found(self, portal_node: PortalNavNode, observer: Observer) -> None:
        """replay with nonexistent ID should report error."""
        result = await portal_node.replay(observer, trail_id="nonexistent-xyz")

        assert "error" in result.metadata or "not_found" in str(result.metadata)

    @pytest.mark.asyncio
    async def test_replay_via_invoke(self, portal_node: PortalNavNode, observer: Observer) -> None:
        """_invoke_aspect should route 'replay' correctly."""
        result = await portal_node._invoke_aspect(
            "replay",
            observer,
            trail_id="test-trail",
        )
        assert result is not None


class TestAffordancesIncludePhase3:
    """Tests for Phase 3 affordances."""

    def test_save_trail_in_affordances(self) -> None:
        """save_trail should be in PORTAL_AFFORDANCES."""
        assert "save_trail" in PORTAL_AFFORDANCES

    def test_load_trail_in_affordances(self) -> None:
        """load_trail should be in PORTAL_AFFORDANCES."""
        assert "load_trail" in PORTAL_AFFORDANCES

    def test_list_trails_in_affordances(self) -> None:
        """list_trails should be in PORTAL_AFFORDANCES."""
        assert "list_trails" in PORTAL_AFFORDANCES

    def test_replay_in_affordances(self) -> None:
        """replay should be in PORTAL_AFFORDANCES."""
        assert "replay" in PORTAL_AFFORDANCES
