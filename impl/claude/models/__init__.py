"""
SQLAlchemy Models + Crystal Schema Re-exports

This module provides two data layers:
1. SQLAlchemy ORM models (for traditional DB operations)
2. D-gent Crystal schemas (for versioned data contracts)

Crown Jewel Tables:
- brain.py: Crystal, BrainSettings, TeachingCrystal, ExtinctionEvent
- witness.py: WitnessMark, WitnessTrust, WitnessThought, WitnessAction, WitnessEscalation
- trail.py: TrailRow, TrailStepRow, TrailAnnotationRow, TrailCommitmentRow
- annotation.py: SpecAnnotationRow
- ashc.py: VerifiedLemmaModel
- sovereign.py: SovereignCollectionRow, SovereignPlaceholderRow
- onboarding.py: OnboardingSession

Note: town.py removed 2025-12-21 (extinct).
"""

# Base infrastructure
from .base import (
    Base,
    CausalMixin,
    TimestampMixin,
    close_db,
    get_async_session,
    get_engine,
    init_db,
)

# Brain Crown Jewel
from .brain import (
    BrainSettings,
    Crystal,
    CrystalTag,
    ExtinctionEvent,
    ExtinctionTeaching,
    TeachingCrystal,
)

# Witness Crown Jewel
from .witness import (
    WitnessAction,
    WitnessEscalation,
    WitnessMark,
    WitnessThought,
    WitnessTrust,
)

# Trail Protocol
from .trail import (
    TrailAnnotationRow,
    TrailCommitmentRow,
    TrailEvidenceRow,
    TrailForkRow,
    TrailRow,
    TrailStepRow,
)

# Annotation Service
from .annotation import SpecAnnotationRow

# ASHC Crown Jewel
from .ashc import VerifiedLemmaModel

# Sovereign Crown Jewel
from .sovereign import SovereignCollectionRow, SovereignPlaceholderRow

# Onboarding
from .onboarding import OnboardingSession

# Feed Feedback
from .feed_feedback import FeedEngagementStats, FeedInteraction

__all__ = [
    # Base infrastructure
    "Base",
    "TimestampMixin",
    "CausalMixin",
    "get_async_session",
    "get_engine",
    "init_db",
    "close_db",
    # Brain
    "Crystal",
    "CrystalTag",
    "BrainSettings",
    "TeachingCrystal",
    "ExtinctionEvent",
    "ExtinctionTeaching",
    # Witness
    "WitnessMark",
    "WitnessTrust",
    "WitnessThought",
    "WitnessAction",
    "WitnessEscalation",
    # Trail
    "TrailRow",
    "TrailStepRow",
    "TrailAnnotationRow",
    "TrailForkRow",
    "TrailEvidenceRow",
    "TrailCommitmentRow",
    # Annotation
    "SpecAnnotationRow",
    # ASHC
    "VerifiedLemmaModel",
    # Sovereign
    "SovereignCollectionRow",
    "SovereignPlaceholderRow",
    # Onboarding
    "OnboardingSession",
    # Feed Feedback
    "FeedInteraction",
    "FeedEngagementStats",
]
