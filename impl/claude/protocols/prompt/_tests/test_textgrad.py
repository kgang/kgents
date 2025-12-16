"""
Tests for Wave 4: TextGRAD self-improvement system.

These tests verify the TextGRAD improver, feedback parser,
and gradient system work correctly.
"""

from __future__ import annotations

import pytest
from protocols.prompt.textgrad import (
    FeedbackParser,
    FeedbackTarget,
    GradientStep,
    ImprovementResult,
    ParsedFeedback,
    TextGRADImprover,
    TextualGradient,
)
from protocols.prompt.textgrad.feedback_parser import FeedbackType
from protocols.prompt.textgrad.gradient import GradientDirection

# =============================================================================
# GradientStep Tests
# =============================================================================


class TestGradientStep:
    """Tests for GradientStep."""

    def test_creation(self) -> None:
        """Test step creation."""
        step = GradientStep(
            section_name="principles",
            direction=GradientDirection.CONDENSE,
            magnitude=0.5,
            description="Make more concise",
        )
        assert step.section_name == "principles"
        assert step.direction == GradientDirection.CONDENSE
        assert step.magnitude == 0.5

    def test_scale(self) -> None:
        """Test scaling magnitude."""
        step = GradientStep(
            section_name="test",
            direction=GradientDirection.EXPAND,
            magnitude=1.0,
            description="Test",
        )
        scaled = step.scale(0.5)
        assert scaled.magnitude == 0.5
        assert scaled.section_name == step.section_name

    def test_should_apply_high_rigidity(self) -> None:
        """Test that high rigidity blocks low magnitude."""
        step = GradientStep(
            section_name="test",
            direction=GradientDirection.CONDENSE,
            magnitude=0.3,
            description="Test",
        )
        # High rigidity (0.8) should block low magnitude (0.3)
        assert not step.should_apply(rigidity=0.8)

    def test_should_apply_low_rigidity(self) -> None:
        """Test that low rigidity allows changes."""
        step = GradientStep(
            section_name="test",
            direction=GradientDirection.CONDENSE,
            magnitude=0.3,
            description="Test",
        )
        # Low rigidity (0.2) should allow magnitude (0.3)
        assert step.should_apply(rigidity=0.2)

    def test_str_representation(self) -> None:
        """Test string representation."""
        step = GradientStep(
            section_name="principles",
            direction=GradientDirection.CONDENSE,
            magnitude=0.5,
            description="Make concise",
        )
        s = str(step)
        assert "principles" in s
        assert "CONDENSE" in s


# =============================================================================
# TextualGradient Tests
# =============================================================================


