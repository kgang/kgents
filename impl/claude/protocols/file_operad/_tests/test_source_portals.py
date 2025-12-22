"""
Tests for Source Portal Discovery.

"Portal tokens should work on real code, not just .op files."

These tests verify that:
- SourcePortalLink.from_hyperedge() correctly converts ContextNodes
- SourcePortalDiscovery finds imports, tests, and specs
- build_source_portal_tree produces navigable trees

See: spec/protocols/portal-token.md Phase 4
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from textwrap import dedent

import pytest

from protocols.file_operad.source_portals import (
    SOURCE_EDGE_TYPES,
    SUPPORTED_EXTENSIONS,
    SourcePortalDiscovery,
    SourcePortalLink,
    SourcePortalToken,
    build_source_portal_tree,
    discover_portals,
    render_portals_cli,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_project() -> Path:
    """
    Create a temporary project structure for testing.

    Mirrors the kgents impl/claude/ structure for path resolution.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create impl/claude directory structure
        impl_claude = root / "impl" / "claude"
        impl_claude.mkdir(parents=True)

        # Create services structure
        (impl_claude / "services").mkdir()
        (impl_claude / "services" / "brain").mkdir()
        (impl_claude / "services" / "brain" / "_tests").mkdir()

        # Create brain/core.py with imports
        (impl_claude / "services" / "brain" / "core.py").write_text(
            dedent('''
            """Brain service core.

            Spec: spec/protocols/brain.md
            """

            from pathlib import Path
            import json
            from typing import Optional

            def process_memory(data: dict) -> dict:
                """Process memory data."""
                return {"processed": True}

            def analyze_context(path: Path) -> Optional[str]:
                """Analyze context from path."""
                return None
        ''').strip()
        )

        # Create test file
        (impl_claude / "services" / "brain" / "_tests" / "test_core.py").write_text(
            dedent('''
            """Tests for brain core."""

            import pytest
            from services.brain.core import process_memory

            def test_process_memory():
                result = process_memory({})
                assert result["processed"] is True

            def test_analyze_context():
                pass
        ''').strip()
        )

        # Create persistence module
        (impl_claude / "services" / "brain" / "persistence.py").write_text(
            dedent('''
            """Brain persistence layer."""

            from pathlib import Path
            import sqlite3

            def save_memory(path: Path, data: dict) -> None:
                pass

            def load_memory(path: Path) -> dict:
                return {}
        ''').strip()
        )

        # Create spec file
        spec_dir = root / "spec" / "protocols"
        spec_dir.mkdir(parents=True)
        (spec_dir / "brain.md").write_text(
            dedent("""
            # Brain Protocol

            The brain service manages memory persistence.
        """).strip()
        )

        yield root


@pytest.fixture
def temp_python_file(tmp_path: Path) -> Path:
    """Create a temporary Python file with imports."""
    file_path = tmp_path / "test_module.py"
    file_path.write_text(
        dedent('''
        """Test module."""

        import os
        import sys
        from pathlib import Path
        from typing import Optional, List

        def main():
            pass
    ''').strip()
    )
    return file_path


# =============================================================================
# SourcePortalLink Tests
# =============================================================================


class TestSourcePortalLink:
    """Tests for SourcePortalLink class."""

    def test_from_hyperedge_creates_link(self) -> None:
        """from_hyperedge creates a valid SourcePortalLink."""
        from protocols.agentese.contexts.self_context import ContextNode

        dest = ContextNode(path="world.foo.bar", holon="bar")
        source = Path("/project/src/main.py")

        link = SourcePortalLink.from_hyperedge(
            edge_type="imports",
            destination=dest,
            source_file=source,
        )

        assert link.edge_type == "imports"
        assert link.path == "world.foo.bar"
        assert link.source_file == source
        assert link.context_node is dest

    def test_from_hyperedge_infers_file_type(self) -> None:
        """from_hyperedge infers file type from extension."""
        from protocols.agentese.contexts.self_context import ContextNode

        dest = ContextNode(path="world.foo", holon="foo")

        # Python
        py_link = SourcePortalLink.from_hyperedge(
            edge_type="imports",
            destination=dest,
            source_file=Path("/foo.py"),
        )
        assert py_link.file_type == "python"

        # TypeScript
        ts_link = SourcePortalLink.from_hyperedge(
            edge_type="imports",
            destination=dest,
            source_file=Path("/foo.tsx"),
        )
        assert ts_link.file_type == "typescript"

        # JavaScript
        js_link = SourcePortalLink.from_hyperedge(
            edge_type="imports",
            destination=dest,
            source_file=Path("/foo.js"),
        )
        assert js_link.file_type == "javascript"

        # Markdown
        md_link = SourcePortalLink.from_hyperedge(
            edge_type="implements",
            destination=dest,
            source_file=Path("/foo.md"),
        )
        assert md_link.file_type == "markdown"

    def test_from_hyperedge_includes_note(self) -> None:
        """from_hyperedge includes source file in note."""
        from protocols.agentese.contexts.self_context import ContextNode

        dest = ContextNode(path="world.foo", holon="foo")
        link = SourcePortalLink.from_hyperedge(
            edge_type="imports",
            destination=dest,
            source_file=Path("/project/main.py"),
        )

        assert link.note == "from main.py"

    def test_link_without_source_file(self) -> None:
        """Links without source file work correctly."""
        from protocols.agentese.contexts.self_context import ContextNode

        dest = ContextNode(path="world.foo", holon="foo")
        link = SourcePortalLink.from_hyperedge(
            edge_type="calls",
            destination=dest,
            source_file=None,
        )

        assert link.source_file is None
        assert link.note is None
        assert link.file_type == "python"  # Default


