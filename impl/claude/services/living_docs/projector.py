"""
Living Docs Projector: DocNode x Observer -> Surface

Implements the projection functor from the spec:
    project : DocNode x Observer -> Surface

Different observers get different projections:
- human: Narrative with density adaptation (compact/comfortable/spacious)
- agent: Dense, structured - no prose
- ide: Minimal - signature + one critical gotcha

Teaching:
    gotcha: Projection is a single function, not a class hierarchy.
            (Evidence: test_projector.py::test_single_function)

    gotcha: Density only applies to human observers.
            (Evidence: test_projector.py::test_density_human_only)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .types import DocNode, LivingDocsObserver, Surface, TeachingMoment, Tier


# Density parameters following elastic-ui-patterns
@dataclass(frozen=True)
class DensityParams:
    """Parameters that vary by density level."""

    truncate_length: int  # 0 = no truncation
    show_details: bool
    show_teaching: bool
    max_examples: int


DENSITY_PARAMS: dict[Literal["compact", "comfortable", "spacious"], DensityParams] = {
    "compact": DensityParams(
        truncate_length=50,
        show_details=False,
        show_teaching=False,
        max_examples=1,
    ),
    "comfortable": DensityParams(
        truncate_length=100,
        show_details=True,
        show_teaching=True,
        max_examples=2,
    ),
    "spacious": DensityParams(
        truncate_length=0,  # No truncation
        show_details=True,
        show_teaching=True,
        max_examples=5,
    ),
}


def project(node: DocNode, observer: LivingDocsObserver) -> Surface:
    """
    Project a DocNode to a Surface for a specific observer.

    This is the core functor:
        project : DocNode x Observer -> Surface

    Law (Functor): project(compose(a, b)) == compose(project(a), project(b))

    Args:
        node: The documentation node to project
        observer: Who's reading (human/agent/ide + density)

    Returns:
        Surface with appropriate content and format
    """
    if observer.kind == "agent":
        return _agent_projection(node)
    elif observer.kind == "ide":
        return _ide_projection(node)
    else:  # human
        return _human_projection(node, observer.density)


def _agent_projection(node: DocNode) -> Surface:
    """
    Dense, structured projection for agent consumption.

    Agents want:
    - Fast to parse
    - No narrative prose
    - Gotchas as a list
    - Minimal examples
    """
    lines: list[str] = []

    # Header with symbol and signature
    lines.append(f"## {node.symbol}")
    lines.append(f"```\n{node.signature}\n```")

    # AGENTESE path for navigation
    if node.agentese_path:
        lines.append(f"Path: {node.agentese_path}")

    # Summary as single line if present
    if node.summary:
        lines.append(f"Summary: {node.summary}")

    # Gotchas as structured list
    if node.teaching:
        gotchas = [t.insight for t in node.teaching]
        lines.append(f"Gotchas: {gotchas}")

    # First example only
    if node.examples:
        lines.append(f"Example: {node.examples[0]}")

    # Tier for context
    lines.append(f"Tier: {node.tier.value}")

    return Surface(
        content="\n".join(lines),
        format="structured",
        metadata={
            "symbol": node.symbol,
            "tier": node.tier.value,
            "gotcha_count": len(node.teaching),
            "example_count": len(node.examples),
        },
    )


def _ide_projection(node: DocNode) -> Surface:
    """
    Minimal projection for IDE tooltips.

    IDEs want:
    - Signature (always)
    - One critical gotcha (if any)
    - Very short
    """
    lines: list[str] = [node.signature]

    # Find most critical gotcha
    critical = next(
        (t for t in node.teaching if t.severity == "critical"),
        next(
            (t for t in node.teaching if t.severity == "warning"),
            node.teaching[0] if node.teaching else None,
        ),
    )

    if critical:
        # Truncate insight to fit tooltip
        insight = critical.insight
        if len(insight) > 80:
            insight = insight[:77] + "..."
        severity_icon = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}.get(critical.severity, "")
        lines.append(f"{severity_icon} {insight}")

    return Surface(
        content="\n".join(lines),
        format="tooltip",
        metadata={"symbol": node.symbol, "has_gotcha": critical is not None},
    )


def _human_projection(
    node: DocNode,
    density: Literal["compact", "comfortable", "spacious"],
) -> Surface:
    """
    Narrative projection for human readers.

    Humans want:
    - Readable narrative
    - Appropriate detail level based on density
    - Teaching moments with context
    - Examples with explanation
    """
    params = DENSITY_PARAMS[density]
    lines: list[str] = []

    # Header
    lines.append(f"## {node.symbol}")
    lines.append("")
    lines.append(f"```python\n{node.signature}\n```")

    # AGENTESE path (if available)
    if node.agentese_path:
        lines.append("")
        lines.append(f"**AGENTESE:** `{node.agentese_path}`")

    # Summary with potential truncation
    if node.summary:
        summary = node.summary
        if params.truncate_length and len(summary) > params.truncate_length:
            summary = summary[: params.truncate_length - 3] + "..."
        lines.append("")
        lines.append(summary)

    # Details section
    if params.show_details:
        # Examples
        examples_to_show = list(node.examples[: params.max_examples])
        if examples_to_show:
            lines.append("")
            lines.append("### Examples")
            for example in examples_to_show:
                lines.append(f"```python\n>>> {example}\n```")

        # Teaching moments
        if params.show_teaching and node.teaching:
            lines.append("")
            lines.append("### Things to Know")
            for moment in node.teaching:
                lines.append("")
                lines.append(_format_teaching_moment(moment))

    return Surface(
        content="\n".join(lines),
        format="markdown",
        metadata={
            "symbol": node.symbol,
            "density": density,
            "tier": node.tier.value,
        },
    )


def _format_teaching_moment(moment: TeachingMoment) -> str:
    """Format a teaching moment for human readers."""
    severity_icon = {
        "critical": "🚨 **Critical:**",
        "warning": "⚠️ **Note:**",
        "info": "ℹ️",
    }.get(moment.severity, "•")

    lines = [f"{severity_icon} {moment.insight}"]

    if moment.evidence:
        lines.append(f"  - *Verified in: `{moment.evidence}`*")

    if moment.commit:
        lines.append(f"  - *Learned in: {moment.commit[:7]}*")

    return "\n".join(lines)


# === Projector Class (for DI and composition) ===


class LivingDocsProjector:
    """
    Stateless projector for use in AGENTESE nodes.

    Wraps the project function for dependency injection.
    """

    def project(self, node: DocNode, observer: LivingDocsObserver) -> Surface:
        """Project a DocNode to a Surface."""
        return project(node, observer)

    def project_many(self, nodes: list[DocNode], observer: LivingDocsObserver) -> list[Surface]:
        """Project multiple DocNodes."""
        return [project(node, observer) for node in nodes]

    def project_with_filter(
        self,
        nodes: list[DocNode],
        observer: LivingDocsObserver,
        *,
        min_tier: Tier = Tier.MINIMAL,
        only_with_teaching: bool = False,
    ) -> list[Surface]:
        """
        Project nodes with filtering.

        Args:
            nodes: DocNodes to project
            observer: The observer
            min_tier: Minimum tier to include
            only_with_teaching: Only include nodes with teaching moments
        """
        tier_order = [Tier.MINIMAL, Tier.STANDARD, Tier.RICH]
        min_tier_idx = tier_order.index(min_tier)

        filtered = [
            n
            for n in nodes
            if tier_order.index(n.tier) >= min_tier_idx and (not only_with_teaching or n.teaching)
        ]

        return self.project_many(filtered, observer)
