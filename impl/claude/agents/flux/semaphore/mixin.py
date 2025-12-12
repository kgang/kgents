"""
SemaphoreMixin: Protocol for agents that can yield semaphores.

Agents implementing SemaphoreCapable can:
1. Return SemaphoreToken from invoke() to yield to human
2. Implement resume() to complete processing after human input
3. Optionally implement freeze_state() for custom state serialization

The Rodizio Pattern:
- Agent encounters situation needing human input
- Agent returns SemaphoreToken (not yields!)
- FluxAgent detects, ejects to Purgatory
- Stream continues (no head-of-line blocking)
- Human resolves, ReentryContext injected as Perturbation
- Agent.resume() completes processing
"""

from __future__ import annotations

import pickle
from abc import abstractmethod
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from .reentry import ReentryContext
from .token import SemaphoreToken

A = TypeVar("A")  # Input type
B = TypeVar("B", covariant=True)  # Output type (covariant for Protocol)
S = TypeVar("S")  # State type


@runtime_checkable
class SemaphoreCapable(Protocol[B]):
    """
    Protocol for agents that can yield semaphores.

    An agent implementing this protocol can:
    1. Return SemaphoreToken from invoke() to yield to human
    2. Implement resume() to complete processing with human input

    Example:
        >>> class ReviewAgent(SemaphoreCapable[Document, Review]):
        ...     async def invoke(self, doc: Document) -> Review | SemaphoreToken:
        ...         if doc.is_sensitive:
        ...             return SemaphoreToken(
        ...                 reason=SemaphoreReason.APPROVAL_NEEDED,
        ...                 frozen_state=pickle.dumps({"doc_id": doc.id}),
        ...                 prompt="Review sensitive document?",
        ...             )
        ...         return self._process(doc)
        ...
        ...     async def resume(
        ...         self,
        ...         frozen_state: bytes,
        ...         human_input: Any,
        ...     ) -> Review:
        ...         state = pickle.loads(frozen_state)
        ...         doc = self._load_doc(state["doc_id"])
        ...         return self._process(doc, approved=human_input == "Approve")
    """

    @abstractmethod
    async def resume(
        self,
        frozen_state: bytes,
        human_input: Any,
    ) -> B:
        """
        Resume processing after human provides context.

        Called when ReentryContext is injected as Perturbation.
        The agent should:
        1. Unpickle frozen_state to restore context
        2. Use human_input to complete the processing
        3. Return the final result

        Args:
            frozen_state: Pickled state from SemaphoreToken
            human_input: What the human provided

        Returns:
            Final result of type B
        """
        ...


class SemaphoreMixin(Generic[A, B, S]):
    """
    Mixin providing semaphore utilities for agents.

    Provides helpers for:
    - Creating SemaphoreTokens with proper state serialization
    - Processing ReentryContext in resume()
    - Type-safe state handling

    Example:
        >>> class MyAgent(SemaphoreMixin[Input, Output, MyState]):
        ...     async def invoke(self, input: Input) -> Output | SemaphoreToken:
        ...         if needs_human:
        ...             state = MyState(partial_result=partial)
        ...             return self.create_semaphore(
        ...                 reason=SemaphoreReason.CONTEXT_REQUIRED,
        ...                 state=state,
        ...                 prompt="Which option?",
        ...                 options=["A", "B", "C"],
        ...             )
        ...         return self._process(input)
        ...
        ...     async def resume(
        ...         self,
        ...         frozen_state: bytes,
        ...         human_input: Any,
        ...     ) -> Output:
        ...         state = self.restore_state(frozen_state)
        ...         return self._complete(state, human_input)
    """

    def create_semaphore(
        self,
        reason: Any,  # SemaphoreReason
        state: S,
        original_event: Any = None,
        prompt: str = "",
        options: list[str] | None = None,
        severity: str = "info",
        **kwargs: Any,
    ) -> SemaphoreToken[Any]:
        """
        Create a SemaphoreToken with serialized state.

        Args:
            reason: Why the agent is yielding
            state: Agent state to freeze (will be pickled)
            original_event: The event that triggered this
            prompt: Human-readable question
            options: Suggested responses
            severity: "info" | "warning" | "critical"
            **kwargs: Additional token fields (deadline, escalation, etc.)

        Returns:
            SemaphoreToken ready to return from invoke()
        """
        from .reason import SemaphoreReason

        return SemaphoreToken(
            reason=reason
            if isinstance(reason, SemaphoreReason)
            else SemaphoreReason(reason),
            frozen_state=self.freeze_state(state),
            original_event=original_event,
            prompt=prompt,
            options=options or [],
            severity=severity,
            **kwargs,
        )

    def freeze_state(self, state: S) -> bytes:
        """
        Serialize state for storage in SemaphoreToken.

        Override this for custom serialization (e.g., JSON, msgpack).
        Default uses pickle.

        Args:
            state: State to serialize

        Returns:
            Serialized bytes
        """
        return pickle.dumps(state)

    def restore_state(self, frozen_state: bytes) -> S:
        """
        Deserialize state from ReentryContext.

        Override this for custom deserialization.
        Default uses pickle.

        Args:
            frozen_state: Bytes from SemaphoreToken

        Returns:
            Restored state object
        """
        result: S = pickle.loads(frozen_state)
        return result

    def process_reentry(self, reentry: ReentryContext[Any]) -> tuple[S, Any]:
        """
        Process a ReentryContext into (state, human_input).

        Convenience method for resume() implementations.

        Args:
            reentry: The ReentryContext from Purgatory

        Returns:
            Tuple of (restored_state, human_input)
        """
        return self.restore_state(reentry.frozen_state), reentry.human_input


def is_semaphore_token(result: Any) -> bool:
    """
    Check if a result is a SemaphoreToken.

    Used by FluxAgent to detect when an agent yields.

    Args:
        result: Return value from agent.invoke()

    Returns:
        True if result is a SemaphoreToken
    """
    return isinstance(result, SemaphoreToken)


def is_semaphore_capable(agent: Any) -> bool:
    """
    Check if an agent implements SemaphoreCapable.

    Args:
        agent: The agent to check

    Returns:
        True if agent has a resume() method
    """
    return isinstance(agent, SemaphoreCapable) or hasattr(agent, "resume")
