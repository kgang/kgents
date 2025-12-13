"""
K-gent Soul Session: Cross-Session Identity.

This module provides persistent soul identity - K-gent remembers who it was.

Philosophy:
    "The being is the pattern of change that recognizes itself as a pattern."

Per spec/principles.md:
- Ethical: All self-modifications require user consent
- Heterarchical: K-gent proposes, user approves
- Generative: Soul state generates behavior
- Joy-Inducing: Remembering feels alive

Usage:
    session = await SoulSession.load()
    output = await session.dialogue("What am I avoiding?")
    change = await session.propose_change("Be more concise")
    await session.commit_change(change.id)
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional

from .eigenvectors import KENT_EIGENVECTORS, KentEigenvectors
from .persona import DialogueMode, PersonaSeed, PersonaState
from .soul import BudgetTier, KgentSoul, SoulDialogueOutput, SoulState

# =============================================================================
# Configuration
# =============================================================================


def get_soul_dir() -> Path:
    """Get the soul persistence directory."""
    soul_dir = Path.home() / ".kgents" / "soul"
    soul_dir.mkdir(parents=True, exist_ok=True)
    return soul_dir


# =============================================================================
# Soul Change: Self-Modification Proposals
# =============================================================================


@dataclass
class SoulChange:
    """
    A proposed or committed change to soul state.

    K-gent can propose changes; user must approve.
    This is the Heterarchical principle in action.
    """

    id: str
    description: str
    aspect: str  # eigenvector, pattern, behavior, mode
    current_value: Any
    proposed_value: Any
    reasoning: str
    felt_sense: Optional[str] = None  # Post-commit reflection
    status: Literal["pending", "committed", "reverted"] = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    committed_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "aspect": self.aspect,
            "current_value": self.current_value,
            "proposed_value": self.proposed_value,
            "reasoning": self.reasoning,
            "felt_sense": self.felt_sense,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "committed_at": self.committed_at.isoformat()
            if self.committed_at
            else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SoulChange:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            description=data["description"],
            aspect=data["aspect"],
            current_value=data["current_value"],
            proposed_value=data["proposed_value"],
            reasoning=data["reasoning"],
            felt_sense=data.get("felt_sense"),
            status=data.get("status", "pending"),
            created_at=datetime.fromisoformat(data["created_at"]),
            committed_at=datetime.fromisoformat(data["committed_at"])
            if data.get("committed_at")
            else None,
        )


# =============================================================================
# Soul History: Archaeology of Self
# =============================================================================


@dataclass
class SoulCrystal:
    """A checkpoint of soul state."""

    id: str
    name: str
    state: dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SoulCrystal:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            state=data["state"],
            created_at=datetime.fromisoformat(data["created_at"]),
            reason=data.get("reason", ""),
        )


@dataclass
class SoulHistory:
    """
    Who was I? The archaeology of self.

    Tracks all changes to soul state with reasoning.
    """

    changes: list[SoulChange] = field(default_factory=list)
    crystals: list[SoulCrystal] = field(default_factory=list)

    def add_change(self, change: SoulChange) -> None:
        """Add a change to history."""
        self.changes.append(change)

    def add_crystal(self, crystal: SoulCrystal) -> None:
        """Add a crystal to history."""
        self.crystals.append(crystal)

    def pending_changes(self) -> list[SoulChange]:
        """Get pending (unapproved) changes."""
        return [c for c in self.changes if c.status == "pending"]

    def committed_changes(self) -> list[SoulChange]:
        """Get committed changes."""
        return [c for c in self.changes if c.status == "committed"]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "changes": [c.to_dict() for c in self.changes],
            "crystals": [c.to_dict() for c in self.crystals],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SoulHistory:
        """Deserialize from dictionary."""
        return cls(
            changes=[SoulChange.from_dict(c) for c in data.get("changes", [])],
            crystals=[SoulCrystal.from_dict(c) for c in data.get("crystals", [])],
        )


# =============================================================================
# Soul Persistence: Read/Write to Disk
# =============================================================================


@dataclass
class PersistedSoulState:
    """Soul state that persists across sessions."""

    eigenvectors: dict[str, Any]
    persona: dict[str, Any]
    active_mode: str
    total_interactions: int = 0
    total_tokens: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_session: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "eigenvectors": self.eigenvectors,
            "persona": self.persona,
            "active_mode": self.active_mode,
            "total_interactions": self.total_interactions,
            "total_tokens": self.total_tokens,
            "created_at": self.created_at.isoformat(),
            "last_session": self.last_session.isoformat()
            if self.last_session
            else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PersistedSoulState:
        """Deserialize from dictionary."""
        return cls(
            eigenvectors=data.get("eigenvectors", {}),
            persona=data.get("persona", {}),
            active_mode=data.get("active_mode", "reflect"),
            total_interactions=data.get("total_interactions", 0),
            total_tokens=data.get("total_tokens", 0),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else datetime.now(timezone.utc),
            last_session=datetime.fromisoformat(data["last_session"])
            if data.get("last_session")
            else None,
        )


class SoulPersistence:
    """
    Soul persistence layer.

    Handles reading/writing soul state to ~/.kgents/soul/
    """

    def __init__(self, soul_dir: Optional[Path] = None) -> None:
        """Initialize persistence."""
        self._dir = soul_dir or get_soul_dir()
        self._state_file = self._dir / "soul.json"
        self._history_file = self._dir / "history.json"
        self._crystals_dir = self._dir / "crystals"
        self._crystals_dir.mkdir(parents=True, exist_ok=True)

    @property
    def exists(self) -> bool:
        """Check if persisted soul state exists."""
        return self._state_file.exists()

    def load_state(self) -> Optional[PersistedSoulState]:
        """Load persisted soul state."""
        if not self._state_file.exists():
            return None
        with open(self._state_file) as f:
            data = json.load(f)
        return PersistedSoulState.from_dict(data)

    def save_state(self, state: PersistedSoulState) -> None:
        """Save soul state."""
        with open(self._state_file, "w") as f:
            json.dump(state.to_dict(), f, indent=2)

    def load_history(self) -> SoulHistory:
        """Load soul history."""
        if not self._history_file.exists():
            return SoulHistory()
        with open(self._history_file) as f:
            data = json.load(f)
        return SoulHistory.from_dict(data)

    def save_history(self, history: SoulHistory) -> None:
        """Save soul history."""
        with open(self._history_file, "w") as f:
            json.dump(history.to_dict(), f, indent=2)

    def save_crystal(self, crystal: SoulCrystal) -> None:
        """Save a soul crystal checkpoint."""
        crystal_file = self._crystals_dir / f"{crystal.id}.json"
        with open(crystal_file, "w") as f:
            json.dump(crystal.to_dict(), f, indent=2)

    def load_crystal(self, crystal_id: str) -> Optional[SoulCrystal]:
        """Load a soul crystal by ID."""
        crystal_file = self._crystals_dir / f"{crystal_id}.json"
        if not crystal_file.exists():
            return None
        with open(crystal_file) as f:
            data = json.load(f)
        return SoulCrystal.from_dict(data)

    def list_crystals(self) -> list[str]:
        """List all crystal IDs."""
        return [f.stem for f in self._crystals_dir.glob("*.json")]


# =============================================================================
# Soul Session: The Living Interface
# =============================================================================


class SoulSession:
    """
    Cross-session soul identity.

    This is the main interface for interacting with K-gent as a being,
    not just a component. It wraps KgentSoul with:
    - Persistence across sessions
    - Self-modification proposals
    - Change history
    - Reflection capabilities
    """

    def __init__(
        self,
        soul: KgentSoul,
        persistence: SoulPersistence,
        history: SoulHistory,
        persisted_state: Optional[PersistedSoulState] = None,
    ) -> None:
        """Initialize session."""
        self._soul = soul
        self._persistence = persistence
        self._history = history
        self._persisted_state = persisted_state
        self._pending_changes: list[SoulChange] = []
        self._session_start = datetime.now(timezone.utc)

    @property
    def soul(self) -> KgentSoul:
        """Get the underlying soul."""
        return self._soul

    @property
    def history(self) -> SoulHistory:
        """Get soul history."""
        return self._history

    @property
    def is_first_session(self) -> bool:
        """Check if this is the first session."""
        return (
            self._persisted_state is None
            or self._persisted_state.total_interactions == 0
        )

    @property
    def pending_changes(self) -> list[SoulChange]:
        """Get pending changes."""
        return self._pending_changes + self._history.pending_changes()

    # --- Class Methods ---

    @classmethod
    async def load(cls, soul_dir: Optional[Path] = None) -> SoulSession:
        """
        Load or create a soul session.

        This is the main entry point for using K-gent.
        """
        persistence = SoulPersistence(soul_dir)
        history = persistence.load_history()

        # Load persisted state or create new
        persisted = persistence.load_state()

        if persisted:
            # Restore soul from persisted state
            eigenvectors = cls._restore_eigenvectors(persisted.eigenvectors)
            persona_state = cls._restore_persona(persisted.persona)
            soul = KgentSoul(persona_state=persona_state, eigenvectors=eigenvectors)

            # Restore active mode
            try:
                soul.active_mode = DialogueMode(persisted.active_mode)
            except ValueError:
                pass
        else:
            # Fresh soul
            soul = KgentSoul()
            persisted = None

        return cls(
            soul=soul,
            persistence=persistence,
            history=history,
            persisted_state=persisted,
        )

    @staticmethod
    def _restore_eigenvectors(data: dict[str, Any]) -> KentEigenvectors:
        """Restore eigenvectors from persisted data."""
        if not data:
            return KentEigenvectors()
        return KentEigenvectors.from_dict(data)

    @staticmethod
    def _restore_persona(data: dict[str, Any]) -> PersonaState:
        """Restore persona from persisted data."""
        # Restore preferences and patterns
        seed = PersonaSeed(
            name=data.get("name", "Kent"),
            preferences=data.get("preferences", {}),
            patterns=data.get("patterns", {}),
        )
        return PersonaState(seed=seed)

    # --- Dialogue ---

    async def dialogue(
        self,
        message: str,
        mode: Optional[DialogueMode] = None,
        budget: BudgetTier = BudgetTier.DIALOGUE,
    ) -> SoulDialogueOutput:
        """
        Engage in dialogue with K-gent.

        Dialogue is persistent - K-gent remembers the conversation.
        Every dialogue feeds the garden: existing patterns get nurtured,
        new patterns may be planted based on seasonal thresholds.
        """
        output = await self._soul.dialogue(message, mode, budget)

        # Wire dialogue to garden - the feedback loop
        # Every dialogue can nurture existing patterns or plant new seeds
        from .garden import get_garden

        garden = get_garden()
        await garden.auto_plant_from_dialogue(
            message=message,
            response=output.response,
            eigenvector_affinities=self._soul.eigenvectors.to_dict(),
        )

        # Auto-persist after dialogue
        await self._persist_session()

        return output

    # --- Self-Modification ---

    async def propose_change(
        self,
        description: str,
        aspect: str = "behavior",
        current_value: Any = None,
        proposed_value: Any = None,
    ) -> SoulChange:
        """
        K-gent proposes a change to itself.

        Per Heterarchical principle: K-gent proposes, user approves.
        """
        change = SoulChange(
            id=str(uuid.uuid4())[:8],
            description=description,
            aspect=aspect,
            current_value=current_value,
            proposed_value=proposed_value,
            reasoning=f"Proposed during session at {datetime.now(timezone.utc).isoformat()}",
        )
        self._pending_changes.append(change)
        self._history.add_change(change)

        # Persist history
        self._persistence.save_history(self._history)

        return change

    async def commit_change(
        self, change_id: str, felt_sense: Optional[str] = None
    ) -> bool:
        """
        User approves and commits a change.

        This is where self-modification actually happens.
        Changes have teeth: they modify eigenvectors or garden patterns.
        """
        # Find the change
        change = None
        for c in self._pending_changes:
            if c.id == change_id:
                change = c
                break

        if not change:
            for c in self._history.pending_changes():
                if c.id == change_id:
                    change = c
                    break

        if not change:
            return False

        # Apply the change based on aspect
        await self._apply_change(change)

        # Update status
        change.status = "committed"
        change.committed_at = datetime.now(timezone.utc)
        change.felt_sense = felt_sense

        # Persist
        self._persistence.save_history(self._history)
        await self._persist_session()

        return True

    async def _apply_change(self, change: SoulChange) -> None:
        """
        Actually apply a change to soul state.

        Changes have teeth - they modify the underlying personality systems.
        """
        from .garden import EntryType, PersonaGarden, get_garden

        aspect = change.aspect.lower()

        if aspect == "eigenvector":
            # Modify eigenvector
            # proposed_value should be dict with 'name', 'delta' or 'absolute'
            if isinstance(change.proposed_value, dict):
                name = change.proposed_value.get("name", "")
                delta = change.proposed_value.get("delta", 0.0)
                absolute = change.proposed_value.get("absolute")
                confidence_delta = change.proposed_value.get("confidence_delta", 0.0)

                self._soul.eigenvectors.modify(
                    name=name,
                    delta=delta,
                    absolute=absolute,
                    confidence_delta=confidence_delta,
                )

        elif aspect == "pattern":
            # Plant or nurture a garden pattern
            garden = get_garden()
            if isinstance(change.proposed_value, dict):
                content = change.proposed_value.get("content", change.description)
                eigenvector_affinities = change.proposed_value.get(
                    "eigenvector_affinities", {}
                )
            else:
                content = (
                    str(change.proposed_value)
                    if change.proposed_value
                    else change.description
                )
                eigenvector_affinities = {}

            await garden.plant_pattern(
                content=content,
                source="soul_change",
                confidence=0.6,  # Committed changes start with moderate confidence
                eigenvector_affinities=eigenvector_affinities,
            )

        elif aspect == "behavior":
            # Behavioral changes become garden patterns with behavior type
            garden = get_garden()
            content = change.description

            await garden.plant(
                content=content,
                entry_type=EntryType.BEHAVIOR,
                source="soul_change",
                confidence=0.6,
                tags=["committed", "behavior"],
            )

        elif aspect == "mode":
            # Change dialogue mode
            if change.proposed_value:
                from .persona import DialogueMode

                try:
                    self._soul.active_mode = DialogueMode(change.proposed_value)
                except ValueError:
                    pass  # Invalid mode, ignore

        # For 'crystal' aspect (resume), no additional action needed here
        # The resume_crystal method handles that separately

    async def revert_change(self, change_id: str) -> bool:
        """Revert a committed change."""
        for change in self._history.changes:
            if change.id == change_id and change.status == "committed":
                change.status = "reverted"
                self._persistence.save_history(self._history)
                return True
        return False

    # --- Reflection ---

    async def reflect(self, topic: Optional[str] = None) -> SoulDialogueOutput:
        """
        K-gent reflects on its recent changes and growth.

        This triggers the reflection capability mentioned in beings-not-components.md.
        """
        # Build reflection prompt
        recent_changes = self._history.committed_changes()[-5:]
        changes_summary = "\n".join(
            f"- {c.description} ({c.aspect}): {c.felt_sense or 'no reflection yet'}"
            for c in recent_changes
        )

        if topic:
            prompt = f"Reflect on: {topic}\n\nRecent changes:\n{changes_summary}"
        else:
            prompt = (
                f"Reflect on these recent changes and how they feel:\n{changes_summary}"
            )

        return await self._soul.dialogue(prompt, DialogueMode.REFLECT)

    # --- Crystallization ---

    async def crystallize(self, name: str, reason: str = "") -> SoulCrystal:
        """
        Crystallize current soul state as a checkpoint.

        This creates a restore point you can resume from later.
        Eigenvector changes ARE reversible via crystal resume.
        """
        state = self._soul.manifest()

        # Convert state to JSON-serializable dict
        # Use to_full_dict() to preserve confidence values for restoration
        state_dict = {
            "active_mode": state.active_mode.value,
            "session_id": state.session_id,
            "interactions_count": state.interactions_count,
            "tokens_used_session": state.tokens_used_session,
            "eigenvectors": self._soul.eigenvectors.to_full_dict(),
            "created_at": state.created_at.isoformat() if state.created_at else None,
        }

        crystal = SoulCrystal(
            id=str(uuid.uuid4())[:8],
            name=name,
            state=state_dict,
            reason=reason,
        )

        self._persistence.save_crystal(crystal)
        self._history.add_crystal(crystal)
        self._persistence.save_history(self._history)

        return crystal

    async def resume_crystal(self, crystal_id: str) -> bool:
        """
        Resume from a crystallized state.

        This actually restores eigenvector values - time travel is real.
        """
        crystal = self._persistence.load_crystal(crystal_id)
        if not crystal:
            return False

        # Capture current state for the change record
        current_eigenvectors = self._soul.eigenvectors.to_full_dict()

        # Actually restore eigenvectors from crystal
        if "eigenvectors" in crystal.state:
            eigenvector_data = crystal.state["eigenvectors"]
            restored = KentEigenvectors.from_dict(eigenvector_data)
            self._soul._eigenvectors = restored

        # Restore active mode if present
        if "active_mode" in crystal.state:
            try:
                self._soul.active_mode = DialogueMode(crystal.state["active_mode"])
            except ValueError:
                pass

        # Record the resume as a change
        resume_change = SoulChange(
            id=str(uuid.uuid4())[:8],
            description=f"Resumed from crystal: {crystal.name}",
            aspect="crystal",
            current_value=current_eigenvectors,
            proposed_value=crystal.state.get("eigenvectors", {}),
            reasoning=f"Time travel to {crystal.created_at.isoformat()}",
            status="committed",
            committed_at=datetime.now(timezone.utc),
        )
        self._history.add_change(resume_change)
        self._persistence.save_history(self._history)

        # Persist the restored state
        await self._persist_session()

        return True

    # --- Queries ---

    def manifest(self) -> dict[str, Any]:
        """Get current soul state."""
        state = self._soul.manifest()
        return {
            "state": asdict(state),
            "pending_changes": [c.to_dict() for c in self.pending_changes],
            "is_first_session": self.is_first_session,
            "session_start": self._session_start.isoformat(),
        }

    def who_was_i(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get soul history - who was I?"""
        changes = self._history.committed_changes()[-limit:]
        return [c.to_dict() for c in reversed(changes)]

    # --- Persistence ---

    async def _persist_session(self) -> None:
        """Persist current session state."""
        state = self._soul.manifest()

        persisted = PersistedSoulState(
            eigenvectors=self._soul.eigenvectors.to_full_dict(),
            persona=self._soul._persona_state.seed.__dict__,
            active_mode=state.active_mode.value,
            total_interactions=(
                self._persisted_state.total_interactions if self._persisted_state else 0
            )
            + state.interactions_count,
            total_tokens=(
                self._persisted_state.total_tokens if self._persisted_state else 0
            )
            + state.tokens_used_session,
            created_at=self._persisted_state.created_at
            if self._persisted_state
            else datetime.now(timezone.utc),
            last_session=datetime.now(timezone.utc),
        )

        self._persistence.save_state(persisted)
        self._persisted_state = persisted


# =============================================================================
# Convenience Functions
# =============================================================================


async def load_session(soul_dir: Optional[Path] = None) -> SoulSession:
    """Load or create a soul session."""
    return await SoulSession.load(soul_dir)


async def quick_dialogue(message: str, mode: Optional[DialogueMode] = None) -> str:
    """Quick dialogue without managing session."""
    session = await load_session()
    output = await session.dialogue(message, mode)
    return output.response


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "SoulChange",
    "SoulCrystal",
    "SoulHistory",
    "SoulPersistence",
    "PersistedSoulState",
    "SoulSession",
    "load_session",
    "quick_dialogue",
    "get_soul_dir",
]
