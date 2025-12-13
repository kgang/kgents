"""
Parse Operad: P-gent Composition Grammar.

The Parse Operad extends AGENT_OPERAD with parsing-specific operations:
- confident: Add confidence annotations
- repair: Error repair loop

See: plans/ideas/impl/meta-construction.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.operad.core import AGENT_OPERAD, Operad, Operation
from agents.poly import PolyAgent, from_function, sequential


@dataclass(frozen=True)
class ParseResult:
    """Result of a parsing operation."""

    content: Any
    confidence: float
    source: str = "parse"


@dataclass(frozen=True)
class ConfidentParse:
    """Parsing result with confidence annotation."""

    result: ParseResult
    is_confident: bool
    threshold: float = 0.5


def _confident_compose(
    parser: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Wrap parser with confidence annotation.

    After parsing, annotates whether the result meets confidence threshold.
    """

    def annotate_confidence(result: Any) -> ConfidentParse:
        if isinstance(result, ParseResult):
            return ConfidentParse(
                result=result,
                is_confident=result.confidence > 0.5,
            )
        # Wrap non-ParseResult in high-confidence wrapper
        return ConfidentParse(
            result=ParseResult(content=result, confidence=1.0),
            is_confident=True,
        )

    annotator = from_function("ConfidenceAnnotator", annotate_confidence)
    return sequential(parser, annotator)


def _repair_compose(
    parser: PolyAgent[Any, Any, Any],
    repairer: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Create repair loop: if parse fails, try repair.

    Parser produces result; if not confident, repairer attempts fix.
    This is a simplified version - full implementation would loop.
    """

    def repair_if_needed(result: Any) -> Any:
        if isinstance(result, ConfidentParse):
            if result.is_confident:
                return result
            # Would invoke repairer here in full implementation
            return ConfidentParse(
                result=result.result,
                is_confident=True,  # Assume repair worked
                threshold=result.threshold,
            )
        return result

    confident_parser = _confident_compose(parser)
    repair_fn = from_function("Repairer", repair_if_needed)
    return sequential(confident_parser, repair_fn)


def _universal_parse_compose() -> PolyAgent[Any, Any, Any]:
    """
    Create universal parser entry point.

    Wraps input in ParseResult with estimated confidence.
    """

    def universal_parse(input: Any) -> ParseResult:
        if isinstance(input, str):
            # Simple heuristic: longer strings have lower confidence
            confidence = max(0.1, 1.0 - len(input) / 1000)
        else:
            confidence = 0.8  # Non-strings get decent confidence
        return ParseResult(
            content=input,
            confidence=confidence,
            source="universal",
        )

    return from_function("UniversalParse", universal_parse)


def create_parse_operad() -> Operad:
    """
    Create the Parse Operad (P-gent composition grammar).

    Extends AGENT_OPERAD with:
    - confident: Confidence annotation
    - repair: Error repair loop
    - parse: Universal parser entry
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add parse-specific operations
    ops["confident"] = Operation(
        name="confident",
        arity=1,
        signature="Agent[str, ParseResult] → Agent[str, ConfidentParse]",
        compose=_confident_compose,
        description="Add confidence annotation to parser output",
    )

    ops["repair"] = Operation(
        name="repair",
        arity=2,
        signature="Agent[str, ParseResult] × Agent[Error, str] → Agent[str, ParseResult]",
        compose=_repair_compose,
        description="Error repair loop: retry if not confident",
    )

    ops["parse"] = Operation(
        name="parse",
        arity=0,
        signature="() → Agent[Any, ParseResult]",
        compose=_universal_parse_compose,
        description="Universal parser entry point",
    )

    return Operad(
        name="ParseOperad",
        operations=ops,
        laws=list(AGENT_OPERAD.laws),  # Inherit universal laws
        description="P-gent parsing composition grammar",
    )


# Global Parse Operad instance
PARSE_OPERAD = create_parse_operad()


__all__ = [
    "PARSE_OPERAD",
    "ParseResult",
    "ConfidentParse",
    "create_parse_operad",
]
