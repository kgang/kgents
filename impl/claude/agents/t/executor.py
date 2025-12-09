"""
T-gents Phase 3: Tool Execution Runtime

This module implements a robust execution runtime for Tool[A, B] agents,
including Result monad integration, circuit breaker pattern, and retry logic
with exponential backoff.

Philosophy:
- Railway Oriented Programming: Use Result monad for explicit error handling
- Circuit Breaker: Fail fast when downstream services are unhealthy
- Retry with Backoff: Gracefully handle transient failures
- Composable: All wrappers compose via >> like normal agents

Integration:
- Result monad from bootstrap.types
- Tool base class from agents/t/tool.py
- P-gents for error parsing
- W-gents for observability

References:
- spec/t-gents/README.md - T-gents specification
- bootstrap.types - Result monad and Agent[A, B]
- agents/t/tool.py - Tool base class
"""

from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generic, Optional, TypeVar

from bootstrap.types import Result, ok, err
from agents.t.tool import Tool, ToolError, ToolErrorType, ToolTrace
from agents.t.permissions import (
    PermissionClassifier,
    AgentContext,
    ToolCapabilities,
    TemporaryToken,
    PermissionLevel,
    AuditLogger,
)

# Type variables
A = TypeVar("A")
B = TypeVar("B")


# --- Circuit Breaker ---


class CircuitState(Enum):
    """State of the circuit breaker."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit tripped, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern."""

    failure_threshold: int = 5  # Failures before opening circuit
    success_threshold: int = 2  # Successes before closing from half-open
    timeout_seconds: int = 60  # Time before trying half-open
    monitored_errors: list[ToolErrorType] = field(
        default_factory=lambda: [
            ToolErrorType.NETWORK,
            ToolErrorType.TIMEOUT,
            ToolErrorType.RATE_LIMIT,
        ]
    )


@dataclass
class CircuitBreakerState:
    """Runtime state of circuit breaker."""

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_state_change: datetime = field(default_factory=datetime.now)


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is OPEN."""

    def __init__(self, tool_name: str, state: CircuitBreakerState):
        self.tool_name = tool_name
        self.state = state
        super().__init__(
            f"Circuit breaker OPEN for tool '{tool_name}' "
            f"(failures={state.failure_count}, "
            f"last_failure={state.last_failure_time})"
        )


class CircuitBreakerTool(Tool[A, B], Generic[A, B]):
    """
    Tool wrapper with circuit breaker pattern.

    Implements the Circuit Breaker pattern to fail fast when a tool
    is experiencing repeated failures, preventing cascading failures
    and allowing time for recovery.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, reject all requests immediately
    - HALF_OPEN: Testing recovery, allow limited requests

    Behavior:
    - CLOSED → OPEN: After N consecutive failures
    - OPEN → HALF_OPEN: After timeout expires
    - HALF_OPEN → CLOSED: After M consecutive successes
    - HALF_OPEN → OPEN: On any failure

    Usage:
        tool = MyTool()
        protected = CircuitBreakerTool(
            tool,
            config=CircuitBreakerConfig(
                failure_threshold=5,
                success_threshold=2,
                timeout_seconds=60
            )
        )

        # Will automatically open circuit after 5 failures
        result = await protected.invoke(input_data)
    """

    def __init__(
        self,
        inner: Tool[A, B],
        config: Optional[CircuitBreakerConfig] = None,
    ):
        self.inner = inner
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState()
        self.meta = inner.meta

    def _should_monitor_error(self, error: ToolError) -> bool:
        """Check if error type should trip circuit breaker."""
        return error.error_type in self.config.monitored_errors

    def _can_attempt_request(self) -> bool:
        """Check if circuit breaker allows request."""
        if self.state.state == CircuitState.CLOSED:
            return True

        if self.state.state == CircuitState.OPEN:
            # Check if timeout expired
            if self.state.last_failure_time:
                elapsed = datetime.now() - self.state.last_failure_time
                if elapsed.total_seconds() >= self.config.timeout_seconds:
                    # Transition to HALF_OPEN
                    self.state.state = CircuitState.HALF_OPEN
                    self.state.last_state_change = datetime.now()
                    return True
            return False

        if self.state.state == CircuitState.HALF_OPEN:
            # Allow limited requests in HALF_OPEN
            return True

        return False

    def _record_success(self) -> None:
        """Record successful execution."""
        if self.state.state == CircuitState.HALF_OPEN:
            self.state.success_count += 1
            if self.state.success_count >= self.config.success_threshold:
                # Close circuit
                self.state.state = CircuitState.CLOSED
                self.state.failure_count = 0
                self.state.success_count = 0
                self.state.last_state_change = datetime.now()
        elif self.state.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.state.failure_count = 0

    def _record_failure(self, error: ToolError) -> None:
        """Record failed execution."""
        if not self._should_monitor_error(error):
            return

        self.state.last_failure_time = datetime.now()

        if self.state.state == CircuitState.HALF_OPEN:
            # Any failure in HALF_OPEN reopens circuit
            self.state.state = CircuitState.OPEN
            self.state.success_count = 0
            self.state.last_state_change = datetime.now()
        elif self.state.state == CircuitState.CLOSED:
            self.state.failure_count += 1
            if self.state.failure_count >= self.config.failure_threshold:
                # Open circuit
                self.state.state = CircuitState.OPEN
                self.state.last_state_change = datetime.now()

    async def invoke(self, input: A) -> B:
        """Execute with circuit breaker protection."""
        if not self._can_attempt_request():
            raise CircuitBreakerError(self.inner.name, self.state)

        try:
            output = await self.inner.invoke(input)
            self._record_success()
            return output
        except ToolError as e:
            self._record_failure(e)
            raise

    def get_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self.state

    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED."""
        self.state = CircuitBreakerState()


