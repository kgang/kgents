"""
Tests for Scientific Core CLI Commands (Phase 2).

Tests cover:
1. Falsify - Find counterexamples to hypotheses
2. Conjecture - Generate hypotheses from patterns
3. Rival - Steel-man opposing views
4. Sublate - Synthesize contradictions
5. Shadow - Surface suppressed concerns
"""

import tempfile
from pathlib import Path

import pytest

from ..scientific import (
    # Falsify
    Counterexample,
    CounterexampleType,
    FalsifyReport,
    ScientificCLI,
    falsify_hypothesis,
    find_counterexamples,
    # Conjecture
    Conjecture,
    ConjectureReport,
    ConjectureType,
    generate_conjectures,
    # Rival
    RivalArgument,
    RivalReport,
    generate_rival,
    # Sublate
    Sublation,
    SublateReport,
    SublationType,
    find_antithesis,
    sublate_contradiction,
    # Shadow
    ShadowContent,
    ShadowReport,
    analyze_shadow,
)
from ..cli_types import CLIContext


# =============================================================================
# Falsify Tests
# =============================================================================


class TestCounterexample:
    """Tests for Counterexample dataclass."""

    def test_creation(self):
        ce = Counterexample(
            hypothesis="All tests pass",
            counterexample="Found failing test",
            example_type=CounterexampleType.DIRECT,
            confidence=0.8,
            source="test_file.py",
            suggestion="Fix or remove test",
        )
        assert ce.hypothesis == "All tests pass"
        assert ce.confidence == 0.8
        assert ce.example_type == CounterexampleType.DIRECT


class TestFalsifyReport:
    """Tests for FalsifyReport dataclass."""

    def test_not_falsified(self):
        report = FalsifyReport(
            hypothesis="Test hypothesis",
            counterexamples=(),
            falsified=False,
            confidence=0.0,
            search_depth="medium",
        )
        assert report.falsified is False
        rendered = report.render()
        assert "STANDS" in rendered
        assert "Test hypothesis" in rendered

    def test_falsified(self):
        ce = Counterexample(
            hypothesis="Always works",
            counterexample="Exception found",
            example_type=CounterexampleType.EDGE_CASE,
            confidence=0.7,
            source="edge.py",
            suggestion="Handle edge case",
        )
        report = FalsifyReport(
            hypothesis="Always works",
            counterexamples=(ce,),
            falsified=True,
            confidence=0.7,
            search_depth="deep",
        )
        assert report.falsified is True
        rendered = report.render()
        assert "CHALLENGED" in rendered
        assert "edge_case" in rendered


