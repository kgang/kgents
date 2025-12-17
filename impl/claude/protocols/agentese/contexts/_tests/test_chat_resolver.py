"""
Tests for Chat Protocol Integration (Phase 2)

Tests the @chatty decorator, ChatNode, and ChatResolver.
"""

import pytest
from protocols.agentese.affordances import (
    CHAT_AFFORDANCES,
    CHATTY_MARKER,
    ChattyConfig,
    chatty,
    get_chatty_config,
    is_chatty,
    to_chat_config,
)
from protocols.agentese.chat.config import ChatConfig, ContextStrategy
from protocols.agentese.contexts.chat_resolver import (
    ChatNode,
    ChatResolver,
    create_chat_node,
    get_chat_resolver,
    set_chat_resolver,
)
from protocols.agentese.contexts.self_soul import (
    SOUL_AFFORDANCES,
    SOUL_CHAT_AFFORDANCES,
    SoulNode,
    create_soul_node,
)
from protocols.agentese.node import BaseLogosNode

# === Test @chatty decorator ===


def test_chatty_decorator_marks_class():
    """@chatty adds the CHATTY_MARKER attribute."""

    @chatty()
    class TestNode:
        pass

    assert hasattr(TestNode, CHATTY_MARKER)
    assert isinstance(getattr(TestNode, CHATTY_MARKER), ChattyConfig)


def test_chatty_decorator_with_config():
    """@chatty accepts custom configuration."""

    @chatty(
        context_window=4000,
        context_strategy="sliding",
        persist_history=False,
        entropy_budget=0.5,
    )
    class TestNode:
        pass

    config = get_chatty_config(TestNode)
    assert config is not None
    assert config.context_window == 4000
    assert config.context_strategy == "sliding"
    assert config.persist_history is False
    assert config.entropy_budget == 0.5


def test_is_chatty_function():
    """is_chatty correctly identifies chatty classes and instances."""

    @chatty()
    class ChattyNode:
        pass

    class NonChattyNode:
        pass

    # Test class
    assert is_chatty(ChattyNode) is True
    assert is_chatty(NonChattyNode) is False

    # Test instance
    assert is_chatty(ChattyNode()) is True
    assert is_chatty(NonChattyNode()) is False


def test_get_chatty_config_returns_none_for_non_chatty():
    """get_chatty_config returns None for non-chatty classes."""

    class NotChatty:
        pass

    assert get_chatty_config(NotChatty) is None
    assert get_chatty_config(NotChatty()) is None


def test_to_chat_config_conversion():
    """to_chat_config converts ChattyConfig to ChatConfig."""
    chatty_config = ChattyConfig(
        context_window=16000,
        context_strategy="summarize",
        persist_history=True,
        memory_key="test_key",
        inject_memories=True,
        memory_recall_limit=10,
        entropy_budget=0.8,
        entropy_decay_per_turn=0.05,
    )

    chat_config = to_chat_config(chatty_config)

    assert isinstance(chat_config, ChatConfig)
    assert chat_config.context_window == 16000
    assert chat_config.context_strategy == ContextStrategy.SUMMARIZE
    assert chat_config.persist_history is True
    assert chat_config.memory_key == "test_key"
    assert chat_config.inject_memories is True
    assert chat_config.memory_recall_limit == 10
    assert chat_config.entropy_budget == 0.8
    assert chat_config.entropy_decay_per_turn == 0.05


def test_chat_affordances_defined():
    """CHAT_AFFORDANCES contains expected verbs."""
    assert "send" in CHAT_AFFORDANCES
    assert "stream" in CHAT_AFFORDANCES
    assert "history" in CHAT_AFFORDANCES
    assert "turn" in CHAT_AFFORDANCES
    assert "context" in CHAT_AFFORDANCES
    assert "metrics" in CHAT_AFFORDANCES
    assert "reset" in CHAT_AFFORDANCES
    assert "fork" in CHAT_AFFORDANCES


# === Test ChatNode ===


def test_chat_node_handle():
    """ChatNode has correct handle based on parent path."""
    node = ChatNode(
        _handle="self.soul.chat",
        _parent_path="self.soul",
    )

    assert node.handle == "self.soul.chat"


def test_chat_node_affordances():
    """ChatNode exposes all chat affordances."""
    node = ChatNode(
        _handle="self.soul.chat",
        _parent_path="self.soul",
    )

    affordances = node._get_affordances_for_archetype("developer")

    for affordance in CHAT_AFFORDANCES:
        assert affordance in affordances


