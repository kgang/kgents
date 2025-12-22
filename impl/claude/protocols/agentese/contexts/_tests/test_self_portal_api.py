"""
Tests for Portal API JSON Response Mode.

Phase 4A: Frontend integration tests for self.portal.* aspects
with response_format="json".

Updated for Phase 1 (Portal Fullstack Integration):
- Now uses PortalResponse canonical type
- Fields accessed directly on response, not via metadata

Verifies:
- manifest returns structured PortalResponse with tree
- expand returns PortalResponse with success + tree
- collapse returns PortalResponse with success + tree
- File analysis integration works end-to-end
"""

from __future__ import annotations

from pathlib import Path

import pytest

from protocols.agentese.contexts.portal_response import PortalResponse
from protocols.agentese.contexts.self_portal import (
    PortalNavNode,
    set_portal_nav_node,
)
from protocols.agentese.node import Observer

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def observer() -> Observer:
    """Create a test observer."""
    return Observer(archetype="developer", capabilities=frozenset(["read", "write"]))


@pytest.fixture
def portal_node() -> PortalNavNode:
    """Create a fresh PortalNavNode for each test."""
    # Clear singleton for isolation
    set_portal_nav_node(None)
    node = PortalNavNode()
    return node


@pytest.fixture
def temp_python_file(tmp_path: Path) -> Path:
    """Create a temporary Python file with imports."""
    # Create project structure
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

    # Create module with imports
    (tmp_path / "services").mkdir()
    (tmp_path / "services" / "__init__.py").write_text("")
    (tmp_path / "services" / "brain.py").write_text("""
from dataclasses import dataclass
from typing import Any


@dataclass
class BrainService:
    name: str
""")

    # Create test file
    (tmp_path / "services" / "_tests").mkdir()
    (tmp_path / "services" / "_tests" / "__init__.py").write_text("")
    (tmp_path / "services" / "_tests" / "test_brain.py").write_text("# Tests")

    return tmp_path / "services" / "brain.py"


# =============================================================================
# JSON Manifest Tests
# =============================================================================


