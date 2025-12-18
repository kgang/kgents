"""
Gardener AGENTESE Contract Definitions.

The 7th Crown Jewel - Development session orchestrator.
Implements SENSE -> ACT -> REFLECT polynomial state machine.

These contracts enable BE/FE type synchronization via AGENTESE discovery.

AGENTESE Paths:
- concept.gardener.manifest -> Gardener status
- concept.gardener.session.manifest -> View active session
- concept.gardener.session.define -> Start new session
- concept.gardener.session.advance -> Advance to next phase
- concept.gardener.session.polynomial -> Full polynomial visualization
- concept.gardener.sessions.manifest -> List recent sessions

Contract Protocol (Phase 7: Autopoietic Architecture):
- Response() for perception aspects (manifest, sessions, polynomial)
- Contract() for mutation aspects (define, advance)

@see protocols/agentese/contract.py
@see docs/skills/crown-jewel-patterns.md - Pattern 13: Contract-First Types
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# =============================================================================
# Phase Configuration
# =============================================================================

GardenerPhase = Literal["SENSE", "ACT", "REFLECT"]


# =============================================================================
# Manifest Response
# =============================================================================


@dataclass(frozen=True)
class ConceptGardenerManifestResponse:
    """Gardener health status manifest."""

    active_session_id: str | None
    active_session_name: str | None
    active_phase: GardenerPhase | None
    total_sessions: int
    polynomial_ascii: str


# =============================================================================
# Session Contracts
# =============================================================================


@dataclass(frozen=True)
class ConceptGardenerSessionManifestResponse:
    """Active session status response."""

    status: str  # "active" | "no_session"
    session_id: str | None = None
    name: str | None = None
    phase: GardenerPhase | None = None
    phase_emoji: str = ""
    phase_label: str = ""
    phase_desc: str = ""
    sense_count: int = 0
    act_count: int = 0
    reflect_count: int = 0
    intent: str | None = None
    plan_path: str | None = None
    polynomial: str = ""
    message: str | None = None


@dataclass(frozen=True)
class ConceptGardenerSessionDefineRequest:
    """Request to start a new polynomial session."""

    name: str | None = None
    plan_path: str | None = None
    intent_description: str | None = None
    intent_priority: str = "medium"


@dataclass(frozen=True)
class ConceptGardenerSessionDefineResponse:
    """Response after creating a new session."""

    status: str  # "created" | "error"
    session_id: str | None = None
    name: str | None = None
    phase: GardenerPhase | None = None
    polynomial: str = ""
    message: str = ""


@dataclass(frozen=True)
class ConceptGardenerSessionAdvanceRequest:
    """Request to advance to the next phase."""

    session_id: str | None = None  # Optional, uses active session if not provided


@dataclass(frozen=True)
class ConceptGardenerSessionAdvanceResponse:
    """Response after advancing phase."""

    status: str  # "advanced" | "error"
    phase: GardenerPhase | None = None
    phase_emoji: str = ""
    phase_label: str = ""
    phase_desc: str = ""
    polynomial: str = ""
    message: str = ""


# =============================================================================
# Polynomial Visualization
# =============================================================================


@dataclass(frozen=True)
class ConceptGardenerPolynomialResponse:
    """Full polynomial state visualization."""

    current_phase: GardenerPhase
    polynomial_ascii: str
    diagram: str
    valid_transitions: list[str] = field(default_factory=list)
    sense_count: int = 0
    act_count: int = 0
    reflect_count: int = 0


# =============================================================================
# Sessions List
# =============================================================================


@dataclass(frozen=True)
class ConceptGardenerSessionsListResponse:
    """List of recent sessions."""

    sessions: list[dict] = field(default_factory=list)
    count: int = 0
    active_id: str | None = None


# =============================================================================
# Route Contracts
# =============================================================================


@dataclass(frozen=True)
class ConceptGardenerRouteRequest:
    """Request to route natural language to AGENTESE path."""

    input: str
    use_llm: bool = True


@dataclass(frozen=True)
class ConceptGardenerRouteResponse:
    """Route result with resolved path."""

    original_input: str
    resolved_path: str
    confidence: float
    method: str  # "exact" | "pattern" | "llm" | "fallback"
    alternatives: list[str] = field(default_factory=list)
    explanation: str = ""


# =============================================================================
# Propose Contracts
# =============================================================================


@dataclass(frozen=True)
class ConceptGardenerProposeResponse:
    """Proactive suggestions for what to do next."""

    suggestion_count: int
    suggestions: list[dict] = field(default_factory=list)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Phase type
    "GardenerPhase",
    # Manifest
    "ConceptGardenerManifestResponse",
    # Session contracts
    "ConceptGardenerSessionManifestResponse",
    "ConceptGardenerSessionDefineRequest",
    "ConceptGardenerSessionDefineResponse",
    "ConceptGardenerSessionAdvanceRequest",
    "ConceptGardenerSessionAdvanceResponse",
    # Polynomial
    "ConceptGardenerPolynomialResponse",
    # Sessions list
    "ConceptGardenerSessionsListResponse",
    # Route
    "ConceptGardenerRouteRequest",
    "ConceptGardenerRouteResponse",
    # Propose
    "ConceptGardenerProposeResponse",
]
