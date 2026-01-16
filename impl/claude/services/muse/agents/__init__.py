"""
Muse Agents: Cross-cutting agents for the Co-Creative Engine.

These agents are used by both project-specific pipelines (Little Kant, YouTube)
to implement the core Muse principles:

- TasteVectorAgent: The externalized Mirror Test
- ContradictorAgent: The dialectical challenger
- GhostAnalyzerAgent: Captures paths not taken
- CheckpointAgent: CGP Grey's 66-checkpoint discipline

See: spec/c-gent/muse.md
"""

from .checkpoint import (
    CheckpointAgent,
    CheckpointProgress,
    PhaseProgress,
    create_checkpoint_agent,
    create_little_kant_checkpoint_agent,
    create_youtube_checkpoint_agent,
)
from .contradictor import (
    ContradictionAnalytics,
    ContradictionOutcome,
    ContradictorAgent,
    EffectiveContradiction,
    create_contradictor,
)
from .ghost import (
    AIDisagreement,
    GhostAnalysis,
    GhostAnalyzerAgent,
    RejectionPattern,
    ResurrectionCandidate,
    create_ghost_analyzer,
)
from .taste import (
    DriftReport,
    MirrorTestResult,
    TasteEvolution,
    TasteScore,
    TasteVectorAgent,
    create_taste_agent,
    get_kent_default_taste,
)

__all__ = [
    # Taste Agent
    "TasteScore",
    "MirrorTestResult",
    "DriftReport",
    "TasteEvolution",
    "TasteVectorAgent",
    "create_taste_agent",
    "get_kent_default_taste",
    # Contradictor Agent
    "ContradictionOutcome",
    "ContradictionAnalytics",
    "EffectiveContradiction",
    "ContradictorAgent",
    "create_contradictor",
    # Ghost Analyzer Agent
    "RejectionPattern",
    "AIDisagreement",
    "ResurrectionCandidate",
    "GhostAnalysis",
    "GhostAnalyzerAgent",
    "create_ghost_analyzer",
    # Checkpoint Agent
    "CheckpointProgress",
    "PhaseProgress",
    "CheckpointAgent",
    "create_checkpoint_agent",
    "create_youtube_checkpoint_agent",
    "create_little_kant_checkpoint_agent",
]
