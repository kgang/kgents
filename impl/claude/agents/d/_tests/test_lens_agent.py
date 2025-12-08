"""Tests for LensAgent."""

import pytest
from dataclasses import dataclass

from agents.d import VolatileAgent
from agents.d.lens import key_lens, field_lens
from agents.d.lens_agent import LensAgent, focused


@dataclass
class Address:
    city: str
    zip: str


@dataclass
class User:
    name: str
    address: Address


# === Basic LensAgent Tests ===


@pytest.mark.asyncio
async def test_lens_agent_focused_load():
    """LensAgent loads sub-state through lens."""
    parent = VolatileAgent(_state={"users": {"alice": "data"}, "products": {}})
    lens_dgent = LensAgent(parent=parent, lens=key_lens("users"))

    users = await lens_dgent.load()
    assert users == {"alice": "data"}


@pytest.mark.asyncio
async def test_lens_agent_focused_save():
    """LensAgent saves sub-state, updates parent."""
    parent = VolatileAgent(_state={"users": {}, "products": {}})
    lens_dgent = LensAgent(parent=parent, lens=key_lens("users"))

    await lens_dgent.save({"alice": {"age": 30}})

    # Check sub-state
    users = await lens_dgent.load()
    assert users == {"alice": {"age": 30}}

    # Check parent state
    full_state = await parent.load()
    assert full_state["users"] == {"alice": {"age": 30}}
    assert full_state["products"] == {}  # Unchanged


@pytest.mark.asyncio
async def test_lens_agent_isolation():
    """LensAgent sees only sub-state, not full state."""
    parent = VolatileAgent(
        _state={
            "users": {"alice": "data"},
            "products": {"product1": "info"},
            "secret": "hidden",
        }
    )
    lens_dgent = LensAgent(parent=parent, lens=key_lens("users"))

    sub_state = await lens_dgent.load()

    # LensAgent sees only "users"
    assert sub_state == {"alice": "data"}
    assert "products" not in sub_state  # type: ignore
    assert "secret" not in sub_state  # type: ignore


@pytest.mark.asyncio
async def test_lens_agent_history():
    """LensAgent projects history through lens."""
    parent = VolatileAgent(_state={"count": 0, "other": "data"})
    lens_dgent = LensAgent(parent=parent, lens=key_lens("count"))

    # Save multiple states
    await parent.save({"count": 1, "other": "data"})
    await parent.save({"count": 2, "other": "data"})
    await parent.save({"count": 3, "other": "data"})

    # LensAgent history shows only "count" field
    history = await lens_dgent.history()

    assert len(history) == 3
    assert history[0] == 2  # Newest first (current excluded)
    assert history[1] == 1
    assert history[2] == 0


# === Multi-Agent Coordination Tests ===


@pytest.mark.asyncio
async def test_multiple_lens_agents_shared_parent():
    """Multiple LensAgents can share parent with different lenses."""
    parent = VolatileAgent(_state={"users": {}, "products": {}, "orders": {}})

    user_dgent = LensAgent(parent=parent, lens=key_lens("users"))
    product_dgent = LensAgent(parent=parent, lens=key_lens("products"))
    order_dgent = LensAgent(parent=parent, lens=key_lens("orders"))

    # Each agent updates its domain
    await user_dgent.save({"alice": {"age": 30}})
    await product_dgent.save({"item1": {"price": 100}})
    await order_dgent.save({"order1": {"status": "pending"}})

    # Each agent sees only its domain
    assert await user_dgent.load() == {"alice": {"age": 30}}
    assert await product_dgent.load() == {"item1": {"price": 100}}
    assert await order_dgent.load() == {"order1": {"status": "pending"}}

    # Parent has all domains
    full_state = await parent.load()
    assert full_state == {
        "users": {"alice": {"age": 30}},
        "products": {"item1": {"price": 100}},
        "orders": {"order1": {"status": "pending"}},
    }


# === Composition Tests ===


@pytest.mark.asyncio
async def test_lens_agent_with_composed_lens():
    """LensAgent works with composed lenses for deep access."""
    user_lens = key_lens("user")
    address_lens = key_lens("address")
    city_lens = key_lens("city")
    composed = user_lens >> address_lens >> city_lens

    parent = VolatileAgent(
        _state={
            "user": {"name": "Alice", "address": {"city": "NYC", "zip": "10001"}},
            "settings": {},
        }
    )

    city_dgent = LensAgent(parent=parent, lens=composed)

    # Load city
    city = await city_dgent.load()
    assert city == "NYC"

    # Update city
    await city_dgent.save("SF")

    # Verify update
    updated_city = await city_dgent.load()
    assert updated_city == "SF"

    # Verify parent structure preserved
    full_state = await parent.load()
    assert full_state["user"]["name"] == "Alice"
    assert full_state["user"]["address"]["zip"] == "10001"
    assert full_state["user"]["address"]["city"] == "SF"


@pytest.mark.asyncio
async def test_lens_agent_with_dataclass():
    """LensAgent works with dataclass states."""
    parent = VolatileAgent(
        _state=User(name="Alice", address=Address(city="NYC", zip="10001"))
    )

    name_dgent = LensAgent(parent=parent, lens=field_lens("name"))

    # Load name
    name = await name_dgent.load()
    assert name == "Alice"

    # Update name
    await name_dgent.save("Bob")

    # Verify
    updated_name = await name_dgent.load()
    assert updated_name == "Bob"

    # Parent dataclass updated correctly
    full_user = await parent.load()
    assert full_user.name == "Bob"
    assert full_user.address.city == "NYC"


# === Convenience Function Tests ===


@pytest.mark.asyncio
async def test_focused_convenience_function():
    """focused() creates LensAgent correctly."""
    parent = VolatileAgent(_state={"a": 1, "b": 2})
    lens_dgent = focused(parent, key_lens("a"))

    value = await lens_dgent.load()
    assert value == 1

    await lens_dgent.save(10)
    assert await lens_dgent.load() == 10


# === Edge Cases ===


@pytest.mark.asyncio
async def test_lens_agent_none_value():
    """LensAgent handles None values correctly."""
    parent = VolatileAgent(_state={"value": None, "other": "data"})
    lens_dgent = LensAgent(parent=parent, lens=key_lens("value"))

    value = await lens_dgent.load()
    assert value is None

    await lens_dgent.save("something")
    assert await lens_dgent.load() == "something"


@pytest.mark.asyncio
async def test_lens_agent_empty_history():
    """LensAgent handles empty history gracefully."""
    parent = VolatileAgent(_state={"count": 0})
    lens_dgent = LensAgent(parent=parent, lens=key_lens("count"))

    history = await lens_dgent.history()
    # VolatileAgent starts with no history
    assert history == []
