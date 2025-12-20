"""
ChatSessionFactory: Factory for creating chat sessions with any AGENTESE node.

The factory handles:
- System prompt generation from node metadata
- Context strategy selection
- Memory integration
- Session ID generation
"""

from __future__ import annotations

import hashlib
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable

logger = logging.getLogger(__name__)

# Per Metaphysical Fullstack (AD-009): Agent prompts belong to the agent
from agents.k.prompts import (
    AGENT_SYSTEM_PROMPT,
    CITIZEN_SYSTEM_PROMPT,
    SOUL_SYSTEM_PROMPT,
)

from .config import (
    AGENT_CHAT_CONFIG,
    CITIZEN_CHAT_CONFIG,
    SOUL_CHAT_CONFIG,
    ChatConfig,
)
from .session import ChatSession

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from services.morpheus.persistence import MorpheusPersistence

    from .composer import ChatMorpheusComposer
    from .model_selector import MorpheusConfig


@dataclass
class SystemPromptContext:
    """Context for system prompt generation."""

    node_path: str
    observer_name: str = "user"
    observer_archetype: str = "guest"

    # Citizen-specific
    citizen_name: str = ""
    citizen_archetype: str = ""
    eigenvectors: str = ""
    recent_memories: str = "No recent memories."

    # Custom context
    extra: dict[str, Any] = field(default_factory=dict)


