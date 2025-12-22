"""
Tests for Portal Bridge.

Verifies the bridge between Outline model and PortalTree infrastructure.

Teaching:
    gotcha: The bridge coordinates TWO different PortalToken implementations.
            Tests verify that both stay in sync.
            (Evidence: test_sync_invariant)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from protocols.context.outline import (
    Outline,
    OutlineNode,
    PortalToken,
    SnippetType,
    TextSnippet,
    create_outline,
)
from protocols.context.portal_bridge import (
    BridgeState,
    OutlinePortalBridge,
    PortalExpansionResult,
    create_bridge,
    create_bridge_from_file,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_outline() -> Outline:
    """Create a sample outline with portals."""
    outline = create_outline(root_text="# Investigation", observer_id="test")

    # Add a portal node
    portal = PortalToken(
        source_path="world.auth",
        edge_type="tests",
        destinations=["test_auth.py", "test_login.py"],
    )
    portal_node = OutlineNode(portal=portal, path="root.0")
    outline.root.add_child(portal_node)

    return outline


@pytest.fixture
def bridge(sample_outline: Outline) -> OutlinePortalBridge:
    """Create a bridge with the sample outline."""
    return OutlinePortalBridge(outline=sample_outline, observer_id="test")


# =============================================================================
# Basic Tests
# =============================================================================


class TestOutlinePortalBridge:
    """Tests for OutlinePortalBridge."""

    def test_creation_with_outline(self, sample_outline: Outline) -> None:
        """Bridge can be created with existing outline."""
        bridge = OutlinePortalBridge(outline=sample_outline)
        assert bridge.outline is sample_outline

    def test_creation_without_outline(self) -> None:
        """Bridge creates new outline if none provided."""
        bridge = OutlinePortalBridge(observer_id="test")
        assert bridge.outline is not None
        assert bridge.outline.observer_id == "test"

    def test_portal_tree_initially_none(self, bridge: OutlinePortalBridge) -> None:
        """Portal tree is None until set."""
        assert bridge.portal_tree is None

    def test_set_portal_tree(self, bridge: OutlinePortalBridge) -> None:
        """Can set portal tree."""

        # Create a mock portal tree
        class MockPortalTree:
            pass

        mock_tree = MockPortalTree()
        bridge.set_portal_tree(mock_tree)  # type: ignore
        assert bridge.portal_tree is mock_tree


class TestExpand:
    """Tests for expand operation."""

    @pytest.mark.asyncio
    async def test_expand_nonexistent_portal(self, bridge: OutlinePortalBridge) -> None:
        """Expand returns failure for nonexistent portal."""
        result = await bridge.expand("nonexistent/path")
        assert not result.success
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_expand_existing_portal(self, bridge: OutlinePortalBridge) -> None:
        """Expand succeeds for existing portal."""
        result = await bridge.expand("root.0")
        assert result.success
        assert result.portal_path == "root.0"
        assert result.edge_type == "tests"

    @pytest.mark.asyncio
    async def test_expand_updates_portal_state(self, bridge: OutlinePortalBridge) -> None:
        """Expand updates portal.expanded state."""
        # Portal starts collapsed
        node = bridge.outline.find_node("root.0")
        assert node is not None
        assert not node.portal.expanded

        # Expand
        await bridge.expand("root.0")

        # Portal now expanded
        assert node.portal.expanded

    @pytest.mark.asyncio
    async def test_expand_records_trail_step(self, bridge: OutlinePortalBridge) -> None:
        """Expand records a trail step."""
        initial_steps = bridge.outline.steps_taken

        await bridge.expand("root.0")

        assert bridge.outline.steps_taken == initial_steps + 1
        assert len(bridge.outline.trail_steps) > 0
        last_step = bridge.outline.trail_steps[-1]
        assert last_step["action"] == "expand"
        assert last_step["node_path"] == "root.0"

    @pytest.mark.asyncio
    async def test_expand_idempotent(self, bridge: OutlinePortalBridge) -> None:
        """Expanding already expanded portal succeeds without error."""
        # Expand first time
        result1 = await bridge.expand("root.0")
        assert result1.success

        # Expand second time (idempotent)
        result2 = await bridge.expand("root.0")
        assert result2.success

    @pytest.mark.asyncio
    async def test_expand_returns_content(self, bridge: OutlinePortalBridge) -> None:
        """Expand returns loaded content."""
        result = await bridge.expand("root.0")
        assert result.success
        assert result.content is not None
        # Content dict has keys for destinations
        assert len(result.content) == 2  # test_auth.py, test_login.py


class TestCollapse:
    """Tests for collapse operation."""

    @pytest.mark.asyncio
    async def test_collapse_nonexistent(self, bridge: OutlinePortalBridge) -> None:
        """Collapse returns False for nonexistent portal."""
        result = await bridge.collapse("nonexistent/path")
        assert not result

    @pytest.mark.asyncio
    async def test_collapse_already_collapsed(self, bridge: OutlinePortalBridge) -> None:
        """Collapse on already collapsed portal returns True (idempotent)."""
        result = await bridge.collapse("root.0")
        assert result  # Success (already collapsed)

    @pytest.mark.asyncio
    async def test_collapse_after_expand(self, bridge: OutlinePortalBridge) -> None:
        """Collapse after expand updates state."""
        # Expand first
        await bridge.expand("root.0")
        node = bridge.outline.find_node("root.0")
        assert node.portal.expanded

        # Collapse
        result = await bridge.collapse("root.0")
        assert result
        assert not node.portal.expanded

    @pytest.mark.asyncio
    async def test_collapse_records_trail(self, bridge: OutlinePortalBridge) -> None:
        """Collapse records a trail step."""
        # Expand first
        await bridge.expand("root.0")
        initial_steps = bridge.outline.steps_taken

        # Collapse
        await bridge.collapse("root.0")

        assert bridge.outline.steps_taken == initial_steps + 1
        last_step = bridge.outline.trail_steps[-1]
        assert last_step["action"] == "collapse"


class TestNavigate:
    """Tests for navigate operation."""

    @pytest.mark.asyncio
    async def test_navigate_to_existing(self, bridge: OutlinePortalBridge) -> None:
        """Navigate to existing node succeeds."""
        result = await bridge.navigate("root.0")
        assert result

    @pytest.mark.asyncio
    async def test_navigate_to_nonexistent(self, bridge: OutlinePortalBridge) -> None:
        """Navigate to nonexistent node fails."""
        result = await bridge.navigate("nonexistent")
        assert not result

    @pytest.mark.asyncio
    async def test_navigate_records_trail(self, bridge: OutlinePortalBridge) -> None:
        """Navigate records a trail step."""
        initial_steps = bridge.outline.steps_taken

        await bridge.navigate("root.0")

        assert bridge.outline.steps_taken == initial_steps + 1
        last_step = bridge.outline.trail_steps[-1]
        assert last_step["action"] == "navigate"


class TestCreateLens:
    """Tests for create_lens operation."""

    @pytest.mark.asyncio
    async def test_lens_nonexistent_file(self, bridge: OutlinePortalBridge) -> None:
        """Creating lens for nonexistent file returns None."""
        result = await bridge.create_lens("/nonexistent/file.py", "some_function")
        assert result is None

    @pytest.mark.asyncio
    async def test_lens_function_focus(self, bridge: OutlinePortalBridge, tmp_path: Path) -> None:
        """Creating lens with function focus."""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    return 'world'\n")

        result = await bridge.create_lens(str(test_file), "hello")
        # Lens creation depends on function being found
        # May return None if AST parsing fails

    @pytest.mark.asyncio
    async def test_lens_class_focus(self, bridge: OutlinePortalBridge, tmp_path: Path) -> None:
        """Creating lens with class focus."""
        test_file = tmp_path / "test.py"
        test_file.write_text("class Foo:\n    pass\n")

        result = await bridge.create_lens(str(test_file), "class:Foo")
        # May return None if class not found

    @pytest.mark.asyncio
    async def test_lens_lines_focus(self, bridge: OutlinePortalBridge, tmp_path: Path) -> None:
        """Creating lens with lines focus."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3\nline4\n")

        result = await bridge.create_lens(str(test_file), "lines:1-2")
        assert result is not None
        assert "line1" in result.visible_content
        assert "line2" in result.visible_content


