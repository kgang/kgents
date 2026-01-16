"""
Muse Pipelines: Domain-specific agent pipelines.

Pipelines compose cross-cutting agents with domain-specific agents
to create complete creative workflows.

Available Pipelines:
- Little Kant: Children's ethics show production
- YouTube: Video content creation

See: spec/c-gent/muse.md
"""

from .little_kant import (
    # Canonical data
    CANONICAL_PHILOSOPHERS,
    DilemmaAgent,
    DilemmaConstraints,
    EpisodeArchitectAgent,
    EpisodeStructure,
    EthicalDilemma,
    # Agents
    PhilosopherAgent,
    # Types
    PhilosopherProfile,
    # Enums
    PhilosophicalTradition,
    # Factory
    create_little_kant_pipeline,
)
from .youtube import (
    # Agents
    ConceptAgent,
    ScriptAgent,
    ScriptDraft,
    ScriptSection,
    ThumbnailAgent,
    ThumbnailConcept,
    VideoConcept,
    # Enums
    VideoDomain,
    # Types
    VideoPromise,
    VideoScript,
    # Factory
    create_youtube_pipeline,
)

__all__ = [
    # === Little Kant Pipeline ===
    # Enums
    "PhilosophicalTradition",
    # Types
    "PhilosopherProfile",
    "EthicalDilemma",
    "DilemmaConstraints",
    "EpisodeStructure",
    # Canonical data
    "CANONICAL_PHILOSOPHERS",
    # Agents
    "PhilosopherAgent",
    "DilemmaAgent",
    "EpisodeArchitectAgent",
    # Factory
    "create_little_kant_pipeline",
    # === YouTube Pipeline ===
    # Enums
    "VideoDomain",
    # Types
    "VideoPromise",
    "VideoConcept",
    "ScriptSection",
    "VideoScript",
    "ScriptDraft",
    "ThumbnailConcept",
    # Agents
    "ConceptAgent",
    "ScriptAgent",
    "ThumbnailAgent",
    # Factory
    "create_youtube_pipeline",
]
