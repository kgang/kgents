"""
Muse AGENTESE Contracts: Type-safe request/response definitions.

These dataclasses define the contracts for all MuseNode aspects.
They serve as the single source of truth for BE/FE type alignment.

Pattern 13 (Contract-First Types):
- @node(contracts={...}) is the authority
- Frontend discovers contracts at build time
- Type drift caught in CI

See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# =============================================================================
# Manifest Aspect (Response only)
# =============================================================================


@dataclass
class MuseManifestResponse:
    """Response for manifest aspect."""

    state: str  # MuseState name
    arc_phase: str  # ArcPhase name
    arc_confidence: float
    tension: float
    tension_trend: float
    crystals_observed: int
    whispers_made: int
    whispers_accepted: int
    whispers_dismissed: int
    acceptance_rate: float
    can_whisper: bool
    pending_whisper_id: str | None
    status: str  # "silent", "contemplating", "whispering", "resonating", "reflecting", "dormant"


# =============================================================================
# Arc Aspect
# =============================================================================


@dataclass
class ArcRequest:
    """Request for arc aspect - get current story arc."""

    include_history: bool = False


@dataclass
class ArcResponse:
    """Response for arc aspect."""

    phase: str  # ArcPhase name
    phase_emoji: str
    confidence: float
    tension: float
    momentum: float
    phase_duration_seconds: float
    is_rising: bool
    is_falling: bool
    is_peak: bool


# =============================================================================
# Tension Aspect
# =============================================================================


@dataclass
class TensionRequest:
    """Request for tension aspect."""

    include_trend: bool = True


@dataclass
class TensionResponse:
    """Response for tension aspect."""

    level: float  # Current tension [0, 1]
    trend: float  # Rate of change [-1, 1]
    category: str  # "low", "medium", "high", "critical"
    trigger: str | None  # What caused the current tension


# =============================================================================
# Whisper Aspect
# =============================================================================


@dataclass
class WhisperRequest:
    """Request for whisper aspect - get current whisper if any."""

    pass  # No parameters needed


@dataclass
class WhisperResponse:
    """Response for whisper aspect."""

    has_whisper: bool
    whisper_id: str | None = None
    content: str | None = None
    category: str | None = None  # "encouragement", "reframe", "observation", "suggestion"
    urgency: float | None = None
    confidence: float | None = None
    timestamp: str | None = None


# =============================================================================
# Encourage Aspect
# =============================================================================


@dataclass
class EncourageRequest:
    """Request for encourage aspect - request earned encouragement."""

    context: str = ""  # Optional context about what user is working on


@dataclass
class EncourageResponse:
    """Response for encourage aspect."""

    whisper_id: str
    content: str
    earned: bool  # Whether this is earned vs requested
    arc_phase: str
    tension: float
    timestamp: str


# =============================================================================
# Reframe Aspect
# =============================================================================


@dataclass
class ReframeRequest:
    """Request for reframe aspect - request perspective shift."""

    context: str = ""  # What user wants reframed
    current_perspective: str = ""  # User's current view


@dataclass
class ReframeResponse:
    """Response for reframe aspect."""

    whisper_id: str
    content: str
    original_perspective: str
    new_perspective: str
    arc_phase: str
    timestamp: str


# =============================================================================
# Summon Aspect
# =============================================================================


@dataclass
class SummonRequest:
    """Request for summon aspect - force suggestion (bypass timing)."""

    topic: str = ""  # Optional topic to focus on


@dataclass
class SummonResponse:
    """Response for summon aspect."""

    whisper_id: str
    content: str
    category: str
    confidence: float
    summoned: bool  # Always true for summon
    timestamp: str


# =============================================================================
# Dismiss Aspect
# =============================================================================


@dataclass
class DismissRequest:
    """Request for dismiss aspect - dismiss current whisper."""

    whisper_id: str
    reason: str = ""  # Optional reason for dismissal


@dataclass
class DismissResponse:
    """Response for dismiss aspect."""

    dismissed: bool
    whisper_id: str
    cooldown_minutes: int
    timestamp: str


# =============================================================================
# Accept Aspect
# =============================================================================


@dataclass
class AcceptRequest:
    """Request for accept aspect - accept/acknowledge a whisper."""

    whisper_id: str
    action: str = "acknowledged"  # "acknowledged", "acted", "saved"


@dataclass
class AcceptResponse:
    """Response for accept aspect."""

    accepted: bool
    whisper_id: str
    action: str
    timestamp: str


# =============================================================================
# History Aspect
# =============================================================================


@dataclass
class HistoryRequest:
    """Request for history aspect - get whisper history."""

    limit: int = 20
    category: str | None = None  # Filter by category
    accepted_only: bool = False


@dataclass
class WhisperHistoryItem:
    """A single whisper in history."""

    whisper_id: str
    content: str
    category: str
    urgency: float
    confidence: float
    arc_phase: str
    tension: float
    accepted: bool
    dismissed: bool
    timestamp: str


@dataclass
class HistoryResponse:
    """Response for history aspect."""

    count: int
    whispers: list[WhisperHistoryItem] = field(default_factory=list)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Manifest
    "MuseManifestResponse",
    # Arc
    "ArcRequest",
    "ArcResponse",
    # Tension
    "TensionRequest",
    "TensionResponse",
    # Whisper
    "WhisperRequest",
    "WhisperResponse",
    # Encourage
    "EncourageRequest",
    "EncourageResponse",
    # Reframe
    "ReframeRequest",
    "ReframeResponse",
    # Summon
    "SummonRequest",
    "SummonResponse",
    # Dismiss
    "DismissRequest",
    "DismissResponse",
    # Accept
    "AcceptRequest",
    "AcceptResponse",
    # History
    "HistoryRequest",
    "HistoryResponse",
    "WhisperHistoryItem",
]
