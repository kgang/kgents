"""
Tests for Town Citizen Chat Integration (Phase 2.5)

Tests the TownCitizenNode, archetype system prompts, and chat affordances.
"""

import pytest

from protocols.agentese.affordances import (
    CHAT_AFFORDANCES,
    chatty,
    get_chatty_config,
    is_chatty,
)
from protocols.agentese.contexts.chat_resolver import ChatNode
from protocols.agentese.contexts.town_citizen import (
    ARCHETYPE_PROMPTS,
    CITIZEN_CHAT_AFFORDANCES,
    DEFAULT_CITIZEN_PROMPT,
    TownCitizenNode,
    TownCitizenResolver,
    build_citizen_system_prompt,
    create_citizen_chat_node,
    create_town_citizen_node,
    get_citizen_resolver,
    set_citizen_resolver,
)

# === Test Fixtures ===


@pytest.fixture
def builder_citizen():
    """Create a Builder citizen for testing."""
    from agents.town.archetypes import create_builder

    return create_builder("Marcus", "workshop")


@pytest.fixture
def healer_citizen():
    """Create a Healer citizen for testing."""
    from agents.town.archetypes import create_healer

    return create_healer("Sage", "healing_grove")


@pytest.fixture
def scholar_citizen():
    """Create a Scholar citizen for testing."""
    from agents.town.archetypes import create_scholar

    return create_scholar("Thales", "library")


# === Test @chatty Decorator on TownCitizenNode ===


def test_town_citizen_node_is_chatty():
    """TownCitizenNode is decorated with @chatty."""
    assert is_chatty(TownCitizenNode) is True


def test_town_citizen_node_chatty_config():
    """TownCitizenNode has expected chatty configuration."""
    config = get_chatty_config(TownCitizenNode)

    assert config is not None
    assert config.context_window == 8000  # Smaller than K-gent
    assert config.context_strategy == "summarize"
    assert config.persist_history is True
    assert config.inject_memories is True
    assert config.memory_recall_limit == 3  # Fewer memories for citizens
    assert config.entropy_budget == 0.8  # Slightly less entropy
    assert config.entropy_decay_per_turn == 0.03  # Faster decay


# === Test Archetype System Prompts ===


def test_archetype_prompts_exist():
    """All five archetypes have system prompts."""
    expected_archetypes = ["Builder", "Trader", "Healer", "Scholar", "Watcher"]

    for archetype in expected_archetypes:
        assert archetype in ARCHETYPE_PROMPTS
        assert "{name}" in ARCHETYPE_PROMPTS[archetype]
        assert "{eigenvectors}" in ARCHETYPE_PROMPTS[archetype]


def test_build_citizen_system_prompt_builder(builder_citizen):
    """Build system prompt for Builder citizen."""
    prompt = build_citizen_system_prompt(builder_citizen, "developer")

    assert builder_citizen.name in prompt
    assert "Builder" in prompt
    assert "architecture" in prompt.lower() or "construct" in prompt.lower()
    assert "Warmth:" in prompt
    assert "Curiosity:" in prompt


def test_build_citizen_system_prompt_healer(healer_citizen):
    """Build system prompt for Healer citizen."""
    prompt = build_citizen_system_prompt(healer_citizen, "visitor")

    assert healer_citizen.name in prompt
    assert "Healer" in prompt
    assert "mend" in prompt.lower() or "heal" in prompt.lower()


def test_build_citizen_system_prompt_scholar(scholar_citizen):
    """Build system prompt for Scholar citizen."""
    prompt = build_citizen_system_prompt(scholar_citizen, "scientist")

    assert scholar_citizen.name in prompt
    assert "Scholar" in prompt
    assert "discover" in prompt.lower() or "knowledge" in prompt.lower()


def test_build_citizen_system_prompt_includes_eigenvectors(builder_citizen):
    """System prompt includes eigenvector values."""
    prompt = build_citizen_system_prompt(builder_citizen)

    # Eigenvectors should be formatted with values
    assert "Warmth:" in prompt
    assert "Creativity:" in prompt
    assert "Patience:" in prompt
    assert "Resilience:" in prompt
    assert "Ambition:" in prompt


def test_build_citizen_system_prompt_includes_cosmotechnics(builder_citizen):
    """System prompt includes cosmotechnics metaphor."""
    prompt = build_citizen_system_prompt(builder_citizen)

    assert builder_citizen.cosmotechnics.metaphor in prompt


def test_build_citizen_system_prompt_includes_opacity(builder_citizen):
    """System prompt includes opacity statement if present."""
    prompt = build_citizen_system_prompt(builder_citizen)

    if builder_citizen.cosmotechnics.opacity_statement:
        assert builder_citizen.cosmotechnics.opacity_statement in prompt


