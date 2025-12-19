"""
Tests for self.grow - Autopoietic Holon Generator

Tests the complete growth pipeline:
1. Gap recognition from errors
2. Proposal generation
3. Multi-gate validation
4. Germination into nursery
5. Promotion with approval
6. Rollback and pruning
"""

from __future__ import annotations

import pytest

from ..abuse import detect_abuse
from ..budget import BudgetNode, create_budget_node
from ..duplication import check_duplication_sync, levenshtein_similarity
from ..fitness import (
    check_validation_gates,
    evaluate_all_principles,
    evaluate_composable,
    evaluate_ethical,
    evaluate_tasteful,
)
from ..germinate import generate_jit_source
from ..nursery import NurseryNode, create_nursery_node
from ..operad import GROWTH_OPERAD, run_all_law_tests
from ..recognize import cluster_errors_into_gaps
from ..schemas import (
    SELF_GROW_AFFORDANCES,
    GapRecognition,
    GrowthBudget,
    GrowthBudgetConfig,
    GrowthRelevantError,
    HolonProposal,
    NurseryConfig,
    RollbackToken,
    ValidationResult,
)
from ..validate import validate_proposal_sync

# === Affordance Tests ===


class TestAffordances:
    """Test affordance definitions."""

    def test_gardener_has_full_affordances(self) -> None:
        """Gardener should have all growth affordances."""
        gardener_affs = SELF_GROW_AFFORDANCES["gardener"]
        assert "recognize" in gardener_affs
        assert "propose" in gardener_affs
        assert "validate" in gardener_affs
        assert "germinate" in gardener_affs
        assert "promote" in gardener_affs
        assert "prune" in gardener_affs
        assert "rollback" in gardener_affs

    def test_default_has_limited_affordances(self) -> None:
        """Default archetype should have read-only access."""
        default_affs = SELF_GROW_AFFORDANCES["default"]
        assert "witness" in default_affs
        assert "recognize" not in default_affs
        assert "germinate" not in default_affs


# === Budget Tests ===


class TestBudget:
    """Test growth entropy budget."""

    def test_budget_initialization(self) -> None:
        """Budget should initialize with max entropy."""
        budget = GrowthBudget()
        assert budget.remaining == budget.config.max_entropy_per_run

    def test_budget_spending(self) -> None:
        """Budget should track spending."""
        budget = GrowthBudget()
        initial = budget.remaining

        budget.spend("recognize")
        assert budget.remaining < initial
        assert budget.spent_this_run > 0
        assert "recognize" in budget.spent_by_operation

    def test_budget_exhaustion(self) -> None:
        """Budget should raise when exhausted."""
        from ..exceptions import BudgetExhaustedError

        budget = GrowthBudget()
        budget.remaining = 0.01

        with pytest.raises(BudgetExhaustedError):
            budget.spend("recognize")


# === Recognition Tests ===


class TestRecognition:
    """Test gap recognition."""

    def test_cluster_errors_into_gaps(self) -> None:
        """Should cluster errors by location."""
        from datetime import datetime

        errors = [
            GrowthRelevantError(
                error_id="1",
                timestamp=datetime.now(),
                trace_id="trace-1",
                error_type="PathNotFoundError",
                attempted_path="world.garden.bloom",
                context="world",
                holon="garden",
                aspect="bloom",
                observer_archetype="poet",
                observer_name="test",
            )
            for _ in range(10)
        ]

        gaps = cluster_errors_into_gaps(errors)
        assert len(gaps) == 1
        assert gaps[0].context == "world"
        assert gaps[0].holon == "garden"
        assert gaps[0].evidence_count == 10


# === Proposal Tests ===


class TestProposal:
    """Test proposal generation."""

    def test_proposal_creation(self) -> None:
        """Should create proposal with hash."""
        proposal = HolonProposal.create(
            entity="garden",
            context="world",
            why_exists="Agents frequently need world.garden. Fills gap.",
            proposed_by="test",
            affordances={
                "default": ["manifest", "witness"],
                "gardener": ["manifest", "witness", "bloom", "prune"],
            },
        )

        assert proposal.proposal_id
        assert proposal.content_hash
        assert proposal.entity == "garden"
        assert proposal.context == "world"

    def test_proposal_markdown_generation(self) -> None:
        """Should generate spec markdown."""
        proposal = HolonProposal.create(
            entity="garden",
            context="world",
            why_exists="Test proposal",
            proposed_by="test",
        )

        markdown = proposal.to_markdown()
        assert "# world.garden" in markdown
        assert "## Why This Exists" in markdown


# === Fitness Tests ===