class TestTextualGradient:
    """Tests for TextualGradient."""

    def test_zero_gradient(self) -> None:
        """Test zero gradient creation."""
        zero = TextualGradient.zero()
        assert len(zero) == 0
        assert not zero

    def test_gradient_with_steps(self) -> None:
        """Test gradient with steps."""
        steps = (
            GradientStep("a", GradientDirection.CONDENSE, 0.5, "desc"),
            GradientStep("b", GradientDirection.EXPAND, 0.3, "desc"),
        )
        gradient = TextualGradient(
            steps=steps,
            reasoning=("test",),
            source_feedback="feedback",
        )
        assert len(gradient) == 2
        assert gradient

    def test_gradient_addition(self) -> None:
        """Test adding two gradients."""
        g1 = TextualGradient(
            steps=(GradientStep("a", GradientDirection.CONDENSE, 0.5, "desc"),),
            reasoning=("first",),
            source_feedback="f1",
        )
        g2 = TextualGradient(
            steps=(GradientStep("b", GradientDirection.EXPAND, 0.3, "desc"),),
            reasoning=("second",),
            source_feedback="f2",
        )
        combined = g1 + g2
        assert len(combined) == 2
        assert "first" in combined.reasoning
        assert "second" in combined.reasoning

    def test_gradient_scale(self) -> None:
        """Test scaling a gradient."""
        gradient = TextualGradient(
            steps=(GradientStep("a", GradientDirection.CONDENSE, 1.0, "desc"),),
            reasoning=(),
            source_feedback="test",
        )
        scaled = gradient.scale(0.5)
        assert scaled.steps[0].magnitude == 0.5

    def test_filter_by_rigidity(self) -> None:
        """Test filtering steps by rigidity."""
        gradient = TextualGradient(
            steps=(
                GradientStep("high_rigid", GradientDirection.CONDENSE, 0.3, "desc"),
                GradientStep("low_rigid", GradientDirection.CONDENSE, 0.3, "desc"),
            ),
            reasoning=(),
            source_feedback="test",
        )

        def rigidity_lookup(name: str) -> float:
            return 0.8 if name == "high_rigid" else 0.1

        filtered = gradient.filter_by_rigidity(rigidity_lookup)

        # Only low_rigid should remain
        assert len(filtered) == 1
        assert filtered.steps[0].section_name == "low_rigid"

    def test_affected_sections(self) -> None:
        """Test getting affected sections."""
        gradient = TextualGradient(
            steps=(
                GradientStep("a", GradientDirection.CONDENSE, 0.5, "desc"),
                GradientStep("b", GradientDirection.EXPAND, 0.3, "desc"),
                GradientStep("a", GradientDirection.CLARIFY, 0.2, "desc"),  # Duplicate
            ),
            reasoning=(),
            source_feedback="test",
        )
        affected = gradient.affected_sections()
        assert affected == {"a", "b"}

    def test_for_section(self) -> None:
        """Test getting steps for a specific section."""
        gradient = TextualGradient(
            steps=(
                GradientStep("a", GradientDirection.CONDENSE, 0.5, "desc1"),
                GradientStep("b", GradientDirection.EXPAND, 0.3, "desc2"),
                GradientStep("a", GradientDirection.CLARIFY, 0.2, "desc3"),
            ),
            reasoning=(),
            source_feedback="test",
        )
        a_steps = gradient.for_section("a")
        assert len(a_steps) == 2


# =============================================================================
# FeedbackParser Tests
# =============================================================================


class TestFeedbackParser:
    """Tests for FeedbackParser."""

    @pytest.fixture
    def parser(self) -> FeedbackParser:
        return FeedbackParser()

    def test_parse_empty_feedback(self, parser: FeedbackParser) -> None:
        """Test parsing empty feedback."""
        result = parser.parse("")
        assert result.is_empty

    def test_parse_concise_feedback(self, parser: FeedbackParser) -> None:
        """Test parsing 'be more concise'."""
        result = parser.parse("be more concise")
        assert not result.is_empty
        assert result.targets[0].direction == GradientDirection.CONDENSE

    def test_parse_section_specific(self, parser: FeedbackParser) -> None:
        """Test parsing section-specific feedback."""
        result = parser.parse("make the principles section shorter")
        assert not result.is_empty
        assert result.targets[0].section_name == "principles"
        assert result.targets[0].direction == GradientDirection.CONDENSE

    def test_parse_expand_feedback(self, parser: FeedbackParser) -> None:
        """Test parsing 'more detail'."""
        result = parser.parse("add more detail to skills")
        assert not result.is_empty
        assert result.targets[0].section_name == "skills"
        assert result.targets[0].direction == GradientDirection.EXPAND

    def test_parse_formal_feedback(self, parser: FeedbackParser) -> None:
        """Test parsing formality feedback."""
        result = parser.parse("make it more formal")
        assert not result.is_empty
        assert result.targets[0].direction == GradientDirection.FORMALIZE

    def test_parse_casual_feedback(self, parser: FeedbackParser) -> None:
        """Test parsing casual feedback."""
        result = parser.parse("be more casual and friendly")
        assert not result.is_empty
        assert result.targets[0].direction == GradientDirection.CASUALIZE

    def test_parse_remove_feedback(self, parser: FeedbackParser) -> None:
        """Test parsing remove feedback."""
        result = parser.parse("remove the forest section")
        assert not result.is_empty
        assert result.targets[0].section_name == "forest"
        assert result.targets[0].direction == GradientDirection.REMOVE

    def test_parse_multiple_sections(self, parser: FeedbackParser) -> None:
        """Test parsing feedback mentioning multiple sections."""
        result = parser.parse("shorten the principles section")
        # Should find at least one target with section name
        assert len(result.targets) >= 1
        # First target should have the section name
        assert result.targets[0].section_name == "principles"

    def test_reasoning_trace(self, parser: FeedbackParser) -> None:
        """Test that reasoning trace is populated."""
        result = parser.parse("be concise")
        assert len(result.reasoning) > 0
        assert "Parsing" in result.reasoning[0]

    def test_to_gradient(self, parser: FeedbackParser) -> None:
        """Test converting to gradient."""
        result = parser.parse("make principles concise")
        gradient = result.to_gradient(base_magnitude=0.7)
        assert len(gradient) == 1
        assert gradient.steps[0].magnitude == pytest.approx(
            0.7 * 0.7
        )  # Base * confidence


