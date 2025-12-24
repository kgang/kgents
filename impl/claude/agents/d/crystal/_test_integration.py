"""
Integration test for Crystal primitives.

Verifies the complete lifecycle from raw data to typed crystals.
"""

from dataclasses import dataclass
from datetime import datetime, UTC

from .datum import Datum
from .crystal import Crystal
from .schema import Schema
from .query import Query


@dataclass(frozen=True)
class SimpleV1:
    name: str


@dataclass(frozen=True)
class SimpleV2:
    name: str
    count: int = 0


def test_datum_immutability() -> None:
    """Test that Datums are truly immutable."""
    d1 = Datum.create({"test": "value"}, tags={"initial"})
    d2 = d1.with_tags("added")

    assert d1 is not d2
    assert d1.tags == frozenset({"initial"})
    assert d2.tags == frozenset({"initial", "added"})
    print("✓ Datum immutability")


def test_schema_parsing() -> None:
    """Test schema parsing and validation."""
    schema = Schema(name="test.simple", version=1, contract=SimpleV1)

    data = {"name": "test"}
    value = schema.parse(data)

    assert isinstance(value, SimpleV1)
    assert value.name == "test"
    print("✓ Schema parsing")


def test_schema_migration() -> None:
    """Test schema version upgrades."""
    schema = Schema(
        name="test.simple",
        version=2,
        contract=SimpleV2,
        migrations={
            1: lambda d: {**d, "count": 0},
        },
    )

    # Old v1 data
    old_data = {"name": "test", "_version": 1}

    # Upgrade to v2
    upgraded = schema.upgrade(1, old_data)
    assert upgraded["count"] == 0

    # Parse upgraded data
    value = schema.parse(upgraded)
    assert isinstance(value, SimpleV2)
    assert value.count == 0
    print("✓ Schema migration")


def test_crystal_from_datum() -> None:
    """Test crystallizing datums."""
    schema = Schema(name="test.simple", version=1, contract=SimpleV1)
    datum = Datum.create({"name": "test"})

    crystal = Crystal.from_datum(datum, schema)

    assert crystal.value.name == "test"
    assert crystal.datum.data["name"] == "test"
    assert crystal.meta.schema_name == "test.simple"
    assert crystal.meta.schema_version == 1
    print("✓ Crystal from datum")


def test_crystal_create() -> None:
    """Test creating crystals from typed values."""
    schema = Schema(name="test.simple", version=1, contract=SimpleV1)
    value = SimpleV1(name="test")

    crystal = Crystal.create(value, schema, author="test")

    assert crystal.value == value
    assert crystal.datum.author == "test"
    assert crystal.datum.data["name"] == "test"
    print("✓ Crystal create")


def test_crystal_upgrade() -> None:
    """Test lazy schema upgrades during crystallization."""
    schema = Schema(
        name="test.simple",
        version=2,
        contract=SimpleV2,
        migrations={
            1: lambda d: {**d, "count": 0},
        },
    )

    # Old v1 datum
    datum = Datum.create(
        {
            "name": "old",
            "_schema": "test.simple",
            "_version": 1,
        }
    )

    # Crystallize with v2 schema (auto-upgrades)
    crystal = Crystal.from_datum(datum, schema)

    assert isinstance(crystal.value, SimpleV2)
    assert crystal.value.name == "old"
    assert crystal.value.count == 0
    assert crystal.was_upgraded()
    assert crystal.meta.crystallized_from == datum.id
    print("✓ Crystal upgrade")


def test_query_filtering() -> None:
    """Test query filtering logic."""
    datums = [
        Datum.create(
            {"name": "a"},
            tags={"test", "important"},
            author="alice",
        ),
        Datum.create(
            {"name": "b"},
            tags={"test"},
            author="bob",
        ),
        Datum.create(
            {"name": "c"},
            tags={"important"},
            author="alice",
        ),
    ]

    # Filter by tags
    q1 = Query(tags=frozenset({"important"}))
    matches = [d for d in datums if q1.matches_datum(d)]
    assert len(matches) == 2
    assert all("important" in d.tags for d in matches)

    # Filter by author
    q2 = Query(author="alice")
    matches = [d for d in datums if q2.matches_datum(d)]
    assert len(matches) == 2
    assert all(d.author == "alice" for d in matches)

    # Compound filter
    q3 = Query(tags=frozenset({"important"}), author="alice")
    matches = [d for d in datums if q3.matches_datum(d)]
    assert len(matches) == 2  # Both 'a' and 'c' match
    assert {d.data["name"] for d in matches} == {"a", "c"}

    print("✓ Query filtering")


def test_query_fluent_api() -> None:
    """Test query builder pattern."""
    q = (
        Query()
        .with_schema("test.simple")
        .with_tags("important", "urgent")
        .with_limit(10)
        .next_page()
    )

    assert q.schema == "test.simple"
    assert q.tags == frozenset({"important", "urgent"})
    assert q.limit == 10
    assert q.offset == 10  # next_page incremented
    print("✓ Query fluent API")


def test_end_to_end() -> None:
    """Test complete end-to-end workflow."""
    # Define versioned schemas
    @dataclass(frozen=True)
    class MarkV1:
        action: str
        reasoning: str

    @dataclass(frozen=True)
    class MarkV2:
        action: str
        reasoning: str
        tags: tuple[str, ...] = ()

    schema_v1 = Schema(
        name="witness.mark",
        version=1,
        contract=MarkV1,
    )

    schema_v2 = Schema(
        name="witness.mark",
        version=2,
        contract=MarkV2,
        migrations={
            1: lambda d: {**d, "tags": ()},
        },
    )

    # Create v1 datum
    datum_v1 = Datum.create(
        {
            "action": "test",
            "reasoning": "example",
            "_schema": "witness.mark",
            "_version": 1,
        },
        author="claude",
    )

    # Crystallize with v1 schema
    crystal_v1 = Crystal.from_datum(datum_v1, schema_v1)
    assert isinstance(crystal_v1.value, MarkV1)
    assert not crystal_v1.was_upgraded()

    # Crystallize same datum with v2 schema (upgrades)
    crystal_v2 = Crystal.from_datum(datum_v1, schema_v2)
    assert isinstance(crystal_v2.value, MarkV2)
    assert crystal_v2.value.tags == ()
    assert crystal_v2.was_upgraded()

    # Create new v2 datum
    datum_v2 = Datum.create(
        schema_v2.to_dict(
            MarkV2(
                action="new",
                reasoning="example",
                tags=("important",),
            )
        ),
        author="kent",
    )

    # Query both datums
    q = Query(schema="witness.mark")
    all_datums = [datum_v1, datum_v2]
    matches = [d for d in all_datums if q.matches_datum(d)]
    assert len(matches) == 2

    print("✓ End-to-end workflow")


def run_all_tests() -> None:
    """Run all integration tests."""
    print("Running Crystal integration tests...\n")

    test_datum_immutability()
    test_schema_parsing()
    test_schema_migration()
    test_crystal_from_datum()
    test_crystal_create()
    test_crystal_upgrade()
    test_query_filtering()
    test_query_fluent_api()
    test_end_to_end()

    print("\n✓ All integration tests passed")


if __name__ == "__main__":
    run_all_tests()
