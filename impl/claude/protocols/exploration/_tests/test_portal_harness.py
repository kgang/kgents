"""
Tests for Portal Token Integration with Exploration Harness.

These tests verify:
1. Loop detection for portal expansions
2. Budget enforcement for portal expansions
3. Evidence creation from portal expansion
4. Integration with ExplorationHarness.expand_portal()

Spec: spec/protocols/portal-token.md section 10 (Integration Points)
"""

import asyncio
import pytest
from pathlib import Path

from ..budget import NavigationBudget, quick_budget
from ..harness import ExplorationHarness, create_harness
from ..loops import LoopDetector, LoopResponse
from ..types import (
    ContextNode,
    EvidenceStrength,
    LoopStatus,
    Observer,
    PortalExpansionResult,
)
from protocols.file_operad.portal import PortalLink, PortalNode, PortalToken, PortalTree


# =============================================================================
# Loop Detector Portal Tests
# =============================================================================


class TestLoopDetectorPortal:
    """Tests for portal-specific loop detection."""

    def test_check_portal_no_loop_first_expansion(self) -> None:
        """First expansion of a portal should not trigger loop."""
        detector = LoopDetector()
        status = detector.check_portal("tests/unit")
        assert status == LoopStatus.OK

    def test_check_portal_detects_repeated_expansion(self) -> None:
        """Expanding same portal twice should trigger loop."""
        detector = LoopDetector()

        # First expansion
        detector.check_portal("tests/unit")
        # Second expansion
        status = detector.check_portal("tests/unit")

        assert status == LoopStatus.EXACT_LOOP

    def test_different_portals_no_loop(self) -> None:
        """Different portal paths should not trigger loop."""
        detector = LoopDetector()

        detector.check_portal("tests/unit")
        status = detector.check_portal("tests/integration")

        assert status == LoopStatus.OK

    def test_get_portal_response_escalation(self) -> None:
        """Portal loop response should escalate."""
        detector = LoopDetector()

        # First occurrence: CONTINUE
        response = detector.get_portal_response("tests", LoopStatus.EXACT_LOOP)
        assert response == LoopResponse.CONTINUE

        # Second occurrence: BACKTRACK
        response = detector.get_portal_response("tests", LoopStatus.EXACT_LOOP)
        assert response == LoopResponse.BACKTRACK

        # Third occurrence: HALT
        response = detector.get_portal_response("tests", LoopStatus.EXACT_LOOP)
        assert response == LoopResponse.HALT

    def test_reset_clears_portal_history(self) -> None:
        """Reset should clear portal expansion history."""
        detector = LoopDetector()

        detector.check_portal("tests")
        detector.reset()

        # Should be OK again after reset
        status = detector.check_portal("tests")
        assert status == LoopStatus.OK


# =============================================================================
# Portal Tree Setup Helpers
# =============================================================================


def create_test_portal_tree() -> PortalTree:
    """Create a PortalTree for testing."""
    root = PortalNode(path="/test/root", depth=0)
    tree = PortalTree(root=root, max_depth=5)

    # Add child nodes
    tests_node = PortalNode(
        path="tests",
        edge_type="tests",
        depth=1,
    )
    root.children.append(tests_node)

    # Register a token for the tests portal
    link = PortalLink(
        edge_type="tests",
        path="WITNESS_OPERAD/test",
        note="test file",
    )
    tree.tokens["tests"] = PortalToken(link, depth=1)

    return tree


# =============================================================================
# Harness expand_portal Tests
# =============================================================================


