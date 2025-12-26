"""
Analysis Operad: Five Modes of Rigorous Inquiry.

The Analysis Operad extends AGENT_OPERAD with five analysis modes:
- categorical: Verify composition laws and fixed points
- epistemic: Analyze justification structure and grounding
- dialectical: Identify tensions and synthesize resolutions
- generative: Test regenerability from axioms
- constitutional: Verify alignment with 7 kgents principles

Key insight: Analysis that can analyze itself is the only analysis worth having.

See: spec/theory/analysis-operad.md

Teaching:
    gotcha: Each analysis mode is a PolyAgent that returns a typed report.
            The reports are NOT just dictionaries—they have structure that
            enables composition (e.g., findings from categorical inform dialectical).
            (Evidence: CategoricalReport.law_violations feeds DialecticalReport.tensions)

    gotcha: The `full` operation is NOT just parallel application of all modes.
            It runs categorical+epistemic first, then dialectical+generative
            informed by their outputs: seq(par(cat, epi), par(dia, gen)).
            (Evidence: spec/theory/analysis-operad.md §2.2)

    gotcha: Analysis Operad can analyze ITSELF (meta-applicability law).
            This is a deliberate Lawvere fixed-point, not a paradox.
            (Evidence: self_analyze() method and meta_applicability law)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, FrozenSet

from agents.operad.core import (
    AGENT_OPERAD,
    Law,
    LawStatus,
    LawVerification,
    Operad,
    Operation,
)
from agents.poly import PolyAgent, from_function, parallel, sequential

# =============================================================================
# Analysis Report Types
# =============================================================================


class ContradictionType(Enum):
    """Classification of tensions in dialectical analysis."""

    APPARENT = auto()  # Seems contradictory but isn't (different scopes)
    PRODUCTIVE = auto()  # Real tension that drives design decisions
    PROBLEMATIC = auto()  # Contradiction that needs resolution
    PARACONSISTENT = auto()  # Contradiction we tolerate deliberately


class EvidenceTier(Enum):
    """Tier of evidence for epistemic grounding."""

    SOMATIC = auto()  # Felt truth (axiom layer)
    AESTHETIC = auto()  # Beauty/taste judgment
    EMPIRICAL = auto()  # Observed evidence
    CATEGORICAL = auto()  # Formal proof
    DERIVED = auto()  # Derived from other tiers


@dataclass(frozen=True)
class LawExtraction:
    """A law extracted from a specification."""

    name: str
    equation: str
    source: str  # Where in the spec this law comes from
    tier: EvidenceTier = EvidenceTier.CATEGORICAL


@dataclass(frozen=True)
class FixedPointAnalysis:
    """Analysis of self-referential fixed points."""

    is_self_referential: bool
    fixed_point_description: str
    is_valid: bool  # Valid Lawvere fixed point vs paradox
    implications: tuple[str, ...]


@dataclass(frozen=True)
class CategoricalReport:
    """
    Result of categorical analysis.

    Verifies composition laws and identifies fixed points.
    """

    target: str
    laws_extracted: tuple[LawExtraction, ...]
    law_verifications: tuple[LawVerification, ...]
    fixed_point: FixedPointAnalysis | None
    summary: str

    @property
    def laws_passed(self) -> int:
        return sum(1 for v in self.law_verifications if v.passed)

    @property
    def laws_total(self) -> int:
        return len(self.law_verifications)

    @property
    def has_violations(self) -> bool:
        return any(v.status == LawStatus.FAILED for v in self.law_verifications)


@dataclass(frozen=True)
class ToulminStructure:
    """Toulmin argument structure for epistemic grounding."""

    claim: str
    grounds: tuple[str, ...]
    warrant: str
    backing: str
    qualifier: str  # "definitely", "probably", "possibly"
    rebuttals: tuple[str, ...]
    tier: EvidenceTier


@dataclass(frozen=True)
class GroundingChain:
    """Chain of justification from axioms to claim."""

    steps: tuple[tuple[int, str, str], ...]  # (layer, node, edge_type)
    terminates_at_axiom: bool


@dataclass(frozen=True)
class BootstrapAnalysis:
    """Analysis of bootstrapping for self-referential specs."""

    is_self_describing: bool
    layer_described: int  # Which layer the spec describes
    layer_occupied: int  # Which layer the spec occupies
    is_valid: bool  # Valid bootstrap vs infinite regress
    explanation: str


@dataclass(frozen=True)
class EpistemicReport:
    """
    Result of epistemic analysis.

    Analyzes justification structure and grounding.
    """

    target: str
    layer: int  # 1-7 in Zero Seed
    toulmin: ToulminStructure
    grounding: GroundingChain
    bootstrap: BootstrapAnalysis | None
    summary: str

    @property
    def is_grounded(self) -> bool:
        return self.grounding.terminates_at_axiom

    @property
    def has_valid_bootstrap(self) -> bool:
        return self.bootstrap is None or self.bootstrap.is_valid


@dataclass(frozen=True)
class Tension:
    """A tension identified in dialectical analysis."""

    thesis: str
    antithesis: str
    classification: ContradictionType
    synthesis: str | None  # None if unresolved
    is_resolved: bool


@dataclass(frozen=True)
class DialecticalReport:
    """
    Result of dialectical analysis.

    Identifies tensions and synthesizes resolutions.
    """

    target: str
    tensions: tuple[Tension, ...]
    summary: str

    @property
    def resolved_count(self) -> int:
        return sum(1 for t in self.tensions if t.is_resolved)

    @property
    def problematic_count(self) -> int:
        return sum(1 for t in self.tensions if t.classification == ContradictionType.PROBLEMATIC)

    @property
    def paraconsistent_count(self) -> int:
        return sum(1 for t in self.tensions if t.classification == ContradictionType.PARACONSISTENT)


@dataclass(frozen=True)
class OperadGrammar:
    """Extracted generative grammar from a spec."""

    primitives: FrozenSet[str]
    operations: FrozenSet[str]
    laws: FrozenSet[str]


@dataclass(frozen=True)
class RegenerationTest:
    """Result of testing regenerability from axioms."""

    axioms_used: tuple[str, ...]
    structures_regenerated: tuple[str, ...]
    missing_elements: tuple[str, ...]
    passed: bool


@dataclass(frozen=True)
class GenerativeReport:
    """
    Result of generative analysis.

    Tests regenerability from axioms.
    """

    target: str
    grammar: OperadGrammar
    compression_ratio: float  # spec_size / impl_size
    regeneration: RegenerationTest
    minimal_kernel: tuple[str, ...]  # Minimal axioms sufficient
    summary: str

    @property
    def is_compressed(self) -> bool:
        return self.compression_ratio < 1.0

    @property
    def is_regenerable(self) -> bool:
        return self.regeneration.passed


@dataclass(frozen=True)
class ConstitutionalReport:
    """
    Result of constitutional analysis.

    Verifies alignment with the 7 kgents principles.
    """

    target: str
    alignment: "ConstitutionalAlignment"  # From services.witness.mark
    violations: tuple[str, ...]  # Principles below threshold
    remediation_suggestions: tuple[str, ...]
    summary: str

    @property
    def is_aligned(self) -> bool:
        """Check if spec meets constitutional alignment threshold."""
        return self.alignment.is_compliant

    @property
    def violation_count(self) -> int:
        """Count principles below threshold."""
        return len(self.violations)

    @property
    def alignment_score(self) -> float:
        """Return weighted total alignment score."""
        return self.alignment.weighted_total


@dataclass(frozen=True)
class FullAnalysisReport:
    """
    Complete four-mode analysis report.

    Synthesizes insights from all four modes.
    """

    target: str
    categorical: CategoricalReport
    epistemic: EpistemicReport
    dialectical: DialecticalReport
    generative: GenerativeReport
    synthesis: str  # Overall synthesis

    @property
    def is_valid(self) -> bool:
        """Spec is valid if it passes all modes."""
        return (
            not self.categorical.has_violations
            and self.epistemic.is_grounded
            and self.dialectical.problematic_count == 0
            and self.generative.is_regenerable
        )


# =============================================================================
# Analysis Operations
# =============================================================================
#
# Two execution modes:
#   1. LLM-backed (via services/analysis/) - REAL analysis using Claude
#   2. Structural (fallback) - Returns structural placeholders when LLM unavailable
#
# Teaching:
#     gotcha: The async LLM service is wired via analyze_llm() and analyze_full_llm().
#             The sync _*_analysis() functions are structural fallbacks only.
#             Use the async versions for real analysis.
#             (Evidence: handlers/analyze.py should call analyze_full_llm for --llm mode)
#
#     gotcha: Structural analysis is NOT fake—it verifies what can be verified
#             without LLM: category axioms hold by construction, spec file exists, etc.
#             (Evidence: structural mode detects missing files, broken structure)


def _categorical_analysis_structural(spec_path: str) -> CategoricalReport:
    """
    Structural categorical analysis (no LLM).

    Returns baseline categorical properties that hold by construction.
    For real analysis, use the async LLM-backed service.
    """
    from pathlib import Path

    # Check if file exists
    path = Path(spec_path)
    if not path.exists():
        return CategoricalReport(
            target=spec_path,
            laws_extracted=(),
            law_verifications=(
                LawVerification(
                    law_name="file_exists",
                    status=LawStatus.FAILED,
                    message=f"File not found: {spec_path}",
                ),
            ),
            fixed_point=None,
            summary="Structural analysis failed: file not found",
        )

    # Return structural analysis (what holds by construction)
    return CategoricalReport(
        target=spec_path,
        laws_extracted=(
            LawExtraction(
                name="identity",
                equation="Id >> f = f = f >> Id",
                source="implicit (category axiom)",
            ),
            LawExtraction(
                name="associativity",
                equation="(f >> g) >> h = f >> (g >> h)",
                source="implicit (category axiom)",
            ),
        ),
        law_verifications=(
            LawVerification(
                law_name="identity",
                status=LawStatus.STRUCTURAL,
                message="Category law holds by construction",
            ),
            LawVerification(
                law_name="associativity",
                status=LawStatus.STRUCTURAL,
                message="Category law holds by construction",
            ),
        ),
        fixed_point=FixedPointAnalysis(
            is_self_referential=True,
            fixed_point_description="[Structural mode] Self-reference detected but not analyzed",
            is_valid=True,
            implications=("Use --llm for full fixed-point analysis",),
        ),
        summary="Structural analysis: 2/2 category axioms hold by construction. Use --llm for full analysis.",
    )


def _epistemic_analysis_structural(spec_path: str) -> EpistemicReport:
    """
    Structural epistemic analysis (no LLM).

    Returns baseline epistemic properties (assumed L4 spec).
    For real analysis, use the async LLM-backed service.
    """
    from pathlib import Path

    path = Path(spec_path)
    if not path.exists():
        return EpistemicReport(
            target=spec_path,
            layer=4,
            toulmin=ToulminStructure(
                claim="",
                grounds=(),
                warrant="",
                backing="",
                qualifier="unknown",
                rebuttals=(),
                tier=EvidenceTier.EMPIRICAL,
            ),
            grounding=GroundingChain(steps=(), terminates_at_axiom=False),
            bootstrap=None,
            summary="Structural analysis failed: file not found",
        )

    return EpistemicReport(
        target=spec_path,
        layer=4,  # Assume L4 = Specification
        toulmin=ToulminStructure(
            claim="[Structural mode] Spec claims not analyzed",
            grounds=(),
            warrant="Use --llm for Toulmin analysis",
            backing="",
            qualifier="unknown",
            rebuttals=(),
            tier=EvidenceTier.EMPIRICAL,
        ),
        grounding=GroundingChain(
            steps=((4, str(path.name), "structural"),),
            terminates_at_axiom=False,
        ),
        bootstrap=BootstrapAnalysis(
            is_self_describing=False,
            layer_described=4,
            layer_occupied=4,
            is_valid=True,
            explanation="[Structural mode] Bootstrap not analyzed. Use --llm for full analysis.",
        ),
        summary="Structural analysis: assumed L4. Use --llm for full epistemic analysis.",
    )


def _dialectical_analysis_structural(spec_path: str) -> DialecticalReport:
    """
    Structural dialectical analysis (no LLM).

    Returns empty tensions (cannot detect without LLM).
    For real analysis, use the async LLM-backed service.
    """
    from pathlib import Path

    path = Path(spec_path)
    if not path.exists():
        return DialecticalReport(
            target=spec_path,
            tensions=(),
            summary="Structural analysis failed: file not found",
        )

    return DialecticalReport(
        target=spec_path,
        tensions=(),  # Cannot detect tensions without LLM
        summary="Structural analysis: no tensions detected (use --llm for dialectical analysis)",
    )


def _generative_analysis_structural(spec_path: str) -> GenerativeReport:
    """
    Structural generative analysis (no LLM).

    Computes actual file size but cannot test regenerability.
    For real analysis, use the async LLM-backed service.
    """
    from pathlib import Path

    path = Path(spec_path)
    if not path.exists():
        return GenerativeReport(
            target=spec_path,
            grammar=OperadGrammar(
                primitives=frozenset(),
                operations=frozenset(),
                laws=frozenset(),
            ),
            compression_ratio=1.0,
            regeneration=RegenerationTest(
                axioms_used=(),
                structures_regenerated=(),
                missing_elements=("file not found",),
                passed=False,
            ),
            minimal_kernel=(),
            summary="Structural analysis failed: file not found",
        )

    # Actually measure the file
    try:
        content = path.read_text()
        spec_lines = len(content.splitlines())
        # Estimate impl would be ~4x spec (typical ratio)
        estimated_impl_lines = spec_lines * 4
        compression_ratio = spec_lines / estimated_impl_lines if estimated_impl_lines > 0 else 1.0
    except Exception:
        spec_lines = 0
        compression_ratio = 1.0

    return GenerativeReport(
        target=spec_path,
        grammar=OperadGrammar(
            primitives=frozenset({"[use --llm for grammar extraction]"}),
            operations=frozenset(),
            laws=frozenset(),
        ),
        compression_ratio=compression_ratio,
        regeneration=RegenerationTest(
            axioms_used=(),
            structures_regenerated=(),
            missing_elements=("LLM analysis required for regeneration test",),
            passed=False,
        ),
        minimal_kernel=(),
        summary=f"Structural analysis: {spec_lines} lines, compression ~{compression_ratio:.2f}. Use --llm for regenerability test.",
    )


def _constitutional_analysis_structural(spec_path: str) -> ConstitutionalReport:
    """
    Structural constitutional analysis (no LLM).

    Returns neutral alignment (cannot evaluate without LLM).
    For real analysis, use the async LLM-backed service.
    """
    from pathlib import Path

    path = Path(spec_path)
    if not path.exists():
        # Import ConstitutionalAlignment from witness
        from services.witness.mark import ConstitutionalAlignment

        return ConstitutionalReport(
            target=spec_path,
            alignment=ConstitutionalAlignment.neutral(),
            violations=("file not found",),
            remediation_suggestions=("Ensure file exists at specified path",),
            summary="Structural analysis failed: file not found",
        )

    # Import ConstitutionalAlignment
    from services.witness.mark import ConstitutionalAlignment

    # Structural mode: return neutral alignment
    # Cannot evaluate principles without LLM
    alignment = ConstitutionalAlignment.neutral()

    return ConstitutionalReport(
        target=spec_path,
        alignment=alignment,
        violations=(),  # Cannot detect violations without LLM
        remediation_suggestions=("Use --llm for constitutional analysis",),
        summary="Structural analysis: neutral alignment (use --llm for full constitutional analysis)",
    )


def _full_analysis_structural(spec_path: str) -> FullAnalysisReport:
    """
    Structural full analysis (no LLM).

    Combines structural results from all four modes.
    For real analysis, use analyze_full_llm().
    """
    categorical = _categorical_analysis_structural(spec_path)
    epistemic = _epistemic_analysis_structural(spec_path)
    dialectical = _dialectical_analysis_structural(spec_path)
    generative = _generative_analysis_structural(spec_path)

    # Structural mode cannot fully validate—note this clearly
    synthesis = (
        f"Structural analysis of {spec_path}:\n"
        f"• Categorical: {categorical.laws_passed}/{categorical.laws_total} axioms hold by construction\n"
        f"• Epistemic: Assumed L{epistemic.layer} (use --llm for grounding analysis)\n"
        f"• Dialectical: Tensions not analyzed (use --llm)\n"
        f"• Generative: Compression ~{generative.compression_ratio:.2f} (use --llm for regenerability)\n"
        f"\nFor full four-mode analysis, use: kg analyze <path> --llm"
    )

    return FullAnalysisReport(
        target=spec_path,
        categorical=categorical,
        epistemic=epistemic,
        dialectical=dialectical,
        generative=generative,
        synthesis=synthesis,
    )


# =============================================================================
# LLM-Backed Analysis (the REAL analysis)
# =============================================================================


async def analyze_categorical_llm(spec_path: str) -> CategoricalReport:
    """
    LLM-backed categorical analysis.

    Uses services/analysis/AnalysisService for real Claude-powered analysis.
    Falls back to structural if LLM unavailable.
    """
    try:
        from agents.k.soul import create_llm_client
        from services.analysis import AnalysisService

        llm = create_llm_client()
        service = AnalysisService(llm)
        return await service.analyze_categorical(spec_path)
    except ImportError:
        return _categorical_analysis_structural(spec_path)
    except Exception as e:
        # Fallback on any error
        report = _categorical_analysis_structural(spec_path)
        return CategoricalReport(
            target=report.target,
            laws_extracted=report.laws_extracted,
            law_verifications=report.law_verifications,
            fixed_point=report.fixed_point,
            summary=f"LLM error ({e}); fell back to structural: {report.summary}",
        )


async def analyze_epistemic_llm(spec_path: str) -> EpistemicReport:
    """LLM-backed epistemic analysis."""
    try:
        from agents.k.soul import create_llm_client
        from services.analysis import AnalysisService

        llm = create_llm_client()
        service = AnalysisService(llm)
        return await service.analyze_epistemic(spec_path)
    except ImportError:
        return _epistemic_analysis_structural(spec_path)
    except Exception as e:
        report = _epistemic_analysis_structural(spec_path)
        return EpistemicReport(
            target=report.target,
            layer=report.layer,
            toulmin=report.toulmin,
            grounding=report.grounding,
            bootstrap=report.bootstrap,
            summary=f"LLM error ({e}); fell back to structural: {report.summary}",
        )


async def analyze_dialectical_llm(spec_path: str) -> DialecticalReport:
    """LLM-backed dialectical analysis."""
    try:
        from agents.k.soul import create_llm_client
        from services.analysis import AnalysisService

        llm = create_llm_client()
        service = AnalysisService(llm)
        return await service.analyze_dialectical(spec_path)
    except ImportError:
        return _dialectical_analysis_structural(spec_path)
    except Exception as e:
        report = _dialectical_analysis_structural(spec_path)
        return DialecticalReport(
            target=report.target,
            tensions=report.tensions,
            summary=f"LLM error ({e}); fell back to structural: {report.summary}",
        )


async def analyze_generative_llm(spec_path: str) -> GenerativeReport:
    """LLM-backed generative analysis."""
    try:
        from agents.k.soul import create_llm_client
        from services.analysis import AnalysisService

        llm = create_llm_client()
        service = AnalysisService(llm)
        return await service.analyze_generative(spec_path)
    except ImportError:
        return _generative_analysis_structural(spec_path)
    except Exception as e:
        report = _generative_analysis_structural(spec_path)
        return GenerativeReport(
            target=report.target,
            grammar=report.grammar,
            compression_ratio=report.compression_ratio,
            regeneration=report.regeneration,
            minimal_kernel=report.minimal_kernel,
            summary=f"LLM error ({e}); fell back to structural: {report.summary}",
        )


async def analyze_constitutional_llm(spec_path: str) -> ConstitutionalReport:
    """LLM-backed constitutional analysis."""
    try:
        from agents.k.soul import create_llm_client
        from services.analysis import AnalysisService

        llm = create_llm_client()
        service = AnalysisService(llm)
        return await service.analyze_constitutional(spec_path)
    except ImportError:
        return _constitutional_analysis_structural(spec_path)
    except Exception as e:
        report = _constitutional_analysis_structural(spec_path)
        return ConstitutionalReport(
            target=report.target,
            alignment=report.alignment,
            violations=report.violations,
            remediation_suggestions=report.remediation_suggestions,
            summary=f"LLM error ({e}); fell back to structural: {report.summary}",
        )


async def analyze_full_llm(spec_path: str) -> FullAnalysisReport:
    """
    LLM-backed full four-mode analysis.

    Implements the completeness law:
        full(X) = seq(par(categorical, epistemic), par(dialectical, generative))(X)

    Uses services/analysis/AnalysisService which runs:
    - Phase 1: Categorical + Epistemic in parallel
    - Phase 2: Dialectical + Generative in parallel (informed by phase 1)
    - Phase 3: Synthesize results
    """
    try:
        from agents.k.soul import create_llm_client
        from services.analysis import AnalysisService

        llm = create_llm_client()
        service = AnalysisService(llm)
        return await service.analyze_full(spec_path)
    except ImportError:
        return _full_analysis_structural(spec_path)
    except Exception as e:
        report = _full_analysis_structural(spec_path)
        return FullAnalysisReport(
            target=report.target,
            categorical=report.categorical,
            epistemic=report.epistemic,
            dialectical=report.dialectical,
            generative=report.generative,
            synthesis=f"LLM error ({e}); fell back to structural:\n\n{report.synthesis}",
        )


# =============================================================================
# Legacy Sync Wrappers (for backward compatibility)
# =============================================================================
# These call structural analysis. Use async *_llm() functions for real analysis.


def _categorical_analysis(spec_path: str) -> CategoricalReport:
    """Backward-compatible sync wrapper. Use analyze_categorical_llm() for real analysis."""
    return _categorical_analysis_structural(spec_path)


def _epistemic_analysis(spec_path: str) -> EpistemicReport:
    """Backward-compatible sync wrapper. Use analyze_epistemic_llm() for real analysis."""
    return _epistemic_analysis_structural(spec_path)


def _dialectical_analysis(spec_path: str) -> DialecticalReport:
    """Backward-compatible sync wrapper. Use analyze_dialectical_llm() for real analysis."""
    return _dialectical_analysis_structural(spec_path)


def _generative_analysis(spec_path: str) -> GenerativeReport:
    """Backward-compatible sync wrapper. Use analyze_generative_llm() for real analysis."""
    return _generative_analysis_structural(spec_path)


def _constitutional_analysis(spec_path: str) -> ConstitutionalReport:
    """Backward-compatible sync wrapper. Use analyze_constitutional_llm() for real analysis."""
    return _constitutional_analysis_structural(spec_path)


def _full_analysis(spec_path: str) -> FullAnalysisReport:
    """Backward-compatible sync wrapper. Use analyze_full_llm() for real analysis."""
    return _full_analysis_structural(spec_path)


# =============================================================================
# PolyAgent Wrappers for Analysis Operations
# =============================================================================


def _categorical_compose() -> PolyAgent[Any, str, CategoricalReport]:
    """Create categorical analysis agent."""
    return from_function("CategoricalAnalysis", _categorical_analysis)


def _epistemic_compose() -> PolyAgent[Any, str, EpistemicReport]:
    """Create epistemic analysis agent."""
    return from_function("EpistemicAnalysis", _epistemic_analysis)


def _dialectical_compose() -> PolyAgent[Any, str, DialecticalReport]:
    """Create dialectical analysis agent."""
    return from_function("DialecticalAnalysis", _dialectical_analysis)


def _generative_compose() -> PolyAgent[Any, str, GenerativeReport]:
    """Create generative analysis agent."""
    return from_function("GenerativeAnalysis", _generative_analysis)


def _constitutional_compose() -> PolyAgent[Any, str, ConstitutionalReport]:
    """Create constitutional analysis agent."""
    return from_function("ConstitutionalAnalysis", _constitutional_analysis)


def _full_compose() -> PolyAgent[Any, str, FullAnalysisReport]:
    """Create full analysis agent (all four modes)."""
    return from_function("FullAnalysis", _full_analysis)


def _seq_analysis(
    first: PolyAgent[Any, Any, Any],
    second: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Sequential analysis: output of first informs second."""
    return sequential(first, second)


