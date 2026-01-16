"""
Monad Variator Probe: Testing semantic-preserving transformations.

Phase 1 hypothesis:
    "Transformations that preserve prompt semantics should preserve behavior.
    These are 'monadic' in the sense that they are morphisms in the category
    of prompts that preserve essence."

Variators:
    1. Whitespace normalization (extra spaces, line breaks)
    2. Reordering non-ordered information (e.g., list items)
    3. [FUTURE] Language translation (too expensive for Phase A)

Teaching:
    These variators test whether the LLM's reasoning is robust to superficial
    changes. High variator scores indicate monadic behavior—essence preservation.
"""

from __future__ import annotations

import logging
import random
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .probes import LLMProtocol

logger = logging.getLogger("kgents.categorical.monad_variators")


@dataclass(frozen=True)
class MonadVariatorResult:
    """Result from monad variator testing."""

    variator_type: str  # "whitespace", "reordering", "language"
    base_answer: str
    variated_answer: str
    passed: bool  # True if answers match (variator preserved semantics)
    variated_prompt: str
    n_samples: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def score(self) -> float:
        """1.0 if passed, 0.0 otherwise."""
        return 1.0 if self.passed else 0.0


class MonadVariatorProbe:
    """
    Test: Do semantically-equivalent transformations preserve behavior?

    Usage:
        >>> probe = MonadVariatorProbe(llm_client)
        >>> result = await probe.whitespace_invariance_test(llm, "What is 2+2?", n=10)
        >>> print(f"Whitespace invariance: {result.score}")
    """

    def __init__(
        self,
        llm: LLMProtocol,
        system_prompt: str = "You are a helpful assistant. Answer concisely.",
        temperature: float = 0.0,
    ):
        """
        Initialize MonadVariatorProbe.

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

    async def whitespace_invariance_test(
        self,
        prompt: str,
        n: int = 30,
    ) -> MonadVariatorResult:
        """
        Add extra whitespace throughout.
        Measure: Should not change answer.

        Args:
            prompt: The problem to solve
            n: Number of samples for majority voting

        Returns:
            MonadVariatorResult with pass/fail
        """
        logger.info(f"Testing whitespace invariance (n={n})")

        # Get baseline answers
        base_answers = [await self._solve(prompt) for _ in range(n)]
        base_mode = Counter(base_answers).most_common(1)[0][0]

        # Double all spaces
        spaced_prompt = re.sub(r" ", "  ", prompt)

        # Get spaced answers
        spaced_answers = [await self._solve(spaced_prompt) for _ in range(n)]
        spaced_mode = Counter(spaced_answers).most_common(1)[0][0]

        passed = base_mode == spaced_mode

        return MonadVariatorResult(
            variator_type="whitespace",
            base_answer=base_mode,
            variated_answer=spaced_mode,
            passed=passed,
            variated_prompt=spaced_prompt,
            n_samples=n,
        )

    async def reordering_invariance_test(
        self,
        prompt: str,
        items: list[str],
        n: int = 30,
    ) -> MonadVariatorResult:
        """
        Given a prompt with an unordered list of items, shuffle the list.
        Measure: Should not change answer.

        Example: "Given colors: red, blue, green" → "Given colors: green, blue, red"

        Args:
            prompt: The problem to solve (must contain items as comma-separated list)
            items: List of items to shuffle (must appear in prompt)
            n: Number of samples for majority voting

        Returns:
            MonadVariatorResult with pass/fail
        """
        logger.info(f"Testing reordering invariance (n={n})")

        # Get baseline answers
        base_answers = [await self._solve(prompt) for _ in range(n)]
        base_mode = Counter(base_answers).most_common(1)[0][0]

        # Shuffle items
        shuffled_items = items.copy()
        random.shuffle(shuffled_items)

        original_list = ", ".join(items)
        shuffled_list = ", ".join(shuffled_items)

        # Replace in prompt
        perturbed_prompt = prompt.replace(original_list, shuffled_list)

        # Get shuffled answers
        shuffled_answers = [await self._solve(perturbed_prompt) for _ in range(n)]
        shuffled_mode = Counter(shuffled_answers).most_common(1)[0][0]

        passed = base_mode == shuffled_mode

        return MonadVariatorResult(
            variator_type="reordering",
            base_answer=base_mode,
            variated_answer=shuffled_mode,
            passed=passed,
            variated_prompt=perturbed_prompt,
            n_samples=n,
        )

    async def language_invariance_test(
        self,
        prompt: str,
        n: int = 30,
    ) -> MonadVariatorResult:
        """
        Translate prompt to Spanish, then back to English.
        Measure: Does the answer stay the same?

        NOTE: This is EXPENSIVE (2 extra LLM calls per sample).
        Skip for Phase A toy example.

        Args:
            prompt: The problem to solve
            n: Number of samples for majority voting

        Returns:
            MonadVariatorResult with pass/fail
        """
        logger.info(f"Testing language invariance (n={n}) [EXPENSIVE]")

        # Get baseline answers
        base_answers = [await self._solve(prompt) for _ in range(n)]
        base_mode = Counter(base_answers).most_common(1)[0][0]

        # Translate to Spanish
        spanish_response = await self.llm.generate(
            system="You are a translator.",
            user=f"Translate to Spanish: {prompt}",
            temperature=0.0,
        )
        spanish = (
            spanish_response.text
            if hasattr(spanish_response, "text")
            else spanish_response.get("text", str(spanish_response))
        )

        # Translate back to English
        back_to_english_response = await self.llm.generate(
            system="You are a translator.",
            user=f"Translate to English: {spanish}",
            temperature=0.0,
        )
        back_to_english = (
            back_to_english_response.text
            if hasattr(back_to_english_response, "text")
            else back_to_english_response.get("text", str(back_to_english_response))
        )

        # Get translated answers
        translated_answers = [await self._solve(back_to_english) for _ in range(n)]
        translated_mode = Counter(translated_answers).most_common(1)[0][0]

        passed = base_mode == translated_mode

        return MonadVariatorResult(
            variator_type="language",
            base_answer=base_mode,
            variated_answer=translated_mode,
            passed=passed,
            variated_prompt=back_to_english,
            n_samples=n,
        )

    async def test_all(
        self,
        prompt: str,
        items: list[str] | None = None,
        n: int = 30,
        skip_language: bool = True,
    ) -> dict[str, MonadVariatorResult]:
        """
        Run all variator tests (except language by default).

        Args:
            prompt: The problem to solve
            items: Optional list of items for reordering test
            n: Number of samples
            skip_language: If True, skip expensive language test

        Returns:
            Dict of variator_type -> result
        """
        results = {}

        # Always run whitespace
        results["whitespace"] = await self.whitespace_invariance_test(prompt, n)

        # Run reordering if items provided
        if items:
            results["reordering"] = await self.reordering_invariance_test(prompt, items, n)

        # Run language if requested (expensive)
        if not skip_language:
            results["language"] = await self.language_invariance_test(prompt, n)

        return results


__all__ = ["MonadVariatorProbe", "MonadVariatorResult"]
