"""
Experience Quality Operad: Domain-Specific Algebras Registry.

Provides default algebras and a registry for domain-specific quality measurement.
An O-algebra instantiates the operad for a specific domain.

Philosophy:
    "The operad defines the grammar. The algebra speaks the language."

Note:
    Domain-specific algebras (e.g., for specific pilots) should be registered
    at runtime by the domain code, not hardcoded here. This module provides
    only the universal defaults and registry infrastructure.

Example:
    >>> from services.experience_quality.algebras import get_algebra, register_algebra
    >>>
    >>> # Register a domain-specific algebra
    >>> register_algebra(my_domain_algebra)
    >>>
    >>> # Get it back
    >>> algebra = get_algebra("my_domain")

See: spec/theory/experience-quality-operad.md Section 5 (Algebras)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .types import (
    ContrastDimension,
    PhaseDefinition,
    VoiceDefinition,
    FloorCheckDefinition,
    QualityAlgebra,
)

if TYPE_CHECKING:
    from .types import Experience, ExperienceQuality


# =============================================================================
# Default Contrast Dimensions (The Seven)
# =============================================================================

DEFAULT_CONTRAST_DIMS = (
    ContrastDimension(
        name="breath",
        description="C1: Intensity oscillation (crescendo <-> silence)",
        measurement_hint="Track intensity values over time, compute variance",
    ),
    ContrastDimension(
        name="scarcity",
        description="C2: Resource oscillation (feast <-> famine)",
        measurement_hint="Track resource availability over time",
    ),
    ContrastDimension(
        name="tempo",
        description="C3: Speed oscillation (fast <-> slow)",
        measurement_hint="Track pacing/speed over time",
    ),
    ContrastDimension(
        name="stakes",
        description="C4: Risk oscillation (safe <-> lethal)",
        measurement_hint="Track danger level over time",
    ),
    ContrastDimension(
        name="anticipation",
        description="C5: Tension oscillation (calm <-> dread)",
        measurement_hint="Track tension/anticipation over time",
    ),
    ContrastDimension(
        name="reward",
        description="C6: Gratification oscillation (drought <-> burst)",
        measurement_hint="Track reward density over time",
    ),
    ContrastDimension(
        name="identity",
        description="C7: Choice oscillation (exploration <-> commitment)",
        measurement_hint="Track choice breadth over time",
    ),
)


# =============================================================================
# Default Arc Phases (The Five)
# =============================================================================

DEFAULT_ARC_PHASES = (
    PhaseDefinition(
        name="hope",
        description="I can do this - optimism and confidence",
        triggers=("high_health", "good_position", "early_game"),
    ),
    PhaseDefinition(
        name="flow",
        description="I'm unstoppable - in the zone",
        triggers=("combo_active", "high_score_streak", "no_damage_taken"),
    ),
    PhaseDefinition(
        name="crisis",
        description="Oh no, maybe not - tension and challenge",
        triggers=("low_health", "surrounded", "boss_encounter"),
    ),
    PhaseDefinition(
        name="triumph",
        description="I DID IT! - victory and satisfaction",
        triggers=("victory", "boss_defeated", "goal_achieved"),
    ),
    PhaseDefinition(
        name="grief",
        description="So close... - defeat with understanding",
        triggers=("death", "failure", "game_over"),
    ),
)


# =============================================================================
# Default Voice Definitions (The Three)
# =============================================================================

DEFAULT_VOICES = (
    VoiceDefinition(
        name="adversarial",
        question="Is this technically correct and fair?",
        checks=("laws_satisfied", "invariants_hold", "no_undefined_behavior"),
    ),
    VoiceDefinition(
        name="creative",
        question="Is this interesting and novel?",
        checks=("novelty", "surprise", "aesthetic_coherence"),
    ),
    VoiceDefinition(
        name="advocate",
        question="Is this fun and engaging?",
        checks=("engagement", "agency", "satisfaction"),
    ),
)


# =============================================================================
# Default Algebra (Universal Fallback)
# =============================================================================

DEFAULT_ALGEBRA = QualityAlgebra(
    domain="default",
    description="Default quality algebra for unknown domains",
    contrast_dims=DEFAULT_CONTRAST_DIMS,
    arc_phases=DEFAULT_ARC_PHASES,
    arc_canonical_transitions=(
        ("hope", "flow"),
        ("flow", "crisis"),
        ("crisis", "triumph"),
        ("crisis", "grief"),
    ),
    voices=DEFAULT_VOICES,
    floor_checks=(
        FloorCheckDefinition(
            name="engagement",
            threshold=0.5,
            comparison=">=",
            unit="ratio",
            description="Minimum engagement level",
        ),
    ),
)


# =============================================================================
# Algebra Registry
# =============================================================================

_ALGEBRA_REGISTRY: dict[str, QualityAlgebra] = {
    "default": DEFAULT_ALGEBRA,
}


def get_algebra(domain: str | None) -> QualityAlgebra | None:
    """
    Get the quality algebra for a domain.

    Args:
        domain: Domain name (e.g., "my_domain")

    Returns:
        QualityAlgebra for the domain, or None if not found.
        Note: Returns None for unknown domains to allow fallback to legacy behavior.
    """
    if domain is None:
        return None
    return _ALGEBRA_REGISTRY.get(domain)


def get_algebra_or_raise(domain: str) -> QualityAlgebra:
    """
    Get the quality algebra for a domain, raising if not found.

    Args:
        domain: Domain name

    Returns:
        QualityAlgebra for the domain.

    Raises:
        KeyError: If domain is not registered.
    """
    if domain not in _ALGEBRA_REGISTRY:
        raise KeyError(f"No algebra registered for domain: {domain}")
    return _ALGEBRA_REGISTRY[domain]


def register_algebra(algebra: QualityAlgebra) -> None:
    """
    Register a new quality algebra.

    Args:
        algebra: The algebra to register

    Raises:
        ValueError: If algebra for domain already exists.
    """
    if algebra.domain in _ALGEBRA_REGISTRY:
        raise ValueError(
            f"Algebra for domain '{algebra.domain}' already exists. "
            "Use register_algebra_overwrite() to replace."
        )
    _ALGEBRA_REGISTRY[algebra.domain] = algebra


def register_algebra_overwrite(algebra: QualityAlgebra) -> None:
    """
    Register a quality algebra, overwriting if exists.

    Args:
        algebra: The algebra to register
    """
    _ALGEBRA_REGISTRY[algebra.domain] = algebra


def unregister_algebra(domain: str) -> bool:
    """
    Unregister an algebra by domain.

    Args:
        domain: Domain name to unregister.

    Returns:
        True if algebra was removed, False if not found.
    """
    if domain in _ALGEBRA_REGISTRY:
        del _ALGEBRA_REGISTRY[domain]
        return True
    return False


def clear_registry() -> None:
    """Clear all registered algebras."""
    _ALGEBRA_REGISTRY.clear()


def list_algebras() -> list[str]:
    """List all registered algebra domain names."""
    return list(_ALGEBRA_REGISTRY.keys())


def all_algebras() -> dict[str, QualityAlgebra]:
    """Get all registered algebras."""
    return dict(_ALGEBRA_REGISTRY)


# =============================================================================
# Utility Functions
# =============================================================================


def measure_with_algebra(
    experience: "Experience",
    algebra: QualityAlgebra | None = None,
) -> "ExperienceQuality":
    """
    Measure experience quality using an algebra.

    This is a convenience wrapper that imports measure_quality lazily
    to avoid circular imports.

    Args:
        experience: The experience to measure.
        algebra: Optional algebra (will use experience.domain if None).

    Returns:
        ExperienceQuality measurement.
    """
    from .measurement import measure_quality
    return measure_quality(experience, algebra=algebra)


def validate_experience_against_algebra(
    experience: "Experience",
    algebra: QualityAlgebra | None = None,
) -> list[str]:
    """
    Validate that an experience has the data expected by an algebra.

    Returns a list of warnings for missing data.

    Args:
        experience: The experience to validate.
        algebra: The algebra to validate against.

    Returns:
        List of warning messages for missing/incompatible data.
    """
    if algebra is None:
        algebra = get_algebra(experience.domain)
    if algebra is None:
        return [f"No algebra registered for domain: {experience.domain}"]

    warnings: list[str] = []
    data = experience.data

    # Check for expected contrast curves
    for dim in algebra.contrast_dims:
        # Derive curve key from dimension name
        curve_key = f"{dim.name}_curve"
        if curve_key not in data:
            warnings.append(f"Missing contrast curve: {curve_key}")

    # Check for floor check data
    for check in algebra.floor_checks:
        if check.name not in data:
            # This is a warning, not an error - default values are used
            warnings.append(f"Missing floor check data: {check.name}")

    return warnings


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Default definitions
    "DEFAULT_CONTRAST_DIMS",
    "DEFAULT_ARC_PHASES",
    "DEFAULT_VOICES",
    # Pre-defined algebras
    "DEFAULT_ALGEBRA",
    # Registry functions
    "get_algebra",
    "get_algebra_or_raise",
    "register_algebra",
    "register_algebra_overwrite",
    "unregister_algebra",
    "clear_registry",
    "list_algebras",
    "all_algebras",
    # Utility functions
    "measure_with_algebra",
    "validate_experience_against_algebra",
]
