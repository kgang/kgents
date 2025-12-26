"""
Analysis AGENTESE Node: @node("concept.analysis")

Wraps AnalysisService as an AGENTESE node for universal gateway access.

AGENTESE Paths:
- concept.analysis.manifest       - Analysis service health and statistics
- concept.analysis.categorical    - Verify composition laws and fixed points
- concept.analysis.epistemic      - Analyze justification and grounding
- concept.analysis.dialectical    - Identify tensions and synthesize
- concept.analysis.generative     - Test compression and regeneration
- concept.analysis.full           - Complete four-mode analysis
- concept.analysis.self           - Meta-applicability: analyze the operad itself

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

Philosophy:
    "Analysis is not one thing but four."
    "Analysis that can analyze itself is the only analysis worth having."

See: spec/theory/analysis-operad.md
See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from protocols.agentese.affordances import AspectCategory, aspect
from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

if TYPE_CHECKING:
    from agents.operad.domains.analysis import (
        CategoricalReport,
        DialecticalReport,
        EpistemicReport,
        FullAnalysisReport,
        GenerativeReport,
    )
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Rendering Types
# =============================================================================


@dataclass(frozen=True)
class AnalysisManifestRendering:
    """Rendering for analysis service status."""

    service_status: str
    modes_available: tuple[str, ...]
    recent_analyses: int
    llm_available: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "analysis_manifest",
            "service_status": self.service_status,
            "modes_available": list(self.modes_available),
            "recent_analyses": self.recent_analyses,
            "llm_available": self.llm_available,
        }

    def to_text(self) -> str:
        lines = [
            "Analysis Operad Status",
            "=" * 40,
            f"Service: {self.service_status}",
            f"LLM Backend: {'Available' if self.llm_available else 'Unavailable (structural mode)'}",
            f"Recent Analyses: {self.recent_analyses}",
            "",
            "Available Modes:",
        ]
        for mode in self.modes_available:
            lines.append(f"  • {mode}")
        return "\n".join(lines)


@dataclass(frozen=True)
class AnalysisReportRendering:
    """Rendering for any analysis report."""

    mode: str
    target: str
    passed: bool
    summary: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": f"analysis_{self.mode}",
            "target": self.target,
            "passed": self.passed,
            "summary": self.summary,
            **self.details,
        }

    def to_text(self) -> str:
        status = "✓ PASS" if self.passed else "✗ FAIL"
        lines = [
            f"{self.mode.upper()} ANALYSIS: {status}",
            "=" * 40,
            f"Target: {self.target}",
            "",
            self.summary,
        ]
        return "\n".join(lines)


# =============================================================================
# Request/Response Contracts
# =============================================================================


@dataclass(frozen=True)
class AnalyzeRequest:
    """Request for analysis operation."""
    target: str
    use_llm: bool = True


@dataclass(frozen=True)
class AnalyzeResponse:
    """Response from analysis operation."""
    mode: str
    target: str
    passed: bool
    summary: str


@dataclass(frozen=True)
class FullAnalyzeResponse:
    """Response from full four-mode analysis."""
    target: str
    is_valid: bool
    categorical_passed: bool
    epistemic_passed: bool
    dialectical_passed: bool
    generative_passed: bool
    synthesis: str


# =============================================================================
# Analysis Node
# =============================================================================


@node(
    "concept.analysis",
    description="Four-mode spec analysis: categorical, epistemic, dialectical, generative",
    contracts={
        "manifest": Response(AnalysisManifestRendering),
        "categorical": Contract(AnalyzeRequest, AnalyzeResponse),
        "epistemic": Contract(AnalyzeRequest, AnalyzeResponse),
        "dialectical": Contract(AnalyzeRequest, AnalyzeResponse),
        "generative": Contract(AnalyzeRequest, AnalyzeResponse),
        "full": Contract(AnalyzeRequest, FullAnalyzeResponse),
    },
    examples=[
        ("manifest", {}, "Show analysis service status"),
        ("categorical", {"target": "spec/protocols/witness.md"}, "Verify laws"),
        ("full", {"target": "spec/theory/zero-seed.md"}, "Full 4-mode analysis"),
        ("self", {}, "Meta-applicability: analyze the Analysis Operad"),
    ],
)
class AnalysisNode(BaseLogosNode):
    """
    AGENTESE node for the Analysis Operad.

    Exposes four-mode spec analysis via the AGENTESE protocol.
    No explicit routes needed—the protocol IS the API.

    Modes:
    - categorical: Verify composition laws, detect fixed points
    - epistemic: Analyze justification structure, trace grounding
    - dialectical: Identify tensions, attempt synthesis
    - generative: Test compression and regeneration from axioms
    - full: Run all four modes with completeness law ordering
    - self: Meta-applicability test (analyze the Analysis Operad itself)
    """

    def __init__(self) -> None:
        """Initialize without dependencies (analysis functions are imported on demand)."""
        self._analysis_count = 0

    @property
    def handle(self) -> str:
        return "concept.analysis"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        if archetype in ("developer", "admin", "cli", "system"):
            return (
                "manifest",
                "categorical",
                "epistemic",
                "dialectical",
                "generative",
                "full",
                "self",
            )
        if archetype in ("architect", "researcher"):
            return ("manifest", "categorical", "epistemic", "dialectical", "full")
        if archetype in ("operator",):
            return ("manifest", "full")
        return ("manifest",)  # Minimal for guests

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Show analysis service status and statistics",
    )
    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Return analysis service status."""
        # Check LLM availability
        try:
            from agents.k.llm import has_llm_credentials
            llm_available = has_llm_credentials()
        except ImportError:
            llm_available = False

        return AnalysisManifestRendering(
            service_status="operational",
            modes_available=(
                "categorical",
                "epistemic",
                "dialectical",
                "generative",
                "full",
                "self",
            ),
            recent_analyses=self._analysis_count,
            llm_available=llm_available,
        )

    async def _invoke_aspect(
        self,
        aspect_name: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route custom aspects to handlers."""
        if aspect_name == "categorical":
            return await self._analyze_categorical(kwargs.get("target", ""), kwargs.get("use_llm", True))
        if aspect_name == "epistemic":
            return await self._analyze_epistemic(kwargs.get("target", ""), kwargs.get("use_llm", True))
        if aspect_name == "dialectical":
            return await self._analyze_dialectical(kwargs.get("target", ""), kwargs.get("use_llm", True))
        if aspect_name == "generative":
            return await self._analyze_generative(kwargs.get("target", ""), kwargs.get("use_llm", True))
        if aspect_name == "full":
            return await self._analyze_full(kwargs.get("target", ""), kwargs.get("use_llm", True))
        if aspect_name == "self":
            return await self._analyze_self(kwargs.get("use_llm", True))

        raise NotImplementedError(f"Aspect {aspect_name} not implemented")

    async def _analyze_categorical(self, target: str, use_llm: bool) -> AnalysisReportRendering:
        """Run categorical analysis."""
        self._analysis_count += 1

        if use_llm:
            from agents.operad.domains.analysis import analyze_categorical_llm
            report = await analyze_categorical_llm(target)
        else:
            from agents.operad.domains.analysis import _categorical_analysis
            report = _categorical_analysis(target)

        return AnalysisReportRendering(
            mode="categorical",
            target=target,
            passed=not report.has_violations,
            summary=report.summary,
            details={
                "laws_passed": report.laws_passed,
                "laws_total": report.laws_total,
                "has_fixed_point": report.fixed_point is not None,
            },
        )

    async def _analyze_epistemic(self, target: str, use_llm: bool) -> AnalysisReportRendering:
        """Run epistemic analysis."""
        self._analysis_count += 1

        if use_llm:
            from agents.operad.domains.analysis import analyze_epistemic_llm
            report = await analyze_epistemic_llm(target)
        else:
            from agents.operad.domains.analysis import _epistemic_analysis
            report = _epistemic_analysis(target)

        return AnalysisReportRendering(
            mode="epistemic",
            target=target,
            passed=report.is_grounded,
            summary=report.summary,
            details={
                "layer": report.layer,
                "is_grounded": report.is_grounded,
                "has_bootstrap": report.bootstrap is not None,
            },
        )

    async def _analyze_dialectical(self, target: str, use_llm: bool) -> AnalysisReportRendering:
        """Run dialectical analysis."""
        self._analysis_count += 1

        if use_llm:
            from agents.operad.domains.analysis import analyze_dialectical_llm
            report = await analyze_dialectical_llm(target)
        else:
            from agents.operad.domains.analysis import _dialectical_analysis
            report = _dialectical_analysis(target)

        return AnalysisReportRendering(
            mode="dialectical",
            target=target,
            passed=report.problematic_count == 0,
            summary=report.summary,
            details={
                "tensions_total": len(report.tensions),
                "tensions_resolved": report.resolved_count,
                "problematic_count": report.problematic_count,
            },
        )

    async def _analyze_generative(self, target: str, use_llm: bool) -> AnalysisReportRendering:
        """Run generative analysis."""
        self._analysis_count += 1

        if use_llm:
            from agents.operad.domains.analysis import analyze_generative_llm
            report = await analyze_generative_llm(target)
        else:
            from agents.operad.domains.analysis import _generative_analysis
            report = _generative_analysis(target)

        return AnalysisReportRendering(
            mode="generative",
            target=target,
            passed=report.is_regenerable,
            summary=report.summary,
            details={
                "compression_ratio": report.compression_ratio,
                "is_compressed": report.is_compressed,
                "is_regenerable": report.is_regenerable,
            },
        )

    async def _analyze_full(self, target: str, use_llm: bool) -> AnalysisReportRendering:
        """Run full four-mode analysis."""
        self._analysis_count += 1

        if use_llm:
            from agents.operad.domains.analysis import analyze_full_llm
            report = await analyze_full_llm(target)
        else:
            from agents.operad.domains.analysis import _full_analysis
            report = _full_analysis(target)

        return AnalysisReportRendering(
            mode="full",
            target=target,
            passed=report.is_valid,
            summary=report.synthesis,
            details={
                "categorical_passed": not report.categorical.has_violations,
                "epistemic_passed": report.epistemic.is_grounded,
                "dialectical_passed": report.dialectical.problematic_count == 0,
                "generative_passed": report.generative.is_regenerable,
            },
        )

    async def _analyze_self(self, use_llm: bool) -> AnalysisReportRendering:
        """Meta-applicability: analyze the Analysis Operad itself."""
        self._analysis_count += 1

        if use_llm:
            from agents.operad.domains.analysis import self_analyze_llm
            report = await self_analyze_llm()
        else:
            from agents.operad.domains.analysis import self_analyze
            report = self_analyze()

        return AnalysisReportRendering(
            mode="meta",
            target="spec/theory/analysis-operad.md",
            passed=report.is_valid,
            summary=f"Meta-Applicability: {'✓ PASSED' if report.is_valid else '⚠️ ISSUES'}\n\n{report.synthesis}",
            details={
                "is_valid": report.is_valid,
                "categorical_passed": not report.categorical.has_violations,
                "epistemic_passed": report.epistemic.is_grounded,
                "dialectical_passed": report.dialectical.problematic_count == 0,
                "generative_passed": report.generative.is_regenerable,
            },
        )


__all__ = [
    "AnalysisNode",
    "AnalysisManifestRendering",
    "AnalysisReportRendering",
    "AnalyzeRequest",
    "AnalyzeResponse",
    "FullAnalyzeResponse",
]
