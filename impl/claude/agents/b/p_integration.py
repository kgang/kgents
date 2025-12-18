"""
B-gent Hypothesis Parser Integration with P-gents Protocol

This module provides adapters that make B-gent hypothesis parsers conform to
the P-gents Parser[A] protocol.

Architecture:
- Wraps HypothesisResponseParser to implement Parser[ParsedHypothesisResponse]
- Enables composition with other P-gents parsers
- Maintains backward compatibility with existing B-gent code
"""

from __future__ import annotations

from typing import Any, Iterator, Optional

from agents.p.core import (
    Parser,
    ParserConfig as PParserConfig,
    ParseResult as PParseResult,
)

from .hypothesis_parser import (
    HypothesisResponseParser,
    ParsedHypothesisResponse,
)


class BgentHypothesisParser:
    """
    B-gent hypothesis parser conforming to P-gents Parser[ParsedHypothesisResponse].

    Bridges B-gent's HypothesisResponseParser with P-gents Parser protocol,
    enabling composition and standardization.

    Example:
        >>> from agents.b.p_integration import hypothesis_parser
        >>> parser = hypothesis_parser()
        >>> result = parser.parse(llm_response)
        >>> if result.success:
        ...     for h in result.value.hypotheses:
        ...         print(f"- {h.statement} (confidence: {h.confidence:.0%})")
    """

    def __init__(self, config: Optional[PParserConfig] = None):
        self.config = config or PParserConfig()
        self._parser = HypothesisResponseParser()

    def parse(self, text: str) -> PParseResult[ParsedHypothesisResponse]:
        """
        Parse LLM response into structured hypotheses.

        Args:
            text: LLM response with HYPOTHESES / REASONING / TESTS sections

        Returns:
            PParseResult[ParsedHypothesisResponse] with parsed hypotheses
        """
        try:
            parsed = self._parser.parse(text)

            # Calculate confidence based on hypothesis quality
            confidence = self._assess_confidence(parsed)

            return PParseResult(
                success=True,
                value=parsed,
                strategy="b-gent:hypothesis",
                confidence=confidence,
                metadata={
                    "num_hypotheses": len(parsed.hypotheses),
                    "num_reasoning_steps": len(parsed.reasoning_chain),
                    "num_tests": len(parsed.suggested_tests),
                    "avg_hypothesis_confidence": sum(h.confidence for h in parsed.hypotheses)
                    / len(parsed.hypotheses),
                },
            )

        except ValueError as e:
            return PParseResult(
                success=False,
                error=str(e),
                strategy="b-gent:hypothesis",
                confidence=0.0,
            )

    def parse_stream(
        self, tokens: Iterator[str]
    ) -> Iterator[PParseResult[ParsedHypothesisResponse]]:
        """
        Stream parsing for hypotheses (accumulate and parse).

        Since hypothesis parsing requires complete sections,
        we accumulate tokens and attempt parsing at section boundaries.
        """
        accumulated = []
        section_markers = ["HYPOTHESES", "REASONING", "SUGGESTED"]

        for token in tokens:
            accumulated.append(token)
            text = "".join(accumulated)

            # Try parsing at potential section boundaries
            if any(marker in token.upper() for marker in section_markers):
                result = self.parse(text)
                if result.success:
                    # Emit partial result
                    yield PParseResult(
                        success=True,
                        value=result.value,
                        strategy=result.strategy,
                        confidence=result.confidence * 0.9,  # Reduce for partial
                        partial=True,
                        metadata=result.metadata,
                    )

        # Final parse
        final_text = "".join(accumulated)
        yield self.parse(final_text)

    def configure(self, **config: Any) -> "BgentHypothesisParser":
        """Return new parser with updated P-gents config."""
        new_config = PParserConfig(**{**vars(self.config), **config})
        new_config.validate()
        return BgentHypothesisParser(config=new_config)

    def _assess_confidence(self, parsed: ParsedHypothesisResponse) -> float:
        """
        Assess confidence in parsed hypothesis response.

        Factors:
        - Number of hypotheses (at least 1, ideally 2-5)
        - Quality of falsification criteria
        - Presence of reasoning chain
        - Presence of suggested tests
        - Hypothesis confidence scores
        """
        confidence = 0.5  # Base confidence

        # Hypotheses count (optimal: 2-5)
        num_hyp = len(parsed.hypotheses)
        if num_hyp >= 1:
            confidence += 0.2
        if 2 <= num_hyp <= 5:
            confidence += 0.1

        # Quality of falsification criteria
        has_good_falsification = all(
            len(h.falsifiable_by) >= 1
            and not any("[No falsification" in f for f in h.falsifiable_by)
            for h in parsed.hypotheses
        )
        if has_good_falsification:
            confidence += 0.15

        # Reasoning chain
        if len(parsed.reasoning_chain) >= 2:
            confidence += 0.1

        # Suggested tests
        if len(parsed.suggested_tests) >= 1:
            confidence += 0.05

        return min(1.0, max(0.0, confidence))


# Convenience factory function


def hypothesis_parser(
    config: Optional[PParserConfig] = None,
) -> Parser[ParsedHypothesisResponse]:
    """
    Create B-gent hypothesis parser conforming to P-gents protocol.

    This is the standard parser for B-gent hypothesis generation.

    Usage:
        >>> from agents.b.p_integration import hypothesis_parser
        >>> parser = hypothesis_parser()
        >>> result = parser.parse(llm_response)
        >>> if result.success:
        ...     print(f"Parsed {len(result.value.hypotheses)} hypotheses")
        ...     for h in result.value.hypotheses:
        ...         print(f"  - {h.statement} ({h.confidence:.0%})")
    """
    return BgentHypothesisParser(config=config)