def test_default_citizen_prompt_used_for_unknown_archetype():
    """Unknown archetypes use the default prompt."""
    from agents.town.citizen import GATHERING, Citizen, Eigenvectors

    unknown_citizen = Citizen(
        name="Mystery",
        archetype="Unknown",
        region="unknown",
        eigenvectors=Eigenvectors(),
        cosmotechnics=GATHERING,
    )

    prompt = build_citizen_system_prompt(unknown_citizen)

    assert unknown_citizen.name in prompt
    assert "Unknown" in prompt


# === Test TownCitizenNode ===


def test_town_citizen_node_handle():
    """TownCitizenNode has correct handle based on name."""
    node = create_town_citizen_node("elara")

    assert node.handle == "world.town.citizen.elara"


def test_town_citizen_node_handle_normalized():
    """Citizen names are normalized to lowercase in handle."""
    node = create_town_citizen_node("Marcus")

    assert node.handle == "world.town.citizen.marcus"


def test_town_citizen_node_with_citizen(builder_citizen):
    """TownCitizenNode can be created with Citizen instance."""
    node = create_town_citizen_node(builder_citizen.name, builder_citizen)

    assert node.citizen is builder_citizen
    assert node.citizen_name == builder_citizen.name


def test_town_citizen_node_affordances():
    """TownCitizenNode exposes citizen chat affordances."""
    node = create_town_citizen_node("elara")

    affordances = node._get_affordances_for_archetype("developer")

    for affordance in CITIZEN_CHAT_AFFORDANCES:
        assert affordance in affordances


def test_town_citizen_node_chat_included():
    """TownCitizenNode includes 'chat' affordance."""
    node = create_town_citizen_node("elara")

    affordances = node._get_affordances_for_archetype("developer")

    assert "chat" in affordances


def test_town_citizen_node_get_chat_node():
    """TownCitizenNode provides access to ChatNode."""
    node = create_town_citizen_node("elara")

    chat_node = node._get_chat_node()

    assert isinstance(chat_node, ChatNode)
    assert chat_node.handle == "world.town.citizen.elara.chat"


def test_town_citizen_node_get_system_prompt(builder_citizen):
    """TownCitizenNode provides system prompt for chat."""
    node = create_town_citizen_node(builder_citizen.name, builder_citizen)

    prompt = node.get_system_prompt("visitor")

    assert builder_citizen.name in prompt
    assert "Builder" in prompt


def test_town_citizen_node_get_system_prompt_without_citizen():
    """TownCitizenNode provides fallback prompt when no citizen."""
    node = create_town_citizen_node("unknown")

    prompt = node.get_system_prompt()

    assert "unknown" in prompt
    assert "Agent Town" in prompt


# === Test TownCitizenResolver ===


def test_citizen_resolver_resolve():
    """TownCitizenResolver creates nodes for citizen names."""
    resolver = TownCitizenResolver()

    node = resolver.resolve("elara")

    assert isinstance(node, TownCitizenNode)
    assert node.handle == "world.town.citizen.elara"


def test_citizen_resolver_caches_nodes():
    """TownCitizenResolver caches nodes by name."""
    resolver = TownCitizenResolver()

    node1 = resolver.resolve("elara")
    node2 = resolver.resolve("elara")

    assert node1 is node2


def test_citizen_resolver_different_names():
    """TownCitizenResolver creates different nodes for different names."""
    resolver = TownCitizenResolver()

    elara_node = resolver.resolve("elara")
    marcus_node = resolver.resolve("marcus")

    assert elara_node is not marcus_node
    assert elara_node.handle == "world.town.citizen.elara"
    assert marcus_node.handle == "world.town.citizen.marcus"


def test_citizen_resolver_with_citizen(builder_citizen):
    """TownCitizenResolver can accept Citizen instance."""
    resolver = TownCitizenResolver()

    node = resolver.resolve(builder_citizen.name, builder_citizen)

    assert node.citizen is builder_citizen


def test_citizen_resolver_list_citizens():
    """TownCitizenResolver lists cached citizen names."""
    resolver = TownCitizenResolver()

    resolver.resolve("elara")
    resolver.resolve("marcus")

    names = resolver.list_citizens()

    assert "elara" in names
    assert "marcus" in names


def test_citizen_resolver_clear_cache():
    """TownCitizenResolver clears cache."""
    resolver = TownCitizenResolver()

    resolver.resolve("elara")
    resolver.clear_cache()

    assert len(resolver.list_citizens()) == 0


# === Test Global Resolver ===


def test_global_citizen_resolver():
    """get_citizen_resolver returns global instance."""
    resolver1 = get_citizen_resolver()
    resolver2 = get_citizen_resolver()

    assert resolver1 is resolver2


def test_set_citizen_resolver():
    """set_citizen_resolver replaces global instance."""
    original = get_citizen_resolver()

    try:
        new_resolver = TownCitizenResolver()
        set_citizen_resolver(new_resolver)

        assert get_citizen_resolver() is new_resolver
    finally:
        # Restore original
        set_citizen_resolver(original)


