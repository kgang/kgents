"""
AGENTESE Self-Judgment: SPECS-based Critique System

Implements the Critic's Loop for self-evaluation of creative output.

self.judgment.critique - Evaluate artifact against SPECS criteria
self.judgment.refine - Auto-improvement loop

Source: SPECS (Jordanous 2012) - Standardised Procedure for Evaluating Creative Systems.

Core Insight: "A generator without a critic is just a random number generator."

PAYADOR Fix (v2.5): Bidirectional Skeleton-Texture Pipeline
When critique detects structural issues (low novelty AND low utility), the system:
1. Detects that the structure is wrong (not just texture)
2. Rewrites the skeleton via LLM
3. Re-expands with new skeleton

Source: "Minimalist Approach to Grounding Language Models" (ICCC 2024)

Principle Alignment:
- Tasteful: Critique provides architectural quality assessment
- Ethical: Self-evaluation maintains agent responsibility
- Joy-Inducing: Iterative refinement improves output quality
- Composable: CriticsLoop composes with any generation aspect
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Protocol, runtime_checkable

from ..middleware.curator import structural_surprise

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from runtime.cli import ClaudeCLIRuntime


# === Critique Weights ===


@dataclass(frozen=True)
class CritiqueWeights:
    """
    Weights for combining critique scores.

    Different domains may weight criteria differently:
    - Art: novelty=0.5, utility=0.2, surprise=0.3
    - Engineering: novelty=0.2, utility=0.6, surprise=0.2
    - Science: novelty=0.35, utility=0.45, surprise=0.2

    Default balances novelty and utility equally with surprise as tie-breaker.
    """

    novelty: float = 0.4
    utility: float = 0.4
    surprise: float = 0.2

    def __post_init__(self) -> None:
        """Validate weights sum to 1.0."""
        total = self.novelty + self.utility + self.surprise
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")


# === Critique Dataclass ===


@dataclass(frozen=True)
class Critique:
    """
    SPECS-based evaluation result.

    Frozen to ensure immutability and enable hashing for caching.

    Attributes:
        novelty: 0-1: Is this new relative to prior work?
        utility: 0-1: Is this useful for the stated purpose?
        surprise: 0-1: Is this unexpected given context?
        overall: Weighted combination of above
        reasoning: Why these scores?
        suggestions: How to improve?
    """

    novelty: float
    utility: float
    surprise: float
    overall: float
    reasoning: str
    suggestions: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate scores are in valid range."""
        for name, value in [
            ("novelty", self.novelty),
            ("utility", self.utility),
            ("surprise", self.surprise),
            ("overall", self.overall),
        ]:
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0, got {value}")

    @classmethod
    def create(
        cls,
        novelty: float,
        utility: float,
        surprise: float,
        reasoning: str,
        suggestions: list[str] | tuple[str, ...],
        weights: CritiqueWeights | None = None,
    ) -> "Critique":
        """
        Create Critique with computed overall score.

        Args:
            novelty: Novelty score (0-1)
            utility: Utility score (0-1)
            surprise: Surprise score (0-1)
            reasoning: Explanation for scores
            suggestions: Improvement suggestions
            weights: Optional custom weights (defaults to balanced)

        Returns:
            Critique instance with computed overall score
        """
        w = weights or CritiqueWeights()
        overall = w.novelty * novelty + w.utility * utility + w.surprise * surprise
        return cls(
            novelty=novelty,
            utility=utility,
            surprise=surprise,
            overall=overall,
            reasoning=reasoning,
            suggestions=tuple(suggestions),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "novelty": self.novelty,
            "utility": self.utility,
            "surprise": self.surprise,
            "overall": self.overall,
            "reasoning": self.reasoning,
            "suggestions": list(self.suggestions),
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        lines = [
            f"Critique (Overall: {self.overall:.2f})",
            f"  Novelty:  {self.novelty:.2f}",
            f"  Utility:  {self.utility:.2f}",
            f"  Surprise: {self.surprise:.2f}",
            f"  Reasoning: {self.reasoning}",
        ]
        if self.suggestions:
            lines.append("  Suggestions:")
            for s in self.suggestions:
                lines.append(f"    - {s}")
        return "\n".join(lines)


# === Refinement Result ===


@dataclass(frozen=True)
class RefinedArtifact:
    """
    Result of the critique-refine loop.

    Attributes:
        artifact: The refined artifact
        final_critique: Final critique after refinement
        iterations: Number of refinement iterations performed
        history: List of (artifact, critique) pairs from each iteration
    """

    artifact: Any
    final_critique: Critique
    iterations: int
    history: tuple[tuple[Any, Critique], ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "artifact": self.artifact,
            "final_critique": self.final_critique.to_dict(),
            "iterations": self.iterations,
            "history_length": len(self.history),
        }


# === PAYADOR: Bidirectional Skeleton-Texture Types ===


class RefinementMode(Enum):
    """
    Mode of refinement for the PAYADOR bidirectional pipeline.

    - TEXTURE: Refine the surface rendering (default)
    - SKELETON: Rewrite the underlying structure
    """

    TEXTURE = "texture"
    SKELETON = "skeleton"


@dataclass(frozen=True)
class SkeletonRewriteConfig:
    """
    Configuration for skeleton rewriting via LLM.

    Attributes:
        novelty_threshold: Below this novelty score, consider skeleton rewrite
        utility_threshold: Below this utility score (combined with novelty), trigger rewrite
        temperature: LLM temperature for skeleton generation
        max_tokens: Maximum tokens for skeleton response
    """

    novelty_threshold: float = 0.3
    utility_threshold: float = 0.4
    temperature: float = 0.8
    max_tokens: int = 1024

    def __post_init__(self) -> None:
        """Validate thresholds are in valid range."""
        for name, value in [
            ("novelty_threshold", self.novelty_threshold),
            ("utility_threshold", self.utility_threshold),
        ]:
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0, got {value}")


@dataclass(frozen=True)
class Skeleton:
    """
    Structural representation of an artifact.

    The skeleton captures the high-level structure (plot points, arguments,
    sections) without surface details (prose, formatting, examples).

    Attributes:
        structure: The structural elements as a list of strings
        intent: The original purpose or goal
        constraints: Any constraints to maintain during re-expansion
    """

    structure: tuple[str, ...]
    intent: str
    constraints: tuple[str, ...] = ()

    def to_prompt(self) -> str:
        """Convert skeleton to LLM-readable format."""
        lines = [
            "## Skeleton Structure",
            "",
        ]
        for i, elem in enumerate(self.structure, 1):
            lines.append(f"{i}. {elem}")
        lines.extend(
            [
                "",
                f"## Intent: {self.intent}",
            ]
        )
        if self.constraints:
            lines.append("")
            lines.append("## Constraints:")
            for c in self.constraints:
                lines.append(f"- {c}")
        return "\n".join(lines)


# === Skeleton Agent Prompts ===


SKELETON_REWRITE_SYSTEM = """You are a structural rewriter for creative artifacts.

Given an artifact and critique, you extract and rewrite the underlying STRUCTURE (skeleton),
not the surface text (texture). The skeleton captures:
- Key points, arguments, or plot elements
- Logical organization and flow
- Core concepts that need to be communicated

You respond in JSON format with:
{
    "structure": ["point 1", "point 2", ...],
    "intent": "the core purpose of this artifact",
    "constraints": ["constraint 1", ...],
    "reasoning": "why this new structure addresses the critique"
}

Focus on STRUCTURAL changes. If the critique indicates low novelty, propose a more
novel organizational approach. If utility is low, restructure to better serve the purpose."""


def build_skeleton_rewrite_prompt(
    artifact: Any,
    critique: "Critique",
    purpose: str | None = None,
) -> str:
    """Build prompt for skeleton rewriting."""
    lines = [
        "## Current Artifact",
        str(artifact),
        "",
        "## Critique",
        f"Novelty: {critique.novelty:.2f}",
        f"Utility: {critique.utility:.2f}",
        f"Surprise: {critique.surprise:.2f}",
        f"Overall: {critique.overall:.2f}",
        f"Reasoning: {critique.reasoning}",
        "",
        "## Suggestions",
    ]
    for s in critique.suggestions:
        lines.append(f"- {s}")

    if purpose:
        lines.extend(
            [
                "",
                f"## Purpose: {purpose}",
            ]
        )

    lines.extend(
        [
            "",
            "## Task",
            "Analyze the STRUCTURAL issues in this artifact based on the critique.",
            "Propose a new skeleton (structure) that addresses the critique.",
            "Focus on reorganization and restructuring, not word-level changes.",
            "",
            'Respond with JSON: {"structure": [...], "intent": "...", '
            '"constraints": [...], "reasoning": "..."}',
        ]
    )

    return "\n".join(lines)


SKELETON_EXPAND_SYSTEM = """You are a creative writer expanding structural skeletons into full prose.

Given a skeleton (structure, intent, constraints), you generate the full artifact
that realizes this structure. Maintain the skeleton's organization while adding:
- Rich detail and examples
- Smooth transitions
- Appropriate tone and style
- Engaging prose

The output should feel natural, not like a mechanical expansion of bullet points."""


def build_skeleton_expand_prompt(
    skeleton: "Skeleton",
    original_artifact: Any | None = None,
) -> str:
    """Build prompt for skeleton expansion."""
    lines = [skeleton.to_prompt()]

    if original_artifact is not None:
        lines.extend(
            [
                "",
                "## Original Artifact (for reference, do not copy directly)",
                str(original_artifact)[:500],  # Truncate for context
            ]
        )

    lines.extend(
        [
            "",
            "## Task",
            "Expand this skeleton into a full, polished artifact.",
            "Follow the structure exactly, but make it read naturally.",
            "Respect all constraints.",
            "",
            "Provide ONLY the expanded artifact, no commentary.",
        ]
    )

    return "\n".join(lines)


def parse_skeleton_response(response: str) -> Skeleton | None:
    """Parse LLM response into a Skeleton."""
    # Try to extract JSON from response
    json_match = re.search(r"\{[^{}]*\}", response, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return Skeleton(
                structure=tuple(data.get("structure", [])),
                intent=data.get("intent", ""),
                constraints=tuple(data.get("constraints", [])),
            )
        except (json.JSONDecodeError, ValueError, KeyError):
            pass

    return None


# === Logos Protocol (for type hints) ===


@runtime_checkable
class LogosLike(Protocol):
    """Protocol for Logos-like invocation interface."""

    async def invoke(
        self,
        path: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Invoke an AGENTESE path."""
        ...


# === Critics Loop ===


@dataclass
class CriticsLoop:
    """
    Generative-Evaluative Pairing for iterative refinement.

    Implements the fundamental insight from creative AI research:
    separate generation from evaluation, then iterate.

    PAYADOR Enhancement (v2.5): Bidirectional Skeleton-Texture Pipeline
    When critique detects structural issues (low novelty AND low utility),
    the system can rewrite the underlying skeleton structure via LLM,
    rather than just refining the surface texture.

    Usage:
        loop = CriticsLoop(threshold=0.7, max_iterations=3)
        result, critique = await loop.generate_with_critique(
            logos, observer, "concept.generate.story", theme="adventure"
        )

    Or for direct critique:
        critique = await loop.critique(artifact, observer, purpose="documentation")

    For skeleton-aware refinement (requires LLM runtime):
        loop = CriticsLoop(
            skeleton_config=SkeletonRewriteConfig(),
            llm_solver=my_llm_solver,
        )
    """

    max_iterations: int = 3
    threshold: float = 0.7
    weights: CritiqueWeights = field(default_factory=CritiqueWeights)

    # PAYADOR: Skeleton rewriting configuration
    skeleton_config: SkeletonRewriteConfig | None = None
    # LLM solver for skeleton operations (optional, enables PAYADOR)
    llm_solver: Callable[[str, str], Any] | None = None

    # Configuration for assessment
    _prior_work: list[Any] = field(default_factory=list)
    # Cached purpose for skeleton operations
    _current_purpose: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("threshold must be between 0.0 and 1.0")

    async def critique(
        self,
        artifact: Any,
        observer: "Umwelt[Any, Any]",
        *,
        purpose: str | None = None,
        prior_work: list[Any] | None = None,
    ) -> Critique:
        """
        Evaluate artifact against SPECS criteria.

        Args:
            artifact: The artifact to evaluate
            observer: Observer's Umwelt (contains expectations)
            purpose: Optional purpose for utility assessment
            prior_work: Optional list of prior work for novelty comparison

        Returns:
            Critique with novelty, utility, surprise scores
        """
        # Assess each criterion
        priors = prior_work or self._prior_work
        novelty = self._assess_novelty(artifact, priors)
        utility = self._assess_utility(artifact, purpose)
        surprise = self._assess_surprise(artifact, observer)

        # Generate reasoning
        reasoning = self._generate_reasoning(novelty, utility, surprise, purpose)

        # Generate suggestions
        suggestions = self._generate_suggestions(novelty, utility, surprise)

        return Critique.create(
            novelty=novelty,
            utility=utility,
            surprise=surprise,
            reasoning=reasoning,
            suggestions=suggestions,
            weights=self.weights,
        )

    async def generate_with_critique(
        self,
        logos: LogosLike,
        observer: "Umwelt[Any, Any]",
        generator_path: str,
        *,
        purpose: str | None = None,
        **kwargs: Any,
    ) -> tuple[Any, Critique]:
        """
        Generator -> Critic -> Refine loop.

        1. Generate initial artifact via generator_path
        2. Critique it
        3. If below threshold, refine based on feedback
        4. Repeat until threshold met or max iterations

        Args:
            logos: Logos instance for invocations
            observer: Observer's Umwelt
            generator_path: AGENTESE path for generation
            purpose: Optional purpose for utility assessment
            **kwargs: Arguments for generator

        Returns:
            Tuple of (final_artifact, final_critique)
        """
        # Generate initial artifact
        result = await logos.invoke(generator_path, observer, **kwargs)

        # Iterate critique-refine loop
        for iteration in range(self.max_iterations):
            critique = await self.critique(result, observer, purpose=purpose)

            if critique.overall >= self.threshold:
                return result, critique

            # Try to refine
            try:
                refined = await self._refine_artifact(logos, observer, result, critique)
                # Check for no-progress (identical output)
                if refined == result:
                    return result, critique
                result = refined
            except Exception:
                # Refinement failed, return current best
                return result, critique

        # Max iterations reached, return best effort
        final_critique = await self.critique(result, observer, purpose=purpose)
        return result, final_critique

    async def generate_with_trace(
        self,
        logos: LogosLike,
        observer: "Umwelt[Any, Any]",
        generator_path: str,
        *,
        purpose: str | None = None,
        **kwargs: Any,
    ) -> RefinedArtifact:
        """
        Like generate_with_critique but returns full trace.

        Args:
            logos: Logos instance for invocations
            observer: Observer's Umwelt
            generator_path: AGENTESE path for generation
            purpose: Optional purpose for utility assessment
            **kwargs: Arguments for generator

        Returns:
            RefinedArtifact with full history
        """
        history: list[tuple[Any, Critique]] = []

        # Generate initial artifact
        result = await logos.invoke(generator_path, observer, **kwargs)

        # Iterate critique-refine loop
        for iteration in range(self.max_iterations):
            critique = await self.critique(result, observer, purpose=purpose)
            history.append((result, critique))

            if critique.overall >= self.threshold:
                return RefinedArtifact(
                    artifact=result,
                    final_critique=critique,
                    iterations=iteration + 1,
                    history=tuple(history),
                )

            # Try to refine
            try:
                refined = await self._refine_artifact(logos, observer, result, critique)
                if refined == result:
                    return RefinedArtifact(
                        artifact=result,
                        final_critique=critique,
                        iterations=iteration + 1,
                        history=tuple(history),
                    )
                result = refined
            except Exception:
                return RefinedArtifact(
                    artifact=result,
                    final_critique=critique,
                    iterations=iteration + 1,
                    history=tuple(history),
                )

        # Max iterations reached
        final_critique = await self.critique(result, observer, purpose=purpose)
        history.append((result, final_critique))

        return RefinedArtifact(
            artifact=result,
            final_critique=final_critique,
            iterations=self.max_iterations,
            history=tuple(history),
        )

    def add_prior_work(self, artifact: Any) -> None:
        """Add artifact to prior work for novelty comparison."""
        self._prior_work.append(artifact)

    def clear_prior_work(self) -> None:
        """Clear prior work cache."""
        self._prior_work.clear()

    # === Private Assessment Methods ===

    def _assess_novelty(
        self,
        artifact: Any,
        prior_work: list[Any],
    ) -> float:
        """
        Measure novelty relative to prior work.

        If no prior work, uses structural complexity as proxy.
        """
        if not prior_work:
            return self._structural_novelty(artifact)

        # Compute minimum distance to any prior work
        distances = [structural_surprise(artifact, prior) for prior in prior_work]
        return max(distances) if distances else 0.5

    def _assess_utility(
        self,
        artifact: Any,
        purpose: str | None,
    ) -> float:
        """
        Measure utility for stated purpose.

        Without explicit purpose, defaults to coherence check.
        """
        if not purpose:
            return self._coherence_score(artifact)

        return self._purpose_alignment(artifact, purpose)

    def _assess_surprise(
        self,
        artifact: Any,
        observer: "Umwelt[Any, Any]",
    ) -> float:
        """
        Measure surprise relative to observer's expectations.

        Uses structural surprise via Wundt Curator infrastructure.
        """
        # Get prior expectation from observer context
        prior = self._get_expectation(observer)

        if prior is None:
            return 0.5  # Neutral when no prior

        return structural_surprise(artifact, prior)

    def _structural_novelty(self, artifact: Any) -> float:
        """
        Estimate novelty from structural complexity.

        Proxy when no prior work available.
        """
        if artifact is None:
            return 0.0

        if isinstance(artifact, str):
            # Word diversity and length
            words = set(artifact.lower().split())
            length_factor = min(1.0, len(artifact) / 1000.0)
            diversity = min(1.0, len(words) / 50.0)
            return (length_factor + diversity) / 2.0

        if isinstance(artifact, dict):
            # Structural depth and breadth
            depth = self._dict_depth(artifact)
            breadth = len(artifact)
            return min(1.0, (depth * 0.2) + (breadth * 0.05))

        if isinstance(artifact, list):
            return min(1.0, len(artifact) * 0.1)

        return 0.5  # Default moderate novelty

    def _coherence_score(self, artifact: Any) -> float:
        """
        Estimate coherence/consistency of artifact.

        Proxy for utility when no purpose specified.
        """
        if artifact is None:
            return 0.0

        if isinstance(artifact, str):
            # Check for reasonable structure
            if not artifact.strip():
                return 0.1
            # Has sentences/structure
            sentences = artifact.count(".") + artifact.count("!") + artifact.count("?")
            if sentences > 0:
                return min(1.0, 0.5 + sentences * 0.05)
            return 0.4

        if isinstance(artifact, dict):
            # Non-empty dict with string keys
            if not artifact:
                return 0.2
            return min(1.0, 0.5 + len(artifact) * 0.05)

        if isinstance(artifact, list):
            if not artifact:
                return 0.2
            return min(1.0, 0.5 + len(artifact) * 0.05)

        return 0.5  # Default moderate coherence

    def _purpose_alignment(self, artifact: Any, purpose: str) -> float:
        """
        Estimate alignment between artifact and purpose.

        Simple heuristic: check for keyword overlap.
        """
        if artifact is None:
            return 0.0

        artifact_str = str(artifact).lower()
        purpose_lower = purpose.lower()

        # Extract keywords from purpose
        purpose_words = set(purpose_lower.split())
        stop_words = {"a", "an", "the", "is", "are", "to", "for", "and", "or", "of"}
        keywords = purpose_words - stop_words

        if not keywords:
            return 0.5  # No keywords to match

        # Count keyword matches
        matches = sum(1 for kw in keywords if kw in artifact_str)
        alignment = matches / len(keywords)

        # Scale: some matches = good, all matches = excellent
        return min(1.0, 0.3 + alignment * 0.7)

    def _get_expectation(self, observer: "Umwelt[Any, Any]") -> Any:
        """Get prior expectation from observer's context."""
        try:
            context = getattr(observer, "context", {})
            if isinstance(context, dict):
                expectations = context.get("expectations", {})
                if isinstance(expectations, dict):
                    return expectations.get("prior")
            return None
        except Exception:
            return None

    def _dict_depth(self, d: dict[str, Any], current: int = 0) -> int:
        """Compute maximum depth of nested dict."""
        if not isinstance(d, dict) or not d:
            return current
        depths = [
            self._dict_depth(v, current + 1) for v in d.values() if isinstance(v, dict)
        ]
        return max(depths) if depths else current + 1

    def _generate_reasoning(
        self,
        novelty: float,
        utility: float,
        surprise: float,
        purpose: str | None,
    ) -> str:
        """Generate human-readable reasoning for scores."""
        parts = []

        # Novelty assessment
        if novelty < 0.3:
            parts.append("Low novelty - similar to existing work")
        elif novelty > 0.7:
            parts.append("High novelty - significantly different from prior")
        else:
            parts.append("Moderate novelty")

        # Utility assessment
        if purpose:
            if utility < 0.3:
                parts.append(f"Low utility for purpose: '{purpose}'")
            elif utility > 0.7:
                parts.append(f"High utility for purpose: '{purpose}'")
            else:
                parts.append("Moderate utility alignment")
        else:
            if utility < 0.3:
                parts.append("Low coherence")
            elif utility > 0.7:
                parts.append("High coherence")
            else:
                parts.append("Moderate coherence")

        # Surprise assessment
        if surprise < 0.3:
            parts.append("Expected output")
        elif surprise > 0.7:
            parts.append("Surprisingly different from expectations")
        else:
            parts.append("Moderate surprise")

        return ". ".join(parts) + "."

    def _generate_suggestions(
        self,
        novelty: float,
        utility: float,
        surprise: float,
    ) -> list[str]:
        """Generate improvement suggestions based on scores."""
        suggestions: list[str] = []

        if novelty < 0.3:
            suggestions.append("Consider adding unique perspectives or approaches")
            suggestions.append("Explore less conventional solutions")

        if utility < 0.3:
            suggestions.append("Ensure output addresses the core requirements")
            suggestions.append("Add more relevant details or structure")

        if surprise < 0.3:
            suggestions.append("Try unexpected combinations or framings")

        # High surprise but low utility might need grounding
        if surprise > 0.7 and utility < 0.5:
            suggestions.append("Ground creative elements in practical constraints")

        return suggestions

    async def _refine_artifact(
        self,
        logos: LogosLike,
        observer: "Umwelt[Any, Any]",
        artifact: Any,
        critique: Critique,
    ) -> Any:
        """
        Apply critique feedback to improve artifact.

        PAYADOR Enhancement: When structural issues are detected (low novelty
        AND low utility), attempts skeleton rewriting before texture refinement.

        Flow:
        1. Check if critique suggests structural issues (_needs_skeleton_rewrite)
        2. If yes and LLM available: rewrite skeleton, then expand
        3. Otherwise: delegate to concept.refine.apply
        4. Fallback: return artifact unchanged
        """
        # PAYADOR: Check for structural issues requiring skeleton rewrite
        if self._needs_skeleton_rewrite(critique):
            try:
                rewritten = await self._rewrite_with_skeleton(artifact, critique)
                if rewritten is not None and rewritten != artifact:
                    return rewritten
            except Exception:
                # Skeleton rewrite failed, fall through to texture refinement
                pass

        # Texture refinement: delegate to concept.refine.apply
        try:
            return await logos.invoke(
                "concept.refine.apply",
                observer,
                input=artifact,
                feedback=critique.to_dict(),
                suggestions=list(critique.suggestions),
            )
        except Exception:
            # Fallback: return artifact unchanged
            # Real refinement requires LLM or domain-specific logic
            return artifact

    # === PAYADOR: Bidirectional Skeleton-Texture Methods ===

    def _needs_skeleton_rewrite(self, critique: Critique) -> bool:
        """
        Determine if critique indicates structural (skeleton) issues.

        The PAYADOR insight: when BOTH novelty AND utility are low,
        the problem is likely structural, not just surface-level.
        Texture refinement won't help - we need to rewrite the skeleton.

        Args:
            critique: The critique of the current artifact

        Returns:
            True if skeleton rewrite is recommended
        """
        # No skeleton config = no skeleton rewriting
        if self.skeleton_config is None:
            return False

        # No LLM solver = can't do skeleton rewriting
        if self.llm_solver is None:
            return False

        config = self.skeleton_config

        # PAYADOR condition: low novelty AND low utility
        # This indicates the structure itself is problematic
        structural_issue = (
            critique.novelty < config.novelty_threshold
            and critique.utility < config.utility_threshold
        )

        return structural_issue

    def _determine_refinement_mode(self, critique: Critique) -> RefinementMode:
        """
        Determine whether to refine texture or rewrite skeleton.

        Args:
            critique: The critique of the current artifact

        Returns:
            RefinementMode indicating the type of refinement needed
        """
        if self._needs_skeleton_rewrite(critique):
            return RefinementMode.SKELETON
        return RefinementMode.TEXTURE

    async def _rewrite_with_skeleton(
        self,
        artifact: Any,
        critique: Critique,
    ) -> Any | None:
        """
        Rewrite artifact via skeleton rewrite then expansion.

        PAYADOR bidirectional flow:
        1. Extract/rewrite skeleton from artifact based on critique
        2. Expand skeleton back to full artifact

        Args:
            artifact: The current artifact
            critique: Critique indicating structural issues

        Returns:
            New artifact, or None if rewrite failed
        """
        if self.llm_solver is None:
            return None

        # Step 1: Rewrite skeleton
        skeleton = await self._rewrite_skeleton(artifact, critique)
        if skeleton is None:
            return None

        # Step 2: Expand skeleton to new artifact
        return await self._expand_skeleton(skeleton, artifact)

    async def _rewrite_skeleton(
        self,
        artifact: Any,
        critique: Critique,
    ) -> Skeleton | None:
        """
        Use LLM to rewrite the structural skeleton based on critique.

        Args:
            artifact: The current artifact
            critique: Critique with structural issues

        Returns:
            New Skeleton, or None if rewrite failed
        """
        if self.llm_solver is None:
            return None

        # Build prompt for skeleton rewriting
        user_prompt = build_skeleton_rewrite_prompt(
            artifact, critique, self._current_purpose
        )

        try:
            # Call LLM solver
            response = await self._call_llm(SKELETON_REWRITE_SYSTEM, user_prompt)
            return parse_skeleton_response(response)
        except Exception:
            return None

    async def _expand_skeleton(
        self,
        skeleton: Skeleton,
        original_artifact: Any | None = None,
    ) -> Any:
        """
        Expand a skeleton back into a full artifact.

        Args:
            skeleton: The skeleton to expand
            original_artifact: Optional original for style reference

        Returns:
            Expanded artifact as string
        """
        if self.llm_solver is None:
            # Without LLM, return skeleton as structured text
            return skeleton.to_prompt()

        # Build expansion prompt
        user_prompt = build_skeleton_expand_prompt(skeleton, original_artifact)

        try:
            response = await self._call_llm(SKELETON_EXPAND_SYSTEM, user_prompt)
            return response.strip()
        except Exception:
            # Fallback: return skeleton as text
            return skeleton.to_prompt()

    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Call the LLM solver with system and user prompts.

        Args:
            system_prompt: System prompt for LLM
            user_prompt: User prompt with task

        Returns:
            LLM response string
        """
        if self.llm_solver is None:
            raise RuntimeError("No LLM solver configured")

        # The llm_solver is expected to be async and take (system, user) prompts
        import asyncio

        if asyncio.iscoroutinefunction(self.llm_solver):
            result = await self.llm_solver(system_prompt, user_prompt)
        else:
            result = self.llm_solver(system_prompt, user_prompt)

        return str(result)


# === PAYADOR: Helper Functions ===
# Define these before revise_skeleton so they can be used


def critique_suggests_structure_change(critique: Critique) -> bool:
    """
    Check if critique suggests the issue is structural.

    PAYADOR condition: low novelty AND low utility indicates
    the skeleton itself needs rewriting, not just texture polish.
    """
    return critique.novelty < 0.3 and critique.utility < 0.4


def critique_structural_issues(critique: Critique) -> list[str]:
    """
    Extract structural issues from critique suggestions.

    Filters suggestions to those that indicate structural problems.
    """
    structural_keywords = [
        "reorganiz",
        "restructur",
        "reorder",
        "approach",
        "perspective",
        "structure",
        "organization",
        "flow",
        "logic",
    ]

    issues: list[str] = []
    for suggestion in critique.suggestions:
        suggestion_lower = suggestion.lower()
        if any(keyword in suggestion_lower for keyword in structural_keywords):
            issues.append(suggestion)

    # If no explicit structural issues but PAYADOR condition met, add generic
    if not issues and critique.novelty < 0.3 and critique.utility < 0.4:
        issues.append("Structure may need fundamental reorganization")

    return issues


# === PAYADOR: High-Level API ===


async def revise_skeleton(
    skeleton: Skeleton,
    critique: Critique,
    llm_solver: Callable[[str, str], Any] | None = None,
) -> Skeleton:
    """
    PAYADOR: When texture reveals structural issues, rewrite the skeleton.

    This function implements the "bidirectional" part of the PAYADOR pipeline.
    When critique detects that the problem is structural (not surface-level),
    we regenerate the skeleton rather than trying to polish prose.

    The key insight from "Minimalist Approach to Grounding Language Models" (ICCC 2024):
    texture-to-structure feedback catches issues that forward-only generation misses.

    Args:
        skeleton: The current skeleton structure
        critique: The critique indicating structural issues
        llm_solver: Optional LLM solver (system_prompt, user_prompt) -> response
                   If None, performs rule-based restructuring

    Returns:
        New Skeleton with revised structure addressing the critique

    Example:
        # Without LLM - rule-based restructuring
        new_skeleton = await revise_skeleton(skeleton, critique)

        # With LLM - uses LLM for intelligent restructuring
        new_skeleton = await revise_skeleton(skeleton, critique, llm_solver=my_llm)
    """
    if not critique_suggests_structure_change(critique):
        # No structural change needed
        return skeleton

    # If LLM solver available, use it for intelligent restructuring
    if llm_solver is not None:
        # Build prompt for skeleton revision
        user_prompt = _build_revision_prompt(skeleton, critique)
        try:
            import asyncio

            if asyncio.iscoroutinefunction(llm_solver):
                response = await llm_solver(SKELETON_REWRITE_SYSTEM, user_prompt)
            else:
                response = llm_solver(SKELETON_REWRITE_SYSTEM, user_prompt)

            new_skeleton = parse_skeleton_response(str(response))
            if new_skeleton is not None:
                return new_skeleton
        except Exception:
            pass  # Fall through to rule-based restructuring

    # Rule-based restructuring (fallback or when no LLM)
    return _rule_based_restructure(skeleton, critique)


def _build_revision_prompt(skeleton: Skeleton, critique: Critique) -> str:
    """Build prompt for skeleton revision based on critique."""
    lines = [
        "## Current Skeleton",
        skeleton.to_prompt(),
        "",
        "## Critique",
        f"Novelty: {critique.novelty:.2f}",
        f"Utility: {critique.utility:.2f}",
        f"Surprise: {critique.surprise:.2f}",
        f"Overall: {critique.overall:.2f}",
        f"Reasoning: {critique.reasoning}",
        "",
        "## Issues Identified",
    ]

    for issue in critique_structural_issues(critique):
        lines.append(f"- {issue}")

    lines.extend(
        [
            "",
            "## Task",
            "Revise the skeleton structure to address the identified issues.",
            "Focus on structural reorganization, not surface changes.",
            "",
            'Respond with JSON: {"structure": [...], "intent": "...", '
            '"constraints": [...], "reasoning": "..."}',
        ]
    )

    return "\n".join(lines)


def _rule_based_restructure(skeleton: Skeleton, critique: Critique) -> Skeleton:
    """
    Apply rule-based restructuring when LLM is unavailable.

    Rules applied:
    - Low novelty (< 0.3): Reorder elements to create new perspective
    - Low utility (< 0.4): Add purpose-alignment constraints
    - Combine above: Split long elements, merge redundant ones
    """
    new_structure = list(skeleton.structure)
    new_constraints = list(skeleton.constraints)

    # Low novelty: Reorder to create new perspective
    if critique.novelty < 0.3 and len(new_structure) > 2:
        # Move later elements earlier (different perspective)
        mid = len(new_structure) // 2
        new_structure = new_structure[mid:] + new_structure[:mid]

    # Low utility: Add purpose-alignment constraint
    if critique.utility < 0.4 and skeleton.intent:
        constraint = f"Each element must directly serve: {skeleton.intent}"
        if constraint not in new_constraints:
            new_constraints.append(constraint)

    # Both low: Split complex elements
    if critique.novelty < 0.3 and critique.utility < 0.4:
        expanded: list[str] = []
        for elem in new_structure:
            # Split elements with conjunctions
            if " and " in elem.lower():
                parts = elem.split(" and ")
                expanded.extend(part.strip() for part in parts if part.strip())
            else:
                expanded.append(elem)
        new_structure = expanded

    return Skeleton(
        structure=tuple(new_structure),
        intent=skeleton.intent,
        constraints=tuple(new_constraints),
    )


# === Critique Extensions for PAYADOR ===


# Monkey-patch Critique class with PAYADOR methods as properties
# Using a property descriptor that delegates to the standalone functions
class _SuggestsStructureChangeDescriptor:
    """Property descriptor for Critique.suggests_structure_change."""

    def __get__(
        self, obj: Critique | None, objtype: type[Critique] | None = None
    ) -> bool:
        if obj is None:
            return False
        return critique_suggests_structure_change(obj)


class _StructuralIssuesDescriptor:
    """Property descriptor for Critique.structural_issues."""

    def __get__(
        self, obj: Critique | None, objtype: type[Critique] | None = None
    ) -> list[str]:
        if obj is None:
            return []
        return critique_structural_issues(obj)


# Attach descriptors to Critique
Critique.suggests_structure_change = _SuggestsStructureChangeDescriptor()  # type: ignore[attr-defined]
Critique.structural_issues = _StructuralIssuesDescriptor()  # type: ignore[attr-defined]


# === Exports ===

__all__ = [
    "Critique",
    "CritiqueWeights",
    "CriticsLoop",
    "RefinedArtifact",
    # PAYADOR types
    "RefinementMode",
    "Skeleton",
    "SkeletonRewriteConfig",
    # PAYADOR prompt builders (for testing/extension)
    "build_skeleton_rewrite_prompt",
    "build_skeleton_expand_prompt",
    "parse_skeleton_response",
    # PAYADOR high-level API (v2.5)
    "revise_skeleton",
]
