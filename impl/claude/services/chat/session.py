"""
ChatSession: Stateful conversation wrapper over F-gent ChatFlow.

A ChatSession is a coalgebra: State -> (Response x State)

The session manages:
- Turn protocol (atomic turns)
- State transitions
- Budget tracking
- Entropy management
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncIterator

from .config import ChatConfig, ContextStrategy

if TYPE_CHECKING:
    from agents.f.modalities.chat import ChatFlow, Turn as FgentTurn
    from bootstrap.umwelt import Umwelt
    from .composer import ChatMorpheusComposer, TurnResult as ComposerTurnResult


class ChatSessionState(Enum):
    """
    Chat session states.

    State machine:
        DORMANT -> READY (create_session)
        READY -> STREAMING (send_message)
        STREAMING -> WAITING (response_complete)
        STREAMING -> DRAINING (finalizing)
        WAITING -> STREAMING (send_message)
        STREAMING -> COLLAPSED (entropy depleted)
        WAITING -> COLLAPSED (entropy depleted)
        DRAINING -> COLLAPSED (finalized)
    """

    DORMANT = "dormant"  # No active conversation
    READY = "ready"  # Session created, awaiting first message
    STREAMING = "streaming"  # Response in progress
    WAITING = "waiting"  # Awaiting user input
    DRAINING = "draining"  # Finalizing, no new input
    COLLAPSED = "collapsed"  # Session ended


@dataclass
class Message:
    """A single message in the conversation."""

    role: str  # "system", "user", "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tokens: int = 0  # Computed if not provided
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.tokens == 0:
            # Rough estimate: 1 token ~= 4 characters
            self.tokens = len(self.content) // 4


@dataclass
class Turn:
    """
    A complete conversation turn.

    A turn is atomic - it either completes fully or rolls back.
    """

    turn_number: int
    user_message: Message
    assistant_response: Message
    started_at: datetime
    completed_at: datetime
    tokens_in: int
    tokens_out: int
    context_before: int  # Context size before this turn
    context_after: int  # Context size after (may differ due to compression)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Turn duration in seconds."""
        return (self.completed_at - self.started_at).total_seconds()

    @property
    def total_tokens(self) -> int:
        """Total tokens for this turn."""
        return self.tokens_in + self.tokens_out

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "turn_number": self.turn_number,
            "user_message": self.user_message.content,
            "assistant_response": self.assistant_response.content,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "duration": self.duration,
        }


@dataclass
class SessionBudget:
    """Track conversation costs and token usage."""

    tokens_in_total: int = 0
    tokens_out_total: int = 0
    estimated_cost_usd: float = 0.0
    turn_count: int = 0

    # Model pricing (per 1M tokens)
    _model_costs: dict[str, tuple[float, float]] = field(
        default_factory=lambda: {
            "claude-3-haiku": (0.25, 1.25),
            "claude-3-sonnet": (3.0, 15.0),
            "claude-3-opus": (15.0, 75.0),
            "gpt-4o-mini": (0.15, 0.60),
            "gpt-4o": (2.50, 10.0),
            "default": (1.0, 5.0),
        }
    )

    def record_turn(self, turn: Turn, model: str = "default") -> None:
        """Record a turn's token usage."""
        self.tokens_in_total += turn.tokens_in
        self.tokens_out_total += turn.tokens_out
        self.turn_count += 1

        # Estimate cost
        costs = self._model_costs.get(model, self._model_costs["default"])
        input_cost = (turn.tokens_in / 1_000_000) * costs[0]
        output_cost = (turn.tokens_out / 1_000_000) * costs[1]
        self.estimated_cost_usd += input_cost + output_cost

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.tokens_in_total + self.tokens_out_total

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tokens_in": self.tokens_in_total,
            "tokens_out": self.tokens_out_total,
            "total_tokens": self.total_tokens,
            "turn_count": self.turn_count,
            "estimated_cost_usd": round(self.estimated_cost_usd, 6),
        }


