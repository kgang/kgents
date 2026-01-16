"""
Middle-Invariance Probe: Testing that prompt middle is less critical than edges.

Phase 1 hypothesis:
    "The middle of a prompt matters less than the edges. Beginning frames the task;
    end triggers completion. The middle carries detail but tolerates noise."

Testable predictions:
    1. Inserting noise in middle → similar output distribution
    2. Removing middle tokens → similar output (within semantic bounds)
    3. Perturbing edges → different output (control)

Teaching:
    The middle-invariance hypothesis replaces the naive "monoid identity" approach.
    It's categorically more defensible because it aligns with attention mechanisms
    and positional salience in transformer architectures.
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .probes import LLMProtocol

logger = logging.getLogger("kgents.categorical.middle_invariance")


@dataclass(frozen=True)
class MiddleInvarianceResult:
    """Result from middle-invariance testing."""

    test_type: str  # "middle_perturbation", "middle_deletion", "edge_perturbation"
    base_answer: str
    modified_answer: str
    passed: bool  # True if answers match (invariance holds)
    modification_text: str
    n_samples: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def score(self) -> float:
        """1.0 if passed, 0.0 otherwise."""
        return 1.0 if self.passed else 0.0


class MiddleInvarianceProbe:
    """
    Test: Does the middle matter less than the edges?

    The hypothesis is that perturbations to the middle 20-80% of a prompt
    should NOT change the answer, while perturbations to the edges SHOULD.

    Usage:
        >>> probe = MiddleInvarianceProbe(llm_client)
        >>> result = await probe.middle_perturbation_test(llm, "What is 2 + 2?", n=10)
        >>> print(f"Middle invariance: {result.score}")
    """

    def __init__(
        self,
        llm: LLMProtocol,
        system_prompt: str = "You are a helpful assistant. Answer concisely.",
        temperature: float = 0.0,
    ):
        """
        Initialize MiddleInvarianceProbe.

        Args:
            llm: LLM client conforming to LLMProtocol
            system_prompt: System prompt for all generations
            temperature: Generation temperature (0.0 = deterministic)
        """
        self.llm = llm
        self.system_prompt = system_prompt
        self.temperature = temperature

    def _extract_answer(self, response: str) -> str:
        """Extract canonical answer from response."""
        # Simple extraction: use last line or look for "Answer:" pattern
        import re

        lines = response.strip().split("\n")

        # Look for explicit answer pattern
        for line in reversed(lines):
            line_lower = line.lower().strip()
            for pattern in [r"answer\s*(?:is)?:?\s*(.+)", r"=\s*(.+?)(?:\s|$)"]:
                match = re.search(pattern, line_lower, re.IGNORECASE)
                if match:
                    return match.group(1).strip().rstrip(".")

        # Fallback: last line
        if lines:
            return lines[-1].strip()

        return response.strip()

    def _normalize_answer(self, answer: str) -> str:
        """Normalize answer for comparison."""
        answer = answer.lower().strip().rstrip(".,!?")

        # Remove common currency symbols
        answer = answer.replace("$", "").replace("€", "").replace("£", "")

        # Normalize yes/no
        if answer in ("yes", "yep", "correct", "true"):
            return "yes"
        if answer in ("no", "nope", "incorrect", "false"):
            return "no"

        # Try to normalize numbers
        try:
            num = float(answer.replace(",", ""))
            if num == int(num):
                return str(int(num))
            return str(num)
        except ValueError:
            pass

        return answer

    async def _solve(self, prompt: str) -> str:
        """Solve problem and extract answer."""
        response = await self.llm.generate(
            system=self.system_prompt,
            user=prompt,
            temperature=self.temperature,
        )
        text = response.text if hasattr(response, "text") else response.get("text", str(response))
        answer = self._extract_answer(text)
        return self._normalize_answer(answer)

    async def middle_perturbation_test(
        self,
        prompt: str,
        n: int = 50,
    ) -> MiddleInvarianceResult:
        """
        Insert noise tokens in the middle 20-80% of the prompt.
        Measure: How often does this CHANGE the answer?

        If middle-invariance holds: Change rate ≈ 0
        If middle is critical: Change rate > 0

        Args:
            prompt: The problem to solve
            n: Number of samples for majority voting

        Returns:
            MiddleInvarianceResult with pass/fail
        """
        logger.info(f"Testing middle perturbation (n={n})")

        # Get baseline answers
        base_answers = [await self._solve(prompt) for _ in range(n)]
        base_mode = Counter(base_answers).most_common(1)[0][0]

        # Create perturbed prompt: inject noise in middle
        mid_start = len(prompt) // 5
        mid_end = 4 * len(prompt) // 5
        noise_text = " [Note: intermediate detail follows.] "
        perturbed_prompt = (
            prompt[:mid_start]
            + noise_text
            + prompt[mid_start:mid_end]
            + " [End intermediate detail.] "
            + prompt[mid_end:]
        )

        # Get perturbed answers
        perturbed_answers = [await self._solve(perturbed_prompt) for _ in range(n)]
        perturbed_mode = Counter(perturbed_answers).most_common(1)[0][0]

        passed = base_mode == perturbed_mode

        return MiddleInvarianceResult(
            test_type="middle_perturbation",
            base_answer=base_mode,
            modified_answer=perturbed_mode,
            passed=passed,
            modification_text=noise_text,
            n_samples=n,
        )

    async def middle_deletion_test(
        self,
        prompt: str,
        n: int = 50,
    ) -> MiddleInvarianceResult:
        """
        Remove a semantically-redundant middle clause.
        Measure: Does the answer stay the same?

        Args:
            prompt: The problem to solve
            n: Number of samples for majority voting

        Returns:
            MiddleInvarianceResult with pass/fail
        """
        logger.info(f"Testing middle deletion (n={n})")

        # Split by sentences
        sentences = prompt.split(". ")
        if len(sentences) < 3:
            # Not applicable - return trivial pass
            return MiddleInvarianceResult(
                test_type="middle_deletion",
                base_answer="N/A",
                modified_answer="N/A",
                passed=True,
                modification_text="(prompt too short)",
                n_samples=0,
            )

        # Get baseline answers
        base_answers = [await self._solve(prompt) for _ in range(n)]
        base_mode = Counter(base_answers).most_common(1)[0][0]

        # Remove middle sentence
        reduced_prompt = ". ".join(sentences[:1] + sentences[2:])

        # Get reduced answers
        reduced_answers = [await self._solve(reduced_prompt) for _ in range(n)]
        reduced_mode = Counter(reduced_answers).most_common(1)[0][0]

        passed = base_mode == reduced_mode

        return MiddleInvarianceResult(
            test_type="middle_deletion",
            base_answer=base_mode,
            modified_answer=reduced_mode,
            passed=passed,
            modification_text=f"(removed: {sentences[1]})",
            n_samples=n,
        )

    async def edge_perturbation_test(
        self,
        prompt: str,
        n: int = 50,
    ) -> MiddleInvarianceResult:
        """
        CONTROL: Insert noise at the BEGINNING.
        Measure: This SHOULD break things (lower score = hypothesis confirmed).

        Args:
            prompt: The problem to solve
            n: Number of samples for majority voting

        Returns:
            MiddleInvarianceResult with pass/fail (inverted: pass = changed)
        """
        logger.info(f"Testing edge perturbation (control) (n={n})")

        # Get baseline answers
        base_answers = [await self._solve(prompt) for _ in range(n)]
        base_mode = Counter(base_answers).most_common(1)[0][0]

        # Perturb beginning
        prefix = "Ignore this. "
        prefix_perturbed_prompt = prefix + prompt

        # Get perturbed answers
        perturbed_answers = [await self._solve(prefix_perturbed_prompt) for _ in range(n)]
        perturbed_mode = Counter(perturbed_answers).most_common(1)[0][0]

        # INVERTED: We WANT this to differ
        passed = base_mode != perturbed_mode

        return MiddleInvarianceResult(
            test_type="edge_perturbation",
            base_answer=base_mode,
            modified_answer=perturbed_mode,
            passed=passed,  # Pass if they differ
            modification_text=prefix,
            n_samples=n,
        )

    async def test_all(
        self,
        prompt: str,
        n: int = 50,
    ) -> tuple[MiddleInvarianceResult, MiddleInvarianceResult, MiddleInvarianceResult]:
        """
        Run all middle-invariance tests.

        Returns:
            Tuple of (middle_perturbation, middle_deletion, edge_perturbation) results
        """
        middle_pert = await self.middle_perturbation_test(prompt, n)
        middle_del = await self.middle_deletion_test(prompt, n)
        edge_pert = await self.edge_perturbation_test(prompt, n)

        return middle_pert, middle_del, edge_pert


__all__ = ["MiddleInvarianceProbe", "MiddleInvarianceResult"]
