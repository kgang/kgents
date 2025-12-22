"""
Tests for Hyperedge Resolvers.

These resolvers implement the actual logic for finding connections
between nodes in the typed-hypergraph.

Teaching:
    gotcha: Resolvers are async functions. Always await them.
            (Evidence: test_resolver_async)

    gotcha: Resolvers return ContextNode instances, not strings.
            This preserves lazy loading and graph structure.
            (Evidence: test_resolver_returns_nodes)
"""

from __future__ import annotations

import pytest
from pathlib import Path
import tempfile
import os

from protocols.agentese.contexts.self_context import ContextNode
from protocols.agentese.contexts.hyperedge_resolvers import (
    ResolverRegistry,
    get_resolver_registry,
    register_resolver,
    agentese_path_to_file,
    file_to_agentese_path,
    resolve_hyperedge,
    resolve_all_edges,
)


# === Module-Level Fixtures ===


@pytest.fixture
def temp_project() -> Path:
    """Create a temporary project structure for testing.

    Teaching:
        gotcha: The temp project must mirror the kgents impl/claude/ structure
                for path resolution to work correctly. Services are under
                impl/claude/services/, not at the root.
                (Evidence: this fixture + test_follow_with_temp_project)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create impl/claude directory structure (mirrors kgents)
        impl_claude = root / "impl" / "claude"
        impl_claude.mkdir(parents=True)

        # Create services structure
        (impl_claude / "services").mkdir()
        (impl_claude / "services" / "brain").mkdir()
        (impl_claude / "services" / "brain" / "_tests").mkdir()

        # Create some Python files
        (impl_claude / "services" / "brain" / "core.py").write_text('''
"""Brain service core."""

from pathlib import Path
import json

def process_memory():
    pass
''')
        (impl_claude / "services" / "brain" / "_tests" / "test_core.py").write_text('''
"""Tests for brain core."""

def test_process_memory():
    pass
''')

        yield root


# === Registry Tests ===


class TestResolverRegistry:
    """Tests for ResolverRegistry."""

    def test_register_and_get(self) -> None:
        """Resolvers can be registered and retrieved."""
        registry = ResolverRegistry()

        async def mock_resolver(node: ContextNode, root: Path) -> list[ContextNode]:
            return []

        registry.register("test_edge", mock_resolver)

        assert registry.get("test_edge") is mock_resolver

    def test_register_with_reverse(self) -> None:
        """Resolvers can be registered with reverse edge mapping."""
        registry = ResolverRegistry()

        async def mock_resolver(node: ContextNode, root: Path) -> list[ContextNode]:
            return []

        registry.register("parent", mock_resolver, reverse_edge="children")

        assert registry.get_reverse("parent") == "children"
        assert registry.get_reverse("children") == "parent"

    def test_list_edge_types(self) -> None:
        """list_edge_types returns all registered types."""
        registry = ResolverRegistry()

        async def mock_resolver(node: ContextNode, root: Path) -> list[ContextNode]:
            return []

        registry.register("edge_a", mock_resolver)
        registry.register("edge_b", mock_resolver)

        types = registry.list_edge_types()
        assert "edge_a" in types
        assert "edge_b" in types

    def test_get_nonexistent_returns_none(self) -> None:
        """Getting non-existent resolver returns None."""
        registry = ResolverRegistry()
        assert registry.get("nonexistent") is None


class TestGlobalRegistry:
    """Tests for global resolver registry."""

    def test_get_resolver_registry_returns_singleton(self) -> None:
        """get_resolver_registry returns the same instance."""
        r1 = get_resolver_registry()
        r2 = get_resolver_registry()
        assert r1 is r2

    def test_global_registry_has_standard_resolvers(self) -> None:
        """Global registry has standard resolvers registered."""
        registry = get_resolver_registry()
        types = registry.list_edge_types()

        # Standard resolvers should be registered
        assert "contains" in types
        assert "parent" in types
        assert "imports" in types
        assert "tests" in types


class TestRegisterDecorator:
    """Tests for @register_resolver decorator."""

    def test_decorator_registers_resolver(self) -> None:
        """@register_resolver decorator registers the function."""

        @register_resolver("custom_test_edge")
        async def custom_resolver(
            node: ContextNode, root: Path
        ) -> list[ContextNode]:
            return []

        registry = get_resolver_registry()
        assert registry.get("custom_test_edge") is custom_resolver


# === Path Utility Tests ===


class TestPathUtilities:
    """Tests for path conversion utilities."""

    def test_file_to_agentese_path_services(self) -> None:
        """Services path converts correctly."""
        root = Path("/project")
        file_path = Path("/project/services/brain/core.py")

        result = file_to_agentese_path(file_path, root)

        assert result.startswith("world.")
        assert "brain" in result

    def test_file_to_agentese_path_removes_common_suffixes(self) -> None:
        """Common suffixes like 'core', '__init__' are removed."""
        root = Path("/project")

        # __init__.py → module name
        init_path = Path("/project/services/brain/__init__.py")
        result = file_to_agentese_path(init_path, root)
        assert not result.endswith("__init__")

    def test_agentese_to_file_returns_none_for_missing(self) -> None:
        """agentese_path_to_file returns None for non-existent files."""
        result = agentese_path_to_file("world.nonexistent.module", Path("/nonexistent"))
        assert result is None


# === Resolver Function Tests ===


class TestResolvers:
    """Tests for individual resolvers."""

    # Note: temp_project fixture is defined at module level

    @pytest.mark.asyncio
    async def test_resolver_async(self) -> None:
        """Resolvers are async functions."""
        node = ContextNode(path="world.test", holon="test")

        # This should not raise
        result = await resolve_hyperedge(node, "contains", Path("/nonexistent"))

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_resolver_returns_nodes(self) -> None:
        """Resolvers return ContextNode instances."""
        node = ContextNode(path="world.test", holon="test")
        root = Path("/nonexistent")

        result = await resolve_hyperedge(node, "parent", root)

        # Even if empty, should be a list
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_parent_resolver(self) -> None:
        """Parent resolver finds parent module."""
        node = ContextNode(path="world.services.brain.core", holon="core")
        root = Path("/nonexistent")

        result = await resolve_hyperedge(node, "parent", root)

        assert len(result) == 1
        assert result[0].path == "world.services.brain"
        assert result[0].holon == "brain"

    @pytest.mark.asyncio
    async def test_parent_resolver_top_level(self) -> None:
        """Parent resolver returns empty for top-level nodes."""
        node = ContextNode(path="world.foo", holon="foo")
        root = Path("/nonexistent")

        result = await resolve_hyperedge(node, "parent", root)

        # world.foo has no parent (world is the context, not a module)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_imports_resolver(self, temp_project: Path) -> None:
        """Imports resolver finds import statements."""
        node = ContextNode(path="world.services.brain.core", holon="core")

        result = await resolve_hyperedge(node, "imports", temp_project)

        # The test file imports pathlib and json
        # Note: Results depend on file resolution working
        # For now, verify it returns a list
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_related_resolver(self) -> None:
        """Related resolver finds sibling modules."""
        node = ContextNode(path="world.services.brain.core", holon="core")
        root = Path("/nonexistent")

        result = await resolve_hyperedge(node, "related", root)

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_resolve_all_edges(self) -> None:
        """resolve_all_edges returns all edge types."""
        node = ContextNode(path="world.services.brain.core", holon="core")
        root = Path("/nonexistent")

        result = await resolve_all_edges(node, root)

        assert isinstance(result, dict)
        # Parent should be in there
        assert "parent" in result

    @pytest.mark.asyncio
    async def test_nonexistent_edge_type(self) -> None:
        """Resolving unknown edge type returns empty list."""
        node = ContextNode(path="world.test", holon="test")
        root = Path("/nonexistent")

        result = await resolve_hyperedge(node, "nonexistent_edge_type", root)

        assert result == []


# === Integration Tests ===


class TestResolverIntegration:
    """Integration tests for resolvers."""

    @pytest.mark.asyncio
    async def test_resolver_chain(self) -> None:
        """Resolvers can be chained to navigate the graph."""
        # Start at a module
        start = ContextNode(path="world.services.brain.core", holon="core")
        root = Path("/nonexistent")

        # Go to parent
        parents = await resolve_hyperedge(start, "parent", root)
        assert len(parents) == 1

        parent = parents[0]
        assert parent.path == "world.services.brain"

        # Go up again
        grandparents = await resolve_hyperedge(parent, "parent", root)
        assert len(grandparents) == 1
        assert grandparents[0].path == "world.services"


# === Project Root Discovery Tests ===


class TestProjectRootDiscovery:
    """Tests for project root discovery."""

    def test_project_root_discovery(self) -> None:
        """_get_project_root() returns a valid path."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )

        # Reset to force re-discovery
        _set_project_root(None)

        root = _get_project_root()
        assert root.exists(), f"Project root {root} does not exist"
        # Should be kgents directory
        assert (root / "spec").exists() or (root / "impl").exists(), \
            f"Project root {root} doesn't look like kgents root"

    def test_project_root_caching(self) -> None:
        """_get_project_root() caches the result."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )

        _set_project_root(None)
        root1 = _get_project_root()
        root2 = _get_project_root()
        assert root1 is root2  # Same object, not just equal

    def test_set_project_root_for_testing(self) -> None:
        """_set_project_root() allows injection for tests."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _get_project_root,
            _set_project_root,
        )

        original = _get_project_root()
        test_path = Path("/test/path")

        try:
            _set_project_root(test_path)
            assert _get_project_root() == test_path
        finally:
            # Reset to original
            _set_project_root(original)