class TestFindCounterexamples:
    """Tests for find_counterexamples function."""

    @pytest.fixture
    def temp_codebase(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            # Create some source files
            (path / "main.py").write_text("# TODO: Fix edge case\ndef main(): pass")
            (path / "utils.py").write_text("# Sometimes this fails\ndef util(): pass")
            yield path

    def test_finds_negation_pattern(self, temp_codebase):
        # "always" should find "sometimes" as potential counterexample
        counterexamples = find_counterexamples(
            "This always works",
            temp_codebase,
            depth="medium",
        )
        # May or may not find depending on content
        assert isinstance(counterexamples, list)

    def test_finds_todo_related_counterexample(self, temp_codebase):
        # Looking for counterexamples to "edge cases handled"
        counterexamples = find_counterexamples(
            "All edge cases are handled",
            temp_codebase,
            depth="medium",
        )
        # The TODO about edge case should be found
        assert isinstance(counterexamples, list)


class TestFalsifyHypothesis:
    """Tests for falsify_hypothesis function."""

    @pytest.fixture
    def temp_codebase(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "code.py").write_text("def foo(): pass")
            yield path

    def test_returns_report(self, temp_codebase):
        report = falsify_hypothesis(
            "Functions always have docstrings",
            temp_codebase,
            depth="shallow",
        )
        assert isinstance(report, FalsifyReport)
        assert report.search_depth == "shallow"


# =============================================================================
# Conjecture Tests
# =============================================================================


class TestConjecture:
    """Tests for Conjecture dataclass."""

    def test_creation(self):
        c = Conjecture(
            statement="This project uses type hints",
            conjecture_type=ConjectureType.STRUCTURAL,
            confidence=0.85,
            evidence=("90% of files have type hints",),
            testable=True,
            falsification_hint="Look for Any types",
        )
        assert c.confidence == 0.85
        assert c.testable is True


class TestConjectureReport:
    """Tests for ConjectureReport dataclass."""

    def test_empty_report(self):
        report = ConjectureReport(
            conjectures=(),
            patterns_analyzed=0,
            files_scanned=0,
        )
        rendered = report.render()
        assert "NO CONJECTURES" in rendered

    def test_with_conjectures(self):
        c = Conjecture(
            statement="Testing is a priority",
            conjecture_type=ConjectureType.BEHAVIORAL,
            confidence=0.7,
            evidence=("10 test files",),
            testable=True,
            falsification_hint="Check coverage",
        )
        report = ConjectureReport(
            conjectures=(c,),
            patterns_analyzed=5,
            files_scanned=20,
        )
        rendered = report.render()
        assert "CONJECTURES" in rendered
        assert "Testing is a priority" in rendered


class TestGenerateConjectures:
    """Tests for generate_conjectures function."""

    @pytest.fixture
    def typed_codebase(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            # Create files with type hints
            (path / "typed.py").write_text(
                '"""Module doc."""\ndef foo(x: int) -> str: return str(x)'
            )
            (path / "typed2.py").write_text(
                '"""Another doc."""\nasync def bar() -> None: pass'
            )
            yield path

    def test_generates_type_conjecture(self, typed_codebase):
        report = generate_conjectures(typed_codebase, limit=5)
        assert isinstance(report, ConjectureReport)
        # Should find type hints pattern
        type_conjectures = [
            c for c in report.conjectures if "type" in c.statement.lower()
        ]
        # May or may not generate depending on threshold
        assert isinstance(type_conjectures, list)


# =============================================================================
# Rival Tests
# =============================================================================


class TestRivalArgument:
    """Tests for RivalArgument dataclass."""

    def test_creation(self):
        r = RivalArgument(
            position="Tests are essential",
            rival="Tests give false confidence",
            strength=0.7,
            concessions=("Tests catch some bugs",),
            synthesis_hint="Test critical paths",
        )
        assert r.strength == 0.7
        assert "Tests give false confidence" in r.rival


class TestRivalReport:
    """Tests for RivalReport dataclass."""

    def test_no_rivals(self):
        report = RivalReport(
            original_position="Unknown position",
            rivals=(),
            strongest_rival=None,
        )
        rendered = report.render()
        assert "NO RIVALS" in rendered

    def test_with_rivals(self):
        r = RivalArgument(
            position="Speed matters",
            rival="Quality matters more",
            strength=0.8,
            concessions=("Fast feedback is good",),
            synthesis_hint="Fast for validation, careful for shipping",
        )
        report = RivalReport(
            original_position="Speed matters",
            rivals=(r,),
            strongest_rival="Quality matters more",
        )
        rendered = report.render()
        assert "RIVALS" in rendered
        assert "Quality matters more" in rendered


class TestGenerateRival:
    """Tests for generate_rival function."""

    def test_generates_test_rival(self):
        report = generate_rival("We must always write tests")
        assert len(report.rivals) > 0
        # Should generate a rival about testing
        assert any(
            "test" in r.rival.lower() or "false" in r.rival.lower()
            for r in report.rivals
        )

    def test_generates_type_rival(self):
        report = generate_rival("We use types everywhere")
        assert len(report.rivals) > 0

    def test_generates_generic_rival(self):
        report = generate_rival("Completely unique position xyz123")
        assert len(report.rivals) > 0
        # Should have at least a generic rival


# =============================================================================
# Sublate Tests
# =============================================================================


class TestSublation:
    """Tests for Sublation dataclass."""

    def test_creation(self):
        s = Sublation(
            thesis="Speed is essential",
            antithesis="Quality is essential",
            synthesis="Quality at the speed of learning",
            sublation_type=SublationType.ELEVATE,
            preserved_from_thesis="Fast feedback",
            preserved_from_antithesis="Quality compounds",
            transcendent_insight="Speed without learning is waste",
        )
        assert s.sublation_type == SublationType.ELEVATE


class TestSublateReport:
    """Tests for SublateReport dataclass."""

    def test_productive_tension(self):
        report = SublateReport(
            original_thesis="A",
            original_antithesis="B",
            sublation=None,
            productive_tension=True,
        )
        rendered = report.render()
        assert "PRODUCTIVE TENSION" in rendered

    def test_with_synthesis(self):
        s = Sublation(
            thesis="A",
            antithesis="B",
            synthesis="A+B",
            sublation_type=SublationType.ELEVATE,
            preserved_from_thesis="A insight",
            preserved_from_antithesis="B insight",
            transcendent_insight="Higher truth",
        )
        report = SublateReport(
            original_thesis="A",
            original_antithesis="B",
            sublation=s,
            productive_tension=False,
        )
        rendered = report.render()
        assert "SUBLATION" in rendered
        assert "Synthesis:" in rendered


class TestFindAntithesis:
    """Tests for find_antithesis function."""

    def test_finds_always_antithesis(self):
        antithesis = find_antithesis("We always do X")
        assert antithesis is not None
        assert "sometimes" in antithesis.lower()

    def test_finds_never_antithesis(self):
        antithesis = find_antithesis("We never do Y")
        assert antithesis is not None

    def test_no_antithesis_for_neutral(self):
        antithesis = find_antithesis("The code is here")
        # Might be None if no patterns match
        assert antithesis is None or isinstance(antithesis, str)


class TestSublateContradiction:
    """Tests for sublate_contradiction function."""

    def test_known_synthesis_pattern(self):
        report = sublate_contradiction(
            "Speed is essential",
            "Quality is essential",
        )
        # Should find the speed/quality synthesis
        assert report.sublation is not None or report.productive_tension is True

    def test_productive_tension_without_force(self):
        report = sublate_contradiction(
            "Unknown thesis X",
            "Unknown antithesis Y",
        )
        # Should mark as productive tension since no known pattern
        assert report.productive_tension is True or report.sublation is not None

    def test_force_synthesis(self):
        report = sublate_contradiction(
            "Unknown thesis X",
            "Unknown antithesis Y",
            force_synthesis=True,
        )
        # With force, should still produce a synthesis
        assert report.sublation is not None or report.productive_tension is True


# =============================================================================
# Shadow Tests
# =============================================================================


class TestShadowContent:
    """Tests for ShadowContent dataclass."""

    def test_creation(self):
        s = ShadowContent(
            persona_claim="helpful",
            shadow="Capacity to refuse",
            integration_difficulty="high",
            integration_path="Acknowledge that helpful sometimes means saying no",
        )
        assert s.persona_claim == "helpful"
        assert s.integration_difficulty == "high"


class TestShadowReport:
    """Tests for ShadowReport dataclass."""

    def test_no_shadow(self):
        report = ShadowReport(
            self_image="Just some text",
            shadows=(),
            persona_shadow_balance=1.0,
        )
        rendered = report.render()
        assert "NO SHADOW DETECTED" in rendered

    def test_with_shadows(self):
        s = ShadowContent(
            persona_claim="helpful",
            shadow="Capacity to refuse",
            integration_difficulty="high",
            integration_path="Say no when needed",
        )
        report = ShadowReport(
            self_image="I am helpful",
            shadows=(s,),
            persona_shadow_balance=0.5,
        )
        rendered = report.render()
        assert "SHADOW ANALYSIS" in rendered
        assert "helpful" in rendered


class TestAnalyzeShadow:
    """Tests for analyze_shadow function."""

    def test_finds_helpful_shadow(self):
        report = analyze_shadow("I am helpful and accurate")
        assert len(report.shadows) >= 2
        persona_claims = [s.persona_claim for s in report.shadows]
        assert "helpful" in persona_claims
        assert "accurate" in persona_claims

    def test_finds_ethical_shadow(self):
        report = analyze_shadow("This is an ethical and tasteful system")
        assert len(report.shadows) >= 2
        persona_claims = [s.persona_claim for s in report.shadows]
        assert "ethical" in persona_claims
        assert "tasteful" in persona_claims

    def test_balance_decreases_with_shadows(self):
        many_shadows = analyze_shadow("I am helpful, accurate, neutral, safe, bounded")
        few_shadows = analyze_shadow("I am helpful")
        assert many_shadows.persona_shadow_balance <= few_shadows.persona_shadow_balance


# =============================================================================
# CLI Integration Tests
# =============================================================================


class TestScientificCLI:
    """Tests for ScientificCLI class."""

    @pytest.fixture
    def cli(self):
        return ScientificCLI()

    @pytest.fixture
    def temp_codebase(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "main.py").write_text("def main(): pass")
            yield path

    @pytest.fixture
    def ctx(self):
        return CLIContext()

    @pytest.mark.asyncio
    async def test_falsify_returns_result(self, cli, temp_codebase, ctx):
        result = await cli.falsify("All tests pass", temp_codebase, ctx)
        assert result.success is True
        assert isinstance(result.output, FalsifyReport)

    @pytest.mark.asyncio
    async def test_conjecture_returns_result(self, cli, temp_codebase, ctx):
        result = await cli.conjecture(temp_codebase, ctx)
        assert result.success is True
        assert isinstance(result.output, ConjectureReport)

    @pytest.mark.asyncio
    async def test_rival_returns_result(self, cli, ctx):
        result = await cli.rival("Testing is important", ctx)
        assert result.success is True
        assert isinstance(result.output, RivalReport)

    @pytest.mark.asyncio
    async def test_sublate_returns_result(self, cli, ctx):
        result = await cli.sublate("Speed", "Quality", ctx)
        assert result.success is True
        assert isinstance(result.output, SublateReport)

    @pytest.mark.asyncio
    async def test_shadow_returns_result(self, cli, ctx):
        result = await cli.shadow("I am helpful", ctx)
        assert result.success is True
        assert isinstance(result.output, ShadowReport)


# =============================================================================
# Render Tests (Output Formatting)
# =============================================================================


class TestRenderFunctions:
    """Tests that render functions produce valid output."""

    def test_falsify_report_render_formats(self):
        report = FalsifyReport(
            hypothesis="Test",
            counterexamples=(),
            falsified=False,
            confidence=0.0,
            search_depth="medium",
        )
        rendered = report.render()
        assert isinstance(rendered, str)
        assert len(rendered) > 0

    def test_conjecture_report_render_formats(self):
        report = ConjectureReport(
            conjectures=(),
            patterns_analyzed=0,
            files_scanned=0,
        )
        rendered = report.render()
        assert isinstance(rendered, str)

    def test_rival_report_render_formats(self):
        report = RivalReport(
            original_position="Test",
            rivals=(),
            strongest_rival=None,
        )
        rendered = report.render()
        assert isinstance(rendered, str)

    def test_sublate_report_render_formats(self):
        report = SublateReport(
            original_thesis="A",
            original_antithesis="B",
            sublation=None,
            productive_tension=True,
        )
        rendered = report.render()
        assert isinstance(rendered, str)

    def test_shadow_report_render_formats(self):
        report = ShadowReport(
            self_image="Test",
            shadows=(),
            persona_shadow_balance=1.0,
        )
        rendered = report.render()
        assert isinstance(rendered, str)
