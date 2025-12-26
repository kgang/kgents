"""
Analysis Service: LLM-backed four-mode spec analysis.

> *"Analysis that can analyze itself is the only analysis worth having."*

The Analysis Service provides LLM-backed implementations of the four
analysis modes from the Analysis Operad:

1. Categorical: Extract laws, verify composition, find fixed points
2. Epistemic: Determine layer, build Toulmin structure, trace grounding
3. Dialectical: Find tensions, classify contradictions, synthesize
4. Generative: Extract grammar, measure compression, test regeneration

Architecture:
    - service.py: Main AnalysisService orchestrator
    - prompts.py: LLM prompt templates per mode
    - llm_agents.py: LLM agent wrappers
    - parsers.py: Parse LLM responses into report types
    - ashc_bridge.py: ASHC integration for Bayesian confidence

Integration Points:
    - Uses agents.operad.domains.analysis report types
    - Can integrate with ASHC for confidence tracking (optional)
    - Emits Witness marks for analysis operations (optional)

Usage:
    >>> from services.analysis import AnalysisService
    >>> from agents.k.soul import create_llm_client
    >>>
    >>> llm = create_llm_client()
    >>> service = AnalysisService(llm)
    >>>
    >>> # Full four-mode analysis
    >>> report = await service.analyze_full("spec/theory/zero-seed.md")
    >>> print(report.synthesis)
    >>>
    >>> # Single mode
    >>> cat_report = await service.analyze_categorical("spec/protocols/witness.md")
    >>> print(f"Laws verified: {cat_report.laws_passed}/{cat_report.laws_total}")
    >>>
    >>> # With ASHC evidence
    >>> from services.analysis.ashc_bridge import analyze_with_evidence
    >>> evidenced = await analyze_with_evidence("spec/theory/zero-seed.md", report)
    >>> print(f"Confidence: {evidenced.confidence:.2%}")

Teaching:
    gotcha: The service reads specs from disk. Paths must be absolute or relative
            to working directory. Non-existent paths raise FileNotFoundError.
            (Evidence: test_service.py::test_analyze_missing_file)

    gotcha: LLM responses are parsed into structured reports. If parsing fails,
            the service returns a report with error information rather than raising.
            Check report.summary for parse errors.
            (Evidence: test_service.py::test_analyze_parse_error)

    gotcha: Full analysis runs categorical+epistemic first, then dialectical+generative
            informed by first phase results. This is NOT simple parallel execution.
            (Evidence: spec/theory/analysis-operad.md §2.2 completeness law)

See: spec/theory/analysis-operad.md
"""

from __future__ import annotations

from .ashc_bridge import (
    AnalysisASHCBridge,
    EvidencedAnalysis,
    ModeEvidence,
    analyze_with_evidence,
)
from .service import AnalysisService

__all__ = [
    "AnalysisService",
    "AnalysisASHCBridge",
    "EvidencedAnalysis",
    "ModeEvidence",
    "analyze_with_evidence",
]