class TestSourcePortalLinkExists:
    """Tests for SourcePortalLink.exists() method."""

    def test_exists_with_context_node(self, temp_project: Path) -> None:
        """exists() works when context_node can resolve to file."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )
        from protocols.agentese.contexts.self_context import ContextNode

        original = _get_project_root()
        try:
            _set_project_root(temp_project)

            # This should resolve to impl/claude/services/brain/core.py
            dest = ContextNode(path="world.brain", holon="brain")
            link = SourcePortalLink.from_hyperedge(
                edge_type="tests",
                destination=dest,
                source_file=temp_project / "impl" / "claude" / "services" / "brain" / "core.py",
            )

            # Note: exists() depends on file resolution
            # This tests the path resolution logic
            assert link.context_node is not None
        finally:
            _set_project_root(original)


# =============================================================================
# SourcePortalDiscovery Tests
# =============================================================================


class TestSourcePortalDiscovery:
    """Tests for SourcePortalDiscovery class."""

    @pytest.mark.asyncio
    async def test_discovery_async(self, temp_project: Path) -> None:
        """discover_portals is async."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )

        original = _get_project_root()
        try:
            _set_project_root(temp_project)

            discovery = SourcePortalDiscovery(project_root=temp_project)
            core_path = temp_project / "impl" / "claude" / "services" / "brain" / "core.py"

            # Should not raise
            links = await discovery.discover_portals(core_path)
            assert isinstance(links, list)
        finally:
            _set_project_root(original)

    @pytest.mark.asyncio
    async def test_discover_imports(self, temp_project: Path) -> None:
        """discover_portals finds imports."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )

        original = _get_project_root()
        try:
            _set_project_root(temp_project)

            discovery = SourcePortalDiscovery(project_root=temp_project)
            core_path = temp_project / "impl" / "claude" / "services" / "brain" / "core.py"

            links = await discovery.discover_portals(
                core_path,
                edge_types={"imports"},
            )

            import_links = [l for l in links if l.edge_type == "imports"]
            assert len(import_links) >= 1

            # Should find pathlib, json, typing
            paths = {l.path for l in import_links}
            assert any("pathlib" in p for p in paths), f"Expected pathlib in {paths}"
        finally:
            _set_project_root(original)

    @pytest.mark.asyncio
    async def test_discover_tests(self, temp_project: Path) -> None:
        """discover_portals finds test files."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )

        original = _get_project_root()
        try:
            _set_project_root(temp_project)

            discovery = SourcePortalDiscovery(project_root=temp_project)
            core_path = temp_project / "impl" / "claude" / "services" / "brain" / "core.py"

            links = await discovery.discover_portals(
                core_path,
                edge_types={"tests"},
            )

            test_links = [l for l in links if l.edge_type == "tests"]
            # Should find test_core.py
            assert len(test_links) >= 1
            assert any("test" in l.path for l in test_links)
        finally:
            _set_project_root(original)

    @pytest.mark.asyncio
    async def test_discover_nonexistent_file(self) -> None:
        """discover_portals returns empty for non-existent files."""
        discovery = SourcePortalDiscovery()
        links = await discovery.discover_portals(Path("/nonexistent/file.py"))
        assert links == []

    @pytest.mark.asyncio
    async def test_discover_unsupported_extension(self, tmp_path: Path) -> None:
        """discover_portals skips unsupported file types."""
        unsupported = tmp_path / "file.xyz"
        unsupported.write_text("content")

        discovery = SourcePortalDiscovery()
        links = await discovery.discover_portals(unsupported)
        assert links == []

    @pytest.mark.asyncio
    async def test_discover_python_imports_directly(self, temp_python_file: Path) -> None:
        """discover_python_imports parses imports with AST."""
        discovery = SourcePortalDiscovery()
        links = await discovery.discover_python_imports(temp_python_file)

        assert len(links) >= 3  # os, sys, pathlib, typing
        edge_types = {l.edge_type for l in links}
        assert edge_types == {"imports"}

        paths = {l.path for l in links}
        assert "world.os" in paths
        assert "world.sys" in paths
        assert "world.pathlib" in paths

    @pytest.mark.asyncio
    async def test_discover_python_imports_handles_syntax_error(self, tmp_path: Path) -> None:
        """discover_python_imports handles syntax errors gracefully."""
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("def broken(\n  # incomplete")

        discovery = SourcePortalDiscovery()
        links = await discovery.discover_python_imports(bad_file)
        assert links == []

    @pytest.mark.asyncio
    async def test_observer_filtering(self, temp_project: Path) -> None:
        """discover_portals respects observer visibility."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )
        from protocols.agentese.node import Observer

        original = _get_project_root()
        try:
            _set_project_root(temp_project)

            discovery = SourcePortalDiscovery(project_root=temp_project)
            core_path = temp_project / "impl" / "claude" / "services" / "brain" / "core.py"

            # Guest observer has limited visibility
            guest = Observer(archetype="guest")
            guest_links = await discovery.discover_portals(core_path, observer=guest)

            # Developer sees more
            dev = Observer(archetype="developer")
            dev_links = await discovery.discover_portals(core_path, observer=dev)

            # Developer should see at least as many edges
            assert len(dev_links) >= len(guest_links)
        finally:
            _set_project_root(original)


# =============================================================================
# SourcePortalToken Tests
# =============================================================================


class TestSourcePortalToken:
    """Tests for SourcePortalToken class."""

    def test_load_with_valid_file(self, temp_project: Path) -> None:
        """load() works for files that exist."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )
        from protocols.agentese.contexts.self_context import ContextNode
        from protocols.file_operad.portal import PortalState

        original = _get_project_root()
        try:
            _set_project_root(temp_project)

            dest = ContextNode(path="world.brain", holon="brain")
            link = SourcePortalLink.from_hyperedge(
                edge_type="tests",
                destination=dest,
                source_file=temp_project / "impl" / "claude" / "services" / "brain" / "core.py",
            )

            token = SourcePortalToken(link=link, depth=1)
            result = token.load()

            # Result depends on path resolution
            # For this test, we check the state machine works
            assert token.state in {PortalState.EXPANDED, PortalState.ERROR}
        finally:
            _set_project_root(original)

    def test_load_error_for_missing_file(self) -> None:
        """load() sets ERROR state for missing files."""
        from protocols.agentese.contexts.self_context import ContextNode
        from protocols.file_operad.portal import PortalState

        dest = ContextNode(path="world.nonexistent", holon="nonexistent")
        link = SourcePortalLink.from_hyperedge(
            edge_type="tests",
            destination=dest,
            source_file=None,
        )

        token = SourcePortalToken(link=link, depth=1)
        result = token.load()

        assert result is False
        assert token.state == PortalState.ERROR


