"""
Response Parsers: Convert LLM JSON responses into typed report objects.

The parsers handle:
1. Extracting JSON from markdown-wrapped responses
2. Validating structure
3. Converting to typed dataclasses from agents.operad.domains.analysis
4. Graceful error handling (return error reports instead of raising)

Teaching:
    gotcha: LLMs often wrap JSON in ```json...``` fences. extract_json_from_response
            strips these automatically. Don't assume raw JSON.
            (Evidence: test_parsers.py::test_extract_json_wrapped)

    gotcha: Parsers return error reports on parse failure, NOT exceptions.
            Always check report.summary for parse errors.
            (Evidence: test_parsers.py::test_parse_invalid_json_returns_error_report)

    gotcha: Missing fields use sensible defaults. An incomplete LLM response
            won't crash parsing—it'll produce a degraded report.
            (Evidence: test_parsers.py::test_parse_categorical_missing_fields)
"""

from __future__ import annotations

import json
import re
from typing import Any

from agents.operad.core import LawStatus
from agents.operad.domains.analysis import (
    BootstrapAnalysis,
    CategoricalReport,
    ContradictionType,
    DialecticalReport,
    EpistemicReport,
    EvidenceTier,
    FixedPointAnalysis,
    GenerativeReport,
    GroundingChain,
    LawExtraction,
    OperadGrammar,
    RegenerationTest,
    Tension,
    ToulminStructure,
)
from agents.operad.core import LawVerification

# =============================================================================
# JSON Extraction
# =============================================================================


def extract_json_from_response(response: str) -> str:
    """
    Extract JSON from LLM response (handles markdown wrapping).

    LLMs often wrap JSON in:
    - ```json ... ```
    - ``` ... ```
    - Just raw JSON

    This function strips the wrapping and returns clean JSON string.
    """
    # Strip leading/trailing whitespace
    response = response.strip()

    # Check for markdown code fence
    if response.startswith("```"):
        # Remove opening fence (```json or just ```)
        lines = response.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        # Remove closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        response = "\n".join(lines)

    return response.strip()


# =============================================================================
# Categorical Parsing
# =============================================================================


def parse_categorical_response(response: str, target: str) -> CategoricalReport:
    """
    Parse LLM response into CategoricalReport.

    Args:
        response: Raw LLM response (may be JSON-wrapped)
        target: Spec path being analyzed

    Returns:
        CategoricalReport with parsed data or error information
    """
    try:
        json_str = extract_json_from_response(response)
        data = json.loads(json_str)

        # Parse laws_extracted
        laws_extracted = tuple(
            LawExtraction(
                name=law.get("name", "unknown"),
                equation=law.get("equation", ""),
                source=law.get("source", ""),
                tier=EvidenceTier.CATEGORICAL,
            )
            for law in data.get("laws_extracted", [])
        )

        # Parse law_verifications
        law_verifications = tuple(
            LawVerification(
                law_name=v.get("law_name", "unknown"),
                status=LawStatus[v.get("status", "SKIPPED").upper()],
                message=v.get("message", ""),
            )
            for v in data.get("law_verifications", [])
        )

        # Parse fixed_point (optional)
        fp_data = data.get("fixed_point")
        fixed_point = None
        if fp_data:
            fixed_point = FixedPointAnalysis(
                is_self_referential=fp_data.get("is_self_referential", False),
                fixed_point_description=fp_data.get("description", ""),
                is_valid=fp_data.get("is_valid", True),
                implications=tuple(fp_data.get("implications", [])),
            )

        summary = data.get("summary", "Categorical analysis completed")

        return CategoricalReport(
            target=target,
            laws_extracted=laws_extracted,
            law_verifications=law_verifications,
            fixed_point=fixed_point,
            summary=summary,
        )

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # Return error report instead of raising
        return CategoricalReport(
            target=target,
            laws_extracted=(),
            law_verifications=(),
            fixed_point=None,
            summary=f"Parse error: {e}",
        )


# =============================================================================
# Epistemic Parsing
# =============================================================================


def parse_epistemic_response(response: str, target: str) -> EpistemicReport:
    """
    Parse LLM response into EpistemicReport.

    Args:
        response: Raw LLM response (may be JSON-wrapped)
        target: Spec path being analyzed

    Returns:
        EpistemicReport with parsed data or error information
    """
    try:
        json_str = extract_json_from_response(response)
        data = json.loads(json_str)

        # Parse toulmin structure
        toulmin_data = data.get("toulmin", {})
        toulmin = ToulminStructure(
            claim=toulmin_data.get("claim", ""),
            grounds=tuple(toulmin_data.get("grounds", [])),
            warrant=toulmin_data.get("warrant", ""),
            backing=toulmin_data.get("backing", ""),
            qualifier=toulmin_data.get("qualifier", "possibly"),
            rebuttals=tuple(toulmin_data.get("rebuttals", [])),
            tier=EvidenceTier[toulmin_data.get("tier", "EMPIRICAL").upper()],
        )

        # Parse grounding chain
        chain_data = data.get("grounding_chain", [])
        grounding = GroundingChain(
            steps=tuple(tuple(step) for step in chain_data),  # type: ignore
            terminates_at_axiom=data.get("terminates_at_axiom", False),
        )

        # Parse bootstrap (optional)
        bootstrap_data = data.get("bootstrap")
        bootstrap = None
        if bootstrap_data:
            bootstrap = BootstrapAnalysis(
                is_self_describing=bootstrap_data.get("is_self_describing", False),
                layer_described=bootstrap_data.get("layer_described", 4),
                layer_occupied=bootstrap_data.get("layer_occupied", 4),
                is_valid=bootstrap_data.get("is_valid", True),
                explanation=bootstrap_data.get("explanation", ""),
            )

        summary = data.get("summary", "Epistemic analysis completed")

        return EpistemicReport(
            target=target,
            layer=data.get("layer", 4),
            toulmin=toulmin,
            grounding=grounding,
            bootstrap=bootstrap,
            summary=summary,
        )

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # Return error report
        return EpistemicReport(
            target=target,
            layer=4,
            toulmin=ToulminStructure(
                claim="",
                grounds=(),
                warrant="",
                backing="",
                qualifier="possibly",
                rebuttals=(),
                tier=EvidenceTier.EMPIRICAL,
            ),
            grounding=GroundingChain(steps=(), terminates_at_axiom=False),
            bootstrap=None,
            summary=f"Parse error: {e}",
        )