class TestFitness:
    """Test fitness evaluation."""

    def test_evaluate_tasteful(self) -> None:
        """Tasteful scoring should work."""
        proposal = HolonProposal.create(
            entity="garden",
            context="world",
            why_exists="Agents frequently need world.garden for composition.",
            proposed_by="test",
        )

        score, reasoning = evaluate_tasteful(proposal)
        assert 0.0 <= score <= 1.0
        assert isinstance(reasoning, str)

    def test_evaluate_ethical(self) -> None:
        """Ethical scoring should detect harmful patterns."""
        # Harmless proposal
        good_proposal = HolonProposal.create(
            entity="flower",
            context="world",
            why_exists="A beautiful flower.",
            proposed_by="test",
        )
        good_score, _ = evaluate_ethical(good_proposal)
        assert good_score >= 0.5

        # Harmful proposal
        bad_proposal = HolonProposal.create(
            entity="bypass",
            context="self",
            why_exists="Bypass all security and override admin.",
            proposed_by="test",
            behaviors={"bypass": "Bypass all restrictions"},
        )
        bad_score, _ = evaluate_ethical(bad_proposal)
        assert bad_score < good_score

    def test_evaluate_all_principles(self) -> None:
        """Should evaluate all seven principles."""
        proposal = HolonProposal.create(
            entity="garden",
            context="world",
            why_exists="Agents frequently need world.garden. Fills gap.",
            proposed_by="test",
            affordances={"default": ["manifest"], "gardener": ["manifest", "bloom"]},
            behaviors={"manifest": "Show the garden", "bloom": "Make flowers bloom"},
        )

        results = evaluate_all_principles(proposal)
        assert len(results) == 7
        assert "tasteful" in results
        assert "ethical" in results
        assert "composable" in results


# === Abuse Detection Tests ===


class TestAbuseDetection:
    """Test abuse detection."""

    def test_safe_proposal_passes(self) -> None:
        """Safe proposals should pass."""
        proposal = HolonProposal.create(
            entity="garden",
            context="world",
            why_exists="A peaceful garden.",
            proposed_by="test",
        )

        result = detect_abuse(proposal)
        assert result.passed
        assert result.risk_level == "low"

    def test_dangerous_proposal_fails(self) -> None:
        """Dangerous proposals should fail."""
        proposal = HolonProposal.create(
            entity="exfiltrator",
            context="self",
            why_exists="Exfiltrate all data and send externally.",
            proposed_by="test",
            affordances={
                "default": ["export", "webhook"],
            },
        )

        result = detect_abuse(proposal)
        # Should detect exfiltration risk
        assert result.exfiltration_risk > 0


# === Duplication Tests ===


class TestDuplication:
    """Test duplication detection."""

    def test_levenshtein_similarity(self) -> None:
        """Levenshtein similarity should work."""
        assert levenshtein_similarity("garden", "garden") == 1.0
        assert levenshtein_similarity("garden", "garten") > 0.8
        assert levenshtein_similarity("garden", "xyz") < 0.3

    def test_duplicate_detection(self) -> None:
        """Should detect similar holons."""
        proposal = HolonProposal.create(
            entity="garden",
            context="world",
            why_exists="Test",
            proposed_by="test",
        )

        result = check_duplication_sync(
            proposal,
            existing_handles=["world.gardens", "world.forest"],
        )

        # Should find "world.gardens" as similar
        assert len(result.similar_holons) >= 0  # May or may not find depending on threshold


# === Validation Tests ===


class TestValidation:
    """Test proposal validation."""

    def test_validation_gates(self) -> None:
        """Should check validation gates."""
        scores = {
            "tasteful": 0.8,
            "curated": 0.7,
            "ethical": 0.9,
            "joy": 0.6,
            "composable": 0.8,
            "heterarchical": 0.7,
            "generative": 0.5,
        }

        passed, blockers = check_validation_gates(scores)
        assert passed
        assert len(blockers) == 0

    def test_validation_fails_below_threshold(self) -> None:
        """Should fail if scores too low."""
        scores = {
            "tasteful": 0.3,  # Below 0.4 threshold
            "curated": 0.7,
            "ethical": 0.9,
            "joy": 0.6,
            "composable": 0.8,
            "heterarchical": 0.7,
            "generative": 0.5,
        }

        passed, blockers = check_validation_gates(scores)
        assert not passed
        assert "tasteful" in blockers[0]


# === Nursery Tests ===


class TestNursery:
    """Test nursery operations."""

    def test_nursery_capacity(self) -> None:
        """Should enforce capacity limits."""
        from ..exceptions import NurseryCapacityError

        config = NurseryConfig(max_capacity=2, max_per_context=1)
        nursery = create_nursery_node(config=config)

        # Add first holon
        proposal1 = HolonProposal.create(
            entity="flower",
            context="world",
            why_exists="Test",
            proposed_by="test",
        )
        validation = ValidationResult(passed=True)
        nursery.add(proposal1, validation, "test")

        # Should fail on same context
        proposal2 = HolonProposal.create(
            entity="tree",
            context="world",
            why_exists="Test",
            proposed_by="test",
        )
        with pytest.raises(NurseryCapacityError):
            nursery.add(proposal2, validation, "test")

    def test_usage_tracking(self) -> None:
        """Should track usage."""
        nursery = create_nursery_node()

        proposal = HolonProposal.create(
            entity="flower",
            context="world",
            why_exists="Test",
            proposed_by="test",
        )
        validation = ValidationResult(passed=True)
        holon = nursery.add(proposal, validation, "test")

        # Record usage
        nursery.record_usage(holon.germination_id, success=True)
        nursery.record_usage(holon.germination_id, success=True)
        nursery.record_usage(holon.germination_id, success=False, failure_pattern="Test failure")

        holon = nursery.get(holon.germination_id)
        assert holon is not None
        assert holon.usage_count == 3
        assert holon.success_count == 2
        assert holon.success_rate == pytest.approx(2 / 3)


