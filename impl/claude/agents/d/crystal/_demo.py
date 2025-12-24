"""
Demo script showcasing the Crystal primitives.

This demonstrates the full lifecycle:
1. Define a versioned schema contract
2. Create raw datums
3. Crystallize into typed values
4. Evolve schema with migrations
5. Query declaratively
"""

from dataclasses import dataclass
from datetime import datetime, UTC

from .datum import Datum
from .crystal import Crystal
from .schema import Schema
from .query import Query


# Version 1: Initial witness mark
@dataclass(frozen=True)
class MarkV1:
    action: str
    reasoning: str


# Version 2: Added tags
@dataclass(frozen=True)
class MarkV2:
    action: str
    reasoning: str
    tags: tuple[str, ...] = ()


# Version 3: Added principles
@dataclass(frozen=True)
class MarkV3:
    action: str
    reasoning: str
    tags: tuple[str, ...] = ()
    principles: tuple[str, ...] = ()


def demo_basic_usage() -> None:
    """Demonstrate basic Datum → Crystal flow."""
    print("=== Basic Usage ===\n")

    # Create a schema
    schema_v1 = Schema(
        name="witness.mark",
        version=1,
        contract=MarkV1,
    )

    # Create a datum (schema-free)
    datum = Datum.create(
        data={
            "action": "Implemented Crystal primitives",
            "reasoning": "Foundation for unified data architecture",
        },
        tags={"witness", "foundation"},
        author="claude",
    )

    print(f"Datum ID: {datum.id}")
    print(f"Created: {datum.created_at}")
    print(f"Tags: {datum.tags}")
    print(f"Data: {datum.data}\n")

    # Crystallize into typed value
    crystal = Crystal.from_datum(datum, schema_v1)

    print(f"Crystal schema: {crystal.meta.schema_name} v{crystal.meta.schema_version}")
    print(f"Typed value: {crystal.value}")
    print(f"  action: {crystal.value.action}")
    print(f"  reasoning: {crystal.value.reasoning}\n")


def demo_schema_evolution() -> None:
    """Demonstrate schema versioning and migration."""
    print("=== Schema Evolution ===\n")

    # Define schemas with migrations
    schema_v3 = Schema(
        name="witness.mark",
        version=3,
        contract=MarkV3,
        migrations={
            1: lambda d: {**d, "tags": ()},           # v1 -> v2
            2: lambda d: {**d, "principles": ()},     # v2 -> v3
        },
    )

    # Create old-version datum (v1)
    old_datum = Datum.create(
        data={
            "action": "Legacy mark",
            "reasoning": "Created before tags existed",
            "_schema": "witness.mark",
            "_version": 1,
        },
        author="system",
    )

    print(f"Old datum version: {old_datum.data.get('_version')}")
    print(f"Has tags field: {'tags' in old_datum.data}")
    print(f"Has principles field: {'principles' in old_datum.data}\n")

    # Crystallize with v3 schema (auto-upgrades)
    crystal_v3 = Crystal.from_datum(old_datum, schema_v3)

    print(f"Crystal version: {crystal_v3.meta.schema_version}")
    print(f"Was upgraded: {crystal_v3.was_upgraded()}")
    print(f"Crystallized from: {crystal_v3.meta.crystallized_from}")
    print(f"Typed value: {crystal_v3.value}")
    print(f"  tags: {crystal_v3.value.tags}")
    print(f"  principles: {crystal_v3.value.principles}\n")


def demo_query_api() -> None:
    """Demonstrate declarative query API."""
    print("=== Query API ===\n")

    # Create sample datums
    datums = [
        Datum.create(
            {"action": "First mark", "reasoning": "Test"},
            tags={"eureka", "test"},
            author="claude",
        ),
        Datum.create(
            {"action": "Second mark", "reasoning": "Example"},
            tags={"test"},
            author="kent",
        ),
        Datum.create(
            {"action": "Third mark", "reasoning": "Demo"},
            tags={"eureka", "witness"},
            author="claude",
        ),
    ]

    # Query by tags
    q1 = Query(tags=frozenset(["eureka"]))
    matches = [d for d in datums if q1.matches_datum(d)]
    print(f"Query: tags contain 'eureka'")
    print(f"Matches: {len(matches)} datums")
    for d in matches:
        print(f"  - {d.data['action']}")
    print()

    # Query by author
    q2 = Query(author="claude")
    matches = [d for d in datums if q2.matches_datum(d)]
    print(f"Query: author = 'claude'")
    print(f"Matches: {len(matches)} datums")
    for d in matches:
        print(f"  - {d.data['action']}")
    print()

    # Compound query
    q3 = Query(
        tags=frozenset(["eureka"]),
        author="claude",
    )
    matches = [d for d in datums if q3.matches_datum(d)]
    print(f"Query: tags contain 'eureka' AND author = 'claude'")
    print(f"Matches: {len(matches)} datums")
    for d in matches:
        print(f"  - {d.data['action']}")
    print()

    # Fluent API
    q4 = (
        Query()
        .with_tags("eureka")
        .with_schema("witness.mark")
        .with_limit(10)
    )
    print(f"Fluent query: {q4}")


def demo_immutability() -> None:
    """Demonstrate immutable semantics."""
    print("\n=== Immutability ===\n")

    datum = Datum.create({"test": "value"}, tags={"initial"})
    print(f"Original tags: {datum.tags}")

    # Create new datum with additional tags
    datum2 = datum.with_tags("added")
    print(f"After with_tags: {datum2.tags}")
    print(f"Original unchanged: {datum.tags}")
    print(f"Different objects: {datum is not datum2}\n")


if __name__ == "__main__":
    demo_basic_usage()
    demo_schema_evolution()
    demo_query_api()
    demo_immutability()

    print("=== All demos complete ===")
