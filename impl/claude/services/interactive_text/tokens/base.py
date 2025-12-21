"""
MeaningToken Base Class Implementation.

This module provides the concrete base implementation for meaning tokens,
including the on_interact method with trace witness capture for formal
verification integration.

MeaningTokens are the atomic unit of interface in the projection-based
architecture. They carry meaning independent of how they are rendered,
and project to different observer surfaces through projection functors.

See: .kiro/specs/meaning-token-frontend/design.md
Requirements: 1.2, 6.3, 12.1
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar

from services.interactive_text.contracts import (
    Affordance,
    AffordanceAction,
    InteractionResult,
    Observer,
    TokenDefinition,
)
from services.interactive_text.registry import TokenRegistry

T = TypeVar("T")  # Projection target type


@dataclass(frozen=True)
class ExecutionTrace:
    """Trace of a token interaction for formal verification.

    ExecutionTraces capture the details of token interactions for
    integration with the verification system. They form the basis
    of Trace_Witnesses that provide constructive proofs of behavior.

    Attributes:
        agent_path: AGENTESE path of the handler
        operation: The operation performed (e.g., "toggle", "navigate")
        input_data: Input data for the operation
        output_data: Output data from the operation
        timestamp: When the interaction occurred
        observer_id: ID of the observer who performed the interaction
    """

    agent_path: str
    operation: str
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    observer_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_path": self.agent_path,
            "operation": self.operation,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "timestamp": self.timestamp.isoformat(),
            "observer_id": self.observer_id,
        }


@dataclass(frozen=True)
class TraceWitness:
    """A constructive proof of interaction captured for formal verification.

    TraceWitnesses are created when tokens are interacted with, providing
    evidence that can be used by the verification system to prove
    correctness properties.

    Attributes:
        id: Unique identifier for this witness
        trace: The execution trace being witnessed
        verified: Whether this witness has been verified
        verification_result: Result of verification (if verified)
    """

    id: str
    trace: ExecutionTrace
    verified: bool = False
    verification_result: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "trace": self.trace.to_dict(),
            "verified": self.verified,
            "verification_result": self.verification_result,
        }


class BaseMeaningToken(ABC, Generic[T]):
    """Base implementation for meaning tokens with interaction handling.

    This class extends the MeaningToken protocol with concrete implementations
    for common functionality including:
    - Affordance retrieval based on observer capabilities
    - Interaction handling with trace witness capture
    - Token serialization

    Subclasses must implement:
    - token_type: Return the token type name
    - source_text: Return the original matched text
    - source_position: Return (start, end) position in source
    - get_affordances: Return affordances for an observer
    - project: Project to target-specific rendering
    - _execute_action: Execute the actual action logic

    Type Parameters:
        T: The type of the projection target
    """

    @property
    @abstractmethod
    def token_type(self) -> str:
        """Token type name from registry."""
        ...

    @property
    @abstractmethod
    def source_text(self) -> str:
        """Original text that was recognized as this token."""
        ...

    @property
    @abstractmethod
    def source_position(self) -> tuple[int, int]:
        """(start, end) position in source document."""
        ...

    @property
    def token_id(self) -> str:
        """Unique identifier for this token instance."""
        start, end = self.source_position
        return f"{self.token_type}:{start}:{end}"

    def get_definition(self) -> TokenDefinition | None:
        """Get the token definition from the registry."""
        return TokenRegistry.get(self.token_type)

    @abstractmethod
    async def get_affordances(self, observer: Observer) -> list[Affordance]:
        """Get available affordances for this observer.

        Affordances may be filtered based on observer capabilities and role.

        Args:
            observer: The observer requesting affordances

        Returns:
            List of available affordances for this observer
        """
        ...

    @abstractmethod
    async def project(self, target: str, observer: Observer) -> str | dict[str, Any]:
        """Project token to target-specific rendering.

        Args:
            target: Target name (e.g., "cli", "web", "json")
            observer: The observer receiving the projection

        Returns:
            Target-specific rendering of this token (str for text targets, dict for JSON)
        """
        ...

    @abstractmethod
    async def _execute_action(
        self,
        action: AffordanceAction,
        observer: Observer,
        **kwargs: Any,
    ) -> Any:
        """Execute the actual action logic.

        This method is called by on_interact after affordance validation.
        Subclasses implement the specific action behavior here.

        Args:
            action: The action being performed
            observer: The observer performing the action
            **kwargs: Additional action-specific arguments

        Returns:
            The result of the action
        """
        ...

    async def on_interact(
        self,
        action: AffordanceAction,
        observer: Observer,
        capture_trace: bool = True,
        **kwargs: Any,
    ) -> InteractionResult:
        """Handle interaction with this token.

        This method:
        1. Validates the action is available for this observer
        2. Executes the action
        3. Captures a trace witness for formal verification (if enabled)
        4. Returns the interaction result

        Args:
            action: The action being performed
            observer: The observer performing the action
            capture_trace: Whether to capture a trace witness (default True)
            **kwargs: Additional action-specific arguments

        Returns:
            InteractionResult with success status, data, and optional witness ID

        Requirements: 1.2, 6.3, 12.1
        """
        # Get available affordances for this observer
        affordances = await self.get_affordances(observer)

        # Find the affordance for this action
        affordance = next(
            (a for a in affordances if a.action == action and a.enabled),
            None,
        )

        if affordance is None:
            return InteractionResult.not_available(action.value)

        try:
            # Execute the action
            result = await self._execute_action(action, observer, **kwargs)

            # Capture trace witness if enabled
            witness_id: str | None = None
            if capture_trace:
                witness = await self._capture_trace_witness(
                    affordance=affordance,
                    observer=observer,
                    input_data={"token": self.source_text, **kwargs},
                    output_data=result,
                )
                witness_id = witness.id

            return InteractionResult.success_result(data=result, witness_id=witness_id)

        except Exception as e:
            return InteractionResult.failure(str(e))

    async def _capture_trace_witness(
        self,
        affordance: Affordance,
        observer: Observer,
        input_data: dict[str, Any],
        output_data: Any,
    ) -> TraceWitness:
        """Capture a trace witness for formal verification.

        Creates an ExecutionTrace and wraps it in a TraceWitness for
        integration with the verification system.

        Args:
            affordance: The affordance that was invoked
            observer: The observer who performed the interaction
            input_data: Input data for the operation
            output_data: Output data from the operation

        Returns:
            TraceWitness capturing the interaction

        Requirements: 6.3, 12.1
        """
        import uuid

        trace = ExecutionTrace(
            agent_path=affordance.handler,
            operation=affordance.name,
            input_data=input_data,
            output_data=output_data,
            observer_id=observer.id,
        )

        witness = TraceWitness(
            id=uuid.uuid4().hex,
            trace=trace,
        )

        # In a full implementation, this would invoke:
        # await logos.invoke("world.trace.capture", observer, trace=trace)
        # For now, we return the witness directly

        return witness

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "token_type": self.token_type,
            "source_text": self.source_text,
            "source_position": self.source_position,
            "token_id": self.token_id,
        }


def filter_affordances_by_observer(
    affordances: tuple[Affordance, ...],
    observer: Observer,
    required_capabilities: dict[str, frozenset[str]] | None = None,
) -> list[Affordance]:
    """Filter affordances based on observer capabilities and role.

    This utility function filters affordances to only include those
    that the observer can actually use based on their capabilities.

    Args:
        affordances: All affordances for the token
        observer: The observer to filter for
        required_capabilities: Optional mapping of affordance names to
            required capabilities. If not provided, all affordances
            are returned.

    Returns:
        List of affordances available to this observer
    """
    if required_capabilities is None:
        return list(affordances)

    result: list[Affordance] = []
    for affordance in affordances:
        required = required_capabilities.get(affordance.name, frozenset())
        if required.issubset(observer.capabilities):
            result.append(affordance)
        else:
            # Return disabled version of affordance
            result.append(
                Affordance(
                    name=affordance.name,
                    action=affordance.action,
                    handler=affordance.handler,
                    enabled=False,
                    description=f"{affordance.description} (requires: {', '.join(required)})",
                )
            )

    return result


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "BaseMeaningToken",
    "ExecutionTrace",
    "TraceWitness",
    "filter_affordances_by_observer",
]
