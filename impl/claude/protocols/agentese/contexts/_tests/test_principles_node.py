"""
Tests for concept.principles AGENTESE node.

Integration tests verifying the node is discoverable and all aspects work.
Verifies the four laws from spec/principles/node.md.
"""

from __future__ import annotations

import pytest

from protocols.agentese.node import Observer
from protocols.agentese.registry import get_registry

# === Node Discovery ===


def test_node_registered() -> None:
    """PrinciplesNode is registered in the registry."""
    registry = get_registry()

    # May need to import to trigger registration
    try:
        from protocols.agentese.contexts import concept_principles  # noqa: F401
    except ImportError:
        pytest.skip("PrinciplesNode not available")

    assert registry.has("concept.principles")


def test_node_in_discover() -> None:
    """concept.principles appears in discover paths."""
    registry = get_registry()

    try:
        from protocols.agentese.contexts import concept_principles  # noqa: F401
    except ImportError:
        pytest.skip("PrinciplesNode not available")

    paths = registry.list_paths()
    assert "concept.principles" in paths


# === Node Instantiation ===


@pytest.fixture
def node():
    """Get a PrinciplesNode instance."""
    try:
        from protocols.agentese.contexts.concept_principles import get_principles_node

        return get_principles_node()
    except ImportError:
        pytest.skip("PrinciplesNode not available")


@pytest.fixture
def observer() -> Observer:
    """Create a test observer."""
    return Observer.test()


# === Law Tests ===


@pytest.mark.asyncio
async def test_law_stance_coherence(node, observer: Observer) -> None:
    """Law: manifest(stance=X) returns exactly STANCE_SLICES[X]."""
    from services.principles import STANCE_SLICES, Stance

    for stance in Stance:
        result = await node.manifest(observer, stance=stance.value)
        expected_slices = STANCE_SLICES[stance]

        # Result should mention files from the stance slices
        content = result.to_dict().get("metadata", {}).get("slices", [])
        for expected_file in expected_slices:
            assert expected_file in content, f"Missing {expected_file} for stance {stance}"


@pytest.mark.asyncio
async def test_law_check_completeness(node, observer: Observer) -> None:
    """Law: check() always evaluates all seven principles unless filtered."""
    result = await node.check(observer, target="test agent")

    checks = result.to_dict().get("metadata", {}).get("checks", [])
    assert len(checks) == 7

    # All principles 1-7 should be represented
    principles = {c["principle"] for c in checks}
    assert principles == {1, 2, 3, 4, 5, 6, 7}


@pytest.mark.asyncio
async def test_law_heal_specificity(node, observer: Observer) -> None:
    """Law: heal(violation) always returns at least one prescription path."""
    for principle in range(1, 8):
        result = await node.heal(observer, violation=principle)

        path = result.to_dict().get("metadata", {}).get("path", [])
        assert len(path) >= 1, f"No path for principle {principle}"


@pytest.mark.asyncio
async def test_law_constitution_immutability(node, observer: Observer) -> None:
    """Law: constitution() returns identical content across all observers."""
    # Different observer archetypes
    guest = Observer.guest()
    developer = Observer(archetype="developer", capabilities=frozenset({"write"}))
    architect = Observer(archetype="architect", capabilities=frozenset({"admin"}))

    result1 = await node.constitution(guest)
    result2 = await node.constitution(developer)
    result3 = await node.constitution(architect)

    # All should return same content
    content1 = result1.to_dict().get("content", "")
    content2 = result2.to_dict().get("content", "")
    content3 = result3.to_dict().get("content", "")

    assert content1 == content2
    assert content2 == content3


# === Aspect Tests ===


@pytest.mark.asyncio
async def test_manifest_aspect(node, observer: Observer) -> None:
    """manifest aspect works."""
    result = await node.manifest(observer)

    assert result is not None
    d = result.to_dict()
    assert "summary" in d
    assert "content" in d


@pytest.mark.asyncio
async def test_constitution_aspect(node, observer: Observer) -> None:
    """constitution aspect works."""
    result = await node.constitution(observer)

    content = result.to_dict().get("content", "")
    # Constitution can be full content or a reference summary
    assert len(content) > 0
    # Check for either full content or file reference format
    assert "CONSTITUTION" in content or "Tasteful" in content


@pytest.mark.asyncio
async def test_meta_aspect(node, observer: Observer) -> None:
    """meta aspect works."""
    result = await node.meta(observer)

    content = result.to_dict().get("content", "")
    assert len(content) > 0


@pytest.mark.asyncio
async def test_meta_section_aspect(node, observer: Observer) -> None:
    """meta aspect with section works."""
    result = await node.meta(observer, section="The Accursed Share")

    content = result.to_dict().get("content", "")
    assert "Accursed" in content


@pytest.mark.asyncio
async def test_operational_aspect(node, observer: Observer) -> None:
    """operational aspect works."""
    result = await node.operational(observer)

    content = result.to_dict().get("content", "")
    assert len(content) > 0


@pytest.mark.asyncio
async def test_ad_aspect_by_id(node, observer: Observer) -> None:
    """ad aspect works with id."""
    result = await node.ad(observer, ad_id=1)

    content = result.to_dict().get("content", "")
    # AD-001 is Universal Functor
    assert len(content) > 0


@pytest.mark.asyncio
async def test_ad_aspect_by_category(node, observer: Observer) -> None:
    """ad aspect works with category."""
    result = await node.ad(observer, category="categorical")

    d = result.to_dict()
    assert d.get("summary", "").lower().startswith("ads:")


@pytest.mark.asyncio
async def test_check_aspect(node, observer: Observer) -> None:
    """check aspect works."""
    result = await node.check(observer, target="my test agent")

    d = result.to_dict()
    assert "metadata" in d
    checks = d["metadata"].get("checks", [])
    assert len(checks) == 7


@pytest.mark.asyncio
async def test_teach_aspect(node, observer: Observer) -> None:
    """teach aspect works."""
    result = await node.teach(observer, principle=5, depth="examples")

    content = result.to_dict().get("content", "")
    assert "Composable" in content


@pytest.mark.asyncio
async def test_heal_aspect(node, observer: Observer) -> None:
    """heal aspect works."""
    result = await node.heal(observer, violation=1)

    d = result.to_dict()
    assert "Tasteful" in d.get("summary", "")


# === Affordances ===


def test_base_affordances(node) -> None:
    """Node has base affordances."""
    from protocols.agentese.node import AgentMeta

    meta = AgentMeta(name="test", archetype="guest")
    affordances = node.affordances(meta)

    assert "manifest" in affordances
    assert "affordances" in affordances


def test_developer_affordances(node) -> None:
    """Developer has check/heal/ad affordances."""
    from protocols.agentese.node import AgentMeta

    meta = AgentMeta(name="test", archetype="developer")
    affordances = node.affordances(meta)

    assert "check" in affordances
    assert "heal" in affordances
    assert "ad" in affordances


# === Handle ===


def test_node_handle(node) -> None:
    """Node has correct handle."""
    assert node.handle == "concept.principles"
