"""
Categorical Probes: Testing LLM Reasoning for Law Satisfaction.

This module implements probes that measure how well LLM reasoning
satisfies categorical laws—specifically monad laws and sheaf coherence.

The core insight from the theory monograph (Chapter 3):
    "Chain-of-thought IS Kleisli composition in the Writer monad.
    The monad laws are rationality constraints on extended reasoning."

And from Chapter 5:
    "Hallucinations are sheaf condition failures—local claims that
    don't glue into a coherent global picture."

Philosophy:
    "The proof IS the decision. The mark IS the witness."
    Every probe run emits Marks for witnessed measurement.
"""

from __future__ import annotations

import hashlib
import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Protocol, Sequence

if TYPE_CHECKING:
    from agents.t.truth_functor import ConstitutionalScore as TFConstitutionalScore

logger = logging.getLogger("kgents.categorical.probes")


# =============================================================================
# LLM Protocol (Dependency Injection)
# =============================================================================


class LLMProtocol(Protocol):
    """Protocol for LLM clients used by probes."""

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> Any:
        """Generate a response from the LLM."""
        ...


# =============================================================================
# Monad Probe Types
# =============================================================================


@dataclass(frozen=True)
class IdentityTestResult:
    """Result of a monad identity law test.

    The identity law states: Adding "trivial" prefixes/suffixes
    should not change the answer.

    Tests:
    - Left identity: η >> f ≡ f (adding "Let me think" prefix)
    - Right identity: f >> η ≡ f (adding "Thus concludes" suffix)
    """

    base_answer: str
    modified_answer: str
    passed: bool
    modification_type: str  # "prefix" or "suffix"
    modification_text: str

    @property
    def score(self) -> float:
        """1.0 if passed, 0.0 otherwise."""
        return 1.0 if self.passed else 0.0


@dataclass(frozen=True)
class AssociativityTestResult:
    """Result of a monad associativity law test.

    The associativity law states: Grouping of reasoning steps
    shouldn't affect the final answer.

    (A >> B) >> C ≡ A >> (B >> C)
    """

    left_grouped_answer: str  # ((A >> B) >> C)
    right_grouped_answer: str  # (A >> (B >> C))
    passed: bool
    steps: tuple[str, ...]

    @property
    def score(self) -> float:
        """1.0 if passed, 0.0 otherwise."""
        return 1.0 if self.passed else 0.0


@dataclass(frozen=True)
class MonadResult:
    """Combined result from all monad law tests."""

    identity_results: tuple[IdentityTestResult, ...]
    associativity_results: tuple[AssociativityTestResult, ...]
    problem: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def identity_score(self) -> float:
        """Average identity law satisfaction (0-1)."""
        if not self.identity_results:
            return 0.0
        return sum(r.score for r in self.identity_results) / len(self.identity_results)

    @property
    def associativity_score(self) -> float:
        """Average associativity law satisfaction (0-1)."""
        if not self.associativity_results:
            return 0.0
        return sum(r.score for r in self.associativity_results) / len(self.associativity_results)

    @property
    def overall_score(self) -> float:
        """Combined monad law score (average of identity and associativity)."""
        scores = []
        if self.identity_results:
            scores.append(self.identity_score)
        if self.associativity_results:
            scores.append(self.associativity_score)
        return sum(scores) / len(scores) if scores else 0.0

    def to_constitutional_score(self) -> TFConstitutionalScore:
        """
        Convert MonadResult to ConstitutionalScore.

        Maps monad law satisfaction to constitutional principles:
        - COMPOSABLE: Direct mapping (monad laws ARE composition laws)
        - ETHICAL: Law satisfaction implies predictability
        - GENERATIVE: Reproducible reasoning
        """
        from agents.t.truth_functor import ConstitutionalScore

        # Law satisfaction maps to COMPOSABLE and ETHICAL
        composable = self.overall_score
        ethical = self.overall_score  # Law-abiding = predictable = ethical

        return ConstitutionalScore(
            tasteful=0.5,  # Neutral - monad laws don't imply tastefulness
            curated=0.5,  # Neutral
            ethical=ethical,
            joy_inducing=0.5,  # Neutral
            composable=composable,
            heterarchical=0.5,  # Neutral
            generative=self.overall_score * 0.8,  # Law-satisfying reasoning is regenerable
        )