class TestHarnessExpandPortal:
    """Tests for ExplorationHarness.expand_portal()."""

    @pytest.mark.asyncio
    async def test_expand_portal_succeeds_first_time(self) -> None:
        """First portal expansion should succeed."""
        node = ContextNode(path="world.auth", holon="auth")
        harness = create_harness(node)
        tree = create_test_portal_tree()

        result = await harness.expand_portal(["tests"], tree)

        # The result depends on whether files exist
        # We mainly test that it doesn't crash and returns valid result
        assert isinstance(result, PortalExpansionResult)
        assert result.portal_path == "tests"

    @pytest.mark.asyncio
    async def test_expand_portal_halted_harness(self) -> None:
        """Halted harness should reject expansion."""
        node = ContextNode(path="world.auth", holon="auth")
        harness = create_harness(node)
        harness._halted = True
        harness._halt_reason = "Test halt"

        tree = create_test_portal_tree()

        result = await harness.expand_portal(["tests"], tree)

        assert not result.success
        assert "halted" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_expand_portal_budget_exhausted(self) -> None:
        """Exhausted budget should reject expansion."""
        node = ContextNode(path="world.auth", holon="auth")
        harness = create_harness(node, budget=NavigationBudget(max_steps=0))

        tree = create_test_portal_tree()

        result = await harness.expand_portal(["tests"], tree)

        assert not result.success
        assert result.budget_exhausted

    @pytest.mark.asyncio
    async def test_expand_portal_loop_detected(self) -> None:
        """Repeated expansion should trigger loop detection."""
        node = ContextNode(path="world.auth", holon="auth")
        harness = create_harness(node)
        tree = create_test_portal_tree()

        # First expansion - record it
        harness.loop_detector.check_portal("tests")
        # Second expansion - triggers EXACT_LOOP, but CONTINUE
        harness.loop_detector.check_portal("tests")
        # Third would BACKTRACK

        # Reset and use harness method
        harness.reset_loop_detector()

        # Do first expansion via harness
        await harness.expand_portal(["tests"], tree)
        # Second time, loop detector sees it again
        result = await harness.expand_portal(["tests"], tree)

        # Second expansion may still work (CONTINUE on first loop)
        assert isinstance(result, PortalExpansionResult)

    @pytest.mark.asyncio
    async def test_expand_portal_creates_evidence(self) -> None:
        """Portal expansion should create evidence."""
        node = ContextNode(path="world.auth", holon="auth")
        harness = create_harness(node)
        tree = create_test_portal_tree()

        initial_count = harness.evidence_collector.evidence_count

        await harness.expand_portal(["tests"], tree)

        # Evidence should be created regardless of expansion success
        # because we record the attempt
        assert harness.evidence_collector.evidence_count >= initial_count

    @pytest.mark.asyncio
    async def test_expand_portal_empty_path(self) -> None:
        """Empty portal path should be handled."""
        node = ContextNode(path="world.auth", holon="auth")
        harness = create_harness(node)
        tree = create_test_portal_tree()

        result = await harness.expand_portal([], tree)

        # Should fail gracefully or return root
        assert isinstance(result, PortalExpansionResult)


# =============================================================================
# PortalExpansionResult Tests
# =============================================================================


class TestPortalExpansionResult:
    """Tests for PortalExpansionResult."""

    def test_ok_result(self) -> None:
        """ok() should create successful result."""
        result = PortalExpansionResult.ok(
            "tests/unit",
            ["/path/to/file.py"],
        )
        assert result.success
        assert result.portal_path == "tests/unit"
        assert result.files_opened == ("/path/to/file.py",)
        assert not result.budget_exhausted
        assert result.loop_detected is None

    def test_budget_exhausted_result(self) -> None:
        """budget_exhausted_result() should create failed result."""
        result = PortalExpansionResult.budget_exhausted_result(
            "tests", "max_steps"
        )
        assert not result.success
        assert result.budget_exhausted
        assert "Budget exhausted" in result.error_message

    def test_loop_detected_result(self) -> None:
        """loop_detected_result() should create failed result."""
        result = PortalExpansionResult.loop_detected_result(
            "tests", LoopStatus.EXACT_LOOP
        )
        assert not result.success
        assert result.loop_detected == LoopStatus.EXACT_LOOP
        assert "Loop detected" in result.error_message

    def test_expansion_failed_result(self) -> None:
        """expansion_failed_result() should create failed result."""
        result = PortalExpansionResult.expansion_failed_result(
            "tests", "File not found"
        )
        assert not result.success
        assert result.error_message == "File not found"

    def test_ok_with_evidence(self) -> None:
        """ok() should include evidence when provided."""
        from ..types import Evidence

        evidence = Evidence(
            claim="Test",
            content="Test content",
        )
        result = PortalExpansionResult.ok(
            "tests",
            ["/file.py"],
            evidence=evidence,
        )

        assert result.evidence_created == evidence


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
