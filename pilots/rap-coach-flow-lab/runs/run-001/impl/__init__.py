"""
Rap Coach Flow Lab Implementation.

This package implements the Joy Integration and Courage Preservation
theory for the rap-coach pilot.

Core Components:
    - joy_functor: RAP_COACH_JOY functor with courage-aware observations
    - courage_preservation: L4 Courage Preservation Law enforcement
    - voice_crystal: Voice-aware crystal compression (L3, L4, L5)

Laws Implemented:
    L1 Intent Declaration: Take only valid if intent explicit before analysis
    L2 Feedback Grounding: All critique references mark or trace segment
    L3 Voice Continuity: Crystal identifies through-line of voice
    L4 Courage Preservation: High-risk takes protected from negative weighting
    L5 Repair Path: High loss proposes repair path, not verdict

Joy Calibration:
    WARMTH:   0.9 (primary - the kind coach)
    SURPRISE: 0.3 (secondary - unexpected voice breakthroughs)
    FLOW:     0.7 (tertiary - creative momentum)

See: pilots/rap-coach-flow-lab/PROTO_SPEC.md
See: plans/enlightened-synthesis/04-joy-integration.md
"""

from .courage_preservation import (
    AntiJudgeDetector,
    CourageMoment,
    CourageProtectionEngine,
    RiskLevel,
    TakeMark,
)
from .joy_functor import (
    RAP_COACH_JOY,
    CourageAwareJoyObservation,
    RAP_COACH_WARMTH_TEMPLATES,
    SessionJoyProfile,
    rap_coach_warmth_response,
)
from .voice_crystal import (
    RepairPath,
    VoiceCrystal,
    VoiceDelta,
    VoiceThroughline,
)

__all__ = [
    # Joy
    "RAP_COACH_JOY",
    "CourageAwareJoyObservation",
    "RAP_COACH_WARMTH_TEMPLATES",
    "rap_coach_warmth_response",
    "SessionJoyProfile",
    # Courage
    "RiskLevel",
    "CourageMoment",
    "CourageProtectionEngine",
    "TakeMark",
    "AntiJudgeDetector",
    # Crystal
    "VoiceDelta",
    "VoiceThroughline",
    "RepairPath",
    "VoiceCrystal",
]
