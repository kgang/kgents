"""
Morpheus Types: OpenAI-compatible request/response schemas.

These types match the OpenAI API schema exactly, enabling standard
SDK usage with base_url override.

Reference: https://platform.openai.com/docs/api-reference/chat
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, Optional


@dataclass
class ChatMessage:
    """A single message in the conversation."""

    role: Literal["system", "user", "assistant"]
    content: str
    name: Optional[str] = None  # Optional name for function calls

    def to_dict(self) -> dict[str, Any]:
        """Convert to OpenAI API format."""
        result: dict[str, Any] = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class ChatRequest:
    """OpenAI-compatible chat completion request."""

    model: str
    messages: list[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    n: int = 1  # Number of completions
    stream: bool = False
    stop: Optional[list[str]] = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    user: Optional[str] = None  # Unique identifier for rate limiting

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChatRequest":
        """Create from dict (e.g., JSON body)."""
        messages = [
            ChatMessage(
                role=m["role"],
                content=m["content"],
                name=m.get("name"),
            )
            for m in data.get("messages", [])
        ]
        return cls(
            model=data["model"],
            messages=messages,
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 4096),
            top_p=data.get("top_p", 1.0),
            n=data.get("n", 1),
            stream=data.get("stream", False),
            stop=data.get("stop"),
            presence_penalty=data.get("presence_penalty", 0.0),
            frequency_penalty=data.get("frequency_penalty", 0.0),
            user=data.get("user"),
        )


@dataclass
class Usage:
    """Token usage statistics."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    def to_dict(self) -> dict[str, int]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass
class ChatChoice:
    """A single completion choice."""

    index: int
    message: ChatMessage
    finish_reason: Literal["stop", "length", "content_filter", "function_call"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "message": self.message.to_dict(),
            "finish_reason": self.finish_reason,
        }


@dataclass
class ChatResponse:
    """OpenAI-compatible chat completion response."""

    id: str
    object: str = "chat.completion"
    created: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    model: str = ""
    choices: list[ChatChoice] = field(default_factory=list)
    usage: Optional[Usage] = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [c.to_dict() for c in self.choices],
        }
        if self.usage:
            result["usage"] = self.usage.to_dict()
        return result

    @classmethod
    def from_text(
        cls,
        text: str,
        model: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> "ChatResponse":
        """Create response from plain text."""
        return cls(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            model=model,
            choices=[
                ChatChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=text),
                    finish_reason="stop",
                )
            ],
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
        )


@dataclass
class MorpheusError:
    """Error response following OpenAI error format."""

    message: str
    type: str  # e.g., "invalid_request_error", "rate_limit_error"
    code: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "error": {
                "message": self.message,
                "type": self.type,
            }
        }
        if self.code:
            result["error"]["code"] = self.code
        return result


@dataclass
class StreamDelta:
    """Delta content in a streaming chunk."""

    role: Optional[str] = None
    content: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.role:
            result["role"] = self.role
        if self.content:
            result["content"] = self.content
        return result


@dataclass
class StreamChoice:
    """A single streaming choice."""

    index: int
    delta: StreamDelta
    finish_reason: Optional[Literal["stop", "length", "content_filter"]] = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "index": self.index,
            "delta": self.delta.to_dict(),
        }
        if self.finish_reason:
            result["finish_reason"] = self.finish_reason
        return result


@dataclass
class StreamChunk:
    """OpenAI-compatible streaming chunk."""

    id: str
    object: str = "chat.completion.chunk"
    created: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    model: str = ""
    choices: list[StreamChoice] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [c.to_dict() for c in self.choices],
        }

    def to_sse(self) -> str:
        """Convert to Server-Sent Events format."""
        import json

        return f"data: {json.dumps(self.to_dict())}\n\n"

    @classmethod
    def from_text(cls, text: str, chunk_id: str, model: str) -> "StreamChunk":
        """Create a content chunk from plain text."""
        return cls(
            id=chunk_id,
            model=model,
            choices=[
                StreamChoice(
                    index=0,
                    delta=StreamDelta(content=text),
                )
            ],
        )

    @classmethod
    def final(cls, chunk_id: str, model: str) -> "StreamChunk":
        """Create a final chunk with finish_reason."""
        return cls(
            id=chunk_id,
            model=model,
            choices=[
                StreamChoice(
                    index=0,
                    delta=StreamDelta(),
                    finish_reason="stop",
                )
            ],
        )


__all__ = [
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ChatChoice",
    "Usage",
    "MorpheusError",
    "StreamChunk",
    "StreamChoice",
    "StreamDelta",
]
