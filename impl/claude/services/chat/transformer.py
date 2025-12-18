"""
Transform functions between Chat and Morpheus types.

Per spec/protocols/chat-morpheus-synergy.md Part II §2.3:
A Transform Functor T connects Chat and Morpheus:
    T : ChatMessage → MorpheusRequest
    T⁻¹ : MorpheusResponse → ChatResponse

This is NOT an adapter. It's a natural transformation between categories.
Key property: preserves structured messages—no string parsing required.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Sequence, cast

if TYPE_CHECKING:
    from services.morpheus.persistence import CompletionResult
    from services.morpheus.types import ChatMessage as MorpheusMessage, ChatRequest

    from .model_selector import MorpheusConfig
    from .session import Message


def to_morpheus_request(
    context: Sequence["Message"],
    user_message: str,
    config: "MorpheusConfig",
    system_prompt: str | None = None,
) -> "ChatRequest":
    """
    Transform chat context to Morpheus request.

    Preserves structured messages—no string parsing.
    This is the forward transform T.

    Args:
        context: Existing conversation messages
        user_message: New message from user
        config: Model configuration (from observer selection)
        system_prompt: Optional system prompt to prepend

    Returns:
        ChatRequest ready for Morpheus gateway
    """
    from services.morpheus.types import ChatMessage as MorpheusMessage, ChatRequest

    messages: list[MorpheusMessage] = []

    # Add system prompt if provided
    if system_prompt:
        messages.append(MorpheusMessage(role="system", content=system_prompt))

    # Transform existing context messages
    for msg in context:
        # Map chat roles to Morpheus roles (type-safe casting)
        role: Literal["system", "user", "assistant"] = (
            msg.role if msg.role in ("system", "user", "assistant") else "user"
        )

        messages.append(MorpheusMessage(role=role, content=msg.content))

    # Add new user message
    messages.append(MorpheusMessage(role="user", content=user_message))

    return ChatRequest(
        model=config.model,
        messages=messages,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def from_morpheus_response(result: "CompletionResult") -> str:
    """
    Extract content from Morpheus result.

    This is the inverse transform T⁻¹.

    Args:
        result: CompletionResult from Morpheus

    Returns:
        Response content string
    """
    if result.response.choices:
        return result.response.choices[0].message.content
    return ""


def extract_usage(result: "CompletionResult") -> tuple[int, int]:
    """
    Extract token usage from Morpheus result.

    Returns:
        Tuple of (tokens_in, tokens_out)
    """
    if result.response.usage:
        return (
            result.response.usage.prompt_tokens,
            result.response.usage.completion_tokens,
        )
    return (0, 0)


def to_streaming_request(
    context: Sequence["Message"],
    user_message: str,
    config: "MorpheusConfig",
    system_prompt: str | None = None,
) -> "ChatRequest":
    """
    Create a streaming request.

    Same as to_morpheus_request but with stream=True.

    Args:
        context: Existing conversation messages
        user_message: New message from user
        config: Model configuration
        system_prompt: Optional system prompt

    Returns:
        ChatRequest with stream=True
    """
    request = to_morpheus_request(context, user_message, config, system_prompt)
    request.stream = True
    return request


__all__ = [
    "to_morpheus_request",
    "from_morpheus_response",
    "extract_usage",
    "to_streaming_request",
]
