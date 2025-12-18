"""
Context Section: Dynamic session context for the prompt.

The Context section provides real-time information about:
- Git status (branch, working tree)
- Current N-Phase (if set)
- Session metadata

This is a "soft" section (rigidity ~0.3) because it changes
frequently based on user activity.

This section is typically placed near the top of the prompt
to give immediate situational awareness.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from ..section_base import NPhase, Section, estimate_tokens, run_sync
from ..soft_section import MergeStrategy, SoftSection
from ..sources.base import SectionSource, SourcePriority, SourceResult, TemplateSource
from ..sources.git_source import GitBranchSource, GitSource

if TYPE_CHECKING:
    from ..compiler import CompilationContext

logger = logging.getLogger(__name__)


# =============================================================================
# Phase Source: Extract N-Phase info from context
# =============================================================================


@dataclass
class PhaseSource(SectionSource):
    """
    Source that provides current N-Phase information.

    Reads from CompilationContext.current_phase and formats
    it for inclusion in the prompt.
    """

    name: str = "context:phase"
    priority: SourcePriority = field(default=SourcePriority.MEMORY)
    rigidity: float = 0.5  # Medium - set per session

    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """Get current phase information."""
        traces = ["PhaseSource: Checking current phase"]

        phase = context.current_phase
        if phase is None:
            traces.append("No phase set in context")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        # Format phase name nicely
        phase_name = phase.name.replace("_", " ").title()
        traces.append(f"Current phase: {phase_name}")

        # Phase descriptions
        phase_descriptions = {
            NPhase.PLAN: "Defining scope and approach",
            NPhase.RESEARCH: "Investigating and exploring options",
            NPhase.DEVELOP: "Building core functionality",
            NPhase.STRATEGIZE: "Determining priorities and ordering",
            NPhase.CROSS_SYNERGIZE: "Finding connections across domains",
            NPhase.IMPLEMENT: "Writing production code",
            NPhase.QA: "Testing and quality assurance",
            NPhase.TEST: "Running test suites",
            NPhase.EDUCATE: "Documenting and teaching",
            NPhase.MEASURE: "Gathering metrics and feedback",
            NPhase.REFLECT: "Reviewing and synthesizing learnings",
        }

        description = phase_descriptions.get(phase, "")
        traces.append(f"Description: {description}")

        content = f"**Current Phase**: {phase_name}"
        if description:
            content += f" — *{description}*"

        return SourceResult(
            content=content,
            success=True,
            source_name=self.name,
            reasoning_trace=tuple(traces),
            rigidity=self.rigidity,
        )


@dataclass
class SessionSource(SectionSource):
    """
    Source that provides session metadata.

    Includes timestamp and any session-specific context.
    """

    name: str = "context:session"
    priority: SourcePriority = field(default=SourcePriority.MEMORY)
    rigidity: float = 0.3  # Soft - changes every compilation

    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """Generate session metadata."""
        traces = ["SessionSource: Generating session info"]

        timestamp = datetime.now()
        traces.append(f"Timestamp: {timestamp.isoformat()}")

        # Format as concise metadata
        parts = [f"**Session**: {timestamp.strftime('%Y-%m-%d %H:%M')}"]

        # Add focus intent if set
        if context.focus_intent:
            parts.append(f"**Focus**: {context.focus_intent}")
            traces.append(f"Focus intent: {context.focus_intent}")

        # Add pressure budget if not default
        if context.pressure_budget < 1.0:
            pressure_pct = int(context.pressure_budget * 100)
            parts.append(f"**Budget**: {pressure_pct}%")
            traces.append(f"Pressure budget: {pressure_pct}%")

        content = " | ".join(parts)
        traces.append(f"Built session info: {len(content)} chars")

        return SourceResult(
            content=content,
            success=True,
            source_name=self.name,
            reasoning_trace=tuple(traces),
            rigidity=self.rigidity,
        )


@dataclass
class CombinedContextSource(SectionSource):
    """
    Source that combines git, phase, and session context.

    Produces a compact context block suitable for prompt headers.
    """

    name: str = "context:combined"
    priority: SourcePriority = field(default=SourcePriority.GIT)
    rigidity: float = 0.4  # Average of components
    include_git: bool = True
    include_phase: bool = True
    include_session: bool = True

    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """Gather and combine all context sources."""
        traces = ["CombinedContextSource: Gathering context"]

        parts: list[str] = []

        # Git branch (compact)
        if self.include_git and (context.project_root / ".git").exists():
            git_source = GitBranchSource()
            git_result = await git_source.fetch(context)
            if git_result.success and git_result.content:
                parts.append(git_result.content)
                traces.extend(git_result.reasoning_trace)

        # Phase
        if self.include_phase:
            phase_source = PhaseSource()
            phase_result = await phase_source.fetch(context)
            if phase_result.success and phase_result.content:
                parts.append(phase_result.content)
                traces.extend(phase_result.reasoning_trace)

        # Session
        if self.include_session:
            session_source = SessionSource()
            session_result = await session_source.fetch(context)
            if session_result.success and session_result.content:
                parts.append(session_result.content)
                traces.extend(session_result.reasoning_trace)

        if not parts:
            traces.append("No context available")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        # Build compact context block
        content = self._build_content(parts, traces)

        return SourceResult(
            content=content,
            success=True,
            source_name=self.name,
            reasoning_trace=tuple(traces),
            rigidity=self.rigidity,
        )

    def _build_content(self, parts: list[str], traces: list[str]) -> str:
        """Build the combined context content."""
        lines = ["## Session Context"]
        lines.append("")
        lines.append(" | ".join(parts))
        lines.append("")

        traces.append(f"Built combined context: {len(parts)} components")
        return "\n".join(lines)


# =============================================================================
# Context Section Compiler
# =============================================================================


class ContextSectionCompiler:
    """
    Compile the Context section.

    Uses SoftSection with multiple context sources.
    This is one of the softest sections (rigidity ~0.3) since
    it changes with every compilation.
    """

    FALLBACK_CONTENT = """## Session Context

