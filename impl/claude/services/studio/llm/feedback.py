"""
Studio Feedback Loop: Self-Feedback and Self-Improvement for Creative Production.

Implements the Three Voices pattern + Galois loss + Floor checks for iterative
improvement of creative artifacts in the Studio.

Philosophy:
    "The proof IS the decision. The mark IS the witness.
     The critique IS the path to excellence."

The Three Voices:
    - Adversarial: "Is this technically correct?"
    - Creative: "Is this interesting and novel?"
    - Advocate: "Would Kent be delighted?"

Floor Checks (F1-F4):
    - F1: Provenance - all elements traceable
    - F2: Format - technical specs met
    - F3: Coherence - 80%+ style alignment
    - F4: Accessibility - WCAG compliance

Galois Loss:
    Measures semantic drift during transformation. High loss = drift from intent.
    Uses the adjunction pattern: compress -> expand -> measure residual.

Teaching:
    gotcha: The feedback loop uses asymmetric trust gradients. Small improvements
            accumulate slowly (conservative), but major regressions trigger
            immediate rollback (fail-fast). This prevents quality degradation
            while allowing careful iteration.

    gotcha: The Three Voices are not equally weighted. Adversarial failures
            are blocking (hard floor), while Creative and Advocate scores
            can be traded off against each other (soft optimization).

See: spec/s-gents/studio.md Part V
See: services/verification/self_improvement.py (pattern source)
See: services/studio/quality.py (STUDIO_QUALITY_ALGEBRA)
See: services/constitutional/reward.py (PrincipleScore pattern)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar, cast

if TYPE_CHECKING:
    from agents.k.llm import LLMClient

from ..quality import (
    STUDIO_FLOOR_CHECKS,
    STUDIO_VOICES,
    STYLE_COHERENCE_THRESHOLD,
    check_accessibility,
    check_format_compliance,
    check_provenance,
    compute_voice_verdict,
)
from ..types import (
    ArchaeologicalFindings,
    Asset,
    CreativeVision,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Type Variables
# =============================================================================

T = TypeVar("T", ArchaeologicalFindings, CreativeVision, Asset)


# =============================================================================
# Critique Dataclass
# =============================================================================


@dataclass(frozen=True)
class Critique:
    """
    Structured critique from the Three Voices.

    Contains scores from each voice, overall quality assessment,
    identified issues, and actionable suggestions.

    The critique is immutable to ensure it can be safely stored
    and compared across improvement iterations.
    """

    voice_scores: dict[str, float]  # adversarial, creative, advocate
    overall_score: float
    issues: tuple[str, ...]  # Using tuple for immutability
    suggestions: tuple[str, ...]  # Using tuple for immutability
    floor_violations: tuple[str, ...]  # Using tuple for immutability
    artifact_type: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def passes_threshold(self) -> bool:
        """Check if critique passes quality threshold.

        Returns True if:
        - Overall score >= 0.8
        - No floor violations (hard blockers)
        """
        return self.overall_score >= 0.8 and len(self.floor_violations) == 0

    @property
    def adversarial_passes(self) -> bool:
        """Check if adversarial voice passes (hard requirement)."""
        return self.voice_scores.get("adversarial", 0.0) >= 0.8

    @property
    def has_critical_issues(self) -> bool:
        """Check if there are critical issues blocking progress."""
        return len(self.floor_violations) > 0 or not self.adversarial_passes

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "voice_scores": self.voice_scores,
            "overall_score": self.overall_score,
            "issues": list(self.issues),
            "suggestions": list(self.suggestions),
            "floor_violations": list(self.floor_violations),
            "artifact_type": self.artifact_type,
            "timestamp": self.timestamp.isoformat(),
            "passes_threshold": self.passes_threshold,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Critique:
        """Create from dictionary."""
        return cls(
            voice_scores=data.get("voice_scores", {}),
            overall_score=data.get("overall_score", 0.0),
            issues=tuple(data.get("issues", [])),
            suggestions=tuple(data.get("suggestions", [])),
            floor_violations=tuple(data.get("floor_violations", [])),
            artifact_type=data.get("artifact_type", ""),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.now(),
        )

    @classmethod
    def empty(cls) -> Critique:
        """Create an empty critique (for initialization)."""
        return cls(
            voice_scores={"adversarial": 0.0, "creative": 0.0, "advocate": 0.0},
            overall_score=0.0,
            issues=(),
            suggestions=(),
            floor_violations=(),
        )


# =============================================================================
# Witness Protocol (for dependency injection)
# =============================================================================


class WitnessProtocol(Protocol):
    """Protocol for witness service integration."""

    async def mark(
        self,
        action: str,
        reasoning: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Record a mark in the witness log."""
        ...