def test_create_citizen_chat_node_helper():
    """create_citizen_chat_node uses global resolver."""
    node = create_citizen_chat_node("elara")

    assert isinstance(node, TownCitizenNode)
    assert node.handle == "world.town.citizen.elara"


# === Integration Tests ===


@pytest.mark.asyncio
async def test_town_citizen_manifest_without_citizen():
    """TownCitizenNode manifest shows not found when no citizen."""
    from protocols.agentese.node import Observer

    node = create_town_citizen_node("unknown_citizen")
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

    assert "not found" in rendering.to_text().lower()


@pytest.mark.asyncio
async def test_town_citizen_manifest_with_citizen(builder_citizen):
    """TownCitizenNode manifest shows citizen state."""
    from protocols.agentese.node import Observer

    node = create_town_citizen_node(builder_citizen.name, builder_citizen)
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

    text = rendering.to_text()
    assert builder_citizen.name in text
    assert "Builder" in text


@pytest.mark.asyncio
async def test_town_citizen_manifest_resting(builder_citizen):
    """TownCitizenNode manifest shows resting when citizen is resting."""
    from protocols.agentese.node import Observer

    # Put citizen to rest
    builder_citizen.rest()
    assert builder_citizen.is_resting

    node = create_town_citizen_node(builder_citizen.name, builder_citizen)
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

    text = rendering.to_text()
    assert "resting" in text.lower()
    assert "Right to Rest" in text


@pytest.mark.asyncio
async def test_town_citizen_eigenvectors_aspect(builder_citizen):
    """TownCitizenNode eigenvectors aspect returns eigenvector data."""
    from protocols.agentese.node import Observer

    node = create_town_citizen_node(builder_citizen.name, builder_citizen)
    observer = Observer.test()

    class MockUmwelt:
        def __init__(self, obs):
            self.dna = type(
                "DNA",
                (),
                {"archetype": obs.archetype, "capabilities": obs.capabilities},
            )()

    umwelt = MockUmwelt(observer)
    result = await node._get_eigenvectors(umwelt)

    assert result["name"] == builder_citizen.name
    assert result["archetype"] == "Builder"
    assert "eigenvectors" in result
    assert "warmth" in result["eigenvectors"]
    assert "creativity" in result["eigenvectors"]


@pytest.mark.asyncio
async def test_town_citizen_cosmotechnics_aspect(builder_citizen):
    """TownCitizenNode cosmotechnics aspect returns cosmotechnics data."""
    from protocols.agentese.node import Observer

    node = create_town_citizen_node(builder_citizen.name, builder_citizen)
    observer = Observer.test()

    class MockUmwelt:
        def __init__(self, obs):
            self.dna = type(
                "DNA",
                (),
                {"archetype": obs.archetype, "capabilities": obs.capabilities},
            )()

    umwelt = MockUmwelt(observer)
    result = await node._get_cosmotechnics(umwelt)

    assert result["name"] == builder_citizen.name
    assert "cosmotechnics" in result
    assert "metaphor" in result["cosmotechnics"]


@pytest.mark.asyncio
async def test_town_citizen_mood_aspect(builder_citizen):
    """TownCitizenNode mood aspect returns mood data."""
    from protocols.agentese.node import Observer

    node = create_town_citizen_node(builder_citizen.name, builder_citizen)
    observer = Observer.test()

    class MockUmwelt:
        def __init__(self, obs):
            self.dna = type(
                "DNA",
                (),
                {"archetype": obs.archetype, "capabilities": obs.capabilities},
            )()

    umwelt = MockUmwelt(observer)
    result = await node._get_mood(umwelt)

    assert result["name"] == builder_citizen.name
    assert "mood" in result
    assert "is_available" in result


@pytest.mark.asyncio
async def test_town_citizen_chat_node_manifest():
    """ChatNode for citizen shows session status."""
    from protocols.agentese.node import Observer

    citizen_node = create_town_citizen_node("elara")
    chat_node = citizen_node._get_chat_node()
    observer = Observer.test()

    class MockUmwelt:
        def __init__(self, obs):
            self.dna = type(
                "DNA",
                (),
                {"archetype": obs.archetype, "capabilities": obs.capabilities},
            )()

    umwelt = MockUmwelt(observer)
    rendering = await chat_node.manifest(umwelt)

    text = rendering.to_text()
    assert "Chat:" in text or "Session:" in text


# === Test Eigenvector Formatting ===


def test_eigenvector_formatting(builder_citizen):
    """Eigenvectors are formatted correctly in prompt."""
    prompt = build_citizen_system_prompt(builder_citizen)

    # Check that eigenvector values are present and formatted
    assert f"{builder_citizen.eigenvectors.warmth:.2f}" in prompt
    assert f"{builder_citizen.eigenvectors.creativity:.2f}" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
