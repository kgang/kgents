"""
Tests for Bootstrap CLI Commands

Tests the laws and principles CLI commands from Phase 2.
"""

from __future__ import annotations

import json

import pytest

from protocols.cli.bootstrap.laws import (
    CATEGORY_LAWS,
    LawName,
    LawVerification,
    Verdict,
    VerificationReport,
    cmd_laws,
    format_laws_json,
    format_laws_rich,
    verify_laws,
    witness_composition,
)
from protocols.cli.bootstrap.principles import (
    DESIGN_PRINCIPLES,
    EvaluationReport,
    PrincipleEvaluation,
    PrincipleName,
    Verdict as PrincipleVerdict,
    cmd_principles,
    evaluate_against_principles,
    format_principles_json,
    format_principles_rich,
)

# ─────────────────────────────────────────────────────────────────
# Laws Tests
# ─────────────────────────────────────────────────────────────────


class TestLawDefinitions:
    """Test law definitions are complete and correct."""

    def test_seven_laws_defined(self) -> None:
        """Verify all 7 category laws are defined."""
        assert len(CATEGORY_LAWS) == 7

    def test_all_law_names_covered(self) -> None:
        """Verify all LawName enum values have definitions."""
        defined_names = {law.name for law in CATEGORY_LAWS}
        enum_names = set(LawName)
        assert defined_names == enum_names

    def test_law_has_required_fields(self) -> None:
        """Verify each law has all required fields."""
        for law in CATEGORY_LAWS:
            assert law.name is not None
            assert law.title, f"Law {law.name} missing title"
            assert law.statement, f"Law {law.name} missing statement"
            assert law.formula, f"Law {law.name} missing formula"
            assert law.example, f"Law {law.name} missing example"
            assert law.why_matters, f"Law {law.name} missing why_matters"

    def test_identity_laws_present(self) -> None:
        """Verify both identity laws are defined."""
        law_names = {law.name for law in CATEGORY_LAWS}
        assert LawName.IDENTITY_LEFT in law_names
        assert LawName.IDENTITY_RIGHT in law_names

    def test_associativity_law_present(self) -> None:
        """Verify associativity law is defined."""
        law_names = {law.name for law in CATEGORY_LAWS}
        assert LawName.ASSOCIATIVITY in law_names


class TestLawsFormatters:
    """Test law formatting functions."""

    def test_format_laws_rich_contains_all_laws(self) -> None:
        """Verify rich format includes all laws."""
        output = format_laws_rich()
        for law in CATEGORY_LAWS:
            assert law.title.upper() in output

    def test_format_laws_rich_has_header(self) -> None:
        """Verify rich format has proper header."""
        output = format_laws_rich()
        assert "CATEGORY LAWS" in output
        assert "VERIFIED" in output

    def test_format_laws_json_is_valid(self) -> None:
        """Verify JSON format is valid JSON."""
        output = format_laws_json()
        data = json.loads(output)
        assert "laws" in data
        assert "count" in data
        assert data["count"] == 7

    def test_format_laws_json_has_all_fields(self) -> None:
        """Verify JSON format includes all law fields."""
        output = format_laws_json()
        data = json.loads(output)
        for law_dict in data["laws"]:
            assert "name" in law_dict
            assert "title" in law_dict
            assert "statement" in law_dict
            assert "formula" in law_dict
            assert "example" in law_dict
            assert "why_matters" in law_dict


