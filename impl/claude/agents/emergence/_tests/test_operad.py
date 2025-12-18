"""
Tests for EMERGENCE_OPERAD composition grammar.

Verifies:
1. Operations exist and have correct signatures
2. Law verification (pattern commutativity, circadian naturality)
3. Inheritance from DESIGN_OPERAD
4. Qualia blending symmetry

Target: 15+ tests for operad alone.
"""

import pytest
from agents.emergence import (
    CIRCADIAN_MODIFIERS,
    EMERGENCE_OPERAD,
    FAMILY_QUALIA,
    CircadianPhase,
    PatternFamily,
    QualiaCoords,
    QualiaModifier,
    create_emergence_operad,
)
from agents.operad import LawStatus, OperadRegistry

# =============================================================================
# Basic Structure Tests
# =============================================================================


class TestOperadStructure:
    """Test operad basic structure."""

    def test_operad_exists(self):
        """EMERGENCE_OPERAD exists."""
        assert EMERGENCE_OPERAD is not None

    def test_operad_name(self):
        """EMERGENCE_OPERAD has correct name."""
        assert EMERGENCE_OPERAD.name == "EMERGENCE"

    def test_operad_factory(self):
        """Factory creates valid operad."""
        operad = create_emergence_operad()
        assert operad.name == "EMERGENCE"

    def test_operad_registered(self):
        """EMERGENCE_OPERAD is registered in OperadRegistry."""
        assert "EMERGENCE" in OperadRegistry._operads


# =============================================================================
# Operations Tests
# =============================================================================


class TestOperations:
    """Test operad operations."""

    def test_has_select_family(self):
        """Has select_family operation."""
        assert "select_family" in EMERGENCE_OPERAD.operations

    def test_has_tune_param(self):
        """Has tune_param operation."""
        assert "tune_param" in EMERGENCE_OPERAD.operations

    def test_has_apply_preset(self):
        """Has apply_preset operation."""
        assert "apply_preset" in EMERGENCE_OPERAD.operations

    def test_has_modulate_qualia(self):
        """Has modulate_qualia operation."""
        assert "modulate_qualia" in EMERGENCE_OPERAD.operations

    def test_has_apply_circadian(self):
        """Has apply_circadian operation."""
        assert "apply_circadian" in EMERGENCE_OPERAD.operations

    def test_has_inject_entropy(self):
        """Has inject_entropy operation."""
        assert "inject_entropy" in EMERGENCE_OPERAD.operations

    def test_select_family_arity(self):
        """select_family is unary."""
        op = EMERGENCE_OPERAD.operations["select_family"]
        assert op.arity == 1

    def test_tune_param_arity(self):
        """tune_param is binary."""
        op = EMERGENCE_OPERAD.operations["tune_param"]
        assert op.arity == 2

    def test_modulate_qualia_arity(self):
        """modulate_qualia is binary."""
        op = EMERGENCE_OPERAD.operations["modulate_qualia"]
        assert op.arity == 2


# =============================================================================
# Inherited Operations Tests
# =============================================================================


class TestInheritedOperations:
    """Test operations inherited from DESIGN_OPERAD."""

    def test_has_split(self):
        """Has split operation from LAYOUT_OPERAD."""
        assert "split" in EMERGENCE_OPERAD.operations

    def test_has_stack(self):
        """Has stack operation from LAYOUT_OPERAD."""
        assert "stack" in EMERGENCE_OPERAD.operations

    def test_has_degrade(self):
        """Has degrade operation from CONTENT_OPERAD."""
        assert "degrade" in EMERGENCE_OPERAD.operations

    def test_has_breathe(self):
        """Has breathe operation from MOTION_OPERAD."""
        assert "breathe" in EMERGENCE_OPERAD.operations

    def test_has_pop(self):
        """Has pop operation from MOTION_OPERAD."""
        assert "pop" in EMERGENCE_OPERAD.operations

    def test_has_shimmer(self):
        """Has shimmer operation from MOTION_OPERAD."""
        assert "shimmer" in EMERGENCE_OPERAD.operations


# =============================================================================
# Law Tests
# =============================================================================


class TestLaws:
    """Test operad laws."""

    def test_has_pattern_commutativity_law(self):
        """Has pattern_commutativity law."""
        law_names = [law.name for law in EMERGENCE_OPERAD.laws]
        assert "pattern_commutativity" in law_names

    def test_has_circadian_naturality_law(self):
        """Has circadian_naturality law."""
        law_names = [law.name for law in EMERGENCE_OPERAD.laws]
        assert "circadian_naturality" in law_names

    def test_has_qualia_blending_law(self):
        """Has qualia_blending law."""
        law_names = [law.name for law in EMERGENCE_OPERAD.laws]
        assert "qualia_blending" in law_names

    def test_has_entropy_bounds_law(self):
        """Has entropy_bounds law."""
        law_names = [law.name for law in EMERGENCE_OPERAD.laws]
        assert "entropy_bounds" in law_names

    def test_has_inherited_content_lattice_law(self):
        """Has content_lattice law from DESIGN_OPERAD."""
        law_names = [law.name for law in EMERGENCE_OPERAD.laws]
        assert "content_lattice" in law_names

    def test_pattern_commutativity_structural(self):
        """pattern_commutativity law is structural (design choice)."""
        law = next(
            l for l in EMERGENCE_OPERAD.laws if l.name == "pattern_commutativity"
        )
        result = law.verify()
        assert result.status == LawStatus.STRUCTURAL

    def test_circadian_naturality_passes(self):
        """circadian_naturality law passes verification."""
        law = next(l for l in EMERGENCE_OPERAD.laws if l.name == "circadian_naturality")
        result = law.verify()
        assert result.status == LawStatus.PASSED

    def test_qualia_blending_passes(self):
        """qualia_blending law passes verification."""
        law = next(l for l in EMERGENCE_OPERAD.laws if l.name == "qualia_blending")
        result = law.verify()
        assert result.status == LawStatus.PASSED

    def test_entropy_bounds_structural(self):
        """entropy_bounds law is structural (design constraint)."""
        law = next(l for l in EMERGENCE_OPERAD.laws if l.name == "entropy_bounds")
        result = law.verify()
        assert result.status == LawStatus.STRUCTURAL