# === Test ChatResolver ===


def test_chat_resolver_resolve():
    """ChatResolver creates ChatNode for parent path."""
    resolver = ChatResolver()

    node = resolver.resolve("self.soul")

    assert isinstance(node, ChatNode)
    assert node.handle == "self.soul.chat"


def test_chat_resolver_caches_nodes():
    """ChatResolver caches ChatNodes by parent path."""
    resolver = ChatResolver()

    node1 = resolver.resolve("self.soul")
    node2 = resolver.resolve("self.soul")

    assert node1 is node2


def test_chat_resolver_different_paths():
    """ChatResolver creates different nodes for different paths."""
    resolver = ChatResolver()

    soul_node = resolver.resolve("self.soul")
    citizen_node = resolver.resolve("world.town.citizen.elara")

    assert soul_node is not citizen_node
    assert soul_node.handle == "self.soul.chat"
    assert citizen_node.handle == "world.town.citizen.elara.chat"


def test_global_chat_resolver():
    """get_chat_resolver returns global instance."""
    resolver1 = get_chat_resolver()
    resolver2 = get_chat_resolver()

    assert resolver1 is resolver2


def test_set_chat_resolver():
    """set_chat_resolver replaces global instance."""
    original = get_chat_resolver()

    try:
        new_resolver = ChatResolver()
        set_chat_resolver(new_resolver)

        assert get_chat_resolver() is new_resolver
    finally:
        # Restore original
        set_chat_resolver(original)


def test_create_chat_node_helper():
    """create_chat_node uses global resolver."""
    node = create_chat_node("self.soul")

    assert isinstance(node, ChatNode)
    assert node.handle == "self.soul.chat"


# === Test SoulNode ===


def test_soul_node_is_chatty():
    """SoulNode is decorated with @chatty."""
    assert is_chatty(SoulNode) is True


def test_soul_node_chatty_config():
    """SoulNode has expected chatty configuration."""
    config = get_chatty_config(SoulNode)

    assert config is not None
    assert config.context_window == 16000
    assert config.context_strategy == "summarize"
    assert config.persist_history is True
    assert config.inject_memories is True


def test_soul_node_handle():
    """SoulNode has correct handle."""
    node = create_soul_node()

    assert node.handle == "self.soul"


def test_soul_node_affordances():
    """SoulNode includes both soul and chat affordances."""
    node = create_soul_node()

    affordances = node._get_affordances_for_archetype("developer")

    # Check soul affordances
    for affordance in SOUL_AFFORDANCES:
        assert affordance in affordances

    # Check chat is included
    assert "chat" in affordances


def test_soul_chat_affordances_combined():
    """SOUL_CHAT_AFFORDANCES includes both soul and chat."""
    for affordance in SOUL_AFFORDANCES:
        assert affordance in SOUL_CHAT_AFFORDANCES

    assert "chat" in SOUL_CHAT_AFFORDANCES


def test_soul_node_get_chat_node():
    """SoulNode provides access to ChatNode via chat aspect."""
    soul_node = create_soul_node()

    chat_node = soul_node._get_chat_node()

    assert isinstance(chat_node, ChatNode)
    assert chat_node.handle == "self.soul.chat"


# === Integration Tests ===


@pytest.mark.asyncio
async def test_soul_node_manifest_without_soul():
    """SoulNode manifest shows uninitialized state when no soul injected."""
    from protocols.agentese.node import Observer

    node = create_soul_node(soul=None)
    observer = Observer.test()

    # Create a mock Umwelt with the observer
    class MockUmwelt:
        def __init__(self, obs):
            self.dna = type(
                "DNA",
                (),
                {"archetype": obs.archetype, "capabilities": obs.capabilities},
            )()

    umwelt = MockUmwelt(observer)
    rendering = await node.manifest(umwelt)

    assert "Soul not initialized" in rendering.to_text()


@pytest.mark.asyncio
async def test_chat_node_manifest():
    """ChatNode manifest shows session status."""
    from protocols.agentese.node import Observer

    node = create_chat_node("self.soul")
    observer = Observer.test()

    class MockUmwelt:
        def __init__(self, obs):
            self.dna = type(
                "DNA",
                (),
                {"archetype": obs.archetype, "capabilities": obs.capabilities},
            )()

    umwelt = MockUmwelt(observer)
    rendering = await node.manifest(umwelt)

    # Should show chat session info
    text = rendering.to_text()
    assert "Chat:" in text or "Session:" in text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
