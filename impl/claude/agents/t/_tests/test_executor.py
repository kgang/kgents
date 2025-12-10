"""
Test suite for T-gents Phase 3: Tool Execution Runtime

Tests for executor.py:
- ToolExecutor with Result monad
- CircuitBreakerTool
- RetryExecutor with exponential backoff
- RobustToolExecutor (composite)
"""

import asyncio
import pytest
from datetime import datetime

from agents.t.tool import Tool, ToolMeta, ToolError, ToolErrorType
from agents.t.executor import (
    # Circuit Breaker
    CircuitState,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitBreakerTool,
    # Executors
    ToolExecutor,
    RetryExecutor,
    RobustToolExecutor,
    RetryConfig,
)


# --- Test Tools ---


class SuccessTool(Tool[str, str]):
    """Tool that always succeeds."""

    def __init__(self):
        self.meta = ToolMeta.minimal(
            name="success_tool",
            description="Always succeeds",
            input_schema=str,
            output_schema=str,
        )
        self.call_count = 0

    async def invoke(self, input: str) -> str:
        self.call_count += 1
        return f"Success: {input}"


class FailingTool(Tool[str, str]):
    """Tool that fails N times then succeeds."""

    def __init__(self, fail_count: int, error_type: ToolErrorType):
        self.meta = ToolMeta.minimal(
            name="failing_tool",
            description="Fails N times",
            input_schema=str,
            output_schema=str,
        )
        self.fail_count = fail_count
        self.error_type = error_type
        self.call_count = 0
        self.attempts = 0

    async def invoke(self, input: str) -> str:
        self.call_count += 1
        self.attempts += 1

        if self.attempts <= self.fail_count:
            raise ToolError(
                error_type=self.error_type,
                message=f"Simulated failure (attempt {self.attempts})",
                tool_name=self.name,
                input=input,
                recoverable=self.error_type
                in [
                    ToolErrorType.NETWORK,
                    ToolErrorType.TIMEOUT,
                    ToolErrorType.TRANSIENT,
                ],
            )

        return f"Success after {self.attempts} attempts"


class AlwaysFailingTool(Tool[str, str]):
    """Tool that always fails."""

    def __init__(self, error_type: ToolErrorType):
        self.meta = ToolMeta.minimal(
            name="always_failing",
            description="Always fails",
            input_schema=str,
            output_schema=str,
        )
        self.error_type = error_type
        self.call_count = 0

    async def invoke(self, input: str) -> str:
        self.call_count += 1
        raise ToolError(
            error_type=self.error_type,
            message="Always fails",
            tool_name=self.name,
            input=input,
            recoverable=self.error_type
            in [
                ToolErrorType.NETWORK,
                ToolErrorType.TIMEOUT,
                ToolErrorType.TRANSIENT,
            ],
        )


class SlowTool(Tool[str, str]):
    """Tool that takes a long time."""

    def __init__(self, delay_ms: int):
        self.meta = ToolMeta.minimal(
            name="slow_tool",
            description="Takes time to complete",
            input_schema=str,
            output_schema=str,
        )
        self.delay_ms = delay_ms

    async def invoke(self, input: str) -> str:
        await asyncio.sleep(self.delay_ms / 1000)
        return f"Completed after {self.delay_ms}ms"


# --- ToolExecutor Tests ---


@pytest.mark.asyncio
async def test_tool_executor_success():
    """Test ToolExecutor with successful tool."""
    tool = SuccessTool()
    executor = ToolExecutor(tool)

    result = await executor.execute("test input")

    assert result.is_ok()
    assert result.value == "Success: test input"
    assert tool.call_count == 1


@pytest.mark.asyncio
async def test_tool_executor_failure():
    """Test ToolExecutor with failing tool."""
    tool = AlwaysFailingTool(ToolErrorType.NETWORK)
    executor = ToolExecutor(tool)

    result = await executor.execute("test input")

    assert result.is_err()
    assert isinstance(result.error, ToolError)
    assert result.error.error_type == ToolErrorType.NETWORK
    assert tool.call_count == 1


@pytest.mark.asyncio
async def test_tool_executor_timeout():
    """Test ToolExecutor with timeout."""
    tool = SlowTool(delay_ms=500)
    executor = ToolExecutor(tool)

    result = await executor.execute_with_timeout("test", timeout_ms=100)

    assert result.is_err()
    assert result.error.error_type == ToolErrorType.TIMEOUT
    assert "timed out" in result.error.message.lower()


