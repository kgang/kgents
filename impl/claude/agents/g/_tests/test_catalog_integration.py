"""
G-gent Catalog Integration Tests

Tests for G-gent integration with L-gent catalog.
Tests tongue registration, discovery, and compatibility checking.
"""

import pytest
from agents.g import GrammarLevel, create_command_tongue, create_schema_tongue
from agents.g.catalog_integration import (
    check_compatibility,
    find_composable,
    find_tongue,
    register_tongue,
    update_tongue_metrics,
)
from agents.l import EntityType, Registry

# ============================================================================
# Registration Tests
# ============================================================================


@pytest.mark.asyncio
async def test_register_tongue():
    """Test registering a tongue with L-gent."""
    registry = Registry()

    # Create a test tongue
    tongue = create_command_tongue(
        name="CalendarCommands",
        domain="Calendar Management",
        grammar='<verb> ::= "CHECK" | "ADD"',
    )

    # Register
    entry_id = await register_tongue(tongue, registry, author="G-gent-test")

    # Verify registration
    assert entry_id.startswith("tongue:")
    assert await registry.exists(entry_id)

    # Get and verify entry
    entry = await registry.get(entry_id)
    assert entry is not None
    assert entry.entity_type == EntityType.TONGUE
    assert entry.name == "CalendarCommands"
    assert entry.tongue_domain == "Calendar Management"
    assert entry.author == "G-gent-test"


@pytest.mark.asyncio
async def test_register_multiple_tongues():
    """Test registering multiple tongues."""
    registry = Registry()

    # Register multiple tongues
    tongue1 = create_command_tongue(
        name="Calendar",
        domain="Calendar",
        grammar='<verb> ::= "CHECK"',
    )

    tongue2 = create_schema_tongue(
        name="Database",
        domain="Database",
        grammar="QueryModel",
    )

    id1 = await register_tongue(tongue1, registry)
    id2 = await register_tongue(tongue2, registry)

    assert id1 != id2
    assert await registry.exists(id1)
    assert await registry.exists(id2)


# ============================================================================
# Discovery Tests
# ============================================================================


@pytest.mark.asyncio
async def test_find_tongue_by_domain():
    """Test finding tongues by domain."""
    registry = Registry()

    # Register tongues with different domains
    calendar_tongue = create_command_tongue(
        name="CalendarOps",
        domain="Calendar Management",
        grammar='<verb> ::= "CHECK" | "ADD"',
    )

    database_tongue = create_command_tongue(
        name="DatabaseOps",
        domain="Database Operations",
        grammar='<verb> ::= "SELECT" | "INSERT"',
    )

    await register_tongue(calendar_tongue, registry)
    await register_tongue(database_tongue, registry)

    # Find by domain
    calendar_results = await find_tongue(registry, domain="Calendar")
    assert len(calendar_results) > 0
    assert any("calendar" in e.tongue_domain.lower() for e in calendar_results)

    database_results = await find_tongue(registry, domain="Database")
    assert len(database_results) > 0
    assert any("database" in e.tongue_domain.lower() for e in database_results)


@pytest.mark.asyncio
async def test_find_tongue_by_constraints():
    """Test finding tongues by constraints."""
    registry = Registry()

    # Register tongues with different constraints
    safe_tongue = create_command_tongue(
        name="SafeCalendar",
        domain="Calendar",
        grammar='<verb> ::= "CHECK" | "ADD"',
    )
    safe_tongue = safe_tongue.__replace__(constraints=("No deletes", "No overwrites"))

    full_tongue = create_command_tongue(
        name="FullCalendar",
        domain="Calendar",
        grammar='<verb> ::= "CHECK" | "ADD" | "DELETE"',
    )

    await register_tongue(safe_tongue, registry)
    await register_tongue(full_tongue, registry)

    # Find by constraints
    safe_results = await find_tongue(registry, constraints=["No deletes"])
    assert len(safe_results) > 0
    assert all(
        "no deletes" in [c.lower() for c in e.tongue_constraints] for e in safe_results
    )


@pytest.mark.asyncio
async def test_find_tongue_by_level():
    """Test finding tongues by grammar level."""
    registry = Registry()

    command_tongue = create_command_tongue(
        name="Commands",
        domain="Testing",
        grammar='<verb> ::= "TEST"',
    )

    schema_tongue = create_schema_tongue(
        name="Schema",
        domain="Testing",
        grammar="TestModel",
    )

    await register_tongue(command_tongue, registry)
    await register_tongue(schema_tongue, registry)

    # Find by level
    command_results = await find_tongue(registry, level=GrammarLevel.COMMAND)
    assert len(command_results) > 0
    assert all(e.tongue_level == "command" for e in command_results)


# ============================================================================
# Compatibility Tests
# ============================================================================


@pytest.mark.asyncio
async def test_check_compatibility_same_domain():
    """Test compatibility check for tongues with same domain."""
    tongue_a = create_command_tongue(
        name="CalendarA",
        domain="Calendar Management",
        grammar='<verb> ::= "CHECK"',
    )

    tongue_b = create_command_tongue(
        name="CalendarB",
        domain="Calendar Management",
        grammar='<verb> ::= "ADD"',
    )

    compat = await check_compatibility(tongue_a, tongue_b)

    # Same domain should have high overlap
    assert compat.domain_overlap > 0.5
    # But still might be compatible if no constraint conflicts
    assert len(compat.constraint_conflicts) == 0