# --- Tool Executor with Result Monad ---


class ToolExecutor(Generic[A, B]):
    """
    Execution runtime for Tool[A, B] with Result monad.

    Wraps tool execution in Result[B, ToolError] for Railway Oriented
    Programming, converting exceptions into explicit error values.

    This allows composition of tools with explicit error handling:
        result = await executor.execute(input)
        result.map(process_success).map_err(handle_error)

    Features:
    - Converts exceptions to Result[B, ToolError]
    - Supports tracing via W-gents
    - Composes with circuit breaker and retry
    - Type-safe error handling

    Usage:
        tool = MyTool()
        executor = ToolExecutor(tool)

        # Execute with Result monad
        result: Result[Output, ToolError] = await executor.execute(input_data)

        match result:
            case Ok(value):
                print(f"Success: {value}")
            case Err(error):
                print(f"Error: {error}")
    """

    def __init__(
        self,
        tool: Tool[A, B],
        enable_tracing: bool = False,
    ):
        self.tool = tool
        self.enable_tracing = enable_tracing

    async def execute(self, input: A) -> Result[B, ToolError]:
        """
        Execute tool and return Result monad.

        Converts exceptions into ToolError wrapped in Result.Err,
        allowing explicit error handling via map/bind/match.
        """
        trace: Optional[ToolTrace] = None
        if self.enable_tracing:
            trace = ToolTrace(tool_name=self.tool.name, input=input)

        try:
            output = await self.tool.invoke(input)

            if trace:
                trace.finish_success(output)

            return ok(output)

        except ToolError as e:
            if trace:
                trace.finish_error(e)

            return err(e, str(e), e.recoverable)

        except Exception as e:
            # Convert unexpected exceptions to ToolError
            tool_error = ToolError(
                error_type=ToolErrorType.FATAL,
                message=str(e),
                tool_name=self.tool.name,
                input=input,
                recoverable=False,
            )

            if trace:
                trace.finish_error(tool_error)

            return err(tool_error, str(e), False)

    async def execute_with_timeout(
        self, input: A, timeout_ms: int
    ) -> Result[B, ToolError]:
        """
        Execute tool with timeout.

        Returns ToolError(TIMEOUT) if execution exceeds timeout.
        """
        try:
            result = await asyncio.wait_for(
                self.execute(input), timeout=timeout_ms / 1000
            )
            return result
        except asyncio.TimeoutError:
            timeout_error = ToolError(
                error_type=ToolErrorType.TIMEOUT,
                message=f"Tool execution timed out after {timeout_ms}ms",
                tool_name=self.tool.name,
                input=input,
                recoverable=True,
            )
            return err(timeout_error, str(timeout_error), True)