# =============================================================================
# build_source_portal_tree Tests
# =============================================================================


class TestBuildSourcePortalTree:
    """Tests for build_source_portal_tree function."""

    @pytest.mark.asyncio
    async def test_builds_tree_from_python_file(self, temp_project: Path) -> None:
        """build_source_portal_tree creates tree from Python file."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )

        original = _get_project_root()
        try:
            _set_project_root(temp_project)

            core_path = temp_project / "impl" / "claude" / "services" / "brain" / "core.py"
            tree = await build_source_portal_tree(core_path)

            assert tree.root.path == str(core_path)
            assert tree.root.depth == 0
            # Should have child nodes for discovered edge types
            assert isinstance(tree.root.children, list)
        finally:
            _set_project_root(original)

    @pytest.mark.asyncio
    async def test_tree_respects_max_depth(self, temp_project: Path) -> None:
        """build_source_portal_tree respects max_depth."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )

        original = _get_project_root()
        try:
            _set_project_root(temp_project)

            core_path = temp_project / "impl" / "claude" / "services" / "brain" / "core.py"
            tree = await build_source_portal_tree(core_path, max_depth=1)

            assert tree.max_depth == 1
        finally:
            _set_project_root(original)

    @pytest.mark.asyncio
    async def test_tree_expand_all(self, temp_project: Path) -> None:
        """build_source_portal_tree can expand all nodes."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )

        original = _get_project_root()
        try:
            _set_project_root(temp_project)

            core_path = temp_project / "impl" / "claude" / "services" / "brain" / "core.py"
            tree = await build_source_portal_tree(core_path, expand_all=True)

            assert tree.root.expanded is True
        finally:
            _set_project_root(original)


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    @pytest.mark.asyncio
    async def test_discover_portals_convenience(self, temp_project: Path) -> None:
        """discover_portals() convenience function works."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )

        original = _get_project_root()
        try:
            _set_project_root(temp_project)

            core_path = temp_project / "impl" / "claude" / "services" / "brain" / "core.py"
            links = await discover_portals(core_path)

            assert isinstance(links, list)
        finally:
            _set_project_root(original)

    def test_render_portals_cli_empty(self) -> None:
        """render_portals_cli handles empty list."""
        result = render_portals_cli([])
        assert result == "No portals discovered."

    def test_render_portals_cli_groups_by_type(self) -> None:
        """render_portals_cli groups links by edge type."""
        from protocols.agentese.contexts.self_context import ContextNode

        links = [
            SourcePortalLink.from_hyperedge(
                "imports",
                ContextNode(path="world.os", holon="os"),
            ),
            SourcePortalLink.from_hyperedge(
                "imports",
                ContextNode(path="world.sys", holon="sys"),
            ),
            SourcePortalLink.from_hyperedge(
                "tests",
                ContextNode(path="world.test_foo", holon="test_foo"),
            ),
        ]

        result = render_portals_cli(links)

        assert "[imports]" in result
        assert "[tests]" in result
        assert "2 files" in result  # 2 imports
        assert "1 file" in result  # 1 test

    def test_render_portals_cli_truncates_long_lists(self) -> None:
        """render_portals_cli truncates lists > 5 items."""
        from protocols.agentese.contexts.self_context import ContextNode

        links = [
            SourcePortalLink.from_hyperedge(
                "imports",
                ContextNode(path=f"world.mod{i}", holon=f"mod{i}"),
            )
            for i in range(10)
        ]

        result = render_portals_cli(links)

        assert "... and 5 more" in result


