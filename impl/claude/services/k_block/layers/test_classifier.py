"""
Tests for Zero Seed Layer Classifier

Run: uv run python -m pytest services/k_block/layers/test_classifier.py -v
"""

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from agents.d.crystal import Crystal, CrystalMeta
from agents.d.crystal.schema import Schema
from agents.d.galois import GaloisLossComputer
from services.k_block.layers.classifier import (
    LAYER_NAMES,
    LAYER_THRESHOLDS,
    classify_crystal,
    classify_layer,
    get_layer_confidence,
    get_layer_name,
)


class MockGalois:
    """Mock Galois computer for testing."""

    def __init__(self, loss_value: float):
        self.loss_value = loss_value

    async def compute(self, content: str) -> float:
        return self.loss_value


# Test Fixtures


@dataclass(frozen=True)
class TestMark:
    action: str
    reasoning: str


TEST_SCHEMA = Schema(
    name="test.mark",
    version=1,
    contract=TestMark,
)


# CrystalMeta Tests


def test_crystal_meta_default_fields():
    """Test CrystalMeta has new fields with default None."""
    meta = CrystalMeta("test", 1, datetime.now(UTC))
    assert meta.layer is None
    assert meta.galois_loss is None
    assert meta.proof_id is None


def test_crystal_meta_with_layer():
    """Test CrystalMeta with layer specified."""
    meta = CrystalMeta(
        "test",
        1,
        datetime.now(UTC),
        layer=3,
        galois_loss=0.25,
        proof_id="proof123",
    )
    assert meta.layer == 3
    assert meta.galois_loss == 0.25
    assert meta.proof_id == "proof123"


def test_requires_proof_none_layer():
    """Test requires_proof returns False when layer is None."""
    meta = CrystalMeta("test", 1, datetime.now(UTC))
    assert meta.requires_proof is False


def test_requires_proof_layer_1_2():
    """Test requires_proof returns False for L1-L2 (axiomatic layers)."""
    meta1 = CrystalMeta("test", 1, datetime.now(UTC), layer=1)
    meta2 = CrystalMeta("test", 1, datetime.now(UTC), layer=2)
    assert meta1.requires_proof is False
    assert meta2.requires_proof is False


def test_requires_proof_layer_3_plus():
    """Test requires_proof returns True for L3+ (derivational layers)."""
    for layer in [3, 4, 5, 6, 7]:
        meta = CrystalMeta("test", 1, datetime.now(UTC), layer=layer)
        assert meta.requires_proof is True, f"L{layer} should require proof"


# Classifier Tests


@pytest.mark.asyncio
async def test_classify_layer_without_galois():
    """Test classify_layer defaults to L4 without Galois."""
    layer = await classify_layer("Any content")
    assert layer == 4


@pytest.mark.asyncio
async def test_classify_layer_thresholds():
    """Test classify_layer respects threshold boundaries."""
    test_cases = [
        (0.03, 1),  # L1: Axiom
        (0.12, 2),  # L2: Value
        (0.25, 3),  # L3: Goal
        (0.40, 4),  # L4: Specification
        (0.55, 5),  # L5: Action
        (0.70, 6),  # L6: Reflection
        (0.90, 7),  # L7: Representation
    ]

    for loss, expected_layer in test_cases:
        galois = MockGalois(loss)
        layer = await classify_layer("test", galois)
        assert layer == expected_layer, f"Loss {loss} should map to L{expected_layer}"


@pytest.mark.asyncio
async def test_classify_crystal():
    """Test classify_crystal extracts content and classifies."""
    mark = TestMark(action="Test action", reasoning="Test reasoning")
    crystal = Crystal.create(mark, TEST_SCHEMA)

    galois = MockGalois(0.25)  # Should be L3
    layer = await classify_crystal(crystal, galois)
    assert layer == 3


def test_layer_names():
    """Test get_layer_name returns correct names."""
    expected = {
        1: "Axiom",
        2: "Value",
        3: "Goal",
        4: "Specification",
        5: "Action",
        6: "Reflection",
        7: "Representation",
    }

    for layer_num, expected_name in expected.items():
        assert get_layer_name(layer_num) == expected_name


def test_layer_confidence():
    """Test get_layer_confidence returns correct defaults."""
    expected = {
        1: 1.00,
        2: 0.95,
        3: 0.90,
        4: 0.85,
        5: 0.80,
        6: 0.75,
        7: 0.70,
    }

    for layer_num, expected_conf in expected.items():
        assert get_layer_confidence(layer_num) == expected_conf


def test_layer_thresholds_structure():
    """Test LAYER_THRESHOLDS has correct structure."""
    assert len(LAYER_THRESHOLDS) == 7

    # Should be monotonically increasing
    prev_threshold = 0.0
    for threshold, layer in LAYER_THRESHOLDS:
        assert threshold > prev_threshold
        assert 1 <= layer <= 7
        prev_threshold = threshold


# Integration Tests


@pytest.mark.asyncio
async def test_full_integration():
    """Test full integration: Galois → Classifier → CrystalMeta."""
    # Create a crystal
    mark = TestMark(action="Validated axiom", reasoning="Self-evident truth")
    crystal = Crystal.create(mark, TEST_SCHEMA)

    # Classify with real Galois
    galois = GaloisLossComputer(metric="token")
    layer = await classify_crystal(crystal, galois)

    # Create CrystalMeta with classification
    loss = await galois.compute(f"{mark.action}. {mark.reasoning}")
    meta = CrystalMeta(
        schema_name=TEST_SCHEMA.name,
        schema_version=TEST_SCHEMA.version,
        created_at=datetime.now(UTC),
        layer=layer,
        galois_loss=loss,
    )

    # Verify integration
    assert meta.layer is not None
    assert meta.galois_loss is not None
    assert isinstance(meta.layer, int)
    assert 1 <= meta.layer <= 7
    assert 0.0 <= meta.galois_loss <= 1.0
