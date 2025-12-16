"""
Competitive Intelligence Task Template.

Coalition Shape: Scout + 3 specialists
Output Format: Briefing Document
Credits: 100

Competitive intelligence is the most expensive template,
reflecting the depth of research and analysis required.
Multiple Scouts work in parallel to gather comprehensive data.

Flow:
    1. Lead Scout coordinates research strategy
    2. Specialist Scouts focus on different aspects:
       - Market positioning
       - Product features
       - Financial indicators
       - Customer sentiment
    3. Sage synthesizes into strategic briefing
    4. Output as executive briefing document
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from ..task import (
    CoalitionShape,
    HandoffPattern,
    OutputFormat,
    TaskInput,
    TaskOutput,
)
from .base import TaskTemplate

# Coalition shape for competitive intel - scout-heavy
COMPETITIVE_INTEL_SHAPE = CoalitionShape(
    required=("Scout", "Sage"),  # Lead Scout + analysis
    optional=("Scout", "Scout", "Steady"),  # Specialist Scouts + validation
    lead="Scout",
    pattern=HandoffPattern.PARALLEL,  # Scouts work in parallel
    min_eigenvector={"analytical": 0.9, "creativity": 0.4},
)


@dataclass
class CompetitiveIntelTask(TaskTemplate):
    """
    Competitive Intelligence: Deep competitive analysis.

    Input: Company/product to analyze, competitors, focus areas
    Output: Executive briefing with:
        - Competitive landscape overview
        - Per-competitor profiles
        - SWOT analysis
        - Strategic recommendations
        - Market trends
    """

    template_id: ClassVar[str] = "competitive_intel"
    name: ClassVar[str] = "Competitive Intelligence"
    description: ClassVar[str] = (
        "Deep competitive analysis and market intelligence. "
        "Multiple Scouts research in parallel, Sage synthesizes "
        "into strategic briefing."
    )
    base_credits: ClassVar[int] = 100
    output_format: ClassVar[OutputFormat] = OutputFormat.BRIEFING

    coalition_shape: CoalitionShape = field(
        default_factory=lambda: COMPETITIVE_INTEL_SHAPE
    )

    def validate_input(self, input: TaskInput) -> tuple[bool, list[str]]:
        """Validate competitive intel requirements."""
        is_valid, errors = super().validate_input(input)

        # Need a target company/product
        if not input.target:
            errors.append(
                "Competitive intelligence requires a target company or product. "
                "Specify target='Company Name' or context={'target': '...'}."
            )
            is_valid = False

        # Competitors are helpful
        competitors = input.context.get("competitors", [])
        if not competitors:
            errors.append(
                "No competitors specified. Add context={'competitors': ['Comp A', 'Comp B']} "
                "or the analysis will auto-discover competitors."
            )
            # Warning only

        return is_valid, errors

    def estimate_credits(self, input: TaskInput) -> int:
        """Intel is expensive - scales with competitor count."""
        base = super().estimate_credits(input)

        # More competitors = more research
        competitors = input.context.get("competitors", [])
        if len(competitors) > 5:
            base = int(base * 1.5)
        elif len(competitors) > 10:
            base = int(base * 2.0)

        return base

    def suggest_coalition(self, input: TaskInput) -> CoalitionShape:
        """Scale coalition with competitor count."""
        competitors = input.context.get("competitors", [])

        if len(competitors) > 5:
            # Many competitors: add more scouts
            return CoalitionShape(
                required=("Scout", "Scout", "Scout", "Sage"),
                optional=("Steady",),
                lead="Scout",
                pattern=HandoffPattern.PARALLEL,
            )
        elif len(competitors) <= 2:
            # Few competitors: lighter team
            return CoalitionShape(
                required=("Scout", "Sage"),
                optional=(),
                lead="Scout",
                pattern=HandoffPattern.SEQUENTIAL,
            )

        return self.coalition_shape

    def get_phase_sequence(self) -> list[str]:
        """Intel is exploration-heavy."""
        return ["EXPLORING", "EXPLORING", "EXPLORING", "DESIGNING"]

    def get_handoff_descriptions(self) -> dict[str, str]:
        """Parallel scouts converge to Sage."""
        return {
            "Scout(Lead)→Scout(Market)": "Lead Scout delegates market research",
            "Scout(Lead)→Scout(Product)": "Lead Scout delegates product analysis",
            "Scout(Lead)→Scout(Financial)": "Lead Scout delegates financial review",
            "All Scouts→Sage": "Scouts converge findings to Sage for synthesis",
            "Sage→Steady": "Sage passes briefing draft for validation",
        }

    async def execute(
        self,
        input: TaskInput,
        coalition: Any,
    ) -> TaskOutput:
        """Execute competitive intelligence gathering."""
        target = input.target or "Unknown Company"
        competitors = input.context.get("competitors", ["Competitor A", "Competitor B"])
        focus_areas = input.context.get("focus_areas", ["market", "product", "pricing"])

        # Build briefing document
        competitor_profiles = []
        for competitor in competitors:
            profile = {
                "name": competitor,
                "strengths": [f"{competitor} has strong brand recognition"],
                "weaknesses": [f"{competitor} has limited international presence"],
                "market_share": "~15%",  # Simulated
                "key_products": [f"{competitor} Core", f"{competitor} Pro"],
                "recent_moves": [f"{competitor} launched new feature X"],
            }
            competitor_profiles.append(profile)

        swot = {
            "strengths": [
                f"{target} has innovative technology",
                f"{target} has loyal customer base",
            ],
            "weaknesses": [
                f"{target} has smaller market share",
                f"{target} has limited marketing budget",
            ],
            "opportunities": [
                "Growing market segment",
                "Competitor vulnerabilities",
            ],
            "threats": [
                "New market entrants",
                "Regulatory changes",
            ],
        }

        content = {
            "title": f"Competitive Intelligence Briefing: {target}",
            "executive_summary": (
                f"Analysis of {target} competitive position against "
                f"{len(competitors)} key competitors in {', '.join(focus_areas)}."
            ),
            "target": {
                "name": target,
                "description": input.description,
            },
            "competitive_landscape": {
                "total_competitors_analyzed": len(competitors),
                "focus_areas": focus_areas,
                "market_overview": "The market is competitive with several established players.",
            },
            "competitor_profiles": competitor_profiles,
            "swot_analysis": swot,
            "strategic_recommendations": [
                {
                    "priority": "high",
                    "recommendation": "Differentiate on innovation",
                    "rationale": "Technology advantage is key differentiator",
                },
                {
                    "priority": "medium",
                    "recommendation": "Expand marketing reach",
                    "rationale": "Increase brand awareness in target segments",
                },
                {
                    "priority": "low",
                    "recommendation": "Monitor competitor pricing",
                    "rationale": "Stay competitive without race to bottom",
                },
            ],
            "market_trends": [
                "Trend 1: Shift to subscription models",
                "Trend 2: Increased focus on AI features",
                "Trend 3: Consolidation through M&A",
            ],
            "appendix": {
                "methodology": "Multi-source research using public data",
                "data_sources": [
                    "Public filings",
                    "Press releases",
                    "Customer reviews",
                ],
                "limitations": [
                    "Private company data limited",
                    "Real-time data not available",
                ],
            },
        }

        return TaskOutput(
            content=content,
            format=OutputFormat.BRIEFING,
            summary=f"Competitive intel briefing for {target} vs {len(competitors)} competitors",
            coalition_used=("Scout", "Scout", "Scout", "Sage"),
            handoffs=5,
            confidence=0.65,  # Intel always has uncertainty
            coverage=0.8,
            warnings=(
                "Analysis based on publicly available information",
                "Market conditions may have changed since analysis",
            ),
            artifacts=[
                {"type": "competitors_analyzed", "value": len(competitors)},
                {"type": "focus_areas", "value": len(focus_areas)},
            ],
        )


# Singleton template instance
COMPETITIVE_INTEL_TEMPLATE = CompetitiveIntelTask()

__all__ = [
    "CompetitiveIntelTask",
    "COMPETITIVE_INTEL_TEMPLATE",
    "COMPETITIVE_INTEL_SHAPE",
]