class TestEventSubscription:
    """Tests for event subscription."""

    @pytest.mark.asyncio
    async def test_expand_emits_event(self, bridge: OutlinePortalBridge) -> None:
        """Expand emits event to subscribers."""
        events_received: list[Any] = []

        def on_expand(event: Any) -> None:
            events_received.append(event)

        bridge.subscribe_expand(on_expand)
        await bridge.expand("root.0")

        # Event should have been emitted
        assert len(events_received) == 1

    @pytest.mark.asyncio
    async def test_collapse_emits_event(self, bridge: OutlinePortalBridge) -> None:
        """Collapse emits event to subscribers."""
        events_received: list[Any] = []

        def on_collapse(event: Any) -> None:
            events_received.append(event)

        bridge.subscribe_collapse(on_collapse)

        # Expand first, then collapse
        await bridge.expand("root.0")
        await bridge.collapse("root.0")

        assert len(events_received) == 1


class TestGetState:
    """Tests for get_state."""

    def test_get_state_returns_bridge_state(self, bridge: OutlinePortalBridge) -> None:
        """get_state returns BridgeState."""
        state = bridge.get_state()
        assert isinstance(state, BridgeState)
        assert state.outline is bridge.outline
        assert state.portal_tree is None


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_bridge_empty(self) -> None:
        """create_bridge with no args creates empty bridge."""
        bridge = create_bridge()
        assert bridge.outline is not None
        assert bridge.portal_tree is None

    def test_create_bridge_with_observer(self) -> None:
        """create_bridge with observer_id."""
        bridge = create_bridge(observer_id="test-user")
        assert bridge.observer_id == "test-user"
        assert bridge.outline.observer_id == "test-user"

    def test_create_bridge_with_outline(self, sample_outline: Outline) -> None:
        """create_bridge with existing outline."""
        bridge = create_bridge(outline=sample_outline)
        assert bridge.outline is sample_outline

    def test_create_bridge_from_file_nonexistent(self) -> None:
        """create_bridge_from_file with nonexistent file."""
        bridge = create_bridge_from_file("/nonexistent/file.md")
        assert bridge.outline is not None  # Creates empty outline

    def test_create_bridge_from_file_exists(self, tmp_path: Path) -> None:
        """create_bridge_from_file with existing file."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test Outline\n\nSome content here.")

        bridge = create_bridge_from_file(test_file)
        assert bridge.outline is not None
        # Root should contain file content
        assert "Test Outline" in bridge.outline.root.visible_text


class TestPortalExpansionResult:
    """Tests for PortalExpansionResult."""

    def test_to_trail_step(self) -> None:
        """to_trail_step converts to dictionary."""
        result = PortalExpansionResult(
            success=True,
            portal_path="root.0",
            edge_type="tests",
            depth=1,
            parent_path="root",
        )

        step = result.to_trail_step()

        assert step["action"] == "expand"
        assert step["node_path"] == "root.0"
        assert step["edge_type"] == "tests"
        assert step["depth"] == 1
        assert "timestamp" in step


class TestSyncInvariant:
    """Tests for synchronization between Outline and PortalTree."""

    @pytest.mark.asyncio
    async def test_expand_syncs_both(self, bridge: OutlinePortalBridge) -> None:
        """Expanding via bridge updates both Outline and PortalTree."""

        # Create a mock portal tree that tracks calls
        class MockPortalTree:
            expanded_paths: list[list[str]] = []

            def expand(self, path_segments: list[str]) -> bool:
                self.expanded_paths.append(path_segments)
                return True

        mock_tree = MockPortalTree()
        bridge.set_portal_tree(mock_tree)  # type: ignore

        # Expand via bridge
        await bridge.expand("root.0")

        # Both should be updated
        node = bridge.outline.find_node("root.0")
        assert node.portal.expanded  # Outline updated
        assert ["root.0"] in mock_tree.expanded_paths  # PortalTree updated

    @pytest.mark.asyncio
    async def test_collapse_syncs_both(self, bridge: OutlinePortalBridge) -> None:
        """Collapsing via bridge updates both Outline and PortalTree."""

        class MockPortalTree:
            collapsed_paths: list[list[str]] = []

            def expand(self, path_segments: list[str]) -> bool:
                return True

            def collapse(self, path_segments: list[str]) -> bool:
                self.collapsed_paths.append(path_segments)
                return True

        mock_tree = MockPortalTree()
        bridge.set_portal_tree(mock_tree)  # type: ignore

        # Expand then collapse
        await bridge.expand("root.0")
        await bridge.collapse("root.0")

        # Both should be updated
        node = bridge.outline.find_node("root.0")
        assert not node.portal.expanded  # Outline updated
        assert ["root.0"] in mock_tree.collapsed_paths  # PortalTree updated


# =============================================================================
# Phase 3: Token Parsing Tests
# =============================================================================


class TestTokenParsing:
    """Tests for Phase 3 live token parsing integration."""

    def test_parse_content_tokens_empty(self, bridge: OutlinePortalBridge) -> None:
        """Parsing empty content returns empty lists."""
        tokens, paths, links = bridge._parse_content_tokens({})
        assert tokens == []
        assert paths == []
        assert links == []

    def test_parse_content_tokens_plain_text(self, bridge: OutlinePortalBridge) -> None:
        """Parsing plain text returns no tokens."""
        content = {"file.txt": "Hello world\nNo tokens here"}
        tokens, paths, links = bridge._parse_content_tokens(content)
        assert tokens == []
        assert paths == []
        assert links == []

    def test_parse_content_discovers_agentese_paths(self, bridge: OutlinePortalBridge) -> None:
        """Parser discovers AGENTESE paths in content."""
        content = {
            "doc.md": "See `world.auth.validate` for details.\nAlso check `self.context.trail`."
        }
        tokens, paths, links = bridge._parse_content_tokens(content)

        assert len(paths) == 2
        assert "world.auth.validate" in paths
        assert "self.context.trail" in paths

    def test_parse_content_discovers_evidence_links(self, bridge: OutlinePortalBridge) -> None:
        """Parser discovers evidence links in content."""
        content = {"investigation.md": "📎 Found bug in auth\n📎 Confirmed fix (strong)"}
        tokens, paths, links = bridge._parse_content_tokens(content)

        assert len(links) == 2
        assert "Found bug in auth" in links
        assert "Confirmed fix" in links

    def test_parse_content_discovers_portals(self, bridge: OutlinePortalBridge) -> None:
        """Parser discovers nested portal tokens in content."""
        content = {"outline.md": "▶ [tests] test_auth.py\n▼ [imports] dependencies"}
        tokens, paths, links = bridge._parse_content_tokens(content)

        # Should find portal tokens
        from protocols.context.parser import TokenType

        portal_tokens = [
            t
            for t in tokens
            if t.token_type in (TokenType.PORTAL_COLLAPSED, TokenType.PORTAL_EXPANDED)
        ]
        assert len(portal_tokens) == 2

    def test_expansion_result_includes_tokens(self, bridge: OutlinePortalBridge) -> None:
        """PortalExpansionResult includes discovered tokens after expansion."""
        # Note: This tests the integration, but content is mocked
        # so we check the structure is correct
        result = PortalExpansionResult(
            success=True,
            portal_path="test",
            discovered_tokens=[],
            agentese_paths=["world.foo"],
            evidence_links=["claim"],
        )

        assert result.agentese_paths == ["world.foo"]
        assert result.evidence_links == ["claim"]
        step = result.to_trail_step()
        assert "discovered_tokens" in step