*Context unavailable.*
"""

    @property
    def name(self) -> str:
        return "context"

    @property
    def required(self) -> bool:
        return False  # Optional - can be omitted under pressure

    @property
    def phases(self) -> frozenset[NPhase]:
        return frozenset()  # Relevant to all phases

    def compile(self, context: "CompilationContext") -> Section:
        """
        Compile context section synchronously.

        Uses run_sync() for safe async execution from sync context.
        This handles event loop detection properly for both CLI
        and async framework usage (Wave 3 P1 fix).
        """
        soft = self._create_soft_section()
        result = run_sync(soft.crystallize(context))
        return result.section.with_reasoning(result.reasoning_trace)

    def _create_soft_section(self) -> SoftSection:
        """Create the SoftSection with sources."""
        from ..sources.base import FallbackSource

        return SoftSection(
            name=self.name,
            sources=[
                CombinedContextSource(),
                # Use FallbackSource (priority=0) so CombinedContextSource is tried first
                FallbackSource(
                    name=f"{self.name}:fallback",
                    fallback_message=self.FALLBACK_CONTENT,
                ),
            ],
            merge_strategy=MergeStrategy.FIRST_WINS,
            required=self.required,
            default_rigidity=0.3,
        )

    def estimate_tokens(self) -> int:
        """Estimate token cost for budget planning."""
        return 100  # Context section is compact


# =============================================================================
# Full Git Context Section (Optional - More Detailed)
# =============================================================================


class GitContextSectionCompiler:
    """
    Compile a detailed Git context section.

    This is a more detailed version that includes:
    - Full working tree status
    - Recent commits
    - Modified file list

    Use this when detailed git context is valuable.
    """

    FALLBACK_CONTENT = """## Git Context

*Not in a git repository.*
"""

    @property
    def name(self) -> str:
        return "git_context"

    @property
    def required(self) -> bool:
        return False

    @property
    def phases(self) -> frozenset[NPhase]:
        return frozenset()

    def compile(self, context: "CompilationContext") -> Section:
        """
        Compile detailed git context section.

        Uses run_sync() for safe async execution (Wave 3 P1 fix).
        """
        soft = self._create_soft_section()
        result = run_sync(soft.crystallize(context))
        return result.section.with_reasoning(result.reasoning_trace)

    def _create_soft_section(self) -> SoftSection:
        """Create the SoftSection with GitSource."""
        from ..sources.base import FallbackSource

        return SoftSection(
            name=self.name,
            sources=[
                GitSource(),  # Full git status
                # Use FallbackSource (priority=0) so GitSource is tried first
                FallbackSource(
                    name=f"{self.name}:fallback",
                    fallback_message=self.FALLBACK_CONTENT,
                ),
            ],
            merge_strategy=MergeStrategy.FIRST_WINS,
            required=self.required,
            default_rigidity=0.5,
        )

    def estimate_tokens(self) -> int:
        """Estimate token cost for budget planning."""
        return 250  # Detailed git context is larger


# =============================================================================
# Utility Functions
# =============================================================================


def create_context_soft_section() -> SoftSection:
    """
    Create a SoftSection for the Context section.

    Useful for direct async usage outside the compiler.
    """
    from ..sources.base import FallbackSource

    return SoftSection(
        name="context",
        sources=[
            CombinedContextSource(),
            # Use FallbackSource (priority=0) so CombinedContextSource is tried first
            FallbackSource(
                name="context:fallback",
                fallback_message=ContextSectionCompiler.FALLBACK_CONTENT,
            ),
        ],
        merge_strategy=MergeStrategy.FIRST_WINS,
        required=False,
        default_rigidity=0.3,
    )


__all__ = [
    "PhaseSource",
    "SessionSource",
    "CombinedContextSource",
    "ContextSectionCompiler",
    "GitContextSectionCompiler",
    "create_context_soft_section",
]
