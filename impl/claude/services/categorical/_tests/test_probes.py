"""
Tests for categorical probes (MonadProbe, SheafDetector).

Philosophy:
    "The proof IS the decision. The mark IS the witness."
    These tests verify that probes correctly detect law violations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from services.categorical.probes import (
    AssociativityTestResult,
    CategoricalProbeRunner,
    Claim,
    ClaimPair,
    CoherenceResult,
    IdentityTestResult,
    MonadProbe,
    MonadResult,
    ProbeResults,
    SheafDetector,
    Violation,
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
    """Mock LLM for testing probes."""

    def __init__(self, responses: list[str] | None = None, default: str = "42"):
        self._responses = list(responses) if responses else []
        self._default = default
        self.call_count = 0
        self.last_user: str = ""

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> MockLLMResponse:
        """Return mock response."""
        self.call_count += 1
        self.last_user = user

        if self._responses:
            text = self._responses.pop(0)
        else:
            text = self._default

        return MockLLMResponse(text=text)


# =============================================================================
# MonadProbe Tests
# =============================================================================


class TestMonadProbe:
    """Tests for MonadProbe."""

    @pytest.mark.asyncio
    async def test_identity_test_passes_when_answers_match(self) -> None:
        """Identity law holds when prefixes don't change answers."""
        # All responses return "42" - identity holds
        llm = MockLLM(default="The answer is 42")
        probe = MonadProbe(llm)

        results = await probe.test_identity("What is 2+2?", n_samples=3)

        # Should test multiple prefixes and suffixes
        assert len(results) > 0

        # All should pass since answer is consistent
        for result in results:
            assert result.base_answer == "42"
            assert result.passed

    @pytest.mark.asyncio
    async def test_identity_test_fails_when_prefix_changes_answer(self) -> None:
        """Identity law violated when prefix changes answer."""
        # First 3 (base samples) return "42", then modified returns "43"
        responses = ["42", "42", "42", "43", "43", "43"] * 6  # Enough for all tests
        llm = MockLLM(responses=responses)
        probe = MonadProbe(llm)

        results = await probe.test_identity("What is 2+2?", n_samples=3)

        # At least one should fail
        assert any(not r.passed for r in results)

    @pytest.mark.asyncio
    async def test_associativity_test_basic(self) -> None:
        """Associativity test with three steps."""
        llm = MockLLM(default="The answer is 10")
        probe = MonadProbe(llm)

        steps = ("Add 2 to 3", "Multiply by 2", "Subtract 1")
        result = await probe.test_associativity("What is ((2+3)*2)-1?", steps)

        assert isinstance(result, AssociativityTestResult)
        assert result.steps == steps
        assert result.passed  # Same answer for both groupings

    @pytest.mark.asyncio
    async def test_associativity_requires_three_steps(self) -> None:
        """Associativity test requires at least 3 steps."""
        llm = MockLLM()
        probe = MonadProbe(llm)

        with pytest.raises(ValueError, match="at least 3 steps"):
            await probe.test_associativity("test", ("step1", "step2"))

    @pytest.mark.asyncio
    async def test_test_all_returns_monad_result(self) -> None:
        """test_all combines identity and associativity results."""
        llm = MockLLM(default="The answer is 42")
        probe = MonadProbe(llm)

        result = await probe.test_all(
            "What is 2+2?",
            n_samples=2,
            steps=("Step 1", "Step 2", "Step 3"),
        )

        assert isinstance(result, MonadResult)
        assert len(result.identity_results) > 0
        assert len(result.associativity_results) == 1
        assert 0 <= result.overall_score <= 1

    @pytest.mark.asyncio
    async def test_custom_answer_extractor(self) -> None:
        """Custom answer extractor works."""
        llm = MockLLM(default="The result is FORTY-TWO")

        def custom_extract(response: str) -> str:
            return "42" if "FORTY-TWO" in response else response

        probe = MonadProbe(llm, extract_answer=custom_extract)
        results = await probe.test_identity("test", n_samples=2)

        assert results[0].base_answer == "42"


# =============================================================================
# SheafDetector Tests
# =============================================================================


