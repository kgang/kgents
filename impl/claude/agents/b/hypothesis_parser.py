"""
Hypothesis Response Parser: Parse LLM responses into structured hypotheses.

Extracted from hypothesis.py (H14) as part of Phase D polish.

This module handles parsing of LLM-generated hypothesis responses,
which have a specific format with sections for hypotheses, reasoning,
and suggested tests.

Expected format:
    HYPOTHESES:
    1. STATEMENT: ...
       CONFIDENCE: 0.7
       NOVELTY: exploratory
       FALSIFIABLE_BY:
       - ...
       SUPPORTS_OBSERVATIONS: 0, 1
       ASSUMPTIONS:
       - ...

    REASONING_CHAIN:
    1. ...
    2. ...

    SUGGESTED_TESTS:
    - ...
    - ...
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class NoveltyLevel(Enum):
    """Classification of hypothesis novelty."""

    INCREMENTAL = "incremental"  # Builds on existing knowledge
    EXPLORATORY = "exploratory"  # Tests new territory
    PARADIGM_SHIFTING = "paradigm_shifting"  # Challenges fundamentals


@dataclass
class Hypothesis:
    """
    A testable scientific hypothesis.

    The falsifiable_by field is REQUIRED - a hypothesis without
    falsification criteria is not scientific (Popper).
    """

    statement: str  # The hypothesis itself
    confidence: float  # 0.0-1.0, epistemic confidence
    novelty: NoveltyLevel  # How novel is this hypothesis
    falsifiable_by: list[str]  # What would disprove this (REQUIRED)
    supporting_observations: list[int]  # Indices into input observations
    assumptions: list[str]  # Unstated assumptions

    def __post_init__(self) -> None:
        # Validate confidence bounds
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
        # Ensure falsifiability
        if not self.falsifiable_by:
            raise ValueError("Hypothesis must have falsification criteria")

    def __str__(self) -> str:
        lines = [
            f"Hypothesis: {self.statement}",
            f"  Confidence: {self.confidence:.0%}",
            f"  Novelty: {self.novelty.value}",
            "  Falsifiable by:",
        ]
        for falsifiable in self.falsifiable_by:
            lines.append(f"    - {falsifiable}")
        if self.assumptions:
            lines.append("  Assumptions:")
            for assumption in self.assumptions:
                lines.append(f"    - {assumption}")
        return "\n".join(lines)


@dataclass
class ParsedHypothesisResponse:
    """Parsed hypothesis response from LLM."""

    hypotheses: list[Hypothesis]
    reasoning_chain: list[str]
    suggested_tests: list[str]

    def __str__(self) -> str:
        lines = ["HYPOTHESES:"]
        for i, h in enumerate(self.hypotheses, 1):
            lines.append(f"\n{i}. {h}")
        lines.append("\nREASONING CHAIN:")
        for i, r in enumerate(self.reasoning_chain, 1):
            lines.append(f"  {i}. {r}")
        lines.append("\nSUGGESTED TESTS:")
        for t in self.suggested_tests:
            lines.append(f"  - {t}")
        return "\n".join(lines)


class HypothesisResponseParser:
    """
    Parse LLM responses into structured hypotheses.

    Handles the specific format expected from HypothesisEngine
    with sections for hypotheses, reasoning chain, and suggested tests.

    Robust to:
    - Missing sections
    - Malformed hypothesis entries
    - Incomplete data (provides defaults)
    """

    def parse(self, response: str) -> ParsedHypothesisResponse:
        """
        Parse LLM response into structured format.

        Args:
            response: Raw LLM response text

        Returns:
            ParsedHypothesisResponse with parsed data

        Raises:
            ValueError: If no valid hypotheses found in response
        """
        hypotheses: list[Hypothesis] = []
        reasoning_chain: list[str] = []
        suggested_tests: list[str] = []

        lines = response.strip().split("\n")
        section: Optional[str] = None
        current_hypothesis: dict[str, Any] = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect section headers
            upper = line.upper()
            if upper.startswith("HYPOTHES") or upper.startswith("**HYPOTHES"):
                section = "hypotheses"
                continue
            elif upper.startswith("REASONING") or upper.startswith("**REASONING"):
                # Save any pending hypothesis
                if current_hypothesis.get("statement"):
                    hypotheses.append(self._build_hypothesis(current_hypothesis))
                    current_hypothesis = {}
                section = "reasoning"
                continue
            elif upper.startswith("SUGGESTED") or upper.startswith("**SUGGESTED"):
                section = "tests"
                continue

            # Parse content based on section
            if section == "hypotheses":
                current_hypothesis = self._parse_hypothesis_line(
                    line, current_hypothesis, hypotheses
                )

            elif section == "reasoning":
                reasoning_chain = self._parse_reasoning_line(line, reasoning_chain)

            elif section == "tests":
                suggested_tests = self._parse_test_line(line, suggested_tests)

        # Don't forget the last hypothesis
        if current_hypothesis.get("statement"):
            hypotheses.append(self._build_hypothesis(current_hypothesis))

        # Validate we got at least one hypothesis
        if not hypotheses:
            raise ValueError("No valid hypotheses found in response")

        return ParsedHypothesisResponse(
            hypotheses=hypotheses,
            reasoning_chain=reasoning_chain,
            suggested_tests=suggested_tests,
        )

    def _parse_hypothesis_line(
        self,
        line: str,
        current: dict[str, Any],
        hypotheses: list[Hypothesis],
    ) -> dict[str, Any]:
        """Parse a line in the hypotheses section."""
        # New hypothesis detected
        if line[0].isdigit() and ". STATEMENT:" in line.upper():
            # Save previous hypothesis
            if current.get("statement"):
                hypotheses.append(self._build_hypothesis(current))
            current = {
                "statement": line.split(":", 1)[1].strip() if ":" in line else "",
                "falsifiable_by": [],
                "assumptions": [],
                "supporting_observations": [],
            }
        elif "STATEMENT:" in line.upper():
            current["statement"] = line.split(":", 1)[1].strip()
        elif "CONFIDENCE:" in line.upper():
            try:
                val = line.split(":", 1)[1].strip()
                current["confidence"] = float(val)
            except ValueError:
                current["confidence"] = 0.5
        elif "NOVELTY:" in line.upper():
            val = line.split(":", 1)[1].strip().lower()
            current["novelty"] = val
        elif "FALSIFIABLE_BY:" in line.upper():
            current["_section"] = "falsifiable"
        elif "SUPPORTS_OBS" in line.upper() or "SUPPORTING_OBS" in line.upper():
            val = line.split(":", 1)[1].strip() if ":" in line else ""
            try:
                indices = [
                    int(x.strip()) for x in val.split(",") if x.strip().isdigit()
                ]
                current["supporting_observations"] = indices
            except ValueError:
                pass
            current["_section"] = None
        elif "ASSUMPTIONS:" in line.upper():
            current["_section"] = "assumptions"
        elif line.startswith("-") or line.startswith("*"):
            text = line.lstrip("-* ").strip()
            subsection = current.get("_section")
            if subsection == "falsifiable" and text:
                current["falsifiable_by"].append(text)
            elif subsection == "assumptions" and text:
                current["assumptions"].append(text)

        return current

    def _parse_reasoning_line(self, line: str, reasoning_chain: list[str]) -> list[str]:
        """Parse a line in the reasoning chain section."""
        if line[0].isdigit():
            text = line.lstrip("0123456789.-) ").strip()
            if text:
                reasoning_chain.append(text)
        elif line.startswith("-") or line.startswith("*"):
            text = line.lstrip("-* ").strip()
            if text:
                reasoning_chain.append(text)
        return reasoning_chain

    def _parse_test_line(self, line: str, suggested_tests: list[str]) -> list[str]:
        """Parse a line in the suggested tests section."""
        if line.startswith("-") or line.startswith("*") or line[0].isdigit():
            text = line.lstrip("-*0123456789.) ").strip()
            if text:
                suggested_tests.append(text)
        return suggested_tests

    def _build_hypothesis(self, data: dict[str, Any]) -> Hypothesis:
        """
        Build a Hypothesis from parsed data with defaults.

        Handles missing or malformed data gracefully.
        """
        # Map novelty string to enum
        novelty_str = data.get("novelty", "incremental").lower()
        novelty_map = {
            "incremental": NoveltyLevel.INCREMENTAL,
            "exploratory": NoveltyLevel.EXPLORATORY,
            "paradigm_shifting": NoveltyLevel.PARADIGM_SHIFTING,
            "paradigm-shifting": NoveltyLevel.PARADIGM_SHIFTING,
        }
        novelty = novelty_map.get(novelty_str, NoveltyLevel.INCREMENTAL)

        # Ensure falsifiable_by has at least one entry
        falsifiable_by = data.get("falsifiable_by", [])
        if not falsifiable_by:
            falsifiable_by = [
                "[No falsification criteria provided - hypothesis incomplete]"
            ]

        return Hypothesis(
            statement=data.get("statement", ""),
            confidence=min(1.0, max(0.0, data.get("confidence", 0.5))),
            novelty=novelty,
            falsifiable_by=falsifiable_by,
            supporting_observations=data.get("supporting_observations", []),
            assumptions=data.get("assumptions", []),
        )


# Convenience function


def parse_hypothesis_response(response: str) -> ParsedHypothesisResponse:
    """
    Parse LLM hypothesis response.

    Args:
        response: Raw LLM response text

    Returns:
        ParsedHypothesisResponse with structured data

    Raises:
        ValueError: If no valid hypotheses found
    """
    parser = HypothesisResponseParser()
    return parser.parse(response)