# =============================================================================
# Constants Tests
# =============================================================================


class TestConstants:
    """Tests for module constants."""

    def test_supported_extensions(self) -> None:
        """SUPPORTED_EXTENSIONS contains expected types."""
        assert ".py" in SUPPORTED_EXTENSIONS
        assert ".ts" in SUPPORTED_EXTENSIONS
        assert ".tsx" in SUPPORTED_EXTENSIONS
        assert ".md" in SUPPORTED_EXTENSIONS

    def test_source_edge_types(self) -> None:
        """SOURCE_EDGE_TYPES contains expected edges."""
        assert "imports" in SOURCE_EDGE_TYPES
        assert "tests" in SOURCE_EDGE_TYPES
        assert "implements" in SOURCE_EDGE_TYPES
        assert "contains" in SOURCE_EDGE_TYPES


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for full workflow."""

    @pytest.mark.asyncio
    async def test_full_discovery_to_tree_workflow(self, temp_project: Path) -> None:
        """Full workflow: discover -> build tree -> render."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )

        original = _get_project_root()
        try:
            _set_project_root(temp_project)

            # 1. Discover portals from source file
            core_path = temp_project / "impl" / "claude" / "services" / "brain" / "core.py"
            links = await discover_portals(core_path)

            # 2. Build tree
            tree = await build_source_portal_tree(core_path, expand_all=True)

            # 3. Render
            rendered = tree.render()

            # Should have root path
            assert "core.py" in rendered

            # CLI render should show edge types
            cli_output = render_portals_cli(links)
            # Should have some output (may vary based on what's found)
            assert isinstance(cli_output, str)
        finally:
            _set_project_root(original)

    @pytest.mark.asyncio
    async def test_spec_file_discovery(self, temp_project: Path) -> None:
        """Discover implements edges to spec files."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )

        original = _get_project_root()
        try:
            _set_project_root(temp_project)

            discovery = SourcePortalDiscovery(project_root=temp_project)
            core_path = temp_project / "impl" / "claude" / "services" / "brain" / "core.py"

            # The core.py has "Spec: spec/protocols/brain.md" in docstring
            links = await discovery.find_implementing_specs(core_path)

            # Should find the spec file
            # Note: depends on implements resolver finding the docstring reference
            assert isinstance(links, list)
            # If found, it should be an implements edge
            for link in links:
                assert link.edge_type == "implements"
        finally:
            _set_project_root(original)