class ChatSession:
    """
    ChatSession: Stateful conversation wrapper over F-gent ChatFlow.

    A chat session is a coalgebra:
        step : State -> (Response x State)

    The session state S is a product of:
        - Context: The rendered conversation window
        - Turns: The complete history (ground truth)
        - Entropy: Remaining conversation budget
    """

    def __init__(
        self,
        session_id: str,
        node_path: str,
        observer: "Umwelt[Any, Any]",
        config: ChatConfig | None = None,
        flow: "ChatFlow | None" = None,
    ):
        """
        Initialize a chat session.

        Args:
            session_id: Unique session identifier
            node_path: AGENTESE path of the node (e.g., "self.soul")
            observer: The observer's umwelt
            config: Chat configuration
            flow: Optional pre-configured ChatFlow
        """
        self.session_id = session_id
        self.node_path = node_path
        self.observer = observer
        self.config = config or ChatConfig()

        # State
        self._state = ChatSessionState.DORMANT
        self._flow = flow
        self._created_at = datetime.now()
        self._updated_at = datetime.now()

        # Ground truth: complete turn history
        self._turns: list[Turn] = []

        # Working state
        self._current_turn: int = 0
        self._partial_response: str = ""
        self._streaming: bool = False

        # Entropy budget
        self._entropy = self.config.entropy_budget

        # Budget tracking
        self._budget = SessionBudget()

        # Session name (for persistence)
        self._name: str | None = None
        self._tags: list[str] = []

        # Morpheus composition hook (injected by ChatServiceFactory)
        self._composer: "ChatMorpheusComposer | None" = None

    # === Properties ===

    @property
    def state(self) -> ChatSessionState:
        """Current session state."""
        return self._state

    @property
    def turn_count(self) -> int:
        """Number of completed turns."""
        return len(self._turns)

    @property
    def entropy(self) -> float:
        """Remaining entropy budget (0.0 to 1.0)."""
        return self._entropy

    @property
    def is_active(self) -> bool:
        """Whether the session is actively conversing."""
        return self._state in (
            ChatSessionState.READY,
            ChatSessionState.STREAMING,
            ChatSessionState.WAITING,
        )

    @property
    def is_collapsed(self) -> bool:
        """Whether the session has ended."""
        return self._state == ChatSessionState.COLLAPSED

    @property
    def budget(self) -> SessionBudget:
        """Token budget tracking."""
        return self._budget

    @property
    def has_composer(self) -> bool:
        """Whether a Morpheus composer is attached."""
        return self._composer is not None

    # === Composer Injection ===

    def set_composer(self, composer: "ChatMorpheusComposer") -> None:
        """
        Inject external turn composer for LLM integration.

        Called by ChatServiceFactory to wire Morpheus.

        Args:
            composer: The ChatMorpheusComposer to use for turns
        """
        self._composer = composer

    # === State Transitions ===

    def _transition(self, to_state: ChatSessionState) -> None:
        """
        Perform a state transition.

        Validates the transition is legal.
        """
        legal_transitions: dict[ChatSessionState, set[ChatSessionState]] = {
            ChatSessionState.DORMANT: {ChatSessionState.READY},
            ChatSessionState.READY: {ChatSessionState.STREAMING, ChatSessionState.COLLAPSED},
            ChatSessionState.STREAMING: {
                ChatSessionState.WAITING,
                ChatSessionState.DRAINING,
                ChatSessionState.COLLAPSED,
            },
            ChatSessionState.WAITING: {ChatSessionState.STREAMING, ChatSessionState.COLLAPSED},
            ChatSessionState.DRAINING: {ChatSessionState.COLLAPSED},
            ChatSessionState.COLLAPSED: set(),  # Terminal state
        }

        if to_state not in legal_transitions.get(self._state, set()):
            raise ValueError(
                f"Invalid state transition: {self._state.value} -> {to_state.value}"
            )

        self._state = to_state
        self._updated_at = datetime.now()

    def activate(self) -> None:
        """Activate the session (DORMANT -> READY)."""
        self._transition(ChatSessionState.READY)

    def collapse(self, reason: str = "entropy_depleted") -> None:
        """
        Collapse the session (terminal state).

        Args:
            reason: Why the session collapsed
        """
        if self._state != ChatSessionState.COLLAPSED:
            # Allow transition from any non-collapsed state
            self._state = ChatSessionState.COLLAPSED
            self._updated_at = datetime.now()

    # === Core Operations ===

    async def send(self, message: str) -> str:
        """
        Send a message and get the complete response.

        This is a blocking operation that waits for the full response.

        Args:
            message: User's message

        Returns:
            Complete assistant response

        Raises:
            RuntimeError: If session is collapsed or max turns exceeded
        """
        # Validate state
        if self._state == ChatSessionState.COLLAPSED:
            raise RuntimeError("Session is collapsed")

        if self._state == ChatSessionState.DORMANT:
            self.activate()

        # Check max turns
        if self.config.max_turns and self.turn_count >= self.config.max_turns:
            self.collapse("max_turns_exceeded")
            raise RuntimeError(f"Max turns ({self.config.max_turns}) exceeded")

        # Check entropy
        if self._entropy <= 0:
            self.collapse("entropy_depleted")
            raise RuntimeError("Entropy depleted")

        # Start turn
        self._transition(ChatSessionState.STREAMING)
        started_at = datetime.now()
        self._current_turn += 1

        # Create user message
        user_msg = Message(role="user", content=message)
        context_before = self._get_context_size()

        try:
            # Generate response via composer or fallback
            tokens_in = user_msg.tokens
            tokens_out = 0
            model_used = self.config.model or "default"

            if self._composer is not None:
                # Use Morpheus composition (real LLM)
                result = await self._composer.compose_turn(self, message, self.observer)
                response_text = result.content
                tokens_in = result.tokens_in or user_msg.tokens
                tokens_out = result.tokens_out
                model_used = result.model or model_used
            elif self._flow is not None:
                response_text = await self._flow.send_message(message)
            else:
                # Fallback: generate stub response
                response_text = await self._generate_stub_response(message)

            # Create response message
            response_msg = Message(role="assistant", content=response_text, tokens=tokens_out or 0)
            completed_at = datetime.now()
            context_after = self._get_context_size()

            # Record turn
            turn = Turn(
                turn_number=self._current_turn,
                user_message=user_msg,
                assistant_response=response_msg,
                started_at=started_at,
                completed_at=completed_at,
                tokens_in=tokens_in,
                tokens_out=tokens_out or response_msg.tokens,
                context_before=context_before,
                context_after=context_after,
            )
            self._turns.append(turn)
            self._budget.record_turn(turn, model_used)

            # Decay entropy
            self._entropy = max(0, self._entropy - self.config.entropy_decay_per_turn)

            # Transition to waiting
            self._transition(ChatSessionState.WAITING)

            # Check if entropy depleted after turn
            if self._entropy <= 0:
                self.collapse("entropy_depleted")

            return response_text

        except Exception as e:
            # Rollback on failure
            self._current_turn -= 1
            self._transition(ChatSessionState.WAITING)
            raise RuntimeError(f"Turn failed: {e}") from e

    async def stream(self, message: str) -> AsyncIterator[str]:
        """
        Stream response tokens as they're generated.

        Args:
            message: User's message

        Yields:
            Individual tokens or chunks

        Raises:
            RuntimeError: If session is collapsed or max turns exceeded
        """
        # Validate state
        if self._state == ChatSessionState.COLLAPSED:
            raise RuntimeError("Session is collapsed")

        if self._state == ChatSessionState.DORMANT:
            self.activate()

        # Check max turns
        if self.config.max_turns and self.turn_count >= self.config.max_turns:
            self.collapse("max_turns_exceeded")
            raise RuntimeError(f"Max turns ({self.config.max_turns}) exceeded")

        # Check entropy
        if self._entropy <= 0:
            self.collapse("entropy_depleted")
            raise RuntimeError("Entropy depleted")

        # Start turn
        self._transition(ChatSessionState.STREAMING)
        started_at = datetime.now()
        self._current_turn += 1
        self._streaming = True

        # Create user message
        user_msg = Message(role="user", content=message)
        context_before = self._get_context_size()

        self._partial_response = ""
        model_used = self.config.model or "default"

        try:
            if self._composer is not None:
                # Stream from Morpheus composition (real LLM)
                async for token in self._composer.compose_stream(self, message, self.observer):
                    self._partial_response += token
                    yield token
                # Note: For streaming, we estimate tokens from content length
                # Real token counts would require post-hoc API call
            elif self._flow is not None:
                # Stream from flow
                async for token in self._flow.stream_response(message):
                    self._partial_response += token
                    yield token
            else:
                # Fallback: generate stub response as stream
                response = await self._generate_stub_response(message)
                for word in response.split():
                    token = word + " "
                    self._partial_response += token
                    yield token
                    await asyncio.sleep(0.01)

            # Create response message
            response_msg = Message(role="assistant", content=self._partial_response)
            completed_at = datetime.now()
            context_after = self._get_context_size()

            # Record turn
            turn = Turn(
                turn_number=self._current_turn,
                user_message=user_msg,
                assistant_response=response_msg,
                started_at=started_at,
                completed_at=completed_at,
                tokens_in=user_msg.tokens,
                tokens_out=response_msg.tokens,
                context_before=context_before,
                context_after=context_after,
            )
            self._turns.append(turn)
            self._budget.record_turn(turn, model_used)

            # Decay entropy
            self._entropy = max(0, self._entropy - self.config.entropy_decay_per_turn)

            # Transition to waiting
            self._streaming = False
            self._transition(ChatSessionState.WAITING)

            # Check if entropy depleted after turn
            if self._entropy <= 0:
                self.collapse("entropy_depleted")

        except Exception as e:
            # Rollback on failure
            self._current_turn -= 1
            self._streaming = False
            self._transition(ChatSessionState.WAITING)
            raise RuntimeError(f"Streaming failed: {e}") from e
        finally:
            self._partial_response = ""

    async def _generate_stub_response(self, message: str) -> str:
        """Generate a stub response when no flow is configured."""
        return f"[ChatSession] Received: {message[:50]}... (no LLM configured)"

    # === Context Operations ===

    def _get_context_size(self) -> int:
        """Get current context size in tokens."""
        if self._flow is not None and hasattr(self._flow, "_get_context_size"):
            return self._flow._get_context_size()
        # Estimate from turns
        return sum(t.tokens_in + t.tokens_out for t in self._turns)

    def get_context_utilization(self) -> float:
        """Get context utilization as a percentage."""
        context_size = self._get_context_size()
        return context_size / self.config.context_window

    # === History Operations ===

    def get_history(self, limit: int | None = None) -> list[Turn]:
        """
        Get conversation history.

        Args:
            limit: Maximum number of turns to return (most recent)

        Returns:
            List of turns
        """
        if limit is None:
            return self._turns.copy()
        return self._turns[-limit:]

    def get_messages(self) -> list[Message]:
        """
        Get all messages (flattened from turns).

        Returns:
            List of messages in order
        """
        messages = []
        for turn in self._turns:
            messages.append(turn.user_message)
            messages.append(turn.assistant_response)
        return messages

    # === Metrics ===

    def get_metrics(self) -> dict[str, Any]:
        """
        Get session metrics.

        Returns:
            Dictionary of metrics
        """
        if not self._turns:
            return {
                "session_id": self.session_id,
                "state": self._state.value,
                "turns_completed": 0,
                "tokens_in": 0,
                "tokens_out": 0,
                "average_turn_latency": 0.0,
                "context_utilization": 0.0,
                "entropy": self._entropy,
                "estimated_cost_usd": 0.0,
            }

        total_latency = sum(t.duration for t in self._turns)
        avg_latency = total_latency / len(self._turns)

        return {
            "session_id": self.session_id,
            "state": self._state.value,
            "turns_completed": len(self._turns),
            "tokens_in": self._budget.tokens_in_total,
            "tokens_out": self._budget.tokens_out_total,
            "average_turn_latency": round(avg_latency, 3),
            "context_utilization": round(self.get_context_utilization(), 3),
            "entropy": round(self._entropy, 3),
            "estimated_cost_usd": round(self._budget.estimated_cost_usd, 6),
        }

    # === Session Management ===

    def reset(self) -> None:
        """Reset the session to initial state."""
        self._turns.clear()
        self._current_turn = 0
        self._partial_response = ""
        self._streaming = False
        self._entropy = self.config.entropy_budget
        self._budget = SessionBudget()
        self._state = ChatSessionState.READY
        self._updated_at = datetime.now()

        if self._flow is not None:
            self._flow.reset()

    def set_name(self, name: str) -> None:
        """Set session name for persistence."""
        self._name = name
        self._updated_at = datetime.now()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the session."""
        if tag not in self._tags:
            self._tags.append(tag)
            self._updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize session to dictionary.

        Used for persistence.
        """
        return {
            "session_id": self.session_id,
            "node_path": self.node_path,
            "state": self._state.value,
            "name": self._name,
            "tags": self._tags,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
            "turn_count": len(self._turns),
            "turns": [t.to_dict() for t in self._turns],
            "entropy": self._entropy,
            "budget": self._budget.to_dict(),
            "config": {
                "context_window": self.config.context_window,
                "context_strategy": self.config.context_strategy.value,
                "max_turns": self.config.max_turns,
            },
        }


__all__ = [
    "ChatSessionState",
    "Message",
    "Turn",
    "SessionBudget",
    "ChatSession",
]
