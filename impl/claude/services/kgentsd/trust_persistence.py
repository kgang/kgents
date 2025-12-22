"""
TrustPersistence: JSON-Based State Persistence for the Witness Daemon.

"Trust is earned, and earned trust should persist."

Phase 4C: Saves witness trust state to ~/.kgents/witness.json
This ensures trust level survives daemon restarts.

Persisted State:
- trust_level: Current trust level (L0-L3)
- observation_count: Total observations made
- successful_operations: Successful bounded operations
- confirmed_suggestions: Confirmed L2 suggestions
- total_suggestions: Total suggestions made
- acceptance_rate: Suggestion acceptance rate
- last_active: Last activity timestamp

Philosophy:
    Trust takes time to earn, so it should never be lost to a restart.
    Decay still applies on load (24h inactivity reduces trust).

See: plans/kgentsd-phase4b-prompt.md
See: spec/principles.md (Ethical principle - transparent state)
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from services.witness.polynomial import TrustLevel

logger = logging.getLogger(__name__)


# =============================================================================
# Default Paths
# =============================================================================

KGENTS_DIR = Path.home() / ".kgents"
WITNESS_STATE_FILE = KGENTS_DIR / "witness.json"


# =============================================================================
# Persisted State
# =============================================================================


@dataclass
class PersistedTrustState:
    """
    Trust state that persists across daemon restarts.

    This is a subset of WitnessState focused on trust metrics.
    """

    # Trust level
    trust_level: int = 0  # TrustLevel value (0-3)
    trust_level_raw: float = 0.0  # Raw level for decay calculations

    # Metrics for escalation
    observation_count: int = 0
    successful_operations: int = 0
    confirmed_suggestions: int = 0
    total_suggestions: int = 0

    # Timestamps
    last_active_iso: str = ""  # ISO format datetime
    first_observed_iso: str = ""  # When trust was first established

    # Version for future migrations
    version: int = 1

    @property
    def trust(self) -> TrustLevel:
        """Get trust level as TrustLevel enum."""
        return TrustLevel(min(self.trust_level, 3))

    @property
    def last_active(self) -> datetime | None:
        """Get last_active as datetime."""
        if not self.last_active_iso:
            return None
        try:
            return datetime.fromisoformat(self.last_active_iso)
        except ValueError:
            return None

    @property
    def acceptance_rate(self) -> float:
        """Calculate suggestion acceptance rate."""
        if self.total_suggestions == 0:
            return 0.0
        return self.confirmed_suggestions / self.total_suggestions

    def apply_decay(self) -> bool:
        """
        Apply trust decay based on inactivity.

        Decay rule: -0.1 levels per 24h of inactivity.
        Floor: L1 (never drops below L1 after first achievement).

        Returns:
            True if decay was applied
        """
        if self.last_active is None:
            return False

        inactive_hours = (datetime.now() - self.last_active).total_seconds() / 3600
        if inactive_hours < 24:
            return False

        # Calculate decay
        decay_amount = (inactive_hours / 24) * 0.1
        old_raw = self.trust_level_raw
        self.trust_level_raw = max(1.0, self.trust_level_raw - decay_amount)  # Floor at L1

        # Update discrete level
        self.trust_level = int(self.trust_level_raw)

        decayed = old_raw != self.trust_level_raw
        if decayed:
            logger.info(
                f"Trust decay applied: {old_raw:.2f} -> {self.trust_level_raw:.2f} "
                f"(inactive {inactive_hours:.1f}h)"
            )

        return decayed

    def touch(self) -> None:
        """Update last_active to now."""
        self.last_active_iso = datetime.now().isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "trust_level": self.trust_level,
            "trust_level_raw": self.trust_level_raw,
            "observation_count": self.observation_count,
            "successful_operations": self.successful_operations,
            "confirmed_suggestions": self.confirmed_suggestions,
            "total_suggestions": self.total_suggestions,
            "last_active_iso": self.last_active_iso,
            "first_observed_iso": self.first_observed_iso,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PersistedTrustState":
        """Create from dictionary."""
        return cls(
            trust_level=data.get("trust_level", 0),
            trust_level_raw=data.get("trust_level_raw", 0.0),
            observation_count=data.get("observation_count", 0),
            successful_operations=data.get("successful_operations", 0),
            confirmed_suggestions=data.get("confirmed_suggestions", 0),
            total_suggestions=data.get("total_suggestions", 0),
            last_active_iso=data.get("last_active_iso", ""),
            first_observed_iso=data.get("first_observed_iso", ""),
            version=data.get("version", 1),
        )


# =============================================================================
# TrustPersistence Class
# =============================================================================


class TrustPersistence:
    """
    Manages persistence of witness trust state to disk.

    Handles:
    - Loading state from ~/.kgents/witness.json
    - Saving state on trust changes
    - Applying decay on load
    - Creating backups before overwrite

    Example:
        persistence = TrustPersistence()

        # Load existing state (with decay applied)
        state = await persistence.load()

        # Update and save
        state.observation_count += 1
        state.touch()
        await persistence.save(state)

        # Get current state without reloading
        current = persistence.current_state
    """

    def __init__(
        self,
        state_file: Path | None = None,
        auto_save: bool = True,
    ) -> None:
        """
        Initialize trust persistence.

        Args:
            state_file: Path to state file (default: ~/.kgents/witness.json)
            auto_save: Whether to save after each update (default: True)
        """
        self.state_file = state_file or WITNESS_STATE_FILE
        self.auto_save = auto_save
        self._state: PersistedTrustState | None = None
        self._dirty = False

    @property
    def current_state(self) -> PersistedTrustState:
        """Get current state (load if not loaded)."""
        if self._state is None:
            # Synchronous fallback - prefer using load()
            self._state = self._load_sync()
        return self._state

    async def load(self, apply_decay: bool = True) -> PersistedTrustState:
        """
        Load trust state from disk.

        If no state file exists, creates a fresh L0 state.
        Optionally applies trust decay based on inactivity.

        Args:
            apply_decay: Whether to apply decay on load (default: True)

        Returns:
            PersistedTrustState
        """
        state = self._load_sync()

        if apply_decay and state.apply_decay():
            # Decay was applied, save updated state
            await self.save(state)

        self._state = state
        return state

    def _load_sync(self) -> PersistedTrustState:
        """Synchronous load for initialization."""
        if not self.state_file.exists():
            logger.info(f"No existing state at {self.state_file}, starting fresh")
            state = PersistedTrustState()
            state.first_observed_iso = datetime.now().isoformat()
            state.touch()
            # Save initial state so file exists
            self._save_sync(state)
            return state

        try:
            data = json.loads(self.state_file.read_text())
            state = PersistedTrustState.from_dict(data)
            logger.info(
                f"Loaded trust state: L{state.trust_level} ({state.observation_count} observations)"
            )
            return state
        except Exception as e:
            logger.error(f"Failed to load trust state: {e}")
            # Return fresh state on error
            return PersistedTrustState()

    def _save_sync(self, state: PersistedTrustState) -> bool:
        """Synchronous save for initialization."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.state_file.write_text(json.dumps(state.to_dict(), indent=2))
            logger.info(f"Initial trust state saved to {self.state_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save initial trust state: {e}")
            return False

    async def save(self, state: PersistedTrustState | None = None) -> bool:
        """
        Save trust state to disk.

        Creates parent directory if needed.
        Creates a backup before overwriting.

        Args:
            state: State to save (uses current_state if None)

        Returns:
            True if save succeeded
        """
        if state is None:
            state = self.current_state

        try:
            # Ensure directory exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            # Create backup if file exists
            if self.state_file.exists():
                backup = self.state_file.with_suffix(".json.bak")
                backup.write_text(self.state_file.read_text())

            # Write new state
            self.state_file.write_text(json.dumps(state.to_dict(), indent=2))

            self._state = state
            self._dirty = False
            logger.debug(f"Trust state saved to {self.state_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save trust state: {e}")
            return False

    async def record_observation(self) -> None:
        """Record an observation and auto-save if enabled."""
        state = self.current_state
        state.observation_count += 1
        state.touch()

        if self.auto_save:
            await self.save(state)

    async def record_operation(self, success: bool = True) -> None:
        """Record a bounded operation and auto-save if enabled."""
        state = self.current_state
        if success:
            state.successful_operations += 1
        state.touch()

        if self.auto_save:
            await self.save(state)

    async def record_suggestion(self, confirmed: bool) -> None:
        """Record a suggestion response and auto-save if enabled."""
        state = self.current_state
        state.total_suggestions += 1
        if confirmed:
            state.confirmed_suggestions += 1
        state.touch()

        if self.auto_save:
            await self.save(state)

    async def escalate(self, to_level: TrustLevel, reason: str = "") -> bool:
        """
        Escalate trust level.

        Args:
            to_level: Target trust level
            reason: Reason for escalation (logged)

        Returns:
            True if escalation succeeded
        """
        state = self.current_state
        old_level = state.trust_level

        if to_level.value <= old_level:
            logger.warning(f"Cannot escalate from L{old_level} to L{to_level.value}")
            return False

        state.trust_level = to_level.value
        state.trust_level_raw = float(to_level.value)
        state.touch()

        logger.info(f"Trust escalated: L{old_level} -> L{to_level.value} ({reason})")

        if self.auto_save:
            await self.save(state)

        return True

    def get_status(self) -> dict[str, Any]:
        """Get current trust status for display."""
        state = self.current_state
        level = state.trust

        return {
            "trust_level": level.name,
            "trust_level_value": level.value,
            "trust_emoji": level.emoji,
            "trust_description": level.description,
            "observation_count": state.observation_count,
            "successful_operations": state.successful_operations,
            "confirmed_suggestions": state.confirmed_suggestions,
            "total_suggestions": state.total_suggestions,
            "acceptance_rate": f"{state.acceptance_rate:.0%}",
            "last_active": state.last_active_iso,
            "escalation_progress": self._calculate_progress(state),
        }

    def _calculate_progress(self, state: PersistedTrustState) -> dict[str, Any]:
        """Calculate progress toward next trust level."""
        level = state.trust_level

        if level == 0:
            # L0 → L1: Need 24h + 100 observations
            obs_progress = min(state.observation_count / 100, 1.0)
            hours = 0.0
            if state.last_active:
                first = (
                    datetime.fromisoformat(state.first_observed_iso)
                    if state.first_observed_iso
                    else datetime.now()
                )
                hours = (datetime.now() - first).total_seconds() / 3600
            time_progress = min(hours / 24, 1.0)
            return {
                "next_level": "L1 BOUNDED",
                "observations_needed": max(0, 100 - state.observation_count),
                "hours_remaining": max(0, 24 - hours),
                "overall_progress": min(obs_progress, time_progress),
            }

        elif level == 1:
            # L1 → L2: Need 100 successful operations
            return {
                "next_level": "L2 SUGGESTION",
                "operations_needed": max(0, 100 - state.successful_operations),
                "overall_progress": min(state.successful_operations / 100, 1.0),
            }

        elif level == 2:
            # L2 → L3: Need 50 suggestions with >90% acceptance
            if state.total_suggestions < 50:
                return {
                    "next_level": "L3 AUTONOMOUS",
                    "suggestions_needed": 50 - state.total_suggestions,
                    "acceptance_rate": state.acceptance_rate,
                    "overall_progress": state.total_suggestions / 50,
                }
            else:
                return {
                    "next_level": "L3 AUTONOMOUS",
                    "suggestions_needed": 0,
                    "acceptance_rate": state.acceptance_rate,
                    "acceptance_needed": 0.9,
                    "overall_progress": min(state.acceptance_rate / 0.9, 1.0),
                }

        else:
            # L3 - maximum level
            return {
                "next_level": None,
                "overall_progress": 1.0,
                "message": "Maximum trust level achieved",
            }


# =============================================================================
# Factory Functions
# =============================================================================


def create_trust_persistence(
    state_file: Path | None = None,
) -> TrustPersistence:
    """Create a TrustPersistence instance."""
    return TrustPersistence(state_file=state_file)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TrustPersistence",
    "PersistedTrustState",
    "create_trust_persistence",
    "WITNESS_STATE_FILE",
    "KGENTS_DIR",
]
