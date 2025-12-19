"""
Soul AGENTESE Contract Definitions.

Defines request and response types for self.soul @node contracts.
These enable BE/FE contract synchronization via AGENTESE discovery.

Contract Protocol (Phase 7: Autopoietic Architecture):
- Response() for perception aspects (manifest, eigenvectors, starters)
- Contract() for mutation aspects (dialogue, challenge, reflect, mode)

Types here are used by:
1. @node(contracts={...}) in self_soul.py
2. /discover?include_schemas=true endpoint
3. web/scripts/sync-types.ts for FE type generation

AGENTESE: self.soul.*
"""

from __future__ import annotations

from dataclasses import dataclass, field

# === Eigenvectors ===


@dataclass(frozen=True)
class EigenvectorCoordinate:
    """A single personality eigenvector coordinate."""

    name: str
    axis_low: str
    axis_high: str
    value: float
    confidence: float


@dataclass(frozen=True)
class EigenvectorsResponse:
    """Response for eigenvectors aspect."""

    aesthetic: float
    categorical: float
    gratitude: float
    heterarchy: float
    generativity: float
    joy: float


# === Manifest ===


@dataclass(frozen=True)
class SoulManifestResponse:
    """Soul manifest response."""

    mode: str
    has_llm: bool
    eigenvectors: EigenvectorsResponse


# === Starters ===


@dataclass(frozen=True)
class StartersByMode:
    """Starters organized by dialogue mode."""

    reflect: list[str]
    advise: list[str]
    challenge: list[str]
    explore: list[str]


@dataclass(frozen=True)
class StartersRequest:
    """Request for starters, optionally filtered by mode."""

    mode: str | None = None


@dataclass(frozen=True)
class StartersResponse:
    """Response for starters aspect."""

    mode: str | None
    starters: list[str] | dict[str, list[str]]


# === Mode ===


@dataclass(frozen=True)
class ModeRequest:
    """Request to get or set dialogue mode."""

    set: str | None = None


@dataclass(frozen=True)
class ModeResponse:
    """Response for mode aspect."""

    mode: str
    status: str = "current"


# === Dialogue ===


@dataclass(frozen=True)
class DialogueRequest:
    """Request for dialogue aspect."""

    message: str
    mode: str | None = None


@dataclass(frozen=True)
class DialogueResponse:
    """Response for dialogue aspect."""

    response: str
    mode: str
    tokens_used: int
    was_template: bool = False


# === Challenge ===


@dataclass(frozen=True)
class ChallengeRequest:
    """Request for challenge aspect."""

    message: str


@dataclass(frozen=True)
class ChallengeResponse:
    """Response for challenge aspect."""

    response: str
    mode: str
    tokens_used: int


# === Reflect ===


@dataclass(frozen=True)
class ReflectRequest:
    """Request for reflect aspect."""

    message: str


@dataclass(frozen=True)
class ReflectResponse:
    """Response for reflect aspect."""

    response: str
    mode: str
    tokens_used: int


# === Why ===


@dataclass(frozen=True)
class WhyRequest:
    """Request for why aspect (purpose exploration)."""

    message: str | None = None
    topic: str | None = None


@dataclass(frozen=True)
class WhyResponse:
    """Response for why aspect."""

    response: str
    mode: str
    depth: str
    tokens_used: int


# === Tension ===


@dataclass(frozen=True)
class TensionRequest:
    """Request for tension aspect (creative tension exploration)."""

    message: str | None = None
    topic: str | None = None


@dataclass(frozen=True)
class TensionResponse:
    """Response for tension aspect."""

    response: str
    mode: str
    holding_space: bool
    tokens_used: int


# === Governance ===


@dataclass(frozen=True)
class GovernanceRequest:
    """Request for governance aspect (semantic gatekeeper)."""

    action: str
    context: dict[str, str] = field(default_factory=dict)
    budget: str = "dialogue"


@dataclass(frozen=True)
class GovernanceResponse:
    """Response for governance aspect."""

    approved: bool
    reasoning: str
    alternatives: list[str]
    confidence: float
    tokens_used: int
    recommendation: str
    principles: list[str]


# === Exports ===

__all__ = [
    # Eigenvectors
    "EigenvectorCoordinate",
    "EigenvectorsResponse",
    # Manifest
    "SoulManifestResponse",
    # Starters
    "StartersRequest",
    "StartersResponse",
    "StartersByMode",
    # Mode
    "ModeRequest",
    "ModeResponse",
    # Dialogue
    "DialogueRequest",
    "DialogueResponse",
    # Challenge
    "ChallengeRequest",
    "ChallengeResponse",
    # Reflect
    "ReflectRequest",
    "ReflectResponse",
    # Why
    "WhyRequest",
    "WhyResponse",
    # Tension
    "TensionRequest",
    "TensionResponse",
    # Governance
    "GovernanceRequest",
    "GovernanceResponse",
]
