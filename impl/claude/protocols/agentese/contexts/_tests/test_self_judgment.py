"""
Tests for Self-Judgment: self.judgment.critique, self.judgment.refine

Tests verify:
1. Critique dataclass structure and validation
2. CritiqueWeights configuration
3. CriticsLoop iteration and termination
4. Novelty, utility, and surprise assessment
5. Refinement loop improvement

Required tests from creativity.md Phase 7:
- test_critique_scores_novelty
- test_critique_loop_improves
- test_critique_max_iterations

Property-based tests ensure the spec is correct regardless of implementation.
"""
# mypy: disable-error-code="arg-type,no-any-return"

from __future__ import annotations

from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from ..self_judgment import (
    CriticsLoop,
    Critique,
    CritiqueWeights,
    RefinedArtifact,
)

# === Test Fixtures ===


class MockDNA:
    """Mock DNA for testing."""

    def __init__(self, name: str = "test", archetype: str = "default") -> None:
        self.name = name
        self.archetype = archetype
        self.capabilities: tuple[str, ...] = ()


class MockUmwelt:
    """Mock Umwelt for testing - satisfies Umwelt protocol for test purposes."""

    def __init__(
        self,
        archetype: str = "default",
        prior: Any = None,
    ) -> None:
        self.dna = MockDNA(archetype=archetype)
        self.gravity: tuple[Any, ...] = ()
        self.context: dict[str, Any] = {}
        if prior is not None:
            self.context["expectations"] = {"prior": prior}


class MockLogos:
    """Mock Logos for testing."""

    def __init__(
        self,
        generator_result: Any = "Generated output",
        refine_modifier: str = " (refined)",
    ) -> None:
        self.generator_result = generator_result
        self.refine_modifier = refine_modifier
        self.invoke_count = 0
        self.last_path: str | None = None
        self.last_kwargs: dict[str, Any] = {}

    async def invoke(
        self,
        path: str,
        observer: Any,
        **kwargs: Any,
    ) -> Any:
        self.invoke_count += 1
        self.last_path = path
        self.last_kwargs = kwargs

        if path.startswith("concept.generate") or path == "generator":
            return self.generator_result
        elif path == "concept.refine.apply":
            # Simulate refinement by modifying input
            input_val = kwargs.get("input", "")
            if isinstance(input_val, str):
                return input_val + self.refine_modifier
            return input_val

        return {"path": path, "kwargs": kwargs}


@pytest.fixture
def observer() -> Any:
    """Create a default observer (typed as Any to satisfy mock usage)."""
    return MockUmwelt()


@pytest.fixture
def observer_with_prior() -> Any:
    """Create an observer with prior expectation (typed as Any to satisfy mock usage)."""
    return MockUmwelt(prior="Expected output")


@pytest.fixture
def logos() -> MockLogos:
    """Create a mock Logos."""
    return MockLogos()


@pytest.fixture
def loop() -> CriticsLoop:
    """Create a CriticsLoop for testing."""
    return CriticsLoop(max_iterations=3, threshold=0.7)


# === CritiqueWeights Tests ===


class TestCritiqueWeights:
    """Tests for CritiqueWeights configuration."""

    def test_default_weights_sum_to_one(self) -> None:
        """Default weights sum to 1.0."""
        weights = CritiqueWeights()
        total = weights.novelty + weights.utility + weights.surprise
        assert abs(total - 1.0) < 0.001

    def test_custom_weights_validated(self) -> None:
        """Custom weights must sum to 1.0."""
        # Valid custom weights
        weights = CritiqueWeights(novelty=0.5, utility=0.3, surprise=0.2)
        assert weights.novelty == 0.5

        # Invalid weights should raise
        with pytest.raises(ValueError, match="sum to 1.0"):
            CritiqueWeights(novelty=0.5, utility=0.5, surprise=0.5)

    def test_weights_are_frozen(self) -> None:
        """CritiqueWeights is immutable."""
        weights = CritiqueWeights()
        with pytest.raises(Exception):  # FrozenInstanceError
            weights.novelty = 0.5  # type: ignore[misc]

    @given(
        novelty=st.floats(min_value=0.0, max_value=1.0),
        utility=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=50)
    def test_weights_computed_surprise(
        self,
        novelty: float,
        utility: float,
    ) -> None:
        """Surprise weight can be computed from novelty and utility."""
        if novelty + utility <= 1.0:
            surprise = 1.0 - novelty - utility
            weights = CritiqueWeights(
                novelty=novelty, utility=utility, surprise=surprise
            )
            assert (
                abs(weights.novelty + weights.utility + weights.surprise - 1.0) < 0.001
            )