@pytest.mark.asyncio
async def test_tool_executor_timeout_success():
    """Test ToolExecutor timeout with fast enough tool."""
    tool = SlowTool(delay_ms=50)
    executor = ToolExecutor(tool)

    result = await executor.execute_with_timeout("test", timeout_ms=200)

    assert result.is_ok()
    assert "Completed" in result.value


# --- CircuitBreakerTool Tests ---


@pytest.mark.asyncio
async def test_circuit_breaker_closed_state():
    """Test circuit breaker in CLOSED state (normal operation)."""
    tool = SuccessTool()
    config = CircuitBreakerConfig(failure_threshold=3)
    circuit = CircuitBreakerTool(tool, config)

    # Execute successfully
    result = await circuit.invoke("test")
    assert result == "Success: test"
    assert circuit.state.state == CircuitState.CLOSED
    assert circuit.state.failure_count == 0


@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_failures():
    """Test circuit breaker opens after threshold failures."""
    tool = AlwaysFailingTool(ToolErrorType.NETWORK)
    config = CircuitBreakerConfig(failure_threshold=3)
    circuit = CircuitBreakerTool(tool, config)

    # Fail 3 times to open circuit
    for i in range(3):
        with pytest.raises(ToolError):
            await circuit.invoke("test")

    assert circuit.state.state == CircuitState.OPEN
    assert circuit.state.failure_count == 3

    # Circuit should reject requests immediately
    with pytest.raises(CircuitBreakerError) as exc_info:
        await circuit.invoke("test")

    assert "Circuit breaker OPEN" in str(exc_info.value)
    assert tool.call_count == 3  # No additional calls after opening


@pytest.mark.asyncio
@pytest.mark.slow
async def test_circuit_breaker_half_open_after_timeout():
    """Test circuit breaker transitions to HALF_OPEN after timeout."""
    tool = FailingTool(fail_count=3, error_type=ToolErrorType.NETWORK)
    config = CircuitBreakerConfig(failure_threshold=3, timeout_seconds=1)
    circuit = CircuitBreakerTool(tool, config)

    # Open circuit
    for i in range(3):
        with pytest.raises(ToolError):
            await circuit.invoke("test")

    assert circuit.state.state == CircuitState.OPEN

    # Wait for timeout
    await asyncio.sleep(1.1)

    # Next request should be allowed (HALF_OPEN)
    result = await circuit.invoke("test")
    assert "Success" in result
    assert circuit.state.state == CircuitState.HALF_OPEN


@pytest.mark.asyncio
@pytest.mark.slow
async def test_circuit_breaker_closes_after_successes():
    """Test circuit breaker closes after success threshold in HALF_OPEN."""
    tool = FailingTool(fail_count=3, error_type=ToolErrorType.NETWORK)
    config = CircuitBreakerConfig(
        failure_threshold=3, success_threshold=2, timeout_seconds=1
    )
    circuit = CircuitBreakerTool(tool, config)

    # Open circuit
    for i in range(3):
        with pytest.raises(ToolError):
            await circuit.invoke("test")

    assert circuit.state.state == CircuitState.OPEN

    # Wait for timeout
    await asyncio.sleep(1.1)

    # Succeed twice to close circuit
    await circuit.invoke("test")
    assert circuit.state.state == CircuitState.HALF_OPEN

    await circuit.invoke("test")
    assert circuit.state.state == CircuitState.CLOSED
    assert circuit.state.failure_count == 0


@pytest.mark.asyncio
async def test_circuit_breaker_ignores_non_monitored_errors():
    """Test circuit breaker doesn't trip on non-monitored errors."""
    tool = AlwaysFailingTool(ToolErrorType.VALIDATION)
    config = CircuitBreakerConfig(
        failure_threshold=3,
        monitored_errors=[ToolErrorType.NETWORK, ToolErrorType.TIMEOUT],
    )
    circuit = CircuitBreakerTool(tool, config)

    # Fail 5 times with VALIDATION error
    for i in range(5):
        with pytest.raises(ToolError):
            await circuit.invoke("test")

    # Circuit should still be CLOSED (VALIDATION not monitored)
    assert circuit.state.state == CircuitState.CLOSED
    assert circuit.state.failure_count == 0


