"""
Hydration Context Generator for Claude Code Sessions

Generates task-relevant context from Living Docs for Claude Code sessions,
replacing ad-hoc context gathering with structured, observer-dependent projection.

AGENTESE: concept.docs.hydrate

Usage:
    from services.living_docs import hydrate_context

    # Generate context for a task
    context = hydrate_context("implement wasm projector")
    print(context.to_markdown())

    # Or via CLI
    # kg docs hydrate "implement wasm projector"

Teaching:
    gotcha: hydrate_context() is keyword-based, not semantic.
            Use Brain vectors for semantic similarity (future work).
            (Evidence: test_hydrator.py::test_keyword_matching)

    gotcha: Voice anchors are curated, not mined.
            They come from _focus.md, not git history.
            (Evidence: test_hydrator.py::test_voice_anchors)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator

from .teaching import TeachingCollector, TeachingResult

if TYPE_CHECKING:
    from services.brain.persistence import BrainPersistence

    from .brain_adapter import ASHCEvidence, HydrationBrainAdapter, ScoredTeachingResult
    from .types import DocNode

logger = logging.getLogger(__name__)


# Voice anchors from _focus.md — Kent's authentic voice
# These phrases should be preserved, never paraphrased
VOICE_ANCHORS: list[str] = [
    '"Daring, bold, creative, opinionated but not gaudy"',
    '"The Mirror Test: Does K-gent feel like me on my best day?"',
    '"Tasteful > feature-complete"',
    '"Joy-inducing > merely functional"',
    '"The persona is a garden, not a museum"',
    '"Depth over breadth"',
]


@dataclass
class HydrationContext:
    """
    Context blob optimized for Claude Code sessions.

    The docs don't describe the code. The docs compile context for the observer.
    This class is the compiled context for the "task-focused Claude" observer.

    Enhanced with semantic fields (Checkpoint 0.2):
    - semantic_teaching: Teaching moments from Brain vectors
    - prior_evidence: ASHC evidence for similar work (Phase 2)
    - ancestral_wisdom: Ghost teaching from deleted code (Memory-First Docs)

    Teaching:
        gotcha: to_markdown() output is designed for system prompts.
                It's not a reference doc—it's a focus lens.
                (Evidence: test_hydrator.py::test_markdown_format)
    """

    task: str
    relevant_teaching: list[TeachingResult] = field(default_factory=list)
    related_modules: list[str] = field(default_factory=list)
    voice_anchors: list[str] = field(default_factory=list)
    # Semantic enhancements (Checkpoint 0.2)
    # Note: semantic_teaching contains ScoredTeachingResult from brain_adapter
    semantic_teaching: list[Any] = field(default_factory=list)
    prior_evidence: list[Any] = field(default_factory=list)  # ASHCEvidence when Phase 2
    has_semantic: bool = False
    # Ghost hydration (Memory-First Docs Phase 4)
    ancestral_wisdom: list[Any] = field(default_factory=list)  # GhostWisdom from deleted code
    extinct_modules: list[str] = field(default_factory=list)  # Modules that no longer exist

    def to_markdown(self) -> str:
        """
        Render as markdown suitable for system prompt or /hydrate.

        Output is optimized for Claude Code consumption:
        - Gotchas first (avoid mistakes)
        - Modules second (what to look at)
        - Voice anchors last (how to communicate)
        """
        lines: list[str] = []

        # Header
        lines.append(f"# Hydration Context: {self.task}")
        lines.append("")

        # Combine keyword and semantic teaching moments
        all_teaching = list(self.relevant_teaching)

        # Add semantic teaching with source marker
        for t in self.semantic_teaching:
            # Avoid duplicates by checking insight
            if not any(existing.moment.insight == t.moment.insight for existing in all_teaching):
                all_teaching.append(t)

        # Teaching moments (gotchas)
        if all_teaching:
            header = "## Relevant Gotchas"
            if self.has_semantic:
                header += " 🧠"  # Brain icon indicates semantic matching was used
            lines.append(header)
            lines.append("")

            # Group by severity
            critical = [t for t in all_teaching if t.moment.severity == "critical"]
            warning = [t for t in all_teaching if t.moment.severity == "warning"]
            info = [t for t in all_teaching if t.moment.severity == "info"]

            if critical:
                lines.append("### 🚨 Critical")
                for t in critical[:5]:  # Top 5 per severity
                    lines.append(f"- **{t.symbol}**: {t.moment.insight}")
                    if t.moment.evidence:
                        lines.append(f"  - Evidence: `{t.moment.evidence}`")
                lines.append("")

            if warning:
                lines.append("### ⚠️ Warning")
                for t in warning[:5]:
                    lines.append(f"- **{t.symbol}**: {t.moment.insight}")
                lines.append("")

            if info:
                lines.append("### ℹ️ Info")
                for t in info[:5]:
                    lines.append(f"- **{t.symbol}**: {t.moment.insight}")
                lines.append("")

        # Prior evidence from ASHC (Phase 2)
        if self.prior_evidence:
            lines.append("## Prior Evidence (ASHC)")
            lines.append("")
            for ev in self.prior_evidence[:3]:
                lines.append(
                    f"- **{ev.task_pattern}**: {ev.run_count} runs, {ev.pass_rate:.0%} pass rate"
                )
                if ev.causal_insights:
                    for insight in ev.causal_insights[:2]:
                        lines.append(f"  - {insight}")
            lines.append("")

        # Ancestral wisdom from deleted code (Memory-First Docs Phase 4)
        if self.ancestral_wisdom:
            lines.append("## \u26b0\ufe0f Ancestral Wisdom (From Deleted Code)")
            lines.append("")
            lines.append("These modules no longer exist but their lessons persist:")
            lines.append("")

            # Group by source module
            by_module: dict[str, list[Any]] = {}
            for ghost in self.ancestral_wisdom:
                module = ghost.teaching.source_module
                if module not in by_module:
                    by_module[module] = []
                by_module[module].append(ghost)

            for module, ghosts in list(by_module.items())[:5]:  # Top 5 modules
                first_ghost = ghosts[0]
                lines.append(f"### `{module}`")
                if first_ghost.extinction_event:
                    lines.append(f"*Reason: {first_ghost.extinction_event.reason}*")
                if first_ghost.successor:
                    lines.append(f"*Replaced by: `{first_ghost.successor}`*")
                lines.append("")

                for ghost in ghosts[:3]:  # Top 3 per module
                    icon = {
                        "critical": "\U0001f6a8",
                        "warning": "\u26a0\ufe0f",
                        "info": "\u2139\ufe0f",
                    }.get(ghost.teaching.severity, "\u2022")
                    lines.append(
                        f"- {icon} **{ghost.teaching.source_symbol}**: {ghost.teaching.insight}"
                    )
                lines.append("")

        # Related modules
        if self.related_modules:
            lines.append("## Files You'll Likely Touch")
            lines.append("")
            for module in self.related_modules[:10]:  # Top 10
                lines.append(f"- `{module}`")
            lines.append("")

        # Voice anchors
        if self.voice_anchors:
            lines.append("## Voice Anchors (Preserve These)")
            lines.append("")
            for anchor in self.voice_anchors:
                lines.append(f"- {anchor}")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append(f"*Context compiled for: {self.task}*")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for JSON serialization."""
        return {
            "task": self.task,
            "relevant_teaching": [
                {
                    "symbol": t.symbol,
                    "module": t.module,
                    "insight": t.moment.insight,
                    "severity": t.moment.severity,
                    "evidence": t.moment.evidence,
                }
                for t in self.relevant_teaching
            ],
            "semantic_teaching": [
                {
                    "symbol": t.symbol,
                    "module": t.module,
                    "insight": t.moment.insight,
                    "severity": t.moment.severity,
                    "evidence": t.moment.evidence,
                    "score": t.score,
                }
                for t in self.semantic_teaching
            ],
            "prior_evidence": [
                ev.to_dict() if hasattr(ev, "to_dict") else ev for ev in self.prior_evidence
            ],
            "ancestral_wisdom": [
                {
                    "insight": g.teaching.insight,
                    "severity": g.teaching.severity,
                    "source_module": g.teaching.source_module,
                    "source_symbol": g.teaching.source_symbol,
                    "successor": g.successor,
                    "extinction_reason": g.extinction_event.reason if g.extinction_event else None,
                }
                for g in self.ancestral_wisdom
            ],
            "extinct_modules": self.extinct_modules,
            "related_modules": self.related_modules,
            "voice_anchors": self.voice_anchors,
            "has_semantic": self.has_semantic,
        }