# =============================================================================
# Qualia Tests
# =============================================================================


class TestQualia:
    """Test qualia coordinates and operations."""

    def test_qualia_default_is_neutral(self):
        """Default QualiaCoords is neutral (all zeros)."""
        q = QualiaCoords()
        assert q.warmth == 0.0
        assert q.weight == 0.0
        assert q.tempo == 0.0

    def test_qualia_clamping(self):
        """QualiaCoords values are clamped to [-1, 1]."""
        q = QualiaCoords(warmth=2.0, weight=-2.0)
        assert q.warmth == 1.0
        assert q.weight == -1.0

    def test_qualia_blend_midpoint_symmetric(self):
        """Blending at t=0.5 is symmetric."""
        a = QualiaCoords(warmth=-0.5, weight=0.5)
        b = QualiaCoords(warmth=0.5, weight=-0.5)

        ab = a.blend(b, 0.5)
        ba = b.blend(a, 0.5)

        assert abs(ab.warmth - ba.warmth) < 0.001
        assert abs(ab.weight - ba.weight) < 0.001

    def test_qualia_blend_at_zero(self):
        """Blending at t=0 returns first."""
        a = QualiaCoords(warmth=0.3)
        b = QualiaCoords(warmth=0.7)

        result = a.blend(b, 0.0)
        assert result.warmth == 0.3

    def test_qualia_blend_at_one(self):
        """Blending at t=1 returns second."""
        a = QualiaCoords(warmth=0.3)
        b = QualiaCoords(warmth=0.7)

        result = a.blend(b, 1.0)
        assert result.warmth == 0.7

    def test_qualia_modifier_apply(self):
        """QualiaModifier applies correctly."""
        base = QualiaCoords(warmth=0.0, brightness=0.5)
        modifier = QualiaModifier(warmth=0.3, brightness=0.8)

        result = base.apply_modifier(modifier)
        assert result.warmth == 0.3  # 0 + 0.3
        assert result.brightness == 0.4  # 0.5 * 0.8

    def test_family_qualia_exists_for_all_families(self):
        """FAMILY_QUALIA has entry for every PatternFamily."""
        for family in PatternFamily:
            assert family in FAMILY_QUALIA

    def test_circadian_modifiers_exist_for_all_phases(self):
        """CIRCADIAN_MODIFIERS has entry for every CircadianPhase."""
        for phase in CircadianPhase:
            assert phase in CIRCADIAN_MODIFIERS


# =============================================================================
# Circadian Tests
# =============================================================================


class TestCircadian:
    """Test circadian phase determination."""

    def test_from_hour_dawn(self):
        """Hours 6-9 map to DAWN."""
        for hour in [6, 7, 8, 9]:
            assert CircadianPhase.from_hour(hour) == CircadianPhase.DAWN

    def test_from_hour_noon(self):
        """Hours 10-15 map to NOON."""
        for hour in [10, 11, 12, 13, 14, 15]:
            assert CircadianPhase.from_hour(hour) == CircadianPhase.NOON

    def test_from_hour_dusk(self):
        """Hours 16-19 map to DUSK."""
        for hour in [16, 17, 18, 19]:
            assert CircadianPhase.from_hour(hour) == CircadianPhase.DUSK

    def test_from_hour_midnight(self):
        """Other hours map to MIDNIGHT."""
        for hour in [0, 1, 2, 3, 4, 5, 20, 21, 22, 23]:
            assert CircadianPhase.from_hour(hour) == CircadianPhase.MIDNIGHT

    def test_dawn_modifier_cool(self):
        """DAWN modifier has negative warmth (cool)."""
        modifier = CIRCADIAN_MODIFIERS[CircadianPhase.DAWN]
        assert modifier.warmth < 0

    def test_dusk_modifier_warm(self):
        """DUSK modifier has positive warmth (warm)."""
        modifier = CIRCADIAN_MODIFIERS[CircadianPhase.DUSK]
        assert modifier.warmth > 0

    def test_midnight_modifier_dim(self):
        """MIDNIGHT modifier has low brightness."""
        modifier = CIRCADIAN_MODIFIERS[CircadianPhase.MIDNIGHT]
        assert modifier.brightness < 0.5
