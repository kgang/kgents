"""
The Gardener: Autopoietic Development Interface.

Crown Jewel #7 — N-Phase (Autopoiesis) stress test.

The Gardener is the interface through which Kent speaks with kgents to
evolve kgents itself. Every development session is a living entity that:
1. SENSEs context (forest, codebase, memory)
2. ACTs on intent (code, docs, plans)
3. REFLECTs learnings (meta.md, forest updates)

AGENTESE Paths:
    concept.gardener.session.create  — Start new development session
    concept.gardener.session.manifest — View current session state
    concept.gardener.session.resume  — Resume existing session
    concept.gardener.session.advance — Advance to next phase

See: plans/core-apps/the-gardener.md
"""

from __future__ import annotations

from .handlers import (
    GARDENER_HANDLERS,
    GardenerContext,
    register_gardener_handlers,
)
from .persistence import (
    SessionStore,
    create_session_store,
)
from .session import (
    GARDENER_SESSION_POLYNOMIAL,
    # Agent
    GardenerSession,
    SessionArtifact,
    SessionConfig,
    SessionIntent,
    # Phases
    SessionPhase,
    # Data structures
    SessionState,
    # Factory
    create_gardener_session,
    # Projections
    project_session_to_ascii,
    project_session_to_dict,
)

__all__ = [
    # Phases
    "SessionPhase",
    # Data structures
    "SessionState",
    "SessionConfig",
    "SessionIntent",
    "SessionArtifact",
    # Agent
    "GardenerSession",
    "GARDENER_SESSION_POLYNOMIAL",
    # Factory
    "create_gardener_session",
    # Persistence
    "SessionStore",
    "create_session_store",
    # Projections
    "project_session_to_ascii",
    "project_session_to_dict",
    # Handlers
    "GardenerContext",
    "GARDENER_HANDLERS",
    "register_gardener_handlers",
]