class Hydrator:
    """
    Generate task-relevant context for Claude Code sessions.

    Uses keyword matching against teaching moments and module paths.
    Enhanced with Brain semantic search (Checkpoint 0.2).

    Teaching:
        gotcha: Hydrator prefers keyword matching; Brain is supplemental.
                Semantic matching is best-effort—graceful degradation if unavailable.
                (Evidence: test_hydrator.py::test_keyword_extraction)
    """

    def __init__(
        self,
        base_path: Path | None = None,
        collector: TeachingCollector | None = None,
        brain_adapter: "HydrationBrainAdapter | None" = None,
    ):
        self._base_path = base_path or Path(__file__).parent.parent.parent
        self._collector = collector or TeachingCollector(base_path=base_path)
        self._brain_adapter = brain_adapter

    def hydrate(self, task: str) -> HydrationContext:
        """
        Generate hydration context for a task (sync version).

        Uses keyword matching only. For semantic matching, use hydrate_async().

        Args:
            task: Natural language description of the task

        Returns:
            HydrationContext with relevant gotchas, modules, and voice anchors
        """
        keywords = self._extract_keywords(task)

        # Find relevant teaching moments (keyword-based)
        relevant_teaching = list(self._find_relevant_teaching(keywords))

        # Find related modules
        related_modules = list(self._find_related_modules(keywords))

        # Select applicable voice anchors
        voice_anchors = self._select_voice_anchors(task)

        return HydrationContext(
            task=task,
            relevant_teaching=relevant_teaching,
            related_modules=related_modules,
            voice_anchors=voice_anchors,
            has_semantic=False,
        )

    async def hydrate_async(self, task: str) -> HydrationContext:
        """
        Generate hydration context with semantic enhancement.

        Enhanced with Brain vectors when available. Falls back to
        keyword matching if Brain is unavailable.

        Args:
            task: Natural language description of the task

        Returns:
            HydrationContext with keyword + semantic gotchas
        """
        # Start with keyword-based context
        context = self.hydrate(task)

        # Enhance with Brain semantic search if available
        if self._brain_adapter and self._brain_adapter.is_available:
            try:
                semantic_result = await self._brain_adapter.semantic_hydrate(task)

                context = HydrationContext(
                    task=context.task,
                    relevant_teaching=context.relevant_teaching,
                    related_modules=context.related_modules,
                    voice_anchors=context.voice_anchors,
                    semantic_teaching=semantic_result.get("semantic_teaching", []),
                    prior_evidence=semantic_result.get("prior_evidence", []),
                    has_semantic=True,
                )
                logger.debug(
                    f"Enhanced hydration with {len(context.semantic_teaching)} "
                    f"semantic teaching moments"
                )
            except Exception as e:
                # Graceful degradation: log and return keyword-only context
                logger.warning(f"Semantic hydration failed, using keyword-only: {e}")

        return context

    async def hydrate_with_ghosts(
        self,
        task: str,
        brain: "BrainPersistence",
    ) -> HydrationContext:
        """
        Hydrate context including ancestral wisdom from deleted code.

        AGENTESE: concept.docs.hydrate (with ghost section)

        The Ghost Hydration Law: Hydration MUST surface wisdom
        from extinct code when relevant.

        Args:
            task: Natural language description of the task
            brain: BrainPersistence instance for querying extinct wisdom

        Returns:
            HydrationContext with ancestral wisdom when task matches

        Teaching:
            gotcha: Ghost hydration is keyword-based, not semantic.
                    Keywords from task are matched against extinct teaching insights.
                    (Evidence: test_ghost_hydration.py::test_keyword_matching)
        """
        # Start with regular hydration
        context = self.hydrate(task)

        # Extract keywords for ghost matching
        keywords = self._extract_keywords(task)

        # Query for ghost matches
        try:
            ghosts = await brain.get_extinct_wisdom(keywords=keywords)

            if ghosts:
                # Create new context with ghosts
                context = HydrationContext(
                    task=context.task,
                    relevant_teaching=context.relevant_teaching,
                    related_modules=context.related_modules,
                    voice_anchors=context.voice_anchors,
                    semantic_teaching=context.semantic_teaching,
                    prior_evidence=context.prior_evidence,
                    has_semantic=context.has_semantic,
                    ancestral_wisdom=ghosts,
                    extinct_modules=list(set(g.teaching.source_module for g in ghosts)),
                )
                logger.debug(f"Enhanced hydration with {len(ghosts)} ancestral wisdom entries")

        except Exception as e:
            # Graceful degradation: log and return without ghosts
            logger.warning(f"Ghost hydration failed, continuing without: {e}")

        return context

    def _extract_keywords(self, task: str) -> list[str]:
        """
        Extract keywords from task description.

        Simple tokenization with stop word removal.
        Semantic extraction is future work.
        """
        # Stop words to ignore
        stop_words = {
            "a",
            "an",
            "the",
            "and",
            "or",
            "but",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "to",
            "for",
            "of",
            "in",
            "on",
            "at",
            "by",
            "with",
            "about",
            "from",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "up",
            "down",
            "out",
            "off",
            "over",
            "under",
            "again",
            "further",
            "then",
            "once",
            "here",
            "there",
            "when",
            "where",
            "why",
            "how",
            "all",
            "each",
            "every",
            "both",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "just",
            "also",
            "now",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "my",
            "your",
            "his",
            "its",
            "our",
            "their",
            "what",
            "which",
            "who",
            "whom",
            "implement",
            "add",
            "create",
            "build",
            "make",
            "fix",
            "update",
            "change",
            "new",
            "please",
            "help",
        }

        # Tokenize (alphanumeric + underscore)
        import re

        tokens = re.findall(r"\w+", task.lower())

        # Filter and deduplicate
        keywords = []
        seen = set()
        for token in tokens:
            if token not in stop_words and token not in seen and len(token) > 2:
                keywords.append(token)
                seen.add(token)

        return keywords

    def _find_relevant_teaching(self, keywords: list[str]) -> Iterator[TeachingResult]:
        """
        Find teaching moments relevant to keywords (sync, from docstrings).

        Matches against:
        - module path
        - symbol name
        - insight text

        NOTE: This is the legacy path. Prefer hydrate_from_brain() for
        unified hydration that queries Brain instead of re-extracting.
        """
        if not keywords:
            return

        # Collect all teaching moments
        all_results = list(self._collector.collect_all())

        # Score and rank
        scored: list[tuple[int, TeachingResult]] = []
        for result in all_results:
            score = 0

            # Check module path
            module_lower = result.module.lower()
            for kw in keywords:
                if kw in module_lower:
                    score += 3  # Module match is high signal

            # Check symbol name
            symbol_lower = result.symbol.lower()
            for kw in keywords:
                if kw in symbol_lower:
                    score += 2  # Symbol match is medium signal

            # Check insight text
            insight_lower = result.moment.insight.lower()
            for kw in keywords:
                if kw in insight_lower:
                    score += 1  # Insight match is low signal

            if score > 0:
                scored.append((score, result))

        # Sort by score descending, take top 15
        scored.sort(key=lambda x: x[0], reverse=True)
        for _, result in scored[:15]:
            yield result

    async def _find_relevant_teaching_from_brain(
        self,
        keywords: list[str],
        brain: "BrainPersistence",
    ) -> list[TeachingResult]:
        """
        Find teaching moments from Brain (async, unified hydration).

        AGENTESE: concept.docs.hydrate (unified path)

        This is the new unified path that queries Brain's crystallized
        teaching moments instead of re-extracting from docstrings.

        Args:
            keywords: Keywords to search for
            brain: BrainPersistence instance

        Returns:
            List of TeachingResult converted from TeachingCrystal
        """
        if not keywords:
            return []

        crystals = await brain.query_teaching_by_keywords(keywords)
        return [self._crystal_to_result(c) for c in crystals]

    def _crystal_to_result(self, crystal: Any) -> TeachingResult:
        """Convert a TeachingCrystal to TeachingResult for compatibility."""
        from .types import TeachingMoment

        # Create TeachingMoment from crystal fields
        moment = TeachingMoment(
            severity=crystal.severity
            if crystal.severity in ("critical", "warning", "info")
            else "info",
            insight=crystal.insight,
            evidence=crystal.evidence,
            commit=crystal.source_commit,
        )

        return TeachingResult(
            moment=moment,
            symbol=crystal.source_symbol,
            module=crystal.source_module,
            source_path=None,  # Not available from crystal
        )

    async def hydrate_from_brain(self, task: str, brain: "BrainPersistence") -> HydrationContext:
        """
        Generate hydration context from Brain (unified path).

        AGENTESE: concept.docs.hydrate (via Brain)

        This is the primary hydration path for AD-017 unified Living Docs.
        Queries Brain's crystallized teaching instead of re-extracting
        from docstrings on every call.

        Args:
            task: Natural language description of the task
            brain: BrainPersistence instance

        Returns:
            HydrationContext with teaching from Brain

        Teaching:
            gotcha: This method requires teaching crystals to be bootstrapped.
                    Run bootstrap_teaching_crystals.py first.
                    (Evidence: test_unified_hydration.py::test_requires_bootstrap)
        """
        keywords = self._extract_keywords(task)

        # Query Brain for teaching moments
        relevant_teaching = await self._find_relevant_teaching_from_brain(keywords, brain)

        # Query for ghost wisdom (ancestral teaching from deleted code)
        ghosts = await brain.get_extinct_wisdom(keywords=keywords)

        # Find related modules from the teaching results
        related_modules = list(set(t.module for t in relevant_teaching))

        # Select applicable voice anchors
        voice_anchors = self._select_voice_anchors(task)

        return HydrationContext(
            task=task,
            relevant_teaching=relevant_teaching,
            related_modules=related_modules,
            voice_anchors=voice_anchors,
            has_semantic=False,  # Brain query is keyword-based for now
            ancestral_wisdom=ghosts,
            extinct_modules=list(set(g.teaching.source_module for g in ghosts)) if ghosts else [],
        )

    def _find_related_modules(self, keywords: list[str]) -> Iterator[str]:
        """
        Find modules related to keywords.

        Uses teaching moment modules as proxy for "important" modules.
        """
        if not keywords:
            return

        # Get unique modules from teaching moments
        modules_seen: set[str] = set()
        for result in self._collector.collect_all():
            if result.module not in modules_seen:
                module_lower = result.module.lower()
                for kw in keywords:
                    if kw in module_lower:
                        modules_seen.add(result.module)
                        yield result.module
                        break

    def _select_voice_anchors(self, task: str) -> list[str]:
        """
        Select voice anchors relevant to the task.

        For now, returns the general-purpose anchors.
        Task-specific selection is future work.
        """
        # Simple heuristics for now
        task_lower = task.lower()

        selected = []

        # Always include the mirror test for implementation tasks
        if any(word in task_lower for word in ["implement", "build", "create", "add"]):
            selected.append(VOICE_ANCHORS[1])  # Mirror Test

        # Always include tasteful > feature-complete
        selected.append(VOICE_ANCHORS[2])  # Tasteful

        # If joy/delight mentioned, include joy anchor
        if any(word in task_lower for word in ["joy", "delight", "fun", "happy"]):
            selected.append(VOICE_ANCHORS[3])  # Joy-inducing

        # If garden/evolve mentioned, include garden anchor
        if any(word in task_lower for word in ["garden", "evolve", "grow", "cultivate"]):
            selected.append(VOICE_ANCHORS[4])  # Garden

        # Default: return first 3 if nothing else selected
        if not selected:
            selected = VOICE_ANCHORS[:3]

        return selected


