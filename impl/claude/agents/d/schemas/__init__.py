"""
D-gent schemas - Versioned data contracts for the Crystal system.

Schemas define the shape of data independent of database models.
Each schema is a frozen dataclass with a version number.

Available schema domains:
- brain: Brain Crown Jewel schemas (crystals, settings)
- trail: Trail navigation and exploration schemas
- witness: Witness Crown Jewel schemas (marks, trust, thoughts, actions, escalations)
"""

from .brain import (
    BrainCrystal,
    BrainSetting,
    BRAIN_CRYSTAL_SCHEMA,
    BRAIN_SETTING_SCHEMA,
)
from .trail import (
    Trail,
    TRAIL_SCHEMA,
    TrailStep,
    TRAIL_STEP_SCHEMA,
    TrailCommitment,
    TRAIL_COMMITMENT_SCHEMA,
    TrailAnnotation,
    TRAIL_ANNOTATION_SCHEMA,
)
from .witness import (
    WitnessMark,
    WITNESS_MARK_SCHEMA,
    WitnessTrust,
    WITNESS_TRUST_SCHEMA,
    WitnessThought,
    WITNESS_THOUGHT_SCHEMA,
    WitnessAction,
    WITNESS_ACTION_SCHEMA,
    WitnessEscalation,
    WITNESS_ESCALATION_SCHEMA,
)

__all__ = [
    # Brain schemas
    "BrainCrystal",
    "BrainSetting",
    "BRAIN_CRYSTAL_SCHEMA",
    "BRAIN_SETTING_SCHEMA",
    # Trail schemas
    "Trail",
    "TRAIL_SCHEMA",
    "TrailStep",
    "TRAIL_STEP_SCHEMA",
    "TrailCommitment",
    "TRAIL_COMMITMENT_SCHEMA",
    "TrailAnnotation",
    "TRAIL_ANNOTATION_SCHEMA",
    # Witness schemas
    "WitnessMark",
    "WITNESS_MARK_SCHEMA",
    "WitnessTrust",
    "WITNESS_TRUST_SCHEMA",
    "WitnessThought",
    "WITNESS_THOUGHT_SCHEMA",
    "WitnessAction",
    "WITNESS_ACTION_SCHEMA",
    "WitnessEscalation",
    "WITNESS_ESCALATION_SCHEMA",
]
