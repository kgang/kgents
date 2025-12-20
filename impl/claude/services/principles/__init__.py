"""
Principles Service: The queryable knowledge layer for kgents principles.

This service provides programmatic access to the kgents design principles
through the concept.principles AGENTESE node.

The Four Stances (from spec/principles/consumption.md):
- Genesis: Which principles apply?
- Poiesis: How do I build according to principles?
- Krisis: Does this embody the principles?
- Therapeia: Which principle was violated?

Example:
    from services.principles import PrincipleLoader, PrincipleChecker

    loader = create_principle_loader()
    content = await loader.load("CONSTITUTION.md")

    checker = create_principle_checker()
    result = await checker.check("my_agent")

See: spec/principles/node.md for the full specification.
"""

from __future__ import annotations

# === Checker ===
from .checker import (
    CheckJudgment,
    PrincipleChecker,
    create_principle_checker,
)

# === Healer ===
from .healer import (
    PrincipleHealer,
    create_principle_healer,
)

# === Loader ===
from .loader import (
    PrincipleLoader,
    create_principle_loader,
)

# === Stance ===
from .stance import (
    GENESIS_SIGNALS,
    KRISIS_SIGNALS,
    POIESIS_SIGNALS,
    THERAPEIA_SIGNALS,
    detect_stance,
    get_stance_slices,
    get_task_ad_slices,
    stance_from_aspect,
    validate_stance_transition,
)

# === Teacher ===
from .teacher import (
    PRINCIPLE_EXAMPLES,
    PRINCIPLE_EXERCISES,
    PrincipleTeacher,
    create_principle_teacher,
)

# === Types ===
from .types import (
    AD_TASK_MAPPING,
    PRINCIPLE_AD_MAPPING,
    PRINCIPLE_NAMES,
    PRINCIPLE_NUMBERS,
    # Constants
    STANCE_SLICES,
    THE_SEVEN_PRINCIPLES,
    THE_SEVEN_QUESTIONS,
    ADRendering,
    CheckResult,
    ConstitutionRendering,
    # Healing types
    HealingPrescription,
    MetaPrincipleRendering,
    OperationalRendering,
    # Core types
    Principle,
    # Check types
    PrincipleCheck,
    # Renderings
    PrincipleProjection,
    # Enums
    Stance,
    # Teaching types
    TeachingContent,
)

# === Exports ===

__all__ = [
    # Enums
    "Stance",
    # Constants
    "STANCE_SLICES",
    "THE_SEVEN_PRINCIPLES",
    "THE_SEVEN_QUESTIONS",
    "PRINCIPLE_NAMES",
    "PRINCIPLE_NUMBERS",
    "AD_TASK_MAPPING",
    "PRINCIPLE_AD_MAPPING",
    "PRINCIPLE_EXAMPLES",
    "PRINCIPLE_EXERCISES",
    # Core types
    "Principle",
    # Renderings
    "PrincipleProjection",
    "ConstitutionRendering",
    "MetaPrincipleRendering",
    "OperationalRendering",
    "ADRendering",
    # Check types
    "PrincipleCheck",
    "CheckResult",
    "CheckJudgment",
    # Healing types
    "HealingPrescription",
    # Teaching types
    "TeachingContent",
    # Loader
    "PrincipleLoader",
    "create_principle_loader",
    # Stance detection
    "detect_stance",
    "get_stance_slices",
    "get_task_ad_slices",
    "stance_from_aspect",
    "validate_stance_transition",
    "GENESIS_SIGNALS",
    "POIESIS_SIGNALS",
    "KRISIS_SIGNALS",
    "THERAPEIA_SIGNALS",
    # Checker
    "PrincipleChecker",
    "create_principle_checker",
    # Healer
    "PrincipleHealer",
    "create_principle_healer",
    # Teacher
    "PrincipleTeacher",
    "create_principle_teacher",
]
