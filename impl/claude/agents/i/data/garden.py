"""
Garden snapshot data types for Observatory view.

A garden is a collection of agents working together. The Observatory
view shows all gardens in the ecosystem.

HotData Integration (AD-004):
Demo functions use pre-computed fixtures when available,
with inline fallbacks for first-run scenarios.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from shared.hotdata import FIXTURES_DIR, HotData, register_hotdata


@dataclass
class GardenSnapshot:
    """
    Snapshot of a garden (collection of agents).

    Used by the ObservatoryScreen to display ecosystem-level view.
    """

    id: str
    name: str
    agent_ids: list[str] = field(default_factory=list)
    health: float = 0.0  # 0.0-1.0
    flux_rate: float = 0.0  # events/second
    orchestration_state: str = "idle"  # idle, converging, diverging, stable
    breath_phase: float = 0.0  # 0.0-1.0 for animation

    def __post_init__(self) -> None:
        """Validate fields."""
        self.health = max(0.0, min(1.0, self.health))
        self.flux_rate = max(0.0, self.flux_rate)
        self.breath_phase = max(0.0, min(1.0, self.breath_phase))

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "id": self.id,
            "name": self.name,
            "agent_ids": self.agent_ids,
            "health": self.health,
            "flux_rate": self.flux_rate,
            "orchestration_state": self.orchestration_state,
            "breath_phase": self.breath_phase,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GardenSnapshot":
        """Create from dict."""
        return cls(
            id=data["id"],
            name=data["name"],
            agent_ids=data.get("agent_ids", []),
            health=data.get("health", 0.0),
            flux_rate=data.get("flux_rate", 0.0),
            orchestration_state=data.get("orchestration_state", "idle"),
            breath_phase=data.get("breath_phase", 0.0),
        )


@dataclass
class PolynomialState:
    """
    Polynomial agent state for Cockpit view.

    Shows current mode, valid transitions, and state hash.
    """

    current_mode: str
    valid_inputs: list[str] = field(default_factory=list)
    state_hash: str = ""
    transition_history: list[tuple[str, str]] = field(
        default_factory=list
    )  # [(from_mode, to_mode), ...]

    def get_valid_transitions(self) -> list[str]:
        """Get list of valid next modes."""
        # Simple state machine inference from valid_inputs
        # In practice, this would be more sophisticated
        return self.valid_inputs

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "current_mode": self.current_mode,
            "valid_inputs": self.valid_inputs,
            "state_hash": self.state_hash,
            "transition_history": self.transition_history,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PolynomialState":
        """Create from dict."""
        history = data.get("transition_history", [])
        # Convert lists to tuples
        if history and isinstance(history[0], list):
            history = [tuple(h) for h in history]
        return cls(
            current_mode=data["current_mode"],
            valid_inputs=data.get("valid_inputs", []),
            state_hash=data.get("state_hash", ""),
            transition_history=history,
        )


@dataclass
class YieldTurn:
    """
    A YIELD turn awaiting approval in the Cockpit.
    """

    id: str
    content: str
    turn_type: str  # "YIELD:ACTION", "YIELD:SPEECH", etc
    timestamp: float
    is_approved: bool = False
    reason: str = ""  # Rejection reason if applicable

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "id": self.id,
            "content": self.content,
            "turn_type": self.turn_type,
            "timestamp": self.timestamp,
            "is_approved": self.is_approved,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "YieldTurn":
        """Create from dict."""
        return cls(
            id=data["id"],
            content=data["content"],
            turn_type=data["turn_type"],
            timestamp=data.get("timestamp", 0.0),
            is_approved=data.get("is_approved", False),
            reason=data.get("reason", ""),
        )


# ─────────────────────────────────────────────────────────────────────────────
# List Wrapper Classes for HotData serialization
# ─────────────────────────────────────────────────────────────────────────────


class GardenList:
    """Wrapper for list[GardenSnapshot] with serialization."""

    def __init__(self, gardens: list[GardenSnapshot]) -> None:
        self.gardens = gardens

    @classmethod
    def from_dict(cls, data: list[dict[str, Any]]) -> "GardenList":
        """Create from list of dicts."""
        return cls([GardenSnapshot.from_dict(d) for d in data])


class YieldTurnList:
    """Wrapper for list[YieldTurn] with serialization."""

    def __init__(self, turns: list[YieldTurn]) -> None:
        self.turns = turns

    @classmethod
    def from_dict(cls, data: list[dict[str, Any]]) -> "YieldTurnList":
        """Create from list of dicts."""
        return cls([YieldTurn.from_dict(d) for d in data])


# ─────────────────────────────────────────────────────────────────────────────
# HotData Fixtures (AD-004: Pre-Computed Richness)
# ─────────────────────────────────────────────────────────────────────────────

# Note: We use raw JSON loading for lists since HotData expects single objects

DEMO_GARDENS_PATH = FIXTURES_DIR / "garden_states" / "demo.json"
DEMO_POLYNOMIAL_STATE_HOTDATA = HotData(
    path=FIXTURES_DIR / "polynomial_states" / "demo.json",
    schema=PolynomialState,
)
DEMO_YIELD_TURNS_PATH = FIXTURES_DIR / "yield_turns" / "demo.json"

# Register with global registry
register_hotdata("demo_polynomial_state", DEMO_POLYNOMIAL_STATE_HOTDATA)


def _create_fallback_gardens() -> list[GardenSnapshot]:
    """Create inline fallback gardens (used when fixture is missing)."""
    return [
        GardenSnapshot(
            id="main",
            name="main",
            agent_ids=["K-gent", "A-gent", "L-gent", "D-gent", "E-gent"],
            health=0.8,
            flux_rate=2.3,
            orchestration_state="converging",
            breath_phase=0.5,
        ),
        GardenSnapshot(
            id="experiment-alpha",
            name="experiment-α",
            agent_ids=["robin", "test", "valid"],
            health=0.45,
            flux_rate=0.4,
            orchestration_state="diverging",
            breath_phase=0.2,
        ),
    ]


def _create_fallback_polynomial_state() -> PolynomialState:
    """Create inline fallback polynomial state (used when fixture is missing)."""
    return PolynomialState(
        current_mode="DELIBERATING",
        valid_inputs=["Claim", "Evidence", "Objection"],
        state_hash="7a3f2e1d",
        transition_history=[
            ("GROUNDING", "DELIBERATING"),
        ],
    )


def _create_fallback_yield_turns() -> list[YieldTurn]:
    """Create inline fallback yield turns (used when fixture is missing)."""
    import time

    now = time.time()

    return [
        YieldTurn(
            id="yield-1",
            content="Execute deployment script to production?",
            turn_type="YIELD:ACTION",
            timestamp=now - 5,
        ),
        YieldTurn(
            id="yield-2",
            content="Publish package to npm registry?",
            turn_type="YIELD:ACTION",
            timestamp=now - 10,
        ),
    ]


def create_demo_gardens() -> list[GardenSnapshot]:
    """
    Create demo garden snapshots for testing.

    HotData Integration (AD-004):
    - Loads from pre-computed fixture when available
    - Falls back to inline definition for first-run scenarios
    """
    if DEMO_GARDENS_PATH.exists():
        try:
            data = json.loads(DEMO_GARDENS_PATH.read_text())
            return [GardenSnapshot.from_dict(d) for d in data]
        except (json.JSONDecodeError, KeyError):
            pass
    return _create_fallback_gardens()


def create_demo_polynomial_state() -> PolynomialState:
    """
    Create demo polynomial state for testing.

    HotData Integration (AD-004):
    - Loads from pre-computed fixture when available
    - Falls back to inline definition for first-run scenarios
    """
    return DEMO_POLYNOMIAL_STATE_HOTDATA.load_or_default(
        _create_fallback_polynomial_state()
    )


def create_demo_yield_turns() -> list[YieldTurn]:
    """
    Create demo yield turns for testing.

    HotData Integration (AD-004):
    - Loads from pre-computed fixture when available
    - Falls back to inline definition for first-run scenarios
    """
    if DEMO_YIELD_TURNS_PATH.exists():
        try:
            import time

            data = json.loads(DEMO_YIELD_TURNS_PATH.read_text())
            turns: list[YieldTurn] = []
            now = time.time()
            for d in data:
                # If timestamp is 0, use current time offset
                if d.get("timestamp", 0) == 0:
                    d["timestamp"] = now - 5.0 * (len(turns) + 1)
                turns.append(YieldTurn.from_dict(d))
            return turns
        except (json.JSONDecodeError, KeyError):
            pass
    return _create_fallback_yield_turns()
