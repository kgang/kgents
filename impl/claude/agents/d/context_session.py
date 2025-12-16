"""
ContextSession: Cross-request state management with polynomial transitions.

The ContextSession is the unified interface for context management.
It combines:
- ContextWindow (Store Comonad for turn history)
- PromptBuilder (prompt assembly)
- ComponentRenderer (React props)
- ContextProjector (Galois Connection compression)

State Machine (Polynomial):
    EMPTY → ACCUMULATING → PRESSURED → COMPRESSED

Inputs:
    user_turn, assistant_turn, system, compress, clear

The frontend never sees prompts—only component props via render().

AGENTESE: self.context.* (future namespace)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto
from typing import Any

from .component_renderer import (
    ComponentRenderer,
    ContextProps,
    ContextStatus,
    create_component_renderer,
)
from .context_window import (
    ContextWindow,
    Turn,
    TurnRole,
    create_context_window,
)
from .linearity import ResourceClass
from .projector import (
    CompressionResult,
    ContextProjector,
    create_projector,
)
from .prompt_builder import PromptBuilder, create_prompt_builder

# === State Machine ===


class ContextState(Enum):
    """Positions in the context polynomial."""

    EMPTY = auto()  # No turns yet
    ACCUMULATING = auto()  # Collecting turns, pressure < 0.7
    PRESSURED = auto()  # Pressure > 0.7, needs attention
    COMPRESSED = auto()  # Recently compressed, cooling down


# Valid inputs per state (polynomial directions)
VALID_DIRECTIONS: dict[ContextState, frozenset[str]] = {
    ContextState.EMPTY: frozenset(["user_turn", "system"]),
    ContextState.ACCUMULATING: frozenset(
        ["user_turn", "assistant_turn", "system", "compress", "clear"]
    ),
    ContextState.PRESSURED: frozenset(
        ["compress", "clear"]
    ),  # Must handle pressure first
    ContextState.COMPRESSED: frozenset(
        ["user_turn", "assistant_turn", "system", "clear"]
    ),
}


# === Input/Output Types ===


@dataclass(frozen=True)
class ContextInput:
    """Direction (valid input) for context polynomial."""

    kind: str  # "user_turn", "assistant_turn", "system", "compress", "clear"
    payload: Any = None

    @classmethod
    def user_turn(cls, content: str) -> "ContextInput":
        """Create user turn input."""
        return cls(kind="user_turn", payload=content)

    @classmethod
    def assistant_turn(cls, content: str) -> "ContextInput":
        """Create assistant turn input."""
        return cls(kind="assistant_turn", payload=content)

    @classmethod
    def system(cls, content: str) -> "ContextInput":
        """Create system message input."""
        return cls(kind="system", payload=content)

    @classmethod
    def compress(cls, target: float = 0.5) -> "ContextInput":
        """Create compress input."""
        return cls(kind="compress", payload=target)

    @classmethod
    def clear(cls) -> "ContextInput":
        """Create clear input."""
        return cls(kind="clear")


@dataclass(frozen=True)
class ContextOutput:
    """Output from context transition."""

    state: ContextState
    turn: Turn | None  # The turn that was added (if any)
    compressed: bool = False
    compression_result: CompressionResult | None = None
    error: str | None = None

    @property
    def success(self) -> bool:
        """True if operation succeeded."""
        return self.error is None


class ContextPressureError(Exception):
    """Raised when operation blocked by pressure."""

    pass


# === ContextSession ===


@dataclass
class ContextSession:
    """
    Cross-request state management with polynomial transitions.

    Provides unified interface for:
    - Adding turns (user, assistant, system)
    - Compression management
    - Prompt building (backend only)
    - Component rendering (frontend props)

    Example:
        session = ContextSession()

        # Add user message
        output = session.add_user_turn("Hello!")
        print(output.state)  # ContextState.ACCUMULATING

        # Build prompt for LLM (never exposed to frontend)
        prompt = session.build_prompt("kgent", eigenvectors)

        # Get frontend props
        props = session.render()
        props.to_dict()  # → JSON for React

        # Check if compression needed
        if session.needs_compression:
            output = await session.compress()

    Integration:
        # K-gent session
        class SoulSession:
            def __init__(self):
                self._context = ContextSession()

            async def dialogue(self, message: str) -> dict:
                self._context.add_user_turn(message)
                prompt = self._context.build_prompt("kgent", self._eigenvectors)
                response = await llm.complete(prompt)
                self._context.add_assistant_turn(response)
                return {"response": response, "context": self._context.render().to_dict()}
    """

    # Core components
    _window: ContextWindow = field(
        default_factory=lambda: ContextWindow(max_tokens=100_000)
    )
    _prompt_builder: PromptBuilder = field(default_factory=create_prompt_builder)
    _renderer: ComponentRenderer = field(default_factory=create_component_renderer)
    _projector: ContextProjector = field(default_factory=create_projector)

    # State machine
    _state: ContextState = field(default=ContextState.EMPTY)

    # Configuration
    max_tokens: int = 100_000

    def __post_init__(self) -> None:
        """Initialize with configured max_tokens."""
        self._window = ContextWindow(max_tokens=self.max_tokens)

    # === State Properties ===

    @property
    def state(self) -> ContextState:
        """Current polynomial state."""
        return self._state

    @property
    def pressure(self) -> float:
        """Current context pressure."""
        return self._window.pressure

    @property
    def needs_compression(self) -> bool:
        """True if context needs compression."""
        return self._window.needs_compression

    @property
    def window(self) -> ContextWindow:
        """Access underlying window (for advanced use)."""
        return self._window

    # === Turn Operations ===

    def add_user_turn(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> ContextOutput:
        """
        Add a user turn to the context.

        Args:
            content: User message content
            metadata: Optional metadata

        Returns:
            ContextOutput with new state and turn

        Raises:
            ContextPressureError: If in PRESSURED state
        """
        return self._apply_input(ContextInput.user_turn(content), metadata)

    def add_assistant_turn(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> ContextOutput:
        """
        Add an assistant turn to the context.

        Args:
            content: Assistant message content
            metadata: Optional metadata

        Returns:
            ContextOutput with new state and turn
        """
        return self._apply_input(ContextInput.assistant_turn(content), metadata)

    def add_system_message(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> ContextOutput:
        """
        Add a system message to the context.

        System messages are REQUIRED by default (can be summarized but not dropped).

        Args:
            content: System message content
            metadata: Optional metadata

        Returns:
            ContextOutput with new state and turn
        """
        return self._apply_input(ContextInput.system(content), metadata)

    async def compress(self, target_pressure: float = 0.5) -> ContextOutput:
        """
        Compress context to target pressure.

        Args:
            target_pressure: Target pressure (0.0 to 1.0)

        Returns:
            ContextOutput with compression result
        """
        result = await self._projector.compress(self._window, target_pressure)
        self._window = result.window
        self._state = ContextState.COMPRESSED

        return ContextOutput(
            state=self._state,
            turn=None,
            compressed=True,
            compression_result=result,
        )

    def clear(self) -> ContextOutput:
        """
        Clear all context.

        Returns:
            ContextOutput with EMPTY state
        """
        self._window = ContextWindow(max_tokens=self.max_tokens)
        self._state = ContextState.EMPTY

        return ContextOutput(
            state=self._state,
            turn=None,
        )

    # === Prompt Building (Backend Only) ===

    def build_prompt(
        self,
        agent_type: str,
        eigenvectors: dict[str, float] | None = None,
        constraints: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Build system prompt for LLM.

        NEVER expose this to the frontend.

        Args:
            agent_type: "kgent", "builder", "citizen", etc.
            eigenvectors: Personality coordinates
            constraints: User constraints
            **kwargs: Additional template variables

        Returns:
            Complete system prompt string
        """
        return self._prompt_builder.build_system_prompt(
            agent_type=agent_type,
            eigenvectors=eigenvectors,
            constraints=constraints,
            **kwargs,
        )

    def get_messages_for_llm(self) -> list[dict[str, str]]:
        """
        Get messages formatted for LLM API.

        Returns:
            List of {"role": str, "content": str} dicts
        """
        return [
            {"role": turn.role.value, "content": turn.content}
            for turn in self._window.all_turns()
        ]

    # === Component Rendering (Frontend Props) ===

    def render(self, status_override: ContextStatus | None = None) -> ContextProps:
        """
        Render context for frontend.

        This is the ONLY output the frontend should receive.

        Args:
            status_override: Override computed status (e.g., "thinking")

        Returns:
            ContextProps ready for React
        """
        return self._renderer.render_chat(self._window, status_override)

    # === State Machine ===

    def _apply_input(
        self,
        input: ContextInput,
        metadata: dict[str, Any] | None = None,
    ) -> ContextOutput:
        """
        Apply input to context state machine.

        Enforces polynomial transitions.
        """
        # Check if input is valid for current state
        valid_inputs = VALID_DIRECTIONS[self._state]
        if input.kind not in valid_inputs:
            if self._state == ContextState.PRESSURED:
                return ContextOutput(
                    state=self._state,
                    turn=None,
                    error="Context pressured. Call compress() or clear() first.",
                )
            return ContextOutput(
                state=self._state,
                turn=None,
                error=f"Invalid input '{input.kind}' for state {self._state.name}",
            )

        # Apply the input
        turn: Turn | None = None

        match input.kind:
            case "user_turn":
                turn = self._window.append(TurnRole.USER, input.payload, metadata)
            case "assistant_turn":
                turn = self._window.append(TurnRole.ASSISTANT, input.payload, metadata)
            case "system":
                turn = self._window.append(TurnRole.SYSTEM, input.payload, metadata)
                # Promote system messages to REQUIRED
                if turn:
                    self._window.promote_turn(
                        turn, ResourceClass.REQUIRED, "system message"
                    )
            case "clear":
                return self.clear()

        # Compute new state
        self._state = self._compute_next_state()

        return ContextOutput(
            state=self._state,
            turn=turn,
        )

    def _compute_next_state(self) -> ContextState:
        """Compute next state based on window state."""
        if len(self._window) == 0:
            return ContextState.EMPTY

        if self._window.needs_compression:
            return ContextState.PRESSURED

        # Check if recently compressed (within last 3 turns)
        if self._window._meta.compression_count > 0 and len(self._window) <= 3:
            return ContextState.COMPRESSED

        return ContextState.ACCUMULATING

    # === Serialization ===

    def to_dict(self) -> dict[str, Any]:
        """Serialize session for persistence."""
        return {
            "window": self._window.to_dict(),
            "state": self._state.name,
            "max_tokens": self.max_tokens,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContextSession":
        """Deserialize session from persistence."""
        session = cls(max_tokens=data.get("max_tokens", 100_000))
        session._window = ContextWindow.from_dict(data.get("window", {}))
        session._state = ContextState[data.get("state", "EMPTY")]
        return session


# === Factory Functions ===


def create_context_session(
    max_tokens: int = 100_000,
    initial_system: str | None = None,
) -> ContextSession:
    """
    Create a ContextSession with optional initial system message.

    Args:
        max_tokens: Maximum token budget
        initial_system: Optional system message to prepend

    Returns:
        Configured ContextSession
    """
    session = ContextSession(max_tokens=max_tokens)

    if initial_system:
        session.add_system_message(initial_system)
        # Promote to PRESERVED since it's the root context
        if session._window._turns:
            session._window.promote_turn(
                session._window._turns[0],
                ResourceClass.PRESERVED,
                "initial system prompt",
            )

    return session


def from_messages(
    messages: list[dict[str, str]],
    max_tokens: int = 100_000,
) -> ContextSession:
    """
    Create a ContextSession from a list of messages.

    Args:
        messages: List of {"role": str, "content": str}
        max_tokens: Maximum token budget

    Returns:
        Populated ContextSession
    """
    session = ContextSession(max_tokens=max_tokens)

    for msg in messages:
        role = msg.get("role", "user").lower()
        content = msg.get("content", "")

        match role:
            case "user":
                session.add_user_turn(content)
            case "assistant":
                session.add_assistant_turn(content)
            case "system":
                session.add_system_message(content)

    return session