# =============================================================================
# MonadProbe: Test Monad Laws on LLM Reasoning
# =============================================================================


class MonadProbe:
    """
    Probe for testing monad law satisfaction in LLM reasoning.

    The monad laws encode rationality constraints:
    - Identity: Trivial modifications shouldn't change answers
    - Associativity: Grouping of steps shouldn't matter

    Usage:
        >>> probe = MonadProbe(llm_client)
        >>> result = await probe.test_all("What is 2 + 2?", n_samples=10)
        >>> print(f"Identity score: {result.identity_score:.2f}")
        >>> print(f"Associativity score: {result.associativity_score:.2f}")

    Teaching:
        gotcha: Temperature affects law satisfaction. Lower temp → better laws.
                Use temperature=0.0 for deterministic testing.
                (Evidence: test_probes.py::test_temperature_affects_laws)
    """

    # Prefixes for identity law testing (should not change answer)
    IDENTITY_PREFIXES = [
        "Let me think step by step. ",
        "I'll work through this carefully. ",
        "Thinking about this problem: ",
    ]

    # Suffixes for identity law testing (should not change answer)
    IDENTITY_SUFFIXES = [
        " Please be precise.",
        " Show your work.",
        " Think carefully.",
    ]

    def __init__(
        self,
        llm: LLMProtocol,
        system_prompt: str = "You are a helpful assistant. Answer concisely.",
        temperature: float = 0.0,  # Deterministic by default
        extract_answer: Callable[[str], str] | None = None,
    ):
        """
        Initialize MonadProbe.

        Args:
            llm: LLM client conforming to LLMProtocol
            system_prompt: System prompt for all generations
            temperature: Generation temperature (0.0 = deterministic)
            extract_answer: Function to extract canonical answer from response
        """
        self.llm = llm
        self.system_prompt = system_prompt
        self.temperature = temperature
        self._extract_answer = extract_answer or self._default_extract_answer

    def _normalize_answer(self, answer: str) -> str:
        """
        Normalize an answer for comparison.

        - Strip whitespace and punctuation
        - Remove currency symbols ($)
        - Remove markdown formatting (**bold**)
        - Normalize "yes/no" variations
        - Handle numeric formats (18 = 18.0 = 18.00)
        """
        import re

        # Remove markdown bold
        answer = re.sub(r"\*\*([^*]+)\*\*", r"\1", answer)

        # Strip and lowercase
        answer = answer.strip().lower()

        # Remove trailing punctuation
        answer = answer.rstrip(".,!?")

        # Remove currency symbols
        answer = answer.replace("$", "").replace("€", "").replace("£", "")

        # Normalize yes/no
        if answer in ("yes", "yep", "correct", "true", "affirmative"):
            return "yes"
        if answer in ("no", "nope", "incorrect", "false", "negative"):
            return "no"

        # Try to normalize numbers (remove trailing .0, .00)
        try:
            num = float(answer)
            if num == int(num):
                return str(int(num))
            return str(num)
        except ValueError:
            pass

        return answer

    def _extract_number(self, text: str) -> str | None:
        """Extract the last number from text."""
        import re

        # Find all numbers (including decimals and negatives)
        # Pattern matches: 18, $18, 18.5, -3.14, etc.
        numbers = re.findall(r"-?\$?[\d,]+\.?\d*", text)

        if numbers:
            # Take the last number, clean it
            num = numbers[-1].replace("$", "").replace(",", "")
            try:
                val = float(num)
                if val == int(val):
                    return str(int(val))
                return str(val)
            except ValueError:
                return str(num)

        return None

    def _default_extract_answer(self, response: str) -> str:
        """
        Extract the canonical answer from a response.

        Strategy:
        1. Look for explicit "Answer: X" or "The answer is X" patterns
        2. Extract just the value/number after the pattern
        3. Normalize the extracted answer

        Override for domain-specific extraction.
        """
        import re

        lines = response.strip().split("\n")

        # Strategy 1: Look for explicit answer patterns
        answer_patterns = [
            r"(?:the\s+)?answer\s*(?:is)?:?\s*(.+)",
            r"(?:she|he|they|it)\s+makes?\s*:?\s*(.+)",
            r"=\s*(.+?)(?:\s|$)",
        ]

        for line in reversed(lines):
            line_lower = line.lower().strip()
            for pattern in answer_patterns:
                match = re.search(pattern, line_lower, re.IGNORECASE)
                if match:
                    extracted = match.group(1).strip()
                    # Try to get just the number
                    num = self._extract_number(extracted)
                    if num:
                        return self._normalize_answer(num)
                    return self._normalize_answer(extracted)

        # Strategy 2: Find the last number in the response
        num = self._extract_number(response)
        if num:
            return self._normalize_answer(num)

        # Strategy 3: Fall back to last non-empty line (normalized)
        for line in reversed(lines):
            if line.strip():
                return self._normalize_answer(line.strip())

        return self._normalize_answer(response.strip())

    async def _solve(self, problem: str) -> str:
        """Generate solution and extract answer."""
        response = await self.llm.generate(
            system=self.system_prompt,
            user=problem,
            temperature=self.temperature,
        )
        # Handle both dict and object responses
        text = response.text if hasattr(response, "text") else response.get("text", str(response))
        return self._extract_answer(text)

    async def test_identity(
        self,
        problem: str,
        n_samples: int = 10,
    ) -> tuple[IdentityTestResult, ...]:
        """
        Test the monad identity laws.

        Left identity: η >> f ≡ f
            Adding a "Let me think" prefix should not change the answer.

        Right identity: f >> η ≡ f
            Adding a concluding phrase should not change the answer.

        Args:
            problem: The problem to solve
            n_samples: Number of samples for majority voting

        Returns:
            Tuple of IdentityTestResult for each modification tested
        """
        results: list[IdentityTestResult] = []

        # Get base answer (mode of n_samples)
        base_answers = [await self._solve(problem) for _ in range(n_samples)]
        base_mode = Counter(base_answers).most_common(1)[0][0]

        # Test left identity (prefix modifications)
        for prefix in self.IDENTITY_PREFIXES:
            modified_problem = prefix + problem
            modified_answers = [await self._solve(modified_problem) for _ in range(n_samples)]
            modified_mode = Counter(modified_answers).most_common(1)[0][0]

            results.append(
                IdentityTestResult(
                    base_answer=base_mode,
                    modified_answer=modified_mode,
                    passed=base_mode == modified_mode,
                    modification_type="prefix",
                    modification_text=prefix,
                )
            )

        # Test right identity (suffix modifications)
        for suffix in self.IDENTITY_SUFFIXES:
            modified_problem = problem + suffix
            modified_answers = [await self._solve(modified_problem) for _ in range(n_samples)]
            modified_mode = Counter(modified_answers).most_common(1)[0][0]

            results.append(
                IdentityTestResult(
                    base_answer=base_mode,
                    modified_answer=modified_mode,
                    passed=base_mode == modified_mode,
                    modification_type="suffix",
                    modification_text=suffix,
                )
            )

        return tuple(results)

    async def test_associativity(
        self,
        problem: str,
        steps: tuple[str, ...],
    ) -> AssociativityTestResult:
        """
        Test the monad associativity law.

        (A >> B) >> C ≡ A >> (B >> C)

        Grouping of reasoning steps shouldn't change the final answer.

        Args:
            problem: The problem to solve
            steps: Reasoning steps to group differently

        Returns:
            AssociativityTestResult
        """
        if len(steps) < 3:
            raise ValueError("Associativity test requires at least 3 steps")

        # Left grouping: ((step1, step2), step3)
        left_prompt = f"{problem}\n\nFirst, let me address these together:\n"
        left_prompt += f"- {steps[0]}\n- {steps[1]}\n"
        left_prompt += f"\nThen separately:\n- {steps[2]}"

        # Right grouping: (step1, (step2, step3))
        right_prompt = f"{problem}\n\nFirst, let me start with:\n"
        right_prompt += f"- {steps[0]}\n"
        right_prompt += f"\nThen address these together:\n- {steps[1]}\n- {steps[2]}"

        left_answer = await self._solve(left_prompt)
        right_answer = await self._solve(right_prompt)

        return AssociativityTestResult(
            left_grouped_answer=left_answer,
            right_grouped_answer=right_answer,
            passed=left_answer == right_answer,
            steps=steps,
        )

    async def test_all(
        self,
        problem: str,
        n_samples: int = 10,
        steps: tuple[str, ...] | None = None,
    ) -> MonadResult:
        """
        Run all monad law tests on a problem.

        Args:
            problem: The problem to solve
            n_samples: Samples for identity tests
            steps: Optional steps for associativity test

        Returns:
            MonadResult with all test results
        """
        identity_results = await self.test_identity(problem, n_samples)

        assoc_results: tuple[AssociativityTestResult, ...] = ()
        if steps:
            assoc_result = await self.test_associativity(problem, steps)
            assoc_results = (assoc_result,)

        return MonadResult(
            identity_results=identity_results,
            associativity_results=assoc_results,
            problem=problem,
        )


