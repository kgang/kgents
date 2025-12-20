"""
Principle Checker: Validates artifacts against the seven principles.

The Krisis stance - judgment and evaluation.
Checks if a target (agent, spec, or description) embodies the principles.

See: spec/principles/node.md for the check aspect specification.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .types import (
    THE_SEVEN_PRINCIPLES,
    THE_SEVEN_QUESTIONS,
    CheckResult,
    Principle,
    PrincipleCheck,
    Stance,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


@dataclass
class CheckJudgment:
    """Result of evaluating a target against a single question."""

    passed: bool
    evidence: str
    matched_anti_patterns: tuple[str, ...]


class PrincipleChecker:
    """
    Validates targets against the seven principles.

    The checker evaluates targets by:
    1. Analyzing the target description/code
    2. Checking against each principle's question
    3. Matching against known anti-patterns
    4. Returning detailed results with citations

    Example:
        checker = PrincipleChecker()
        result = await checker.check("my_agent.py", observer)
        if not result.passed:
            for check in result.checks:
                if not check.passed:
                    print(f"Failed: {check.name} - {check.citation}")
    """

    def __init__(self) -> None:
        """Initialize the checker."""
        self._principles = THE_SEVEN_PRINCIPLES
        self._questions = THE_SEVEN_QUESTIONS

    async def check(
        self,
        target: str,
        observer: "Umwelt[Any, Any] | None" = None,
        principles: list[int] | None = None,
        context: str | None = None,
    ) -> CheckResult:
        """
        Evaluate target against principles.

        Args:
            target: Target to check (description, code, or identifier)
            observer: Optional observer context
            principles: Optional list of principle numbers to check (1-7)
            context: Optional additional context about the target

        Returns:
            CheckResult with pass/fail and detailed checks
        """
        checks: list[PrincipleCheck] = []

        for principle in self._principles:
            # Skip if not in filter
            if principles and principle.number not in principles:
                continue

            judgment = await self._evaluate(target, principle, context)

            checks.append(
                PrincipleCheck(
                    principle=principle.number,
                    name=principle.name,
                    question=principle.question,
                    passed=judgment.passed,
                    citation=judgment.evidence,
                    anti_patterns=judgment.matched_anti_patterns,
                )
            )

        return CheckResult(
            target=target,
            passed=all(c.passed for c in checks),
            checks=tuple(checks),
            stance=Stance.KRISIS,
        )

    async def _evaluate(
        self,
        target: str,
        principle: Principle,
        context: str | None = None,
    ) -> CheckJudgment:
        """
        Evaluate a target against a single principle.

        Uses heuristic matching against anti-patterns and positive signals.

        Args:
            target: Target description/code
            principle: The principle to check against
            context: Additional context

        Returns:
            CheckJudgment with pass/fail and evidence
        """
        combined = f"{target} {context or ''}".lower()

        # Check for anti-pattern matches
        matched_patterns: list[str] = []
        for anti_pattern in principle.anti_patterns:
            # Convert anti-pattern to keywords
            keywords = self._extract_keywords(anti_pattern)
            if any(kw in combined for kw in keywords):
                matched_patterns.append(anti_pattern)

        # Determine pass/fail based on anti-pattern matches
        if matched_patterns:
            return CheckJudgment(
                passed=False,
                evidence=f"Matches anti-pattern(s): {'; '.join(matched_patterns)}",
                matched_anti_patterns=tuple(matched_patterns),
            )

        # Check for positive signals based on principle
        positive_signals = self._get_positive_signals(principle.number)
        found_positives = [s for s in positive_signals if s in combined]

        if found_positives:
            return CheckJudgment(
                passed=True,
                evidence=f"Shows positive signals: {', '.join(found_positives[:3])}",
                matched_anti_patterns=(),
            )

        # Default: pass with no strong evidence either way
        return CheckJudgment(
            passed=True,
            evidence="No anti-patterns detected",
            matched_anti_patterns=(),
        )

    def _extract_keywords(self, anti_pattern: str) -> list[str]:
        """Extract searchable keywords from an anti-pattern description."""
        # Remove quotes and common words
        text = anti_pattern.lower()
        text = re.sub(r"[\"']", "", text)

        # Extract meaningful words (3+ chars)
        words = re.findall(r"\b[a-z]{3,}\b", text)

        # Filter out common words
        stopwords = {
            "the",
            "and",
            "for",
            "that",
            "with",
            "are",
            "have",
            "from",
            "this",
            "but",
            "not",
            "just",
            "case",
            "added",
            "kept",
        }
        keywords = [w for w in words if w not in stopwords]

        return keywords

    def _get_positive_signals(self, principle_number: int) -> list[str]:
        """Get positive signal keywords for a principle."""
        signals: dict[int, list[str]] = {
            1: [  # Tasteful
                "clear purpose",
                "justified",
                "focused",
                "single responsibility",
                "one thing well",
            ],
            2: [  # Curated
                "intentional",
                "selected",
                "quality",
                "unique value",
                "earned its place",
            ],
            3: [  # Ethical
                "transparent",
                "privacy",
                "human agency",
                "honest",
                "augment",
            ],
            4: [  # Joy-Inducing
                "delight",
                "personality",
                "warmth",
                "surprise",
                "serendipity",
            ],
            5: [  # Composable
                "compose",
                "morphism",
                "identity",
                "associative",
                "single output",
            ],
            6: [  # Heterarchical
                "flux",
                "autonomous",
                "contextual",
                "peer-to-peer",
                "dynamic",
            ],
            7: [  # Generative
                "spec",
                "compression",
                "regenerate",
                "derive",
                "compressed",
            ],
        }
        return signals.get(principle_number, [])

    async def check_quick(
        self,
        target: str,
        principle: int,
    ) -> bool:
        """
        Quick check for a single principle.

        Args:
            target: Target to check
            principle: Principle number (1-7)

        Returns:
            True if passes, False otherwise
        """
        if principle < 1 or principle > 7:
            return False

        p = self._principles[principle - 1]
        judgment = await self._evaluate(target, p, None)
        return judgment.passed

    def get_question(self, principle: int) -> str:
        """
        Get the question for a principle.

        Args:
            principle: Principle number (1-7)

        Returns:
            The question to ask
        """
        if 1 <= principle <= 7:
            return self._questions[principle - 1]
        return ""

    def get_anti_patterns(self, principle: int) -> tuple[str, ...]:
        """
        Get anti-patterns for a principle.

        Args:
            principle: Principle number (1-7)

        Returns:
            Tuple of anti-pattern descriptions
        """
        if 1 <= principle <= 7:
            return self._principles[principle - 1].anti_patterns
        return ()


# === Factory Function ===


def create_principle_checker() -> PrincipleChecker:
    """Create a PrincipleChecker instance."""
    return PrincipleChecker()


# === Exports ===

__all__ = [
    "PrincipleChecker",
    "CheckJudgment",
    "create_principle_checker",
]