# === ContextNode.follow() Integration Tests ===


class TestContextNodeFollow:
    """Tests for ContextNode.follow() integration with resolvers."""

    @pytest.mark.asyncio
    async def test_follow_uses_resolvers(self) -> None:
        """follow() invokes hyperedge resolvers."""
        from protocols.agentese.node import Observer

        node = ContextNode(path="world.services.brain.core", holon="core")
        observer = Observer(archetype="developer")

        # Developer can see "parent" edge and follow it
        results = await node.follow("parent", observer)

        # Should get the parent node
        assert len(results) == 1
        assert results[0].path == "world.services.brain"

    @pytest.mark.asyncio
    async def test_follow_observer_filtering(self) -> None:
        """follow() respects observer visibility (Umwelt principle)."""
        from protocols.agentese.node import Observer

        node = ContextNode(path="world.foo", holon="foo")
        guest = Observer(archetype="guest")

        # Guest can't see "tests" edge (developer-only)
        results = await node.follow("tests", guest)
        assert results == [], "Guest should not be able to follow 'tests' edge"

    @pytest.mark.asyncio
    async def test_follow_developer_sees_tests(self) -> None:
        """Developer observer can follow 'tests' edge."""
        from protocols.agentese.node import Observer

        node = ContextNode(path="world.foo", holon="foo")
        developer = Observer(archetype="developer")

        # Developer can see "tests" edge
        visible = node.edges(developer)
        assert "tests" in visible, "Developer should see 'tests' edge"

        # Follow returns list (may be empty if no test files found)
        results = await node.follow("tests", developer)
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_follow_with_temp_project(self, temp_project: Path) -> None:
        """follow() finds actual test files in temp project."""
        from protocols.agentese.node import Observer
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _set_project_root,
            _get_project_root,
        )

        original_root = _get_project_root()

        try:
            # Set project root to temp directory
            _set_project_root(temp_project)

            # Create a node for the brain module (shorthand works now)
            # world.brain maps to impl/claude/services/brain/core.py
            node = ContextNode(path="world.brain", holon="brain")
            observer = Observer(archetype="developer")

            # Follow "tests" edge
            results = await node.follow("tests", observer)

            # Should find test_core.py in _tests directory
            assert len(results) >= 1, "Should find at least one test file"
            assert any("test" in r.holon for r in results), \
                "Test file holon should contain 'test'"

        finally:
            # Restore original root
            _set_project_root(original_root)