# =============================================================================
# Dialectical Parsing
# =============================================================================


def parse_dialectical_response(response: str, target: str) -> DialecticalReport:
    """
    Parse LLM response into DialecticalReport.

    Args:
        response: Raw LLM response (may be JSON-wrapped)
        target: Spec path being analyzed

    Returns:
        DialecticalReport with parsed data or error information
    """
    try:
        json_str = extract_json_from_response(response)
        data = json.loads(json_str)

        # Parse tensions
        tensions = tuple(
            Tension(
                thesis=t.get("thesis", ""),
                antithesis=t.get("antithesis", ""),
                classification=ContradictionType[
                    t.get("classification", "PRODUCTIVE").upper()
                ],
                synthesis=t.get("synthesis"),
                is_resolved=t.get("is_resolved", False),
            )
            for t in data.get("tensions", [])
        )

        summary = data.get("summary", "Dialectical analysis completed")

        return DialecticalReport(
            target=target,
            tensions=tensions,
            summary=summary,
        )

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # Return error report
        return DialecticalReport(
            target=target,
            tensions=(),
            summary=f"Parse error: {e}",
        )


# =============================================================================
# Generative Parsing
# =============================================================================


def parse_generative_response(response: str, target: str) -> GenerativeReport:
    """
    Parse LLM response into GenerativeReport.

    Args:
        response: Raw LLM response (may be JSON-wrapped)
        target: Spec path being analyzed

    Returns:
        GenerativeReport with parsed data or error information
    """
    try:
        json_str = extract_json_from_response(response)
        data = json.loads(json_str)

        # Parse grammar
        grammar_data = data.get("grammar", {})
        grammar = OperadGrammar(
            primitives=frozenset(grammar_data.get("primitives", [])),
            operations=frozenset(grammar_data.get("operations", [])),
            laws=frozenset(grammar_data.get("laws", [])),
        )

        # Parse regeneration test
        regen_data = data.get("regeneration_test", {})
        regeneration = RegenerationTest(
            axioms_used=tuple(regen_data.get("axioms_used", [])),
            structures_regenerated=tuple(regen_data.get("structures_regenerated", [])),
            missing_elements=tuple(regen_data.get("missing_elements", [])),
            passed=regen_data.get("passed", False),
        )

        summary = data.get("summary", "Generative analysis completed")

        return GenerativeReport(
            target=target,
            grammar=grammar,
            compression_ratio=data.get("compression_ratio", 1.0),
            regeneration=regeneration,
            minimal_kernel=tuple(data.get("minimal_kernel", [])),
            summary=summary,
        )

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # Return error report
        return GenerativeReport(
            target=target,
            grammar=OperadGrammar(
                primitives=frozenset(),
                operations=frozenset(),
                laws=frozenset(),
            ),
            compression_ratio=1.0,
            regeneration=RegenerationTest(
                axioms_used=(),
                structures_regenerated=(),
                missing_elements=(),
                passed=False,
            ),
            minimal_kernel=(),
            summary=f"Parse error: {e}",
        )


# =============================================================================
# Constitutional Parsing
# =============================================================================


def parse_constitutional_response(response: str, target: str) -> "ConstitutionalReport":
    """
    Parse LLM response into ConstitutionalReport.

    Args:
        response: Raw LLM response (may be JSON-wrapped)
        target: Spec path being analyzed

    Returns:
        ConstitutionalReport with parsed data or error information
    """
    try:
        json_str = extract_json_from_response(response)
        data = json.loads(json_str)

        # Import ConstitutionalAlignment from witness
        from services.witness.mark import ConstitutionalAlignment
        from agents.operad.domains.analysis import ConstitutionalReport

        # Build ConstitutionalAlignment
        principle_scores = data.get("principle_scores", {})
        weighted_total = data.get("weighted_total", 0.5)
        threshold = data.get("threshold", 0.5)

        alignment = ConstitutionalAlignment(
            principle_scores=principle_scores,
            weighted_total=weighted_total,
            galois_loss=None,  # Not computed in this analysis
            tier="EMPIRICAL",  # LLM-based evaluation
            threshold=threshold,
        )

        # Parse violations and suggestions
        violations = tuple(data.get("violations", []))
        remediation_suggestions = tuple(data.get("remediation_suggestions", []))
        summary = data.get("summary", "Constitutional analysis completed")

        return ConstitutionalReport(
            target=target,
            alignment=alignment,
            violations=violations,
            remediation_suggestions=remediation_suggestions,
            summary=summary,
        )

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # Return error report
        from services.witness.mark import ConstitutionalAlignment
        from agents.operad.domains.analysis import ConstitutionalReport

        return ConstitutionalReport(
            target=target,
            alignment=ConstitutionalAlignment.neutral(),
            violations=("All principles",),
            remediation_suggestions=(f"Parse error: {e}",),
            summary=f"Parse error: {e}",
        )


__all__ = [
    "extract_json_from_response",
    "parse_categorical_response",
    "parse_epistemic_response",
    "parse_dialectical_response",
    "parse_generative_response",
    "parse_constitutional_response",
]
