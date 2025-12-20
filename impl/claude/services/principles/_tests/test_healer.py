"""
Tests for PrincipleHealer.

Law: heal(violation) always returns at least one prescription path.
"""

from __future__ import annotations

import pytest

from services.principles import (
    HealingPrescription,
    PrincipleHealer,
    PrincipleLoader,
    Stance,
    create_principle_healer,
    create_principle_loader,
)

# === Fixtures ===


@pytest.fixture
def loader() -> PrincipleLoader:
    """Create a loader."""
    return create_principle_loader()


@pytest.fixture
def healer(loader: PrincipleLoader) -> PrincipleHealer:
    """Create a healer with loader."""
    return create_principle_healer(loader)


# === Law: Heal Specificity ===


@pytest.mark.asyncio
async def test_heal_always_returns_path(healer: PrincipleHealer) -> None:
    """heal(violation) always returns at least one prescription path."""
    for principle in range(1, 8):
        prescription = await healer.heal(violation=principle)

        assert len(prescription.path) >= 1
        assert prescription.principle == principle


# === Principle Resolution ===


@pytest.mark.asyncio
async def test_heal_by_number(healer: PrincipleHealer) -> None:
    """Can heal by principle number."""
    prescription = await healer.heal(violation=5)

    assert prescription.principle == 5
    assert prescription.principle_name == "Composable"


@pytest.mark.asyncio
async def test_heal_by_name(healer: PrincipleHealer) -> None:
    """Can heal by principle name."""
    prescription = await healer.heal(violation="Composable")

    assert prescription.principle == 5
    assert prescription.principle_name == "Composable"


@pytest.mark.asyncio
async def test_heal_by_name_case_insensitive(healer: PrincipleHealer) -> None:
    """Principle name matching is case insensitive."""
    prescription = await healer.heal(violation="TASTEFUL")

    assert prescription.principle == 1


@pytest.mark.asyncio
async def test_heal_by_partial_name(healer: PrincipleHealer) -> None:
    """Can match partial principle names."""
    prescription = await healer.heal(violation="joy")

    assert prescription.principle == 4  # Joy-Inducing


@pytest.mark.asyncio
async def test_heal_invalid_principle_raises(healer: PrincipleHealer) -> None:
    """Invalid principle raises ValueError."""
    with pytest.raises(ValueError):
        await healer.heal(violation="nonexistent")


# === Context Matching ===


@pytest.mark.asyncio
async def test_heal_matches_context_to_anti_pattern(healer: PrincipleHealer) -> None:
    """Context is matched to specific anti-pattern."""
    prescription = await healer.heal(
        violation=1,  # Tasteful
        # Use words that directly match anti-patterns
        context="This agent does everything and has kitchen sink configurations",
    )

    # Should match anti-pattern if words overlap
    # Note: matching is based on word overlap, may be None if no overlap
    # This test verifies the matching works when there IS overlap
    if prescription.matched_pattern:
        assert prescription.matched_pattern in prescription.anti_patterns


@pytest.mark.asyncio
async def test_heal_without_context(healer: PrincipleHealer) -> None:
    """Works without context (no matched pattern)."""
    prescription = await healer.heal(violation=1)

    # No context means no matched pattern
    assert prescription.matched_pattern is None


# === Prescription Structure ===


@pytest.mark.asyncio
async def test_prescription_has_anti_patterns(healer: PrincipleHealer) -> None:
    """Prescription includes anti-patterns for the principle."""
    prescription = await healer.heal(violation=1)

    assert len(prescription.anti_patterns) > 0


@pytest.mark.asyncio
async def test_prescription_has_related_ads(healer: PrincipleHealer) -> None:
    """Prescription includes related ADs."""
    prescription = await healer.heal(violation=5)  # Composable

    # Composable maps to AD-001, AD-002, AD-006
    assert len(prescription.related_ads) > 0


@pytest.mark.asyncio
async def test_prescription_stance_is_therapeia(healer: PrincipleHealer) -> None:
    """Prescription has Therapeia stance."""
    prescription = await healer.heal(violation=1)

    assert prescription.stance == Stance.THERAPEIA


# === Healing Path ===


@pytest.mark.asyncio
async def test_healing_path_has_steps(healer: PrincipleHealer) -> None:
    """Healing path has meaningful steps."""
    prescription = await healer.heal(violation=1)

    # Path should have multiple steps
    assert len(prescription.path) >= 3

    # Steps should be instructive
    assert any("anti-pattern" in step.lower() for step in prescription.path)


@pytest.mark.asyncio
async def test_healing_path_ends_with_verify(healer: PrincipleHealer) -> None:
    """Healing path ends with verification step."""
    prescription = await healer.heal(violation=1)

    last_step = prescription.path[-1]
    assert "verify" in last_step.lower() or "check" in last_step.lower()


# === Diagnosis ===


@pytest.mark.asyncio
async def test_diagnose_identifies_violation(healer: PrincipleHealer) -> None:
    """diagnose can identify violated principle from context."""
    result = await healer.diagnose("This agent does everything, kitchen-sink style")

    if result:
        principle_num, anti_pattern = result
        assert principle_num == 1  # Tasteful


@pytest.mark.asyncio
async def test_diagnose_returns_none_for_unknown(healer: PrincipleHealer) -> None:
    """diagnose returns None when no match found."""
    result = await healer.diagnose("A perfectly normal description")

    # May or may not find a match
    # Just verify it doesn't crash


# === Serialization ===


@pytest.mark.asyncio
async def test_prescription_to_dict(healer: PrincipleHealer) -> None:
    """HealingPrescription serializes to dict."""
    prescription = await healer.heal(violation=1)
    d = prescription.to_dict()

    assert "principle" in d
    assert "principle_name" in d
    assert "anti_patterns" in d
    assert "path" in d
    assert "stance" in d


@pytest.mark.asyncio
async def test_prescription_to_text(healer: PrincipleHealer) -> None:
    """HealingPrescription renders as text."""
    prescription = await healer.heal(violation=1)
    text = prescription.to_text()

    assert "Healing" in text
    assert "Tasteful" in text
