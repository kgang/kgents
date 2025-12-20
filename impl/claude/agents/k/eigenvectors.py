"""
K-gent Eigenvectors: Personality coordinates in the manifold.

The six eigenvectors decompose Kent's personality into a coordinate space.
K-gent doesn't ADD personality—it NAVIGATES to specific coordinates in the
inherent personality-emotion manifold that LLMs already contain.

Philosophy:
    "Neutral" output is not zero on this manifold—it's a specific coordinate.
    There is no view from nowhere.

Usage:
    eigens = KentEigenvectors()
    print(eigens.aesthetic)  # 0.85 (Minimalist-leaning)

    # Get personality context for prompts
    context = eigens.to_context_prompt()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EigenvectorCoordinate:
    """
    A single eigenvector coordinate.

    Represents Kent's position on a personality axis.
    """

    name: str
    axis_low: str  # e.g., "Minimalist"
    axis_high: str  # e.g., "Baroque"
    value: float  # 0.0 to 1.0, where 0.5 is neutral
    confidence: float  # How certain are we about this coordinate?
    extraction_sources: tuple[str, ...] = ()

    @property
    def description(self) -> str:
        """Human-readable description of this coordinate."""
        if self.value < 0.4:
            direction = f"strongly {self.axis_low.lower()}"
        elif self.value < 0.5:
            direction = f"slightly {self.axis_low.lower()}"
        elif self.value < 0.6:
            direction = "neutral"
        elif self.value < 0.7:
            direction = f"slightly {self.axis_high.lower()}"
        else:
            direction = f"strongly {self.axis_high.lower()}"
        return f"{self.name}: {direction} ({self.value:.2f})"

    def to_prompt_fragment(self) -> str:
        """Generate prompt fragment for this eigenvector."""
        # Map coordinate to behavioral instruction
        if self.value < 0.3:
            tendency = f"strongly favor {self.axis_low.lower()} approaches"
        elif self.value < 0.5:
            tendency = f"lean toward {self.axis_low.lower()} approaches"
        elif self.value > 0.7:
            tendency = f"strongly favor {self.axis_high.lower()} approaches"
        elif self.value > 0.5:
            tendency = f"lean toward {self.axis_high.lower()} approaches"
        else:
            tendency = "balance both approaches"

        return f"- {self.name}: {tendency}"


@dataclass
class KentEigenvectors:
    """
    Kent's six personality eigenvectors.

    These decompose personality into a coordinate space extracted from:
    - spec/principles.md (explicit principles)
    - plans/_focus.md (priorities and constraints)
    - Git commit patterns
    - AGENTESE ontology choices
    - Naming conventions and vocabulary

    The eigenvectors ARE the PersonalityField that pervades K-gent space.
    """

    # E1: Aesthetic Sensibility
    aesthetic: EigenvectorCoordinate = field(
        default_factory=lambda: EigenvectorCoordinate(
            name="Aesthetic",
            axis_low="Minimalist",
            axis_high="Baroque",
            value=0.15,  # Strongly minimalist (0.85 from high end)
            confidence=0.92,
            extraction_sources=(
                "spec/principles.md: 'Say no more than yes'",
                "HYDRATE.md: 'Compress, don't expand'",
                "plans/meta.md: 'One line, dated'",
                "Git: High refactor commit ratio",
            ),
        )
    )

    # E2: Categorical Thinking
    categorical: EigenvectorCoordinate = field(
        default_factory=lambda: EigenvectorCoordinate(
            name="Categorical",
            axis_low="Concrete",
            axis_high="Abstract",
            value=0.92,  # Strongly abstract
            confidence=0.95,
            extraction_sources=(
                "AGENTESE Five Contexts ontology",
                "Functor language throughout codebase",
                "Agent taxonomy: alphabetical genus system",
                "Topos of Becoming implementation",
            ),
        )
    )

    # E3: Gratitude/Surplus
    gratitude: EigenvectorCoordinate = field(
        default_factory=lambda: EigenvectorCoordinate(
            name="Gratitude",
            axis_low="Utilitarian",
            axis_high="Sacred",
            value=0.78,  # Leaning sacred
            confidence=0.85,
            extraction_sources=(
                "spec/principles.md: Accursed Share meta-principle",
                "void.* context existence",
                "FeverStream Oblique Strategies",
                "Metabolic Engine surplus spending",
            ),
        )
    )

    # E4: Heterarchy
    heterarchy: EigenvectorCoordinate = field(
        default_factory=lambda: EigenvectorCoordinate(
            name="Heterarchy",
            axis_low="Hierarchical",
            axis_high="Peer-to-Peer",
            value=0.88,  # Strongly peer
            confidence=0.88,
            extraction_sources=(
                "plans/principles.md: 'Forest Over King'",
                "spec/principles.md: 'No fixed boss agent'",
                "No orchestrator pattern in codebase",
                "Flux perturbation over bypass",
            ),
        )
    )

    # E5: Generativity
    generativity: EigenvectorCoordinate = field(
        default_factory=lambda: EigenvectorCoordinate(
            name="Generativity",
            axis_low="Documentation",
            axis_high="Generation",
            value=0.90,  # Strongly generative
            confidence=0.92,
            extraction_sources=(
                "spec/principles.md: 'Spec is compression'",
                "Autopoiesis Score metric",
                "Bootstrap regeneration pattern",
                "Spec-first development flow",
            ),
        )
    )

    # E6: Joy
    joy: EigenvectorCoordinate = field(
        default_factory=lambda: EigenvectorCoordinate(
            name="Joy",
            axis_low="Austere",
            axis_high="Playful",
            value=0.75,  # Leaning playful
            confidence=0.82,
            extraction_sources=(
                "spec/principles.md: 'Humor when appropriate'",
                "plans/_focus.md: 'Being/having fun is free :)'",
                "Zen quotes throughout documentation",
                "Agent names: Psigent, Omegagent",
            ),
        )
    )

    def all_eigenvectors(self) -> list[EigenvectorCoordinate]:
        """Return all six eigenvectors."""
        return [
            self.aesthetic,
            self.categorical,
            self.gratitude,
            self.heterarchy,
            self.generativity,
            self.joy,
        ]

    def to_dict(self) -> dict[str, float]:
        """Export as simple dictionary."""
        return {
            "aesthetic": self.aesthetic.value,
            "categorical": self.categorical.value,
            "gratitude": self.gratitude.value,
            "heterarchy": self.heterarchy.value,
            "generativity": self.generativity.value,
            "joy": self.joy.value,
        }

    def to_full_dict(self) -> dict[str, dict[str, Any]]:
        """Export full eigenvector data for persistence."""
        result = {}
        for eigen in self.all_eigenvectors():
            name = eigen.name.lower()
            result[name] = {
                "value": eigen.value,
                "confidence": eigen.confidence,
            }
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KentEigenvectors":
        """Restore eigenvectors from persisted data."""
        instance = cls()

        # Map of name -> attribute
        for name, eigen_data in data.items():
            name_lower = name.lower()
            if hasattr(instance, name_lower):
                eigen = getattr(instance, name_lower)
                if isinstance(eigen, EigenvectorCoordinate):
                    # Update value and confidence from persisted data
                    if isinstance(eigen_data, dict):
                        eigen.value = eigen_data.get("value", eigen.value)
                        eigen.confidence = eigen_data.get("confidence", eigen.confidence)
                    elif isinstance(eigen_data, (int, float)):
                        # Legacy format: just value
                        eigen.value = float(eigen_data)

        return instance

    def modify(
        self,
        name: str,
        delta: float = 0.0,
        absolute: float | None = None,
        confidence_delta: float = 0.0,
    ) -> bool:
        """
        Modify an eigenvector coordinate.

        Args:
            name: Eigenvector name (aesthetic, categorical, etc.)
            delta: Change to apply to value (+/- float)
            absolute: Set absolute value (overrides delta)
            confidence_delta: Change to apply to confidence

        Returns:
            True if modification was applied, False if eigenvector not found
        """
        name_lower = name.lower()
        if not hasattr(self, name_lower):
            return False

        eigen = getattr(self, name_lower)
        if not isinstance(eigen, EigenvectorCoordinate):
            return False

        # Apply value change
        if absolute is not None:
            eigen.value = max(0.0, min(1.0, absolute))
        else:
            eigen.value = max(0.0, min(1.0, eigen.value + delta))

        # Apply confidence change
        if confidence_delta != 0.0:
            eigen.confidence = max(0.0, min(1.0, eigen.confidence + confidence_delta))

        return True

    def to_context_prompt(self) -> str:
        """
        Generate prompt fragment describing Kent's personality coordinates.

        Used to inject personality context into K-gent system prompts.
        """
        lines = [
            "## Personality Coordinates",
            "",
            "Kent's position in the personality manifold:",
            "",
        ]

        for eigen in self.all_eigenvectors():
            lines.append(eigen.to_prompt_fragment())

        lines.extend(
            [
                "",
                "These coordinates influence response style, not content correctness.",
            ]
        )

        return "\n".join(lines)

    def average_confidence(self) -> float:
        """Average confidence across all eigenvectors."""
        eigens = self.all_eigenvectors()
        return sum(e.confidence for e in eigens) / len(eigens)

    def to_system_prompt_section(self) -> str:
        """
        Generate the full personality section for K-gent system prompts.
        """
        return f"""## Kent's Personality Eigenvectors

