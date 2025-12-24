"""
Base Runtime - Core abstractions for LLM-backed agent execution.

An LLMAgent wraps the bootstrap Agent with an LLM execution strategy.
The runtime handles the actual API calls and response parsing.

Uses bootstrap Fix pattern for retry logic with convergence tracking.

Teaching:
    gotcha: Do NOT import from agents.* at module level here!
            This causes circular imports because agents/ imports runtime/.
            Use TYPE_CHECKING for type hints, lazy imports for runtime use.
            (Evidence: agents/a/creativity.py imports from runtime.base)
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Generic, Optional, TypeVar, Union

# Lazy import to avoid circular dependency
# agents/ imports runtime/, runtime/ must not import agents/ at module level
if TYPE_CHECKING:
    from agents.poly import Agent, Fix, FixConfig, FixResult

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
E = TypeVar("E")  # Error type


# --- Result Type (Either-based error handling) ---
# This provides transparent error handling as per Issue #6


@dataclass
class Success(Generic[B]):
    """Success result containing value."""

    value: B

    def is_success(self) -> bool:
        return True

    def is_error(self) -> bool:
        return False

    def unwrap(self) -> B:
        """Extract the value."""
        return self.value

    def unwrap_or(self, default: B) -> B:
        """Extract value or return default."""
        return self.value


@dataclass
class Error(Generic[E]):
    """Error result containing error information."""

    error: E
    message: str = ""
    recoverable: bool = True  # Whether error is recoverable via retry

    def is_success(self) -> bool:
        return False

    def is_error(self) -> bool:
        return True

    def unwrap(self) -> Any:
        """Raises exception - can't unwrap an error."""
        raise RuntimeError(f"Cannot unwrap Error: {self.message or self.error}")

    def unwrap_or(self, default: B) -> B:
        """Return default value."""
        return default


# Result is Either[Error, Success]
# Following Railway Oriented Programming pattern
Result = Union[Success[B], Error[E]]


def success(value: B) -> Success[B]:
    """Create a Success result."""
    return Success(value)


def error(err: E, message: str = "", recoverable: bool = True) -> Error[E]:
    """Create an Error result."""
    return Error(error=err, message=message, recoverable=recoverable)


def result_from_exception(e: Exception, recoverable: bool = True) -> Error[Exception]:
    """Convert an exception to an Error result."""
    return Error(error=e, message=str(e), recoverable=recoverable)


@dataclass
class AgentContext:
    """
    Context passed to LLM during agent execution.

    Contains the agent's system prompt, conversation history,
    and any grounded facts needed for execution.
    """

    system_prompt: str
    messages: list[dict[str, str]] = field(default_factory=list)
    facts: Optional[dict[str, Any]] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    metadata: Optional[dict[str, Any]] = None  # Arbitrary metadata for agent execution


@dataclass
class AgentResult(Generic[B]):
    """
    Result of LLM agent execution.

    Includes the output, raw response, and any metadata.
    """

    output: B
    raw_response: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    retry_count: int = 0
    success: bool = True  # Whether execution succeeded
    error: Optional[str] = None  # Error message if failed

    @property
    def total_tokens(self) -> int:
        return self.usage.get("total_tokens", 0)


class LLMAgent(ABC, Generic[A, B]):
    """
    Base class for LLM-backed agents.

    Implements the Agent interface (name, invoke, >>) with LLM-specific methods:
    - build_prompt: Convert input to LLM prompt
    - parse_response: Extract output from LLM response

    Note: Does not extend agents.poly.Agent to avoid circular imports.
    Implements the same interface via duck typing.

    Usage:
        class MyAgent(LLMAgent[str, dict]):
            def build_prompt(self, input: str) -> AgentContext:
                return AgentContext(
                    system_prompt="You are a helpful assistant.",
                    messages=[{"role": "user", "content": input}],
                )

            def parse_response(self, response: str) -> dict:
                return json.loads(response)
    """

    @abstractmethod
    def build_prompt(self, input: A) -> AgentContext:
        """Convert input to LLM context."""
        pass

    @abstractmethod
    def parse_response(self, response: str) -> B:
        """Parse LLM response to output type."""
        pass

    async def execute_async(self, input: A, runtime: "Runtime") -> B:
        """
        Async execution of this agent.

        Default implementation calls runtime.execute and extracts output.
        Override for custom async behavior.
        """
        result = await runtime.execute(self, input)
        return result.output

    def then_async(self, g: "LLMAgent[B, C]") -> "AsyncComposedAgent[A, B, C]":
        """
        Async composition: self >> g.

        Returns an agent that executes self, then g on the result.
        Both executions are awaited sequentially.
        """
        return AsyncComposedAgent(self, g)


class AsyncComposedAgent(LLMAgent[A, C], Generic[A, B, C]):
    """
    Composition of two async agents: f >> g.

    Executes f, then g on f's output.
    Preserves the morphism structure with clear A → B → C types.
    """

    def __init__(self, f: LLMAgent[A, B], g: LLMAgent[B, C]):
        self.f = f
        self.g = g

    @property
    def name(self) -> str:
        return f"({self.f.name} >> {self.g.name})"

    async def invoke(self, input: A) -> C:
        """Not implemented - use execute_async with runtime instead."""
        raise NotImplementedError("AsyncComposedAgent requires runtime. Use execute_async.")

    def build_prompt(self, input: A) -> AgentContext:
        """Not used - async execution bypasses this."""
        raise NotImplementedError("AsyncComposedAgent uses execute_async")

    def parse_response(self, response: str) -> C:
        """Not used - async execution bypasses this."""
        raise NotImplementedError("AsyncComposedAgent uses execute_async")

    async def execute_async(self, input: A, runtime: "Runtime") -> C:
        """Execute f, then g sequentially."""
        b = await self.f.execute_async(input, runtime)
        c = await self.g.execute_async(b, runtime)
        return c