def generate_session_id(node_path: str, observer_id: str) -> str:
    """
    Generate a unique session ID.

    Format: <node_prefix>_<timestamp>_<random>_<hash>
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Add random component to ensure uniqueness even within same second
    random_part = secrets.token_hex(4)
    hash_input = f"{node_path}:{observer_id}:{timestamp}:{random_part}"
    hash_suffix = hashlib.sha256(hash_input.encode()).hexdigest()[:6]

    # Extract prefix from node path
    prefix = node_path.replace(".", "_")[:16]

    return f"{prefix}_{timestamp}_{random_part}_{hash_suffix}"


class ChatSessionFactory:
    """
    Factory for creating chat sessions with any AGENTESE node.

    The factory handles:
    - System prompt generation from node metadata
    - Context strategy selection
    - Memory integration
    - Observability setup
    """

    def __init__(
        self,
        default_config: ChatConfig | None = None,
        system_prompt_factory: Callable[[SystemPromptContext], str] | None = None,
    ):
        """
        Initialize the factory.

        Args:
            default_config: Default configuration for sessions
            system_prompt_factory: Custom function to generate system prompts
        """
        self._default_config = default_config or ChatConfig()
        self._system_prompt_factory = system_prompt_factory

        # Cache of active sessions by (node_path, observer_id)
        self._sessions: dict[tuple[str, str], ChatSession] = {}

    async def create_session(
        self,
        node_path: str,
        observer: "Umwelt[Any, Any]",
        config: ChatConfig | None = None,
        force_new: bool = False,
    ) -> ChatSession:
        """
        Create (or retrieve) a chat session for a node.

        Args:
            node_path: AGENTESE path (e.g., "self.soul", "world.town.citizen.elara")
            observer: The observer's umwelt
            config: Optional config override
            force_new: If True, always create a new session

        Returns:
            ChatSession ready for conversation
        """
        # Get observer ID
        observer_id = self._get_observer_id(observer)

        # Check for existing session
        session_key = (node_path, observer_id)
        if not force_new and session_key in self._sessions:
            existing = self._sessions[session_key]
            if existing.is_active:
                return existing

        # Resolve configuration
        resolved_config = self._resolve_config(node_path, config)

        # Build system prompt
        system_prompt = await self._build_system_prompt(node_path, observer, resolved_config)
        resolved_config.system_prompt = system_prompt

        # Create ChatFlow (if F-gent is available)
        flow = await self._create_flow(resolved_config)

        # Generate session ID
        session_id = generate_session_id(node_path, observer_id)

        # Create session
        session = ChatSession(
            session_id=session_id,
            node_path=node_path,
            observer=observer,
            config=resolved_config,
            flow=flow,
        )

        # Activate the session
        session.activate()

        # Cache the session
        self._sessions[session_key] = session

        return session

    def get_session(
        self,
        node_path: str,
        observer: "Umwelt[Any, Any]",
    ) -> ChatSession | None:
        """
        Get an existing session if available.

        Args:
            node_path: AGENTESE path
            observer: The observer's umwelt

        Returns:
            Existing session or None
        """
        observer_id = self._get_observer_id(observer)
        session_key = (node_path, observer_id)
        return self._sessions.get(session_key)

    def get_session_by_id(self, session_id: str) -> ChatSession | None:
        """
        Get a session by its ID.

        Args:
            session_id: The session ID

        Returns:
            Session or None
        """
        for session in self._sessions.values():
            if session.session_id == session_id:
                return session
        return None

    def list_sessions(
        self,
        node_path: str | None = None,
        observer_id: str | None = None,
    ) -> list[ChatSession]:
        """
        List sessions matching criteria.

        Args:
            node_path: Filter by node path
            observer_id: Filter by observer ID

        Returns:
            List of matching sessions
        """
        sessions = []
        for (np, oid), session in self._sessions.items():
            if node_path and np != node_path:
                continue
            if observer_id and oid != observer_id:
                continue
            sessions.append(session)
        return sessions

    def close_session(self, session: ChatSession) -> None:
        """
        Close and remove a session from cache.

        Args:
            session: Session to close
        """
        session.collapse("closed")

        # Find and remove from cache
        for key, cached in list(self._sessions.items()):
            if cached.session_id == session.session_id:
                del self._sessions[key]
                break

    # === Private Methods ===

    def _get_observer_id(self, observer: "Umwelt[Any, Any]") -> str:
        """Extract observer ID from umwelt."""
        try:
            meta = observer.meta
            return getattr(meta, "name", "anonymous")
        except Exception:
            return "anonymous"

    def _resolve_config(
        self,
        node_path: str,
        config: ChatConfig | None,
    ) -> ChatConfig:
        """
        Resolve configuration for a node.

        Prioritizes:
        1. Explicit config override
        2. Node-type specific defaults
        3. Factory default
        """
        if config is not None:
            return config

        # Select defaults based on node type
        if node_path.startswith("self.soul"):
            return ChatConfig(**SOUL_CHAT_CONFIG.__dict__.copy())
        elif "citizen" in node_path:
            return ChatConfig(**CITIZEN_CHAT_CONFIG.__dict__.copy())
        elif node_path.startswith("world.agent"):
            return ChatConfig(**AGENT_CHAT_CONFIG.__dict__.copy())

        return ChatConfig(**self._default_config.__dict__.copy())

    async def _build_system_prompt(
        self,
        node_path: str,
        observer: "Umwelt[Any, Any]",
        config: ChatConfig,
    ) -> str:
        """Build system prompt with dynamic context injection."""
        # If config has explicit system prompt, use it
        if config.system_prompt:
            return config.system_prompt

        # If custom factory provided, use it
        if self._system_prompt_factory:
            ctx = self._build_prompt_context(node_path, observer)
            return self._system_prompt_factory(ctx)

        # Use default prompts based on node type
        ctx = self._build_prompt_context(node_path, observer)
        return self._generate_default_prompt(node_path, ctx)

    def _build_prompt_context(
        self,
        node_path: str,
        observer: "Umwelt[Any, Any]",
    ) -> SystemPromptContext:
        """Build context for system prompt generation."""
        ctx = SystemPromptContext(node_path=node_path)

        # Extract observer info
        try:
            meta = observer.meta
            ctx.observer_name = getattr(meta, "name", "user")
            ctx.observer_archetype = getattr(meta, "archetype", "guest")
        except Exception as e:
            # Observer meta unavailable - continue with defaults
            logger.debug(f"Observer meta extraction failed, using defaults: {e}")

        # Extract citizen info if applicable
        if "citizen" in node_path:
            parts = node_path.split(".")
            for i, part in enumerate(parts):
                if part == "citizen" and i + 1 < len(parts):
                    ctx.citizen_name = parts[i + 1]
                    break

        return ctx

    def _generate_default_prompt(
        self,
        node_path: str,
        ctx: SystemPromptContext,
    ) -> str:
        """Generate default system prompt based on node type."""
        if node_path.startswith("self.soul"):
            # Soul prompt is self-contained, no placeholders needed
            return SOUL_SYSTEM_PROMPT

        elif "citizen" in node_path:
            return CITIZEN_SYSTEM_PROMPT.format(
                name=ctx.citizen_name or "Citizen",
                archetype=ctx.citizen_archetype or "townsperson",
                eigenvectors=ctx.eigenvectors or "Standard personality.",
                recent_memories=ctx.recent_memories,
                observer_name=ctx.observer_name,
            )

        else:
            return AGENT_SYSTEM_PROMPT.format(node_path=node_path)

    async def _create_flow(self, config: ChatConfig) -> Any:
        """Create underlying ChatFlow if F-gent is available."""
        try:
            from agents.f.flow import EchoAgent
            from agents.f.modalities.chat import ChatFlow

            # Create a simple echo agent for now
            # In production, this would be the LLM agent
            agent = EchoAgent()

            fgent_config = config.to_fgent_config()

            return ChatFlow(agent=agent, config=fgent_config)

        except ImportError:
            # F-gent not available
            return None


# === ChatServiceFactory: With Morpheus Composition ===


class ChatServiceFactory:
    """
    Factory that creates sessions with Morpheus composition.

    This wraps ChatSessionFactory and adds LLM integration per
    spec/protocols/chat-morpheus-synergy.md Part V.

    The factory:
    1. Delegates session creation to ChatSessionFactory
    2. Lazily creates ChatMorpheusComposer when Morpheus is available
    3. Injects composer into sessions for real LLM responses
    """

    def __init__(
        self,
        morpheus: "MorpheusPersistence | None" = None,
        model_selector: Callable[["Umwelt", str], "MorpheusConfig"] | None = None,
        default_config: ChatConfig | None = None,
        system_prompt_factory: Callable[[SystemPromptContext], str] | None = None,
    ):
        """
        Initialize the service factory.

        Args:
            morpheus: MorpheusPersistence for LLM calls (optional - graceful fallback)
            model_selector: Custom model selection function
            default_config: Default session configuration
            system_prompt_factory: Custom system prompt generator
        """
        self._base_factory = ChatSessionFactory(
            default_config=default_config,
            system_prompt_factory=system_prompt_factory,
        )
        self._morpheus = morpheus
        self._model_selector = model_selector
        self._composer: "ChatMorpheusComposer | None" = None

    @property
    def morpheus(self) -> "MorpheusPersistence | None":
        """Access Morpheus persistence (for testing)."""
        return self._morpheus

    def _get_or_create_composer(self) -> "ChatMorpheusComposer | None":
        """
        Lazily create composer when needed.

        CLI v7 Phase 2: Wires Summarizer and WindowPersistence for deep conversation.
        """
        if self._composer is None and self._morpheus is not None:
            from .composer import ChatMorpheusComposer
            from .model_selector import default_model_selector

            self._composer = ChatMorpheusComposer(
                morpheus=self._morpheus,
                model_selector=self._model_selector or default_model_selector,
            )

            # CLI v7 Phase 2: Wire Conductor services for deep conversation
            self._wire_conductor_services()

        return self._composer

    def _wire_conductor_services(self) -> None:
        """
        Wire Conductor services (Summarizer, WindowPersistence) into composer.

        CLI v7 Phase 2: Enables bounded conversation history with summarization
        and D-gent persistence for session recovery.
        """
        if self._composer is None:
            return

        # Wire summarizer for context compression
        try:
            from services.conductor import create_summarizer

            summarizer = create_summarizer(morpheus=self._morpheus)
            self._composer.set_summarizer(summarizer)
            logger.debug("Summarizer wired to ChatMorpheusComposer")
        except ImportError as e:
            logger.debug(f"Summarizer not available: {e}")

        # Wire window persistence for D-gent storage
        try:
            from services.conductor import get_window_persistence

            persistence = get_window_persistence()
            self._composer.set_window_persistence(persistence)
            logger.debug("WindowPersistence wired to ChatMorpheusComposer")
        except ImportError as e:
            logger.debug(f"WindowPersistence not available: {e}")

    async def create_session(
        self,
        node_path: str,
        observer: "Umwelt[Any, Any]",
        config: ChatConfig | None = None,
        force_new: bool = False,
    ) -> ChatSession:
        """
        Create session with Morpheus composition attached.

        If Morpheus is unavailable, returns session without composer (graceful fallback).

        Args:
            node_path: AGENTESE path
            observer: Observer umwelt
            config: Optional config override
            force_new: Force new session

        Returns:
            ChatSession with composer if Morpheus available
        """
        # Delegate to base factory
        session = await self._base_factory.create_session(node_path, observer, config, force_new)

        # Inject composer if Morpheus available
        composer = self._get_or_create_composer()
        if composer:
            session.set_composer(composer)

        return session

    # === Delegate methods to base factory ===

    def get_session(self, node_path: str, observer: "Umwelt[Any, Any]") -> ChatSession | None:
        """Get existing session."""
        return self._base_factory.get_session(node_path, observer)

    def get_session_by_id(self, session_id: str) -> ChatSession | None:
        """Get session by ID."""
        return self._base_factory.get_session_by_id(session_id)

    def list_sessions(
        self, node_path: str | None = None, observer_id: str | None = None
    ) -> list[ChatSession]:
        """List sessions."""
        return self._base_factory.list_sessions(node_path, observer_id)

    def close_session(self, session: ChatSession) -> None:
        """Close session."""
        self._base_factory.close_session(session)


# === Global Factory Instance ===

_factory_instance: ChatSessionFactory | ChatServiceFactory | None = None


def get_chat_factory() -> ChatSessionFactory | ChatServiceFactory:
    """
    Get the global chat session factory.

    IMPORTANT: This returns the global singleton. If no factory has been set
    via set_chat_factory(), creates a basic ChatSessionFactory as fallback.

    For production use with LLM integration, use services.providers.get_chat_factory()
    which creates a ChatServiceFactory with Morpheus composer.
    """
    global _factory_instance
    if _factory_instance is None:
        # Fallback for testing/direct usage without DI
        # In production, providers.get_chat_factory() should be called first
        logger.debug("Creating fallback ChatSessionFactory (no DI setup)")
        _factory_instance = ChatSessionFactory()
    return _factory_instance


def set_chat_factory(factory: ChatSessionFactory | ChatServiceFactory) -> None:
    """
    Set the global chat session factory.

    IMPORTANT: If a factory already exists, this migrates sessions from
    the old factory to the new one to prevent "session not found" errors.
    """
    global _factory_instance

    # Migrate sessions from old factory to new factory to prevent session loss
    if _factory_instance is not None and factory is not _factory_instance:
        old_sessions = (
            list(_factory_instance._sessions.items())
            if hasattr(_factory_instance, "_sessions")
            else []
        )
        if old_sessions:
            # Get the target session dict (for ChatServiceFactory, use _base_factory._sessions)
            target = (
                factory._base_factory._sessions
                if hasattr(factory, "_base_factory")
                else factory._sessions
            )
            for key, session in old_sessions:
                if key not in target:
                    target[key] = session
                    logger.debug(f"Migrated session {session.session_id} to new factory")

    _factory_instance = factory


def reset_chat_factory() -> None:
    """Reset the global chat session factory (for testing)."""
    global _factory_instance
    _factory_instance = None


__all__ = [
    "ChatSessionFactory",
    "ChatServiceFactory",
    "SystemPromptContext",
    "generate_session_id",
    "get_chat_factory",
    "set_chat_factory",
    "reset_chat_factory",
]