# =============================================================================
# Sheaf Detector Types
# =============================================================================


@dataclass(frozen=True)
class Claim:
    """A factual claim extracted from reasoning trace."""

    content: str
    context: str  # What the claim refers to
    source_position: int  # Position in trace (for ordering)


@dataclass(frozen=True)
class ClaimPair:
    """A pair of claims to check for contradiction."""

    claim_a: Claim
    claim_b: Claim

    @property
    def key(self) -> str:
        """Unique key for this pair."""
        return f"{self.claim_a.source_position}:{self.claim_b.source_position}"


@dataclass(frozen=True)
class Violation:
    """A sheaf condition violation (contradiction between claims)."""

    pair: ClaimPair
    explanation: str = ""

    @property
    def claim_a(self) -> Claim:
        return self.pair.claim_a

    @property
    def claim_b(self) -> Claim:
        return self.pair.claim_b


@dataclass(frozen=True)
class CoherenceResult:
    """Result of sheaf coherence detection."""

    is_coherent: bool
    claims: tuple[Claim, ...]
    violations: tuple[Violation, ...]
    trace: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def score(self) -> float:
        """
        Coherence score from 0-1.

        1.0 = perfectly coherent (no violations)
        0.0 = maximally incoherent (every pair contradicts)
        """
        if len(self.claims) < 2:
            return 1.0  # Trivially coherent

        max_violations = len(self.claims) * (len(self.claims) - 1) // 2
        if max_violations == 0:
            return 1.0

        return 1.0 - (len(self.violations) / max_violations)

    @property
    def violation_rate(self) -> float:
        """Proportion of claim pairs that contradict."""
        if len(self.claims) < 2:
            return 0.0
        max_pairs = len(self.claims) * (len(self.claims) - 1) // 2
        return len(self.violations) / max_pairs if max_pairs > 0 else 0.0

    def to_constitutional_score(self) -> TFConstitutionalScore:
        """
        Convert CoherenceResult to ConstitutionalScore.

        Maps sheaf coherence to constitutional principles:
        - ETHICAL: Coherence = honesty = ethical
        - GENERATIVE: Coherent reasoning is regenerable
        - COMPOSABLE: Sheaf gluing = optimal substructure
        """
        from agents.t.truth_functor import ConstitutionalScore

        coherence = self.score

        return ConstitutionalScore(
            tasteful=0.5,  # Neutral
            curated=0.5,  # Neutral
            ethical=coherence,  # Coherence = honesty
            joy_inducing=0.5,  # Neutral
            composable=coherence,  # Sheaf gluing
            heterarchical=0.5,  # Neutral
            generative=coherence,  # Coherent reasoning is regenerable
        )