# ============================================================================
# Convenience Function (Preferred API)
# ============================================================================


def hydrate_context(task: str) -> HydrationContext:
    """
    Generate hydration context for a task.

    This is the main entry point for generating task-relevant context
    for Claude Code sessions.

    Args:
        task: Natural language description of the task

    Returns:
        HydrationContext with relevant gotchas, modules, and voice anchors

    Usage:
        from services.living_docs import hydrate_context

        # For a task
        ctx = hydrate_context("implement wasm projector")
        print(ctx.to_markdown())

        # For file editing
        ctx = hydrate_context("edit services/brain/persistence.py")
        for t in ctx.relevant_teaching:
            print(f"⚠️ {t.moment.insight}")
    """
    hydrator = Hydrator()
    return hydrator.hydrate(task)


def relevant_for_file(path: str) -> HydrationContext:
    """
    Get relevant context for editing a specific file.

    Convenience wrapper around hydrate_context for file-focused work.

    Args:
        path: Path to the file being edited

    Returns:
        HydrationContext with gotchas relevant to that file

    Usage:
        from services.living_docs import relevant_for_file

        ctx = relevant_for_file("services/brain/persistence.py")
        for t in ctx.relevant_teaching:
            print(f"🚨 {t.symbol}: {t.moment.insight}")
    """
    # Extract meaningful keywords from path
    parts = path.replace("/", " ").replace("_", " ").replace(".py", "").split()
    task = f"edit {' '.join(parts)}"
    return hydrate_context(task)