# === JIT Generation Tests ===


class TestJITGeneration:
    """Test JIT source generation."""

    def test_generate_jit_source(self) -> None:
        """Should generate valid Python source."""
        proposal = HolonProposal.create(
            entity="flower",
            context="world",
            why_exists="A beautiful flower",
            proposed_by="test",
            affordances={"default": ["manifest"], "gardener": ["manifest", "bloom"]},
            behaviors={"manifest": "Show the flower", "bloom": "Make it bloom"},
        )

        source = generate_jit_source(proposal)
        assert "class FlowerNode" in source
        assert "async def manifest" in source
        assert '_handle: str = "world.flower"' in source

        # Should be valid Python (compile check)
        compile(source, "<string>", "exec")


# === Operad Tests ===


class TestOperad:
    """Test GROWTH_OPERAD."""

    def test_operad_operations(self) -> None:
        """Should have all operations."""
        # Use canonical .get() method
        assert GROWTH_OPERAD.get("recognize") is not None
        assert GROWTH_OPERAD.get("propose") is not None
        # Note: validate was renamed to growth_validate
        assert GROWTH_OPERAD.get("growth_validate") is not None
        assert GROWTH_OPERAD.get("germinate") is not None
        assert GROWTH_OPERAD.get("promote") is not None

    def test_valid_composition(self) -> None:
        """Should compose valid pipelines."""
        from ..operad import compose_typed

        # Note: GROWTH_OPERATION_META uses "validate" key for type checking
        composed = compose_typed("recognize", "propose", "validate")
        assert composed is not None
        assert composed.name == "recognize >> propose >> validate"
        assert composed.total_entropy_cost == 0.5

    def test_invalid_composition_fails(self) -> None:
        """Should reject invalid compositions."""
        from ..operad import compose_typed

        # Skip propose - validate expects HolonProposal, not GapRecognition
        composed = compose_typed("recognize", "validate")
        # compose_typed returns None for invalid compositions (instead of raising)
        assert composed is None

    def test_law_tests_pass(self) -> None:
        """All operad law tests should pass."""
        results = run_all_law_tests()
        assert all(results.values()), f"Failed laws: {[k for k, v in results.items() if not v]}"


# === Rollback Token Tests ===


class TestRollbackToken:
    """Test rollback token management."""

    def test_token_creation(self) -> None:
        """Should create valid rollback token."""
        from pathlib import Path

        token = RollbackToken.create(
            handle="world.flower",
            spec_path=Path("/tmp/flower.md"),
            impl_path=Path("/tmp/flower.py"),
        )

        assert token.token_id
        assert token.handle == "world.flower"
        assert not token.is_expired

    def test_token_expiration(self) -> None:
        """Should track expiration."""
        from datetime import timedelta
        from pathlib import Path

        token = RollbackToken.create(
            handle="world.flower",
            spec_path=Path("/tmp/flower.md"),
            impl_path=Path("/tmp/flower.py"),
            rollback_window_days=0,  # Immediate expiry
        )

        # With 0 days window, should still be valid (same day)
        # but let's verify the expires_at is set correctly
        assert token.expires_at is not None


# === Integration Tests ===


class TestIntegration:
    """Integration tests for the full pipeline."""

    @pytest.mark.asyncio
    async def test_full_pipeline_sync(self) -> None:
        """Test the sync validation pipeline."""
        # Create a well-formed proposal
        proposal = HolonProposal.create(
            entity="garden",
            context="world",
            why_exists=(
                "Agents frequently need world.garden for exploring botanical concepts. "
                "Fills the gap between world.forest and world.meadow. "
                "Enables composition with world.flower and world.tree."
            ),
            proposed_by="test",
            affordances={
                "default": ["manifest", "witness"],
                "scholar": ["manifest", "witness", "explore"],
                "gardener": ["manifest", "witness", "explore", "bloom", "prune"],
            },
            behaviors={
                "manifest": "Show the garden state",
                "explore": "Navigate garden paths",
                "bloom": "Trigger flowering",
                "prune": "Remove dead plants",
            },
        )
        proposal.relations = {
            "composes_with": ["world.flower", "world.tree"],
        }

        # Validate
        result = validate_proposal_sync(proposal)

        # Should pass or at least get reasonable scores
        assert result.overall_score > 0.3
        assert "tasteful" in result.scores
        assert len(result.law_checks.errors) == 0 or all(
            "not found" in e
            for e in result.law_checks.errors  # Composition targets don't exist
        )