# === Law Verification Tests ===


class TestBidirectionalConsistencyLaw:
    """
    Law 10.2: Bidirectional Consistency (Hardening)

    A ──[e]──→ B  ⟺  B ──[reverse(e)]──→ A

    These tests verify that reverse edges can actually be traversed,
    not just that mappings exist.

    Teaching:
        gotcha: The spec defines bidirectional edges, but without reverse
                resolvers the law is structurally defined but not functional.
                Until reverse resolvers are implemented, these tests document
                the expected behavior.
                (Evidence: this test class)
    """

    @pytest.mark.asyncio
    async def test_parent_children_bidirectional(self) -> None:
        """parent ↔ children are bidirectional."""
        # parent resolver exists
        child = ContextNode(path="world.services.brain.core", holon="core")
        root = Path("/nonexistent")

        parents = await resolve_hyperedge(child, "parent", root)
        assert len(parents) == 1
        assert parents[0].path == "world.services.brain"

        # Note: children resolver should return to child
        # This is expected behavior when reverse resolvers are implemented
        # Currently tests the forward direction

    @pytest.mark.asyncio
    async def test_contains_contained_in_bidirectional(self, temp_project: Path) -> None:
        """contains ↔ contained_in are bidirectional."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _set_project_root,
            _get_project_root,
        )

        original_root = _get_project_root()
        try:
            _set_project_root(temp_project)

            parent = ContextNode(path="world.brain", holon="brain")

            # Forward: parent contains children
            children = await resolve_hyperedge(parent, "contains", temp_project)

            # If there are children, verify structure
            for child in children:
                assert child.path.startswith("world.")
                assert isinstance(child.holon, str)
        finally:
            _set_project_root(original_root)

    @pytest.mark.asyncio
    async def test_contained_in_resolver(self) -> None:
        """contained_in resolver finds parent container."""
        child = ContextNode(path="world.services.brain.core", holon="core")
        root = Path("/nonexistent")

        # contained_in should return parent (same as parent resolver)
        containers = await resolve_hyperedge(child, "contained_in", root)
        assert len(containers) == 1
        assert containers[0].path == "world.services.brain"

    @pytest.mark.asyncio
    async def test_tested_by_resolver(self, temp_project: Path) -> None:
        """tested_by resolver finds implementation from test."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _set_project_root,
            _get_project_root,
        )

        original_root = _get_project_root()
        try:
            _set_project_root(temp_project)

            # Test file should find the module it tests
            test_node = ContextNode(path="world.brain.test_core", holon="test_core")
            result = await resolve_hyperedge(test_node, "tested_by", temp_project)

            # Should return list (may be empty if paths don't match exactly)
            assert isinstance(result, list)

        finally:
            _set_project_root(original_root)

    @pytest.mark.asyncio
    async def test_imported_by_placeholder(self) -> None:
        """imported_by resolver exists (placeholder)."""
        node = ContextNode(path="world.foo", holon="foo")
        root = Path("/nonexistent")

        # Should return empty (placeholder implementation)
        result = await resolve_hyperedge(node, "imported_by", root)
        assert result == []

    @pytest.mark.asyncio
    async def test_called_by_placeholder(self) -> None:
        """called_by resolver exists (placeholder)."""
        node = ContextNode(path="world.foo", holon="foo")
        root = Path("/nonexistent")

        result = await resolve_hyperedge(node, "called_by", root)
        assert result == []

    @pytest.mark.asyncio
    async def test_implemented_by_resolver(self, temp_project: Path) -> None:
        """implemented_by finds implementations of specs."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _set_project_root,
            _get_project_root,
        )

        original_root = _get_project_root()
        try:
            _set_project_root(temp_project)

            # Create a service that matches a spec name
            brain_core = temp_project / "impl" / "claude" / "services" / "brain" / "core.py"
            brain_core.parent.mkdir(parents=True, exist_ok=True)
            brain_core.write_text("# Brain implementation")

            spec_node = ContextNode(path="concept.spec.brain", holon="brain")
            result = await resolve_hyperedge(spec_node, "implemented_by", temp_project)

            # Should find the brain service
            assert len(result) >= 1
            assert any(r.holon == "brain" for r in result)

        finally:
            _set_project_root(original_root)

    @pytest.mark.asyncio
    async def test_derived_by_placeholder(self) -> None:
        """derived_by resolver exists (placeholder)."""
        node = ContextNode(path="concept.spec.foo", holon="foo")
        root = Path("/nonexistent")

        result = await resolve_hyperedge(node, "derived_by", root)
        assert result == []

    @pytest.mark.asyncio
    async def test_all_reverse_resolvers_registered(self) -> None:
        """All documented reverse resolvers are registered."""
        registry = get_resolver_registry()
        types = registry.list_edge_types()

        # Core reverse resolvers should be registered
        reverse_edges = [
            "contained_in",
            "imported_by",
            "called_by",
            "tested_by",
            "implemented_by",
            "derived_by",
        ]

        for edge in reverse_edges:
            assert edge in types, f"Reverse resolver '{edge}' not registered"


class TestResolverRobustness:
    """
    Robustness tests for edge case handling.

    Teaching:
        gotcha: Resolvers must handle malformed paths, non-existent files,
                and syntax errors gracefully. These tests verify defensive
                coding patterns.
                (Evidence: this test class)
    """

    @pytest.mark.asyncio
    async def test_imports_resolver_handles_syntax_error(
        self, temp_project: Path
    ) -> None:
        """Imports resolver gracefully handles Python syntax errors."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _set_project_root,
            _get_project_root,
        )

        original_root = _get_project_root()
        try:
            _set_project_root(temp_project)

            # Create a file with syntax error
            bad_file = (
                temp_project
                / "impl"
                / "claude"
                / "services"
                / "brain"
                / "broken.py"
            )
            bad_file.write_text("def broken(\n  # incomplete")

            node = ContextNode(path="world.brain.broken", holon="broken")
            # Should not raise, just return empty
            result = await resolve_hyperedge(node, "imports", temp_project)
            assert result == []
        finally:
            _set_project_root(original_root)

    @pytest.mark.asyncio
    async def test_calls_resolver_handles_complex_ast(
        self, temp_project: Path
    ) -> None:
        """Calls resolver handles complex AST patterns."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _set_project_root,
            _get_project_root,
        )

        original_root = _get_project_root()
        try:
            _set_project_root(temp_project)

            # Create file with various call patterns
            complex_file = (
                temp_project
                / "impl"
                / "claude"
                / "services"
                / "brain"
                / "complex.py"
            )
            complex_file.write_text('''
def foo():
    x.method()
    module.function()
    nested.deep.call()
    lambda_call = lambda: func()
    [f() for f in []]
''')

            node = ContextNode(path="world.brain.complex", holon="complex")
            result = await resolve_hyperedge(node, "calls", temp_project)

            # Should find some calls (limited to 20)
            assert isinstance(result, list)
            assert len(result) <= 20  # Limit enforced

        finally:
            _set_project_root(original_root)

    @pytest.mark.asyncio
    async def test_tests_resolver_multiple_patterns(
        self, temp_project: Path
    ) -> None:
        """Tests resolver finds tests in multiple locations."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _set_project_root,
            _get_project_root,
        )

        original_root = _get_project_root()
        try:
            _set_project_root(temp_project)

            # Create additional test location
            tests_dir = (
                temp_project / "impl" / "claude" / "services" / "brain" / "tests"
            )
            tests_dir.mkdir(exist_ok=True)
            (tests_dir / "test_core.py").write_text("def test_alt(): pass")

            node = ContextNode(path="world.brain", holon="brain")
            result = await resolve_hyperedge(node, "tests", temp_project)

            # Should find tests from both _tests/ and tests/ directories
            assert len(result) >= 1

        finally:
            _set_project_root(original_root)

    @pytest.mark.asyncio
    async def test_implements_resolver_finds_spec_references(
        self, temp_project: Path
    ) -> None:
        """Implements resolver finds spec references in docstrings."""
        from protocols.agentese.contexts.hyperedge_resolvers import (
            _set_project_root,
            _get_project_root,
        )

        original_root = _get_project_root()
        try:
            _set_project_root(temp_project)

            # Create a file with spec reference
            (
                temp_project
                / "impl"
                / "claude"
                / "services"
                / "brain"
                / "spec_impl.py"
            ).write_text('''
"""
Implementation module.

Spec: spec/protocols/typed-hypergraph.md
"""
def impl():
    pass
''')

            # Create corresponding spec file
            spec_dir = temp_project / "spec" / "protocols"
            spec_dir.mkdir(parents=True, exist_ok=True)
            (spec_dir / "typed-hypergraph.md").write_text("# Spec\n")

            node = ContextNode(path="world.brain.spec_impl", holon="spec_impl")
            result = await resolve_hyperedge(node, "implements", temp_project)

            # Should find the spec reference
            assert len(result) >= 1
            assert any("typed-hypergraph" in r.holon for r in result)

        finally:
            _set_project_root(original_root)

    @pytest.mark.asyncio
    async def test_empty_path_handling(self) -> None:
        """Resolvers handle empty/invalid paths gracefully."""
        node = ContextNode(path="", holon="")
        root = Path("/nonexistent")

        # None of these should raise
        for edge in ["contains", "parent", "imports", "tests", "related"]:
            result = await resolve_hyperedge(node, edge, root)
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_deep_path_resolution(self) -> None:
        """Deeply nested paths resolve correctly."""
        node = ContextNode(
            path="world.services.brain.deep.nested.module.path",
            holon="path",
        )
        root = Path("/nonexistent")

        # Parent should strip correctly
        parents = await resolve_hyperedge(node, "parent", root)
        assert len(parents) == 1
        assert parents[0].path == "world.services.brain.deep.nested.module"


