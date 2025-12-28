"""
Experience Quality Operad (EQO) Service.

A categorical framework for measuring and composing experiential quality.
Unifies four orthogonal quality dimensions into a single operad.

The Quality Tetrad:
- Contrast (C): Does this experience have variety? [0, 1]
- Arc (A): Does this experience have shape? [0, 1]
- Voice (V): Is this correct, interesting, AND fun? {0, 1}^3
- Floor (F): Is this experience worth having? {0, 1}

Core Insight:
    Experience quality is not a single number but a structured object
    with composition laws. Two experiences compose, and their combined
    quality is derivable from their individual qualities plus interaction terms.

Composition Operations:
- Sequential (>>): A then B
- Parallel (||): A and B simultaneously
- Nested ([]): B inside A

Operad Laws:
- Identity: measure(Id) = Quality.unit()
- Associativity: (A >> B) >> C = A >> (B >> C)
- Floor gate: F=0 => Q=0

Usage:
    >>> from services.experience_quality import (
    ...     Experience, Spec,
    ...     measure_quality, witness_quality, crystallize_quality,
    ...     sequential_compose, parallel_compose, nested_compose,
    ... )
    >>>
    >>> # Create an experience
    >>> exp = Experience(
    ...     id="run-001",
    ...     type="run",
    ...     domain="wasm_survivors",
    ...     duration=120.0,
    ...     data={"intensity_curve": [0.2, 0.5, 0.9, 0.3, 0.7]},
    ... )
    >>>
    >>> # Measure quality
    >>> quality = measure_quality(exp)
    >>> print(f"Quality: {quality.overall:.2f}")
    >>>
    >>> # Witness and crystallize
    >>> mark = await witness_quality(exp)
    >>> crystal = await crystallize_quality([mark])

Philosophy:
    "Quality is not a number. It is a structure. The structure composes."

See: spec/theory/experience-quality-operad.md
"""

# Types
from .types import (
    # Enums
    EmotionalPhase,
    # Contrast
    ContrastMeasurement,
    # Arc
    ArcMeasurement,
    # Voice
    VoiceVerdict,
    VoiceMeasurement,
    # Floor
    FloorCheck,
    FloorMeasurement,
    # Quality
    ExperienceQuality,
    # Containers
    Experience,
    Spec,
    # Quality Algebra (Domain Parameterization)
    ContrastDimension,
    PhaseDefinition,
    VoiceDefinition,
    FloorCheckDefinition,
    QualityAlgebra,
)

# Measurement
from .measurement import (
    # Contrast
    measure_contrast,
    variance_normalized,
    # Arc
    measure_arc,
    classify_emotional_phase,
    # Voice
    check_voice,
    check_adversarial,
    check_creative,
    check_advocate,
    # Floor
    check_floor,
    get_floor_checks_for_domain,
    # Unified
    measure_quality,
    identify_bottleneck,
    generate_recommendation,
    # Utilities
    cosine_distance,
    experience_vector,
    chain_arc_coverage,
)

# Composition
from .composition import (
    # Core compositions
    sequential_compose,
    parallel_compose,
    nested_compose,
    # Multi-way
    sequential_compose_many,
    parallel_compose_many,
    nested_compose_many,
    # Identity and zero
    identity,
    zero,
    # Law verification
    verify_associativity_sequential,
    verify_associativity_parallel,
    verify_floor_gate,
)

# Witness
from .witness import (
    # Types
    QualityMarkId,
    QualityCrystalId,
    generate_quality_mark_id,
    generate_quality_crystal_id,
    # Mark
    QualityMark,
    QualityMoment,
    # Crystal
    QualityCrystal,
    # Functions
    witness_quality,
    crystallize_quality,
)

# Algebras (registry and default definitions)
from .algebras import (
    # Registry functions
    register_algebra,
    register_algebra_overwrite,
    get_algebra,
    get_algebra_or_raise,
    list_algebras,
    all_algebras,
    unregister_algebra,
    clear_registry,
    # Utilities
    measure_with_algebra,
    validate_experience_against_algebra,
    # Default definitions
    DEFAULT_ALGEBRA,
    DEFAULT_CONTRAST_DIMS,
    DEFAULT_ARC_PHASES,
    DEFAULT_VOICES,
)

__all__ = [
    # === Types ===
    # Enums
    "EmotionalPhase",
    # Contrast
    "ContrastMeasurement",
    # Arc
    "ArcMeasurement",
    # Voice
    "VoiceVerdict",
    "VoiceMeasurement",
    # Floor
    "FloorCheck",
    "FloorMeasurement",
    # Quality
    "ExperienceQuality",
    # Containers
    "Experience",
    "Spec",
    # Quality Algebra (Domain Parameterization)
    "ContrastDimension",
    "PhaseDefinition",
    "VoiceDefinition",
    "FloorCheckDefinition",
    "QualityAlgebra",
    # === Measurement ===
    "measure_contrast",
    "variance_normalized",
    "measure_arc",
    "classify_emotional_phase",
    "check_voice",
    "check_adversarial",
    "check_creative",
    "check_advocate",
    "check_floor",
    "get_floor_checks_for_domain",
    "measure_quality",
    "identify_bottleneck",
    "generate_recommendation",
    "cosine_distance",
    "experience_vector",
    "chain_arc_coverage",
    # === Composition ===
    "sequential_compose",
    "parallel_compose",
    "nested_compose",
    "sequential_compose_many",
    "parallel_compose_many",
    "nested_compose_many",
    "identity",
    "zero",
    "verify_associativity_sequential",
    "verify_associativity_parallel",
    "verify_floor_gate",
    # === Witness ===
    "QualityMarkId",
    "QualityCrystalId",
    "generate_quality_mark_id",
    "generate_quality_crystal_id",
    "QualityMark",
    "QualityMoment",
    "QualityCrystal",
    "witness_quality",
    "crystallize_quality",
    # === Algebras (Registry) ===
    "register_algebra",
    "register_algebra_overwrite",
    "get_algebra",
    "get_algebra_or_raise",
    "list_algebras",
    "all_algebras",
    "unregister_algebra",
    "clear_registry",
    "measure_with_algebra",
    "validate_experience_against_algebra",
    # === Default Definitions ===
    "DEFAULT_ALGEBRA",
    "DEFAULT_CONTRAST_DIMS",
    "DEFAULT_ARC_PHASES",
    "DEFAULT_VOICES",
]
