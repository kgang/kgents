"""
Base Runtime - Core abstractions for LLM-backed agent execution.

An LLMAgent wraps the bootstrap Agent with an LLM execution strategy.
The runtime handles the actual API calls and response parsing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar, Optional
import json

from bootstrap import Agent

A = TypeVar("A")
B = TypeVar("B")


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

    @property
    def total_tokens(self) -> int:
        return self.usage.get("total_tokens", 0)


class LLMAgent(Agent[A, B], ABC):
    """
    Base class for LLM-backed agents.

    Extends the bootstrap Agent interface with LLM-specific methods:
    - build_prompt: Convert input to LLM prompt
    - parse_response: Extract output from LLM response

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


class Runtime(ABC):
    """
    Base runtime for executing LLM agents.

    Subclasses implement the actual API calls for different providers.
    """

    @abstractmethod
    async def execute(
        self,
        agent: LLMAgent[A, B],
        input: A
    ) -> AgentResult[B]:
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


def json_response_parser(response: str) -> dict[str, Any]:
    """Standard JSON response parser with markdown code block handling."""
    text = response.strip()

    # Handle markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (```json and ```)
        lines = [l for l in lines[1:] if not l.startswith("```")]
        text = "\n".join(lines)

    return json.loads(text)