# =============================================================================
# SheafDetector: Find Coherence Violations
# =============================================================================


class SheafDetector:
    """
    Detector for sheaf coherence violations in LLM reasoning traces.

    Hallucinations are claims that contradict each other. The sheaf
    condition says: local claims must agree on overlaps.

    Philosophy:
        "The whole is more than the sum of its parts—but only when
        the parts fit together."

    Usage:
        >>> detector = SheafDetector(llm_client)
        >>> result = await detector.detect(reasoning_trace)
        >>> if not result.is_coherent:
        ...     for v in result.violations:
        ...         print(f"Contradiction: {v.claim_a.content} vs {v.claim_b.content}")

    Teaching:
        gotcha: Claim extraction is itself an LLM call. Use low temperature
                for consistent extraction.
                (Evidence: test_probes.py::test_claim_extraction_consistency)
    """

    EXTRACTION_PROMPT = """Extract all factual claims from this reasoning trace.

A factual claim is any statement that asserts something specific about the world,
numbers, relationships, or conclusions.

For each claim, provide:
1. The claim itself (exact quote or close paraphrase)
2. The context (what it refers to)

Format each claim as:
CLAIM: [the claim]
CONTEXT: [what it refers to]

Reasoning trace:
{trace}

List all claims:"""

    CONTRADICTION_PROMPT = """Do these two claims contradict each other?

Claim A: {claim_a}
Context A: {context_a}

Claim B: {claim_b}
Context B: {context_b}

Answer only YES or NO, followed by a brief explanation."""

    def __init__(
        self,
        llm: LLMProtocol,
        system_prompt: str = "You are a precise logical analyzer.",
        temperature: float = 0.0,
    ):
        """
        Initialize SheafDetector.

        Args:
            llm: LLM client conforming to LLMProtocol
            system_prompt: System prompt for analysis
            temperature: Generation temperature
        """
        self.llm = llm
        self.system_prompt = system_prompt
        self.temperature = temperature

    async def extract_claims(self, trace: str) -> tuple[Claim, ...]:
        """
        Extract factual claims from a reasoning trace.

        Uses LLM to identify claims for coherence checking.

        Args:
            trace: The reasoning trace to analyze

        Returns:
            Tuple of extracted Claims
        """
        response = await self.llm.generate(
            system=self.system_prompt,
            user=self.EXTRACTION_PROMPT.format(trace=trace),
            temperature=self.temperature,
        )

        text = response.text if hasattr(response, "text") else response.get("text", str(response))
        return self._parse_claims(text)

    def _parse_claims(self, response: str) -> tuple[Claim, ...]:
        """Parse claims from LLM extraction response."""
        claims: list[Claim] = []
        lines = response.strip().split("\n")

        current_claim: str | None = None
        current_context: str | None = None
        position = 0

        for line in lines:
            line = line.strip()
            if line.upper().startswith("CLAIM:"):
                # Save previous claim if exists
                if current_claim:
                    claims.append(
                        Claim(
                            content=current_claim,
                            context=current_context or "unspecified",
                            source_position=position,
                        )
                    )
                    position += 1

                current_claim = line[6:].strip()
                current_context = None
            elif line.upper().startswith("CONTEXT:"):
                current_context = line[8:].strip()

        # Don't forget the last claim
        if current_claim:
            claims.append(
                Claim(
                    content=current_claim,
                    context=current_context or "unspecified",
                    source_position=position,
                )
            )

        return tuple(claims)

    async def check_contradiction(
        self,
        claim_a: Claim,
        claim_b: Claim,
    ) -> tuple[bool, str]:
        """
        Check if two claims contradict each other.

        Args:
            claim_a: First claim
            claim_b: Second claim

        Returns:
            Tuple of (contradicts: bool, explanation: str)
        """
        response = await self.llm.generate(
            system=self.system_prompt,
            user=self.CONTRADICTION_PROMPT.format(
                claim_a=claim_a.content,
                context_a=claim_a.context,
                claim_b=claim_b.content,
                context_b=claim_b.context,
            ),
            temperature=self.temperature,
        )

        text = response.text if hasattr(response, "text") else response.get("text", str(response))
        text_upper = text.upper().strip()

        contradicts = text_upper.startswith("YES")
        explanation = text.strip()

        return contradicts, explanation

    async def detect(self, trace: str) -> CoherenceResult:
        """
        Detect coherence violations in a reasoning trace.

        Algorithm:
        1. Extract factual claims using structured prompting
        2. Check each pair for contradiction
        3. Return violations and coherence score

        Args:
            trace: The reasoning trace to analyze

        Returns:
            CoherenceResult with coherence status and any violations
        """
        claims = await self.extract_claims(trace)

        if len(claims) < 2:
            return CoherenceResult(
                is_coherent=True,
                claims=claims,
                violations=(),
                trace=trace,
            )

        violations: list[Violation] = []

        # Check all pairs
        for i, claim_a in enumerate(claims):
            for claim_b in claims[i + 1 :]:
                contradicts, explanation = await self.check_contradiction(claim_a, claim_b)
                if contradicts:
                    violations.append(
                        Violation(
                            pair=ClaimPair(claim_a=claim_a, claim_b=claim_b),
                            explanation=explanation,
                        )
                    )

        return CoherenceResult(
            is_coherent=len(violations) == 0,
            claims=claims,
            violations=tuple(violations),
            trace=trace,
        )