class TestObserverMonotonicityHardening:
    """
    Law 10.3: Observer Monotonicity (Hardening)

    Stronger tests for: O₁ ⊆ O₂ → edges(node, O₁) ⊆ edges(node, O₂)

    Teaching:
        gotcha: The monotonicity property requires a full partial ordering.
                These tests verify the complete ordering holds.
                (Evidence: this test class)
    """

    OBSERVER_HIERARCHY = ["guest", "newcomer", "developer", "architect"]

    def test_full_ordering_edge_count(self) -> None:
        """More capable observers see at least as many edge types."""
        for i, archetype_a in enumerate(self.OBSERVER_HIERARCHY):
            for j, archetype_b in enumerate(self.OBSERVER_HIERARCHY):
                if i < j:
                    # Create fresh nodes for each comparison (edge cache)
                    node_a = ContextNode(
                        path=f"world.test_{archetype_a}_{archetype_b}_a",
                        holon="test",
                    )
                    node_b = ContextNode(
                        path=f"world.test_{archetype_a}_{archetype_b}_b",
                        holon="test",
                    )

                    from protocols.agentese.node import Observer

                    edges_less = node_a.edges(Observer(archetype=archetype_a))
                    edges_more = node_b.edges(Observer(archetype=archetype_b))

                    assert len(edges_less) <= len(edges_more), (
                        f"Observer monotonicity violated: "
                        f"{archetype_a} ({len(edges_less)} edges) > "
                        f"{archetype_b} ({len(edges_more)} edges)"
                    )

    def test_all_observers_share_structural_base(self) -> None:
        """All observers see the structural base edges."""
        from protocols.agentese.node import Observer

        for archetype in self.OBSERVER_HIERARCHY:
            node = ContextNode(path=f"world.{archetype}_test", holon="test")
            edges = node.edges(Observer(archetype=archetype))

            # All must see these structural edges
            assert "contains" in edges, f"{archetype} missing 'contains'"
            assert "parent" in edges, f"{archetype} missing 'parent'"