# --- Retry with Exponential Backoff (Result Monad Version) ---


@dataclass
class RetryConfig:
    """Configuration for retry with exponential backoff."""

    max_attempts: int = 3
    initial_delay_ms: int = 100
    max_delay_ms: int = 10000
    backoff_multiplier: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd


class RetryExecutor(Generic[A, B]):
    """
    Execution runtime with retry and exponential backoff.

    Retries failed tool executions with exponential backoff,
    respecting ToolError.recoverable flag and retry_after_ms hints.

    Features:
    - Exponential backoff with jitter
    - Respects retry_after_ms from rate limit errors
    - Only retries recoverable errors
    - Returns Result monad for composability

    Usage:
        tool = MyTool()
        executor = RetryExecutor(
            tool,
            config=RetryConfig(max_attempts=5, initial_delay_ms=200)
        )

        result = await executor.execute(input_data)
        # Automatically retries on recoverable failures
    """

    def __init__(
        self,
        tool: Tool[A, B],
        config: Optional[RetryConfig] = None,
    ):
        self.tool = tool
        self.config = config or RetryConfig()
        self.executor = ToolExecutor(tool)

    def _calculate_delay(self, attempt: int, error: Optional[ToolError] = None) -> int:
        """Calculate delay before next retry."""
        # Use retry_after_ms from error if provided (e.g., rate limit)
        if error and error.retry_after_ms:
            return min(error.retry_after_ms, self.config.max_delay_ms)

        # Exponential backoff
        delay = self.config.initial_delay_ms * (self.config.backoff_multiplier**attempt)
        delay = min(delay, self.config.max_delay_ms)

        # Add jitter to prevent thundering herd
        if self.config.jitter:
            import random

            jitter_amount = delay * 0.1  # 10% jitter
            delay = delay + random.uniform(-jitter_amount, jitter_amount)

        return int(delay)

    async def execute(self, input: A) -> Result[B, ToolError]:
        """
        Execute tool with retry and exponential backoff.

        Retries on recoverable errors, respecting backoff configuration.
        """
        last_error: Optional[ToolError] = None

        for attempt in range(self.config.max_attempts):
            result = await self.executor.execute(input)

            # Success - return immediately
            if result.is_ok():
                return result

            # Extract error
            error = result.error
            last_error = error

            # Don't retry non-recoverable errors
            if not error.recoverable:
                return result

            # Don't retry on last attempt
            if attempt == self.config.max_attempts - 1:
                return result

            # Calculate delay and wait
            delay_ms = self._calculate_delay(attempt, error)
            await asyncio.sleep(delay_ms / 1000)

        # Should never reach here, but return last error
        return err(last_error, str(last_error), last_error.recoverable)


# --- Composite Executor ---