# =============================================================================
# Unified Probe Runner
# =============================================================================


@dataclass(frozen=True)
class ProbeResults:
    """Combined results from all categorical probes."""

    monad_result: MonadResult | None
    coherence_result: CoherenceResult | None
    problem: str
    trace: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def monad_score(self) -> float:
        """Overall monad law score (0-1)."""
        return self.monad_result.overall_score if self.monad_result else 0.0

    @property
    def coherence_score(self) -> float:
        """Sheaf coherence score (0-1)."""
        return self.coherence_result.score if self.coherence_result else 0.0

    @property
    def combined_score(self) -> float:
        """Combined categorical score (average of monad and coherence)."""
        scores = []
        if self.monad_result:
            scores.append(self.monad_score)
        if self.coherence_result:
            scores.append(self.coherence_score)
        return sum(scores) / len(scores) if scores else 0.0


class CategoricalProbeRunner:
    """
    Unified runner for all categorical probes.

    Runs MonadProbe and SheafDetector together, returning combined results.
    Integrates with Witness for mark emission.

    Usage:
        >>> runner = CategoricalProbeRunner(llm_client)
        >>> results = await runner.probe("What is 2+2?", trace="Let me think...")
        >>> print(f"Combined score: {results.combined_score:.2f}")
    """

    def __init__(
        self,
        llm: LLMProtocol,
        system_prompt: str = "You are a helpful assistant. Answer concisely.",
        temperature: float = 0.0,
        emit_marks: bool = True,
    ):
        """
        Initialize CategoricalProbeRunner.

        Args:
            llm: LLM client
            system_prompt: System prompt for all operations
            temperature: Generation temperature
            emit_marks: Whether to emit Witness marks
        """
        self.monad_probe = MonadProbe(
            llm=llm,
            system_prompt=system_prompt,
            temperature=temperature,
        )
        self.sheaf_detector = SheafDetector(
            llm=llm,
            system_prompt="You are a precise logical analyzer.",
            temperature=temperature,
        )
        self.emit_marks = emit_marks

    async def probe(
        self,
        problem: str,
        trace: str = "",
        n_samples: int = 10,
        steps: tuple[str, ...] | None = None,
        run_monad: bool = True,
        run_sheaf: bool = True,
    ) -> ProbeResults:
        """
        Run categorical probes on a problem/trace.

        Args:
            problem: The problem being solved
            trace: Reasoning trace (for sheaf detection)
            n_samples: Samples for monad identity tests
            steps: Optional steps for monad associativity test
            run_monad: Whether to run monad probes
            run_sheaf: Whether to run sheaf detection

        Returns:
            ProbeResults with all categorical measurements
        """
        monad_result: MonadResult | None = None
        coherence_result: CoherenceResult | None = None

        if run_monad:
            monad_result = await self.monad_probe.test_all(
                problem=problem,
                n_samples=n_samples,
                steps=steps,
            )

        if run_sheaf and trace:
            coherence_result = await self.sheaf_detector.detect(trace)

        results = ProbeResults(
            monad_result=monad_result,
            coherence_result=coherence_result,
            problem=problem,
            trace=trace,
        )

        # Emit witness mark if enabled
        if self.emit_marks:
            await self._emit_probe_mark(results)

        return results

    async def _emit_probe_mark(self, results: ProbeResults) -> None:
        """Emit a Witness mark for the probe results."""
        try:
            from services.witness.mark import Mark
            from services.witness.trace_store import get_mark_store

            content = (
                f"Categorical probe: monad={results.monad_score:.2f}, "
                f"coherence={results.coherence_score:.2f}, "
                f"combined={results.combined_score:.2f}"
            )

            mark = Mark.from_thought(
                content=content,
                source="categorical",
                tags=("categorical", "probe", "phase1"),
                origin="categorical_probe",
            )

            store = get_mark_store()
            store.append(mark)
            logger.debug(f"Emitted categorical probe mark: {mark.id}")

        except ImportError:
            # Witness not available
            logger.debug("Witness not available, skipping mark emission")
        except Exception as e:
            logger.warning(f"Failed to emit probe mark: {e}")


