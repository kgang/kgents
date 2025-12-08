"""
FailingAgent: Deliberately failing agent for testing recovery strategies.

This agent simulates various failure modes to test:
- Retry logic
- Fallback strategies
- Error memory
- Recovery pipelines

Philosophy:
- Testing failure paths is as important as testing success paths
- Controlled failures enable validation of recovery mechanisms
- Type errors, syntax errors, import errors all need dedicated testing
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar

from runtime.base import Agent

A = TypeVar("A")
B = TypeVar("B")


class FailureType(Enum):
    """Types of failures the agent can simulate."""
    SYNTAX = "syntax"  # Syntax error (invalid Python)
    TYPE = "type"  # Type checking error (mypy)
    IMPORT = "import"  # Missing import error
    RUNTIME = "runtime"  # Runtime exception
    TIMEOUT = "timeout"  # Simulated timeout
    NETWORK = "network"  # Simulated network error
    INCOMPLETE = "incomplete"  # Incomplete code (TODO/pass)
    GENERIC = "generic"  # Generic failure


@dataclass
class FailingConfig:
    """Configuration for FailingAgent."""
    error_type: FailureType = FailureType.TYPE
    fail_count: int = -1  # -1 = always fail, N = fail N times then succeed
    error_message: str = ""  # Custom error message

    def get_error_message(self, attempt: int) -> str:
        """Generate error message based on failure type."""
        if self.error_message:
            return f"{self.error_message} (attempt {attempt})"

        messages = {
            FailureType.SYNTAX: f"SyntaxError: invalid syntax at line 42 (attempt {attempt})",
            FailureType.TYPE: f"error: Unexpected keyword argument \"runtime\" for \"Agent\" [call-arg] (attempt {attempt})",
            FailureType.IMPORT: f"ImportError: No module named 'nonexistent_module' (attempt {attempt})",
            FailureType.RUNTIME: f"RuntimeError: Simulated runtime failure (attempt {attempt})",
            FailureType.TIMEOUT: f"TimeoutError: Operation timed out after 30s (attempt {attempt})",
            FailureType.NETWORK: f"NetworkError: Connection refused (attempt {attempt})",
            FailureType.INCOMPLETE: f"error: Code contains TODO/pass placeholders (attempt {attempt})",
            FailureType.GENERIC: f"Error: Generic failure (attempt {attempt})",
        }
        return messages.get(self.error_type, f"Unknown error (attempt {attempt})")


class FailingAgent(Agent[A, B], Generic[A, B]):
    """
    Agent that deliberately fails to test recovery strategies.

    Morphism: A → Error (configurable failure type)

    Use cases:
    - Testing retry logic (fail N times, then succeed)
    - Testing fallback strategies (fail consistently)
    - Testing error memory (fail with specific patterns)
    - Validating error handling in pipelines

    Example:
        # Fail 2 times with type errors, then succeed
        agent = FailingAgent[Input, Output](
            FailingConfig(error_type=FailureType.TYPE, fail_count=2)
        )

        # Try 3 times
        for i in range(3):
            try:
                result = await agent.invoke(test_input)
                print(f"Success on attempt {i+1}")
                break
            except Exception as e:
                print(f"Attempt {i+1} failed: {e}")
    """

    def __init__(self, config: FailingConfig):
        """Initialize failing agent with configuration."""
        self.config = config
        self._attempt_count = 0

    @property
    def name(self) -> str:
        """Return agent name."""
        return f"FailingAgent({self.config.error_type.value})"

    async def invoke(self, input: A) -> B:
        """
        Invoke the agent (fails according to configuration).

        Args:
            input: Input of type A (ignored, agent fails regardless)

        Returns:
            Never returns normally - always raises an exception
            (unless fail_count is reached)

        Raises:
            Exception: With error message based on failure type
        """
        self._attempt_count += 1

        # Check if we should succeed this time
        if self.config.fail_count >= 0 and self._attempt_count > self.config.fail_count:
            # Success! Return a mock successful result
            # This is a bit of a hack - in real usage, you'd want to provide
            # a success_output parameter to the config
            return {"status": "success", "message": "Recovered after failures"}  # type: ignore

        # Generate and raise appropriate error
        error_msg = self.config.get_error_message(self._attempt_count)

        # Simulate different error types
        if self.config.error_type == FailureType.SYNTAX:
            raise SyntaxError(error_msg)
        elif self.config.error_type == FailureType.IMPORT:
            raise ImportError(error_msg)
        elif self.config.error_type == FailureType.TIMEOUT:
            raise TimeoutError(error_msg)
        else:
            # Generic exception for type/runtime/network/generic
            raise Exception(error_msg)

    def reset(self) -> None:
        """Reset attempt counter (useful for testing)."""
        self._attempt_count = 0


# Singleton instances for common test scenarios
failing_agent = FailingAgent[Any, Any](FailingConfig())  # Always fails with type error
syntax_failing = FailingAgent[Any, Any](FailingConfig(error_type=FailureType.SYNTAX))
import_failing = FailingAgent[Any, Any](FailingConfig(error_type=FailureType.IMPORT))