@pytest.mark.asyncio
async def test_circuit_breaker_manual_reset():
    """Test manual circuit breaker reset."""
    tool = AlwaysFailingTool(ToolErrorType.NETWORK)
    config = CircuitBreakerConfig(failure_threshold=3)
    circuit = CircuitBreakerTool(tool, config)

    # Open circuit
    for i in range(3):
        with pytest.raises(ToolError):
            await circuit.invoke("test")

    assert circuit.state.state == CircuitState.OPEN

    # Manual reset
    circuit.reset()

    assert circuit.state.state == CircuitState.CLOSED
    assert circuit.state.failure_count == 0


# --- RetryExecutor Tests ---


@pytest.mark.asyncio
async def test_retry_executor_success_first_try():
    """Test RetryExecutor with immediate success."""
    tool = SuccessTool()
    config = RetryConfig(max_attempts=3)
    executor = RetryExecutor(tool, config)

    result = await executor.execute("test")

    assert result.is_ok()
    assert result.value == "Success: test"
    assert tool.call_count == 1  # No retries needed


@pytest.mark.asyncio
async def test_retry_executor_eventual_success():
    """Test RetryExecutor retries until success."""
    tool = FailingTool(fail_count=2, error_type=ToolErrorType.NETWORK)
    config = RetryConfig(max_attempts=5, initial_delay_ms=10)
    executor = RetryExecutor(tool, config)

    start = datetime.now()
    result = await executor.execute("test")
    elapsed_ms = (datetime.now() - start).total_seconds() * 1000

    assert result.is_ok()
    assert "Success after 3 attempts" in result.value
    assert tool.call_count == 3  # Failed twice, succeeded on 3rd
    assert elapsed_ms >= 10  # At least some delay happened


@pytest.mark.asyncio
async def test_retry_executor_max_attempts_exceeded():
    """Test RetryExecutor gives up after max attempts."""
    tool = AlwaysFailingTool(ToolErrorType.NETWORK)
    config = RetryConfig(max_attempts=3, initial_delay_ms=10)
    executor = RetryExecutor(tool, config)

    result = await executor.execute("test")

    assert result.is_err()
    assert tool.call_count == 3  # Tried 3 times
    assert result.error.error_type == ToolErrorType.NETWORK


@pytest.mark.asyncio
async def test_retry_executor_no_retry_on_non_recoverable():
    """Test RetryExecutor doesn't retry non-recoverable errors."""
    tool = AlwaysFailingTool(ToolErrorType.VALIDATION)
    config = RetryConfig(max_attempts=5)
    executor = RetryExecutor(tool, config)

    result = await executor.execute("test")

    assert result.is_err()
    assert tool.call_count == 1  # No retries for VALIDATION error
    assert result.error.error_type == ToolErrorType.VALIDATION


@pytest.mark.asyncio
async def test_retry_executor_exponential_backoff():
    """Test RetryExecutor uses exponential backoff."""
    tool = AlwaysFailingTool(ToolErrorType.NETWORK)
    config = RetryConfig(
        max_attempts=4, initial_delay_ms=100, backoff_multiplier=2.0, jitter=False
    )
    executor = RetryExecutor(tool, config)

    start = datetime.now()
    result = await executor.execute("test")
    elapsed_ms = (datetime.now() - start).total_seconds() * 1000

    # Expected delays: 100, 200, 400 = 700ms total (no jitter)
    assert result.is_err()
    assert elapsed_ms >= 600  # Allow some tolerance
    assert elapsed_ms < 1000  # But not too much


@pytest.mark.asyncio
async def test_retry_executor_respects_retry_after():
    """Test RetryExecutor respects retry_after_ms from rate limits."""

    class RateLimitTool(Tool[str, str]):
        def __init__(self):
            self.meta = ToolMeta.minimal(
                name="rate_limit", description="", input_schema=str, output_schema=str
            )

        async def invoke(self, input: str) -> str:
            raise ToolError(
                error_type=ToolErrorType.RATE_LIMIT,
                message="Rate limited",
                tool_name=self.name,
                input=input,
                recoverable=True,
                retry_after_ms=500,  # Server says wait 500ms
            )

    tool = RateLimitTool()
    config = RetryConfig(max_attempts=2, initial_delay_ms=100)
    executor = RetryExecutor(tool, config)

    start = datetime.now()
    result = await executor.execute("test")
    elapsed_ms = (datetime.now() - start).total_seconds() * 1000

    assert result.is_err()
    assert elapsed_ms >= 500  # Should respect retry_after_ms=500