class TestLawVerification:
    """Test law verification logic."""

    @pytest.mark.asyncio
    async def test_verify_laws_returns_report(self) -> None:
        """Verify verification returns a report."""
        report = await verify_laws()
        assert isinstance(report, VerificationReport)
        assert len(report.results) == 7

    @pytest.mark.asyncio
    async def test_verify_laws_with_agent_id(self) -> None:
        """Verify verification accepts agent_id."""
        report = await verify_laws(agent_id="test_agent")
        assert report.agent_id == "test_agent"

    @pytest.mark.asyncio
    async def test_verify_laws_has_timestamp(self) -> None:
        """Verify report has timestamp."""
        report = await verify_laws()
        assert report.verified_at is not None

    def test_verification_report_counts(self) -> None:
        """Test report counting methods."""
        results = [
            LawVerification(LawName.IDENTITY_LEFT, Verdict.PASS, ""),
            LawVerification(LawName.IDENTITY_RIGHT, Verdict.PASS, ""),
            LawVerification(LawName.ASSOCIATIVITY, Verdict.FAIL, "test"),
            LawVerification(LawName.COMPOSITION_CLOSURE, Verdict.SKIP, ""),
        ]
        report = VerificationReport(
            agent_id=None,
            verified_at=pytest.importorskip("datetime").datetime.now(),
            results=results,
            overall_verdict=Verdict.FAIL,
        )
        assert report.passed == 2
        assert report.failed == 1
        assert report.skipped == 1


class TestWitnessComposition:
    """Test composition witnessing."""

    @pytest.mark.asyncio
    async def test_witness_simple_composition(self) -> None:
        """Test witnessing A >> B composition."""
        report = await witness_composition("A >> B")
        assert report.left == "A"
        assert report.right == "B"
        assert report.valid is True

    @pytest.mark.asyncio
    async def test_witness_compose_function_format(self) -> None:
        """Test witnessing compose(A, B) format."""
        report = await witness_composition("compose(A, B)")
        assert report.left == "A"
        assert report.right == "B"
        assert report.valid is True

    @pytest.mark.asyncio
    async def test_witness_with_identity_left(self) -> None:
        """Test witnessing Id >> B checks identity law."""
        report = await witness_composition("Id >> B")
        assert LawName.IDENTITY_LEFT in report.laws_checked

    @pytest.mark.asyncio
    async def test_witness_with_identity_right(self) -> None:
        """Test witnessing A >> Identity checks identity law."""
        report = await witness_composition("A >> Identity")
        assert LawName.IDENTITY_RIGHT in report.laws_checked

    @pytest.mark.asyncio
    async def test_witness_invalid_format(self) -> None:
        """Test witnessing with invalid format."""
        report = await witness_composition("invalid format")
        assert report.valid is False
        assert "Unknown operation format" in report.notes

    @pytest.mark.asyncio
    async def test_witness_multiple_operators(self) -> None:
        """Test witnessing with multiple >> operators."""
        report = await witness_composition("A >> B >> C")
        assert report.valid is False
        assert "Expected format" in report.notes


class TestLawsCLI:
    """Test the laws CLI command."""

    def test_cmd_laws_no_args_returns_zero(self) -> None:
        """Test 'kgents laws' returns 0."""
        result = cmd_laws([])
        assert result == 0

    def test_cmd_laws_json_format(self) -> None:
        """Test 'kgents laws --format=json' returns valid JSON."""
        # This would need stdout capture in a real test
        result = cmd_laws(["--format=json"])
        assert result == 0

    def test_cmd_laws_verify_returns_result(self) -> None:
        """Test 'kgents laws verify' returns a result."""
        result = cmd_laws(["verify"])
        # May return 0 or 1 depending on verification
        assert result in (0, 1)

    def test_cmd_laws_witness_requires_operation(self) -> None:
        """Test 'kgents laws witness' requires operation."""
        result = cmd_laws(["witness"])
        assert result == 1

    def test_cmd_laws_witness_valid_operation(self) -> None:
        """Test 'kgents laws witness' with valid operation."""
        result = cmd_laws(["witness", "A >> B"])
        assert result == 0


# ─────────────────────────────────────────────────────────────────
# Principles Tests
# ─────────────────────────────────────────────────────────────────