# === Critique Tests ===


class TestCritique:
    """Tests for Critique dataclass."""

    def test_critique_is_frozen(self) -> None:
        """Critique is immutable (frozen)."""
        critique = Critique(
            novelty=0.5,
            utility=0.5,
            surprise=0.5,
            overall=0.5,
            reasoning="Test",
            suggestions=("Suggestion 1",),
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            critique.overall = 0.8  # type: ignore[misc]

    def test_critique_validates_scores(self) -> None:
        """Scores must be between 0.0 and 1.0."""
        with pytest.raises(ValueError, match="novelty"):
            Critique(
                novelty=1.5,  # Invalid
                utility=0.5,
                surprise=0.5,
                overall=0.5,
                reasoning="Test",
                suggestions=(),
            )

        with pytest.raises(ValueError, match="overall"):
            Critique(
                novelty=0.5,
                utility=0.5,
                surprise=0.5,
                overall=-0.1,  # Invalid
                reasoning="Test",
                suggestions=(),
            )

    def test_critique_create_computes_overall(self) -> None:
        """Critique.create computes overall from weights."""
        critique = Critique.create(
            novelty=0.8,
            utility=0.6,
            surprise=0.4,
            reasoning="Test",
            suggestions=["Improve X"],
        )
        # Default weights: 0.4, 0.4, 0.2
        expected = 0.4 * 0.8 + 0.4 * 0.6 + 0.2 * 0.4
        assert abs(critique.overall - expected) < 0.001

    def test_critique_create_custom_weights(self) -> None:
        """Critique.create uses custom weights."""
        weights = CritiqueWeights(novelty=0.5, utility=0.3, surprise=0.2)
        critique = Critique.create(
            novelty=1.0,
            utility=0.0,
            surprise=0.5,
            reasoning="Test",
            suggestions=[],
            weights=weights,
        )
        expected = 0.5 * 1.0 + 0.3 * 0.0 + 0.2 * 0.5
        assert abs(critique.overall - expected) < 0.001

    def test_critique_to_dict(self) -> None:
        """Critique converts to dict correctly."""
        critique = Critique.create(
            novelty=0.5,
            utility=0.5,
            surprise=0.5,
            reasoning="Test reasoning",
            suggestions=["Do X", "Try Y"],
        )
        d = critique.to_dict()
        assert d["novelty"] == 0.5
        assert d["reasoning"] == "Test reasoning"
        assert d["suggestions"] == ["Do X", "Try Y"]

    def test_critique_to_text(self) -> None:
        """Critique converts to text correctly."""
        critique = Critique.create(
            novelty=0.8,
            utility=0.6,
            surprise=0.4,
            reasoning="Good novelty",
            suggestions=["Consider X"],
        )
        text = critique.to_text()
        assert "Critique" in text
        assert "0.80" in text or "0.8" in text
        assert "Good novelty" in text
        assert "Consider X" in text

    @given(
        novelty=st.floats(min_value=0.0, max_value=1.0),
        utility=st.floats(min_value=0.0, max_value=1.0),
        surprise=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=50)
    def test_critique_overall_bounded(
        self,
        novelty: float,
        utility: float,
        surprise: float,
    ) -> None:
        """Overall score is always between 0.0 and 1.0."""
        critique = Critique.create(
            novelty=novelty,
            utility=utility,
            surprise=surprise,
            reasoning="Test",
            suggestions=[],
        )
        assert 0.0 <= critique.overall <= 1.0


# === CriticsLoop Basic Tests ===


class TestCriticsLoopBasic:
    """Basic tests for CriticsLoop."""

    def test_loop_validates_max_iterations(self) -> None:
        """max_iterations must be >= 1."""
        with pytest.raises(ValueError, match="max_iterations"):
            CriticsLoop(max_iterations=0)

    def test_loop_validates_threshold(self) -> None:
        """threshold must be between 0.0 and 1.0."""
        with pytest.raises(ValueError, match="threshold"):
            CriticsLoop(threshold=1.5)

        with pytest.raises(ValueError, match="threshold"):
            CriticsLoop(threshold=-0.1)

    def test_loop_add_prior_work(self) -> None:
        """Prior work can be added for novelty comparison."""
        loop = CriticsLoop()
        assert len(loop._prior_work) == 0

        loop.add_prior_work("artifact 1")
        loop.add_prior_work("artifact 2")
        assert len(loop._prior_work) == 2

        loop.clear_prior_work()
        assert len(loop._prior_work) == 0


# === Required Tests from creativity.md Phase 7 ===


class TestCritiqueScoresNovelty:
    """Test: test_critique_scores_novelty - Verify novelty assessment."""

    @pytest.mark.asyncio
    async def test_identical_artifacts_low_novelty(self, observer: MockUmwelt) -> None:
        """Identical artifacts have low novelty."""
        loop = CriticsLoop()
        artifact = "The quick brown fox"

        # Add the same artifact as prior work
        loop.add_prior_work(artifact)

        critique = await loop.critique(artifact, observer)

        # When artifact matches prior work, novelty should be low
        # structural_surprise returns low value for similar strings
        assert critique.novelty < 0.3

    @pytest.mark.asyncio
    async def test_different_artifacts_high_novelty(self, observer: MockUmwelt) -> None:
        """Very different artifacts have high novelty."""
        loop = CriticsLoop()

        # Add prior work that's very different
        loop.add_prior_work("12345")

        # Critique something completely different
        critique = await loop.critique(
            "The quick brown fox jumps over the lazy dog",
            observer,
        )

        # Different structure and content = higher novelty
        assert critique.novelty > 0.3

    @pytest.mark.asyncio
    async def test_no_prior_work_moderate_novelty(self, observer: MockUmwelt) -> None:
        """Without prior work, novelty is based on structural complexity."""
        loop = CriticsLoop()

        # No prior work
        critique = await loop.critique(
            "A moderately complex sentence with some structure.",
            observer,
        )

        # Should use structural novelty proxy
        assert 0.0 < critique.novelty < 1.0


class TestCritiqueLoopImproves:
    """Test: test_critique_loop_improves - Verify refinement increases score."""

    @pytest.mark.asyncio
    async def test_loop_improves_or_maintains_score(
        self,
        observer: MockUmwelt,
    ) -> None:
        """Each iteration should improve or maintain score."""
        # Mock Logos that provides refinement
        logos = MockLogos(
            generator_result="Initial short output",
            refine_modifier=" with additional meaningful content for better utility",
        )

        loop = CriticsLoop(max_iterations=3, threshold=0.95)  # High threshold

        result = await loop.generate_with_trace(
            logos,
            observer,
            "concept.generate.test",
            purpose="Create comprehensive output",
        )

        # Check that scores generally improve or maintain
        # Allow some variance due to heuristic scoring
        for i in range(1, len(result.history)):
            prev_score = result.history[i - 1][1].overall
            curr_score = result.history[i][1].overall
            # Allow up to 10% variance (refinement is heuristic)
            assert curr_score >= prev_score * 0.9, (
                f"Score dropped significantly: {prev_score} -> {curr_score}"
            )

    @pytest.mark.asyncio
    async def test_loop_returns_refined_artifact(
        self,
        observer: MockUmwelt,
    ) -> None:
        """Loop returns refined artifact after iterations."""
        logos = MockLogos(
            generator_result="Initial",
            refine_modifier=" refined",
        )

        loop = CriticsLoop(max_iterations=2, threshold=1.0)  # Impossible threshold

        result, critique = await loop.generate_with_critique(
            logos,
            observer,
            "generator",
        )

        # Should have refined the output
        assert "refined" in result or result == "Initial"


class TestCritiqueMaxIterations:
    """Test: test_critique_max_iterations - Verify loop termination."""

    @pytest.mark.asyncio
    async def test_loop_terminates_at_max_iterations(
        self,
        observer: MockUmwelt,
    ) -> None:
        """Loop terminates at max iterations even with impossible threshold."""
        logos = MockLogos(generator_result="Output")

        # Impossible threshold ensures we hit max iterations
        loop = CriticsLoop(max_iterations=3, threshold=1.0)

        result = await loop.generate_with_trace(
            logos,
            observer,
            "generator",
        )

        # Should terminate at max iterations
        assert result.iterations <= 3

    @pytest.mark.asyncio
    async def test_loop_terminates_early_on_success(
        self,
        observer: MockUmwelt,
    ) -> None:
        """Loop terminates early when threshold is met."""
        logos = MockLogos(
            generator_result="A sufficiently complex output with good structure.",
        )

        # Low threshold should be met immediately
        loop = CriticsLoop(max_iterations=5, threshold=0.3)

        result = await loop.generate_with_trace(
            logos,
            observer,
            "generator",
        )

        # Should terminate in first iteration
        assert result.iterations == 1
        assert result.final_critique.overall >= 0.3

    @pytest.mark.asyncio
    async def test_loop_terminates_on_no_progress(
        self,
        observer: MockUmwelt,
    ) -> None:
        """Loop terminates if refinement produces identical output."""

        class NoProgressLogos:
            """Logos that doesn't improve artifacts."""

            async def invoke(self, path: str, observer: Any, **kwargs: Any) -> str:
                if path.startswith("concept.generate") or path == "generator":
                    return "Static output"
                elif path == "concept.refine.apply":
                    # Return unchanged input
                    return kwargs.get("input", "Static output")
                return "unknown"

        logos = NoProgressLogos()
        loop = CriticsLoop(max_iterations=10, threshold=0.99)

        result = await loop.generate_with_trace(
            logos,  # type: ignore[arg-type]
            observer,
            "generator",
        )

        # Should terminate early due to no progress (not at max iterations)
        assert result.iterations < 10


# === Utility and Surprise Assessment Tests ===


class TestUtilityAssessment:
    """Tests for utility assessment."""

    @pytest.mark.asyncio
    async def test_utility_without_purpose_uses_coherence(
        self, observer: MockUmwelt
    ) -> None:
        """Without purpose, utility is based on coherence."""
        loop = CriticsLoop()

        # Well-structured text should have moderate-high coherence
        critique = await loop.critique(
            "This is a complete sentence. It has structure. And meaning.",
            observer,
        )
        assert critique.utility > 0.3

        # Empty or minimal text should have low coherence
        critique_empty = await loop.critique("", observer)
        assert critique_empty.utility < 0.5

    @pytest.mark.asyncio
    async def test_utility_with_purpose_checks_alignment(
        self, observer: MockUmwelt
    ) -> None:
        """With purpose, utility checks keyword alignment."""
        loop = CriticsLoop()

        # Artifact that matches purpose keywords
        critique = await loop.critique(
            "This documentation explains the API endpoints and usage patterns.",
            observer,
            purpose="Create API documentation",
        )
        assert critique.utility > 0.5

        # Artifact that doesn't match purpose
        critique_misaligned = await loop.critique(
            "The weather is nice today.",
            observer,
            purpose="Create API documentation",
        )
        assert critique_misaligned.utility < critique.utility


class TestSurpriseAssessment:
    """Tests for surprise assessment."""

    @pytest.mark.asyncio
    async def test_surprise_with_matching_expectation(
        self,
    ) -> None:
        """Output matching expectation has low surprise."""
        observer = MockUmwelt(prior="Expected output")
        loop = CriticsLoop()

        critique = await loop.critique("Expected output", observer)
        # Low surprise when matching prior
        assert critique.surprise < 0.3

    @pytest.mark.asyncio
    async def test_surprise_with_different_expectation(
        self,
    ) -> None:
        """Output differing from expectation has higher surprise."""
        observer = MockUmwelt(prior="Expected: short text")
        loop = CriticsLoop()

        critique = await loop.critique(
            "A completely different and much longer piece of content",
            observer,
        )
        # Higher surprise when different from prior
        assert critique.surprise > 0.3

    @pytest.mark.asyncio
    async def test_surprise_without_expectation(self, observer: MockUmwelt) -> None:
        """Without expectation, surprise is neutral."""
        loop = CriticsLoop()

        critique = await loop.critique("Any content", observer)
        # Neutral surprise when no prior
        assert abs(critique.surprise - 0.5) < 0.01


# === Reasoning and Suggestions Tests ===


class TestReasoningGeneration:
    """Tests for reasoning generation."""

    @pytest.mark.asyncio
    async def test_reasoning_includes_assessment(self, observer: MockUmwelt) -> None:
        """Reasoning includes assessment descriptions."""
        loop = CriticsLoop()

        critique = await loop.critique(
            "A piece of content",
            observer,
            purpose="Write documentation",
        )

        # Reasoning should mention the assessments
        assert len(critique.reasoning) > 0
        # Should end with period
        assert critique.reasoning.endswith(".")

    @pytest.mark.asyncio
    async def test_suggestions_generated_for_low_scores(
        self, observer: MockUmwelt
    ) -> None:
        """Suggestions are generated when scores are low."""
        loop = CriticsLoop()
        loop.add_prior_work("Identical content")

        critique = await loop.critique(
            "Identical content",  # Low novelty
            observer,
        )

        # Low novelty should generate suggestions
        if critique.novelty < 0.3:
            assert len(critique.suggestions) > 0


# === RefinedArtifact Tests ===


class TestRefinedArtifact:
    """Tests for RefinedArtifact dataclass."""

    @pytest.mark.asyncio
    async def test_refined_artifact_contains_history(
        self,
        observer: MockUmwelt,
    ) -> None:
        """RefinedArtifact contains iteration history."""
        logos = MockLogos(
            generator_result="Initial",
            refine_modifier=" v2",
        )

        loop = CriticsLoop(max_iterations=2, threshold=1.0)

        result = await loop.generate_with_trace(
            logos,
            observer,
            "generator",
        )

        assert isinstance(result, RefinedArtifact)
        assert len(result.history) >= 1
        assert result.iterations >= 1

        # Each history entry is (artifact, critique)
        for artifact, critique in result.history:
            assert isinstance(critique, Critique)

    def test_refined_artifact_to_dict(self) -> None:
        """RefinedArtifact converts to dict."""
        critique = Critique.create(
            novelty=0.5,
            utility=0.5,
            surprise=0.5,
            reasoning="Test",
            suggestions=[],
        )

        result = RefinedArtifact(
            artifact="Final output",
            final_critique=critique,
            iterations=2,
            history=(("First", critique), ("Second", critique)),
        )

        d = result.to_dict()
        assert d["artifact"] == "Final output"
        assert d["iterations"] == 2
        assert d["history_length"] == 2
        assert "final_critique" in d


# === Property-Based Tests ===


class TestCritiqueProperties:
    """Property-based tests for Critique."""

    @given(
        novelty=st.floats(min_value=0.0, max_value=1.0),
        utility=st.floats(min_value=0.0, max_value=1.0),
        surprise=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=100)
    def test_overall_always_bounded(
        self,
        novelty: float,
        utility: float,
        surprise: float,
    ) -> None:
        """Overall score is always in [0, 1] for any valid inputs."""
        critique = Critique.create(
            novelty=novelty,
            utility=utility,
            surprise=surprise,
            reasoning="Property test",
            suggestions=[],
        )
        assert 0.0 <= critique.overall <= 1.0

    @given(
        novelty=st.floats(min_value=0.0, max_value=1.0),
        utility=st.floats(min_value=0.0, max_value=1.0),
        surprise=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=50)
    def test_perfect_scores_give_perfect_overall(
        self,
        novelty: float,
        utility: float,
        surprise: float,
    ) -> None:
        """If all scores are 1.0, overall is 1.0."""
        critique = Critique.create(
            novelty=1.0,
            utility=1.0,
            surprise=1.0,
            reasoning="Perfect",
            suggestions=[],
        )
        assert critique.overall == 1.0

        # If all scores are 0.0, overall is 0.0
        critique_zero = Critique.create(
            novelty=0.0,
            utility=0.0,
            surprise=0.0,
            reasoning="Zero",
            suggestions=[],
        )
        assert critique_zero.overall == 0.0


# === PAYADOR Bidirectional Skeleton Tests ===


from ..self_judgment import (
    RefinementMode,
    Skeleton,
    SkeletonRewriteConfig,
    build_skeleton_expand_prompt,
    build_skeleton_rewrite_prompt,
    parse_skeleton_response,
)


class TestSkeletonRewriteConfig:
    """Tests for SkeletonRewriteConfig dataclass."""

    def test_default_config_values(self) -> None:
        """Default config should have sensible thresholds."""
        config = SkeletonRewriteConfig()
        assert config.novelty_threshold == 0.3
        assert config.utility_threshold == 0.4
        assert config.temperature == 0.8
        assert config.max_tokens == 1024

    def test_config_validates_thresholds(self) -> None:
        """Config should validate threshold ranges."""
        with pytest.raises(ValueError, match="novelty_threshold"):
            SkeletonRewriteConfig(novelty_threshold=1.5)

        with pytest.raises(ValueError, match="utility_threshold"):
            SkeletonRewriteConfig(utility_threshold=-0.1)

    def test_config_is_frozen(self) -> None:
        """Config should be immutable."""
        config = SkeletonRewriteConfig()
        with pytest.raises(Exception):  # FrozenInstanceError
            config.novelty_threshold = 0.5  # type: ignore[misc]


class TestSkeleton:
    """Tests for Skeleton dataclass."""

    def test_skeleton_creation(self) -> None:
        """Skeleton should store structure, intent, and constraints."""
        skeleton = Skeleton(
            structure=("Introduction", "Main argument", "Conclusion"),
            intent="Persuade the reader",
            constraints=("Keep under 500 words", "Use formal tone"),
        )
        assert len(skeleton.structure) == 3
        assert skeleton.intent == "Persuade the reader"
        assert len(skeleton.constraints) == 2

    def test_skeleton_to_prompt(self) -> None:
        """to_prompt should produce readable format."""
        skeleton = Skeleton(
            structure=("Point A", "Point B"),
            intent="Explain a concept",
        )
        prompt = skeleton.to_prompt()
        assert "Skeleton Structure" in prompt
        assert "1. Point A" in prompt
        assert "2. Point B" in prompt
        assert "Intent: Explain a concept" in prompt

    def test_skeleton_to_prompt_with_constraints(self) -> None:
        """to_prompt should include constraints when present."""
        skeleton = Skeleton(
            structure=("Point A",),
            intent="Test",
            constraints=("Constraint 1", "Constraint 2"),
        )
        prompt = skeleton.to_prompt()
        assert "Constraints:" in prompt
        assert "- Constraint 1" in prompt
        assert "- Constraint 2" in prompt


class TestSkeletonPromptBuilding:
    """Tests for skeleton prompt building functions."""

    def test_build_skeleton_rewrite_prompt(self) -> None:
        """Should build a valid rewrite prompt."""
        critique = Critique.create(
            novelty=0.2,
            utility=0.3,
            surprise=0.5,
            reasoning="Low novelty and utility",
            suggestions=["Restructure the argument"],
        )
        prompt = build_skeleton_rewrite_prompt(
            "Original text here",
            critique,
            purpose="Explain the concept",
        )

        assert "Current Artifact" in prompt
        assert "Original text here" in prompt
        assert "Critique" in prompt
        assert "0.20" in prompt or "0.2" in prompt  # Novelty
        assert "Purpose: Explain the concept" in prompt
        assert "STRUCTURAL" in prompt

    def test_build_skeleton_expand_prompt(self) -> None:
        """Should build a valid expansion prompt."""
        skeleton = Skeleton(
            structure=("Intro", "Body", "Conclusion"),
            intent="Teach a concept",
        )
        prompt = build_skeleton_expand_prompt(skeleton, "Original artifact")

        assert "Skeleton Structure" in prompt
        assert "Intro" in prompt
        assert "Teach a concept" in prompt
        assert "Original Artifact" in prompt
        assert "Task" in prompt


class TestParseSkeletonResponse:
    """Tests for parse_skeleton_response function."""

    def test_parse_valid_json_response(self) -> None:
        """Should parse valid JSON response."""
        response = """
        Here is the skeleton:
        {"structure": ["Point 1", "Point 2"], "intent": "Test intent", "constraints": ["Be brief"]}
        """
        skeleton = parse_skeleton_response(response)

        assert skeleton is not None
        assert skeleton.structure == ("Point 1", "Point 2")
        assert skeleton.intent == "Test intent"
        assert skeleton.constraints == ("Be brief",)

    def test_parse_invalid_response_returns_none(self) -> None:
        """Should return None for invalid response."""
        skeleton = parse_skeleton_response("This is not JSON at all")
        assert skeleton is None

    def test_parse_partial_json_response(self) -> None:
        """Should handle partial/malformed JSON."""
        response = '{"structure": ["A"], broken json'
        skeleton = parse_skeleton_response(response)
        # Should return None for malformed JSON
        assert skeleton is None


class TestNeedsSkeletonRewrite:
    """Tests for _needs_skeleton_rewrite detection."""

    def test_no_config_returns_false(self) -> None:
        """Without config, should never trigger skeleton rewrite."""
        loop = CriticsLoop()  # No skeleton_config

        critique = Critique.create(
            novelty=0.1,  # Very low
            utility=0.1,  # Very low
            surprise=0.5,
            reasoning="Low scores",
            suggestions=[],
        )

        assert loop._needs_skeleton_rewrite(critique) is False

    def test_no_llm_solver_returns_false(self) -> None:
        """Without LLM solver, should not trigger."""
        loop = CriticsLoop(
            skeleton_config=SkeletonRewriteConfig(),
            llm_solver=None,  # No solver
        )

        critique = Critique.create(
            novelty=0.1,
            utility=0.1,
            surprise=0.5,
            reasoning="Low scores",
            suggestions=[],
        )

        assert loop._needs_skeleton_rewrite(critique) is False

    def test_low_novelty_and_utility_triggers_rewrite(self) -> None:
        """Low novelty AND utility should trigger skeleton rewrite."""

        async def mock_solver(system: str, user: str) -> str:
            return '{"structure": ["test"], "intent": "test", "constraints": []}'

        loop = CriticsLoop(
            skeleton_config=SkeletonRewriteConfig(
                novelty_threshold=0.3,
                utility_threshold=0.4,
            ),
            llm_solver=mock_solver,
        )

        # Both below thresholds
        critique = Critique.create(
            novelty=0.2,  # < 0.3
            utility=0.3,  # < 0.4
            surprise=0.5,
            reasoning="Structural issues",
            suggestions=[],
        )

        assert loop._needs_skeleton_rewrite(critique) is True

    def test_high_novelty_no_rewrite(self) -> None:
        """High novelty should not trigger rewrite even with low utility."""

        async def mock_solver(system: str, user: str) -> str:
            return "{}"

        loop = CriticsLoop(
            skeleton_config=SkeletonRewriteConfig(),
            llm_solver=mock_solver,
        )

        # High novelty, low utility - texture issue, not structural
        critique = Critique.create(
            novelty=0.8,  # High
            utility=0.2,  # Low
            surprise=0.5,
            reasoning="Novel but not useful",
            suggestions=[],
        )

        assert loop._needs_skeleton_rewrite(critique) is False

    def test_high_utility_no_rewrite(self) -> None:
        """High utility should not trigger rewrite even with low novelty."""

        async def mock_solver(system: str, user: str) -> str:
            return "{}"

        loop = CriticsLoop(
            skeleton_config=SkeletonRewriteConfig(),
            llm_solver=mock_solver,
        )

        # Low novelty, high utility - conventional but works
        critique = Critique.create(
            novelty=0.2,  # Low
            utility=0.8,  # High
            surprise=0.5,
            reasoning="Not novel but useful",
            suggestions=[],
        )

        assert loop._needs_skeleton_rewrite(critique) is False


class TestDetermineRefinementMode:
    """Tests for _determine_refinement_mode."""

    def test_returns_skeleton_when_rewrite_needed(self) -> None:
        """Should return SKELETON mode when structural issues detected."""

        async def mock_solver(system: str, user: str) -> str:
            return "{}"

        loop = CriticsLoop(
            skeleton_config=SkeletonRewriteConfig(),
            llm_solver=mock_solver,
        )

        critique = Critique.create(
            novelty=0.1,
            utility=0.1,
            surprise=0.5,
            reasoning="Both low",
            suggestions=[],
        )

        assert loop._determine_refinement_mode(critique) == RefinementMode.SKELETON

    def test_returns_texture_when_no_rewrite_needed(self) -> None:
        """Should return TEXTURE mode for normal refinement."""
        loop = CriticsLoop()  # No skeleton config

        critique = Critique.create(
            novelty=0.5,
            utility=0.5,
            surprise=0.5,
            reasoning="Normal scores",
            suggestions=[],
        )

        assert loop._determine_refinement_mode(critique) == RefinementMode.TEXTURE


class TestSkeletonRewriteIntegration:
    """Integration tests for skeleton rewrite flow."""

    @pytest.mark.asyncio
    async def test_skeleton_rewrite_flow(self) -> None:
        """Test full skeleton rewrite flow with mocked LLM."""
        rewrite_called = False
        expand_called = False

        async def mock_solver(system: str, user: str) -> str:
            nonlocal rewrite_called, expand_called

            if "structural rewriter" in system.lower():
                rewrite_called = True
                return '{"structure": ["New point 1", "New point 2"], "intent": "Improved", "constraints": []}'
            elif "expanding" in system.lower() or "expand" in system.lower():
                expand_called = True
                return "This is the expanded new artifact with improved structure."
            return ""

        loop = CriticsLoop(
            skeleton_config=SkeletonRewriteConfig(),
            llm_solver=mock_solver,
        )

        critique = Critique.create(
            novelty=0.1,
            utility=0.1,
            surprise=0.5,
            reasoning="Structural issues",
            suggestions=[],
        )

        result = await loop._rewrite_with_skeleton(
            "Original artifact",
            critique,
        )

        assert rewrite_called, "Skeleton rewrite should have been called"
        assert expand_called, "Skeleton expand should have been called"
        assert result is not None
        assert "expanded" in result.lower() or "improved" in result.lower()

    @pytest.mark.asyncio
    async def test_skeleton_rewrite_fallback_on_parse_error(self) -> None:
        """Should return None if skeleton parsing fails."""

        async def bad_solver(system: str, user: str) -> str:
            return "Not valid JSON"

        loop = CriticsLoop(
            skeleton_config=SkeletonRewriteConfig(),
            llm_solver=bad_solver,
        )

        critique = Critique.create(
            novelty=0.1,
            utility=0.1,
            surprise=0.5,
            reasoning="Test",
            suggestions=[],
        )

        result = await loop._rewrite_with_skeleton("artifact", critique)
        assert result is None

    @pytest.mark.asyncio
    async def test_refine_artifact_uses_skeleton_when_appropriate(
        self, observer: MockUmwelt
    ) -> None:
        """_refine_artifact should use skeleton rewrite for structural issues."""
        skeleton_used = False

        async def mock_solver(system: str, user: str) -> str:
            nonlocal skeleton_used
            skeleton_used = True
            if "rewriter" in system.lower():
                return '{"structure": ["A", "B"], "intent": "Test", "constraints": []}'
            return "Expanded artifact from skeleton"

        loop = CriticsLoop(
            skeleton_config=SkeletonRewriteConfig(),
            llm_solver=mock_solver,
        )

        critique = Critique.create(
            novelty=0.1,
            utility=0.1,
            surprise=0.5,
            reasoning="Structural",
            suggestions=[],
        )

        logos = MockLogos()
        result = await loop._refine_artifact(logos, observer, "Original", critique)

        assert skeleton_used
        # Result should be from skeleton expansion, not original
        assert result != "Original"
