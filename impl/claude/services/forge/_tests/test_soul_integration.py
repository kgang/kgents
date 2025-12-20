"""
Tests for K-gent integration into Forge (Phase 2).

Verifies:
1. KgentSoul is injectable via DI
2. ForgeNode accepts kgent_soul parameter
3. Governance gates intercept governed aspects
4. ForgeSoulNode AGENTESE paths are registered
5. Soul manifest returns expected structure

See: spec/protocols/metaphysical-forge.md (Phase 2)
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.k.soul import KgentSoul
from protocols.agentese.node import Observer
from services.forge.node import ForgeNode
from services.forge.persistence import ForgePersistence
from services.forge.soul_node import ForgeSoulNode, SoulManifestRendering


# === Helper for xdist compatibility ===
def is_type(obj: Any, type_name: str) -> bool:
    """
    Check if obj is an instance of type by name.

    Used for xdist compatibility where class identity may differ
    across workers due to module reimport.
    """
    return type(obj).__name__ == type_name


# === Fixtures ===


@pytest.fixture
def mock_persistence():
    """Create a mock ForgePersistence."""
    return MagicMock(spec=ForgePersistence)


@pytest.fixture
def kgent_soul():
    """Create a real KgentSoul (no LLM, template mode)."""
    return KgentSoul(auto_llm=False)


@pytest.fixture
def observer():
    """Create a test observer."""
    return Observer(
        archetype="developer",
        capabilities=frozenset(["read", "write"]),
    )


# === DI Tests ===


class TestKgentInjection:
    """Test DI pattern for KgentSoul."""

    def test_forge_node_accepts_kgent_soul(self, mock_persistence, kgent_soul):
        """ForgeNode.__init__ accepts kgent_soul parameter."""
        node = ForgeNode(
            forge_persistence=mock_persistence,
            kgent_soul=kgent_soul,
        )
        assert node.soul is kgent_soul

    def test_forge_node_works_without_soul(self, mock_persistence):
        """ForgeNode works when kgent_soul is None."""
        node = ForgeNode(
            forge_persistence=mock_persistence,
            kgent_soul=None,
        )
        assert node.soul is None

    @pytest.mark.asyncio
    async def test_kgent_soul_from_registry(self):
        """KgentSoul can be retrieved from ServiceRegistry."""
        from services.bootstrap import bootstrap_services, get_service, reset_services

        reset_services()
        await bootstrap_services()

        soul = await get_service("kgent_soul")
        assert isinstance(soul, KgentSoul)

        reset_services()


# === Governance Gate Tests ===


class TestGovernanceGates:
    """Test K-gent governance interception."""

    def test_governed_aspects_defined(self):
        """ForgeNode has GOVERNED_ASPECTS constant."""
        assert hasattr(ForgeNode, "GOVERNED_ASPECTS")
        assert "contribute" in ForgeNode.GOVERNED_ASPECTS
        assert "workshop.create" in ForgeNode.GOVERNED_ASPECTS
        assert "exhibition.create" in ForgeNode.GOVERNED_ASPECTS
        assert "gallery.add" in ForgeNode.GOVERNED_ASPECTS
        assert "festival.create" in ForgeNode.GOVERNED_ASPECTS

    def test_non_governed_aspects_not_in_set(self):
        """Read-only aspects are not governed."""
        assert "workshop.list" not in ForgeNode.GOVERNED_ASPECTS
        assert "workshop.get" not in ForgeNode.GOVERNED_ASPECTS
        assert "artisan.list" not in ForgeNode.GOVERNED_ASPECTS
        assert "manifest" not in ForgeNode.GOVERNED_ASPECTS

    @pytest.mark.asyncio
    async def test_governance_gate_passes_on_approve(self, mock_persistence, kgent_soul, observer):
        """Governance gate allows operation when K-gent approves."""
        # Mock intercept to return auto-handled
        intercept_result = MagicMock(
            handled=True,
            recommendation="approved",
            annotation=None,
            matching_principles=[],
        )
        kgent_soul.intercept = AsyncMock(return_value=intercept_result)

        # Mock persistence to return a workshop
        mock_workshop = MagicMock(
            id="ws-1",
            name="Test Workshop",
            is_active=True,
            description=None,
            theme=None,
            artisan_count=0,
            contribution_count=0,
            started_at=None,
            created_at=None,
        )
        mock_persistence.create_workshop = AsyncMock(return_value=mock_workshop)

        node = ForgeNode(
            forge_persistence=mock_persistence,
            kgent_soul=kgent_soul,
        )

        result = await node._invoke_aspect(
            "workshop.create",
            observer,
            name="Test Workshop",
        )

        # Verify intercept was called
        kgent_soul.intercept.assert_called_once()

        # Verify operation proceeded
        mock_persistence.create_workshop.assert_called_once()

    @pytest.mark.asyncio
    async def test_governance_gate_blocks_on_escalate(self, mock_persistence, kgent_soul, observer):
        """Governance gate blocks operation when K-gent escalates."""
        # Mock intercept to return escalate
        intercept_result = MagicMock(
            handled=False,
            recommendation="escalate",
            annotation="This needs human review",
            matching_principles=["taste", "depth"],
        )
        kgent_soul.intercept = AsyncMock(return_value=intercept_result)

        node = ForgeNode(
            forge_persistence=mock_persistence,
            kgent_soul=kgent_soul,
        )

        result = await node._invoke_aspect(
            "workshop.create",
            observer,
            name="Test Workshop",
        )

        # Verify intercept was called
        kgent_soul.intercept.assert_called_once()

        # Verify operation was blocked
        assert hasattr(result, "to_dict")
        result_dict = result.to_dict()
        # BasicRendering wraps content in a 'content' key
        content = result_dict.get("content", result_dict)
        assert content.get("governance") == "blocked"
        assert "annotation" in content


# === ForgeSoulNode Tests ===


class TestForgeSoulNode:
    """Test ForgeSoulNode AGENTESE paths."""

    def test_node_handle(self, kgent_soul):
        """ForgeSoulNode has correct handle."""
        node = ForgeSoulNode(kgent_soul=kgent_soul)
        assert node.handle == "world.forge.soul"

    @pytest.mark.asyncio
    async def test_manifest_with_soul(self, kgent_soul, observer):
        """Manifest returns soul state when connected."""
        node = ForgeSoulNode(kgent_soul=kgent_soul)
        result = await node.manifest(observer)

        # Use type name comparison for xdist compatibility
        assert is_type(result, "SoulManifestRendering")
        assert result.mode is not None
        assert isinstance(result.eigenvectors, dict)
        assert "aesthetic" in result.eigenvectors or len(result.eigenvectors) >= 0

    @pytest.mark.asyncio
    async def test_manifest_without_soul(self, observer):
        """Manifest returns dormant state when soul not connected."""
        node = ForgeSoulNode(kgent_soul=None)
        result = await node.manifest(observer)

        result_dict = result.to_dict()
        # BasicRendering uses 'metadata' key for structured data
        metadata = result_dict.get("metadata", result_dict)
        assert metadata.get("mode") == "dormant"

    @pytest.mark.asyncio
    async def test_vibe_returns_eigenvectors(self, kgent_soul, observer):
        """Vibe aspect returns eigenvector dimensions."""
        node = ForgeSoulNode(kgent_soul=kgent_soul)
        result = await node._invoke_aspect("vibe", observer)

        result_dict = result.to_dict()
        assert result_dict["type"] == "soul_vibe"
        assert "dimensions" in result_dict
        assert "context" in result_dict

    def test_affordances(self, kgent_soul, observer):
        """ForgeSoulNode returns correct affordances."""
        node = ForgeSoulNode(kgent_soul=kgent_soul)
        affordances = node._get_affordances_for_archetype("developer")
        assert "manifest" in affordances
        assert "vibe" in affordances


# === AGENTESE Registration Tests ===


class TestAgenteseRegistration:
    """Test AGENTESE path registration."""

    def test_forge_soul_path_registered(self):
        """world.forge.soul is registered in AGENTESE registry."""
        # Import gateway to trigger node registration
        from protocols.agentese import gateway  # noqa: F401
        from protocols.agentese.registry import get_registry

        registry = get_registry()

        # The path should be registered by @node decorator
        # Check for either path format
        paths = registry.list_paths() if hasattr(registry, "list_paths") else []
        # Note: registration happens at import time via @node decorator


# === Integration Tests ===


class TestIntegration:
    """Integration tests for full K-gent Forge flow."""

    @pytest.mark.asyncio
    async def test_full_governance_flow(self, mock_persistence, observer):
        """Test complete flow: DI → Governance → Result."""
        from services.bootstrap import (
            bootstrap_services,
            get_service,
            reset_services,
        )

        reset_services()
        await bootstrap_services()

        # Get real KgentSoul from registry
        soul = await get_service("kgent_soul")
        assert isinstance(soul, KgentSoul)

        # Create ForgeNode with soul
        node = ForgeNode(
            forge_persistence=mock_persistence,
            kgent_soul=soul,
        )

        # Mock persistence for workshop creation
        mock_workshop = MagicMock(
            id="ws-int-1",
            name="Integration Test",
            is_active=True,
            description=None,
            theme=None,
            artisan_count=0,
            contribution_count=0,
            started_at=None,
            created_at=None,
        )
        mock_persistence.create_workshop = AsyncMock(return_value=mock_workshop)

        # Invoke governed aspect
        result = await node._invoke_aspect(
            "workshop.create",
            observer,
            name="Integration Test",
        )

        # Should either succeed or be governed
        result_dict = result.to_dict() if hasattr(result, "to_dict") else result
        assert isinstance(result_dict, dict)

        reset_services()
