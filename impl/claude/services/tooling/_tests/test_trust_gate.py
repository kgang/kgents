"""
Tests for ToolTrustGate.

Verifies:
- Trust level checking
- Gate decision types (ALLOWED, DENIED, REQUIRES_CONFIRMATION)
- Integration with Witness (mocked)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from services.tooling.trust_gate import (
    TOOL_TRUST_REQUIREMENTS,
    GateDecision,
    GateResult,
    ToolTrustGate,
    TrustViolation,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def gate() -> ToolTrustGate:
    """Trust gate without witness (uses defaults)."""
    return ToolTrustGate()


@pytest.fixture
def mock_witness() -> MagicMock:
    """Mock witness persistence."""
    witness = MagicMock()

    # Create mock TrustResult
    mock_result = MagicMock()
    mock_result.trust_level.value = 2  # Default to L2

    witness.get_trust_level = AsyncMock(return_value=mock_result)
    return witness


@pytest.fixture
def gate_with_witness(mock_witness: MagicMock) -> ToolTrustGate:
    """Trust gate with mocked witness."""
    return ToolTrustGate(witness=mock_witness)


# =============================================================================
# Default Requirements Tests
# =============================================================================


class TestDefaultRequirements:
    """Tests for default trust requirements."""

    def test_file_read_requires_l0(self) -> None:
        """file.read requires L0."""
        assert TOOL_TRUST_REQUIREMENTS["file.read"] == 0

    def test_file_write_requires_l2(self) -> None:
        """file.write requires L2."""
        assert TOOL_TRUST_REQUIREMENTS["file.write"] == 2

    def test_system_bash_requires_l3(self) -> None:
        """system.bash requires L3."""
        assert TOOL_TRUST_REQUIREMENTS["system.bash"] == 3

    def test_web_fetch_requires_l1(self) -> None:
        """web.fetch requires L1."""
        assert TOOL_TRUST_REQUIREMENTS["web.fetch"] == 1


# =============================================================================
# Gate Check Tests
# =============================================================================


class TestGateCheck:
    """Tests for trust gate checks."""

    @pytest.mark.asyncio
    async def test_l0_tool_allowed_at_l0(self, gate: ToolTrustGate) -> None:
        """L0 tool is allowed at L0 trust."""
        result = await gate.check("file.read")

        assert result.allowed is True
        assert result.decision == GateDecision.ALLOWED
        assert result.required_trust == 0
        assert result.current_trust == 0  # Default

    @pytest.mark.asyncio
    async def test_l2_tool_denied_at_l0(self, gate: ToolTrustGate) -> None:
        """L2 tool is denied at L0 trust."""
        result = await gate.check("file.write")

        assert result.allowed is False
        assert result.decision == GateDecision.DENIED
        assert result.required_trust == 2
        assert result.current_trust == 0

    @pytest.mark.asyncio
    async def test_l3_tool_denied_at_l2(self, gate_with_witness: ToolTrustGate) -> None:
        """L3 tool is denied at L2 trust."""
        result = await gate_with_witness.check("system.bash", git_email="test@example.com")

        assert result.allowed is False
        assert result.decision == GateDecision.DENIED
        assert result.required_trust == 3
        assert result.current_trust == 2

    @pytest.mark.asyncio
    async def test_l2_tool_allowed_at_l2(self, gate_with_witness: ToolTrustGate) -> None:
        """L2 tool is allowed at L2 trust (trust equals requirement)."""
        result = await gate_with_witness.check("file.write", git_email="test@example.com")

        # When trust >= required, tool is allowed
        assert result.allowed is True
        assert result.decision == GateDecision.ALLOWED

    @pytest.mark.asyncio
    async def test_unknown_tool_defaults_to_l3(self, gate: ToolTrustGate) -> None:
        """Unknown tool defaults to L3 requirement."""
        result = await gate.check("unknown.tool")

        assert result.allowed is False
        assert result.required_trust == 3


# =============================================================================
# Check or Raise Tests
# =============================================================================


class TestCheckOrRaise:
    """Tests for check_or_raise method."""

    @pytest.mark.asyncio
    async def test_raises_on_denied(self, gate: ToolTrustGate) -> None:
        """Raises TrustViolation when denied."""
        with pytest.raises(TrustViolation) as exc:
            await gate.check_or_raise("file.write")

        assert exc.value.result is not None
        assert exc.value.result.decision == GateDecision.DENIED

    @pytest.mark.asyncio
    async def test_returns_result_on_allowed(self, gate: ToolTrustGate) -> None:
        """Returns result when allowed."""
        result = await gate.check_or_raise("file.read")

        assert result.allowed is True

    @pytest.mark.asyncio
    async def test_returns_result_when_trust_equals_requirement(
        self, gate_with_witness: ToolTrustGate
    ) -> None:
        """Returns allowed result when trust equals requirement."""
        result = await gate_with_witness.check_or_raise("file.write", git_email="test@example.com")

        assert result.allowed is True


# =============================================================================
# Requirement Override Tests
# =============================================================================


class TestRequirementOverride:
    """Tests for requirement override."""

    @pytest.mark.asyncio
    async def test_set_requirement(self, gate: ToolTrustGate) -> None:
        """Can override requirement for a tool."""
        gate.set_requirement("custom.tool", 1)

        result = await gate.check("custom.tool")
        assert result.required_trust == 1

    def test_get_required_trust(self, gate: ToolTrustGate) -> None:
        """Can get required trust for a tool."""
        assert gate.get_required_trust("file.read") == 0
        assert gate.get_required_trust("file.write") == 2
        assert gate.get_required_trust("unknown") == 3  # Default


# =============================================================================
# Observer Integration Tests
# =============================================================================


class TestObserverIntegration:
    """Tests for observer-based trust lookup."""

    @pytest.mark.asyncio
    async def test_uses_observer_trust_level(self, gate: ToolTrustGate) -> None:
        """Uses trust_level from observer if available."""
        # Mock observer with trust_level attribute
        observer = MagicMock()
        observer.trust_level = 3

        result = await gate.check("system.bash", observer=observer)

        assert result.current_trust == 3
        assert result.allowed is True

    @pytest.mark.asyncio
    async def test_falls_back_to_witness(
        self, gate_with_witness: ToolTrustGate, mock_witness: MagicMock
    ) -> None:
        """Falls back to witness if observer has no trust_level."""
        observer = MagicMock(spec=[])  # No trust_level

        result = await gate_with_witness.check(
            "file.write", observer=observer, git_email="test@example.com"
        )

        mock_witness.get_trust_level.assert_called_once_with("test@example.com")
        assert result.current_trust == 2  # From mock


# =============================================================================
# GateResult Tests
# =============================================================================


class TestGateResult:
    """Tests for GateResult dataclass."""

    def test_allowed_property(self) -> None:
        """allowed property reflects decision."""
        allowed = GateResult(
            decision=GateDecision.ALLOWED,
            tool_path="file.read",
            required_trust=0,
            current_trust=0,
        )
        denied = GateResult(
            decision=GateDecision.DENIED,
            tool_path="file.write",
            required_trust=2,
            current_trust=0,
        )

        assert allowed.allowed is True
        assert denied.allowed is False

    def test_requires_confirmation_property(self) -> None:
        """requires_confirmation property reflects decision."""
        confirm = GateResult(
            decision=GateDecision.REQUIRES_CONFIRMATION,
            tool_path="file.write",
            required_trust=2,
            current_trust=2,
        )
        allowed = GateResult(
            decision=GateDecision.ALLOWED,
            tool_path="file.read",
            required_trust=0,
            current_trust=0,
        )

        assert confirm.requires_confirmation is True
        assert allowed.requires_confirmation is False
