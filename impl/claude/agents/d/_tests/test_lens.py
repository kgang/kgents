"""
Tests for Lens infrastructure.

Lens Laws (from category theory):
- GetPut: set(s, get(s)) == s
- PutGet: get(set(s, v)) == v
- PutPut: set(set(s, v1), v2) == set(s, v2)

Composition Laws:
- Associativity: (l1 >> l2) >> l3 == l1 >> (l2 >> l3)
"""

from dataclasses import dataclass

import pytest
from agents.d.lens import (
    field_lens,
    identity_lens,
    index_lens,
    key_lens,
    verify_lens_laws,
)


@dataclass
class Address:
    city: str
    zip: str


@dataclass
class User:
    name: str
    address: Address


# === Basic Lens Tests ===


def test_key_lens_get() -> None:
    """key_lens extracts dictionary value."""
    lens = key_lens("name")
    state = {"name": "Alice", "age": 30}
    assert lens.get(state) == "Alice"


def test_key_lens_set() -> None:
    """key_lens updates dictionary value."""
    lens = key_lens("name")
    state = {"name": "Alice", "age": 30}
    new_state = lens.set(state, "Bob")

    assert new_state["name"] == "Bob"
    assert new_state["age"] == 30
    assert state["name"] == "Alice"  # Original unchanged


def test_field_lens_get() -> None:
    """field_lens extracts dataclass field."""
    lens = field_lens("name")
    user = User(name="Alice", address=Address(city="NYC", zip="10001"))
    assert lens.get(user) == "Alice"


def test_field_lens_set() -> None:
    """field_lens updates dataclass field."""
    lens = field_lens("name")
    user = User(name="Alice", address=Address(city="NYC", zip="10001"))
    new_user = lens.set(user, "Bob")

    assert new_user.name == "Bob"
    assert user.name == "Alice"  # Original unchanged
    assert new_user.address == user.address  # Other fields unchanged


def test_index_lens_get() -> None:
    """index_lens extracts list element."""
    lens = index_lens(0)
    items = [1, 2, 3]
    assert lens.get(items) == 1


def test_index_lens_set() -> None:
    """index_lens updates list element."""
    lens = index_lens(1)
    items = [1, 2, 3]
    new_items = lens.set(items, 20)

    assert new_items == [1, 20, 3]
    assert items == [1, 2, 3]  # Original unchanged


def test_identity_lens() -> None:
    """identity_lens returns state unchanged."""
    lens = identity_lens()
    state = {"name": "Alice"}

    assert lens.get(state) == state
    assert lens.set(state, {"name": "Bob"}) == {"name": "Bob"}


# === Composition Tests ===


def test_lens_composition_dict() -> None:
    """Lenses compose to access nested dict."""
    user_lens = key_lens("user")
    name_lens = key_lens("name")
    composed = user_lens >> name_lens

    state = {"user": {"name": "Alice", "age": 30}, "count": 5}

    assert composed.get(state) == "Alice"

    new_state = composed.set(state, "Bob")
    assert new_state["user"]["name"] == "Bob"
    assert new_state["user"]["age"] == 30
    assert new_state["count"] == 5


def test_lens_composition_dataclass() -> None:
    """Lenses compose to access nested dataclass."""
    user_lens = field_lens("user")
    address_lens = field_lens("address")
    city_lens = field_lens("city")

    composed = user_lens >> address_lens >> city_lens

    @dataclass
    class State:
        user: User
        settings: dict

    state = State(
        user=User(name="Alice", address=Address(city="NYC", zip="10001")),
        settings={},
    )

    assert composed.get(state) == "NYC"

    new_state = composed.set(state, "SF")
    assert new_state.user.address.city == "SF"
    assert state.user.address.city == "NYC"  # Original unchanged


@pytest.mark.law("associativity")
@pytest.mark.law_associativity
def test_lens_composition_associativity() -> None:
    """Lens composition is associative: (a >> b) >> c = a >> (b >> c)"""
    l1 = key_lens("a")
    l2 = key_lens("b")
    l3 = key_lens("c")

    state = {"a": {"b": {"c": 42}}}

    left = (l1 >> l2) >> l3
    right = l1 >> (l2 >> l3)

    assert left.get(state) == right.get(state) == 42
    assert left.set(state, 99) == right.set(state, 99)


# === Lens Law Tests ===


@pytest.mark.law("lens")
class TestLensLaws:
    """Lens laws verification tests."""

    def test_key_lens_laws(self) -> None:
        """key_lens satisfies all three lens laws."""
        lens = key_lens("name")
        state = {"name": "Alice", "age": 30}

        laws = verify_lens_laws(lens, state, "Bob", "Carol")

        assert laws["get_put"], "GetPut law violated"
        assert laws["put_get"], "PutGet law violated"
        assert laws["put_put"], "PutPut law violated"

    def test_field_lens_laws(self) -> None:
        """field_lens satisfies all three lens laws."""
        lens = field_lens("name")
        user = User(name="Alice", address=Address(city="NYC", zip="10001"))

        laws = verify_lens_laws(lens, user, "Bob", "Carol")

        assert laws["get_put"], "GetPut law violated"
        assert laws["put_get"], "PutGet law violated"
        assert laws["put_put"], "PutPut law violated"

    def test_index_lens_laws(self) -> None:
        """index_lens satisfies all three lens laws."""
        lens = index_lens(1)
        state = [1, 2, 3]

        laws = verify_lens_laws(lens, state, 20, 30)

        assert laws["get_put"], "GetPut law violated"
        assert laws["put_get"], "PutGet law violated"
        assert laws["put_put"], "PutPut law violated"

    def test_composed_lens_laws(self) -> None:
        """Composed lenses preserve lens laws."""
        user_lens = key_lens("user")
        name_lens = key_lens("name")
        composed = user_lens >> name_lens

        state = {"user": {"name": "Alice", "age": 30}, "count": 5}

        laws = verify_lens_laws(composed, state, "Bob", "Carol")

        assert laws["get_put"], "GetPut law violated for composition"
        assert laws["put_get"], "PutGet law violated for composition"
        assert laws["put_put"], "PutPut law violated for composition"


# === Property-Based Tests ===


@pytest.mark.law("lens")
@pytest.mark.property
class TestLensLawsPropertyBased:
    """Property-based lens law tests."""

    @pytest.mark.parametrize(
        "state,value1,value2",
        [
            ({"a": 1, "b": 2}, 10, 20),
            ({"a": "hello", "b": "world"}, "foo", "bar"),
            ({"a": [1, 2, 3], "b": [4, 5]}, [10], [20, 30]),
        ],
    )
    def test_key_lens_laws_property_based(self, state, value1, value2) -> None:
        """Property test: key_lens laws hold for various types."""
        lens = key_lens("a")
        laws = verify_lens_laws(lens, state, value1, value2)

        assert all(laws.values()), f"Laws violated: {laws}"

    @pytest.mark.parametrize(
        "items,index,v1,v2",
        [
            ([1, 2, 3], 0, 10, 20),
            ([1, 2, 3], 1, 10, 20),
            ([1, 2, 3], 2, 10, 20),
            (["a", "b", "c"], 1, "x", "y"),
        ],
    )
    def test_index_lens_laws_property_based(self, items, index, v1, v2) -> None:
        """Property test: index_lens laws hold for various indices."""
        lens = index_lens(index)
        laws = verify_lens_laws(lens, items, v1, v2)

        assert all(laws.values()), f"Laws violated for index {index}: {laws}"
