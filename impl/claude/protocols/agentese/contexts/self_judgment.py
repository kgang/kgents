"""
AGENTESE Self-Judgment: SPECS-based Critique System

Implements the Critic's Loop for self-evaluation of creative output.

self.judgment.critique - Evaluate artifact against SPECS criteria
self.judgment.refine - Auto-improvement loop

Source: SPECS (Jordanous 2012) - Standardised Procedure for Evaluating Creative Systems.

Core Insight: "A generator without a critic is just a random number generator."

Principle Alignment:
- Tasteful: Critique provides architectural quality assessment
- Ethical: Self-evaluation maintains agent responsibility
- Joy-Inducing: Iterative refinement improves output quality
- Composable: CriticsLoop composes with any generation aspect
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from ..middleware.curator import structural_surprise

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


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

    Usage:
        loop = CriticsLoop(threshold=0.7, max_iterations=3)
        result, critique = await loop.generate_with_critique(
            logos, observer, "concept.generate.story", theme="adventure"
        )

    Or for direct critique:
        critique = await loop.critique(artifact, observer, purpose="documentation")
    """

    max_iterations: int = 3
    threshold: float = 0.7
    weights: CritiqueWeights = field(default_factory=CritiqueWeights)

    # Configuration for assessment
    _prior_work: list[Any] = field(default_factory=list)

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

        Delegates to concept.refine.apply if available.
        Falls back to simple modification for basic types.
        """
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


# === Exports ===

__all__ = [
    "Critique",
    "CritiqueWeights",
    "CriticsLoop",
    "RefinedArtifact",
]
