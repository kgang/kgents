"""
AGENTESE Chat Sub-Resolver

Resolves `<node>.chat.*` paths for any @chatty decorated node.

The chat sub-resolver:
1. Creates/retrieves ChatSessions by (node_path, observer)
2. Routes chat affordances (send, stream, history, context, metrics, reset)
3. Manages session lifecycle

Usage:
    # The chat resolver is invoked when parsing paths like:
    # self.soul.chat.send[message="Hello"]
    # world.town.citizen.elara.chat.history

    resolver = ChatResolver()
    node = resolver.resolve("self.soul", observer, "send", message="Hello")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncIterator

from ..affordances import (
    CHAT_AFFORDANCES,
    AspectCategory,
    Effect,
    aspect,
    get_chatty_config,
    is_chatty,
    to_chat_config,
)
from ..chat.factory import ChatSessionFactory
from ..chat.session import ChatSession
from ..node import BaseLogosNode, BasicRendering, Renderable

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


@dataclass
class ChatNode(BaseLogosNode):
    """
    A node that handles chat affordances for a parent node.

    This is a virtual node created when accessing <node>.chat
    for any @chatty decorated node.

    AGENTESE: <node>.chat.*
    """

    _handle: str
    _parent_node: BaseLogosNode | None = None
    _parent_path: str = ""
    _factory: ChatSessionFactory | None = None

    # Cached session for this (node, observer) pair
    _session: ChatSession | None = None

    def __post_init__(self) -> None:
        if self._factory is None:
            self._factory = ChatSessionFactory()

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Chat affordances available to all archetypes."""
        return CHAT_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show chat session status."""
        session = await self._get_or_create_session(observer)

        return BasicRendering(
            summary=f"Chat: {self._parent_path}",
            content=(
                f"Session: {session.session_id}\n"
                f"State: {session.state.value}\n"
                f"Turns: {session.turn_count}\n"
                f"Entropy: {session.entropy:.2f}"
            ),
            metadata={
                "session_id": session.session_id,
                "state": session.state.value,
                "turn_count": session.turn_count,
                "entropy": session.entropy,
                "parent_path": self._parent_path,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle chat-specific aspects."""
        match aspect:
            case "send":
                return await self._send(observer, **kwargs)
            case "stream":
                return await self._stream(observer, **kwargs)
            case "history":
                return await self._get_history(observer, **kwargs)
            case "turn":
                return await self._get_turn(observer, **kwargs)
            case "context":
                return await self._get_context(observer, **kwargs)
            case "metrics":
                return await self._get_metrics(observer, **kwargs)
            case "reset":
                return await self._reset(observer, **kwargs)
            case "fork":
                return await self._fork(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _get_or_create_session(
        self,
        observer: "Umwelt[Any, Any]",
    ) -> ChatSession:
        """Get or create a chat session for this node and observer."""
        if self._session is not None and self._session.is_active:
            return self._session

        # Get chatty config from parent node if available
        config = None
        if self._parent_node is not None and is_chatty(self._parent_node):
            chatty_config = get_chatty_config(self._parent_node)
            if chatty_config:
                config = to_chat_config(chatty_config)

        # Create session via factory
        assert self._factory is not None
        self._session = await self._factory.create_session(
            self._parent_path,
            observer,
            config=config,
        )
        return self._session

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[
            Effect.CALLS("llm"),
            Effect.WRITES("chat_session"),
            Effect.CHARGES("tokens"),
        ],
        help="Send a message and receive a response",
        examples=["self.soul.chat.send[message='Hello']"],
        budget_estimate="medium",
    )
    async def _send(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Send a message and get the complete response.

        Args:
            message: The message to send

        Returns:
            Dict with response and turn info
        """
        message = kwargs.get("message")
        if not message:
            return {"error": "message required"}

        session = await self._get_or_create_session(observer)

        try:
            response = await session.send(message)
            return {
                "response": response,
                "turn": session.turn_count,
                "entropy": session.entropy,
                "session_id": session.session_id,
            }
        except RuntimeError as e:
            return {"error": str(e), "session_id": session.session_id}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[
            Effect.CALLS("llm"),
            Effect.WRITES("chat_session"),
            Effect.CHARGES("tokens"),
        ],
        help="Stream a response as tokens are generated",
        examples=["self.soul.chat.stream[message='Tell me more']"],
        streaming=True,
        budget_estimate="medium",
    )
    async def _stream(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> AsyncIterator[str] | dict[str, Any]:
        """
        Stream response tokens as they're generated.

        Args:
            message: The message to send

        Yields:
            Individual tokens/chunks
        """
        message = kwargs.get("message")
        if not message:
            return {"error": "message required"}

        session = await self._get_or_create_session(observer)

        try:
            # Return the async iterator directly
            return session.stream(message)
        except RuntimeError as e:
            return {"error": str(e), "session_id": session.session_id}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("chat_session")],
        help="Get conversation history",
        examples=["self.soul.chat.history", "self.soul.chat.history[limit=5]"],
    )
    async def _get_history(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get conversation history.

        Args:
            limit: Optional limit on number of turns

        Returns:
            Dict with turn history
        """
        session = await self._get_or_create_session(observer)
        limit = kwargs.get("limit")

        turns = session.get_history(limit=limit)

        return {
            "turns": [t.to_dict() for t in turns],
            "total_turns": session.turn_count,
            "session_id": session.session_id,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("chat_session")],
        help="Get current turn number",
        examples=["self.soul.chat.turn"],
    )
    async def _get_turn(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get current turn number."""
        session = await self._get_or_create_session(observer)
        return {
            "turn": session.turn_count,
            "state": session.state.value,
            "session_id": session.session_id,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("chat_session")],
        help="Get context window status",
        examples=["self.soul.chat.context"],
    )
    async def _get_context(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get context window status.

        Returns:
            Dict with context utilization info
        """
        session = await self._get_or_create_session(observer)

        return {
            "utilization": session.get_context_utilization(),
            "window_size": session.config.context_window,
            "strategy": session.config.context_strategy.value,
            "session_id": session.session_id,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("chat_session")],
        help="Get session metrics (tokens, latency, cost)",
        examples=["self.soul.chat.metrics"],
    )
    async def _get_metrics(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get session metrics."""
        session = await self._get_or_create_session(observer)
        return session.get_metrics()

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("chat_session")],
        help="Reset the chat session",
        examples=["self.soul.chat.reset"],
    )
    async def _reset(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Reset the chat session to initial state."""
        session = await self._get_or_create_session(observer)
        old_id = session.session_id
        session.reset()

        return {
            "status": "reset",
            "old_session_id": old_id,
            "new_turn_count": session.turn_count,
        }

    @aspect(
        category=AspectCategory.GENERATION,
        effects=[Effect.WRITES("chat_session")],
        help="Fork the conversation into a branch",
        examples=["self.soul.chat.fork"],
    )
    async def _fork(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Fork the current session into a branch.

        Creates a new session with the same history.
        """
        # For now, return not implemented
        # Full implementation would require D-gent persistence
        return {
            "status": "not_implemented",
            "note": "Fork requires D-gent persistence (Phase 4)",
        }


@dataclass
class ChatResolver:
    """
    Resolver for <node>.chat.* paths.

    The chat resolver creates ChatNode instances for any @chatty
    decorated node and routes chat affordances.
    """

    # Global ChatSessionFactory (shared across nodes)
    _factory: ChatSessionFactory = field(default_factory=ChatSessionFactory)

    # Cache of ChatNodes by parent path
    _nodes: dict[str, ChatNode] = field(default_factory=dict)

    def resolve(
        self,
        parent_path: str,
        parent_node: BaseLogosNode | None = None,
    ) -> ChatNode:
        """
        Resolve a chat node for a parent path.

        Args:
            parent_path: The parent node's AGENTESE path (e.g., "self.soul")
            parent_node: Optional parent node instance

        Returns:
            ChatNode for handling chat affordances
        """
        # Check cache
        if parent_path in self._nodes:
            return self._nodes[parent_path]

        # Create new ChatNode
        chat_node = ChatNode(
            _handle=f"{parent_path}.chat",
            _parent_node=parent_node,
            _parent_path=parent_path,
            _factory=self._factory,
        )

        # Cache it
        self._nodes[parent_path] = chat_node

        return chat_node

    def get_session(
        self,
        parent_path: str,
        observer: "Umwelt[Any, Any]",
    ) -> ChatSession | None:
        """
        Get an existing session for a node and observer.

        Returns None if no session exists.
        """
        return self._factory.get_session(parent_path, observer)

    def list_sessions(
        self,
        parent_path: str | None = None,
    ) -> list[ChatSession]:
        """List active sessions, optionally filtered by parent path."""
        return self._factory.list_sessions(node_path=parent_path)


# Global chat resolver instance
_chat_resolver: ChatResolver | None = None


def get_chat_resolver() -> ChatResolver:
    """Get the global chat resolver."""
    global _chat_resolver
    if _chat_resolver is None:
        _chat_resolver = ChatResolver()
    return _chat_resolver


def set_chat_resolver(resolver: ChatResolver) -> None:
    """Set the global chat resolver (for testing)."""
    global _chat_resolver
    _chat_resolver = resolver


def create_chat_node(
    parent_path: str,
    parent_node: BaseLogosNode | None = None,
) -> ChatNode:
    """
    Create a chat node for a parent path.

    This is the main entry point for the chat sub-resolver.
    """
    resolver = get_chat_resolver()
    return resolver.resolve(parent_path, parent_node)


__all__ = [
    "ChatNode",
    "ChatResolver",
    "get_chat_resolver",
    "set_chat_resolver",
    "create_chat_node",
]