async def hydrate_context_with_ghosts(task: str) -> HydrationContext:
    """
    Generate hydration context including ancestral wisdom.

    This is the async entry point for Memory-First Documentation.
    Surfaces wisdom from deleted code when relevant to the task.

    Args:
        task: Natural language description of the task

    Returns:
        HydrationContext with ancestral wisdom when matches found

    Usage:
        import asyncio
        from services.living_docs import hydrate_context_with_ghosts

        ctx = asyncio.run(hydrate_context_with_ghosts("town dialogue"))
        if ctx.ancestral_wisdom:
            print("Ancestral wisdom found!")
            for ghost in ctx.ancestral_wisdom:
                print(f"  {ghost.teaching.insight}")
    """
    try:
        from protocols.agentese.container import get_container

        container = get_container()
        brain = await container.resolve("brain_persistence")

        hydrator = Hydrator()
        return await hydrator.hydrate_with_ghosts(task, brain)
    except Exception as e:
        # Graceful degradation: return basic context
        logger.warning(f"Failed to get brain for ghost hydration: {e}")
        return hydrate_context(task)


async def hydrate_from_brain(task: str) -> HydrationContext:
    """
    Generate hydration context from Brain (AD-017 unified path).

    This is the PREFERRED hydration path. Queries Brain's crystallized
    teaching moments instead of re-extracting from docstrings.

    REQUIRES: Run bootstrap_teaching_crystals.py first to populate Brain.

    Args:
        task: Natural language description of the task

    Returns:
        HydrationContext with teaching from Brain + ancestral wisdom

    Usage:
        import asyncio
        from services.living_docs import hydrate_from_brain

        ctx = asyncio.run(hydrate_from_brain("implement brain search"))
        print(ctx.to_markdown())

    Teaching:
        gotcha: Falls back to docstring extraction if Brain is unavailable.
                This preserves functionality but loses the unified guarantee.
                (Evidence: test_unified_hydration.py::test_fallback)
    """
    try:
        from protocols.agentese.container import get_container

        container = get_container()
        brain = await container.resolve("brain_persistence")

        hydrator = Hydrator()
        return await hydrator.hydrate_from_brain(task, brain)
    except Exception as e:
        # Graceful degradation: fall back to docstring extraction
        logger.warning(f"Failed to hydrate from Brain, using docstrings: {e}")
        return hydrate_context(task)