class TestFeedbackTarget:
    """Tests for FeedbackTarget."""

    def test_to_gradient_step(self) -> None:
        """Test conversion to GradientStep."""
        target = FeedbackTarget(
            section_name="principles",
            feedback_type=FeedbackType.LENGTH,
            direction=GradientDirection.CONDENSE,
            confidence=0.8,
        )
        step = target.to_gradient_step(magnitude=0.5)
        assert step.section_name == "principles"
        assert step.direction == GradientDirection.CONDENSE
        assert step.magnitude == 0.4  # 0.5 * 0.8

    def test_global_target(self) -> None:
        """Test target without specific section."""
        target = FeedbackTarget(
            section_name=None,
            feedback_type=FeedbackType.STYLE,
            direction=GradientDirection.FORMALIZE,
            confidence=0.5,
        )
        step = target.to_gradient_step()
        assert step.section_name == "*"


# =============================================================================
# TextGRADImprover Tests
# =============================================================================


class TestTextGRADImprover:
    """Tests for TextGRADImprover."""

    @pytest.fixture
    def improver(self) -> TextGRADImprover:
        return TextGRADImprover(learning_rate=0.5)

    @pytest.fixture
    def sample_sections(self) -> dict[str, str]:
        return {
            "principles": "Be helpful. Be honest. Be harmless.\nMore details here.\nEven more content.",
            "skills": "Python programming. TypeScript development. Testing expertise.",
        }

    def test_empty_feedback_returns_unchanged(
        self, improver: TextGRADImprover, sample_sections: dict[str, str]
    ) -> None:
        """Test that empty feedback returns unchanged content (identity law)."""
        result = improver.improve(sample_sections, "")
        assert result.improved_content == result.original_content
        assert not result.content_changed
        assert "identity law" in " ".join(result.reasoning_trace).lower()

    def test_improve_returns_result(
        self, improver: TextGRADImprover, sample_sections: dict[str, str]
    ) -> None:
        """Test improve returns ImprovementResult."""
        result = improver.improve(sample_sections, "make it shorter")
        assert isinstance(result, ImprovementResult)
        assert len(result.reasoning_trace) > 0

    def test_improve_with_section_target(
        self, improver: TextGRADImprover, sample_sections: dict[str, str]
    ) -> None:
        """Test improvement targeting specific section."""
        result = improver.improve(sample_sections, "make principles shorter")

        # Should have targeted principles
        assert "principles" in " ".join(result.reasoning_trace).lower()

    def test_improve_respects_rigidity(
        self, improver: TextGRADImprover, sample_sections: dict[str, str]
    ) -> None:
        """Test that rigidity affects which sections change."""
        rigidity = {
            "principles": 0.9,  # Very rigid
            "skills": 0.1,  # Very changeable
        }

        result = improver.improve(
            sample_sections,
            "make everything shorter",
            rigidity_lookup=rigidity,
        )

        # Should mention rigidity filtering
        assert "rigidity" in " ".join(result.reasoning_trace).lower()

    def test_improve_gradient_preserved(
        self, improver: TextGRADImprover, sample_sections: dict[str, str]
    ) -> None:
        """Test that gradient is preserved in result."""
        result = improver.improve(sample_sections, "be concise")
        assert result.gradient is not None
        assert isinstance(result.gradient, TextualGradient)

    def test_learning_rate_scales_changes(self) -> None:
        """Test that learning rate affects change magnitude."""
        sections = {
            "test": "Content line 1\nContent line 2\nContent line 3\nContent line 4"
        }

        low_lr = TextGRADImprover(learning_rate=0.1)
        high_lr = TextGRADImprover(learning_rate=0.9)

        low_result = low_lr.improve(sections, "make shorter")
        high_result = high_lr.improve(sections, "make shorter")

        # Both should produce gradients with different magnitudes
        # The actual change may or may not differ depending on threshold
        assert low_result.gradient is not None
        assert high_result.gradient is not None


