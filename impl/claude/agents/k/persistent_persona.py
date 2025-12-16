"""
Persistent K-gent: Persona with durable state storage.

Uses the NEW D-gent architecture:
- DgentRouter: Auto-selects best backend (SQLite by default)
- Datum: Schema-free bytes with causal linking for history
- causal_chain: Track persona evolution over time

Enables:
- Personality continuity across sessions
- Preference evolution tracking
- Confidence updates over time
- Pattern learning persistence
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

from agents.d import Datum, DgentRouter
from agents.d.router import Backend

from .persona import (
    DialogueInput,
    DialogueOutput,
    KgentAgent,
    PersonaQueryAgent,
    PersonaSeed,
    PersonaState,
)


class PersistentPersonaAgent(KgentAgent):
    """
    K-gent with persistent persona state.

    Uses the NEW D-gent architecture:
    - DgentRouter for backend selection (SQLite by default)
    - Datum for storage (state serialized as JSON bytes)
    - causal_chain for evolution history tracking

    Example:
        >>> persona = PersistentPersonaAgent(
        ...     namespace="kgent_persona"
        ... )
        >>> # First session
        >>> response = await persona.invoke(
        ...     DialogueInput(message="I prefer minimal design", mode=DialogueMode.REFLECT)
        ... )
        >>> # Later session - remembers preferences
        >>> persona2 = PersistentPersonaAgent(namespace="kgent_persona")
        >>> await persona2.load_state()
        >>> # State is restored, preferences remembered
    """

    def __init__(
        self,
        namespace: str = "kgent_persona",
        initial_state: Optional[PersonaState] = None,
        auto_save: bool = True,
        data_dir: Path | None = None,
        preferred_backend: Backend = Backend.SQLITE,
    ):
        """
        Initialize persistent persona agent.

        Args:
            namespace: Namespace for D-gent storage
            initial_state: Initial state (used if no file exists)
            auto_save: Whether to save state after each invoke
            data_dir: Directory for data files
            preferred_backend: Preferred storage backend
        """
        # Initialize with default or provided state
        state = initial_state or PersonaState(seed=PersonaSeed())
        super().__init__(state=state)

        # Create D-gent router
        self._dgent = DgentRouter(
            namespace=namespace,
            preferred=preferred_backend,
            data_dir=data_dir,
        )
        self.auto_save = auto_save
        self._current_datum_id: str | None = None

    async def load_state(self) -> None:
        """
        Load persona state from storage.

        Call this after initialization to restore persisted state.
        If no state exists or is corrupted, keeps the initial state.
        """
        try:
            # Get the most recent datum
            recent = await self._dgent.list(limit=1)
            if recent:
                self._current_datum_id = recent[0].id
                data = json.loads(recent[0].content.decode("utf-8"))
                self._state = PersonaState.from_dict(data)
                self._query_agent = PersonaQueryAgent(self._state)
        except Exception as e:
            # Corrupted state - log but keep initial state
            import logging

            logging.getLogger(__name__).warning(
                "Failed to load persona state, using defaults: %s", e
            )

    async def save_state(self) -> None:
        """Persist current persona state to storage."""
        content = json.dumps(self._state.to_dict(), default=str).encode("utf-8")

        datum = Datum.create(
            content=content,
            causal_parent=self._current_datum_id,
            metadata={"type": "persona_state"},
        )

        await self._dgent.put(datum)
        self._current_datum_id = datum.id

    async def invoke(self, input: DialogueInput) -> DialogueOutput:
        """
        Engage in dialogue and optionally persist state changes.

        Args:
            input: Dialogue input with message and mode

        Returns:
            Dialogue output with response
        """
        # Invoke parent dialogue logic
        output = await super().invoke(input)

        # Auto-save if enabled (captures preference evolution)
        if self.auto_save:
            await self.save_state()

        return output

    async def get_evolution_history(self, limit: int = 10) -> list[PersonaState]:
        """
        Get history of persona state changes via causal chain.

        Args:
            limit: Maximum number of historical states

        Returns:
            List of past persona states (oldest to newest)
        """
        if self._current_datum_id is None:
            return []

        chain = await self._dgent.causal_chain(self._current_datum_id)
        states = []

        for datum in chain:
            try:
                data = json.loads(datum.content.decode("utf-8"))
                states.append(PersonaState.from_dict(data))
            except (json.JSONDecodeError, KeyError):
                continue

        if limit is not None:
            states = states[-limit:]

        return states

    def update_preference(
        self,
        category: str,
        key: str,
        value: Any,
        confidence: float = 0.9,
        source: str = "explicit",
    ) -> None:
        """
        Update a persona preference with tracking.

        Args:
            category: Preference category (e.g., "communication")
            key: Preference key
            value: New preference value
            confidence: Confidence in this preference (0.0-1.0)
            source: How was this learned ("explicit", "inferred", "inherited")
        """
        # Update preference in seed
        if category not in self._state.seed.preferences:
            self._state.seed.preferences[category] = {}

        self._state.seed.preferences[category][key] = value

        # Track metadata
        pref_path = f"{category}.{key}"
        self._state.confidence[pref_path] = confidence
        self._state.sources[pref_path] = source


class PersistentPersonaQueryAgent(PersonaQueryAgent):
    """
    Persona query agent backed by persistent storage.

    Uses the NEW D-gent architecture for state persistence.
    """

    def __init__(
        self,
        namespace: str = "kgent_persona_query",
        initial_state: Optional[PersonaState] = None,
        data_dir: Path | None = None,
        preferred_backend: Backend = Backend.SQLITE,
    ):
        """
        Initialize persistent query agent.

        Args:
            namespace: Namespace for D-gent storage
            initial_state: Initial state if no file exists
            data_dir: Directory for data files
            preferred_backend: Preferred storage backend
        """
        state = initial_state or PersonaState(seed=PersonaSeed())
        super().__init__(state=state)

        self._dgent = DgentRouter(
            namespace=namespace,
            preferred=preferred_backend,
            data_dir=data_dir,
        )
        self._current_datum_id: str | None = None

    async def load_state(self) -> None:
        """Load persona state from storage.

        If no state exists or is corrupted, keeps the initial state.
        """
        try:
            recent = await self._dgent.list(limit=1)
            if recent:
                self._current_datum_id = recent[0].id
                data = json.loads(recent[0].content.decode("utf-8"))
                self._state = PersonaState.from_dict(data)
        except Exception as e:
            # Corrupted state file - log but keep initial state
            import logging

            logging.getLogger(__name__).warning(
                "Failed to load query agent state, using defaults: %s", e
            )

    async def save_state(self) -> None:
        """Persist current persona state."""
        content = json.dumps(self._state.to_dict(), default=str).encode("utf-8")

        datum = Datum.create(
            content=content,
            causal_parent=self._current_datum_id,
            metadata={"type": "persona_query_state"},
        )

        await self._dgent.put(datum)
        self._current_datum_id = datum.id


# Convenience functions


def persistent_kgent(
    namespace: str = "kgent_persona",
    initial_state: Optional[PersonaState] = None,
    data_dir: Path | None = None,
) -> PersistentPersonaAgent:
    """
    Create a persistent K-gent dialogue agent.

    Args:
        namespace: Namespace for D-gent storage
        initial_state: Initial state if file doesn't exist
        data_dir: Directory for data files

    Returns:
        Configured PersistentPersonaAgent
    """
    return PersistentPersonaAgent(
        namespace=namespace,
        initial_state=initial_state,
        data_dir=data_dir,
    )


def persistent_query_persona(
    namespace: str = "kgent_persona_query",
    initial_state: Optional[PersonaState] = None,
    data_dir: Path | None = None,
) -> PersistentPersonaQueryAgent:
    """
    Create a persistent persona query agent.

    Args:
        namespace: Namespace for D-gent storage
        initial_state: Initial state if file doesn't exist
        data_dir: Directory for data files

    Returns:
        Configured PersistentPersonaQueryAgent
    """
    return PersistentPersonaQueryAgent(
        namespace=namespace,
        initial_state=initial_state,
        data_dir=data_dir,
    )