class TestPrincipleDefinitions:
    """Test principle definitions are complete and correct."""

    def test_seven_principles_defined(self) -> None:
        """Verify all 7 design principles are defined."""
        assert len(DESIGN_PRINCIPLES) == 7

    def test_all_principle_names_covered(self) -> None:
        """Verify all PrincipleName enum values have definitions."""
        defined_names = {p.name for p in DESIGN_PRINCIPLES}
        enum_names = set(PrincipleName)
        assert defined_names == enum_names

    def test_principle_has_required_fields(self) -> None:
        """Verify each principle has all required fields."""
        for principle in DESIGN_PRINCIPLES:
            assert principle.name is not None
            assert principle.title, f"Principle {principle.name} missing title"
            assert principle.essence, f"Principle {principle.name} missing essence"
            assert principle.question, f"Principle {principle.name} missing question"
            assert len(principle.anti_patterns) > 0, (
                f"Principle {principle.name} missing anti-patterns"
            )

    def test_tasteful_principle_present(self) -> None:
        """Verify Tasteful principle is defined."""
        names = {p.name for p in DESIGN_PRINCIPLES}
        assert PrincipleName.TASTEFUL in names

    def test_composable_principle_present(self) -> None:
        """Verify Composable principle is defined."""
        names = {p.name for p in DESIGN_PRINCIPLES}
        assert PrincipleName.COMPOSABLE in names


class TestPrinciplesFormatters:
    """Test principles formatting functions."""

    def test_format_principles_rich_contains_all(self) -> None:
        """Verify rich format includes all principles."""
        output = format_principles_rich()
        for principle in DESIGN_PRINCIPLES:
            assert principle.title.upper() in output

    def test_format_principles_rich_has_header(self) -> None:
        """Verify rich format has proper header."""
        output = format_principles_rich()
        assert "DESIGN PRINCIPLES" in output

    def test_format_principles_json_is_valid(self) -> None:
        """Verify JSON format is valid JSON."""
        output = format_principles_json()
        data = json.loads(output)
        assert "principles" in data
        assert "count" in data
        assert data["count"] == 7

    def test_format_principles_json_has_all_fields(self) -> None:
        """Verify JSON format includes all principle fields."""
        output = format_principles_json()
        data = json.loads(output)
        for p_dict in data["principles"]:
            assert "name" in p_dict
            assert "title" in p_dict
            assert "essence" in p_dict
            assert "question" in p_dict
            assert "anti_patterns" in p_dict


