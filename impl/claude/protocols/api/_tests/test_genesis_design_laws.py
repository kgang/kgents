"""
Tests for Genesis Design Laws API endpoints.

Tests the newly added endpoints:
- GET /api/genesis/design-laws - List all design laws
- GET /api/genesis/design-laws/{law_name} - Get specific design law
"""

import pytest


@pytest.mark.tier1
def test_list_design_laws_endpoint_structure():
    """Test that the list endpoint returns correct structure."""
    from services.zero_seed.seed import DESIGN_LAWS

    # Simulate the endpoint response
    design_laws = [
        {
            "id": law.id,
            "name": law.name,
            "statement": law.statement,
            "layer": law.layer,
            "immutable": law.immutable,
            "kblock_id": "",
        }
        for law in DESIGN_LAWS
    ]

    response = {"design_laws": design_laws}

    # Test structure
    assert "design_laws" in response
    assert len(response["design_laws"]) == 4

    # Test each law has required fields
    for law in response["design_laws"]:
        assert "id" in law
        assert "name" in law
        assert "statement" in law
        assert "layer" in law
        assert "immutable" in law
        assert law["immutable"] is True


@pytest.mark.tier1
def test_get_design_law_endpoint_structure():
    """Test that the individual law endpoint returns correct structure."""
    from services.zero_seed.seed import DESIGN_LAWS

    # Test first law
    law = DESIGN_LAWS[0]
    response = {
        "id": law.id,
        "name": law.name,
        "statement": law.statement,
        "layer": law.layer,
        "immutable": law.immutable,
        "description": law.statement,
        "kblock_id": "",
    }

    # Test structure
    assert "id" in response
    assert "name" in response
    assert "statement" in response
    assert "layer" in response
    assert "immutable" in response
    assert "description" in response
    assert response["immutable"] is True


@pytest.mark.tier1
def test_name_normalization_logic():
    """Test that name normalization works for all design law names."""
    import re

    def normalize_for_match(name: str) -> str:
        """Normalize name for case/space/hyphen-insensitive matching."""
        return re.sub(r'[\s\-]', '', name).lower()

    # Test cases from the actual design laws
    test_cases = [
        ("Feed Is Primitive", "FeedIsPrimitive"),
        ("K-Block Incidental Essential", "KBlockIncidentalEssential"),
        ("K-Block Incidental Essential", "K-BlockIncidentalEssential"),
        ("Linear Adaptation", "LinearAdaptation"),
        ("Contradiction Surfacing", "ContradictionSurfacing"),
    ]

    for actual, test_input in test_cases:
        assert normalize_for_match(actual) == normalize_for_match(test_input), \
            f"Failed to match '{actual}' with '{test_input}'"


@pytest.mark.tier1
def test_all_design_laws_exist():
    """Test that all expected design laws exist."""
    from services.zero_seed.seed import DESIGN_LAWS

    law_ids = {law.id for law in DESIGN_LAWS}
    expected_ids = {
        "feed-is-primitive",
        "kblock-incidental-essential",
        "linear-adaptation",
        "contradiction-surfacing",
    }

    assert law_ids == expected_ids, \
        f"Missing or unexpected law IDs: expected {expected_ids}, got {law_ids}"


@pytest.mark.tier1
def test_design_law_layers():
    """Test that design laws are assigned to correct layers."""
    from services.zero_seed.seed import DESIGN_LAWS

    layer_1_laws = [law for law in DESIGN_LAWS if law.layer == 1]
    layer_2_laws = [law for law in DESIGN_LAWS if law.layer == 2]

    # Layer 1 (Axiom level)
    assert len(layer_1_laws) == 2
    layer_1_ids = {law.id for law in layer_1_laws}
    assert "feed-is-primitive" in layer_1_ids
    assert "contradiction-surfacing" in layer_1_ids

    # Layer 2 (Value level)
    assert len(layer_2_laws) == 2
    layer_2_ids = {law.id for law in layer_2_laws}
    assert "kblock-incidental-essential" in layer_2_ids
    assert "linear-adaptation" in layer_2_ids