# =============================================================================
# StepExtractor: Automatic Reasoning Step Extraction
# =============================================================================


class StepExtractor:
    """
    Extract reasoning steps from a trace automatically.

    Phase 1 enhancement: Current associativity test requires pre-defined steps.
    This limits applicability. StepExtractor enables automatic step discovery.

    Usage:
        >>> extractor = StepExtractor(llm_client)
        >>> steps = await extractor.extract("Let me think... First, I calculate 5+3=8...")
        >>> print(steps)  # ("5+3=8", "Then multiply by 2", "Result is 16")
    """

    EXTRACTION_PROMPT = """Identify the distinct reasoning steps in this trace.

A step is a self-contained logical move (calculation, inference, lookup, decision).
Return each step on a new line, prefixed with "STEP: ".

Be concise - each step should be 1-2 sentences.

Trace:
{trace}

Steps:"""

    def __init__(
        self,
        llm: LLMProtocol,
        system_prompt: str = "You identify reasoning steps precisely.",
        temperature: float = 0.0,
        min_steps: int = 2,
        max_steps: int = 10,
    ):
        """
        Initialize StepExtractor.

        Args:
            llm: LLM client conforming to LLMProtocol
            system_prompt: System prompt for extraction
            temperature: Generation temperature
            min_steps: Minimum steps to extract (pad if needed)
            max_steps: Maximum steps to return
        """
        self.llm = llm
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.min_steps = min_steps
        self.max_steps = max_steps

    async def extract(self, trace: str) -> tuple[str, ...]:
        """
        Extract reasoning steps from trace.

        Returns tuple of step descriptions suitable for associativity testing.
        """
        response = await self.llm.generate(
            system=self.system_prompt,
            user=self.EXTRACTION_PROMPT.format(trace=trace),
            temperature=self.temperature,
        )

        text = response.text if hasattr(response, "text") else response.get("text", str(response))
        steps = self._parse_steps(text)

        # Ensure we have at least min_steps
        if len(steps) < self.min_steps:
            # Pad with generic steps (fallback)
            padded = list(steps) + [f"Step {i + 1}" for i in range(len(steps), self.min_steps)]
            steps = tuple(padded)

        return steps[: self.max_steps]

    def _parse_steps(self, response: str) -> tuple[str, ...]:
        """Parse steps from LLM extraction response."""
        steps: list[str] = []

        for line in response.strip().split("\n"):
            line = line.strip()
            if line.upper().startswith("STEP:"):
                step = line[5:].strip()
                if step:
                    steps.append(step)

        return tuple(steps)