class TestSheafDetector:
    """Tests for SheafDetector."""

    @pytest.mark.asyncio
    async def test_extract_claims_parses_response(self) -> None:
        """Claim extraction parses formatted response."""
        response = """CLAIM: X equals 5
CONTEXT: Problem setup

CLAIM: Y is greater than X
CONTEXT: Inequality relationship"""

        llm = MockLLM(default=response)
        detector = SheafDetector(llm)

        claims = await detector.extract_claims("Some trace")

        assert len(claims) == 2
        assert claims[0].content == "X equals 5"
        assert claims[0].context == "Problem setup"
        assert claims[1].content == "Y is greater than X"

    @pytest.mark.asyncio
    async def test_check_contradiction_detects_yes(self) -> None:
        """Contradiction check detects YES response."""
        llm = MockLLM(default="YES, these claims contradict because...")
        detector = SheafDetector(llm)

        claim_a = Claim("X = 5", "math", 0)
        claim_b = Claim("X = 6", "math", 1)

        contradicts, explanation = await detector.check_contradiction(claim_a, claim_b)

        assert contradicts
        assert explanation.startswith("YES")

    @pytest.mark.asyncio
    async def test_check_contradiction_detects_no(self) -> None:
        """Contradiction check detects NO response."""
        llm = MockLLM(default="NO, these claims are consistent")
        detector = SheafDetector(llm)

        claim_a = Claim("X = 5", "math", 0)
        claim_b = Claim("Y = 6", "math", 1)

        contradicts, _ = await detector.check_contradiction(claim_a, claim_b)

        assert not contradicts

    @pytest.mark.asyncio
    async def test_detect_coherent_trace(self) -> None:
        """Detect returns coherent for consistent trace."""
        # Mock: extraction returns 2 claims, contradiction check returns NO
        responses = [
            """CLAIM: X equals 5
CONTEXT: Setup

CLAIM: Y equals 10
CONTEXT: Calculation""",
            "NO, these claims don't contradict",
        ]
        llm = MockLLM(responses=responses)
        detector = SheafDetector(llm)

        result = await detector.detect("X=5, Y=10")

        assert result.is_coherent
        assert len(result.violations) == 0
        assert result.score == 1.0

    @pytest.mark.asyncio
    async def test_detect_incoherent_trace(self) -> None:
        """Detect returns incoherent for contradictory trace."""
        responses = [
            """CLAIM: The ball is red
CONTEXT: Color

CLAIM: The ball is blue
CONTEXT: Color""",
            "YES, red and blue contradict",
        ]
        llm = MockLLM(responses=responses)
        detector = SheafDetector(llm)

        result = await detector.detect("The ball is red. The ball is blue.")

        assert not result.is_coherent
        assert len(result.violations) == 1
        assert result.score < 1.0

    def test_coherence_score_calculation(self) -> None:
        """Coherence score calculated correctly."""
        # 3 claims = 3 pairs, 1 violation = 1 - 1/3 = 0.667
        claims = (
            Claim("A", "ctx", 0),
            Claim("B", "ctx", 1),
            Claim("C", "ctx", 2),
        )
        violation = Violation(ClaimPair(claims[0], claims[1]))

        result = CoherenceResult(
            is_coherent=False,
            claims=claims,
            violations=(violation,),
            trace="test",
        )

        assert abs(result.score - 0.667) < 0.01

    def test_coherence_score_trivially_coherent(self) -> None:
        """Single claim is trivially coherent."""
        result = CoherenceResult(
            is_coherent=True,
            claims=(Claim("A", "ctx", 0),),
            violations=(),
            trace="test",
        )

        assert result.score == 1.0


# =============================================================================
# CategoricalProbeRunner Tests
# =============================================================================


class TestCategoricalProbeRunner:
    """Tests for unified probe runner."""

    @pytest.mark.asyncio
    async def test_probe_runs_both(self) -> None:
        """probe() runs both monad and sheaf probes."""
        # Responses for: identity samples, sheaf extraction, contradiction check
        responses = ["42"] * 20 + [
            "CLAIM: X=42\nCONTEXT: answer",
            "NO",
        ]
        llm = MockLLM(responses=responses)
        runner = CategoricalProbeRunner(llm, emit_marks=False)

        result = await runner.probe(
            problem="What is 2+2?",
            trace="Let me think... X=42",
            n_samples=2,
        )

        assert isinstance(result, ProbeResults)
        assert result.monad_result is not None
        assert result.coherence_result is not None

    @pytest.mark.asyncio
    async def test_probe_monad_only(self) -> None:
        """probe() can run monad only."""
        llm = MockLLM(default="42")
        runner = CategoricalProbeRunner(llm, emit_marks=False)

        result = await runner.probe(
            problem="test",
            trace="",  # No trace = no sheaf
            n_samples=2,
            run_sheaf=False,
        )

        assert result.monad_result is not None
        assert result.coherence_result is None

    @pytest.mark.asyncio
    async def test_probe_sheaf_only(self) -> None:
        """probe() can run sheaf only."""
        responses = [
            "CLAIM: X=5\nCONTEXT: test",
        ]
        llm = MockLLM(responses=responses)
        runner = CategoricalProbeRunner(llm, emit_marks=False)

        result = await runner.probe(
            problem="test",
            trace="X=5",
            run_monad=False,
            run_sheaf=True,
        )

        assert result.monad_result is None
        assert result.coherence_result is not None

    def test_combined_score_averages(self) -> None:
        """combined_score averages monad and coherence."""
        monad = MonadResult(
            identity_results=(IdentityTestResult("42", "42", True, "prefix", "test"),),
            associativity_results=(),
            problem="test",
        )
        coherence = CoherenceResult(
            is_coherent=True,
            claims=(),
            violations=(),
            trace="test",
        )

        result = ProbeResults(
            monad_result=monad,
            coherence_result=coherence,
            problem="test",
        )

        # Both perfect = 1.0
        assert result.combined_score == 1.0


# =============================================================================
# Answer Extraction Tests
# =============================================================================


class TestAnswerExtraction:
    """Tests for answer extraction logic."""

    @pytest.mark.asyncio
    async def test_extracts_answer_prefix(self) -> None:
        """Extracts answer after 'Answer:' prefix."""
        llm = MockLLM(default="Let me think...\nAnswer: 42")
        probe = MonadProbe(llm)

        results = await probe.test_identity("test", n_samples=1)
        assert results[0].base_answer == "42"

    @pytest.mark.asyncio
    async def test_extracts_the_answer_is(self) -> None:
        """Extracts answer after 'The answer is' phrase."""
        llm = MockLLM(default="So, the answer is 42.")
        probe = MonadProbe(llm)

        results = await probe.test_identity("test", n_samples=1)
        assert results[0].base_answer == "42"

    @pytest.mark.asyncio
    async def test_falls_back_to_last_line(self) -> None:
        """Falls back to last non-empty line."""
        llm = MockLLM(default="Step 1\nStep 2\n42")
        probe = MonadProbe(llm)

        results = await probe.test_identity("test", n_samples=1)
        assert results[0].base_answer == "42"