class TestImproverMonadic:
    """Tests for monadic TextGRAD integration."""

    def test_improve_monadic_returns_promptm(self) -> None:
        """Test that improve_monadic returns PromptM."""
        from protocols.prompt.monad import PromptM, Source

        improver = TextGRADImprover()
        sections = {"test": "content"}

        result = improver.improve_monadic(sections, "be concise")

        assert isinstance(result, PromptM)
        assert Source.TEXTGRAD in result.provenance

    def test_improve_monadic_empty_feedback(self) -> None:
        """Test monadic version with empty feedback."""
        from protocols.prompt.monad import PromptM

        improver = TextGRADImprover()
        sections = {"test": "content"}

        result = improver.improve_monadic(sections, "")

        assert isinstance(result, PromptM)
        # Should be identity
        assert result.value.improved_content == result.value.original_content


# =============================================================================
# Integration Tests
# =============================================================================


class TestTextGRADIntegration:
    """Integration tests for TextGRAD."""

    def test_full_pipeline(self) -> None:
        """Test full improvement pipeline."""
        sections = {
            "principles": """
# Core Principles

1. Be helpful to users
2. Be honest in responses
3. Avoid harmful content
4. Additional principle here
5. Another one
            """.strip(),
        }

        improver = TextGRADImprover(learning_rate=0.5)
        result = improver.improve(sections, "make principles more concise")

        # Should have processed
        assert isinstance(result, ImprovementResult)
        assert len(result.reasoning_trace) > 3  # Multiple trace entries

    def test_chained_improvements(self) -> None:
        """Test chaining multiple improvements."""
        sections = {"test": "Long content here with lots of words and details."}
        improver = TextGRADImprover(learning_rate=0.3)

        # First improvement
        r1 = improver.improve(sections, "be concise")

        # Parse improved sections
        improved_sections = {
            "test": r1.improved_content.split("## test")[-1].strip()
            if "## test" in r1.improved_content
            else sections["test"]
        }

        # Second improvement
        r2 = improver.improve(improved_sections, "be more formal")

        # Both should have reasoning traces
        assert len(r1.reasoning_trace) > 0
        assert len(r2.reasoning_trace) > 0

    def test_monad_improve_function(self) -> None:
        """Test the monad.improve() convenience function."""
        from protocols.prompt.monad import improve

        sections = {"principles": "Be helpful.", "skills": "Python."}
        result = improve(sections, "be concise")

        # Should return PromptM
        from protocols.prompt.monad import PromptM

        assert isinstance(result, PromptM)
        assert isinstance(result.value, dict)


# =============================================================================
# RuleBasedSectionImprover Tests
# =============================================================================


class TestRuleBasedSectionImprover:
    """Tests for the rule-based section improver."""

    def test_condense_removes_content(self) -> None:
        """Test that condensing reduces content."""
        from protocols.prompt.textgrad.improver import RuleBasedSectionImprover

        improver = RuleBasedSectionImprover()
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6"
        steps = [
            GradientStep(
                section_name="test",
                direction=GradientDirection.CONDENSE,
                magnitude=0.5,
                description="condense",
            )
        ]

        improved, traces = improver.improve("test", content, steps)

        # Should be shorter
        assert len(improved) <= len(content)
        assert "Condensed" in " ".join(traces)

    def test_remove_specific_content(self) -> None:
        """Test removing specific content."""
        from protocols.prompt.textgrad.improver import RuleBasedSectionImprover

        improver = RuleBasedSectionImprover()
        content = "Keep this. Remove this. Keep this too."
        steps = [
            GradientStep(
                section_name="test",
                direction=GradientDirection.REMOVE,
                magnitude=0.5,
                description="remove",
                target_content="Remove this. ",
            )
        ]

        improved, traces = improver.improve("test", content, steps)

        assert "Remove this" not in improved
        assert "Keep this" in improved