# --- RobustToolExecutor Tests ---


@pytest.mark.asyncio
async def test_robust_executor_success():
    """Test RobustToolExecutor with successful tool."""
    tool = SuccessTool()
    executor = RobustToolExecutor(tool)

    result = await executor.execute("test")

    assert result.is_ok()
    assert "Success" in result.value


@pytest.mark.asyncio
async def test_robust_executor_retry_then_success():
    """Test RobustToolExecutor retries transient failures."""
    tool = FailingTool(fail_count=2, error_type=ToolErrorType.NETWORK)
    executor = RobustToolExecutor(
        tool,
        circuit_config=CircuitBreakerConfig(failure_threshold=5),
        retry_config=RetryConfig(max_attempts=5, initial_delay_ms=10),
    )

    result = await executor.execute("test")

    assert result.is_ok()
    assert "Success" in result.value


@pytest.mark.asyncio
async def test_robust_executor_circuit_breaker_opens():
    """Test RobustToolExecutor opens circuit after repeated failures."""
    tool = AlwaysFailingTool(ToolErrorType.NETWORK)
    executor = RobustToolExecutor(
        tool,
        circuit_config=CircuitBreakerConfig(failure_threshold=5),
        retry_config=RetryConfig(max_attempts=3, initial_delay_ms=10),
    )

    # First execution: retries 3 times (3 failures)
    result1 = await executor.execute("test1")
    assert result1.is_err()
    assert tool.call_count == 3

    # Second execution: retries 3 times (6 failures total), opens circuit on 5th
    result2 = await executor.execute("test2")
    assert result2.is_err()

    # Check circuit state - should be OPEN after 5 failures
    state = executor.get_circuit_state()
    assert state.state == CircuitState.OPEN

    # Third execution: circuit open, immediate rejection
    call_count_before = tool.call_count
    result3 = await executor.execute("test3")
    assert result3.is_err()
    # No additional calls should be made (circuit is open)
    assert tool.call_count == call_count_before


@pytest.mark.asyncio
async def test_robust_executor_manual_reset():
    """Test RobustToolExecutor manual circuit reset."""
    tool = AlwaysFailingTool(ToolErrorType.NETWORK)
    executor = RobustToolExecutor(
        tool,
        circuit_config=CircuitBreakerConfig(failure_threshold=1),
        retry_config=RetryConfig(max_attempts=2, initial_delay_ms=10),
    )

    # Open circuit
    result1 = await executor.execute("test")
    assert result1.is_err()

    state = executor.get_circuit_state()
    assert state.state == CircuitState.OPEN

    # Reset circuit
    executor.reset_circuit()

    state = executor.get_circuit_state()
    assert state.state == CircuitState.CLOSED


# --- Integration Tests ---


@pytest.mark.asyncio
async def test_integration_full_stack():
    """Test full integration of executor components."""
    # Tool that fails 3 times, then succeeds
    tool = FailingTool(fail_count=3, error_type=ToolErrorType.NETWORK)

    executor = RobustToolExecutor(
        tool,
        circuit_config=CircuitBreakerConfig(failure_threshold=5),
        retry_config=RetryConfig(max_attempts=5, initial_delay_ms=10),
    )

    result = await executor.execute("test")

    # Should eventually succeed via retry
    assert result.is_ok()
    assert "Success after 4 attempts" in result.value

    # Circuit should still be CLOSED
    assert executor.get_circuit_state().state == CircuitState.CLOSED


@pytest.mark.asyncio
async def test_integration_circuit_prevents_retry_spam():
    """Test circuit breaker prevents excessive retry attempts."""
    tool = AlwaysFailingTool(ToolErrorType.NETWORK)

    executor = RobustToolExecutor(
        tool,
        circuit_config=CircuitBreakerConfig(failure_threshold=2),
        retry_config=RetryConfig(max_attempts=3, initial_delay_ms=10),
    )

    # Execute twice to open circuit
    await executor.execute("test1")
    await executor.execute("test2")

    assert executor.get_circuit_state().state == CircuitState.OPEN

    # Further executions should be blocked immediately
    call_count_before = tool.call_count
    result = await executor.execute("test3")
    call_count_after = tool.call_count

    assert result.is_err()
    assert call_count_after == call_count_before  # No new calls


# --- Run tests ---

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