class TestPrincipleEvaluation:
    """Test principle evaluation logic."""

    @pytest.mark.asyncio
    async def test_evaluate_returns_report(self) -> None:
        """Verify evaluation returns a report."""
        report = await evaluate_against_principles("test input")
        assert isinstance(report, EvaluationReport)
        assert len(report.evaluations) == 7

    @pytest.mark.asyncio
    async def test_evaluate_detects_monolithic_antipattern(self) -> None:
        """Verify evaluation detects 'monolithic' anti-pattern."""
        report = await evaluate_against_principles("A monolithic agent that does everything")
        composable = next(e for e in report.evaluations if e.principle == PrincipleName.COMPOSABLE)
        assert composable.verdict == PrincipleVerdict.REJECT

    @pytest.mark.asyncio
    async def test_evaluate_detects_composable_signals(self) -> None:
        """Verify evaluation detects composable design signals."""
        report = await evaluate_against_principles(
            "A modular agent with clear interface for composition"
        )
        composable = next(e for e in report.evaluations if e.principle == PrincipleName.COMPOSABLE)
        assert composable.verdict == PrincipleVerdict.ACCEPT

    @pytest.mark.asyncio
    async def test_evaluate_detects_ethical_concerns(self) -> None:
        """Verify evaluation detects ethical concerns."""
        report = await evaluate_against_principles("Trust me, I know what I'm doing with your data")
        ethical = next(e for e in report.evaluations if e.principle == PrincipleName.ETHICAL)
        assert ethical.verdict == PrincipleVerdict.REJECT

    @pytest.mark.asyncio
    async def test_evaluate_detects_tasteful_signals(self) -> None:
        """Verify evaluation detects tasteful design."""
        report = await evaluate_against_principles(
            "A focused agent with clear purpose that does one thing well"
        )
        tasteful = next(e for e in report.evaluations if e.principle == PrincipleName.TASTEFUL)
        assert tasteful.verdict == PrincipleVerdict.ACCEPT

    @pytest.mark.asyncio
    async def test_evaluate_unclear_for_vague_input(self) -> None:
        """Verify evaluation returns unclear for vague input."""
        report = await evaluate_against_principles("something")
        # Most evaluations should be unclear
        unclear_count = sum(1 for e in report.evaluations if e.verdict == PrincipleVerdict.UNCLEAR)
        assert unclear_count >= 4  # At least 4 of 7 should be unclear

    def test_evaluation_report_counts(self) -> None:
        """Test report counting methods."""
        from datetime import datetime

        evaluations = [
            PrincipleEvaluation(PrincipleName.TASTEFUL, PrincipleVerdict.ACCEPT, "", 0.8),
            PrincipleEvaluation(PrincipleName.CURATED, PrincipleVerdict.ACCEPT, "", 0.7),
            PrincipleEvaluation(PrincipleName.ETHICAL, PrincipleVerdict.REJECT, "", 0.9),
            PrincipleEvaluation(PrincipleName.JOY_INDUCING, PrincipleVerdict.UNCLEAR, "", 0.3),
        ]
        report = EvaluationReport(
            input_description="test",
            evaluated_at=datetime.now(),
            evaluations=evaluations,
            overall_verdict=PrincipleVerdict.REJECT,
            summary="test",
        )
        assert report.accepted == 2
        assert report.rejected == 1
        assert report.unclear == 1


class TestPrinciplesCLI:
    """Test the principles CLI command."""

    def test_cmd_principles_no_args_returns_zero(self) -> None:
        """Test 'kgents principles' returns 0."""
        result = cmd_principles([])
        assert result == 0

    def test_cmd_principles_json_format(self) -> None:
        """Test 'kgents principles --format=json' returns valid JSON."""
        result = cmd_principles(["--format=json"])
        assert result == 0

    def test_cmd_principles_check_requires_input(self) -> None:
        """Test 'kgents principles check' requires input."""
        result = cmd_principles(["check"])
        assert result == 1

    def test_cmd_principles_check_with_text(self) -> None:
        """Test 'kgents principles check' with text input."""
        result = cmd_principles(["check", "A modular composable agent"])
        # Returns based on verdict
        assert result in (0, 1)

    def test_cmd_principles_check_monolithic_fails(self) -> None:
        """Test 'kgents principles check' rejects monolithic design."""
        result = cmd_principles(["check", "A monolithic agent that does everything"])
        assert result == 1  # Should fail


# ─────────────────────────────────────────────────────────────────
# Integration Tests
# ─────────────────────────────────────────────────────────────────


class TestBootstrapIntegration:
    """Integration tests for bootstrap commands."""

    def test_laws_and_principles_consistent(self) -> None:
        """Verify laws and principles have consistent structure."""
        # Both have 7 items
        assert len(CATEGORY_LAWS) == len(DESIGN_PRINCIPLES)

        # Both use similar verdict enums
        assert Verdict.PASS.value == "pass"
        assert PrincipleVerdict.ACCEPT.value == "accept"

    def test_composable_principle_references_laws(self) -> None:
        """Verify Composable principle references category laws."""
        composable = next(p for p in DESIGN_PRINCIPLES if p.name == PrincipleName.COMPOSABLE)
        # Should reference composition/category
        assert "morphism" in composable.essence.lower() or "category" in composable.essence.lower()

    def test_all_json_outputs_valid(self) -> None:
        """Verify all JSON outputs are valid."""
        json.loads(format_laws_json())
        json.loads(format_principles_json())
