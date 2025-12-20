"""
A2A Protocol: Agent-to-Agent messaging via SynergyBus.

CLI v7 Phase 6: Agent Swarms

Agents communicate without human intermediation.
This is the "autonomous collaborators" pattern from Microsoft A2A.

Key insight: A2A messages ARE synergy events. We don't need
a separate bus--we need a typed event shape for agent messages
that flows through the existing WitnessSynergyBus.

Message Types:
- REQUEST: Ask another agent to do something
- RESPONSE: Reply to a request
- HANDOFF: Transfer context and responsibility
- NOTIFY: Broadcast information (no response expected)
- HEARTBEAT: Presence signal

Usage:
    channel = A2AChannel("my-agent-id")

    # Send a message
    await channel.send(message)

    # Request/response with timeout
    response = await channel.request("other-agent", {"action": "do_thing"})

    # Hand off to another agent
    await channel.handoff("successor-agent", context, conversation)

    # Subscribe to messages
    async for message in channel.subscribe():
        if message.message_type == A2AMessageType.REQUEST:
            await handle_request(message)

Industry Innovation:
- Microsoft A2A (Agent-to-Agent) protocol
- Multi-agent coordination patterns

Constitution Alignment:
- S6 (Heterarchical): "Agents exist in flux, not fixed hierarchy"
  - Agents can request help from any other agent
  - No fixed boss/worker relationships
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, AsyncIterator, Callable
from uuid import uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# A2A Message Types
# =============================================================================


class A2AMessageType(Enum):
    """Types of agent-to-agent messages."""

    REQUEST = auto()      # Ask another agent to do something
    RESPONSE = auto()     # Reply to a request
    HANDOFF = auto()      # Transfer context and responsibility
    NOTIFY = auto()       # Broadcast information (no response expected)
    HEARTBEAT = auto()    # Presence signal


# =============================================================================
# A2A Message
# =============================================================================


@dataclass
class A2AMessage:
    """
    Message between agents.

    Flows through WitnessSynergyBus as a typed event.

    Fields:
        from_agent: Source agent ID
        to_agent: Target agent ID ("*" for broadcast)
        message_type: Type of message (REQUEST, RESPONSE, etc.)
        payload: Message content (action, data, etc.)
        correlation_id: Links request/response pairs
        timestamp: When message was created
        conversation_context: For handoffs, includes conversation history
    """

    from_agent: str
    to_agent: str  # "*" for broadcast
    message_type: A2AMessageType
    payload: dict[str, Any]
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    # Optional: conversation context for handoffs
    conversation_context: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize for transmission."""
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.name,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "conversation_context": self.conversation_context,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "A2AMessage":
        """Deserialize from transmission."""
        return cls(
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            message_type=A2AMessageType[data["message_type"]],
            payload=data["payload"],
            correlation_id=data["correlation_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            conversation_context=data.get("conversation_context"),
        )

    def create_response(self, payload: dict[str, Any]) -> "A2AMessage":
        """Create a response to this message."""
        return A2AMessage(
            from_agent=self.to_agent,  # Swap sender/receiver
            to_agent=self.from_agent,
            message_type=A2AMessageType.RESPONSE,
            payload=payload,
            correlation_id=self.correlation_id,  # Same correlation
        )


# =============================================================================
# A2A Topics (for WitnessSynergyBus)
# =============================================================================


class A2ATopics:
    """Topic namespace for A2A events on WitnessSynergyBus."""

    # Message type topics
    REQUEST = "a2a.request"
    RESPONSE = "a2a.response"
    HANDOFF = "a2a.handoff"
    NOTIFY = "a2a.notify"
    HEARTBEAT = "a2a.heartbeat"

    # Wildcards
    ALL = "a2a.*"

    @classmethod
    def for_type(cls, message_type: A2AMessageType) -> str:
        """Get topic for message type."""
        return {
            A2AMessageType.REQUEST: cls.REQUEST,
            A2AMessageType.RESPONSE: cls.RESPONSE,
            A2AMessageType.HANDOFF: cls.HANDOFF,
            A2AMessageType.NOTIFY: cls.NOTIFY,
            A2AMessageType.HEARTBEAT: cls.HEARTBEAT,
        }[message_type]


# =============================================================================
# A2A Channel
# =============================================================================


class A2AChannel:
    """
    Agent-to-agent communication channel.

    Wraps WitnessSynergyBus with agent-specific semantics.

    Features:
    - Non-blocking send
    - Request/response with correlation and timeout
    - Handoff with context transfer
    - Filtered subscription (only messages for this agent)
    """

    def __init__(self, agent_id: str):
        """
        Create a channel for an agent.

        Args:
            agent_id: This agent's identifier
        """
        self.agent_id = agent_id
        self._pending_responses: dict[str, asyncio.Future[A2AMessage]] = {}
        self._message_queue: asyncio.Queue[A2AMessage] = asyncio.Queue(maxsize=100)
        self._subscription_active = False
        self._unsub_func: Callable[[], None] | None = None

    async def send(self, message: A2AMessage) -> None:
        """
        Send a message to another agent.

        The message flows through WitnessSynergyBus.
        """
        from services.witness.bus import get_synergy_bus

        bus = get_synergy_bus()
        topic = A2ATopics.for_type(message.message_type)

        await bus.publish(topic, message.to_dict())

        logger.debug(
            f"A2A {message.message_type.name}: "
            f"{message.from_agent} -> {message.to_agent}"
        )

    async def request(
        self,
        to_agent: str,
        payload: dict[str, Any],
        timeout: float = 30.0,
    ) -> A2AMessage:
        """
        Request/response pattern with timeout.

        Sends REQUEST, waits for RESPONSE with matching correlation_id.

        Args:
            to_agent: Target agent ID
            payload: Request payload
            timeout: Seconds to wait for response

        Returns:
            The response message

        Raises:
            asyncio.TimeoutError: If no response within timeout
        """
        correlation_id = str(uuid4())
        message = A2AMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=A2AMessageType.REQUEST,
            payload=payload,
            correlation_id=correlation_id,
        )

        # Create future for response
        loop = asyncio.get_running_loop()
        future: asyncio.Future[A2AMessage] = loop.create_future()
        self._pending_responses[correlation_id] = future

        try:
            await self.send(message)
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            self._pending_responses.pop(correlation_id, None)

    async def respond(self, request: A2AMessage, payload: dict[str, Any]) -> None:
        """
        Respond to a request.

        Creates and sends a RESPONSE with matching correlation_id.
        """
        response = request.create_response(payload)
        await self.send(response)

    async def handoff(
        self,
        to_agent: str,
        context: dict[str, Any],
        conversation: list[dict[str, Any]] | None = None,
    ) -> None:
        """
        Hand off work to another agent with full context.

        The receiving agent becomes responsible for the task.
        The handing-off agent typically exits after this.

        Args:
            to_agent: Target agent ID
            context: Task context (current state, goals, etc.)
            conversation: Optional conversation history for continuity
        """
        message = A2AMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=A2AMessageType.HANDOFF,
            payload=context,
            conversation_context=conversation,
        )
        await self.send(message)
        logger.info(f"Handoff: {self.agent_id} -> {to_agent}")

    async def notify(self, to_agent: str, payload: dict[str, Any]) -> None:
        """
        Send a notification (no response expected).

        Use for broadcasting information to other agents.
        """
        message = A2AMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=A2AMessageType.NOTIFY,
            payload=payload,
        )
        await self.send(message)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        """
        Broadcast to all agents.

        Uses "*" as the to_agent, which all agents should match.
        """
        await self.notify("*", payload)

    async def heartbeat(self) -> None:
        """Send a heartbeat signal."""
        message = A2AMessage(
            from_agent=self.agent_id,
            to_agent="*",  # Broadcast
            message_type=A2AMessageType.HEARTBEAT,
            payload={"status": "alive", "timestamp": datetime.now().isoformat()},
        )
        await self.send(message)

    def start_subscription(self) -> None:
        """
        Start subscribing to A2A messages for this agent.

        Messages are queued and can be read via subscribe().
        """
        if self._subscription_active:
            return

        from services.witness.bus import get_synergy_bus

        bus = get_synergy_bus()

        async def handler(topic: str, event: Any) -> None:
            """Handle incoming A2A messages."""
            if not isinstance(event, dict):
                return

            try:
                message = A2AMessage.from_dict(event)
            except (KeyError, ValueError) as e:
                logger.warning(f"Invalid A2A message: {e}")
                return

            # Check if message is for us
            if message.to_agent not in (self.agent_id, "*"):
                return

            # Handle response correlation
            if message.message_type == A2AMessageType.RESPONSE:
                future = self._pending_responses.get(message.correlation_id)
                if future and not future.done():
                    future.set_result(message)
                    return

            # Queue for subscription
            try:
                self._message_queue.put_nowait(message)
            except asyncio.QueueFull:
                logger.warning(f"A2A message queue full for {self.agent_id}")

        self._unsub_func = bus.subscribe(A2ATopics.ALL, handler)
        self._subscription_active = True
        logger.debug(f"A2A subscription started for {self.agent_id}")

    def stop_subscription(self) -> None:
        """Stop subscribing to A2A messages."""
        if self._unsub_func:
            self._unsub_func()
            self._unsub_func = None
        self._subscription_active = False
        logger.debug(f"A2A subscription stopped for {self.agent_id}")

    async def subscribe(self) -> AsyncIterator[A2AMessage]:
        """
        Subscribe to messages addressed to this agent.

        Yields A2AMessage events as they arrive.
        Automatically starts subscription if not already active.

        Usage:
            async for message in channel.subscribe():
                if message.message_type == A2AMessageType.REQUEST:
                    await handle_request(message)
        """
        self.start_subscription()

        try:
            while True:
                message = await self._message_queue.get()
                yield message
        finally:
            self.stop_subscription()

    async def receive_one(self, timeout: float = 30.0) -> A2AMessage | None:
        """
        Receive a single message with timeout.

        Convenience method for simple request handling.

        Returns:
            The next message, or None if timeout
        """
        self.start_subscription()

        try:
            return await asyncio.wait_for(self._message_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
        finally:
            # Don't stop subscription - caller may want more messages
            pass


# =============================================================================
# A2A Registry (Track Active Channels)
# =============================================================================


class A2ARegistry:
    """
    Registry of active A2A channels.

    Tracks which agents have active channels for discovery.
    """

    _instance: "A2ARegistry | None" = None
    _channels: dict[str, A2AChannel]

    def __new__(cls) -> "A2ARegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._channels = {}
        return cls._instance

    def register(self, channel: A2AChannel) -> None:
        """Register a channel."""
        self._channels[channel.agent_id] = channel

    def unregister(self, agent_id: str) -> None:
        """Unregister a channel."""
        channel = self._channels.pop(agent_id, None)
        if channel:
            channel.stop_subscription()

    def get(self, agent_id: str) -> A2AChannel | None:
        """Get a channel by agent ID."""
        return self._channels.get(agent_id)

    def list_agents(self) -> list[str]:
        """List all registered agent IDs."""
        return list(self._channels.keys())

    def clear(self) -> None:
        """Clear all channels (for testing)."""
        for channel in self._channels.values():
            channel.stop_subscription()
        self._channels.clear()


def get_a2a_registry() -> A2ARegistry:
    """Get the global A2A registry."""
    return A2ARegistry()


def reset_a2a_registry() -> None:
    """Reset the global A2A registry (for testing)."""
    A2ARegistry._instance = None


# =============================================================================
# Module Exports
# =============================================================================


__all__ = [
    # Message types
    "A2AMessageType",
    "A2AMessage",
    # Topics
    "A2ATopics",
    # Channel
    "A2AChannel",
    # Registry
    "A2ARegistry",
    "get_a2a_registry",
    "reset_a2a_registry",
]
