"""
Chat Flow: Streaming conversation modality.

Implements turn-based conversational interaction with context management.

See: spec/f-gents/chat.md
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, AsyncIterator, Literal

from agents.f.config import ChatConfig, FlowConfig
from agents.f.flow import Flow, FlowAgent, FlowEvent
from agents.f.modalities.context import Message, SlidingContext, SummarizingContext
from agents.f.state import FlowState

if TYPE_CHECKING:
    from agents.f.flow import AgentProtocol


@dataclass
class Turn:
    """
    A single conversation turn.

    Captures one complete message/response cycle with metadata.
    """

    turn_number: int
    user_message: Message
    assistant_response: Message
    started_at: datetime
    completed_at: datetime
    tokens_in: int
    tokens_out: int
    context_size_before: int
    context_size_after: int

    @property
    def duration(self) -> float:
        """Get turn duration in seconds."""
        return (self.completed_at - self.started_at).total_seconds()

    @property
    def total_tokens(self) -> int:
        """Get total tokens for this turn."""
        return self.tokens_in + self.tokens_out


class ChatFlow:
    """
    Chat flow implementation wrapping FlowAgent.

    Provides chat-specific behavior:
    - Turn protocol
    - Context window management
    - Streaming output
    - System prompt handling
    - Interruption handling
    """

    def __init__(
        self,
        agent: AgentProtocol,
        config: ChatConfig | None = None,
    ):
        """
        Initialize chat flow.

        Args:
            agent: The underlying agent to wrap
            config: Chat-specific configuration
        """
        if config is None:
            config = ChatConfig()

        self.config = config
        self.flow_config = config.to_flow_config()

        # Create the flow agent
        self.flow_agent = Flow.lift(agent, self.flow_config)

        # Initialize context based on strategy
        if config.context_strategy == "sliding":
            self.context = SlidingContext(config.context_window)
        elif config.context_strategy == "summarize":
            self.context = SummarizingContext(
                window_size=config.context_window,
                threshold=config.summarization_threshold,
            )
        else:  # forget
            self.context = SlidingContext(config.context_window)

        # Turn tracking
        self.turns: list[Turn] = []
        self._current_turn: int = 0
        self._partial_response: str = ""
        self._pending_messages: list[Message] = []
        self._streaming: bool = False

        # System prompt handling
        if config.system_prompt:
            system_msg = Message(
                role="system",
                content=config.system_prompt,
            )
            self.context.add(system_msg)

    @property
    def name(self) -> str:
        """Get chat flow name."""
        return f"ChatFlow({self.flow_agent.inner.name})"

    @property
    def state(self) -> FlowState:
        """Get current flow state."""
        return self.flow_agent.state

    @property
    def turn_count(self) -> int:
        """Get number of completed turns."""
        return len(self.turns)

    async def send_message(self, user_message: str) -> str:
        """
        Send a message and get complete response.

        Args:
            user_message: User's message

        Returns:
            Complete assistant response

        Raises:
            RuntimeError: If max turns exceeded or turn timeout
        """
        # Check max turns
        if self.config.max_turns and self.turn_count >= self.config.max_turns:
            raise RuntimeError(f"Max turns ({self.config.max_turns}) exceeded")

        # Handle interruption
        if self._streaming:
            await self._handle_interruption(Message(role="user", content=user_message))

        # Start turn
        started_at = datetime.now()
        self._current_turn += 1

        message = Message(role="user", content=user_message)
        context_before = self._get_context_size()

        # Add to context
        if isinstance(self.context, SummarizingContext):
            await self.context.add_async(message)
        else:
            self.context.add(message)

        # Generate response with timeout
        try:
            response_text = await asyncio.wait_for(
                self._generate_response(),
                timeout=self.config.turn_timeout,
            )
        except TimeoutError:
            response_text = "[Response truncated due to timeout]"

        # Create response message
        response = Message(role="assistant", content=response_text)

        # Add to context
        if isinstance(self.context, SummarizingContext):
            await self.context.add_async(response)
        else:
            self.context.add(response)

        completed_at = datetime.now()
        context_after = self._get_context_size()

        # Record turn
        turn = Turn(
            turn_number=self._current_turn,
            user_message=message,
            assistant_response=response,
            started_at=started_at,
            completed_at=completed_at,
            tokens_in=message.tokens,
            tokens_out=response.tokens,
            context_size_before=context_before,
            context_size_after=context_after,
        )
        self.turns.append(turn)

        return response_text

    async def stream_response(
        self,
        user_message: str,
    ) -> AsyncIterator[str]:
        """
        Stream response tokens as they're generated.

        Args:
            user_message: User's message

        Yields:
            Individual tokens or chunks

        Raises:
            RuntimeError: If max turns exceeded or turn timeout
        """
        # Check max turns
        if self.config.max_turns and self.turn_count >= self.config.max_turns:
            raise RuntimeError(f"Max turns ({self.config.max_turns}) exceeded")

        # Start turn
        started_at = datetime.now()
        self._current_turn += 1
        self._streaming = True

        message = Message(role="user", content=user_message)
        context_before = self._get_context_size()

        # Add to context
        if isinstance(self.context, SummarizingContext):
            await self.context.add_async(message)
        else:
            self.context.add(message)

        # Stream response with timeout
        self._partial_response = ""
        try:
            async with asyncio.timeout(self.config.turn_timeout):
                async for token in self._stream_tokens():
                    yield token
                    self._partial_response += token
        except TimeoutError:
            timeout_msg = "[Response truncated due to timeout]"
            yield timeout_msg
            self._partial_response += timeout_msg

        self._streaming = False

        # Create response message
        response = Message(role="assistant", content=self._partial_response)

        # Add to context
        if isinstance(self.context, SummarizingContext):
            await self.context.add_async(response)
        else:
            self.context.add(response)

        completed_at = datetime.now()
        context_after = self._get_context_size()

        # Record turn
        turn = Turn(
            turn_number=self._current_turn,
            user_message=message,
            assistant_response=response,
            started_at=started_at,
            completed_at=completed_at,
            tokens_in=message.tokens,
            tokens_out=response.tokens,
            context_size_before=context_before,
            context_size_after=context_after,
        )
        self.turns.append(turn)

        # Clear partial response
        self._partial_response = ""

    async def _generate_response(self) -> str:
        """
        Generate complete response from agent.

        Returns:
            Complete response text
        """
        # Render context as input
        messages = self.context.render()
        context_str = self._messages_to_string(messages)

        # Invoke agent
        result = await self.flow_agent.invoke(context_str)

        return str(result)

    async def _stream_tokens(self) -> AsyncIterator[str]:
        """
        Stream response tokens from agent.

        This is a simplified implementation. For real token-level streaming,
        integrate with LLM streaming APIs.

        Yields:
            Token chunks
        """
        # Render context as input
        messages = self.context.render()
        context_str = self._messages_to_string(messages)

        # For now, simulate streaming by invoking and yielding
        # In production, this should use the LLM's streaming API
        result = await self.flow_agent.invoke(context_str)
        response_text = str(result)

        # Simulate token streaming (chunk by words)
        words = response_text.split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.01)  # Simulate streaming delay

    def _messages_to_string(self, messages: list[Message]) -> str:
        """
        Convert messages to string format for agent.

        Args:
            messages: List of messages

        Returns:
            Formatted string
        """
        parts = []
        for msg in messages:
            if msg.role == "system":
                parts.append(f"[SYSTEM]\n{msg.content}\n")
            elif msg.role == "user":
                parts.append(f"[USER]\n{msg.content}\n")
            elif msg.role == "assistant":
                parts.append(f"[ASSISTANT]\n{msg.content}\n")

        return "\n".join(parts)

    def _get_context_size(self) -> int:
        """Get current context size in tokens."""
        if isinstance(self.context, SlidingContext):
            return self.context.token_count
        elif isinstance(self.context, SummarizingContext):
            return self.context._count_tokens()
        return 0

    async def _handle_interruption(self, new_message: Message) -> None:
        """
        Handle user interruption during streaming.

        Args:
            new_message: The interrupting message
        """
        match self.config.interruption_strategy:
            case "complete":
                # Queue the message for after current response completes
                self._pending_messages.append(new_message)
            case "abort":
                # Cancel current streaming (set flag)
                self._streaming = False
                # Clear partial response
                self._partial_response = ""
            case "merge":
                # Add as perturbation to flow agent
                context_str = f"[INTERRUPTION] {new_message.content}"
                await self.flow_agent.invoke(context_str)

    def get_history(self) -> list[Turn]:
        """
        Get conversation history.

        Returns:
            List of completed turns
        """
        return self.turns.copy()

    def get_metrics(self) -> dict:
        """
        Get conversation metrics.

        Returns:
            Dictionary of metrics
        """
        if not self.turns:
            return {
                "turns_completed": 0,
                "tokens_in": 0,
                "tokens_out": 0,
                "average_turn_latency": 0.0,
                "context_utilization": 0.0,
            }

        total_tokens_in = sum(t.tokens_in for t in self.turns)
        total_tokens_out = sum(t.tokens_out for t in self.turns)
        total_latency = sum(t.duration for t in self.turns)
        avg_latency = total_latency / len(self.turns)

        context_size = self._get_context_size()
        utilization = context_size / self.config.context_window

        return {
            "turns_completed": len(self.turns),
            "tokens_in": total_tokens_in,
            "tokens_out": total_tokens_out,
            "average_turn_latency": avg_latency,
            "context_utilization": utilization,
        }

    def reset(self) -> None:
        """Reset the chat flow."""
        self.turns.clear()
        self._current_turn = 0
        self._partial_response = ""
        self._pending_messages.clear()
        self._streaming = False
        self.context.clear()

        # Re-add system prompt if configured
        if self.config.system_prompt:
            system_msg = Message(
                role="system",
                content=self.config.system_prompt,
            )
            self.context.add(system_msg)

        # Reset flow agent
        self.flow_agent.reset()


__all__ = [
    "Turn",
    "ChatFlow",
]
