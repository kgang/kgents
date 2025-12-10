"""
Psi-gent DialecticalRotator: The X-axis of the 4-axis tensor.

Controls Jungian parallax - shadow rotation to stress-test metaphors.

Delegates to H-gent Jung for shadow generation and integration.
If solution fails in Shadow context, metaphor is fragile.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .types import (
    AxisType,
    Projection,
    StabilityStatus,
    ValidationResult,
    AntiPattern,
    AntiPatternDetection,
)


# =============================================================================
# Shadow Types
# =============================================================================


class ShadowType(Enum):
    """Types of shadow content to test."""

    # Original types
    NEGATIVE_EXTERNALITY = "negative_externality"  # Hidden costs
    UNINTENDED_CONSEQUENCE = "unintended"  # Second-order effects
    SUPPRESSED_ALTERNATIVE = "suppressed"  # Ignored options
    HIDDEN_ASSUMPTION = "assumption"  # Implicit beliefs
    DENIED_RISK = "risk"  # Unacknowledged dangers

    # Test-expected types
    NEGATION = "negation"  # Direct negation of concept
    INVERSION = "inversion"  # Logical inversion
    EXTREME = "extreme"  # Extreme/edge case
    OPPOSITE_DOMAIN = "opposite_domain"  # From opposite domain


@dataclass(frozen=True)
class Shadow:
    """
    The shadow of a metaphor projection.

    In Jungian terms, the Shadow is what is excluded to maintain
    the coherence of the Ego (the projection).
    """

    shadow_type: ShadowType
    content: str = ""
    severity: float = 0.5  # 0 = minor, 1 = critical

    # Concept-based shadow (for test compatibility)
    original_concept: str = ""
    shadow_concept: str = ""
    stress_factor: float = 0.5

    # What it reveals
    hidden_truth: str = ""
    challenge_to_projection: str = ""


@dataclass(frozen=True)
class ShadowTestResult:
    """Result of testing a projection against its shadow."""

    projection: Projection
    shadows: tuple[Shadow, ...] = ()
    survived: bool = True  # Did projection survive shadow testing?
    survives: bool = True  # Alias for survived (test compatibility)
    fragility_score: float = 0.0  # 0 = robust, 1 = completely fragile

    # Details
    failed_shadows: tuple[Shadow, ...] = ()
    integration_notes: str = ""

    def __post_init__(self):
        # Keep survives in sync with survived
        object.__setattr__(self, "survives", self.survived)


# =============================================================================
# Shadow Generator (Jungian Pattern)
# =============================================================================


class ShadowGenerator:
    """
    Generates shadow content for metaphor projections.

    This is the H-jung delegate functionality within Psi-gent.
    """

    def generate(self, projection: Projection, count: int = 3) -> list[Shadow]:
        """
        Generate shadow content for a projection (test-compatible API).

        Args:
            projection: The projection to generate shadows for
            count: Maximum number of shadows to generate

        Returns:
            List of Shadow objects
        """
        shadow_types = [
            ShadowType.NEGATION,
            ShadowType.INVERSION,
            ShadowType.EXTREME,
            ShadowType.OPPOSITE_DOMAIN,
        ]

        shadows = []
        concepts = (
            list(projection.mapped_concepts.keys())
            if projection.mapped_concepts
            else ["problem"]
        )

        for i, concept in enumerate(concepts[:count]):
            shadow_type = shadow_types[i % len(shadow_types)]
            shadow = Shadow(
                shadow_type=shadow_type,
                original_concept=concept,
                shadow_concept=f"non-{concept}"
                if shadow_type == ShadowType.NEGATION
                else f"inverse-{concept}",
                stress_factor=0.5 + (i * 0.1),
                content=f"Shadow of {concept}",
                severity=0.5,
            )
            shadows.append(shadow)

        return shadows[:count]

    def generate_shadows(self, projection: Projection) -> list[Shadow]:
        """
        Generate shadow content for a projection.

        Asks: What is this projection NOT seeing?
        """
        shadows = []

        # 1. Negative externalities
        shadows.append(self._generate_externality_shadow(projection))

        # 2. Unintended consequences
        shadows.append(self._generate_consequence_shadow(projection))

        # 3. Suppressed alternatives
        shadows.append(self._generate_alternative_shadow(projection))

        # 4. Hidden assumptions
        shadows.append(self._generate_assumption_shadow(projection))

        return [s for s in shadows if s is not None]

    def _generate_externality_shadow(self, projection: Projection) -> Shadow:
        """What costs are being ignored?"""
        metaphor = projection.target

        # Generate based on metaphor type
        externalities = {
            "military_strategy": "Human cost and collateral damage",
            "economics": "Environmental and social externalities",
            "biological_system": "Ecosystem disruption effects",
            "thermodynamics": "Energy dissipation and waste heat",
            "game_theory": "Player welfare and fairness",
        }

        content = externalities.get(
            metaphor.metaphor_id, "Unaccounted costs and side effects"
        )

        return Shadow(
            shadow_type=ShadowType.NEGATIVE_EXTERNALITY,
            content=content,
            severity=0.6,
            hidden_truth=f"The {metaphor.name} metaphor may hide: {content}",
            challenge_to_projection="What costs are not being counted?",
        )

    def _generate_consequence_shadow(self, projection: Projection) -> Shadow:
        """What unintended consequences might occur?"""
        ops = projection.applicable_operations

        if not ops:
            content = "Unknown second-order effects"
        else:
            # Each operation has potential unintended consequences
            content = f"Applying {ops[0]} may trigger unforeseen cascades"

        return Shadow(
            shadow_type=ShadowType.UNINTENDED_CONSEQUENCE,
            content=content,
            severity=0.5,
            hidden_truth="Second-order effects are often larger than primary effects",
            challenge_to_projection="What happens after the immediate solution?",
        )

    def _generate_alternative_shadow(self, projection: Projection) -> Shadow:
        """What alternatives are being suppressed?"""
        metaphor = projection.target

        return Shadow(
            shadow_type=ShadowType.SUPPRESSED_ALTERNATIVE,
            content=f"Alternative metaphors to {metaphor.name} were not considered",
            severity=0.4,
            hidden_truth="The first metaphor is rarely the only valid one",
            challenge_to_projection="What other frames could apply?",
        )

    def _generate_assumption_shadow(self, projection: Projection) -> Shadow:
        """What assumptions are hidden?"""
        metaphor = projection.target

        # Common hidden assumptions per metaphor
        assumptions = {
            "military_strategy": "Assumes clear adversary and winning is possible",
            "economics": "Assumes rational actors and measurable value",
            "biological_system": "Assumes natural selection as primary force",
            "thermodynamics": "Assumes closed system and equilibrium goal",
            "game_theory": "Assumes known rules and players",
        }

        content = assumptions.get(
            metaphor.metaphor_id, "Implicit assumptions about structure and dynamics"
        )

        return Shadow(
            shadow_type=ShadowType.HIDDEN_ASSUMPTION,
            content=content,
            severity=0.5,
            hidden_truth=f"Hidden assumption: {content}",
            challenge_to_projection="Is this assumption valid for the original problem?",
        )


# =============================================================================
# Dialectical Rotator
# =============================================================================


@dataclass
class DialecticalRotator:
    """
    The X-axis controller: Jungian parallax rotation.

    Tests if metaphor projections survive shadow examination.
    If a solution ignores its shadow, the metaphor is fragile.

    Responsibilities:
    1. Generate shadow content for projections
    2. Test projections against their shadows
    3. Detect shadow blindness anti-pattern
    4. Suggest shadow integration strategies
    """

    # Configuration
    fragility_threshold: float = 0.6  # Above this = unstable
    shadow_generator: ShadowGenerator = field(default_factory=ShadowGenerator)

    def test_shadow(self, projection: Projection, shadow: Shadow) -> ShadowTestResult:
        """
        Test a single shadow against a projection.

        Args:
            projection: The projection to test
            shadow: The shadow to test against

        Returns:
            ShadowTestResult indicating if the projection survives
        """
        survives = self._projection_survives_shadow(projection, shadow)
        return ShadowTestResult(
            projection=projection,
            shadows=(shadow,),
            survived=survives,
            fragility_score=0.0 if survives else shadow.stress_factor,
            failed_shadows=() if survives else (shadow,),
        )

    def rotate(self, projection: Projection) -> ShadowTestResult:
        """
        Apply Jungian parallax rotation to a projection.

        Tests if the projection survives shadow examination.
        """
        # Generate shadows
        shadows = self.shadow_generator.generate_shadows(projection)

        # Test each shadow
        failed_shadows = []
        total_severity = 0.0

        for shadow in shadows:
            if not self._projection_survives_shadow(projection, shadow):
                failed_shadows.append(shadow)
            total_severity += shadow.severity

        # Calculate fragility
        if not shadows:
            fragility = 0.0
        else:
            fragility = len(failed_shadows) / len(shadows)
            # Weight by severity
            avg_severity = total_severity / len(shadows)
            fragility = fragility * avg_severity

        survived = fragility < self.fragility_threshold

        # Generate integration notes
        notes = self._generate_integration_notes(projection, failed_shadows)

        return ShadowTestResult(
            projection=projection,
            shadows=tuple(shadows),
            survived=survived,
            fragility_score=fragility,
            failed_shadows=tuple(failed_shadows),
            integration_notes=notes,
        )

    def validate(self, projection: Projection) -> ValidationResult:
        """
        Validate a projection via shadow testing.

        Returns a ValidationResult for the X-axis.
        """
        result = self.rotate(projection)

        if result.survived and result.fragility_score < 0.3:
            return ValidationResult(
                axis=AxisType.X_JUNGIAN,
                status=StabilityStatus.STABLE,
                score=1.0 - result.fragility_score,
                message="Projection survives shadow examination",
                details={
                    "shadows_tested": len(result.shadows),
                    "shadows_failed": len(result.failed_shadows),
                },
            )
        elif result.survived:
            return ValidationResult(
                axis=AxisType.X_JUNGIAN,
                status=StabilityStatus.FRAGILE,
                score=1.0 - result.fragility_score,
                message=f"Projection is fragile: {len(result.failed_shadows)} shadow challenges",
                details={
                    "integration_notes": result.integration_notes,
                    "failed_shadows": [s.content for s in result.failed_shadows],
                },
            )
        else:
            return ValidationResult(
                axis=AxisType.X_JUNGIAN,
                status=StabilityStatus.UNSTABLE,
                score=1.0 - result.fragility_score,
                message="Projection fails shadow examination - metaphor is too fragile",
                details={
                    "fragility": result.fragility_score,
                    "critical_shadows": [s.content for s in result.failed_shadows],
                },
            )

    def detect_shadow_blindness(self, projection: Projection) -> AntiPatternDetection:
        """
        Detect the shadow blindness anti-pattern.

        Shadow blindness = accepting a solution while ignoring its shadow.
        """
        result = self.rotate(projection)

        # Shadow blindness if:
        # 1. Projection has high confidence but...
        # 2. Multiple critical shadows exist
        high_confidence = projection.confidence > 0.7
        critical_shadows = [s for s in result.shadows if s.severity > 0.7]

        detected = high_confidence and len(critical_shadows) >= 2

        return AntiPatternDetection(
            pattern=AntiPattern.SHADOW_BLINDNESS,
            detected=detected,
            confidence=len(critical_shadows) * 0.25 if detected else 0.0,
            evidence=f"{len(critical_shadows)} critical shadows ignored"
            if detected
            else "",
            mitigation="Explicitly address shadow content before proceeding",
        )

    def suggest_integration(self, result: ShadowTestResult) -> str:
        """
        Suggest how to integrate shadow content.

        Shadow integration = acknowledging and incorporating shadow insights.
        """
        if not result.failed_shadows:
            return "No shadow integration needed."

        suggestions = ["Shadow integration suggestions:"]

        for shadow in result.failed_shadows:
            match shadow.shadow_type:
                case ShadowType.NEGATIVE_EXTERNALITY:
                    suggestions.append(f"  - Account for: {shadow.content}")
                case ShadowType.UNINTENDED_CONSEQUENCE:
                    suggestions.append(f"  - Plan for: {shadow.content}")
                case ShadowType.SUPPRESSED_ALTERNATIVE:
                    suggestions.append(f"  - Consider: {shadow.content}")
                case ShadowType.HIDDEN_ASSUMPTION:
                    suggestions.append(f"  - Validate: {shadow.content}")
                case ShadowType.DENIED_RISK:
                    suggestions.append(f"  - Mitigate: {shadow.content}")

        return "\n".join(suggestions)

    # =========================================================================
    # Private Implementation
    # =========================================================================

    def _projection_survives_shadow(
        self, projection: Projection, shadow: Shadow
    ) -> bool:
        """
        Test if a projection can survive a specific shadow challenge.

        A projection survives if:
        1. It explicitly addresses the shadow concern, OR
        2. The shadow severity is low enough to be acceptable
        """
        # Low severity shadows are survivable
        if shadow.severity < 0.3:
            return True

        # Check if projection addresses shadow
        # (Simple heuristic: look for related concepts in mapping)
        shadow_content = shadow.content or shadow.original_concept or ""
        shadow_words = set(shadow_content.lower().split()) if shadow_content else set()

        # Get mapped concepts - handle both dict and tuple of ConceptMapping
        mapped_concepts = projection.mapped_concepts
        if isinstance(mapped_concepts, dict):
            concepts_to_check = set(mapped_concepts.keys())
        else:
            # Handle tuple/list of ConceptMapping
            concepts_to_check = set()
            for cm in mapped_concepts:
                if hasattr(cm, "source_concept"):
                    concepts_to_check.add(cm.source_concept)
                elif isinstance(cm, str):
                    concepts_to_check.add(cm)

        mapped_words = set()
        for concept in concepts_to_check:
            mapped_words.update(concept.lower().split())

        # If there's overlap, projection may address shadow
        overlap = shadow_words & mapped_words
        if overlap:
            return True

        # Check if applicable operations could address shadow
        for op in projection.applicable_operations:
            # Handle both string operations and MetaphorOperation objects
            op_name = op.name if hasattr(op, "name") else str(op)
            if any(word in op_name.lower() for word in shadow_words):
                return True

        # Default: doesn't survive
        return False

    def _generate_integration_notes(
        self, projection: Projection, failed_shadows: list[Shadow]
    ) -> str:
        """Generate notes on how to integrate failed shadows."""
        if not failed_shadows:
            return "All shadows addressed."

        notes = [
            f"The {projection.target.name} projection has {len(failed_shadows)} unaddressed shadows:",
        ]

        for shadow in failed_shadows:
            notes.append(
                f"  - [{shadow.shadow_type.value}] {shadow.challenge_to_projection}"
            )

        notes.append(
            "\nConsider whether these challenges invalidate the metaphor choice."
        )

        return "\n".join(notes)
