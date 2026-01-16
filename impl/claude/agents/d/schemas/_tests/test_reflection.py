"""
Tests for Layer 6-7 Reflection and Interpretation crystals.
"""

from datetime import UTC, datetime

import pytest

from agents.d.schemas.proof import GaloisWitnessedProof
from agents.d.schemas.reflection import InterpretationCrystal, ReflectionCrystal


def test_reflection_crystal_creation():
    """Test creating a reflection crystal."""
    proof = GaloisWitnessedProof(
        data="Test data", warrant="Test warrant", claim="Test claim", backing="Test backing"
    )

    reflection = ReflectionCrystal(
        id="r1",
        target_ids=("t1", "t2"),
        reflection_type="synthesis",
        insight="Combined insights from artifacts t1 and t2",
        recommendations=("rec1", "rec2"),
        derived_from=("d1",),
        proof=proof,
    )

    assert reflection.id == "r1"
    assert reflection.layer == 6
    assert reflection.reflection_type == "synthesis"
    assert len(reflection.target_ids) == 2
    assert len(reflection.recommendations) == 2


def test_reflection_crystal_serialization():
    """Test reflection crystal to_dict and from_dict."""
    proof = GaloisWitnessedProof(
        data="Test data", warrant="Test warrant", claim="Test claim", backing="Test backing"
    )

    reflection = ReflectionCrystal(
        id="r1",
        target_ids=("t1", "t2"),
        reflection_type="comparison",
        insight="Artifact t1 differs from t2 in approach",
        recommendations=("Consider hybrid approach",),
        derived_from=("d1", "d2"),
        proof=proof,
    )

    # Serialize
    data = reflection.to_dict()

    # Verify structure
    assert data["id"] == "r1"
    assert data["layer"] == 6
    assert data["reflection_type"] == "comparison"
    assert isinstance(data["target_ids"], list)
    assert isinstance(data["proof"], dict)

    # Deserialize
    reflection2 = ReflectionCrystal.from_dict(data)

    assert reflection2.id == reflection.id
    assert reflection2.layer == reflection.layer
    assert reflection2.target_ids == reflection.target_ids
    assert reflection2.insight == reflection.insight


def test_interpretation_crystal_creation():
    """Test creating an interpretation crystal."""
    now = datetime.now(UTC)
    proof = GaloisWitnessedProof(
        data="Historical data",
        warrant="Trend analysis",
        claim="Increasing complexity",
        backing="Code metrics over 6 months",
    )

    interp = InterpretationCrystal(
        id="i1",
        artifact_pattern="impl/**/*.py",
        time_range=(now, now),
        insight_type="trend",
        content="Code complexity increasing over time",
        confidence=0.85,
        supporting_ids=("s1", "s2", "s3"),
        proof=proof,
    )

    assert interp.id == "i1"
    assert interp.layer == 7
    assert interp.insight_type == "trend"
    assert interp.confidence == 0.85
    assert len(interp.supporting_ids) == 3


def test_interpretation_crystal_serialization():
    """Test interpretation crystal to_dict and from_dict."""
    now = datetime.now(UTC)
    later = datetime.fromtimestamp(now.timestamp() + 3600, UTC)

    proof = GaloisWitnessedProof(
        data="Pattern data",
        warrant="Recurring structure",
        claim="Common pattern identified",
        backing="Analysis of 50+ files",
    )

    interp = InterpretationCrystal(
        id="i1",
        artifact_pattern="impl/claude/agents/**/*.py",
        time_range=(now, later),
        insight_type="pattern",
        content="All agents follow polynomial pattern",
        confidence=0.95,
        supporting_ids=("s1", "s2"),
        proof=proof,
    )

    # Serialize
    data = interp.to_dict()

    # Verify structure
    assert data["id"] == "i1"
    assert data["layer"] == 7
    assert data["insight_type"] == "pattern"
    assert isinstance(data["time_range"], list)
    assert len(data["time_range"]) == 2
    assert isinstance(data["proof"], dict)

    # Deserialize
    interp2 = InterpretationCrystal.from_dict(data)

    assert interp2.id == interp.id
    assert interp2.layer == interp.layer
    assert interp2.artifact_pattern == interp.artifact_pattern
    assert interp2.content == interp.content
    assert interp2.confidence == interp.confidence


def test_reflection_types():
    """Test different reflection types."""
    proof = GaloisWitnessedProof(data="Test", warrant="Test", claim="Test", backing="Test")

    types = ["synthesis", "comparison", "delta", "audit"]

    for rtype in types:
        reflection = ReflectionCrystal(
            id=f"r_{rtype}",
            target_ids=("t1",),
            reflection_type=rtype,
            insight=f"{rtype} insight",
            recommendations=(),
            derived_from=(),
            proof=proof,
        )
        assert reflection.reflection_type == rtype


def test_interpretation_types():
    """Test different interpretation types."""
    now = datetime.now(UTC)
    proof = GaloisWitnessedProof(data="Test", warrant="Test", claim="Test", backing="Test")

    types = ["trend", "pattern", "prediction"]

    for itype in types:
        interp = InterpretationCrystal(
            id=f"i_{itype}",
            artifact_pattern="**/*.py",
            time_range=(now, now),
            insight_type=itype,
            content=f"{itype} content",
            confidence=0.8,
            supporting_ids=(),
            proof=proof,
        )
        assert interp.insight_type == itype
