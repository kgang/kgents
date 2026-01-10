"""
Analysis Service: Main orchestrator for four-mode LLM analysis.

The AnalysisService coordinates the four analysis modes:
1. Categorical (laws and fixed points)
2. Epistemic (grounding and justification)
3. Dialectical (tensions and contradictions)
4. Generative (compression and regeneration)

Architecture:
    - Loads spec content from disk
    - Delegates to mode-specific LLM agents
    - Runs modes in optimal order (cat+epi first, then dia+gen)
    - Synthesizes results into FullAnalysisReport

Integration Points:
    - Uses agents.k.soul.LLMClient for Claude API
    - Returns typed reports from agents.operad.domains.analysis
    - Can emit Witness marks (optional)
    - Can integrate with ASHC for confidence (optional)

Teaching:
    gotcha: Full analysis is NOT just parallel execution of four modes.
            It runs categorical+epistemic first, THEN dialectical+generative
            informed by first phase results (completeness law).
            (Evidence: spec/theory/analysis-operad.md §2.2)

    gotcha: File paths are resolved relative to working directory.
            Use absolute paths or ensure CWD is project root.
            (Evidence: _load_spec_content uses pathlib.Path.resolve())

    gotcha: Missing or unreadable files return error reports, not exceptions.
            Check report.summary for "error" or "not found".
            (Evidence: test_service.py::test_analyze_missing_file)

See: spec/theory/analysis-operad.md
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from agents.operad.domains.analysis import FullAnalysisReport

from .llm_agents import (
    CategoricalAnalyzer,
    ConstitutionalAnalyzer,
    DialecticalAnalyzer,
    EpistemicAnalyzer,
    GenerativeAnalyzer,
)

if TYPE_CHECKING:
    from agents.k.soul import LLMClient  # type: ignore[attr-defined]
    from agents.operad.domains.analysis import (
        CategoricalReport,
        ConstitutionalReport,
        DialecticalReport,
        EpistemicReport,
        GenerativeReport,
    )

logger = logging.getLogger(__name__)


# =============================================================================
# Helper Functions
# =============================================================================


def _load_spec_content(spec_path: str) -> str:
    """
    Load spec content from disk.

    Args:
        spec_path: Path to spec file (absolute or relative to CWD)

    Returns:
        Spec content as string

    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file can't be read
    """
    path = Path(spec_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Spec not found: {spec_path}")
    if not path.is_file():
        raise IOError(f"Not a file: {spec_path}")

    return path.read_text(encoding="utf-8")


# =============================================================================
# Main Service
# =============================================================================


class AnalysisService:
    """
    LLM-backed four-mode analysis service.

    Coordinates categorical, epistemic, dialectical, and generative
    analysis of specifications using Claude.

    Usage:
        >>> from agents.k.soul import create_llm_client
        >>> from services.analysis import AnalysisService
        >>>
        >>> llm = create_llm_client()
        >>> service = AnalysisService(llm)
        >>>
        >>> # Full analysis
        >>> report = await service.analyze_full("spec/theory/zero-seed.md")
        >>> print(report.synthesis)
        >>>
        >>> # Single mode
        >>> cat_report = await service.analyze_categorical("spec/protocols/witness.md")
        >>> print(f"Laws: {cat_report.laws_passed}/{cat_report.laws_total}")

    The service follows the completeness law from the Analysis Operad:
        full(X) = seq(par(categorical, epistemic), par(dialectical, generative))(X)

    Phase 1: Run categorical + epistemic in parallel
    Phase 2: Run dialectical + generative in parallel (informed by phase 1)
    Phase 3: Synthesize all four results
    """

    def __init__(self, llm: "LLMClient"):
        """
        Initialize with LLM client.

        Args:
            llm: LLMClient instance from agents.k.soul.create_llm_client()
        """
        self.llm = llm
        self.categorical = CategoricalAnalyzer(llm)
        self.epistemic = EpistemicAnalyzer(llm)
        self.dialectical = DialecticalAnalyzer(llm)
        self.generative = GenerativeAnalyzer(llm)
        self.constitutional = ConstitutionalAnalyzer(llm)

    async def analyze_categorical(self, spec_path: str) -> "CategoricalReport":
        """
        Perform categorical analysis (laws and fixed points).

        Args:
            spec_path: Path to specification file

        Returns:
            CategoricalReport with law verifications
        """
        try:
            spec_content = _load_spec_content(spec_path)
            return await self.categorical.analyze(spec_content, spec_path)
        except Exception as e:
            logger.error(f"Categorical analysis failed for {spec_path}: {e}")
            from agents.operad.domains.analysis import CategoricalReport

            return CategoricalReport(
                target=spec_path,
                laws_extracted=(),
                law_verifications=(),
                fixed_point=None,
                summary=f"Error: {e}",
            )

    async def analyze_epistemic(self, spec_path: str) -> "EpistemicReport":
        """
        Perform epistemic analysis (grounding and justification).

        Args:
            spec_path: Path to specification file

        Returns:
            EpistemicReport with layer, Toulmin structure, grounding
        """
        try:
            spec_content = _load_spec_content(spec_path)
            return await self.epistemic.analyze(spec_content, spec_path)
        except Exception as e:
            logger.error(f"Epistemic analysis failed for {spec_path}: {e}")
            from agents.operad.domains.analysis import (
                EpistemicReport,
                EvidenceTier,
                GroundingChain,
                ToulminStructure,
            )

            return EpistemicReport(
                target=spec_path,
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
                summary=f"Error: {e}",
            )

    async def analyze_dialectical(
        self,
        spec_path: str,
        categorical: "CategoricalReport | None" = None,
    ) -> "DialecticalReport":
        """
        Perform dialectical analysis (tensions and contradictions).

        Args:
            spec_path: Path to specification file
            categorical: Optional categorical report for context

        Returns:
            DialecticalReport with tensions and syntheses
        """
        try:
            spec_content = _load_spec_content(spec_path)

            # Build context from categorical if provided
            context = None
            if categorical and categorical.has_violations:
                violations = [
                    v.law_name for v in categorical.law_verifications if v.status.name == "FAILED"
                ]
                context = f"Law violations detected: {', '.join(violations)}"

            return await self.dialectical.analyze(spec_content, spec_path, context)
        except Exception as e:
            logger.error(f"Dialectical analysis failed for {spec_path}: {e}")
            from agents.operad.domains.analysis import DialecticalReport

            return DialecticalReport(
                target=spec_path,
                tensions=(),
                summary=f"Error: {e}",
            )

    async def analyze_generative(self, spec_path: str) -> "GenerativeReport":
        """
        Perform generative analysis (compression and regeneration).

        Args:
            spec_path: Path to specification file

        Returns:
            GenerativeReport with grammar, compression, regeneration test
        """
        try:
            spec_content = _load_spec_content(spec_path)
            return await self.generative.analyze(spec_content, spec_path)
        except Exception as e:
            logger.error(f"Generative analysis failed for {spec_path}: {e}")
            from agents.operad.domains.analysis import (
                GenerativeReport,
                OperadGrammar,
                RegenerationTest,
            )

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
                    missing_elements=(),
                    passed=False,
                ),
                minimal_kernel=(),
                summary=f"Error: {e}",
            )

    async def analyze_constitutional(self, spec_path: str) -> "ConstitutionalReport":
        """
        Perform constitutional analysis (alignment with 7 principles).

        Args:
            spec_path: Path to specification file

        Returns:
            ConstitutionalReport with alignment scores and violations
        """
        try:
            spec_content = _load_spec_content(spec_path)
            return await self.constitutional.analyze(spec_content, spec_path)
        except Exception as e:
            logger.error(f"Constitutional analysis failed for {spec_path}: {e}")
            from agents.operad.domains.analysis import ConstitutionalReport
            from services.witness.mark import ConstitutionalAlignment

            return ConstitutionalReport(
                target=spec_path,
                alignment=ConstitutionalAlignment.neutral(),
                violations=("All principles",),
                remediation_suggestions=(f"Error: {e}",),
                summary=f"Error: {e}",
            )

    async def analyze_full(self, spec_path: str) -> "FullAnalysisReport":
        """
        Perform complete four-mode analysis.

        Implements the completeness law:
            full(X) = seq(par(categorical, epistemic), par(dialectical, generative))(X)

        Phase 1: Categorical + Epistemic in parallel
        Phase 2: Dialectical + Generative in parallel (informed by phase 1)
        Phase 3: Synthesize all results

        Args:
            spec_path: Path to specification file

        Returns:
            FullAnalysisReport with all four modes and synthesis
        """
        try:
            # Phase 1: Categorical + Epistemic in parallel
            logger.info(f"Full analysis phase 1 (cat+epi): {spec_path}")
            categorical, epistemic = await asyncio.gather(
                self.analyze_categorical(spec_path),
                self.analyze_epistemic(spec_path),
            )

            # Phase 2: Dialectical + Generative in parallel
            # (informed by phase 1 results)
            logger.info(f"Full analysis phase 2 (dia+gen): {spec_path}")
            dialectical, generative = await asyncio.gather(
                self.analyze_dialectical(spec_path, categorical),
                self.analyze_generative(spec_path),
            )

            # Phase 3: Synthesize
            synthesis = self._synthesize(categorical, epistemic, dialectical, generative)

            return FullAnalysisReport(
                target=spec_path,
                categorical=categorical,
                epistemic=epistemic,
                dialectical=dialectical,
                generative=generative,
                synthesis=synthesis,
            )

        except Exception as e:
            logger.error(f"Full analysis failed for {spec_path}: {e}")
            # Return error report
            from agents.operad.domains.analysis import (
                CategoricalReport,
                DialecticalReport,
                EpistemicReport,
                EvidenceTier,
                GenerativeReport,
                GroundingChain,
                OperadGrammar,
                RegenerationTest,
                ToulminStructure,
            )

            return FullAnalysisReport(
                target=spec_path,
                categorical=CategoricalReport(
                    target=spec_path,
                    laws_extracted=(),
                    law_verifications=(),
                    fixed_point=None,
                    summary="Error",
                ),
                epistemic=EpistemicReport(
                    target=spec_path,
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
                    summary="Error",
                ),
                dialectical=DialecticalReport(target=spec_path, tensions=(), summary="Error"),
                generative=GenerativeReport(
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
                        missing_elements=(),
                        passed=False,
                    ),
                    minimal_kernel=(),
                    summary="Error",
                ),
                synthesis=f"Error: {e}",
            )

    def _synthesize(
        self,
        categorical: "CategoricalReport",
        epistemic: "EpistemicReport",
        dialectical: "DialecticalReport",
        generative: "GenerativeReport",
    ) -> str:
        """
        Synthesize insights from all four modes.

        Args:
            categorical: Categorical analysis result
            epistemic: Epistemic analysis result
            dialectical: Dialectical analysis result
            generative: Generative analysis result

        Returns:
            Synthesis string summarizing overall assessment
        """
        parts = []

        # Categorical
        if categorical.has_violations:
            parts.append(
                f"⚠️ Categorical: {categorical.laws_passed}/{categorical.laws_total} laws hold"
            )
        else:
            parts.append(f"✓ Categorical: {categorical.laws_total} laws verified")

        # Epistemic
        if epistemic.is_grounded:
            parts.append(f"✓ Epistemic: Grounded at L{epistemic.layer}")
        else:
            parts.append("⚠️ Epistemic: Not properly grounded")

        # Dialectical
        if dialectical.problematic_count > 0:
            parts.append(f"⚠️ Dialectical: {dialectical.problematic_count} problematic tensions")
        else:
            parts.append(
                f"✓ Dialectical: {len(dialectical.tensions)} tensions, {dialectical.resolved_count} resolved"
            )

        # Generative
        if generative.is_regenerable and generative.is_compressed:
            parts.append(
                f"✓ Generative: Compression {generative.compression_ratio:.2f}, regenerable"
            )
        else:
            status = []
            if not generative.is_compressed:
                status.append("not compressed")
            if not generative.is_regenerable:
                status.append("not regenerable")
            parts.append(f"⚠️ Generative: {', '.join(status)}")

        # Overall verdict
        is_valid = (
            not categorical.has_violations
            and epistemic.is_grounded
            and dialectical.problematic_count == 0
            and generative.is_regenerable
        )

        if is_valid:
            verdict = "✅ VALID SPECIFICATION"
        else:
            verdict = "⚠️ ISSUES DETECTED"

        return f"{verdict}\n\n" + "\n".join(parts)


__all__ = [
    "AnalysisService",
]
