"""
Tests for GestaltNode AGENTESE integration.

Tests:
1. Registers with @node("world.codebase")
2. Returns proper rendering from manifest()
3. Returns topology data from _invoke_aspect
4. Archetype-based affordances work correctly
"""

from __future__ import annotations

import pytest

# =============================================================================
# Registration Tests
# =============================================================================


class TestGestaltNodeRegistration:
    """Test @node decorator registration."""

    def test_node_import_registers_path(self) -> None:
        """Importing GestaltNode registers world.codebase path."""
        from protocols.agentese.registry import get_registry
        from services.gestalt import GestaltNode  # noqa: F401

        registry = get_registry()
        assert registry.has("world.codebase")

    def test_node_is_in_registry_list(self) -> None:
        """GestaltNode path appears in registry list."""
        from protocols.agentese.registry import get_registry
        from services.gestalt import GestaltNode  # noqa: F401

        registry = get_registry()
        paths = registry.list_paths()
        assert "world.codebase" in paths

    def test_node_handle_property(self) -> None:
        """GestaltNode.handle matches @node path."""
        from services.gestalt.node import GestaltNode

        node = GestaltNode()
        assert node.handle == "world.codebase"


# =============================================================================
# Affordance Tests
# =============================================================================


class TestGestaltNodeAffordances:
    """Test archetype-based affordance filtering."""

    def test_developer_gets_all_affordances(self) -> None:
        """Developer archetype gets full access including scan."""
        from services.gestalt.node import GestaltNode

        node = GestaltNode()
        affordances = node._get_affordances_for_archetype("developer")

        assert "manifest" in affordances
        assert "health" in affordances
        assert "topology" in affordances
        assert "drift" in affordances
        assert "module" in affordances
        assert "scan" in affordances

    def test_guest_gets_read_only_affordances(self) -> None:
        """Guest archetype gets read-only access."""
        from services.gestalt.node import GestaltNode

        node = GestaltNode()
        affordances = node._get_affordances_for_archetype("guest")

        assert "manifest" in affordances
        assert "health" in affordances
        assert "topology" in affordances
        assert "drift" in affordances
        assert "module" in affordances
        assert "scan" not in affordances  # No mutation for guests


# =============================================================================
# Manifest Tests
# =============================================================================


class TestGestaltNodeManifest:
    """Test manifest() method."""

    @pytest.mark.asyncio
    @pytest.mark.slow  # Scans full codebase - too slow for CI unit tests
    async def test_manifest_returns_rendering(self) -> None:
        """Manifest returns GestaltManifestRendering."""
        from protocols.agentese.node import Observer
        from services.gestalt.node import GestaltManifestRendering, GestaltNode

        node = GestaltNode()
        observer = Observer(archetype="developer")

        result = await node.manifest(observer)

        assert isinstance(result, GestaltManifestRendering)
        assert result.module_count > 0  # Should have some modules
        assert result.overall_grade in (
            "A+",
            "A",
            "A-",
            "B+",
            "B",
            "B-",
            "C+",
            "C",
            "C-",
            "D",
            "F",
        )

    @pytest.mark.asyncio
    @pytest.mark.slow  # Scans full codebase - too slow for CI unit tests
    async def test_manifest_to_dict(self) -> None:
        """Manifest rendering can convert to dict."""
        from protocols.agentese.node import Observer
        from services.gestalt.node import GestaltNode

        node = GestaltNode()
        observer = Observer(archetype="developer")

        result = await node.manifest(observer)
        data = result.to_dict()

        assert data["type"] == "codebase_manifest"
        assert "module_count" in data
        assert "edge_count" in data
        assert "overall_grade" in data


# =============================================================================
# Topology Tests
# =============================================================================


class TestGestaltNodeTopology:
    """Test topology aspect."""

    @pytest.mark.asyncio
    async def test_topology_returns_nodes_and_links(self) -> None:
        """Topology returns node and link data."""
        from protocols.agentese.node import Observer
        from services.gestalt.node import GestaltNode

        node = GestaltNode()
        observer = Observer(archetype="developer")

        result = await node._invoke_aspect("topology", observer, max_nodes=20)

        assert "nodes" in result
        assert "links" in result
        assert "layers" in result
        assert "stats" in result
        assert isinstance(result["nodes"], list)
        assert len(result["nodes"]) <= 20  # Respects max_nodes

    @pytest.mark.asyncio
    async def test_topology_nodes_have_required_fields(self) -> None:
        """Topology nodes have all required visualization fields."""
        from protocols.agentese.node import Observer
        from services.gestalt.node import GestaltNode

        node = GestaltNode()
        observer = Observer(archetype="developer")

        result = await node._invoke_aspect("topology", observer, max_nodes=5)

        if result["nodes"]:
            n = result["nodes"][0]
            assert "id" in n
            assert "label" in n
            assert "health_score" in n
            assert "x" in n
            assert "y" in n
            assert "z" in n


# =============================================================================
# Other Aspects Tests
# =============================================================================


class TestGestaltNodeAspects:
    """Test other aspects."""

    @pytest.mark.asyncio
    async def test_health_aspect(self) -> None:
        """Health aspect returns health metrics."""
        from protocols.agentese.node import Observer
        from services.gestalt.node import GestaltNode

        node = GestaltNode()
        observer = Observer(archetype="developer")

        result = await node._invoke_aspect("health", observer)

        assert "average_health" in result
        assert "overall_grade" in result

    @pytest.mark.asyncio
    async def test_drift_aspect(self) -> None:
        """Drift aspect returns violations."""
        from protocols.agentese.node import Observer
        from services.gestalt.node import GestaltNode

        node = GestaltNode()
        observer = Observer(archetype="developer")

        result = await node._invoke_aspect("drift", observer)

        assert "total_violations" in result
        assert "violations" in result

    @pytest.mark.asyncio
    async def test_unknown_aspect_returns_error(self) -> None:
        """Unknown aspect returns error dict."""
        from protocols.agentese.node import Observer
        from services.gestalt.node import GestaltNode

        node = GestaltNode()
        observer = Observer(archetype="developer")

        result = await node._invoke_aspect("nonexistent", observer)

        assert "error" in result
        assert "Unknown aspect" in result["error"]
