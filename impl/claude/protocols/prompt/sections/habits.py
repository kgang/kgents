"""
Habits Section Compiler: Dynamic section based on learned developer patterns.

The most adaptive section in the prompt (rigidity ~0.1).

Uses the HabitEncoder to analyze developer patterns from:
- Git history
- Session logs
- Code patterns

And generates recommendations that influence the prompt.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from ..section_base import (
    NPhase,
    Section,
    SectionCompiler,
    estimate_tokens,
    run_sync,
)
from ..soft_section import MergeStrategy, SoftSection
from ..sources.base import SectionSource, SourcePriority, SourceResult

if TYPE_CHECKING:
    from ..compiler import CompilationContext

logger = logging.getLogger(__name__)


class HabitSource(SectionSource):
    """
    Source that generates content from learned habits.

    Uses HabitEncoder to analyze patterns and PolicyVector to
    generate recommendations.
    """

    def __init__(self, repo_path: Path | None = None):
        self.repo_path = repo_path

    @property
    def name(self) -> str:
        return "habit_encoder"

    @property
    def priority(self) -> SourcePriority:
        return SourcePriority.PRIMARY

    @property
    def rigidity(self) -> float:
        return 0.1  # Very adaptive

    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """Fetch habits from HabitEncoder."""
        traces: list[str] = ["Fetching learned habits..."]

        try:
            from ..habits import HabitEncoder, HabitEncoderConfig

            repo_path = self.repo_path or context.repo_path
            if not repo_path or not repo_path.exists():
                traces.append("  No repository path, skipping habits")
                return SourceResult.failure(
                    source_name=self.name,
                    reason="No repository path available",
                    traces=tuple(traces),
                )

            # Create encoder with default config
            config = HabitEncoderConfig(
                git_enabled=True,
                session_enabled=True,
                code_enabled=True,
            )
            encoder = HabitEncoder(repo_path=repo_path, config=config)

            # Encode habits
            policy = encoder.encode()
            traces.append(f"  Encoded {len(policy.learned_from)} sources")
            traces.extend(f"    {t}" for t in policy.reasoning_trace[:5])

            # Generate section content
            content = self._format_policy(policy)
            traces.append(f"  Generated {len(content)} chars of habits content")

            return SourceResult.success(
                source_name=self.name,
                content=content,
                source_path=repo_path,
                traces=tuple(traces),
            )

        except ImportError as e:
            traces.append(f"  Import error: {e}")
            return SourceResult.failure(
                source_name=self.name,
                reason=f"HabitEncoder not available: {e}",
                traces=tuple(traces),
            )
        except Exception as e:
            traces.append(f"  Error: {e}")
            logger.warning(f"Habit encoding failed: {e}")
            return SourceResult.failure(
                source_name=self.name,
                reason=str(e),
                traces=tuple(traces),
            )

    def _format_policy(self, policy: "PolicyVector") -> str:
        """Format PolicyVector as markdown content."""
        from ..habits import PolicyVector

        lines: list[str] = []

        # Style preferences
        lines.append("### Learned Style Preferences")
        lines.append("")

        verbosity_desc = (
            "verbose"
            if policy.verbosity > 0.6
            else "concise"
            if policy.verbosity < 0.4
            else "balanced"
        )
        formality_desc = (
            "formal"
            if policy.formality > 0.7
            else "casual"
            if policy.formality < 0.4
            else "moderate"
        )
        risk_desc = (
            "experimental"
            if policy.risk_tolerance > 0.6
            else "conservative"
            if policy.risk_tolerance < 0.3
            else "balanced"
        )

        lines.append(f"- **Verbosity**: {verbosity_desc} ({policy.verbosity:.0%})")
        lines.append(f"- **Formality**: {formality_desc} ({policy.formality:.0%})")
        lines.append(f"- **Risk tolerance**: {risk_desc} ({policy.risk_tolerance:.0%})")
        lines.append("")

        # Domain focus
        if policy.domain_focus:
            lines.append("### Focus Areas")
            lines.append("")
            for domain, focus in sorted(policy.domain_focus, key=lambda x: -x[1])[:5]:
                lines.append(f"- **{domain}**: {focus:.0%}")
            lines.append("")

        # Section weights (if non-default)
        if policy.section_weights:
            lines.append("### Section Priorities")
            lines.append("")
            for section, weight in sorted(policy.section_weights, key=lambda x: -x[1])[
                :5
            ]:
                lines.append(f"- {section}: {weight:.0%}")
            lines.append("")

        # Metadata
        lines.append("### Source Information")
        lines.append("")
        lines.append(f"- Sources: {', '.join(policy.learned_from)}")
        lines.append(f"- Confidence: {policy.confidence:.0%}")
        if policy.generated_at:
            lines.append(f"- Generated: {policy.generated_at.isoformat()[:19]}")

        return "\n".join(lines)


class HabitsSectionCompiler:
    """
    Compile the habits section from learned patterns.

    This section has very low rigidity (0.1) meaning it changes
    frequently based on developer behavior.
    """

    @property
    def name(self) -> str:
        return "habits"

    @property
    def required(self) -> bool:
        return False  # Optional section

    @property
    def phases(self) -> frozenset[NPhase]:
        return frozenset()  # All phases

    @property
    def rigidity(self) -> float:
        return 0.1  # Most adaptive section

    def compile(self, context: "CompilationContext") -> Section:
        """Compile habits section using SoftSection."""
        # Create soft section with habit source
        soft = self._create_soft_section(context)

        # Crystallize synchronously
        result = run_sync(soft.crystallize(context))

        return result.section

    def _create_soft_section(self, context: "CompilationContext") -> SoftSection:
        """Create a SoftSection for habits."""
        sources: list[SectionSource] = []

        # Primary: HabitEncoder
        sources.append(HabitSource(repo_path=context.repo_path))

        # Fallback: Template
        sources.append(_FallbackHabitSource())

        return SoftSection(
            name=self.name,
            sources=tuple(sources),
            merge_strategy=MergeStrategy.FIRST_WINS,
            required=self.required,
            phases=self.phases,
        )

    def estimate_tokens(self) -> int:
        """Estimate token cost."""
        return 300  # Rough estimate


class _FallbackHabitSource(SectionSource):
    """Fallback source when habits can't be encoded."""

    @property
    def name(self) -> str:
        return "habit_fallback"

    @property
    def priority(self) -> SourcePriority:
        return SourcePriority.FALLBACK

    @property
    def rigidity(self) -> float:
        return 0.8  # Template is rigid

    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """Return fallback content."""
        content = """### Learned Preferences

*No habits encoded yet. The system will learn your preferences from:*

- Git commit patterns
- Claude Code session history
- Code style analysis

*These influence prompt generation over time.*
"""
        return SourceResult.success(
            source_name=self.name,
            content=content,
            traces=("Using fallback habit content",),
        )


__all__ = [
    "HabitsSectionCompiler",
    "HabitSource",
]
