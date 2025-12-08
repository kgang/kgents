"""
Persistent K-gent: Persona with durable state storage.

Wraps PersonaState with PersistentAgent to enable:
- Personality continuity across sessions
- Preference evolution tracking
- Confidence updates over time
- Pattern learning persistence
"""

from pathlib import Path
from typing import Optional

from agents.d import PersistentAgent
from .persona import (
    PersonaState,
    PersonaSeed,
    DialogueInput,
    DialogueOutput,
    KgentAgent,
    PersonaQueryAgent,
)


class PersistentPersonaAgent(KgentAgent):
    """
    K-gent with persistent persona state.

    Automatically saves persona state after each dialogue,
    enabling continuity across sessions and preference evolution.

    Example:
        >>> persona = PersistentPersonaAgent(
        ...     path=Path("~/.kgents/persona.json")
        ... )
        >>> # First session
        >>> response = await persona.invoke(
        ...     DialogueInput(message="I prefer minimal design", mode=DialogueMode.REFLECT)
        ... )
        >>> # Later session - remembers preferences
        >>> persona2 = PersistentPersonaAgent(path=Path("~/.kgents/persona.json"))
        >>> await persona2.load_state()
        >>> # State is restored, preferences remembered
    """

    def __init__(
        self,
        path: Path | str,
        initial_state: Optional[PersonaState] = None,
        auto_save: bool = True,
    ):
        """
        Initialize persistent persona agent.

        Args:
            path: Path to JSON file for persona state
            initial_state: Initial state (used if no file exists)
            auto_save: Whether to save state after each invoke
        """
        # Initialize with default or provided state
        state = initial_state or PersonaState(seed=PersonaSeed())
        super().__init__(state=state)

        # Create persistent backend
        self._dgent = PersistentAgent[PersonaState](
            path=Path(path),
            schema=PersonaState,
            max_history=50,  # Track persona evolution
        )
        self.auto_save = auto_save

    async def load_state(self) -> None:
        """
        Load persona state from disk.

        Call this after initialization to restore persisted state.
        """
        try:
            self._state = await self._dgent.load()
            self._query_agent = PersonaQueryAgent(self._state)
        except Exception:
            # No state exists yet, use initial state
            pass

    async def save_state(self) -> None:
        """Persist current persona state to disk."""
        await self._dgent.save(self._state)

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
        Get history of persona state changes.

        Args:
            limit: Maximum number of historical states

        Returns:
            List of past persona states (newest first)
        """
        return await self._dgent.history(limit=limit)

    def update_preference(
        self,
        category: str,
        key: str,
        value: any,
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

    Wraps PersonaQueryAgent to provide query interface
    with automatic state persistence.
    """

    def __init__(
        self,
        path: Path | str,
        initial_state: Optional[PersonaState] = None,
    ):
        """
        Initialize persistent query agent.

        Args:
            path: Path to JSON file for persona state
            initial_state: Initial state if no file exists
        """
        state = initial_state or PersonaState(seed=PersonaSeed())
        super().__init__(state=state)

        self._dgent = PersistentAgent[PersonaState](
            path=Path(path),
            schema=PersonaState,
            max_history=50,
        )

    async def load_state(self) -> None:
        """Load persona state from disk."""
        try:
            self._state = await self._dgent.load()
        except Exception:
            pass

    async def save_state(self) -> None:
        """Persist current persona state."""
        await self._dgent.save(self._state)


# Convenience functions


def persistent_kgent(
    path: Path | str = "~/.kgents/persona.json",
    initial_state: Optional[PersonaState] = None,
) -> PersistentPersonaAgent:
    """
    Create a persistent K-gent dialogue agent.

    Args:
        path: Path to persona state file
        initial_state: Initial state if file doesn't exist

    Returns:
        Configured PersistentPersonaAgent
    """
    return PersistentPersonaAgent(path=path, initial_state=initial_state)


def persistent_query_persona(
    path: Path | str = "~/.kgents/persona.json",
    initial_state: Optional[PersonaState] = None,
) -> PersistentPersonaQueryAgent:
    """
    Create a persistent persona query agent.

    Args:
        path: Path to persona state file
        initial_state: Initial state if file doesn't exist

    Returns:
        Configured PersistentPersonaQueryAgent
    """
    return PersistentPersonaQueryAgent(path=path, initial_state=initial_state)
