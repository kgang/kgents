"""
Message Protocol

Structured messages for agent-to-LLM communication.
"""

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Message:
    """A single message in a conversation"""
    role: Literal["user", "assistant", "system"]
    content: str


@dataclass(frozen=True)
class TokenUsage:
    """Token usage statistics for a completion"""
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class CompletionResult:
    """Result from an LLM completion"""
    content: str
    model: str
    usage: TokenUsage
    cached: bool = False
    finish_reason: str | None = None

    def __repr__(self) -> str:
        cache_str = " (cached)" if self.cached else ""
        return f"<Completion model={self.model} tokens={self.usage.total_tokens}{cache_str}>"


# Convenience constructors
def user(content: str) -> Message:
    """Create a user message"""
    return Message(role="user", content=content)


def assistant(content: str) -> Message:
    """Create an assistant message"""
    return Message(role="assistant", content=content)


def system(content: str) -> Message:
    """Create a system message"""
    return Message(role="system", content=content)
