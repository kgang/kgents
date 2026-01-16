"""
Muse Engine: The Co-Creative Engine core components.

The engine provides:
- MuseOrchestrator: Coordinates the full creative workflow
- Session management and lifecycle
- Agent coordination

See: spec/c-gent/muse.md
"""

from .orchestrator import (
    BreakthroughEvent,
    CheckpointEvent,
    ContradictionEvent,
    IterationEvent,
    MuseOrchestrator,
    OrchestratorConfig,
    SelectionEvent,
    SessionEvent,
    create_little_kant_orchestrator,
    create_orchestrator,
    create_youtube_orchestrator,
)

__all__ = [
    # Configuration
    "OrchestratorConfig",
    # Events
    "SessionEvent",
    "IterationEvent",
    "SelectionEvent",
    "ContradictionEvent",
    "BreakthroughEvent",
    "CheckpointEvent",
    # Orchestrator
    "MuseOrchestrator",
    # Factory functions
    "create_orchestrator",
    "create_youtube_orchestrator",
    "create_little_kant_orchestrator",
]