async def acompose(*agents: LLMAgent[Any, Any]) -> LLMAgent[Any, Any]:
    """
    Async composition of multiple agents: f >> g >> h.

    Example:
        pipeline = acompose(extract_facts, summarize, format_output)
        result = await pipeline.execute_async(input, runtime)
    """
    if len(agents) == 0:
        raise ValueError("acompose requires at least one agent")
    if len(agents) == 1:
        return agents[0]

    result = agents[0]
    for agent in agents[1:]:
        result = result.then_async(agent)
    return result


async def parallel_execute(
    agents: list[LLMAgent[A, B]], inputs: list[A], runtime: "Runtime"
) -> list[B]:
    """
    Execute multiple agents concurrently on their respective inputs.

    This enables true parallelism for I/O-bound LLM calls.

    Args:
        agents: List of agents to execute
        inputs: Corresponding inputs for each agent
        runtime: Runtime to use for execution

    Returns:
        List of outputs in the same order as inputs

    Example:
        # Process multiple documents concurrently
        results = await parallel_execute(
            [summarize_agent] * len(documents),
            documents,
            runtime
        )
    """
    if len(agents) != len(inputs):
        raise ValueError("agents and inputs must have same length")

    tasks = [agent.execute_async(input_val, runtime) for agent, input_val in zip(agents, inputs)]

    return await asyncio.gather(*tasks)


class TransientError(Exception):
    """Transient error that may succeed on retry (rate limits, timeouts, etc)."""

    pass


class PermanentError(Exception):
    """Permanent error that won't succeed on retry (auth, invalid input, etc)."""

    pass


@dataclass
class RetryState(Generic[B]):
    """State for retry-as-Fix pattern. Tracks value, errors, and attempts."""

    value: Optional[B] = None
    error: Optional[Exception] = None
    attempt: int = 0
    succeeded: bool = False


async def with_retry(
    fn: Callable[[], Awaitable[B]],
    max_attempts: int = 3,
    backoff_base: float = 2.0,
    is_transient: Optional[Callable[[Exception], bool]] = None,
) -> tuple[B, int]:
    """
    Fix pattern for retry logic using bootstrap Fix.

    Executes fn with exponential backoff on transient errors.
    Uses bootstrap Fix for convergence tracking and proper iteration.

    Args:
        fn: Async function to retry
        max_attempts: Maximum number of attempts (default 3)
        backoff_base: Base for exponential backoff in seconds (default 2.0)
        is_transient: Predicate to determine if error is transient (default: check TransientError type)

    Returns:
        Tuple of (result, attempt_count)

    Raises:
        Last exception if all attempts fail

    Example:
        result, attempts = await with_retry(
            lambda: runtime.raw_completion(context),
            max_attempts=5
        )
    """
    if is_transient is None:

        def is_transient(e: BaseException) -> bool:
            return isinstance(e, TransientError)

    async def retry_transform(state: RetryState[B]) -> RetryState[B]:
        """Transform function for Fix: try fn, track result/error."""
        if state.succeeded:
            return state  # Already converged

        # Apply backoff delay (not on first attempt)
        if state.attempt > 0:
            delay = backoff_base ** (state.attempt - 1)
            await asyncio.sleep(delay)

        try:
            result = await fn()
            return RetryState(
                value=result,
                error=None,
                attempt=state.attempt + 1,
                succeeded=True,
            )
        except Exception as e:
            # Permanent error: mark as "converged" to stop iteration
            if not is_transient(e):
                return RetryState(
                    value=None,
                    error=e,
                    attempt=state.attempt + 1,
                    succeeded=True,  # Stop iteration
                )
            # Transient error: continue trying
            return RetryState(
                value=None,
                error=e,
                attempt=state.attempt + 1,
                succeeded=False,
            )

    def has_converged(a: RetryState[B], b: RetryState[B]) -> bool:
        """Converged when succeeded or hit max attempts."""
        return b.succeeded or b.attempt >= max_attempts

    # Lazy import to avoid circular dependency at module level
    from agents.poly import Fix, FixConfig

    config: "FixConfig[RetryState[B]]" = FixConfig(
        max_iterations=max_attempts,
        equality_check=has_converged,
    )

    initial_state: RetryState[B] = RetryState()
    fix_agent: "Fix[RetryState[B]]" = Fix(config)
    fix_result = await fix_agent.invoke((retry_transform, initial_state))

    final_state = fix_result.value

    # Check result
    if final_state.succeeded and final_state.value is not None:
        return (final_state.value, final_state.attempt)
    elif final_state.error is not None:
        raise final_state.error
    else:
        # Should not reach here
        raise RuntimeError(f"Retry exhausted after {final_state.attempt} attempts")


class Runtime(ABC):
    """
    Base runtime for executing LLM agents.

    Subclasses implement the actual API calls for different providers.
    """

    @abstractmethod
    async def execute(self, agent: LLMAgent[A, B], input: A) -> AgentResult[B]:
        """Execute an LLM agent with input and return result."""
        pass

    @abstractmethod
    async def raw_completion(
        self,
        context: AgentContext,
    ) -> tuple[str, dict[str, Any]]:
        """
        Low-level completion call.

        Returns (response_text, metadata).
        """
        pass