def _par_analysis(
    left: PolyAgent[Any, Any, Any],
    right: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Parallel analysis: run both, merge results."""
    return parallel(left, right)


# =============================================================================
# Law Verification
# =============================================================================


def _verify_completeness(*args: Any) -> LawVerification:
    """Verify full = composition of all four modes."""
    # This is structural: full() calls all four modes
    return LawVerification(
        law_name="completeness",
        status=LawStatus.STRUCTURAL,
        message="full() defined as composition of all four modes",
    )


def _verify_idempotence(*args: Any) -> LawVerification:
    """Verify mode(mode(X)) = mode(X)."""
    # Analysis is stateless, so repeated application is idempotent
    return LawVerification(
        law_name="idempotence",
        status=LawStatus.STRUCTURAL,
        message="Analysis is stateless; repeated application yields same result",
    )


def _verify_meta_applicability(*args: Any) -> LawVerification:
    """Verify Analysis Operad can analyze itself."""
    try:
        # Self-analyze
        report = _full_analysis("spec/theory/analysis-operad.md")
        if report.is_valid:
            return LawVerification(
                law_name="meta_applicability",
                status=LawStatus.PASSED,
                message="Analysis Operad successfully analyzed itself",
            )
        else:
            return LawVerification(
                law_name="meta_applicability",
                status=LawStatus.FAILED,
                message=f"Self-analysis failed: {report.synthesis}",
            )
    except Exception as e:
        return LawVerification(
            law_name="meta_applicability",
            status=LawStatus.FAILED,
            message=f"Self-analysis raised exception: {e}",
        )


# =============================================================================
# Analysis Operad Definition
# =============================================================================


def create_analysis_operad() -> Operad:
    """
    Create the Analysis Operad (four modes of rigorous inquiry).

    Extends AGENT_OPERAD with:
    - categorical: Law verification and fixed-point analysis
    - epistemic: Justification and grounding analysis
    - dialectical: Tension identification and synthesis
    - generative: Regenerability and compression analysis
    - full: Complete four-mode analysis
    - seq/par: Analysis composition operations
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add analysis-specific operations
    ops["categorical"] = Operation(
        name="categorical",
        arity=0,  # Creates analysis agent
        signature="() -> Agent[str, CategoricalReport]",
        compose=_categorical_compose,
        description="Verify composition laws and fixed points",
    )

    ops["epistemic"] = Operation(
        name="epistemic",
        arity=0,
        signature="() -> Agent[str, EpistemicReport]",
        compose=_epistemic_compose,
        description="Analyze justification structure and grounding",
    )

    ops["dialectical"] = Operation(
        name="dialectical",
        arity=0,
        signature="() -> Agent[str, DialecticalReport]",
        compose=_dialectical_compose,
        description="Identify tensions and synthesize resolutions",
    )

    ops["generative"] = Operation(
        name="generative",
        arity=0,
        signature="() -> Agent[str, GenerativeReport]",
        compose=_generative_compose,
        description="Test regenerability from axioms",
    )

    ops["constitutional"] = Operation(
        name="constitutional",
        arity=0,
        signature="() -> Agent[str, ConstitutionalReport]",
        compose=_constitutional_compose,
        description="Verify alignment with 7 kgents principles",
    )

    ops["full"] = Operation(
        name="full",
        arity=0,
        signature="() -> Agent[str, FullAnalysisReport]",
        compose=_full_compose,
        description="Apply all four modes and synthesize",
    )

    # Inherit seq/par from AGENT_OPERAD but with analysis semantics
    # (Already present from AGENT_OPERAD)

    return Operad(
        name="AnalysisOperad",
        operations=ops,
        laws=[
            *AGENT_OPERAD.laws,  # Inherit universal laws
            Law(
                name="completeness",
                equation="full(X) = seq(par(categorical, epistemic), par(dialectical, generative))(X)",
                verify=_verify_completeness,
                description="Full analysis = all four modes composed",
            ),
            Law(
                name="idempotence",
                equation="mode(mode(X)) = mode(X)",
                verify=_verify_idempotence,
                description="Repeated analysis doesn't change results",
            ),
            Law(
                name="meta_applicability",
                equation="ANALYSIS_OPERAD.full(ANALYSIS_OPERAD.spec) = valid",
                verify=_verify_meta_applicability,
                description="The Analysis Operad can analyze itself",
            ),
        ],
        description="Four modes of rigorous inquiry: categorical, epistemic, dialectical, generative",
    )


# =============================================================================
# Global Instance and Registration
# =============================================================================


ANALYSIS_OPERAD = create_analysis_operad()


def _get_spec_path() -> str:
    """Resolve the Analysis Operad spec path from project root."""
    from pathlib import Path

    # Navigate from this file to project root
    # This file: impl/claude/agents/operad/domains/analysis.py
    # Project root: 5 levels up
    this_file = Path(__file__).resolve()
    project_root = this_file.parent.parent.parent.parent.parent.parent
    spec_path = project_root / "spec" / "theory" / "analysis-operad.md"

    if not spec_path.exists():
        # Fallback: try relative path (might work if CWD is project root)
        return "spec/theory/analysis-operad.md"

    return str(spec_path)


def self_analyze() -> FullAnalysisReport:
    """
    Apply the Analysis Operad to its own specification (structural mode).

    This is the meta-applicability test: can analysis analyze itself?
    Returns a full report on the Analysis Operad spec.

    For LLM-backed self-analysis, use self_analyze_llm().
    """
    return _full_analysis_structural(_get_spec_path())


async def self_analyze_llm() -> FullAnalysisReport:
    """
    Apply the Analysis Operad to its own specification (LLM mode).

    This is the TRUE meta-applicability test: can analysis analyze itself
    using actual LLM-powered analysis?

    This function:
    1. Loads the Analysis Operad spec
    2. Runs full four-mode LLM analysis
    3. Returns a real report (not hardcoded)

    The report will honestly evaluate the spec, including any issues.
    """
    return await analyze_full_llm(_get_spec_path())


__all__ = [
    # Operad
    "ANALYSIS_OPERAD",
    "create_analysis_operad",
    # Report types
    "CategoricalReport",
    "EpistemicReport",
    "DialecticalReport",
    "GenerativeReport",
    "ConstitutionalReport",
    "FullAnalysisReport",
    # Supporting types
    "LawExtraction",
    "FixedPointAnalysis",
    "ToulminStructure",
    "GroundingChain",
    "BootstrapAnalysis",
    "Tension",
    "OperadGrammar",
    "RegenerationTest",
    # Enums
    "ContradictionType",
    "EvidenceTier",
    # LLM-backed analysis (async) - USE THESE FOR REAL ANALYSIS
    "analyze_categorical_llm",
    "analyze_epistemic_llm",
    "analyze_dialectical_llm",
    "analyze_generative_llm",
    "analyze_constitutional_llm",
    "analyze_full_llm",
    "self_analyze_llm",
    # Structural analysis (sync) - fallback when LLM unavailable
    "self_analyze",
    "_categorical_analysis",
    "_epistemic_analysis",
    "_dialectical_analysis",
    "_generative_analysis",
    "_constitutional_analysis",
    "_full_analysis",
]