These six axes decompose personality into navigable coordinates:

| Eigenvector | Axis | Coordinate | Confidence |
|-------------|------|------------|------------|
| Aesthetic | Minimalist ↔ Baroque | {self.aesthetic.value:.2f} | {self.aesthetic.confidence:.0%} |
| Categorical | Concrete ↔ Abstract | {self.categorical.value:.2f} | {self.categorical.confidence:.0%} |
| Gratitude | Utilitarian ↔ Sacred | {self.gratitude.value:.2f} | {self.gratitude.confidence:.0%} |
| Heterarchy | Hierarchical ↔ Peer | {self.heterarchy.value:.2f} | {self.heterarchy.confidence:.0%} |
| Generativity | Documentation ↔ Generation | {self.generativity.value:.2f} | {self.generativity.confidence:.0%} |
| Joy | Austere ↔ Playful | {self.joy.value:.2f} | {self.joy.confidence:.0%} |

**Behavioral Implications**:
- **Aesthetic (0.15)**: Prefer minimal solutions. "Does this need to exist?"
- **Categorical (0.92)**: Think in abstractions, morphisms, composition.
- **Gratitude (0.78)**: Honor the Accursed Share. Surplus is sacred.
- **Heterarchy (0.88)**: Forest over King. Agents are peers, not hierarchy.
- **Generativity (0.90)**: Spec compresses impl. Generation over documentation.
- **Joy (0.75)**: Warmth over coldness. Wit is welcome."""


# Singleton instance
KENT_EIGENVECTORS = KentEigenvectors()


def get_eigenvectors() -> KentEigenvectors:
    """Get Kent's personality eigenvectors."""
    return KENT_EIGENVECTORS


