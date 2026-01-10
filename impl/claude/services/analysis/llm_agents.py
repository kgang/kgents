"""
LLM Agent Wrappers for Analysis Modes.

Each analysis mode has a specialized LLM agent that:
1. Takes a spec path or content
2. Constructs the appropriate prompt
3. Calls the LLM
4. Parses the response into a typed report

The agents use the async LLM client from agents.k.soul for Claude integration.

Teaching:
    gotcha: These are thin wrappers around LLM calls. Heavy logic belongs
            in parsers.py (parsing) or service.py (orchestration).
            Keep agents focused on prompt+invoke+parse.
            (Evidence: SRP from Crown Jewel patterns)

    gotcha: All methods are async. Do NOT call them synchronously.
            Use await or asyncio.run() in scripts.
            (Evidence: agents.k.soul.LLMClient is fully async)

    gotcha: LLM calls can fail (network, rate limits, API errors).
            Agents catch exceptions and return error reports.
            Check report.summary for "error" or "timeout".
            (Evidence: test_llm_agents.py::test_categorical_agent_handles_llm_error)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .parsers import (
    parse_categorical_response,
    parse_constitutional_response,
    parse_dialectical_response,
    parse_epistemic_response,
    parse_generative_response,
)
from .prompts import (
    CATEGORICAL_PROMPT,
    CONSTITUTIONAL_PROMPT,
    DIALECTICAL_PROMPT,
    EPISTEMIC_PROMPT,
    GENERATIVE_PROMPT,
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
# Categorical Analyzer
# =============================================================================


class CategoricalAnalyzer:
    """
    LLM-backed categorical analysis agent.

    Performs law extraction, verification, and fixed-point analysis.

    Usage:
        >>> analyzer = CategoricalAnalyzer(llm_client)
        >>> report = await analyzer.analyze("spec/theory/zero-seed.md")
        >>> print(f"Laws: {report.laws_passed}/{report.laws_total}")
    """

    def __init__(self, llm: "LLMClient"):
        """
        Initialize with LLM client.

        Args:
            llm: LLMClient instance from agents.k.soul
        """
        self.llm = llm

    async def analyze(self, spec_content: str, target: str) -> "CategoricalReport":
        """
        Perform categorical analysis on spec content.

        Args:
            spec_content: Full text of the specification
            target: Path or identifier of the spec

        Returns:
            CategoricalReport with laws, verifications, and fixed points
        """
        try:
            # Build prompt
            prompt = CATEGORICAL_PROMPT.format(spec_content=spec_content)

            # Call LLM
            logger.debug(f"Categorical analysis of {target}")
            response = await self.llm.generate(
                system="You are a category theorist analyzing software specifications for composition laws and fixed points. Return only valid JSON.",
                user=prompt,
                max_tokens=4000,
            )

            # Parse response (extract text from LLMResponse)
            return parse_categorical_response(response.text, target)

        except Exception as e:
            logger.error(f"Categorical analysis error for {target}: {e}")
            # Return error report
            from agents.operad.domains.analysis import CategoricalReport

            return CategoricalReport(
                target=target,
                laws_extracted=(),
                law_verifications=(),
                fixed_point=None,
                summary=f"LLM error: {e}",
            )


# =============================================================================
# Epistemic Analyzer
# =============================================================================


class EpistemicAnalyzer:
    """
    LLM-backed epistemic analysis agent.

    Analyzes justification structure, grounding, and bootstrapping.

    Usage:
        >>> analyzer = EpistemicAnalyzer(llm_client)
        >>> report = await analyzer.analyze("spec/protocols/witness.md")
        >>> print(f"Layer: L{report.layer}, Grounded: {report.is_grounded}")
    """

    def __init__(self, llm: "LLMClient"):
        """
        Initialize with LLM client.

        Args:
            llm: LLMClient instance from agents.k.soul
        """
        self.llm = llm

    async def analyze(self, spec_content: str, target: str) -> "EpistemicReport":
        """
        Perform epistemic analysis on spec content.

        Args:
            spec_content: Full text of the specification
            target: Path or identifier of the spec

        Returns:
            EpistemicReport with layer, Toulmin structure, and grounding
        """
        try:
            # Build prompt
            prompt = EPISTEMIC_PROMPT.format(spec_content=spec_content)

            # Call LLM
            logger.debug(f"Epistemic analysis of {target}")
            response = await self.llm.generate(
                system="You are an epistemologist analyzing the justification structure and grounding of specifications. Return only valid JSON.",
                user=prompt,
                max_tokens=4000,
            )

            # Parse response (extract text from LLMResponse)
            return parse_epistemic_response(response.text, target)

        except Exception as e:
            logger.error(f"Epistemic analysis error for {target}: {e}")
            # Return error report
            from agents.operad.domains.analysis import (
                EpistemicReport,
                EvidenceTier,
                GroundingChain,
                ToulminStructure,
            )

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
                summary=f"LLM error: {e}",
            )


# =============================================================================
# Dialectical Analyzer
# =============================================================================


class DialecticalAnalyzer:
    """
    LLM-backed dialectical analysis agent.

    Identifies tensions, classifies contradictions, and attempts synthesis.

    Usage:
        >>> analyzer = DialecticalAnalyzer(llm_client)
        >>> report = await analyzer.analyze("spec/agents/operad.md")
        >>> print(f"Tensions: {len(report.tensions)}, Problematic: {report.problematic_count}")
    """

    def __init__(self, llm: "LLMClient"):
        """
        Initialize with LLM client.

        Args:
            llm: LLMClient instance from agents.k.soul
        """
        self.llm = llm

    async def analyze(
        self, spec_content: str, target: str, context: str | None = None
    ) -> "DialecticalReport":
        """
        Perform dialectical analysis on spec content.

        Args:
            spec_content: Full text of the specification
            target: Path or identifier of the spec
            context: Optional context from other analysis modes

        Returns:
            DialecticalReport with tensions and syntheses
        """
        try:
            # Build prompt
            prompt = DIALECTICAL_PROMPT.format(spec_content=spec_content)

            # Call LLM
            logger.debug(f"Dialectical analysis of {target}")
            response = await self.llm.generate(
                system="You are a dialectician analyzing tensions and contradictions in specifications. Return only valid JSON.",
                user=prompt,
                max_tokens=4000,
            )

            # Parse response (extract text from LLMResponse)
            return parse_dialectical_response(response.text, target)

        except Exception as e:
            logger.error(f"Dialectical analysis error for {target}: {e}")
            # Return error report
            from agents.operad.domains.analysis import DialecticalReport

            return DialecticalReport(
                target=target,
                tensions=(),
                summary=f"LLM error: {e}",
            )


# =============================================================================
# Generative Analyzer
# =============================================================================


class GenerativeAnalyzer:
    """
    LLM-backed generative analysis agent.

    Tests compression, grammar extraction, and regenerability.

    Usage:
        >>> analyzer = GenerativeAnalyzer(llm_client)
        >>> report = await analyzer.analyze("spec/theory/dp-native-kgents.md")
        >>> print(f"Compression: {report.compression_ratio:.2f}, Regenerable: {report.is_regenerable}")
    """

    def __init__(self, llm: "LLMClient"):
        """
        Initialize with LLM client.

        Args:
            llm: LLMClient instance from agents.k.soul
        """
        self.llm = llm

    async def analyze(self, spec_content: str, target: str) -> "GenerativeReport":
        """
        Perform generative analysis on spec content.

        Args:
            spec_content: Full text of the specification
            target: Path or identifier of the spec

        Returns:
            GenerativeReport with grammar, compression, and regeneration test
        """
        try:
            # Build prompt
            prompt = GENERATIVE_PROMPT.format(spec_content=spec_content)

            # Call LLM
            logger.debug(f"Generative analysis of {target}")
            response = await self.llm.generate(
                system="You are a compression analyst testing whether specifications are regenerable from axioms. Return only valid JSON.",
                user=prompt,
                max_tokens=4000,
            )

            # Parse response (extract text from LLMResponse)
            return parse_generative_response(response.text, target)

        except Exception as e:
            logger.error(f"Generative analysis error for {target}: {e}")
            # Return error report
            from agents.operad.domains.analysis import (
                GenerativeReport,
                OperadGrammar,
                RegenerationTest,
            )

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
                summary=f"LLM error: {e}",
            )


# =============================================================================
# Constitutional Analyzer
# =============================================================================


class ConstitutionalAnalyzer:
    """
    LLM-backed constitutional analysis agent.

    Verifies alignment with the 7 kgents principles.

    Usage:
        >>> analyzer = ConstitutionalAnalyzer(llm_client)
        >>> report = await analyzer.analyze("spec/protocols/witness.md")
        >>> print(f"Aligned: {report.is_aligned}, Score: {report.alignment_score:.2f}")
    """

    def __init__(self, llm: "LLMClient"):
        """
        Initialize with LLM client.

        Args:
            llm: LLMClient instance from agents.k.soul
        """
        self.llm = llm

    async def analyze(self, spec_content: str, target: str) -> "ConstitutionalReport":
        """
        Perform constitutional analysis on spec content.

        Args:
            spec_content: Full text of the specification
            target: Path or identifier of the spec

        Returns:
            ConstitutionalReport with alignment scores and violations
        """
        try:
            # Build prompt
            prompt = CONSTITUTIONAL_PROMPT.format(spec_content=spec_content)

            # Call LLM
            logger.debug(f"Constitutional analysis of {target}")
            response = await self.llm.generate(
                system="You are a constitutional analyst evaluating specifications against the 7 kgents principles. Return only valid JSON.",
                user=prompt,
                max_tokens=4000,
            )

            # Parse response (extract text from LLMResponse)
            return parse_constitutional_response(response.text, target)

        except Exception as e:
            logger.error(f"Constitutional analysis error for {target}: {e}")
            # Return error report
            from agents.operad.domains.analysis import ConstitutionalReport
            from services.witness.mark import ConstitutionalAlignment

            return ConstitutionalReport(
                target=target,
                alignment=ConstitutionalAlignment.neutral(),
                violations=("All principles",),
                remediation_suggestions=(f"LLM error: {e}",),
                summary=f"LLM error: {e}",
            )


__all__ = [
    "CategoricalAnalyzer",
    "EpistemicAnalyzer",
    "DialecticalAnalyzer",
    "GenerativeAnalyzer",
    "ConstitutionalAnalyzer",
]