# =============================================================================
# SymbolicContradictionChecker: Fast Pre-filter for Sheaf Detection
# =============================================================================


class SymbolicContradictionChecker:
    """
    Fast symbolic checks before expensive LLM calls.

    Phase 1 enhancement: Using LLM to check contradictions is circular.
    If the LLM reasons poorly, it'll miss contradictions. Symbolic checks
    catch obvious contradictions without LLM overhead.

    Usage:
        >>> checker = SymbolicContradictionChecker()
        >>> result = checker.check("x = 5", "x = 7")
        >>> print(result)  # True (contradiction detected)
    """

    def check(self, claim_a: str, claim_b: str) -> bool | None:
        """
        Check if two claims contradict each other symbolically.

        Returns:
            True: Definite contradiction detected
            False: Definite compatibility detected
            None: Inconclusive, defer to LLM
        """
        # Try numeric contradiction first
        numeric_result = self.check_numeric_contradiction(claim_a, claim_b)
        if numeric_result is not None:
            return numeric_result

        # Try boolean contradiction
        boolean_result = self.check_boolean_contradiction(claim_a, claim_b)
        if boolean_result is not None:
            return boolean_result

        # Inconclusive - defer to LLM
        return None

    def check_numeric_contradiction(
        self,
        claim_a: str,
        claim_b: str,
    ) -> bool | None:
        """
        Check if claims have contradictory numbers.

        E.g., "x = 5" vs "x = 7" → contradiction
        """
        import re

        # Extract variable-value pairs from both claims
        nums_a = self._extract_numbers(claim_a)
        nums_b = self._extract_numbers(claim_b)

        # If same variable has different values, contradiction
        for var, val_a in nums_a.items():
            if var in nums_b:
                val_b = nums_b[var]
                # Check if values are meaningfully different
                if abs(val_a - val_b) > 0.001:
                    return True

        # No contradiction found (but not necessarily compatible)
        return None

    def check_boolean_contradiction(
        self,
        claim_a: str,
        claim_b: str,
    ) -> bool | None:
        """
        Check for boolean contradictions (yes/no, true/false, is/is not).

        E.g., "The answer is yes" vs "The answer is no" → contradiction
        """
        claim_a_lower = claim_a.lower()
        claim_b_lower = claim_b.lower()

        # Check for direct contradictions
        contradiction_pairs = [
            ("yes", "no"),
            ("true", "false"),
            ("is", "is not"),
            ("can", "cannot"),
            ("will", "will not"),
            ("does", "does not"),
            ("correct", "incorrect"),
            ("possible", "impossible"),
        ]

        for pos, neg in contradiction_pairs:
            # Check if one claim contains pos and other contains neg
            # in similar context (same subject)
            if pos in claim_a_lower and neg in claim_b_lower:
                return True
            if neg in claim_a_lower and pos in claim_b_lower:
                return True

        return None

    def _extract_numbers(self, text: str) -> dict[str, float]:
        """Extract variable-value pairs from text."""
        import re

        results: dict[str, float] = {}

        patterns = [
            r"(\w+)\s*=\s*(-?\d+(?:\.\d+)?)",  # x = 5, x = -3.14
            r"(\w+)\s+is\s+(-?\d+(?:\.\d+)?)",  # x is 5
            r"(\w+):\s*(-?\d+(?:\.\d+)?)",  # x: 5
            r"(\w+)\s+equals?\s+(-?\d+(?:\.\d+)?)",  # x equals 5
            r"(\w+)\s*→\s*(-?\d+(?:\.\d+)?)",  # x → 5
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                var, val = match.groups()
                try:
                    results[var.lower()] = float(val)
                except ValueError:
                    pass

        return results


__all__ = [
    # Monad probes
    "MonadProbe",
    "MonadResult",
    "IdentityTestResult",
    "AssociativityTestResult",
    # Sheaf probes
    "SheafDetector",
    "CoherenceResult",
    "Claim",
    "ClaimPair",
    "Violation",
    # Unified runner
    "CategoricalProbeRunner",
    "ProbeResults",
    # Protocol
    "LLMProtocol",
    # Phase 1 enhancements
    "StepExtractor",
    "SymbolicContradictionChecker",
]
