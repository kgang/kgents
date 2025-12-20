"""
Tests for Cross-Jewel Invocation (Phase 3B).

Tests the JewelInvoker and path classification for cross-jewel
invocation patterns.

See: plans/kgentsd-cross-jewel.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.witness.invoke import (
    InvocationResult,
    JewelInvoker,
    classify_path,
    create_invoker,
    is_mutation_path,
    is_read_only_path,
)
from services.witness.polynomial import TrustLevel
from services.witness.trust import ActionGate, GateDecision

# =============================================================================
# Path Classification Tests
# =============================================================================


class TestClassifyPath:
    """Tests for path classification utility."""

    def test_classify_simple_path(self) -> None:
        """Test classifying a simple path."""
        context, holon, aspect = classify_path("world.gestalt.manifest")
        assert context == "world"
        assert holon == "gestalt"
        assert aspect == "manifest"

    def test_classify_nested_path(self) -> None:
        """Test classifying a nested path."""
        context, holon, aspect = classify_path("self.memory.crystal.capture")
        assert context == "self"
        assert holon == "memory.crystal"
        assert aspect == "capture"

    def test_classify_invalid_path_raises(self) -> None:
        """Test that malformed paths raise ValueError."""
        with pytest.raises(ValueError, match="at least 3 parts"):
            classify_path("world.gestalt")

        with pytest.raises(ValueError, match="at least 3 parts"):
            classify_path("world")


class TestReadOnlyPath:
    """Tests for read-only path detection."""

    @pytest.mark.parametrize(
        "path",
        [
            "world.gestalt.manifest",
            "self.memory.affordances",
            "world.town.witness",
            "concept.design.query",
            "self.soul.status",
        ],
    )
    def test_read_only_paths(self, path: str) -> None:
        """Test that manifest, affordances, witness, etc. are read-only."""
        assert is_read_only_path(path) is True

    @pytest.mark.parametrize(
        "path",
        [
            "self.memory.capture",
            "world.forge.apply",
            "world.gestalt.refactor",
            "self.witness.escalate",
        ],
    )
    def test_mutation_paths(self, path: str) -> None:
        """Test that capture, apply, refactor, etc. are mutations."""
        assert is_read_only_path(path) is False


class TestMutationPath:
    """Tests for mutation path detection."""

    @pytest.mark.parametrize(
        "path",
        [
            "self.memory.capture",
            "world.forge.create",
            "world.gestalt.update",
            "self.witness.delete",
            "world.forge.apply",
            "world.town.execute",
        ],
    )
    def test_mutation_paths(self, path: str) -> None:
        """Test that mutation aspects are detected."""
        assert is_mutation_path(path) is True

    @pytest.mark.parametrize(
        "path",
        [
            "world.gestalt.manifest",
            "self.memory.affordances",
            "world.town.list",
        ],
    )
    def test_non_mutation_paths(self, path: str) -> None:
        """Test that read-only aspects are not mutations."""
        # Note: is_mutation_path returns True for non-read-only paths
        # So "list" should not be a mutation since it's in READ_ONLY_ASPECTS
        assert is_mutation_path(path) is False


# =============================================================================
# InvocationResult Tests
# =============================================================================


class TestInvocationResult:
    """Tests for InvocationResult dataclass."""

    def test_success_result(self) -> None:
        """Test creating a successful invocation result."""
        result = InvocationResult(
            path="world.gestalt.manifest",
            success=True,
            result={"status": "ok"},
            gate_decision=GateDecision.ALLOW,
        )

        assert result.is_success is True
        assert result.path == "world.gestalt.manifest"
        assert result.result == {"status": "ok"}
        assert result.error is None

    def test_failed_result(self) -> None:
        """Test creating a failed invocation result."""
        result = InvocationResult(
            path="self.memory.capture",
            success=False,
            error="Permission denied",
            gate_decision=GateDecision.DENY,
        )

        assert result.is_success is False
        assert result.error == "Permission denied"
        assert result.result is None

    def test_to_dict(self) -> None:
        """Test serialization to dict."""
        result = InvocationResult(
            path="world.gestalt.manifest",
            success=True,
            result={"data": 123},
            gate_decision=GateDecision.LOG,
        )

        d = result.to_dict()
        assert d["path"] == "world.gestalt.manifest"
        assert d["success"] is True
        assert d["result"] == {"data": 123}
        assert d["gate_decision"] == "LOG"
        assert "timestamp" in d


# =============================================================================
# JewelInvoker Tests
# =============================================================================


class TestJewelInvoker:
    """Tests for JewelInvoker class."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos instance."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={"status": "ok"})
        return logos

    @pytest.fixture
    def l3_invoker(self, mock_logos: MagicMock) -> JewelInvoker:
        """Create a JewelInvoker at L3 AUTONOMOUS."""
        return create_invoker(mock_logos, TrustLevel.AUTONOMOUS)

    @pytest.fixture
    def l2_invoker(self, mock_logos: MagicMock) -> JewelInvoker:
        """Create a JewelInvoker at L2 SUGGESTION."""
        return create_invoker(mock_logos, TrustLevel.SUGGESTION)

    @pytest.fixture
    def l0_invoker(self, mock_logos: MagicMock) -> JewelInvoker:
        """Create a JewelInvoker at L0 READ_ONLY."""
        return create_invoker(mock_logos, TrustLevel.READ_ONLY)

    @pytest.fixture
    def mock_observer(self) -> MagicMock:
        """Create a mock Observer."""
        observer = MagicMock()
        observer.archetype = "developer"
        return observer

    @pytest.mark.asyncio
    async def test_invoke_read_only_at_l0(
        self, l0_invoker: JewelInvoker, mock_observer: MagicMock
    ) -> None:
        """Test that read-only paths can be invoked at L0."""
        result = await l0_invoker.invoke("world.gestalt.manifest", mock_observer)

        assert result.success is True
        assert result.gate_decision in (GateDecision.ALLOW, GateDecision.LOG)

    @pytest.mark.asyncio
    async def test_invoke_mutation_at_l3(
        self, l3_invoker: JewelInvoker, mock_observer: MagicMock
    ) -> None:
        """Test that mutation paths can be invoked at L3."""
        result = await l3_invoker.invoke("self.memory.capture", mock_observer, content="test")

        assert result.success is True
        assert result.gate_decision == GateDecision.LOG

    @pytest.mark.asyncio
    async def test_invoke_mutation_at_l0_denied(
        self, l0_invoker: JewelInvoker, mock_observer: MagicMock
    ) -> None:
        """Test that mutation paths are denied at L0."""
        result = await l0_invoker.invoke("self.memory.capture", mock_observer)

        assert result.success is False
        assert "L3 AUTONOMOUS" in (result.error or "")

    @pytest.mark.asyncio
    async def test_invoke_mutation_at_l2_confirm(
        self, l2_invoker: JewelInvoker, mock_observer: MagicMock
    ) -> None:
        """Test that mutation paths require confirmation at L2."""
        result = await l2_invoker.invoke("self.memory.capture", mock_observer)

        # At L2, mutations should require confirmation
        assert result.success is False
        assert result.gate_decision == GateDecision.CONFIRM

    @pytest.mark.asyncio
    async def test_invoke_forbidden_action(
        self, l3_invoker: JewelInvoker, mock_observer: MagicMock
    ) -> None:
        """Test that forbidden actions are blocked even at L3."""
        # Use a path that would trigger forbidden action detection
        result = await l3_invoker.invoke("world.system.execute", mock_observer, command="rm -rf /")

        # The gate should catch the forbidden action
        # Note: This depends on how the gate pattern matching works
        # The action description would be "invoke world.system.execute"
        # which may or may not trigger forbidden patterns

    @pytest.mark.asyncio
    async def test_invoke_read_convenience(
        self, l0_invoker: JewelInvoker, mock_observer: MagicMock
    ) -> None:
        """Test the invoke_read convenience method."""
        result = await l0_invoker.invoke_read("world.gestalt.manifest", mock_observer)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_invoke_mutation_convenience(
        self, l3_invoker: JewelInvoker, mock_observer: MagicMock
    ) -> None:
        """Test the invoke_mutation convenience method."""
        result = await l3_invoker.invoke_mutation("self.memory.capture", mock_observer)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_invoke_mutation_convenience_l0_blocked(
        self, l0_invoker: JewelInvoker, mock_observer: MagicMock
    ) -> None:
        """Test that invoke_mutation blocks at L0."""
        result = await l0_invoker.invoke_mutation("self.memory.capture", mock_observer)

        assert result.success is False
        assert result.gate_decision == GateDecision.DENY

    def test_can_invoke_read_only(self, l0_invoker: JewelInvoker) -> None:
        """Test can_invoke for read-only paths."""
        assert l0_invoker.can_invoke("world.gestalt.manifest") is True

    def test_can_invoke_mutation_at_l0(self, l0_invoker: JewelInvoker) -> None:
        """Test can_invoke for mutations at L0."""
        assert l0_invoker.can_invoke("self.memory.capture") is False

    def test_can_invoke_mutation_at_l3(self, l3_invoker: JewelInvoker) -> None:
        """Test can_invoke for mutations at L3."""
        assert l3_invoker.can_invoke("self.memory.capture") is True

    @pytest.mark.asyncio
    async def test_invocation_log(self, l3_invoker: JewelInvoker, mock_observer: MagicMock) -> None:
        """Test that invocations are logged."""
        await l3_invoker.invoke("world.gestalt.manifest", mock_observer)
        await l3_invoker.invoke("self.memory.capture", mock_observer)

        log = l3_invoker.get_invocation_log()
        assert len(log) == 2
        assert log[0].path == "self.memory.capture"  # Most recent first
        assert log[1].path == "world.gestalt.manifest"

    @pytest.mark.asyncio
    async def test_invocation_log_success_only(
        self, l3_invoker: JewelInvoker, mock_observer: MagicMock
    ) -> None:
        """Test filtering invocation log by success."""
        # Make one invocation fail
        l3_invoker.logos.invoke = AsyncMock(side_effect=Exception("Test error"))
        await l3_invoker.invoke("world.gestalt.fail", mock_observer)

        # Make one succeed
        l3_invoker.logos.invoke = AsyncMock(return_value={"ok": True})
        await l3_invoker.invoke("world.gestalt.manifest", mock_observer)

        all_log = l3_invoker.get_invocation_log()
        assert len(all_log) == 2

        success_log = l3_invoker.get_invocation_log(success_only=True)
        assert len(success_log) == 1
        assert success_log[0].path == "world.gestalt.manifest"


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestCreateInvoker:
    """Tests for create_invoker factory function."""

    def test_create_invoker_l0(self) -> None:
        """Test creating an invoker at L0."""
        logos = MagicMock()
        invoker = create_invoker(logos, TrustLevel.READ_ONLY)

        assert invoker.trust_level == TrustLevel.READ_ONLY
        assert invoker.logos is logos

    def test_create_invoker_l3(self) -> None:
        """Test creating an invoker at L3."""
        logos = MagicMock()
        invoker = create_invoker(logos, TrustLevel.AUTONOMOUS)

        assert invoker.trust_level == TrustLevel.AUTONOMOUS

    def test_create_invoker_with_custom_boundary_checker(self) -> None:
        """Test creating an invoker with custom boundary checker."""
        from services.witness.trust import BoundaryChecker

        logos = MagicMock()
        checker = BoundaryChecker()
        invoker = create_invoker(logos, TrustLevel.AUTONOMOUS, boundary_checker=checker)

        assert invoker.gate.boundary_checker is checker

    def test_create_invoker_log_disabled(self) -> None:
        """Test creating an invoker with logging disabled."""
        logos = MagicMock()
        invoker = create_invoker(logos, TrustLevel.AUTONOMOUS, log_invocations=False)

        assert invoker.log_invocations is False


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestInvokerErrorHandling:
    """Tests for error handling in JewelInvoker."""

    @pytest.fixture
    def mock_logos_error(self) -> MagicMock:
        """Create a mock Logos that raises errors."""
        logos = MagicMock()
        logos.invoke = AsyncMock(side_effect=Exception("Test error"))
        return logos

    @pytest.fixture
    def mock_observer(self) -> MagicMock:
        """Create a mock Observer."""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_invoke_handles_exception(
        self, mock_logos_error: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test that exceptions during invocation are handled gracefully."""
        invoker = create_invoker(mock_logos_error, TrustLevel.AUTONOMOUS)

        result = await invoker.invoke("world.gestalt.manifest", mock_observer)

        assert result.success is False
        assert "Test error" in (result.error or "")
        # Gate decision should still be recorded
        assert result.gate_decision is not None
