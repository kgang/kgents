"""
Tests for stance detection.

Tests the Four Stances: Genesis, Poiesis, Krisis, Therapeia.
"""

from __future__ import annotations

import pytest

from services.principles import (
    Stance,
    STANCE_SLICES,
    detect_stance,
    get_stance_slices,
    stance_from_aspect,
    validate_stance_transition,
    GENESIS_SIGNALS,
    POIESIS_SIGNALS,
    KRISIS_SIGNALS,
    THERAPEIA_SIGNALS,
)


# === Stance Enum Tests ===


def test_stance_values() -> None:
    """Stance enum has four values."""
    assert len(Stance) == 4
    assert Stance.GENESIS.value == "genesis"
    assert Stance.POIESIS.value == "poiesis"
    assert Stance.KRISIS.value == "krisis"
    assert Stance.THERAPEIA.value == "therapeia"


def test_stance_properties() -> None:
    """Stance properties are accessible."""
    assert Stance.GENESIS.greek_root  # Not empty
    assert Stance.GENESIS.motion == "Emergence"
    assert "?" in Stance.GENESIS.question


# === Stance Slices Tests ===


def test_stance_slices_coverage() -> None:
    """Every stance has slices defined."""
    for stance in Stance:
        assert stance in STANCE_SLICES
        assert len(STANCE_SLICES[stance]) > 0


def test_genesis_slices() -> None:
    """Genesis includes CONSTITUTION.md and meta.md."""
    slices = get_stance_slices(Stance.GENESIS)
    assert "CONSTITUTION.md" in slices
    assert "meta.md" in slices


def test_krisis_slices_minimal() -> None:
    """Krisis is minimal - just the constitution."""
    slices = get_stance_slices(Stance.KRISIS)
    assert "CONSTITUTION.md" in slices
    assert len(slices) == 1


def test_therapeia_includes_puppets() -> None:
    """Therapeia includes puppets for healing."""
    slices = get_stance_slices(Stance.THERAPEIA)
    assert "puppets.md" in slices


# === Detection Tests ===


def test_detect_defaults_to_genesis() -> None:
    """No context defaults to Genesis."""
    stance = detect_stance()
    assert stance == Stance.GENESIS


def test_detect_therapeia_signals() -> None:
    """Healing words trigger Therapeia."""
    stance = detect_stance(task="fix this broken agent")
    assert stance == Stance.THERAPEIA


def test_detect_krisis_signals() -> None:
    """Review words trigger Krisis."""
    stance = detect_stance(task="review this component")
    assert stance == Stance.KRISIS


def test_detect_poiesis_signals() -> None:
    """Building words trigger Poiesis."""
    stance = detect_stance(task="implement the new feature")
    assert stance == Stance.POIESIS


def test_detect_genesis_signals() -> None:
    """Starting words trigger Genesis."""
    stance = detect_stance(task="start a new project")
    assert stance == Stance.GENESIS


def test_therapeia_priority_over_poiesis() -> None:
    """Therapeia has priority when mixed signals."""
    # "fix" (therapeia) + "implement" (poiesis)
    stance = detect_stance(task="fix and implement this broken code")
    assert stance == Stance.THERAPEIA


# === Aspect-Based Detection ===


def test_stance_from_check_aspect() -> None:
    """check aspect implies Krisis."""
    stance = stance_from_aspect("check")
    assert stance == Stance.KRISIS


def test_stance_from_heal_aspect() -> None:
    """heal aspect implies Therapeia."""
    stance = stance_from_aspect("heal")
    assert stance == Stance.THERAPEIA


def test_stance_from_unknown_aspect() -> None:
    """Unknown aspect defaults to Genesis."""
    stance = stance_from_aspect("unknown")
    assert stance == Stance.GENESIS


# === Transition Validation ===


def test_genesis_to_poiesis_valid() -> None:
    """Genesis -> Poiesis is valid."""
    assert validate_stance_transition(Stance.GENESIS, Stance.POIESIS)


def test_poiesis_to_krisis_valid() -> None:
    """Poiesis -> Krisis is valid."""
    assert validate_stance_transition(Stance.POIESIS, Stance.KRISIS)


def test_krisis_to_therapeia_valid() -> None:
    """Krisis -> Therapeia is valid (on failure)."""
    assert validate_stance_transition(Stance.KRISIS, Stance.THERAPEIA)


def test_krisis_to_poiesis_valid() -> None:
    """Krisis -> Poiesis is valid (on success/refine)."""
    assert validate_stance_transition(Stance.KRISIS, Stance.POIESIS)


def test_therapeia_to_poiesis_valid() -> None:
    """Therapeia -> Poiesis is valid (healed)."""
    assert validate_stance_transition(Stance.THERAPEIA, Stance.POIESIS)


def test_genesis_to_krisis_invalid() -> None:
    """Genesis -> Krisis is invalid (skip Poiesis)."""
    assert not validate_stance_transition(Stance.GENESIS, Stance.KRISIS)


def test_therapeia_to_genesis_invalid() -> None:
    """Therapeia -> Genesis is invalid."""
    assert not validate_stance_transition(Stance.THERAPEIA, Stance.GENESIS)


# === Signal Coverage ===


def test_signal_sets_not_empty() -> None:
    """All signal sets have content."""
    assert len(GENESIS_SIGNALS) > 0
    assert len(POIESIS_SIGNALS) > 0
    assert len(KRISIS_SIGNALS) > 0
    assert len(THERAPEIA_SIGNALS) > 0


def test_signal_sets_distinct() -> None:
    """Signal sets have minimal overlap."""
    # Some overlap is okay, but shouldn't be complete overlap
    assert GENESIS_SIGNALS != POIESIS_SIGNALS
    assert KRISIS_SIGNALS != THERAPEIA_SIGNALS