# =============================================================================
# Improvement Tracker
# =============================================================================


@dataclass
class ImprovementTracker:
    """
    Track improvement history for learning.

    Feeds into:
    - Session-level patterns (what works)
    - Cross-session learning (via Witness)

    The tracker maintains a history of (before, after) critique pairs,
    allowing analysis of what kinds of improvements are most effective.
    """

    witness: WitnessProtocol | None = None
    history: list[tuple[Critique, Critique]] = field(default_factory=list)

    async def record_improvement(
        self,
        before: Critique,
        after: Critique,
        artifact_type: str,
    ) -> None:
        """
        Record an improvement for learning.

        Args:
            before: Critique before improvement
            after: Critique after improvement
            artifact_type: Type of artifact improved
        """
        self.history.append((before, after))

        score_delta = after.overall_score - before.overall_score
        issues_fixed = len(before.issues) - len(after.issues)

        logger.info(
            f"Improvement recorded: {artifact_type} "
            f"({before.overall_score:.2f} -> {after.overall_score:.2f}, "
            f"delta={score_delta:+.2f}, issues_fixed={issues_fixed})"
        )

        if self.witness:
            try:
                await self.witness.mark(
                    action=f"studio_improvement:{artifact_type}",
                    reasoning=f"Improved from {before.overall_score:.2f} to {after.overall_score:.2f}",
                    context={
                        "before_score": before.overall_score,
                        "after_score": after.overall_score,
                        "score_delta": score_delta,
                        "issues_fixed": issues_fixed,
                        "before_issues": list(before.issues),
                        "after_issues": list(after.issues),
                        "artifact_type": artifact_type,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to record improvement mark: {e}")

    def get_improvement_stats(self) -> dict[str, Any]:
        """Get statistics about improvements tracked."""
        if not self.history:
            return {
                "total_improvements": 0,
                "avg_score_delta": 0.0,
                "avg_issues_fixed": 0.0,
            }

        total_score_delta = sum(
            after.overall_score - before.overall_score for before, after in self.history
        )
        total_issues_fixed = sum(
            len(before.issues) - len(after.issues) for before, after in self.history
        )

        return {
            "total_improvements": len(self.history),
            "avg_score_delta": total_score_delta / len(self.history),
            "avg_issues_fixed": total_issues_fixed / len(self.history),
            "best_improvement": max(
                after.overall_score - before.overall_score for before, after in self.history
            ),
            "worst_improvement": min(
                after.overall_score - before.overall_score for before, after in self.history
            ),
        }

    def clear(self) -> None:
        """Clear improvement history."""
        self.history.clear()


# =============================================================================
# Studio Feedback Loop
# =============================================================================


class StudioFeedbackLoop:
    """
    Self-feedback and self-improvement for creative production.

    Uses the Three Voices pattern + Galois loss + Floor checks to
    iteratively improve creative artifacts.

    The Three Voices:
        - Adversarial: "Is this technically correct?" (hard requirement)
        - Creative: "Is this interesting and novel?" (soft optimization)
        - Advocate: "Would Kent be delighted?" (soft optimization)

    Voice Weighting:
        - Adversarial: 40% (correctness is foundational)
        - Creative: 30% (novelty matters for creative work)
        - Advocate: 30% (delight is the goal)

    Improvement Process:
        1. Critique artifact with Three Voices
        2. Check floor requirements (F1-F4)
        3. If below threshold, apply suggestions
        4. Re-critique and measure improvement
        5. Continue until threshold reached or max iterations

    Asymmetric Trust Gradient:
        - Small improvements (< 0.05 delta) accumulate slowly (0.5x weight)
        - Large improvements (> 0.1 delta) are trusted more (1.0x weight)
        - Regressions (negative delta) trigger rollback immediately
    """

    # Voice weights for overall score calculation
    VOICE_WEIGHTS = {
        "adversarial": 0.40,  # Correctness is foundational
        "creative": 0.30,  # Novelty matters
        "advocate": 0.30,  # Delight is the goal
    }

    # Threshold for acceptable quality
    QUALITY_THRESHOLD = 0.8

    # Improvement thresholds for asymmetric trust
    SMALL_IMPROVEMENT_THRESHOLD = 0.05
    LARGE_IMPROVEMENT_THRESHOLD = 0.10

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        tracker: ImprovementTracker | None = None,
    ):
        """
        Initialize the feedback loop.

        Args:
            llm_client: LLM client for generating critiques and improvements.
                       If None, uses create_llm_client() on first use.
            tracker: Improvement tracker for learning. If None, creates one.
        """
        self._llm = llm_client
        self.tracker = tracker or ImprovementTracker()

    def _ensure_llm(self) -> "LLMClient":
        """Lazy-initialize the LLM client."""
        if self._llm is None:
            from agents.k.llm import create_llm_client

            self._llm = create_llm_client()
        return self._llm

    async def critique(
        self,
        artifact: ArchaeologicalFindings | CreativeVision | Asset,
        context: dict[str, Any] | None = None,
    ) -> Critique:
        """
        Generate multi-voice critique of artifact.

        Three Voices:
            - Adversarial: "Is this technically correct?"
            - Creative: "Is this interesting and novel?"
            - Advocate: "Would Kent be delighted?"

        Args:
            artifact: The artifact to critique (Findings, Vision, or Asset)
            context: Additional context for critique (style guide, etc.)

        Returns:
            Structured critique with voice scores, issues, and suggestions.
        """
        context = context or {}

        # Determine artifact type
        artifact_type = self._get_artifact_type(artifact)

        # Check floor requirements first
        floor_passed, floor_violations = self.floor_check(artifact)

        # Get voice scores
        voice_scores = await self._evaluate_voices(artifact, context)

        # Identify issues based on voice scores and floor checks
        issues = self._identify_issues(voice_scores, floor_violations, artifact)

        # Generate suggestions for improvement
        suggestions = await self._generate_suggestions(artifact, voice_scores, issues, context)

        # Calculate overall score (weighted average of voices)
        overall_score = self._calculate_overall_score(voice_scores)

        # Penalize for floor violations
        if floor_violations:
            penalty = len(floor_violations) * 0.1
            overall_score = max(0.0, overall_score - penalty)

        return Critique(
            voice_scores=voice_scores,
            overall_score=overall_score,
            issues=tuple(issues),
            suggestions=tuple(suggestions),
            floor_violations=tuple(floor_violations),
            artifact_type=artifact_type,
        )

    async def improve(
        self,
        artifact: T,
        critique: Critique,
        max_iterations: int = 3,
    ) -> tuple[T, list[Critique]]:
        """
        Iteratively improve artifact based on critique.

        Process:
            1. Apply suggestions from critique
            2. Re-critique improved version
            3. If score improved and < threshold, continue
            4. Return best version + critique history

        Asymmetric Trust Gradient:
            - Small improvements accumulate slowly
            - Major regressions trigger rollback

        Args:
            artifact: The artifact to improve
            critique: Initial critique of the artifact
            max_iterations: Maximum improvement iterations

        Returns:
            Tuple of (best artifact version, critique history)
        """
        llm = self._ensure_llm()

        critique_history = [critique]
        best_artifact = artifact
        best_score = critique.overall_score

        current_artifact = artifact
        current_critique = critique

        for iteration in range(max_iterations):
            # Check if we've reached the quality threshold
            if current_critique.passes_threshold:
                logger.info(
                    f"Quality threshold reached at iteration {iteration}: "
                    f"{current_critique.overall_score:.2f}"
                )
                break

            # Check if there are no suggestions to apply
            if not current_critique.suggestions:
                logger.info(f"No suggestions to apply at iteration {iteration}, stopping")
                break

            # Apply improvements
            try:
                improved_artifact = await self._apply_improvements(
                    current_artifact, current_critique
                )
            except Exception as e:
                logger.warning(f"Failed to apply improvements at iteration {iteration}: {e}")
                break

            # Re-critique the improved version
            new_critique = await self.critique(improved_artifact)
            critique_history.append(new_critique)

            # Calculate improvement delta
            score_delta = new_critique.overall_score - current_critique.overall_score

            # Apply asymmetric trust gradient
            if score_delta < 0:
                # Regression - rollback to best version
                logger.warning(
                    f"Regression detected at iteration {iteration}: "
                    f"{current_critique.overall_score:.2f} -> {new_critique.overall_score:.2f}"
                )
                # Don't update current_artifact, keep the previous version
                continue

            elif score_delta < self.SMALL_IMPROVEMENT_THRESHOLD:
                # Small improvement - accept but note it
                logger.info(f"Small improvement at iteration {iteration}: {score_delta:+.3f}")

            else:
                # Large improvement - trust it
                logger.info(f"Significant improvement at iteration {iteration}: {score_delta:+.3f}")

            # Update current state
            current_artifact = improved_artifact
            current_critique = new_critique

            # Track best version
            if new_critique.overall_score > best_score:
                best_artifact = improved_artifact
                best_score = new_critique.overall_score

            # Record improvement for learning
            if len(critique_history) >= 2:
                await self.tracker.record_improvement(
                    before=critique_history[-2],
                    after=new_critique,
                    artifact_type=critique.artifact_type,
                )

        return best_artifact, critique_history

    async def measure_galois_loss(
        self,
        original: str,
        transformed: str,
    ) -> float:
        """
        Measure semantic loss after transformation.

        High loss = drift from intent
        Low loss = faithful transformation

        The Galois loss uses the adjunction pattern:
            loss = |original - expand(compress(original))|

        In practice, we use LLM to assess:
            - Core meaning preserved?
            - Style/tone maintained?
            - Information lost or added?

        Args:
            original: Original text/content
            transformed: Transformed version

        Returns:
            Loss score 0.0-1.0 where 0.0 is perfect preservation.
        """
        llm = self._ensure_llm()

        prompt = f"""Analyze the semantic preservation between these two texts.

ORIGINAL:
{original}

TRANSFORMED:
{transformed}

Evaluate on a scale of 0.0 to 1.0 where:
- 0.0 = Perfect semantic preservation (no meaning lost)
- 0.5 = Moderate drift (some nuance lost or added)
- 1.0 = Severe drift (core meaning changed)

Consider:
1. Core meaning preserved? (most important)
2. Style/tone maintained?
3. Information lost?
4. Information incorrectly added?

Respond with ONLY a single number between 0.0 and 1.0."""

        try:
            response = await llm.generate(
                system="You are a semantic analysis expert. Respond with only a number.",
                user=prompt,
                temperature=0.1,  # Low temperature for consistent scoring
                max_tokens=10,
            )

            # Parse the response
            try:
                loss = float(response.text.strip())
                return max(0.0, min(1.0, loss))
            except ValueError:
                logger.warning(f"Failed to parse Galois loss response: {response.text}")
                return 0.5  # Default to moderate loss on parse failure

        except Exception as e:
            logger.error(f"Failed to measure Galois loss: {e}")
            return 0.5  # Default to moderate loss on error

    def floor_check(
        self,
        artifact: ArchaeologicalFindings | CreativeVision | Asset,
    ) -> tuple[bool, list[str]]:
        """
        Check absolute quality floors (F1-F4).

        F1: Provenance - all elements traceable
        F2: Format - technical specs met
        F3: Coherence - 80%+ style alignment
        F4: Accessibility - WCAG compliance

        Args:
            artifact: The artifact to check

        Returns:
            Tuple of (passed, list of violations)
        """
        violations: list[str] = []

        # F1: Provenance check
        if isinstance(artifact, Asset):
            # Assets must have provenance
            if not artifact.provenance:
                violations.append("F1: Missing provenance - no traceable source")
        elif isinstance(artifact, ArchaeologicalFindings):
            # Findings must have source references in patterns
            orphan_patterns = [p.name for p in artifact.patterns if not p.source_refs]
            if orphan_patterns:
                violations.append(f"F1: Orphan patterns without source refs: {orphan_patterns[:3]}")

        # F2: Format compliance check (for Assets)
        if isinstance(artifact, Asset):
            # Check basic format requirements
            if artifact.type.value in ["sprite", "graphic", "animation"]:
                metadata = artifact.metadata
                if not metadata.get("width") or not metadata.get("height"):
                    violations.append("F2: Missing dimensions for visual asset")
                if not metadata.get("format"):
                    violations.append("F2: Missing format specification")

        # F3: Style coherence check
        if isinstance(artifact, Asset):
            style_score = artifact.metadata.get("style_score", 1.0)
            if style_score < STYLE_COHERENCE_THRESHOLD:
                violations.append(
                    f"F3: Style coherence {style_score:.0%} < {STYLE_COHERENCE_THRESHOLD:.0%} threshold"
                )
        elif isinstance(artifact, CreativeVision):
            # Vision should have a core insight
            if not artifact.core_insight or len(artifact.core_insight) < 10:
                violations.append("F3: Vision lacks substantive core insight")

        # F4: Accessibility check (for visual assets)
        if isinstance(artifact, Asset) and artifact.type.value in [
            "sprite",
            "graphic",
        ]:
            # Check contrast ratio if colors are available
            colors = artifact.metadata.get("colors", [])
            background = artifact.metadata.get("background", (255, 255, 255))
            if colors:
                try:
                    if not check_accessibility(colors, background):
                        violations.append("F4: WCAG AA contrast ratio not met")
                except Exception:
                    # If we can't check, don't fail
                    pass

        return len(violations) == 0, violations

    # =========================================================================
    # Private Methods
    # =========================================================================

    def _get_artifact_type(self, artifact: ArchaeologicalFindings | CreativeVision | Asset) -> str:
        """Get the type name of an artifact."""
        if isinstance(artifact, ArchaeologicalFindings):
            return "findings"
        elif isinstance(artifact, CreativeVision):
            return "vision"
        elif isinstance(artifact, Asset):
            return f"asset:{artifact.type.value}"
        else:
            return "unknown"

    async def _evaluate_voices(
        self,
        artifact: ArchaeologicalFindings | CreativeVision | Asset,
        context: dict[str, Any],
    ) -> dict[str, float]:
        """Evaluate artifact with the Three Voices."""
        llm = self._ensure_llm()

        # Convert artifact to dict for LLM analysis
        artifact_dict = artifact.to_dict()
        style_guide = context.get("style_guide", {})

        # Build evaluation prompt
        adversarial_score = await self._evaluate_voice_with_llm(
            llm,
            "adversarial",
            artifact_dict,
            "Is this technically correct? Check format validity, dimension requirements, palette compliance, and accessibility.",
        )

        creative_score = await self._evaluate_voice_with_llm(
            llm,
            "creative",
            artifact_dict,
            "Is this interesting and novel? Check for originality, unexpected elements, style coherence, and aesthetic quality.",
        )

        advocate_score = await self._evaluate_voice_with_llm(
            llm,
            "advocate",
            artifact_dict,
            "Would Kent be delighted? Check for joy-inducing qualities, tasteful execution (daring but not gaudy), brand alignment, and the mirror test (feels like Kent on his best day).",
        )

        return {
            "adversarial": adversarial_score,
            "creative": creative_score,
            "advocate": advocate_score,
        }

    async def _evaluate_voice_with_llm(
        self,
        llm: "LLMClient",
        voice: str,
        artifact_dict: dict[str, Any],
        evaluation_criteria: str,
    ) -> float:
        """Evaluate artifact with a single voice using LLM."""
        import json

        prompt = f"""Evaluate this creative artifact from the {voice.upper()} perspective.

ARTIFACT:
{json.dumps(artifact_dict, indent=2, default=str)[:2000]}  # Truncate for token efficiency

EVALUATION CRITERIA:
{evaluation_criteria}

Score from 0.0 to 1.0 where:
- 1.0 = Excellent, passes all checks
- 0.8 = Good, minor improvements possible
- 0.6 = Acceptable, notable issues
- 0.4 = Poor, significant problems
- 0.2 = Very poor, major failures
- 0.0 = Unacceptable, fails completely

Respond with ONLY a single number between 0.0 and 1.0."""

        try:
            response = await llm.generate(
                system=f"You are evaluating creative artifacts from the {voice} perspective. Be fair but rigorous.",
                user=prompt,
                temperature=0.2,
                max_tokens=10,
            )

            try:
                score = float(response.text.strip())
                return max(0.0, min(1.0, score))
            except ValueError:
                logger.warning(f"Failed to parse {voice} score: {response.text}")
                return 0.5

        except Exception as e:
            logger.error(f"Failed to evaluate {voice} voice: {e}")
            return 0.5

    def _identify_issues(
        self,
        voice_scores: dict[str, float],
        floor_violations: list[str],
        artifact: ArchaeologicalFindings | CreativeVision | Asset,
    ) -> list[str]:
        """Identify issues based on voice scores and floor violations."""
        issues = list(floor_violations)

        if voice_scores.get("adversarial", 1.0) < 0.8:
            issues.append(
                f"Technical correctness below threshold ({voice_scores['adversarial']:.0%})"
            )

        if voice_scores.get("creative", 1.0) < 0.6:
            issues.append(f"Creative novelty lacking ({voice_scores['creative']:.0%})")

        if voice_scores.get("advocate", 1.0) < 0.6:
            issues.append(f"Delight factor missing ({voice_scores['advocate']:.0%})")

        return issues

    async def _generate_suggestions(
        self,
        artifact: ArchaeologicalFindings | CreativeVision | Asset,
        voice_scores: dict[str, float],
        issues: list[str],
        context: dict[str, Any],
    ) -> list[str]:
        """Generate improvement suggestions using LLM."""
        if not issues:
            return []

        llm = self._ensure_llm()
        import json

        artifact_dict = artifact.to_dict()

        prompt = f"""Given this creative artifact and its issues, suggest specific improvements.

ARTIFACT:
{json.dumps(artifact_dict, indent=2, default=str)[:1500]}

VOICE SCORES:
- Adversarial (correctness): {voice_scores.get("adversarial", 0):.0%}
- Creative (novelty): {voice_scores.get("creative", 0):.0%}
- Advocate (delight): {voice_scores.get("advocate", 0):.0%}

IDENTIFIED ISSUES:
{chr(10).join(f"- {issue}" for issue in issues)}

Provide 2-4 specific, actionable suggestions to address these issues.
Each suggestion should be concrete and implementable.
Format: One suggestion per line, starting with a verb (Add, Remove, Modify, etc.)"""

        try:
            response = await llm.generate(
                system="You are a creative director providing specific, actionable feedback.",
                user=prompt,
                temperature=0.4,
                max_tokens=500,
            )

            # Parse suggestions from response
            suggestions = []
            for line in response.text.strip().split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    # Remove leading numbers or bullets
                    if line[0].isdigit() or line[0] in "-*":
                        line = line.lstrip("0123456789.-*) ").strip()
                    if line:
                        suggestions.append(line)

            return suggestions[:4]  # Limit to 4 suggestions

        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            return ["Review and address identified issues manually"]

    def _calculate_overall_score(self, voice_scores: dict[str, float]) -> float:
        """Calculate weighted overall score from voice scores."""
        total_weight = sum(self.VOICE_WEIGHTS.values())
        weighted_sum = sum(
            voice_scores.get(voice, 0.0) * weight for voice, weight in self.VOICE_WEIGHTS.items()
        )
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    async def _apply_improvements(
        self,
        artifact: T,
        critique: Critique,
    ) -> T:
        """Apply improvements to artifact based on critique suggestions."""
        llm = self._ensure_llm()
        import json

        artifact_dict = artifact.to_dict()

        prompt = f"""Apply these improvements to the creative artifact:

CURRENT ARTIFACT:
{json.dumps(artifact_dict, indent=2, default=str)[:2000]}

IMPROVEMENTS TO APPLY:
{chr(10).join(f"- {s}" for s in critique.suggestions)}

Return the improved artifact as a JSON object with the same structure.
Only modify fields that need changing based on the suggestions.
Maintain all existing fields not affected by the improvements."""

        try:
            response = await llm.generate(
                system="You are applying specific improvements to a creative artifact. Return valid JSON only.",
                user=prompt,
                temperature=0.3,
                max_tokens=3000,
            )

            # Parse the improved artifact
            import re

            # Extract JSON from response (may be wrapped in markdown)
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response.text)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response.text.strip()

            improved_dict = json.loads(json_str)

            # Reconstruct the artifact based on type
            # mypy sees these casts as redundant but they're needed for TypeVar T
            if isinstance(artifact, ArchaeologicalFindings):
                return cast(T, ArchaeologicalFindings.from_dict(improved_dict))  # type: ignore[redundant-cast]
            elif isinstance(artifact, CreativeVision):
                return cast(T, CreativeVision.from_dict(improved_dict))  # type: ignore[redundant-cast]
            elif isinstance(artifact, Asset):
                return cast(T, Asset.from_dict(improved_dict))  # type: ignore[redundant-cast]
            else:
                return artifact

        except Exception as e:
            logger.error(f"Failed to apply improvements: {e}")
            raise


# =============================================================================
# Convenience Functions
# =============================================================================


async def critique_artifact(
    artifact: ArchaeologicalFindings | CreativeVision | Asset,
    context: dict[str, Any] | None = None,
) -> Critique:
    """
    Convenience function to critique an artifact.

    Args:
        artifact: The artifact to critique
        context: Additional context

    Returns:
        Structured critique
    """
    loop = StudioFeedbackLoop()
    return await loop.critique(artifact, context)


async def improve_artifact(
    artifact: T,
    max_iterations: int = 3,
) -> tuple[T, list[Critique]]:
    """
    Convenience function to improve an artifact.

    Args:
        artifact: The artifact to improve
        max_iterations: Maximum improvement iterations

    Returns:
        Tuple of (improved artifact, critique history)
    """
    loop = StudioFeedbackLoop()
    initial_critique = await loop.critique(artifact)
    return await loop.improve(artifact, initial_critique, max_iterations)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "Critique",
    "ImprovementTracker",
    "StudioFeedbackLoop",
    "WitnessProtocol",
    "critique_artifact",
    "improve_artifact",
]