class RobustToolExecutor(Generic[A, B]):
    """
    Composite executor with circuit breaker, retry, and Result monad.

    Combines all execution patterns into a single robust executor:
    - Circuit Breaker: Fail fast on repeated failures
    - Retry with Backoff: Handle transient errors
    - Result Monad: Explicit error handling
    - Tracing: Observability via W-gents

    Usage:
        tool = MyTool()
        executor = RobustToolExecutor(
            tool,
            circuit_config=CircuitBreakerConfig(failure_threshold=5),
            retry_config=RetryConfig(max_attempts=3)
        )

        result = await executor.execute(input_data)
        # Automatically handles failures with circuit breaker + retry
    """

    def __init__(
        self,
        tool: Tool[A, B],
        circuit_config: Optional[CircuitBreakerConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        enable_tracing: bool = False,
    ):
        # Wrap tool with circuit breaker
        self.circuit_breaker = CircuitBreakerTool(tool, circuit_config)

        # Wrap circuit breaker with retry
        self.retry_executor = RetryExecutor(self.circuit_breaker, retry_config)

        self.enable_tracing = enable_tracing

    async def execute(self, input: A) -> Result[B, ToolError]:
        """
        Execute tool with full protection stack.

        Order: Retry → Circuit Breaker → Tool
        - Retry wraps circuit breaker
        - Circuit breaker wraps tool
        """
        try:
            return await self.retry_executor.execute(input)
        except CircuitBreakerError as e:
            # Convert circuit breaker error to ToolError
            circuit_error = ToolError(
                error_type=ToolErrorType.FATAL,
                message=str(e),
                tool_name=e.tool_name,
                input=input,
                recoverable=False,
            )
            return err(circuit_error, str(e), False)

    def get_circuit_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self.circuit_breaker.get_state()

    def reset_circuit(self) -> None:
        """Manually reset circuit breaker."""
        self.circuit_breaker.reset()


# --- Secure Tool Executor (Phase 5: Security & Permissions) ---


class SecureToolExecutor(Generic[A, B]):
    """
    Tool executor with permission checks and audit logging.

    Implements T-gents Phase 5: Security & Permissions
    - Permission checks before execution (ABAC)
    - Short-lived token validation
    - Audit logging for all executions
    - Integration with RobustToolExecutor for reliability

    Security Model:
    - Zero standing privileges: All permissions contextual
    - Attribute-based access control (ABAC)
    - Short-lived tokens (15-60 minutes)
    - Comprehensive audit trail

    Usage:
        tool = MyTool()
        capabilities = ToolCapabilities(requires_network=True)
        context = AgentContext(
            agent_id="research_agent",
            security_level=SecurityLevel.MEDIUM,
            allow_network=True,
        )

        executor = SecureToolExecutor(
            tool,
            capabilities=capabilities,
            context=context,
        )

        result = await executor.execute(input_data)
        # Permission checked, execution audited
    """

    def __init__(
        self,
        tool: Tool[A, B],
        capabilities: ToolCapabilities,
        context: AgentContext,
        classifier: Optional[PermissionClassifier] = None,
        audit_logger: Optional[AuditLogger] = None,
        circuit_config: Optional[CircuitBreakerConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        enable_tracing: bool = True,
    ):
        """
        Initialize secure tool executor.

        Args:
            tool: Tool to execute
            capabilities: Required capabilities for this tool
            context: Agent execution context
            classifier: Permission classifier (default: create new)
            audit_logger: Audit logger (default: create new)
            circuit_config: Circuit breaker config
            retry_config: Retry config
            enable_tracing: Enable W-gent tracing
        """
        self.tool = tool
        self.capabilities = capabilities
        self.context = context

        # Permission and audit
        self.classifier = classifier or PermissionClassifier()
        self.audit_logger = audit_logger or AuditLogger()

        # Robust execution
        self.robust_executor = RobustToolExecutor(
            tool,
            circuit_config=circuit_config,
            retry_config=retry_config,
            enable_tracing=enable_tracing,
        )

        # Token (if granted)
        self.token: Optional[TemporaryToken] = None

    async def request_permission(
        self, duration_seconds: int = 900
    ) -> Result[TemporaryToken, str]:
        """
        Request short-lived permission token.

        Args:
            duration_seconds: Token lifetime (default 900 = 15 min)

        Returns:
            Result containing token or error message
        """
        result = self.classifier.grant_temporary(
            tool_id=self.tool.name,
            capabilities=self.capabilities,
            context=self.context,
            duration_seconds=duration_seconds,
        )

        if result.is_ok():
            self.token = result.value

        # Log permission request
        permission = self.classifier.classify(self.capabilities, self.context)
        await self.audit_logger.log_permission_check(
            tool_id=self.tool.name,
            tool_name=self.tool.name,
            context=self.context,
            permission=permission,
            token_id=self.token.token_id if self.token else None,
        )

        return result

    async def execute(self, input: A) -> Result[B, ToolError]:
        """
        Execute tool with permission check and audit logging.

        Algorithm:
        1. Check permission (token or classify)
        2. If denied, return permission error
        3. Execute tool via robust executor
        4. Log execution to audit trail
        5. Return result

        Returns:
            Result[B, ToolError] with permission/execution errors
        """
        start_time = datetime.now()

        # 1. Check permission
        permission: PermissionLevel

        if self.token:
            # Use existing token
            token_result = self.token.use()
            if not token_result.is_ok():
                # Token invalid/expired
                permission_error = ToolError(
                    error_type=ToolErrorType.PERMISSION,
                    message=token_result.message,
                    tool_name=self.tool.name,
                    input=input,
                    recoverable=False,
                )

                await self.audit_logger.log_execution(
                    tool_id=self.tool.name,
                    tool_name=self.tool.name,
                    context=self.context,
                    permission=PermissionLevel.DENIED,
                    input_summary=self._summarize_input(input),
                    success=False,
                    error=str(permission_error),
                    token_id=self.token.token_id,
                )

                return err(permission_error, str(permission_error), False)

            permission = self.token.permission

        else:
            # Classify permission on-demand
            permission = self.classifier.classify(self.capabilities, self.context)

            if permission == PermissionLevel.DENIED:
                permission_error = ToolError(
                    error_type=ToolErrorType.PERMISSION,
                    message=f"Permission denied for tool '{self.tool.name}' in context {self.context.agent_id}",
                    tool_name=self.tool.name,
                    input=input,
                    recoverable=False,
                )

                await self.audit_logger.log_execution(
                    tool_id=self.tool.name,
                    tool_name=self.tool.name,
                    context=self.context,
                    permission=permission,
                    input_summary=self._summarize_input(input),
                    success=False,
                    error=str(permission_error),
                )

                return err(permission_error, str(permission_error), False)

            if permission == PermissionLevel.RESTRICTED:
                permission_error = ToolError(
                    error_type=ToolErrorType.PERMISSION,
                    message=f"Tool '{self.tool.name}' requires additional approval",
                    tool_name=self.tool.name,
                    input=input,
                    recoverable=True,  # Can be resolved with approval
                )

                await self.audit_logger.log_execution(
                    tool_id=self.tool.name,
                    tool_name=self.tool.name,
                    context=self.context,
                    permission=permission,
                    input_summary=self._summarize_input(input),
                    success=False,
                    error=str(permission_error),
                )

                return err(permission_error, str(permission_error), True)

        # 2. Execute tool via robust executor
        result = await self.robust_executor.execute(input)

        # 3. Calculate metrics
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        # 4. Log execution
        await self.audit_logger.log_execution(
            tool_id=self.tool.name,
            tool_name=self.tool.name,
            context=self.context,
            permission=permission,
            input_summary=self._summarize_input(input),
            success=result.is_ok(),
            output_summary=self._summarize_output(result.value)
            if result.is_ok()
            else None,
            error=str(result.error) if result.is_err() else None,
            duration_ms=duration_ms,
            token_id=self.token.token_id if self.token else None,
        )

        return result

    def _summarize_input(self, input: A) -> str:
        """
        Summarize input for audit log.

        Avoids logging full data (may contain sensitive info).
        """
        input_str = str(input)
        if len(input_str) > 100:
            return input_str[:97] + "..."
        return input_str

    def _summarize_output(self, output: B) -> str:
        """
        Summarize output for audit log.

        Avoids logging full data (may contain sensitive info).
        """
        output_str = str(output)
        if len(output_str) > 100:
            return output_str[:97] + "..."
        return output_str

    def get_permission_status(self) -> dict[str, Any]:
        """
        Get current permission status.

        Returns:
            Dictionary with permission details:
            - permission: Current permission level
            - token: Token info (if exists)
            - context: Context summary
        """
        permission = self.classifier.classify(self.capabilities, self.context)

        status = {
            "permission": permission.value,
            "tool": self.tool.name,
            "context_id": self.context.agent_id,
            "token": None,
        }

        if self.token:
            status["token"] = {
                "id": self.token.token_id,
                "valid": self.token.is_valid(),
                "expires_at": self.token.expires_at.isoformat(),
                "uses": self.token.uses,
            }

        return status


# --- Exports ---

__all__ = [
    # Circuit Breaker
    "CircuitState",
    "CircuitBreakerConfig",
    "CircuitBreakerState",
    "CircuitBreakerError",
    "CircuitBreakerTool",
    # Executors
    "ToolExecutor",
    "RetryExecutor",
    "RobustToolExecutor",
    "SecureToolExecutor",
    # Config
    "RetryConfig",
]
