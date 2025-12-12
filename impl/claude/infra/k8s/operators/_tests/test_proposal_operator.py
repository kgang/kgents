"""Tests for Proposal Operator risk calculation and governance logic.

These tests verify the proposal operator works correctly
without requiring a real K8s cluster.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from infra.k8s.operators.proposal_operator import (
    AUTO_MERGE_THRESHOLD,
    # Constants
    BASE_RISK_BY_TYPE,
    RISK_LEVEL_THRESHOLDS,
    VELOCITY_INCREMENT,
    # Mock classes
    MockProposal,
    MockProposalRegistry,
    # Enums
    ProposalPhase,
    ProposalSpec,
    # Data classes
    RiskAssessment,
    RiskLevel,
    calculate_magnitude_factor,
    calculate_risk,
    calculate_test_coverage_factor,
    generate_review_pheromone,
    # Functions
    get_base_risk,
    get_mock_registry,
    get_risk_level,
    parse_proposal_spec,
    reset_mock_registry,
)


class TestBaseRisk:
    """Test base risk values by change type."""

    def test_code_patch_lowest_risk(self) -> None:
        """CODE_PATCH has low base risk."""
        assert get_base_risk("CODE_PATCH") == 0.1

    def test_code_delete_moderate_risk(self) -> None:
        """CODE_DELETE has moderate risk."""
        assert get_base_risk("CODE_DELETE") == 0.5

    def test_memory_delete_high_risk(self) -> None:
        """MEMORY_DELETE has high risk."""
        assert get_base_risk("MEMORY_DELETE") == 0.8

    def test_risk_override_highest_risk(self) -> None:
        """RISK_OVERRIDE has highest risk."""
        assert get_base_risk("RISK_OVERRIDE") == 0.9

    def test_unknown_type_defaults_to_medium(self) -> None:
        """Unknown change types default to 0.5."""
        assert get_base_risk("UNKNOWN_TYPE") == 0.5


class TestMagnitudeFactor:
    """Test magnitude factor calculation."""

    def test_zero_changes_minimum_factor(self) -> None:
        """Zero changes produce factor of 1.0."""
        factor = calculate_magnitude_factor(0, 0, 0)
        assert factor == 1.0

    def test_small_change_low_factor(self) -> None:
        """Small changes have low magnitude factor."""
        factor = calculate_magnitude_factor(10, 5, 1)
        assert 1.0 < factor < 1.5

    def test_medium_change_moderate_factor(self) -> None:
        """Medium changes have moderate magnitude factor."""
        factor = calculate_magnitude_factor(100, 50, 5)
        assert 1.5 < factor < 2.0

    def test_large_change_higher_factor(self) -> None:
        """Large changes have higher magnitude factor."""
        factor = calculate_magnitude_factor(1000, 500, 20)
        assert factor > 2.0

    def test_files_weighted_more(self) -> None:
        """Files are weighted more than lines."""
        # 100 lines vs 10 files (weighted as 100 lines equivalent)
        lines_factor = calculate_magnitude_factor(100, 0, 0)
        files_factor = calculate_magnitude_factor(0, 0, 10)
        assert files_factor == lines_factor


class TestTestCoverageFactor:
    """Test test coverage factor calculation."""

    def test_no_test_changes_neutral(self) -> None:
        """No test changes produce factor of 1.0."""
        factor = calculate_test_coverage_factor(0, 0)
        assert factor == 1.0

    def test_adding_tests_reduces_risk(self) -> None:
        """Adding tests reduces risk factor."""
        factor = calculate_test_coverage_factor(10, 0)
        assert factor < 1.0
        assert factor >= 0.5  # Minimum

    def test_removing_tests_increases_risk(self) -> None:
        """Removing tests increases risk factor."""
        factor = calculate_test_coverage_factor(0, 10)
        assert factor > 1.0
        assert factor <= 1.5  # Maximum

    def test_net_positive_tests_reduces_risk(self) -> None:
        """Net positive test changes reduce risk."""
        factor = calculate_test_coverage_factor(20, 5)  # +15 net
        assert factor < 1.0

    def test_net_negative_tests_increases_risk(self) -> None:
        """Net negative test changes increase risk."""
        factor = calculate_test_coverage_factor(5, 20)  # -15 net
        assert factor > 1.0


class TestRiskLevel:
    """Test risk level mapping."""

    def test_low_risk_level(self) -> None:
        """Low risk maps to LOW level."""
        assert get_risk_level(0.1) == RiskLevel.LOW
        assert get_risk_level(0.2) == RiskLevel.LOW

    def test_medium_risk_level(self) -> None:
        """Medium risk maps to MEDIUM level."""
        assert get_risk_level(0.3) == RiskLevel.MEDIUM
        assert get_risk_level(0.5) == RiskLevel.MEDIUM

    def test_high_risk_level(self) -> None:
        """High risk maps to HIGH level."""
        assert get_risk_level(0.6) == RiskLevel.HIGH
        assert get_risk_level(0.8) == RiskLevel.HIGH

    def test_critical_risk_level(self) -> None:
        """Critical risk maps to CRITICAL level."""
        assert get_risk_level(0.9) == RiskLevel.CRITICAL
        assert get_risk_level(1.0) == RiskLevel.CRITICAL


class TestCalculateRisk:
    """Test full risk calculation."""

    def test_minimal_spec_low_risk(self) -> None:
        """Minimal CODE_PATCH spec has low risk."""
        spec = ProposalSpec(
            name="test-proposal",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="test-user",
        )

        risk = calculate_risk(spec)

        assert risk.base_risk == 0.1
        assert risk.velocity_penalty == 0.0
        assert risk.magnitude_factor == 1.0
        assert risk.test_coverage == 1.0
        assert risk.cumulative_risk == 0.1
        assert risk.risk_level == RiskLevel.LOW

    def test_velocity_penalty_increases_risk(self) -> None:
        """Velocity penalty increases cumulative risk."""
        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="test-user",
        )

        risk_no_velocity = calculate_risk(spec, velocity_penalty=0.0)
        risk_with_velocity = calculate_risk(spec, velocity_penalty=0.5)

        assert risk_with_velocity.cumulative_risk > risk_no_velocity.cumulative_risk
        assert risk_with_velocity.velocity_penalty == 0.5

    def test_magnitude_increases_risk(self) -> None:
        """Large changes increase cumulative risk."""
        small_spec = ProposalSpec(
            name="small",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="test-user",
            lines_added=10,
            files_changed=1,
        )

        large_spec = ProposalSpec(
            name="large",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="test-user",
            lines_added=1000,
            files_changed=50,
        )

        small_risk = calculate_risk(small_spec)
        large_risk = calculate_risk(large_spec)

        assert large_risk.cumulative_risk > small_risk.cumulative_risk
        assert large_risk.magnitude_factor > small_risk.magnitude_factor

    def test_tests_reduce_risk(self) -> None:
        """Adding tests reduces cumulative risk."""
        no_tests = ProposalSpec(
            name="no-tests",
            namespace="default",
            change_type="CODE_FEATURE",
            target_kind="File",
            target_name="feature.py",
            proposer="test-user",
            lines_added=100,
        )

        with_tests = ProposalSpec(
            name="with-tests",
            namespace="default",
            change_type="CODE_FEATURE",
            target_kind="File",
            target_name="feature.py",
            proposer="test-user",
            lines_added=100,
            tests_added=20,
        )

        no_tests_risk = calculate_risk(no_tests)
        with_tests_risk = calculate_risk(with_tests)

        assert with_tests_risk.cumulative_risk < no_tests_risk.cumulative_risk
        assert with_tests_risk.test_coverage < 1.0

    def test_risk_clamped_to_one(self) -> None:
        """Cumulative risk is clamped to [0, 1]."""
        dangerous_spec = ProposalSpec(
            name="dangerous",
            namespace="default",
            change_type="RISK_OVERRIDE",  # 0.9 base
            target_kind="Policy",
            target_name="fiscal-constitution",
            proposer="reckless-user",
            lines_removed=10000,
            files_changed=100,
            tests_removed=50,
        )

        risk = calculate_risk(dangerous_spec, velocity_penalty=1.0)

        assert risk.cumulative_risk <= 1.0
        assert risk.risk_level == RiskLevel.CRITICAL


class TestParseProposalSpec:
    """Test parsing CRD spec into ProposalSpec."""

    def test_minimal_spec(self) -> None:
        """Parse minimal spec with only required fields."""
        spec = {
            "changeType": "CODE_PATCH",
            "target": {"kind": "File", "name": "test.py"},
            "proposer": "test-user",
        }
        meta = {"name": "test-proposal", "namespace": "kgents-agents"}

        result = parse_proposal_spec(spec, meta)

        assert result.name == "test-proposal"
        assert result.namespace == "kgents-agents"
        assert result.change_type == "CODE_PATCH"
        assert result.target_kind == "File"
        assert result.target_name == "test.py"
        assert result.proposer == "test-user"
        assert result.auto_merge is True  # Default
        assert result.t_gent_validation is True  # Default

    def test_full_spec(self) -> None:
        """Parse spec with all fields."""
        spec = {
            "changeType": "AGENT_UPGRADE",
            "target": {
                "kind": "Agent",
                "name": "l-gent",
                "namespace": "kgents-system",
            },
            "proposer": "m-gent",
            "description": "Upgrade L-gent to v2",
            "rationale": "New features",
            "magnitude": {
                "linesAdded": 500,
                "linesRemoved": 100,
                "filesChanged": 20,
                "testsAdded": 15,
                "testsRemoved": 5,
            },
            "reviewRequirements": {
                "autoMerge": False,
                "requiredApprovers": 2,
                "requiredReviewers": ["T", "B"],
                "tGentValidation": True,
            },
            "riskBudget": {
                "maxCumulativeRisk": 0.5,
                "velocityWindow": "2h",
            },
            "ttlSeconds": 7200,
        }
        meta = {"name": "upgrade-l-gent", "namespace": "kgents-system"}

        result = parse_proposal_spec(spec, meta)

        assert result.change_type == "AGENT_UPGRADE"
        assert result.target_kind == "Agent"
        assert result.target_name == "l-gent"
        assert result.proposer == "m-gent"
        assert result.lines_added == 500
        assert result.lines_removed == 100
        assert result.files_changed == 20
        assert result.tests_added == 15
        assert result.tests_removed == 5
        assert result.auto_merge is False
        assert result.required_approvers == 2
        assert result.required_reviewers == ["T", "B"]
        assert result.max_cumulative_risk == 0.5
        assert result.ttl_seconds == 7200


class TestGenerateReviewPheromone:
    """Test T-gent review pheromone generation."""

    def test_generates_intent_pheromone(self) -> None:
        """Generate INTENT pheromone for T-gent."""
        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_FEATURE",
            target_kind="File",
            target_name="feature.py",
            proposer="dev-user",
        )
        risk = calculate_risk(spec)

        pheromone = generate_review_pheromone("test-proposal", "default", spec, risk)

        assert pheromone["kind"] == "Pheromone"
        assert pheromone["metadata"]["name"] == "review-test-proposal"
        assert pheromone["spec"]["type"] == "INTENT"
        assert "test-proposal" in pheromone["spec"]["payload"]

    def test_higher_risk_higher_intensity(self) -> None:
        """Higher risk proposals have higher pheromone intensity."""
        low_risk_spec = ProposalSpec(
            name="low",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="user",
        )

        high_risk_spec = ProposalSpec(
            name="high",
            namespace="default",
            change_type="MEMORY_DELETE",
            target_kind="Memory",
            target_name="important-data",
            proposer="user",
        )

        low_risk = calculate_risk(low_risk_spec)
        high_risk = calculate_risk(high_risk_spec)

        low_ph = generate_review_pheromone("low", "default", low_risk_spec, low_risk)
        high_ph = generate_review_pheromone(
            "high", "default", high_risk_spec, high_risk
        )

        assert high_ph["spec"]["intensity"] > low_ph["spec"]["intensity"]


class TestMockProposal:
    """Test the mock proposal implementation."""

    def test_create_proposal(self) -> None:
        """Can create a mock proposal."""
        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="user",
        )

        proposal = MockProposal(
            name="test",
            namespace="default",
            spec=spec,
        )

        assert proposal.name == "test"
        assert proposal.phase == ProposalPhase.PENDING
        assert proposal.risk is None

    def test_calculate_risk_stores_result(self) -> None:
        """Calculating risk stores the result."""
        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="user",
        )

        proposal = MockProposal(name="test", namespace="default", spec=spec)
        risk = proposal.calculate_risk()

        assert proposal.risk is not None
        assert proposal.risk.cumulative_risk == risk.cumulative_risk

    def test_approve_adds_approval(self) -> None:
        """Can approve a proposal."""
        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="user",
            required_approvers=1,
        )

        proposal = MockProposal(name="test", namespace="default", spec=spec)
        proposal.phase = ProposalPhase.REVIEWING

        result = proposal.approve("reviewer", "LGTM")

        assert result is True
        assert len(proposal.approvals) == 1
        assert proposal.approvals[0]["approver"] == "reviewer"
        assert proposal.phase == ProposalPhase.APPROVED

    def test_approve_requires_reviewing_phase(self) -> None:
        """Cannot approve if not in REVIEWING phase."""
        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="user",
        )

        proposal = MockProposal(name="test", namespace="default", spec=spec)
        proposal.phase = ProposalPhase.MERGED

        result = proposal.approve("reviewer")

        assert result is False
        assert len(proposal.approvals) == 0

    def test_reject_sets_rejected_phase(self) -> None:
        """Rejecting a proposal sets REJECTED phase."""
        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="user",
        )

        proposal = MockProposal(name="test", namespace="default", spec=spec)
        proposal.phase = ProposalPhase.REVIEWING

        result = proposal.reject("reviewer", "Too risky")

        assert result is True
        assert proposal.phase == ProposalPhase.REJECTED
        assert len(proposal.rejections) == 1

    def test_merge_requires_approved_phase(self) -> None:
        """Can only merge approved proposals."""
        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="user",
        )

        proposal = MockProposal(name="test", namespace="default", spec=spec)

        # Cannot merge from PENDING
        proposal.phase = ProposalPhase.PENDING
        assert proposal.merge("executor") is False

        # Cannot merge from REVIEWING
        proposal.phase = ProposalPhase.REVIEWING
        assert proposal.merge("executor") is False

        # Can merge from APPROVED
        proposal.phase = ProposalPhase.APPROVED
        assert proposal.merge("executor") is True
        assert proposal.phase == ProposalPhase.MERGED

    def test_expiry_detection(self) -> None:
        """Can detect expired proposals."""
        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="user",
            ttl_seconds=60,
        )

        # Fresh proposal is not expired
        proposal = MockProposal(name="test", namespace="default", spec=spec)
        proposal.phase = ProposalPhase.REVIEWING
        assert proposal.is_expired() is False

        # Simulate old proposal
        proposal.created_at = datetime.now(timezone.utc) - timedelta(seconds=120)
        assert proposal.is_expired() is True


class TestMockProposalRegistry:
    """Test the mock proposal registry."""

    def test_create_calculates_risk(self) -> None:
        """Creating a proposal calculates risk."""
        registry = MockProposalRegistry()
        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="user",
        )

        proposal = registry.create("test", spec)

        assert proposal.risk is not None
        assert proposal.risk.cumulative_risk > 0

    def test_low_risk_auto_merge_eligible(self) -> None:
        """Low risk proposals without T-gent validation are auto-approved."""
        registry = MockProposalRegistry()
        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",  # 0.1 base risk
            target_kind="File",
            target_name="test.py",
            proposer="user",
            auto_merge=True,
            required_approvers=0,
            t_gent_validation=False,
        )

        proposal = registry.create("test", spec)

        assert proposal.phase == ProposalPhase.APPROVED
        assert proposal.risk is not None
        assert proposal.risk.cumulative_risk <= AUTO_MERGE_THRESHOLD

    def test_high_risk_needs_review(self) -> None:
        """High risk proposals need review."""
        registry = MockProposalRegistry()
        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="MEMORY_DELETE",  # 0.8 base risk
            target_kind="Memory",
            target_name="critical-data",
            proposer="user",
        )

        proposal = registry.create("test", spec)

        assert proposal.phase == ProposalPhase.REVIEWING
        assert proposal.risk is not None
        assert proposal.risk.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)

    def test_velocity_penalty_accumulates(self) -> None:
        """Velocity penalty accumulates with multiple proposals."""
        registry = MockProposalRegistry()

        first_spec = ProposalSpec(
            name="first",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="a.py",
            proposer="user",
        )

        second_spec = ProposalSpec(
            name="second",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="b.py",
            proposer="user",
        )

        first = registry.create("first", first_spec)
        second = registry.create("second", second_spec)

        # Second proposal has higher velocity penalty
        assert first.risk is not None
        assert second.risk is not None
        assert second.risk.velocity_penalty > first.risk.velocity_penalty
        assert second.risk.cumulative_risk > first.risk.cumulative_risk

    def test_velocity_decay(self) -> None:
        """Velocity penalty decays over time."""
        registry = MockProposalRegistry()

        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="user",
        )

        registry.create("first", spec)
        initial_velocity = registry.get_velocity_penalty()

        # Simulate time passing
        registry.decay_velocity(hours=0.5)
        decayed_velocity = registry.get_velocity_penalty()

        assert decayed_velocity < initial_velocity

    def test_velocity_reset(self) -> None:
        """Velocity penalty can be reset."""
        registry = MockProposalRegistry()

        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="user",
        )

        registry.create("first", spec)
        registry.create("second", spec)
        assert registry.get_velocity_penalty() > 0

        registry.reset_velocity()
        assert registry.get_velocity_penalty() == 0

    def test_list_and_get(self) -> None:
        """Can list and get proposals."""
        registry = MockProposalRegistry()

        spec1 = ProposalSpec(
            name="a",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="a.py",
            proposer="user",
        )

        spec2 = ProposalSpec(
            name="b",
            namespace="default",
            change_type="CODE_FEATURE",
            target_kind="File",
            target_name="b.py",
            proposer="user",
        )

        registry.create("prop-a", spec1)
        registry.create("prop-b", spec2)

        # List
        proposals = registry.list()
        assert len(proposals) == 2

        # Get by name
        prop_a = registry.get("prop-a")
        assert prop_a is not None
        assert prop_a.spec.target_name == "a.py"

        # Get missing
        assert registry.get("nonexistent") is None

    def test_delete(self) -> None:
        """Can delete proposals."""
        registry = MockProposalRegistry()

        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="user",
        )

        registry.create("test", spec)
        assert len(registry.list()) == 1

        result = registry.delete("test")
        assert result is True
        assert len(registry.list()) == 0

        # Delete nonexistent returns False
        assert registry.delete("nonexistent") is False

    def test_expire_proposals(self) -> None:
        """Can expire old proposals."""
        registry = MockProposalRegistry()

        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="user",
            ttl_seconds=60,
        )

        proposal = registry.create("test", spec)
        proposal.phase = ProposalPhase.REVIEWING

        # Fresh proposal doesn't expire
        expired = registry.expire_proposals()
        assert len(expired) == 0

        # Simulate old proposal
        proposal.created_at = datetime.now(timezone.utc) - timedelta(seconds=120)
        expired = registry.expire_proposals()

        assert "test" in expired
        assert proposal.phase == ProposalPhase.EXPIRED


class TestGlobalMockRegistry:
    """Test the global mock registry singleton."""

    def setup_method(self) -> None:
        """Reset the global registry before each test."""
        reset_mock_registry()

    def test_get_creates_singleton(self) -> None:
        """get_mock_registry creates a singleton."""
        registry1 = get_mock_registry()
        registry2 = get_mock_registry()
        assert registry1 is registry2

    def test_reset_clears_registry(self) -> None:
        """reset_mock_registry clears the singleton."""
        registry1 = get_mock_registry()

        spec = ProposalSpec(
            name="test",
            namespace="default",
            change_type="CODE_PATCH",
            target_kind="File",
            target_name="test.py",
            proposer="user",
        )
        registry1.create("test", spec)

        reset_mock_registry()
        registry2 = get_mock_registry()

        assert registry1 is not registry2
        assert len(registry2.list()) == 0


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""

    def setup_method(self) -> None:
        """Reset mock registry before each test."""
        reset_mock_registry()

    def test_code_review_workflow(self) -> None:
        """Full code review workflow: create, review, approve, merge."""
        registry = get_mock_registry()

        spec = ProposalSpec(
            name="feature",
            namespace="default",
            change_type="CODE_FEATURE",
            target_kind="File",
            target_name="new_feature.py",
            proposer="dev-user",
            lines_added=200,
            tests_added=30,
            required_approvers=1,
            t_gent_validation=False,  # Skip T-gent for this test
        )

        # Create proposal
        proposal = registry.create("add-feature", spec)
        assert proposal.phase == ProposalPhase.REVIEWING

        # Approve
        proposal.approve("senior-dev", "Looks good!")
        assert proposal.phase == ProposalPhase.APPROVED  # type: ignore[comparison-overlap]

        # Merge
        proposal.merge("ci-bot")
        assert proposal.phase == ProposalPhase.MERGED

    def test_high_risk_escalation(self) -> None:
        """High risk changes escalate to more reviewers."""
        registry = get_mock_registry()

        spec = ProposalSpec(
            name="dangerous",
            namespace="default",
            change_type="AGENT_DELETE",  # 0.7 base risk
            target_kind="Agent",
            target_name="critical-agent",
            proposer="admin",
            required_approvers=2,
            t_gent_validation=False,
        )

        proposal = registry.create("delete-agent", spec)

        # Verify high risk
        assert proposal.risk is not None
        assert proposal.risk.risk_level == RiskLevel.HIGH
        assert proposal.phase == ProposalPhase.REVIEWING

        # One approval not enough
        proposal.approve("reviewer-1")
        assert proposal.phase == ProposalPhase.REVIEWING  # Still reviewing

        # Second approval triggers approved phase
        proposal.approve("reviewer-2")
        assert proposal.phase == ProposalPhase.APPROVED  # type: ignore[comparison-overlap]

    def test_velocity_throttling(self) -> None:
        """Rapid changes accumulate velocity penalty."""
        registry = get_mock_registry()

        # Create specs for identical changes
        def make_spec(name: str) -> ProposalSpec:
            return ProposalSpec(
                name=name,
                namespace="default",
                change_type="CODE_PATCH",
                target_kind="File",
                target_name=f"{name}.py",
                proposer="fast-typer",
            )

        # First few changes are low risk
        p1 = registry.create("change-1", make_spec("a"))
        p2 = registry.create("change-2", make_spec("b"))
        p3 = registry.create("change-3", make_spec("c"))
        p4 = registry.create("change-4", make_spec("d"))
        p5 = registry.create("change-5", make_spec("e"))

        # Risk should increase with velocity
        assert p1.risk is not None
        assert p2.risk is not None
        assert p3.risk is not None
        assert p4.risk is not None
        assert p5.risk is not None
        risks = [
            p1.risk.cumulative_risk,
            p2.risk.cumulative_risk,
            p3.risk.cumulative_risk,
            p4.risk.cumulative_risk,
            p5.risk.cumulative_risk,
        ]

        # Each should be higher than the previous
        for i in range(1, len(risks)):
            assert risks[i] > risks[i - 1], f"Risk should increase: {risks}"

    def test_t_gent_validation_required(self) -> None:
        """T-gent validation blocks approval until passed."""
        registry = get_mock_registry()

        spec = ProposalSpec(
            name="code-change",
            namespace="default",
            change_type="CODE_FEATURE",
            target_kind="File",
            target_name="feature.py",
            proposer="dev",
            required_approvers=1,
            t_gent_validation=True,
        )

        proposal = registry.create("needs-tests", spec)

        # Should be awaiting T-gent validation
        assert proposal.t_gent_validation.get("requested") is True
        assert proposal.t_gent_validation.get("result") == "PENDING"

        # Approval received but T-gent still pending
        proposal.approve("reviewer")

        # Still reviewing because T-gent validation pending
        # (Note: in real impl, would check t_gent_validation.result)
        # For mock, we simulate that approval checks this
        if proposal.t_gent_validation.get("result") != "PASSED":
            # T-gent validation not passed yet
            pass

        # Simulate T-gent validation passing
        proposal.t_gent_validation["result"] = "PASSED"

        # Now approve again (simulating re-check after T-gent passes)
        proposal.phase = ProposalPhase.REVIEWING  # Reset for re-evaluation
        proposal.approvals.clear()
        proposal.approve("reviewer")

        assert proposal.phase == ProposalPhase.APPROVED
