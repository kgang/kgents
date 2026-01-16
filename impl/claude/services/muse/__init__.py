"""
Muse Crown Jewel: The Co-Creative Engine for Breakthrough Creativity.

From spec/c-gent/muse.md:
    "The goal is not AI-assisted creativity. The goal is Kent-at-10x—daring,
    bold, opinionated—with AI as the amplifier, contradictor, and relentless
    taste-enforcer."

The Muse service provides:
- Co-Creative Engine (30-50 iteration principle, volume generation)
- Cross-cutting Agents (taste, contradictor, ghost analyzer, checkpoints)
- Domain Pipelines (YouTube, Little Kant)
- Session Management (ground → spark → spiral → crystallize → witness)

Philosophy:
    "The Mirror Test: Does this feel like me on my best day?"

See: spec/c-gent/muse.md
See: spec/c-gent/muse-part-vi.md
"""

# =============================================================================
# Core Models
# =============================================================================

# =============================================================================
# Agents
# =============================================================================
from .agents import (
    AIDisagreement,
    CheckpointAgent,
    # Checkpoint Agent
    CheckpointProgress,
    ContradictionAnalytics,
    # Contradictor Agent
    ContradictionOutcome,
    ContradictorAgent,
    DriftReport,
    EffectiveContradiction,
    GhostAnalysis,
    GhostAnalyzerAgent,
    MirrorTestResult,
    PhaseProgress,
    # Ghost Analyzer Agent
    RejectionPattern,
    ResurrectionCandidate,
    TasteEvolution,
    # Taste Agent
    TasteScore,
    TasteVectorAgent,
    create_checkpoint_agent,
    create_contradictor,
    create_ghost_analyzer,
    create_little_kant_checkpoint_agent,
    create_taste_agent,
    create_youtube_checkpoint_agent,
    get_kent_default_taste,
)

# =============================================================================
# Checkpoints
# =============================================================================
from .checkpoints import (
    CHECKPOINT_TEMPLATES,
    LITTLE_KANT_CHECKPOINTS,
    # Templates
    YOUTUBE_CHECKPOINTS,
    # Types
    Checkpoint,
    CheckpointResult,
    # Enums
    CoCreativeMode,
    LockedElement,
    UnlockedElement,
    # Functions
    generate_checkpoint_id,
    get_checkpoint_by_name,
    get_checkpoints,
    get_checkpoints_by_phase,
)

# =============================================================================
# Engine
# =============================================================================
from .engine import (
    BreakthroughEvent,
    CheckpointEvent,
    ContradictionEvent,
    IterationEvent,
    # Orchestrator
    MuseOrchestrator,
    # Configuration
    OrchestratorConfig,
    SelectionEvent,
    # Events
    SessionEvent,
    create_little_kant_orchestrator,
    # Factory functions
    create_orchestrator,
    create_youtube_orchestrator,
)
from .models import (
    # Constants
    ITERATION_MILESTONES,
    KENT_TASTE_DEFAULT,
    VOLUME_TARGETS,
    # Enums
    AIRole,
    Contradiction,
    ContradictionMove,
    CreativeOption,
    DefenseResponse,
    Ghost,
    ResonanceLevel,
    SessionPhase,
    SessionState,
    # Core types
    TasteVector,
    generate_ghost_id,
    # ID generators
    generate_option_id,
)

# =============================================================================
# Pipelines
# =============================================================================
from .pipelines import (
    CANONICAL_PHILOSOPHERS,
    ConceptAgent,
    DilemmaAgent,
    DilemmaConstraints,
    EpisodeArchitectAgent,
    EpisodeStructure,
    EthicalDilemma,
    PhilosopherAgent,
    PhilosopherProfile,
    # Little Kant
    PhilosophicalTradition,
    ScriptAgent,
    ScriptDraft,
    ScriptSection,
    ThumbnailAgent,
    ThumbnailConcept,
    VideoConcept,
    # YouTube
    VideoDomain,
    VideoPromise,
    VideoScript,
    create_little_kant_pipeline,
    create_youtube_pipeline,
)

# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # === Core Models ===
    # Enums
    "AIRole",
    "ResonanceLevel",
    "ContradictionMove",
    "SessionPhase",
    # Core types
    "TasteVector",
    "KENT_TASTE_DEFAULT",
    "CreativeOption",
    "Ghost",
    "Contradiction",
    "DefenseResponse",
    "SessionState",
    # ID generators
    "generate_option_id",
    "generate_ghost_id",
    # Constants
    "ITERATION_MILESTONES",
    "VOLUME_TARGETS",
    # === Checkpoints ===
    "CoCreativeMode",
    "Checkpoint",
    "CheckpointResult",
    "LockedElement",
    "UnlockedElement",
    "YOUTUBE_CHECKPOINTS",
    "LITTLE_KANT_CHECKPOINTS",
    "CHECKPOINT_TEMPLATES",
    "generate_checkpoint_id",
    "get_checkpoints",
    "get_checkpoint_by_name",
    "get_checkpoints_by_phase",
    # === Taste Agent ===
    "TasteScore",
    "MirrorTestResult",
    "DriftReport",
    "TasteEvolution",
    "TasteVectorAgent",
    "create_taste_agent",
    "get_kent_default_taste",
    # === Contradictor Agent ===
    "ContradictionOutcome",
    "ContradictionAnalytics",
    "EffectiveContradiction",
    "ContradictorAgent",
    "create_contradictor",
    # === Ghost Analyzer Agent ===
    "RejectionPattern",
    "AIDisagreement",
    "ResurrectionCandidate",
    "GhostAnalysis",
    "GhostAnalyzerAgent",
    "create_ghost_analyzer",
    # === Checkpoint Agent ===
    "CheckpointProgress",
    "PhaseProgress",
    "CheckpointAgent",
    "create_checkpoint_agent",
    "create_youtube_checkpoint_agent",
    "create_little_kant_checkpoint_agent",
    # === Engine ===
    "OrchestratorConfig",
    "SessionEvent",
    "IterationEvent",
    "SelectionEvent",
    "ContradictionEvent",
    "BreakthroughEvent",
    "CheckpointEvent",
    "MuseOrchestrator",
    "create_orchestrator",
    "create_youtube_orchestrator",
    "create_little_kant_orchestrator",
    # === Little Kant Pipeline ===
    "PhilosophicalTradition",
    "PhilosopherProfile",
    "EthicalDilemma",
    "DilemmaConstraints",
    "EpisodeStructure",
    "CANONICAL_PHILOSOPHERS",
    "PhilosopherAgent",
    "DilemmaAgent",
    "EpisodeArchitectAgent",
    "create_little_kant_pipeline",
    # === YouTube Pipeline ===
    "VideoDomain",
    "VideoPromise",
    "VideoConcept",
    "ScriptSection",
    "VideoScript",
    "ScriptDraft",
    "ThumbnailConcept",
    "ConceptAgent",
    "ScriptAgent",
    "ThumbnailAgent",
    "create_youtube_pipeline",
]