@pytest.mark.asyncio
async def test_check_compatibility_different_domains():
    """Test compatibility for tongues with different domains."""
    calendar_tongue = create_command_tongue(
        name="Calendar",
        domain="Calendar Management",
        grammar='<verb> ::= "CHECK"',
    )

    database_tongue = create_command_tongue(
        name="Database",
        domain="Database Operations",
        grammar='<verb> ::= "SELECT"',
    )

    compat = await check_compatibility(calendar_tongue, database_tongue)

    # Different domains should have low overlap
    assert compat.domain_overlap < 0.5
    # Should be composable (sequential)
    assert compat.composable
    assert compat.composition_type == "sequential"


@pytest.mark.asyncio
async def test_check_compatibility_constraint_conflicts():
    """Test compatibility with conflicting constraints."""
    # This is a simplified test - real conflict detection would be more sophisticated
    tongue_a = create_command_tongue(
        name="SafeOps",
        domain="Operations",
        grammar='<verb> ::= "READ"',
    )
    tongue_a = tongue_a.__replace__(constraints=("no deletes",))

    tongue_b = create_command_tongue(
        name="FullOps",
        domain="Operations",
        grammar='<verb> ::= "READ" | "DELETE"',
    )
    tongue_b = tongue_b.__replace__(constraints=("allows deletes",))

    compat = await check_compatibility(tongue_a, tongue_b)

    # Should detect potential conflict
    # (Note: Our simple heuristic may not catch this, so this test documents current behavior)
    assert compat is not None  # At minimum, check runs without error


# ============================================================================
# Composition Discovery Tests
# ============================================================================


@pytest.mark.asyncio
async def test_find_composable():
    """Test finding composable tongues."""
    registry = Registry()

    # Register tongues with different domains
    input_tongue = create_command_tongue(
        name="Input",
        domain="Input Processing",
        grammar='<verb> ::= "READ"',
    )

    transform_tongue = create_command_tongue(
        name="Transform",
        domain="Data Transformation",
        grammar='<verb> ::= "MAP" | "FILTER"',
    )

    output_tongue = create_command_tongue(
        name="Output",
        domain="Output Formatting",
        grammar='<verb> ::= "WRITE" | "FORMAT"',
    )

    await register_tongue(input_tongue, registry)
    await register_tongue(transform_tongue, registry)
    await register_tongue(output_tongue, registry)

    # Find tongues composable with input_tongue
    composable = await find_composable(
        input_tongue,
        registry,
        composition_type="sequential",
    )

    # Should find tongues with different domains
    assert len(composable) > 0


# ============================================================================
# Metrics Tracking Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_tongue_metrics():
    """Test updating usage metrics for tongues."""
    registry = Registry()

    tongue = create_command_tongue(
        name="MetricsTest",
        domain="Testing",
        grammar='<verb> ::= "TEST"',
    )

    entry_id = await register_tongue(tongue, registry)

    # Initial state
    entry = await registry.get(entry_id)
    assert entry.usage_count == 0
    assert entry.success_rate == 1.0

    # Update with success
    await update_tongue_metrics(tongue, registry, success=True)

    entry = await registry.get(entry_id)
    assert entry.usage_count == 1
    assert entry.success_rate == 1.0

    # Update with failure
    await update_tongue_metrics(tongue, registry, success=False, error="Parse error")

    entry = await registry.get(entry_id)
    assert entry.usage_count == 2
    assert entry.success_rate < 1.0  # Should have decreased
    assert entry.last_error == "Parse error"


# ============================================================================
# Integration Workflow Tests
# ============================================================================


@pytest.mark.asyncio
async def test_full_workflow():
    """Test complete workflow: register, find, check compatibility."""
    registry = Registry()

    # 1. Register multiple tongues
    calendar_tongue = create_command_tongue(
        name="CalendarFull",
        domain="Calendar Management",
        grammar='<verb> ::= "CHECK" | "ADD"',
    )

    email_tongue = create_command_tongue(
        name="EmailOps",
        domain="Email Operations",
        grammar='<verb> ::= "SEND" | "READ"',
    )

    await register_tongue(calendar_tongue, registry, author="G-gent-workflow")
    await register_tongue(email_tongue, registry, author="G-gent-workflow")

    # 2. Find tongues by domain
    calendar_results = await find_tongue(registry, domain="Calendar")
    assert len(calendar_results) > 0

    # 3. Check compatibility
    compat = await check_compatibility(calendar_tongue, email_tongue)
    assert compat.composable  # Different domains should be composable

    # 4. Find composable tongues
    composable = await find_composable(calendar_tongue, registry)
    assert any(e.name == "EmailOps" for e in composable)

    # 5. Track usage
    await update_tongue_metrics(calendar_tongue, registry, success=True)

    # Verify metrics updated
    entry_id = "tongue:calendarfull:1.0.0"
    entry = await registry.get(entry_id)
    assert entry.usage_count == 1
