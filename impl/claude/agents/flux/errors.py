"""
Flux-specific exceptions.

These exceptions provide structured error information for flux operations,
enabling proper error handling and debugging in flux pipelines.

Teaching:
    gotcha: All Flux exceptions carry a `context` dict with structured data.
            Don't just catch and log the message - check context for state info,
            buffer sizes, stage indices, etc. Useful for debugging pipelines.
            (Evidence: Structural - FluxError.__init__ stores context)

    gotcha: FluxStateError contains current_state and attempted_operation fields.
            When debugging "cannot X from state Y" errors, these tell you exactly
            what the flux was doing and what you tried to do.
            (Evidence: Structural - FluxStateError stores these fields)
"""

from typing import Any


class FluxError(Exception):
    """
    Base exception for flux operations.

    All flux-related exceptions inherit from this, enabling catch-all
    error handling while preserving structured error context.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None):
        super().__init__(message)
        self.context = context or {}

    def __str__(self) -> str:
        base = super().__str__()
        if self.context:
            return f"{base} (context: {self.context})"
        return base


class FluxStateError(FluxError):
    """
    Invalid state transition.

    Raised when an operation is attempted from an invalid state.
    For example, trying to start() a flux that is already FLOWING.
    """

    def __init__(
        self,
        message: str,
        current_state: str | None = None,
        attempted_operation: str | None = None,
    ):
        context: dict[str, Any] = {}
        if current_state:
            context["current_state"] = current_state
        if attempted_operation:
            context["attempted_operation"] = attempted_operation
        super().__init__(message, context)
        self.current_state = current_state
        self.attempted_operation = attempted_operation


class FluxEntropyError(FluxError):
    """
    Entropy budget exhausted.

    Raised when a flux operation would exceed the entropy budget.
    This implements J-gent physics - computation has a cost, and
    running out of budget causes collapse.
    """

    def __init__(
        self,
        message: str,
        entropy_remaining: float | None = None,
        entropy_required: float | None = None,
    ):
        context: dict[str, Any] = {}
        if entropy_remaining is not None:
            context["entropy_remaining"] = entropy_remaining
        if entropy_required is not None:
            context["entropy_required"] = entropy_required
        super().__init__(message, context)
        self.entropy_remaining = entropy_remaining
        self.entropy_required = entropy_required


class FluxBackpressureError(FluxError):
    """
    Backpressure limit exceeded.

    Raised when backpressure handling fails - for example, when
    the output buffer is full and the drop_policy cannot be applied.
    """

    def __init__(
        self,
        message: str,
        buffer_size: int | None = None,
        drop_policy: str | None = None,
    ):
        context: dict[str, Any] = {}
        if buffer_size is not None:
            context["buffer_size"] = buffer_size
        if drop_policy:
            context["drop_policy"] = drop_policy
        super().__init__(message, context)
        self.buffer_size = buffer_size
        self.drop_policy = drop_policy


class FluxPerturbationError(FluxError):
    """
    Perturbation failed.

    Raised when a perturbation (invoke on a FLOWING flux) fails
    to be processed. This can happen if:
    - The flux transitions to a non-FLOWING state during perturbation
    - The inner agent raises an exception
    - The perturbation timeout is exceeded
    """

    def __init__(
        self,
        message: str,
        perturbation_data: Any = None,
        inner_exception: Exception | None = None,
    ):
        context: dict[str, Any] = {}
        if perturbation_data is not None:
            context["perturbation_data"] = repr(perturbation_data)
        if inner_exception:
            context["inner_exception"] = str(inner_exception)
        super().__init__(message, context)
        self.perturbation_data = perturbation_data
        self.inner_exception = inner_exception


class FluxPipelineError(FluxError):
    """
    Pipeline composition or execution failed.

    Raised when a flux pipeline encounters an error during
    composition or execution.
    """

    def __init__(
        self,
        message: str,
        stage_index: int | None = None,
        stage_name: str | None = None,
    ):
        context: dict[str, Any] = {}
        if stage_index is not None:
            context["stage_index"] = stage_index
        if stage_name:
            context["stage_name"] = stage_name
        super().__init__(message, context)
        self.stage_index = stage_index
        self.stage_name = stage_name


class FluxSourceError(FluxError):
    """
    Source stream error.

    Raised when the input source stream encounters an error
    that prevents further processing.
    """

    def __init__(
        self,
        message: str,
        source_type: str | None = None,
        events_before_error: int | None = None,
    ):
        context: dict[str, Any] = {}
        if source_type:
            context["source_type"] = source_type
        if events_before_error is not None:
            context["events_before_error"] = events_before_error
        super().__init__(message, context)
        self.source_type = source_type
        self.events_before_error = events_before_error