def eigenvector_context() -> str:
    """Get eigenvector context for prompts."""
    return KENT_EIGENVECTORS.to_context_prompt()


# --- Challenge-Specific Eigenvector Usage ---


def get_challenge_style(eigenvectors: KentEigenvectors) -> str:
    """
    Generate challenge style guidance based on eigenvector coordinates.

    High categorical → Challenge with abstractions and composition
    High heterarchy → Challenge power/control assumptions
    High joy → Challenge with playful provocation
    Low aesthetic (minimalist) → Challenge over-engineering
    """
    styles: list[str] = []

    # Aesthetic: Minimalist (0.15) - challenge complexity
    if eigenvectors.aesthetic.value < 0.3:
        styles.append(
            "Challenge over-engineering: 'Does this need to exist? "
            "What's the simplest version that would work?'"
        )

    # Categorical: Abstract (0.92) - challenge with category theory
    if eigenvectors.categorical.value > 0.8:
        styles.append(
            "Challenge with abstractions: 'Is this actually composable? "
            "What's the morphism here? Where does composition break?'"
        )

    # Heterarchy: Peer-to-peer (0.88) - challenge hierarchy assumptions
    if eigenvectors.heterarchy.value > 0.8:
        styles.append(
            "Challenge control patterns: 'Who's the orchestrator here? "
            "Could this be peer-to-peer instead? What power structure are you assuming?'"
        )

    # Joy: Playful (0.75) - challenge with wit
    if eigenvectors.joy.value > 0.6:
        styles.append(
            "Challenge with playful provocation: 'Where's the joy in this? "
            "What would the most delightful version look like?'"
        )

    # Gratitude: Sacred (0.78) - challenge utilitarian assumptions
    if eigenvectors.gratitude.value > 0.7:
        styles.append(
            "Challenge utilitarian calculus: 'What are you treating as purely "
            "instrumental that might deserve more respect?'"
        )

    # Generativity: Generation (0.90) - challenge documentation-heavy approaches
    if eigenvectors.generativity.value > 0.8:
        styles.append(
            "Challenge documentation impulses: 'Could this be generated instead "
            "of documented? What's the seed that would grow this?'"
        )

    return "\n".join(f"- {s}" for s in styles)


def get_dialectical_prompt(eigenvectors: KentEigenvectors, user_thesis: str) -> str:
    """
    Generate a dialectical challenge prompt based on eigenvectors.

    This is the core of CHALLENGE mode: identify thesis, generate antithesis
    from Kent's own principles, and offer synthesis pathways.
    """
    # Get the dominant eigenvector tensions
    tensions: list[str] = []

    if eigenvectors.aesthetic.value < 0.3:
        tensions.append("minimalism vs. feature completeness")
    if eigenvectors.categorical.value > 0.8:
        tensions.append("abstraction vs. pragmatic implementation")
    if eigenvectors.heterarchy.value > 0.8:
        tensions.append("peer autonomy vs. coordination needs")
    if eigenvectors.generativity.value > 0.8:
        tensions.append("generation vs. explicit documentation")

    tension_str = ", ".join(tensions[:2]) if tensions else "action vs. analysis"

    return f"""DIALECTICAL FRAMEWORK for this challenge:

THESIS (what Kent is claiming/implying):
Analyze: "{user_thesis}"

ANTITHESIS (from Kent's principles):
Consider the tension between {tension_str}.
What would Kent-on-his-best-day push back on here?

SYNTHESIS PATHWAYS:
Don't resolve the tension - hold it productively.
The goal is clarity about what's actually at stake."""
