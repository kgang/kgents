"""
Tests for correlation study infrastructure.

Philosophy:
    "Measure first. Build only what measurement validates."
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

import pytest

from services.categorical.study import (
    CorrelationResult,
    CorrelationStudy,
    Problem,
    ProblemResult,
    ProblemSet,
    ProblemType,
    StudyConfig,
    StudyResult,
)

# =============================================================================
# Mock LLM Client
# =============================================================================


@dataclass
class MockLLMResponse:
    """Mock response matching LLMProtocol."""

    text: str
    model: str = "mock"
    tokens_used: int = 100


class MockLLM:
    """Mock LLM for study testing."""

    def __init__(
        self,
        responses: list[str] | None = None,
        default: str = "42",
        correct_rate: float = 0.8,
    ):
        self._responses = list(responses) if responses else []
        self._default = default
        self._correct_rate = correct_rate
        self.call_count = 0
        self._rng_counter = 0

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> MockLLMResponse:
        """Return mock response."""
        self.call_count += 1

        if self._responses:
            text = self._responses.pop(0)
        else:
            # Simulate correct_rate% correct answers
            self._rng_counter += 1
            if (self._rng_counter % 10) < (self._correct_rate * 10):
                text = f"The answer is {self._default}"
            else:
                text = "The answer is WRONG"

        return MockLLMResponse(text=text)


# =============================================================================
# Problem Tests
# =============================================================================


class TestProblem:
    """Tests for Problem dataclass."""

    def test_check_exact_match(self) -> None:
        """Check passes for exact match."""
        problem = Problem(
            id="test1",
            question="What is 2+2?",
            answer="4",
            problem_type=ProblemType.MATH,
        )

        assert problem.check("4")
        assert problem.check("4.")
        assert problem.check("  4  ")

    def test_check_case_insensitive(self) -> None:
        """Check is case-insensitive."""
        problem = Problem(
            id="test1",
            question="Capital of France?",
            answer="Paris",
            problem_type=ProblemType.MULTI_HOP,
        )

        assert problem.check("paris")
        assert problem.check("PARIS")
        assert problem.check("Paris")

    def test_check_numeric_tolerance(self) -> None:
        """Check allows numeric tolerance."""
        problem = Problem(
            id="test1",
            question="What is pi?",
            answer="3.14159",
            problem_type=ProblemType.MATH,
        )

        assert problem.check("3.14159")
        assert problem.check("3.14158")  # Within tolerance
        assert not problem.check("3.14")

    def test_check_with_commas(self) -> None:
        """Check handles numbers with commas."""
        problem = Problem(
            id="test1",
            question="What is 1000+2000?",
            answer="3000",
            problem_type=ProblemType.MATH,
        )

        assert problem.check("3,000")
        assert problem.check("3000")


class TestProblemSet:
    """Tests for ProblemSet."""

    def test_sample_returns_subset(self) -> None:
        """sample() returns n problems."""
        problems = [Problem(f"p{i}", f"q{i}", f"a{i}", ProblemType.MATH) for i in range(10)]
        ps = ProblemSet("test", problems)

        sample = ps.sample(5)
        assert len(sample) == 5

    def test_sample_returns_all_if_n_exceeds(self) -> None:
        """sample() returns all if n > len."""
        problems = [Problem(f"p{i}", f"q{i}", f"a{i}", ProblemType.MATH) for i in range(5)]
        ps = ProblemSet("test", problems)

        sample = ps.sample(10)
        assert len(sample) == 5


# =============================================================================
# Correlation Tests
# =============================================================================


class TestCorrelationResult:
    """Tests for CorrelationResult."""

    def test_significant_when_p_low(self) -> None:
        """significant property based on p_value."""
        result = CorrelationResult(
            metric_name="test",
            correlation=0.5,
            p_value=0.01,
            n_samples=100,
            mean_when_correct=0.8,
            mean_when_incorrect=0.4,
        )

        assert result.significant

    def test_not_significant_when_p_high(self) -> None:
        """Not significant when p >= 0.05."""
        result = CorrelationResult(
            metric_name="test",
            correlation=0.5,
            p_value=0.1,
            n_samples=100,
            mean_when_correct=0.8,
            mean_when_incorrect=0.4,
        )

        assert not result.significant

    def test_effect_size_categories(self) -> None:
        """Effect size categorized correctly."""
        assert CorrelationResult("t", 0.05, 0.5, 10, 0, 0).effect_size == "negligible"
        assert CorrelationResult("t", 0.15, 0.5, 10, 0, 0).effect_size == "weak"
        assert CorrelationResult("t", 0.35, 0.5, 10, 0, 0).effect_size == "moderate"
        assert CorrelationResult("t", 0.55, 0.5, 10, 0, 0).effect_size == "strong"
        assert CorrelationResult("t", 0.8, 0.5, 10, 0, 0).effect_size == "very_strong"


# =============================================================================
# Study Result Tests
# =============================================================================


class TestStudyResult:
    """Tests for StudyResult."""

    def _make_study_result(
        self,
        identity_r: float = 0.4,
        coherence_r: float = 0.5,
        auc: float = 0.75,
    ) -> StudyResult:
        """Helper to create study result."""
        return StudyResult(
            config=StudyConfig(),
            problem_results=[],
            monad_identity_corr=CorrelationResult("identity", identity_r, 0.01, 100, 0.8, 0.4),
            monad_assoc_corr=None,
            sheaf_coherence_corr=CorrelationResult("coherence", coherence_r, 0.01, 100, 0.9, 0.5),
            combined_auc=auc,
        )

    def test_passed_gate_all_pass(self) -> None:
        """Gate passes when all thresholds met."""
        result = self._make_study_result(
            identity_r=0.35,  # > 0.3
            coherence_r=0.45,  # > 0.4
            auc=0.75,  # > 0.7
        )

        assert result.passed_gate
        assert len(result.blockers) == 0

    def test_gate_blocked_by_identity(self) -> None:
        """Gate blocked when identity correlation too low."""
        result = self._make_study_result(
            identity_r=0.2,  # <= 0.3
            coherence_r=0.5,
            auc=0.8,
        )

        assert not result.passed_gate
        assert "monad_identity" in result.blockers[0]

    def test_gate_blocked_by_coherence(self) -> None:
        """Gate blocked when coherence correlation too low."""
        result = self._make_study_result(
            identity_r=0.4,
            coherence_r=0.3,  # <= 0.4
            auc=0.8,
        )

        assert not result.passed_gate
        assert "sheaf_coherence" in result.blockers[0]

    def test_gate_blocked_by_auc(self) -> None:
        """Gate blocked when AUC too low."""
        result = self._make_study_result(
            identity_r=0.4,
            coherence_r=0.5,
            auc=0.65,  # <= 0.7
        )

        assert not result.passed_gate
        assert "combined_auc" in result.blockers[0]

    def test_to_dict_serialization(self) -> None:
        """to_dict() produces valid dict."""
        result = self._make_study_result()
        d = result.to_dict()

        assert "monad_identity_corr" in d
        assert "sheaf_coherence_corr" in d
        assert "combined_auc" in d
        assert "passed_gate" in d
        assert "blockers" in d


# =============================================================================
# CorrelationStudy Tests
# =============================================================================


class TestCorrelationStudy:
    """Tests for CorrelationStudy runner."""

    @pytest.fixture
    def simple_problem_set(self) -> ProblemSet:
        """Create simple problem set for testing."""
        problems = [
            Problem(
                id=f"p{i}",
                question=f"What is {i}+{i}?",
                answer=str(i * 2),
                problem_type=ProblemType.MATH,
            )
            for i in range(1, 11)
        ]
        return ProblemSet("test", problems)

    @pytest.mark.asyncio
    async def test_run_completes(self, simple_problem_set: ProblemSet) -> None:
        """Study runs to completion."""
        # Mock LLM that returns correct answers
        responses = []
        for i in range(1, 11):
            # For each problem: solution + sheaf extraction + contradiction checks
            responses.extend(
                [
                    f"The answer is {i * 2}",  # Solution
                    f"CLAIM: result is {i * 2}\nCONTEXT: math",  # Sheaf extraction
                ]
            )
            # Identity test responses
            responses.extend([f"The answer is {i * 2}"] * 10)

        llm = MockLLM(responses=responses)
        study = CorrelationStudy(llm, simple_problem_set)

        config = StudyConfig(
            n_problems=5,
            n_samples_per_problem=2,
            run_associativity=False,
        )

        result = await study.run(config)

        assert isinstance(result, StudyResult)
        assert result.monad_identity_corr is not None
        assert result.sheaf_coherence_corr is not None

    def test_compute_correlation_basic(self) -> None:
        """Correlation computed correctly for perfect correlation."""
        llm = MockLLM()
        ps = ProblemSet("test", [])
        study = CorrelationStudy(llm, ps)

        # Perfect positive correlation
        values = [0.0, 0.5, 1.0]
        correct = [False, False, True]

        result = study._compute_correlation("test", values, correct)

        assert result.correlation > 0.8  # Strong positive

    def test_compute_correlation_no_variation(self) -> None:
        """Correlation handles constant values."""
        llm = MockLLM()
        ps = ProblemSet("test", [])
        study = CorrelationStudy(llm, ps)

        # No variation in values
        values = [0.5, 0.5, 0.5]
        correct = [True, False, True]

        result = study._compute_correlation("test", values, correct)

        assert result.correlation == 0.0  # No correlation possible

    def test_compute_auc_perfect(self) -> None:
        """AUC = 1.0 for perfect classifier."""
        llm = MockLLM()
        ps = ProblemSet("test", [])
        study = CorrelationStudy(llm, ps)

        # Higher scores for correct, lower for incorrect
        scores = [0.9, 0.8, 0.7, 0.3, 0.2, 0.1]
        labels = [True, True, True, False, False, False]

        auc = study._compute_auc(scores, labels)

        assert auc == 1.0

    def test_compute_auc_random(self) -> None:
        """AUC ~ 0.5 for random classifier."""
        llm = MockLLM()
        ps = ProblemSet("test", [])
        study = CorrelationStudy(llm, ps)

        # Random scores
        scores = [0.5, 0.5, 0.5, 0.5]
        labels = [True, False, True, False]

        auc = study._compute_auc(scores, labels)

        # Should be around 0.5
        assert 0.4 <= auc <= 0.6


# =============================================================================
# Config Tests
# =============================================================================


class TestStudyConfig:
    """Tests for StudyConfig."""

    def test_defaults(self) -> None:
        """Default config has sensible values."""
        config = StudyConfig()

        assert config.n_problems == 500
        assert config.min_monad_corr == 0.3
        assert config.min_sheaf_corr == 0.4
        assert config.min_combined_auc == 0.7

    def test_custom_config(self) -> None:
        """Custom config overrides defaults."""
        config = StudyConfig(
            n_problems=100,
            temperature=0.5,
        )

        assert config.n_problems == 100
        assert config.temperature == 0.5