class TestManifestJsonResponse:
    """Tests for manifest with response_format='json'."""

    @pytest.mark.asyncio
    async def test_manifest_json_returns_portal_response(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """manifest with json format should return PortalResponse."""
        result = await portal_node.manifest(
            observer,
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        assert result.success is True
        assert result.path == "self.portal"
        assert result.aspect == "manifest"

    @pytest.mark.asyncio
    async def test_manifest_json_has_tree(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """PortalResponse should have tree field."""
        result = await portal_node.manifest(
            observer,
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        assert result.tree is not None
        assert "root" in result.tree

    @pytest.mark.asyncio
    async def test_manifest_json_tree_has_children(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """Tree root should have children from file analysis."""
        result = await portal_node.manifest(
            observer,
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        assert result.tree is not None
        root = result.tree["root"]

        # Root should have children (tests at minimum)
        assert "children" in root
        assert len(root["children"]) > 0

    @pytest.mark.asyncio
    async def test_manifest_json_includes_observer_in_metadata(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """JSON response should include observer archetype in metadata."""
        result = await portal_node.manifest(
            observer,
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        assert result.metadata["observer"] == "developer"

    @pytest.mark.asyncio
    async def test_manifest_json_respects_max_depth(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """Tree max_depth should match parameter."""
        result = await portal_node.manifest(
            observer,
            file_path=str(temp_python_file),
            max_depth=2,
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        assert result.tree is not None
        assert result.tree["max_depth"] == 2


# =============================================================================
# JSON Expand Tests
# =============================================================================


class TestExpandJsonResponse:
    """Tests for expand with response_format='json'."""

    @pytest.mark.asyncio
    async def test_expand_json_returns_portal_response(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """expand with json format should return PortalResponse."""
        # First initialize tree
        await portal_node.manifest(observer, file_path=str(temp_python_file))

        # Try to expand a child
        result = await portal_node.expand(
            observer,
            portal_path="tests",  # Edge type from analysis
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        assert result.aspect == "expand"
        # success is a direct field on PortalResponse
        assert result.success in (True, False)

    @pytest.mark.asyncio
    async def test_expand_success_has_tree(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """Successful expand should return tree in response."""
        await portal_node.manifest(observer, file_path=str(temp_python_file))

        # Expand imports edge (which exists for dataclass file)
        result = await portal_node.expand(
            observer,
            portal_path="imports",  # dataclass, typing
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        if result.success:
            assert result.tree is not None
            assert result.expanded_path == "imports"


# =============================================================================
# JSON Collapse Tests
# =============================================================================


class TestCollapseJsonResponse:
    """Tests for collapse with response_format='json'."""

    @pytest.mark.asyncio
    async def test_collapse_json_returns_portal_response(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """collapse with json format should return PortalResponse."""
        await portal_node.manifest(observer, file_path=str(temp_python_file))

        result = await portal_node.collapse(
            observer,
            portal_path="tests",
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        assert result.aspect == "collapse"
        assert result.success in (True, False)

    @pytest.mark.asyncio
    async def test_collapse_nonexistent_returns_failure(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """collapse of nonexistent path should return failure."""
        await portal_node.manifest(observer, file_path=str(temp_python_file))

        result = await portal_node.collapse(
            observer,
            portal_path="nonexistent",
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        assert result.success is False
        assert result.error is not None


# =============================================================================
# Invoke Routing Tests
# =============================================================================


class TestInvokeRoutingWithJsonFormat:
    """Tests for _invoke_aspect routing with json format."""

    @pytest.mark.asyncio
    async def test_invoke_manifest_with_json(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """_invoke_aspect should route manifest with json format."""
        result = await portal_node._invoke_aspect(
            "manifest",
            observer,
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        assert result.success is True
        assert result.tree is not None

    @pytest.mark.asyncio
    async def test_invoke_expand_with_json(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """_invoke_aspect should route expand with json format."""
        await portal_node.manifest(observer, file_path=str(temp_python_file))

        result = await portal_node._invoke_aspect(
            "expand",
            observer,
            portal_path="tests",
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        assert result.aspect == "expand"


# =============================================================================
# File Analysis Integration Tests
# =============================================================================


class TestFileAnalysisIntegration:
    """End-to-end tests for file analysis integration."""

    @pytest.mark.asyncio
    async def test_python_file_gets_analyzed(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """Python files should be analyzed for imports/tests."""
        result = await portal_node.manifest(
            observer,
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        assert result.tree is not None
        root = result.tree["root"]

        # Should have test edge type
        edge_types = {child["edge_type"] for child in root["children"]}
        assert "tests" in edge_types

    @pytest.mark.asyncio
    async def test_non_python_file_basic_tree(
        self, portal_node: PortalNavNode, observer: Observer, tmp_path: Path
    ) -> None:
        """Non-Python files should get basic tree without analysis."""
        md_file = tmp_path / "readme.md"
        md_file.write_text("# Readme")

        result = await portal_node.manifest(
            observer,
            file_path=str(md_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        assert result.tree is not None
        root = result.tree["root"]

        # Root exists but children are empty (no analysis for .md)
        assert root["path"] == str(md_file)
        assert root["children"] == []


# =============================================================================
# Tree Serialization Tests
# =============================================================================


class TestTreeSerialization:
    """Tests for PortalTree.to_dict() serialization."""

    @pytest.mark.asyncio
    async def test_tree_dict_has_all_fields(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """Serialized tree should have all expected fields."""
        result = await portal_node.manifest(
            observer,
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        assert result.tree is not None
        tree = result.tree

        # Tree level
        assert "root" in tree
        assert "max_depth" in tree

        # Root node level
        root = tree["root"]
        assert "path" in root
        assert "edge_type" in root
        assert "expanded" in root
        assert "children" in root
        assert "depth" in root
        assert "state" in root

    @pytest.mark.asyncio
    async def test_children_are_serialized(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """Child nodes should be serialized recursively."""
        result = await portal_node.manifest(
            observer,
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        assert result.tree is not None
        root = result.tree["root"]

        # Check child structure
        for child in root["children"]:
            assert "path" in child
            assert "edge_type" in child
            assert "state" in child


# =============================================================================
# Phase 2 Readiness Tests
# =============================================================================


class TestPhase2Readiness:
    """Tests verifying readiness for Phase 2 (Witness Mark Integration)."""

    @pytest.mark.asyncio
    async def test_expand_response_has_evidence_id_field(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """PortalResponse should have evidence_id field (None until Phase 2)."""
        await portal_node.manifest(observer, file_path=str(temp_python_file))

        result = await portal_node.expand(
            observer,
            portal_path="imports",
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, PortalResponse)
        # Field exists but is None until Phase 2 implements witness marks
        assert hasattr(result, "evidence_id")

    @pytest.mark.asyncio
    async def test_portal_response_is_renderable(
        self, portal_node: PortalNavNode, observer: Observer, temp_python_file: Path
    ) -> None:
        """PortalResponse should satisfy Renderable protocol."""
        from protocols.agentese.node import Renderable

        result = await portal_node.manifest(
            observer,
            file_path=str(temp_python_file),
            response_format="json",
        )

        assert isinstance(result, Renderable)
        assert callable(getattr(result, "to_dict", None))
        assert callable(getattr(result, "to_text", None))
